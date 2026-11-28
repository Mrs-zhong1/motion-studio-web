#!/usr/bin/env python3
"""Build a deterministic, exact-SHA review archive for the PR branch."""
import argparse,hashlib,json,shutil
from pathlib import Path
from PIL import Image

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):
    try:return json.loads(p.read_text(encoding="utf-8"))
    except (OSError,ValueError):return None
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--tested-sha",required=True)
    ap.add_argument("--output",type=Path,default=Path("/tmp/r43-r55-review-evidence"))
    ap.add_argument("--r50-report",type=Path,default=Path("stage9/R50_HTML_BROWSER_ACCEPTANCE.json"))
    ap.add_argument("--r50-dir",type=Path,default=Path("/tmp/r50-html-browser"))
    ap.add_argument("--r56-dir",type=Path,default=Path("/tmp/r56-reference-screenshots"))
    ap.add_argument("--batch-dir",type=Path,default=Path("batch-report"))
    ap.add_argument("--r52-dir",type=Path,default=Path("r52-candidates"))
    a=ap.parse_args()
    if a.output.exists():shutil.rmtree(a.output)
    a.output.mkdir(parents=True);files=[];missing=[]
    def raw(src,rel):
        src=Path(src)
        if not src.is_file():missing.append(str(src));return
        dst=a.output/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
        files.append({"path":rel.as_posix(),"bytes":dst.stat().st_size,"sha256":sha(dst)})
    def image(src,rel):
        src=Path(src)
        if not src.is_file():missing.append(str(src));return
        dst=(a.output/rel).with_suffix(".jpg");dst.parent.mkdir(parents=True,exist_ok=True)
        with Image.open(src) as im:
            im.load();rgb=im.convert("RGB");w,h=rgb.size;rgb.save(dst,"JPEG",quality=88,optimize=True,progressive=True)
        files.append({"path":dst.relative_to(a.output).as_posix(),"sourcePath":str(src),"sourceSha256":sha(src),
                      "bytes":dst.stat().st_size,"sha256":sha(dst),"width":w,"height":h,"format":"jpeg"})
    r50=load(a.r50_report);r56path=a.r56_dir/"R56_REFERENCE_SCREENSHOTS.json";r56=load(r56path)
    r52=load(a.batch_dir/"R52_PHOTO_RIGHTS_REPORT.json");r53=load(a.batch_dir/"R53_33_ASSET_REPORT.json");r48=load(a.batch_dir/"R48_CANDIDATE_GATE.json")
    raw(a.r50_report,Path("reports/R50_HTML_BROWSER_ACCEPTANCE.json"));raw(r56path,Path("reports/R56_REFERENCE_SCREENSHOTS.json"))
    for src,name in [
      (a.batch_dir/"R52_PHOTO_RIGHTS_REPORT.json","R52_PHOTO_RIGHTS_REPORT.json"),
      (a.r52_dir/"discovery-report.json","R52_DISCOVERY_REPORT.json"),
      (a.r52_dir/"download-report.json","R52_DOWNLOAD_REPORT.json"),
      (Path("release/R52_CANDIDATE_EVIDENCE_LEDGER.csv"),"R52_CANDIDATE_EVIDENCE_LEDGER.csv"),
      (Path("release/R52_PHOTO_RIGHTS_REGISTER.csv"),"R52_PHOTO_RIGHTS_REGISTER.csv"),
      (a.batch_dir/"R53_33_ASSET_REPORT.json","R53_33_ASSET_REPORT.json"),
      (Path("release/R53_PRODUCTION_ASSET_REGISTER.json"),"R53_PRODUCTION_ASSET_REGISTER.json"),
      (a.batch_dir/"R43-R55_ONE_SHOT_RESULT.json","R43-R55_ONE_SHOT_RESULT.json"),
      (a.batch_dir/"HUMAN_ACTION_REQUIRED.md","HUMAN_ACTION_REQUIRED.md"),
      (a.batch_dir/"R48_CANDIDATE_GATE.json","R48_CANDIDATE_GATE.json")]:
        raw(src,Path("reports")/name)
    for browser in ("chromium","firefox","webkit"):
        raw(a.batch_dir/f"R47_{browser}.json",Path(f"reports/R47_{browser}.json"))
        raw(a.batch_dir/f"E2E_{browser}.json",Path(f"reports/E2E_{browser}.json"))
    if r50:
        for group in ("screenshots","pageScreenshots"):
            for item in r50.get(group,[]):
                if item.get("file"):image(a.r50_dir/item["file"],Path("screenshots/r50")/item["file"])
        for template,entry in r50.get("templates",{}).items():
            for viewport,frames in entry.get("frameScreenshots",{}).items():
                for item in frames:
                    if item.get("file"):image(a.r50_dir/item["file"],Path("screenshots/r50/chapters")/f"{template}-{viewport}-{item['file']}")
    else:missing.append(str(a.r50_report))
    if r56:
        for ref in r56.get("references",[]):
            for item in ref.get("captures",[]):
                if item.get("file"):image(a.r56_dir/item["file"],Path("screenshots/r56")/item["file"])
    else:missing.append(str(r56path))
    image(a.batch_dir/"R52_REVIEW_CONTACT_SHEET.png",Path("review-sheets/R52_REVIEW_CONTACT_SHEET.png"))
    image(a.batch_dir/"R53_REVIEW_CONTACT_SHEET.png",Path("review-sheets/R53_REVIEW_CONTACT_SHEET.png"))
    def status(d):return d.get("status","NOT_AVAILABLE") if isinstance(d,dict) else "NOT_AVAILABLE"
    def count(d,k,default=0):return d.get(k,default) if isinstance(d,dict) else default
    page=r53.get("pageReferenceAudit",{}) if isinstance(r53,dict) else {}
    r47={b:status(load(a.batch_dir/f"R47_{b}.json")) for b in ("chromium","firefox","webkit")}
    e2e={b:status(load(a.batch_dir/f"E2E_{b}.json")) for b in ("chromium","firefox","webkit")}
    summary={"testedSha":a.tested_sha,"overall":"HOLD","R50":status(r50),"R56":status(r56),
      "R52":{"status":status(r52),"accepted":count(r52,"accepted"),"expected":count(r52,"expected",15)},
      "R53":{"status":status(r53),"accepted":count(r53,"accepted"),"expected":count(r53,"expected",33),
             "referenced":count(page,"referenced"),"unreferenced":count(page,"unreferenced")},
      "R47":r47,"E2E":e2e,"R48":status(r48),"R54":"HOLD_REAL_DEVICE_REQUIRED",
      "R55":"HOLD_DEPLOYMENT_NOT_AUTHORIZED","humanVisualApproval":False,"rightsApproval":False,
      "productionEligible":False,"missingEvidenceFiles":sorted(set(missing))}
    readme=["# Motion Studio R43–R55 exact-SHA evidence","",f"Candidate SHA: {a.tested_sha}","",
      "Overall HOLD. This is a review archive, not visual, legal, device, merge or production approval.","",
      "| Gate | Result |","|---|---|",f"| R50 | {summary['R50']} |",f"| R56 | {summary['R56']} |",
      f"| R52 | {summary['R52']['status']} — {summary['R52']['accepted']}/{summary['R52']['expected']} accepted |",
      f"| R53 | {summary['R53']['status']} — {summary['R53']['accepted']}/{summary['R53']['expected']} accepted; {summary['R53']['referenced']}/{summary['R53']['expected']} referenced |",
      f"| R47 | {json.dumps(r47,sort_keys=True)} |",f"| E2E | {json.dumps(e2e,sort_keys=True)} |",
      f"| R48 | {status(r48)} |","| R54 | HOLD — physical device evidence required |",
      "| R55 | HOLD — no production deployment authorized |","","## Reports",
      "- [R50 browser report](reports/R50_HTML_BROWSER_ACCEPTANCE.json)","- [R56 reference capture report](reports/R56_REFERENCE_SCREENSHOTS.json)",
      "- [R52 itemized rights report](reports/R52_PHOTO_RIGHTS_REPORT.json)","- [R52 discovery](reports/R52_DISCOVERY_REPORT.json)",
      "- [R52 download evidence](reports/R52_DOWNLOAD_REPORT.json)","- [R53 asset report](reports/R53_33_ASSET_REPORT.json)",
      "- [R53 register](reports/R53_PRODUCTION_ASSET_REGISTER.json)","- [R48 candidate gate](reports/R48_CANDIDATE_GATE.json)",
      "- [Human action list](reports/HUMAN_ACTION_REQUIRED.md)","","## Agency and SaaS full-page captures",""]
    for template in ("agency","saas"):
        for viewport in ("desktop","mobile"):
            name=f"{template}-{viewport}-all-chapters.jpg";p=a.output/"screenshots"/"r50"/name
            if p.is_file():readme.extend([f"### {template.title()} {viewport}","",f"![{name}](screenshots/r50/{name})",""])
    readme.extend(["## R52 candidates — review only","","![R52 candidates](review-sheets/R52_REVIEW_CONTACT_SHEET.jpg)","",
      "## R53 originals — review only","","![R53 originals](review-sheets/R53_REVIEW_CONTACT_SHEET.jpg)","",
      "## Human gates","- Visual review and explicit Agency/SaaS approval.",
      "- Per-image R52 source, exact license, attribution, suitability and commercial compatibility review.",
      "- All 33 R53 assets must be visually approved and referenced by live export pages.",
      "- R54 physical iOS/Android device checks; R55 only after authorization and exact-SHA HTTPS verification.",
      "- PR #4 remains Draft and unmerged.",""])
    (a.output/"README.md").write_text("\n".join(readme),encoding="utf-8")
    manifest={"schema":"motion-studio-r43-r55-evidence-v1","testedSha":a.tested_sha,"summary":summary,
              "files":sorted(files,key=lambda x:x["path"])}
    (a.output/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"testedSha":a.tested_sha,"fileCount":len(files),"missing":len(set(missing)),"summary":summary},indent=2,ensure_ascii=False))
if __name__=="__main__":main()
