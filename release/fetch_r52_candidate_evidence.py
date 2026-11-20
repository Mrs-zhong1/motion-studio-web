#!/usr/bin/env python3
"""Download candidate original files from Wikimedia Commons for review only.

This script does not approve licenses, visual fit, or production eligibility.
"""
import csv, hashlib, json, re, urllib.request
from pathlib import Path
from PIL import Image, UnidentifiedImageError

ROOT=Path("r52-candidates")
LEDGER=Path("release/R52_CANDIDATE_EVIDENCE_LEDGER.csv")
ALLOWED_HOSTS={"upload.wikimedia.org"}
def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    rows=list(csv.DictReader(LEDGER.open(newline="",encoding="utf-8-sig")))
    report={"candidates":[],"downloaded":0,"errors":[],"status":"REVIEW_ONLY"}
    for row in rows:
        if row.get("rights_review_status")!="CANDIDATE_LICENSE_PAGE_VERIFIED_ORIGINAL_NOT_DOWNLOADED":
            continue
        url=row.get("original_file_url","")
        if not url.startswith("https://upload.wikimedia.org/"):
            report["errors"].append(row.get("candidate_id")+": original URL must be Wikimedia HTTPS")
            continue
        name=Path(url.split("?",1)[0]).name
        if not re.fullmatch(r"[A-Za-z0-9_.-]+",name):
            report["errors"].append(row.get("candidate_id")+": unsafe filename")
            continue
        request=urllib.request.Request(url,headers={"User-Agent":"MotionStudioR52EvidenceBot/1.0 (rights-review; contact via repository issues)"})
        try:
            with urllib.request.urlopen(request,timeout=45) as response:
                raw=response.read()
            path=ROOT/(row["candidate_id"]+"-"+name)
            path.write_bytes(raw)
            with Image.open(path) as im:
                im.load(); width,height=im.size; fmt=im.format
            if width!=int(row["original_width"]) or height!=int(row["original_height"]):
                raise ValueError(f"dimension mismatch expected {row['original_width']}x{row['original_height']} got {width}x{height}")
            source_sha1=row.get("source_sha1","").strip()
            actual_sha1=hashlib.sha1(raw).hexdigest()
            if source_sha1 and source_sha1!=actual_sha1:
                raise ValueError(f"Commons SHA-1 mismatch expected {source_sha1} got {actual_sha1}")
            report["downloaded"]+=1
            report["candidates"].append({
                "candidate_id":row["candidate_id"],"proposed_slot":row["proposed_slot"],
                "source_page_url":row["source_page_url"],"original_file_url":url,
                "creator":row["creator"],"license":row["license"],"license_url":row["license_url"],
                "dimensions":[width,height],"format":fmt,"bytes":len(raw),
                "source_sha1":actual_sha1,"local_sha256":hashlib.sha256(raw).hexdigest(),
                "file":path.name,"reviewStatus":"HUMAN_VISUAL_AND_RIGHTS_REVIEW_REQUIRED",
                "productionEligible":False
            })
        except (OSError,ValueError,UnidentifiedImageError) as exc:
            report["errors"].append(row.get("candidate_id")+": "+str(exc))
    (ROOT/"download-report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
if __name__=="__main__": main()
