#!/usr/bin/env python3
"""R52 fail-closed validator with itemized candidate leads; never grants approval."""
import argparse,csv,hashlib,json,os,re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image,UnidentifiedImageError

ALLOWED={"CC0-1.0","PDM-1.0","CC-BY-4.0","CC-BY-3.0","CC-BY-2.0","CC-BY-SA-4.0","CC-BY-SA-3.0","CC-BY-SA-2.0"}
EXPECTED={"architecture":{2,3,4,5},"cinematic":{2,3,4,5},"editorial":{2,3,4},"fashion":{2,3,4,5}}
REQUIRED={"local_file","creator","source_page_url","license_id","license_url","attribution","downloaded_at_utc","original_width","original_height","sha256","review_status"}
def https(value):
    p=urlparse(value or ""); return p.scheme=="https" and bool(p.netloc)
def valid_dimensions(width,height):
    return width>=1600 and height>=900 and abs((width/height)-(16/9))<=0.015
def read_json(path,default):
    try:return json.loads(path.read_text(encoding="utf-8"))
    except (OSError,ValueError):return default
def slot_evidence(row,candidates):
    missing=[k for k in sorted(REQUIRED) if not (row.get(k) or "").strip()]
    status="ACCEPTED" if not missing and row.get("review_status")=="APPROVED" else ("CANDIDATE_REVIEW_REQUIRED" if candidates else "NOT_SOURCED")
    reasons=[]
    if missing:reasons.append("register_missing_fields:"+",".join(missing))
    if candidates:reasons.append("candidate_leads_exist_but_are_not_accepted_into_the_rights_register")
    else:reasons.append("no_candidate_lead_recorded")
    if row.get("review_status")!="APPROVED":reasons.append("explicit_human_approval_missing")
    return {"slotId":row.get("slot_id",""),"template":row.get("template",""),
            "chapter":int(row["chapter"]) if row.get("chapter","").isdigit() else None,
            "registerReviewStatus":row.get("review_status",""),"status":status,
            "accepted":status=="ACCEPTED","productionEligible":status=="ACCEPTED",
            "missingFields":missing,"holdReasons":[] if status=="ACCEPTED" else reasons,"candidates":candidates}
def build_candidate_map(ledger,download,root):
    downloads={x.get("candidate_id"):x for x in download.get("candidates",[]) if x.get("candidate_id")}
    by_slot=defaultdict(list); errors=[]
    for row in ledger:
        cid=row.get("candidate_id",""); item=downloads.get(cid,{})
        filename=item.get("file") or row.get("local_file") or ""
        sha=item.get("local_sha256") or row.get("local_sha256") or ""
        path=root/filename if filename else None
        integrity="NOT_DOWNLOADED"
        if path and path.is_file():
            integrity="PASS" if sha and hashlib.sha256(path.read_bytes()).hexdigest()==sha else "FAIL"
            if integrity=="FAIL":errors.append(f"{cid}: local candidate SHA-256 missing or mismatched")
        by_slot[row.get("proposed_slot","")].append({
            "candidateId":cid,"proposedSlot":row.get("proposed_slot",""),"template":row.get("template",""),
            "sourcePageUrl":row.get("source_page_url",""),"originalFileUrl":row.get("original_file_url",""),
            "creator":row.get("creator",""),"licenseId":row.get("license",""),"licenseUrl":row.get("license_url",""),
            "sourceSha1":item.get("source_sha1") or row.get("source_sha1",""),
            "localFile":filename or None,"localSha256":sha or None,"downloadIntegrity":integrity,
            "rightsReviewStatus":row.get("rights_review_status",""),"visualReviewStatus":row.get("visual_review_status",""),
            "productionEligible":False,"approvalBoundary":"Downloaded candidate evidence is not human rights or visual approval."
        })
    return by_slot,errors
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--register",type=Path,default=Path("release/R52_PHOTO_RIGHTS_REGISTER.csv"))
    ap.add_argument("--asset-root",type=Path,default=Path("stage9/ai-assets"))
    ap.add_argument("--candidate-ledger",type=Path,default=Path("release/R52_CANDIDATE_EVIDENCE_LEDGER.csv"))
    ap.add_argument("--candidate-root",type=Path,default=Path("r52-candidates"))
    ap.add_argument("--download-report",type=Path,default=Path("r52-candidates/download-report.json"))
    ap.add_argument("--discovery-report",type=Path,default=Path("r52-candidates/discovery-report.json"))
    ap.add_argument("--report",type=Path); ap.add_argument("--allow-incomplete",action="store_true")
    args=ap.parse_args(); errors=[]; seen=set(); accepted=0; accepted_slots=[]
    with args.register.open(newline="",encoding="utf-8-sig") as f: rows=list(csv.DictReader(f))
    ledger=[]
    if args.candidate_ledger.is_file():
        with args.candidate_ledger.open(newline="",encoding="utf-8-sig") as f:ledger=list(csv.DictReader(f))
    download=read_json(args.download_report,{"candidates":[],"downloaded":0,"errors":[]})
    discovery=read_json(args.discovery_report,{"unfilledSlots":[]})
    candidate_map,candidate_errors=build_candidate_map(ledger,download,args.candidate_root); errors.extend(candidate_errors)
    if len(rows)!=15:errors.append(f"expected exactly 15 photo rows, found {len(rows)}")
    for n,row in enumerate(rows,2):
        sid=row.get("slot_id",""); template=row.get("template","")
        try:chapter=int(row.get("chapter",""))
        except ValueError:chapter=-1
        key=(template,chapter)
        if key in seen:errors.append(f"line {n}: duplicate slot {key}")
        seen.add(key)
        missing=[k for k in REQUIRED if not (row.get(k) or "").strip()]
        if missing:
            if row.get("review_status")!="NOT_SOURCED":errors.append(f"line {n} {sid}: incomplete record cannot claim {row.get('review_status')}")
            if not args.allow_incomplete:errors.append(f"line {n} {sid}: missing {', '.join(missing)}")
            continue
        lic=row["license_id"]
        if lic not in ALLOWED:errors.append(f"line {n} {sid}: license not approved for commercial reuse: {lic}");continue
        if not https(row["source_page_url"]) or not https(row["license_url"]):errors.append(f"line {n} {sid}: source and exact license URLs must use HTTPS");continue
        if lic.startswith("CC-BY-SA-") and row.get("share_alike_compatibility_reviewed","").lower()!="true":
            errors.append(f"line {n} {sid}: CC BY-SA compatibility review missing");continue
        try:
            stamp=datetime.fromisoformat(row["downloaded_at_utc"].replace("Z","+00:00"))
            if stamp.tzinfo is None:raise ValueError()
        except ValueError:errors.append(f"line {n} {sid}: downloaded_at_utc must be ISO-8601 with timezone");continue
        try:w,h=int(row["original_width"]),int(row["original_height"])
        except ValueError:w=h=0
        if not valid_dimensions(w,h):errors.append(f"line {n} {sid}: original dimensions must be >=1600x900 and 16:9");continue
        if not re.fullmatch(r"[0-9a-f]{64}",row["sha256"]):errors.append(f"line {n} {sid}: invalid SHA-256");continue
        local=Path(row["local_file"])
        if local.is_absolute() or ".." in local.parts:errors.append(f"line {n} {sid}: unsafe asset path");continue
        asset=args.asset_root/local
        if not asset.is_file():errors.append(f"line {n} {sid}: asset file missing: {asset}");continue
        if hashlib.sha256(asset.read_bytes()).hexdigest()!=row["sha256"]:errors.append(f"line {n} {sid}: file SHA-256 mismatch");continue
        try:
            with Image.open(asset) as im:
                im.load()
                if im.size!=(w,h):raise ValueError(f"actual {im.size}, declared {(w,h)}")
        except (OSError,ValueError,UnidentifiedImageError) as exc:errors.append(f"line {n} {sid}: invalid image or dimensions mismatch ({exc})");continue
        if row["review_status"]!="APPROVED":errors.append(f"line {n} {sid}: review_status must be APPROVED");continue
        accepted+=1;accepted_slots.append(sid)
    for template,chapters in EXPECTED.items():
        actual={int(r["chapter"]) for r in rows if r.get("template")==template and r.get("chapter","").isdigit()}
        if actual!=chapters:errors.append(f"{template}: expected chapters {sorted(chapters)}, found {sorted(actual)}")
    slots=[]
    for row in rows:
        item=slot_evidence(row,candidate_map.get(row.get("slot_id",""),[]))
        if item["slotId"] in accepted_slots:
            item.update({"status":"ACCEPTED","accepted":True,"productionEligible":True,"holdReasons":[]})
        slots.append(item)
    held=[x["slotId"] for x in slots if not x["accepted"]]
    report={"schema":"motion-studio-r52-itemized-rights-evidence-v2","candidateSha":os.environ.get("MOTION_CANDIDATE_SHA"),
            "rows":len(rows),"expected":15,"accepted":accepted,"acceptedSlots":accepted_slots,"heldSlots":held,"slots":slots,
            "candidateSummary":{"ledgerRows":len(ledger),"candidateLeads":len(ledger),"downloadedOriginals":int(download.get("downloaded",0)),
                                "downloadErrors":download.get("errors",[]),"unfilledDiscoverySlots":discovery.get("unfilledSlots",[]),"autoApproval":False},
            "errors":errors,"humanApprovalRequired":True,"productionEligible":accepted==15 and not errors,
            "status":"PASS" if not errors and accepted==15 else "HOLD",
            "boundary":"Commons metadata, source pages, downloaded originals and hashes are evidence only; no visual suitability, legal or production approval is inferred."}
    output=json.dumps(report,indent=2,ensure_ascii=False);print(output)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(output+"\n",encoding="utf-8")
    if (errors or accepted!=15) and not args.allow_incomplete:raise SystemExit(1)
if __name__=="__main__":main()
