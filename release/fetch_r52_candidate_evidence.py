#!/usr/bin/env python3
"""Download candidate original files from Wikimedia Commons for review only.

This script does not approve licenses, visual fit, or production eligibility.
"""
import csv, hashlib, json, re, time, urllib.request, urllib.error
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
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
        if row.get("rights_review_status") not in (
            "CANDIDATE_LICENSE_PAGE_VERIFIED_ORIGINAL_NOT_DOWNLOADED",
            "CANDIDATE_LICENSE_METADATA_DISCOVERED_NOT_HUMAN_REVIEWED",
        ):
            continue
        url=row.get("original_file_url","")
        if not url.startswith("https://upload.wikimedia.org/"):
            report["errors"].append(row.get("candidate_id")+": original URL must be Wikimedia HTTPS")
            continue
        name=Path(url.split("?",1)[0]).name
        if not re.fullmatch(r"[A-Za-z0-9_.-]+",name):
            report["errors"].append(row.get("candidate_id")+": unsafe filename")
            continue
        request=urllib.request.Request(url,headers={"User-Agent":"MotionStudioR52EvidenceBot/1.1 (+https://github.com/Mrs-zhong1/motion-studio-web; rights-review contact via repository issues)","Accept":"image/avif,image/webp,image/png,image/jpeg,*/*"})
        try:
            raw=None
            last_error=None
            for attempt in range(7):
                try:
                    with urllib.request.urlopen(request,timeout=45) as response:
                        raw=response.read()
                    break
                except urllib.error.HTTPError as exc:
                    last_error=exc
                    if exc.code not in (429,500,502,503,504) or attempt==6:
                        raise
                    retry_after=exc.headers.get("Retry-After")
                    delay=min(180.0,10.0*(2**attempt))
                    if retry_after:
                        try:
                            delay=min(300.0,max(2.0,float(retry_after)))
                        except ValueError:
                            try:
                                retry_at=parsedate_to_datetime(retry_after)
                                if retry_at.tzinfo is None: retry_at=retry_at.replace(tzinfo=timezone.utc)
                                delay=min(300.0,max(2.0,(retry_at-datetime.now(timezone.utc)).total_seconds()))
                            except (TypeError,ValueError,OverflowError):
                                pass
                    print("RETRY {}: HTTP {}; attempt {}/7; wait {:.1f}s".format(row.get("candidate_id"),exc.code,attempt+1,delay),flush=True)
                    time.sleep(delay)
            if raw is None:
                raise last_error or RuntimeError("download failed without response bytes")
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
        except (OSError,ValueError,UnidentifiedImageError,urllib.error.URLError) as exc:
            report["errors"].append(row.get("candidate_id")+": "+str(exc))
    (ROOT/"download-report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
if __name__=="__main__": main()
