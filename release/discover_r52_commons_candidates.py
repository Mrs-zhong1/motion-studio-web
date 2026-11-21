#!/usr/bin/env python3
"""Discover additional Wikimedia Commons photo leads for R52.

Metadata discovery only: candidates are never approved by this script. Only files
with explicit Commons CC0 or CC BY metadata, a named creator, a direct original
file URL, and native 16:9 dimensions >=1600x900 are appended to the review ledger.
"""
import argparse, csv, html, json, re, time, urllib.parse, urllib.request
from pathlib import Path

LEDGER = Path("release/R52_CANDIDATE_EVIDENCE_LEDGER.csv")
API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "MotionStudioR52CandidateDiscovery/1.0 (https://github.com/Mrs-zhong1/motion-studio-web)"
LICENSES = {
    "CC0": ("CC0-1.0", "https://creativecommons.org/publicdomain/zero/1.0/"),
    "CC0 1.0": ("CC0-1.0", "https://creativecommons.org/publicdomain/zero/1.0/"),
    "CC BY 4.0": ("CC-BY-4.0", "https://creativecommons.org/licenses/by/4.0/"),
    "CC BY 3.0": ("CC-BY-3.0", "https://creativecommons.org/licenses/by/3.0/"),
    "CC BY 2.0": ("CC-BY-2.0", "https://creativecommons.org/licenses/by/2.0/"),
}
SLOTS = {
    "architecture": [2,3,4,5],
    "cinematic": [2,3,4,5],
    "editorial": [2,3,4],
    "fashion": [2,3,4,5],
}
QUERIES = {
    "architecture": ['building architecture interior exterior'],
    "cinematic": ['film production movie set cinematography studio'],
    "editorial": ['editorial photography still life magazine portrait'],
    "fashion": ['fashion editorial clothing runway portrait'],
}

def api(params):
    params = {"action":"query","format":"json","formatversion":2,"maxlag":5,**params}
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent":USER_AGENT,"Accept":"application/json"})
    last = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=35) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            last = exc
            if attempt == 4: raise
            time.sleep(2 ** attempt)
    raise last

def plain(value):
    return html.unescape(re.sub(r"<[^>]+>", " ", value or "")).strip()

def read_ledger(path):
    """Read CSV rows while preserving legacy overflow cells from malformed-width rows."""
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, restkey="_overflow_cells")
        fields = list(reader.fieldnames or [])
        if not fields:
            raise SystemExit("R52 candidate ledger has no CSV header")
        raw_rows = list(reader)
    overflow_count = max((len(row.get("_overflow_cells") or []) for row in raw_rows), default=0)
    extra_fields = []
    index = 1
    while len(extra_fields) < overflow_count:
        name = f"legacy_extra_{index}"
        index += 1
        if name not in fields:
            extra_fields.append(name)
    fields.extend(extra_fields)
    rows = []
    for raw in raw_rows:
        overflow = raw.pop("_overflow_cells", None) or []
        row = {key: (value if value is not None else "") for key, value in raw.items()}
        for key, value in zip(extra_fields, overflow):
            row[key] = value
        for key in fields:
            row.setdefault(key, "")
        rows.append(row)
    return fields, rows

def write_ledger(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--max-new",type=int,default=10)
    args=ap.parse_args()
    fields, rows = read_ledger(LEDGER)
    used_slots={r.get("proposed_slot","") for r in rows}
    used_pages={r.get("source_page_url","") for r in rows}
    next_id=max([int(m.group(1)) for r in rows if (m:=re.match(r"R52-CAND-(\d+)$",r.get("candidate_id","")))]+[0])+1
    added=[]; rejected=[]; seen_files=set()
    for template, chapters in SLOTS.items():
        for chapter in chapters:
            slot=f"{template}-{chapter:02d}"
            if slot in used_slots or len(added)>=args.max_new: continue
            found=None
            for term in QUERIES[template]:
                data=api({"generator":"search","gsrsearch":f"filetype:bitmap {term}",
                          "gsrnamespace":6,"gsrlimit":30,
                          "prop":"imageinfo","iiprop":"url|size|sha1|extmetadata"})
                for page in data.get("query",{}).get("pages",[]):
                    info=(page.get("imageinfo") or [{}])[0]
                    meta=info.get("extmetadata") or {}
                    license_name=plain((meta.get("LicenseShortName") or {}).get("value"))
                    mapped=LICENSES.get(license_name)
                    creator=plain((meta.get("Artist") or {}).get("value"))
                    url=info.get("url","")
                    width,height=info.get("width",0),info.get("height",0)
                    page_url=page.get("canonicalurl") or ("https://commons.wikimedia.org/wiki/"+urllib.parse.quote(page.get("title","").replace(" ","_")))
                    if not mapped or not creator or not url.startswith("https://upload.wikimedia.org/"): continue
                    if info.get("mime") not in ("image/jpeg","image/png","image/webp"): continue
                    if width<1600 or height<900 or abs(width/height-16/9)>0.015: continue
                    if page_url in used_pages or url in seen_files: continue
                    found=(page,info,creator,mapped,page_url); break
                if found: break
            if not found:
                rejected.append({"slot":slot,"reason":"No matching explicit-license 16:9 candidate found in Commons search"})
                continue
            page,info,creator,(license_id,license_url),page_url=found
            cid=f"R52-CAND-{next_id:03d}"; next_id+=1
            row={k:"" for k in fields}
            row.update({
                "candidate_id":cid,"proposed_slot":slot,"template":template,
                "source_page_url":page_url,"original_file_url":info["url"],
                "creator":creator,"license":license_id,"license_url":license_url,
                "original_width":str(info["width"]),"original_height":str(info["height"]),
                "source_sha1":info.get("sha1",""),
                "rights_review_status":"CANDIDATE_LICENSE_METADATA_DISCOVERED_NOT_HUMAN_REVIEWED",
                "visual_review_status":"NOT_REVIEWED","production_eligible":"false",
                "notes":"Discovered by Wikimedia Commons API metadata search. Original binary, local SHA-256, visual suitability, exact page/license re-check and human approval remain required. Not accepted."
            })
            rows.append(row); added.append({"candidate_id":cid,"slot":slot,"title":page.get("title"),"license":license_id,"dimensions":[info["width"],info["height"]]})
            used_slots.add(slot); used_pages.add(page_url); seen_files.add(info["url"])
    write_ledger(LEDGER, fields, rows)
    report={"discovered":len(added),"candidates":added,"unfilledSlots":rejected,
            "ledgerRows":len(rows),"status":"REVIEW_ONLY","autoApproval":False}
    Path("r52-candidates").mkdir(exist_ok=True)
    Path("r52-candidates/discovery-report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
if __name__=="__main__": main()
