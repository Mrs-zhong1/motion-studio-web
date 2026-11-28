#!/usr/bin/env python3
"""Create a review-only contact sheet of downloaded R52 Commons candidates."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--report",type=Path,default=Path("r52-candidates/download-report.json"))
    ap.add_argument("--candidate-root",type=Path,default=Path("r52-candidates"))
    ap.add_argument("--output",type=Path,default=Path("batch-report/R52_REVIEW_CONTACT_SHEET.png"))
    a=ap.parse_args()
    doc=json.loads(a.report.read_text()) if a.report.is_file() else {"candidates":[]}
    items=[];missing=[]
    for row in doc.get("candidates",[]):
        p=a.candidate_root/row["file"] if row.get("file") else None
        if p and p.is_file():items.append((row,p))
        else:missing.append(row.get("candidate_id","unknown"))
    cols=3;cw,ch=520,390;rows=max(1,(len(items)+cols-1)//cols)
    sheet=Image.new("RGB",(cols*cw,rows*ch+86),(245,245,241));d=ImageDraw.Draw(sheet);font=ImageFont.load_default()
    d.rectangle((0,0,sheet.width,72),fill=(30,36,34))
    d.text((24,14),"R52 PHOTOGRAPHY CANDIDATES — REVIEW ONLY / NOT APPROVED",fill="white",font=font)
    d.text((24,38),f"Downloaded: {len(items)} | Missing files: {len(missing)} | Automated approvals: 0",fill=(220,230,222),font=font)
    if not items:d.text((24,112),"No downloaded candidate originals are available.",fill=(30,36,34),font=font)
    for i,(row,path) in enumerate(items):
        x=(i%cols)*cw;y=86+(i//cols)*ch;d.rectangle((x+10,y+10,x+cw-10,y+ch-10),outline=(190,196,188),width=2)
        with Image.open(path) as im:
            im.load();thumb=im.convert("RGB");thumb.thumbnail((cw-44,255),Image.Resampling.LANCZOS)
            sheet.paste(thumb,(x+(cw-thumb.width)//2,y+20))
        dims=row.get("dimensions",[]);size=f"{dims[0]}x{dims[1]}" if len(dims)==2 else "unknown"
        label=[f"{row.get('candidate_id','candidate')} / {row.get('proposed_slot','unassigned')}",
               f"{row.get('creator','unknown')} | {row.get('license','unknown')} | {size}",
               f"SHA-256 {str(row.get('local_sha256','missing'))[:24]}..."]
        d.multiline_text((x+24,y+286),"\n".join(label),fill=(25,31,28),font=font,spacing=5)
    a.output.parent.mkdir(parents=True,exist_ok=True);sheet.save(a.output,format="PNG",optimize=True)
    print(json.dumps({"status":"REVIEW_ONLY","downloaded":len(items),"missing":missing,"productionApproval":False,"output":str(a.output)},indent=2))
if __name__=="__main__":main()
