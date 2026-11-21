#!/usr/bin/env python3
"""R52 fail-closed validator for the 15 photography rights records."""
import argparse,csv,hashlib,json,re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image,UnidentifiedImageError

ALLOWED={"CC0-1.0","PDM-1.0","CC-BY-4.0","CC-BY-3.0","CC-BY-2.0","CC-BY-SA-4.0","CC-BY-SA-3.0","CC-BY-SA-2.0"}
EXPECTED={"architecture":{2,3,4,5},"cinematic":{2,3,4,5},"editorial":{2,3,4},"fashion":{2,3,4,5}}
REQUIRED={"local_file","creator","source_page_url","license_id","license_url","attribution","downloaded_at_utc","original_width","original_height","sha256","review_status"}
def https(value):
 p=urlparse(value or "")
 return p.scheme=="https" and bool(p.netloc)
def valid_dimensions(width,height):
 return width>=1600 and height>=900 and abs((width/height)-(16/9))<=0.015
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--register",type=Path,default=Path("release/R52_PHOTO_RIGHTS_REGISTER.csv"))
 ap.add_argument("--asset-root",type=Path,default=Path("stage9/ai-assets"))
 ap.add_argument("--report",type=Path)
 ap.add_argument("--allow-incomplete",action="store_true")
 args=ap.parse_args(); errors=[]; seen=set(); accepted=0
 with args.register.open(newline="",encoding="utf-8-sig") as f: rows=list(csv.DictReader(f))
 if len(rows)!=15: errors.append(f"expected exactly 15 photo rows, found {len(rows)}")
 for n,row in enumerate(rows,2):
  sid=row.get("slot_id",""); template=row.get("template","")
  try: chapter=int(row.get("chapter",""))
  except ValueError: chapter=-1
  key=(template,chapter)
  if key in seen: errors.append(f"line {n}: duplicate slot {key}")
  seen.add(key)
  missing=[k for k in REQUIRED if not row.get(k,"").strip()]
  if missing:
   if row.get("review_status")!="NOT_SOURCED": errors.append(f"line {n} {sid}: incomplete record cannot claim {row.get('review_status')}")
   if not args.allow_incomplete: errors.append(f"line {n} {sid}: missing {', '.join(missing)}")
   continue
  lic=row["license_id"]
  if lic not in ALLOWED: errors.append(f"line {n} {sid}: license not approved for commercial reuse: {lic}"); continue
  if not https(row["source_page_url"]) or not https(row["license_url"]): errors.append(f"line {n} {sid}: source and exact license URLs must use HTTPS"); continue
  if lic.startswith("CC-BY-SA-") and row.get("share_alike_compatibility_reviewed","").lower()!="true":
   errors.append(f"line {n} {sid}: CC BY-SA compatibility review missing"); continue
  try:
   stamp=datetime.fromisoformat(row["downloaded_at_utc"].replace("Z","+00:00"))
   if stamp.tzinfo is None: raise ValueError()
  except ValueError: errors.append(f"line {n} {sid}: downloaded_at_utc must be ISO-8601 with timezone"); continue
  try: w,h=int(row["original_width"]),int(row["original_height"])
  except ValueError: w=h=0
  if not valid_dimensions(w,h): errors.append(f"line {n} {sid}: original dimensions must be >=1600x900 and 16:9"); continue
  if not re.fullmatch(r"[0-9a-f]{64}",row["sha256"]): errors.append(f"line {n} {sid}: invalid SHA-256"); continue
  local=Path(row["local_file"])
  if local.is_absolute() or ".." in local.parts: errors.append(f"line {n} {sid}: unsafe asset path"); continue
  asset=args.asset_root/local
  if not asset.is_file(): errors.append(f"line {n} {sid}: asset file missing: {asset}"); continue
  if hashlib.sha256(asset.read_bytes()).hexdigest()!=row["sha256"]: errors.append(f"line {n} {sid}: file SHA-256 mismatch"); continue
  try:
   with Image.open(asset) as im:
    im.load()
    if im.size!=(w,h): raise ValueError(f"actual {im.size}, declared {(w,h)}")
  except (OSError,ValueError,UnidentifiedImageError) as exc:
   errors.append(f"line {n} {sid}: invalid image or dimensions mismatch ({exc})"); continue
  if row["review_status"]!="APPROVED": errors.append(f"line {n} {sid}: review_status must be APPROVED"); continue
  accepted+=1
 for template,chapters in EXPECTED.items():
  actual={int(r["chapter"]) for r in rows if r.get("template")==template and r.get("chapter","").isdigit()}
  if actual!=chapters: errors.append(f"{template}: expected chapters {sorted(chapters)}, found {sorted(actual)}")
 report={"rows":len(rows),"accepted":accepted,"errors":errors,"status":"PASS" if not errors and accepted==15 else "HOLD"}
 output=json.dumps(report,indent=2); print(output)
 if args.report: args.report.write_text(output+"\n",encoding="utf-8")
 if errors and not args.allow_incomplete: raise SystemExit(1)
 if accepted!=15 and not args.allow_incomplete: raise SystemExit(1)
if __name__=="__main__": main()
