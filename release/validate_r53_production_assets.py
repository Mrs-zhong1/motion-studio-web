#!/usr/bin/env python3
"""R53 fail-closed validator for all 33 approved replacement slots."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,UnidentifiedImageError

PROCEDURAL={"agency":{1,2,3,4,5},"product-3d":{2,3,4,5},"gallery":{2,3,4,5},"saas":{1,2,3,4,5}}
PHOTOGRAPHY={"architecture":{2,3,4,5},"cinematic":{2,3,4,5},"editorial":{2,3,4},"fashion":{2,3,4,5}}

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--register",type=Path,default=Path("release/R53_PRODUCTION_ASSET_REGISTER.json"))
 ap.add_argument("--asset-root",type=Path,default=Path("stage9/ai-assets"))
 ap.add_argument("--report",type=Path)
 ap.add_argument("--require-release",action="store_true")
 a=ap.parse_args(); doc=json.loads(a.register.read_text()); rows=doc.get("assets",[])
 errors=[]; accepted=[]; seen=set()
 if len(rows)!=33: errors.append(f"expected 33 records, found {len(rows)}")
 expected={(t,c,"procedural") for t,cs in PROCEDURAL.items() for c in cs}|{(t,c,"photography") for t,cs in PHOTOGRAPHY.items() for c in cs}
 for row in rows:
  key=(row.get("template"),row.get("chapter"),row.get("mediaClass"))
  if key in seen: errors.append(f"duplicate slot {key}")
  seen.add(key)
  if key not in expected: errors.append(f"unexpected slot {key}"); continue
  if row.get("productionEligible") is not True or row.get("humanVisualApproval") is not True or row.get("reviewStatus")!="APPROVED":
   errors.append(f"{row.get('slotId')}: human approval and productionEligible=true required"); continue
  filename=row.get("file","")
  if not filename or Path(filename).name!=filename: errors.append(f"{row.get('slotId')}: unsafe/missing filename"); continue
  path=a.asset_root/filename
  if not path.is_file(): errors.append(f"{row.get('slotId')}: missing file {filename}"); continue
  raw=path.read_bytes()
  if hashlib.sha256(raw).hexdigest()!=row.get("sha256"): errors.append(f"{row.get('slotId')}: file SHA-256 mismatch"); continue
  dims=row.get("nativeDimensions")
  if not isinstance(dims,list) or len(dims)!=2 or min(dims)<1600: errors.append(f"{row.get('slotId')}: native dimensions below 1600x900"); continue
  if key[2]=="procedural":
   if row.get("thirdPartyAssets") is not False or row.get("commercialUseTermsChecked") is not True:
    errors.append(f"{row.get('slotId')}: procedural source or terms declaration incomplete"); continue
   source=row.get("sourceCodePath","")
   if not source or not Path(source).is_file(): errors.append(f"{row.get('slotId')}: reproducible source code missing"); continue
   if hashlib.sha256(Path(source).read_bytes()).hexdigest()!=row.get("sourceCodeSha256"): errors.append(f"{row.get('slotId')}: source code hash mismatch"); continue
   if row.get("template")=="saas":
    if path.suffix.lower()!=".svg": errors.append(f"{row.get('slotId')}: SaaS must be original SVG/Canvas vector"); continue
   else:
    try:
     with Image.open(path) as im:
      im.load()
      if im.size[0]<1600 or im.size[1]<900: raise ValueError("image too small")
    except (OSError,ValueError,UnidentifiedImageError):
     errors.append(f"{row.get('slotId')}: procedural render cannot be decoded at native size"); continue
  else:
   required=("creator","sourcePageUrl","licenseId","licenseUrl","attribution","downloadedAtUtc")
   if not all(row.get(k) for k in required): errors.append(f"{row.get('slotId')}: photo rights evidence incomplete"); continue
   lic=row.get("licenseId","").upper().replace("_","-")
   if not (lic.startswith(("CC0-","CC-BY-","CC-BY-SA-")) or lic in ("PDM-1.0","PUBLIC-DOMAIN")) or "NC" in lic or "ND" in lic:
    errors.append(f"{row.get('slotId')}: license is not commercially compatible"); continue
   if lic.startswith("CC-BY-SA-") and row.get("shareAlikeCompatibilityReviewed") is not True:
    errors.append(f"{row.get('slotId')}: CC BY-SA compatibility review missing"); continue
   if path.suffix.lower() not in (".jpg",".jpeg",".png"): errors.append(f"{row.get('slotId')}: unsupported photography format"); continue
   try:
    with Image.open(path) as im:
     im.load()
     if im.size[0]<1600 or im.size[1]<900: raise ValueError()
   except (OSError,ValueError,UnidentifiedImageError):
    errors.append(f"{row.get('slotId')}: photo is not decodable at required native pixels"); continue
  accepted.append(row.get("slotId"))
 missing=expected-seen
 if missing: errors.append(f"missing slots: {sorted(missing)}")
 report={"expected":33,"accepted":len(accepted),"acceptedSlots":accepted,"errors":errors,"status":"PASS" if not errors and len(accepted)==33 else "HOLD"}
 print(json.dumps(report,indent=2))
 if a.report: a.report.write_text(json.dumps(report,indent=2)+"\n")
 if a.require_release and report["status"]!="PASS": raise SystemExit(1)

if __name__=="__main__": main()
