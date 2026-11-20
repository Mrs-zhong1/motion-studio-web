#!/usr/bin/env python3
"""R53 fail-closed validator for all 33 approved replacement slots."""
import argparse, hashlib, json, re, xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image, UnidentifiedImageError

PROCEDURAL={"agency":{1,2,3,4,5},"product-3d":{2,3,4,5},"gallery":{2,3,4,5},"saas":{1,2,3,4,5}}
PHOTOGRAPHY={"architecture":{2,3,4,5},"cinematic":{2,3,4,5},"editorial":{2,3,4},"fashion":{2,3,4,5}}
LICENSES={"CC0-1.0","PDM-1.0","PUBLIC-DOMAIN","CC-BY-2.0","CC-BY-3.0","CC-BY-4.0","CC-BY-SA-2.0","CC-BY-SA-3.0","CC-BY-SA-4.0"}

def https(value):
 p=urlparse(value or "")
 return p.scheme=="https" and bool(p.netloc)

def valid_dimensions(dims):
 if not isinstance(dims,list) or len(dims)!=2: return False
 try: w,h=map(int,dims)
 except (TypeError,ValueError): return False
 return w>=1600 and h>=900 and abs((w/h)-(16/9))<=0.015

def validate_svg(path):
 root=ET.parse(path).getroot()
 if root.tag.split("}")[-1]!="svg": raise ValueError("root is not SVG")
 if root.attrib.get("viewBox")!="0 0 1600 900": raise ValueError("viewBox must be 0 0 1600 900")
 if root.attrib.get("width") not in ("1600","1600px") or root.attrib.get("height") not in ("900","900px"):
  raise ValueError("SVG width/height must be 1600x900")
 return (1600,900)

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--register",type=Path,default=Path("release/R53_PRODUCTION_ASSET_REGISTER.json"))
 ap.add_argument("--asset-root",type=Path,default=Path("stage9/ai-assets"))
 ap.add_argument("--report",type=Path)
 ap.add_argument("--require-release",action="store_true")
 a=ap.parse_args(); doc=json.loads(a.register.read_text()); rows=doc.get("assets",[])
 errors=[]; accepted=[]; seen=set()
 expected={(t,c,"procedural") for t,cs in PROCEDURAL.items() for c in cs}|{(t,c,"photography") for t,cs in PHOTOGRAPHY.items() for c in cs}
 if len(rows)!=33: errors.append(f"expected 33 records, found {len(rows)}")
 for row in rows:
  slot=row.get("slotId",""); key=(row.get("template"),row.get("chapter"),row.get("mediaClass"))
  if key in seen: errors.append(f"duplicate slot {key}")
  seen.add(key)
  if key not in expected: errors.append(f"{slot}: unexpected slot {key}"); continue
  approval_ok=(row.get("productionEligible") is True and row.get("humanVisualApproval") is True and row.get("reviewStatus")=="APPROVED")
  if not approval_ok:
   errors.append(f"{slot}: human approval and productionEligible=true required")
  filename=row.get("file","")
  if not filename or Path(filename).name!=filename: errors.append(f"{slot}: unsafe/missing filename"); continue
  path=a.asset_root/filename
  if not path.is_file(): errors.append(f"{slot}: missing file {filename}"); continue
  raw=path.read_bytes()
  if hashlib.sha256(raw).hexdigest()!=row.get("sha256"): errors.append(f"{slot}: file SHA-256 mismatch"); continue
  dims=row.get("nativeDimensions")
  if not valid_dimensions(dims): errors.append(f"{slot}: declared dimensions must be >=1600x900 and 16:9"); continue
  if key[2]=="procedural":
   if row.get("thirdPartyAssets") is not False or row.get("commercialUseTermsChecked") is not True:
    errors.append(f"{slot}: procedural source or terms declaration incomplete"); continue
   source=row.get("sourceCodePath","")
   if not source or not Path(source).is_file(): errors.append(f"{slot}: reproducible source code missing"); continue
   if not re.fullmatch(r"[0-9a-f]{64}",row.get("sourceCodeSha256","")) or hashlib.sha256(Path(source).read_bytes()).hexdigest()!=row.get("sourceCodeSha256"):
    errors.append(f"{slot}: source code hash mismatch"); continue
   try:
    if key[0]=="saas":
     if path.suffix.lower()!=".svg": raise ValueError("SaaS requires SVG")
     actual=validate_svg(path)
    else:
     if path.suffix.lower()!=".png": raise ValueError("procedural 3D render must be PNG")
     with Image.open(path) as im:
      im.load(); actual=im.size
   except (OSError,ValueError,ET.ParseError,UnidentifiedImageError) as exc:
    errors.append(f"{slot}: invalid native asset ({exc})"); continue
   if actual!=(dims[0],dims[1]): errors.append(f"{slot}: manifest dimensions differ from decoded asset"); continue
  else:
   required=("creator","sourcePageUrl","licenseId","licenseUrl","attribution","downloadedAtUtc")
   if not all(row.get(k) for k in required): errors.append(f"{slot}: photo rights evidence incomplete"); continue
   lic=row.get("licenseId","").upper().replace("_","-")
   if lic not in LICENSES: errors.append(f"{slot}: license not explicitly approved for commercial reuse: {lic}"); continue
   if not https(row.get("sourcePageUrl")) or not https(row.get("licenseUrl")): errors.append(f"{slot}: source and exact license URLs must use HTTPS"); continue
   if lic.startswith("CC-BY-SA-") and row.get("shareAlikeCompatibilityReviewed") is not True:
    errors.append(f"{slot}: CC BY-SA compatibility review missing"); continue
   try:
    from datetime import datetime
    stamp=datetime.fromisoformat(row["downloadedAtUtc"].replace("Z","+00:00"))
    if stamp.tzinfo is None: raise ValueError()
   except ValueError: errors.append(f"{slot}: downloadedAtUtc requires ISO-8601 timezone"); continue
   if path.suffix.lower() not in (".jpg",".jpeg",".png"): errors.append(f"{slot}: unsupported photography format"); continue
   try:
    with Image.open(path) as im:
     im.load(); actual=im.size
   except (OSError,UnidentifiedImageError): errors.append(f"{slot}: photo cannot be decoded"); continue
   if actual!=(dims[0],dims[1]): errors.append(f"{slot}: manifest dimensions differ from decoded photo"); continue
  if approval_ok: accepted.append(slot)
 missing=expected-seen
 if missing: errors.append(f"missing slots: {sorted(missing)}")
 report={"expected":33,"accepted":len(accepted),"acceptedSlots":accepted,"errors":errors,"status":"PASS" if not errors and len(accepted)==33 else "HOLD"}
 print(json.dumps(report,indent=2))
 if a.report: a.report.write_text(json.dumps(report,indent=2)+"\n")
 if a.require_release and report["status"]!="PASS": raise SystemExit(1)
if __name__=="__main__": main()
