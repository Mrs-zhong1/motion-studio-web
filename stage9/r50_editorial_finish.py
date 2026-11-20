#!/usr/bin/env python3
"""Apply template-specific editorial typography after Blender rendering."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--out",type=Path,default=Path("r50-review")); a=ap.parse_args()
 root=a.out; manifest_path=root/"manifest.json"; rows=json.loads(manifest_path.read_text())
 font_root=Path("/usr/share/fonts/truetype/dejavu")
 regular=ImageFont.truetype(str(font_root/"DejaVuSans.ttf"),18)
 small=ImageFont.truetype(str(font_root/"DejaVuSans.ttf"),13)
 title_font=ImageFont.truetype(str(font_root/"DejaVuSans-Bold.ttf"),43)
 specs={
  "agency":("FIELD / 01","FORM FOLLOWS\nFEELING","Creative direction\n& digital worlds","ATELIER  /  2026","A01"),
  "product-3d":("OBJECT / 02","SOUND IN\nPURE FORM","Precision audio\nobject study","INDUSTRIAL  /  01","P02"),
  "gallery":("SPACE / 03","THE ART OF\nSTILLNESS","Sculpture, light\n& spatial rhythm","EXHIBITION  /  04","G03")
 }
 source_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 for row in rows:
  if row["file"].endswith(".png"):
   image=Image.open(root/row["file"]).convert("RGB"); draw=ImageDraw.Draw(image,"RGBA")
   draw.rectangle((0,0,330,900),fill=(8,14,23,242)); draw.rectangle((330,0,334,900),fill=(201,151,87,255))
   eyebrow,title,sub,meta,code=specs[row["template"]]
   white=(241,240,233,255); muted=(154,169,184,255); accent=(210,160,91,255)
   draw.text((42,52),"M / S     MOTION STUDIO",font=small,fill=muted)
   draw.line((42,92,278,92),fill=(96,112,128,180),width=1)
   draw.text((42,145),eyebrow,font=regular,fill=accent)
   draw.multiline_text((40,215),title,font=title_font,fill=white,spacing=7)
   draw.multiline_text((42,365),sub,font=regular,fill=muted,spacing=9)
   draw.line((42,760,278,760),fill=(96,112,128,180),width=1)
   draw.text((42,786),meta,font=small,fill=muted); draw.text((42,835),code,font=regular,fill=accent)
   image.save(root/row["file"],format="PNG",optimize=True)
   row["sha256"]=hashlib.sha256((root/row["file"]).read_bytes()).hexdigest()
   row["editorialFinishSourceSha256"]=source_hash
   row["reviewStatus"]="HUMAN_VISUAL_REVIEW_REQUIRED"; row["productionEligible"]=False
 manifest_path.write_text(json.dumps(rows,indent=2)+"\n")
 print(json.dumps({"finished":3,"sourceSha256":source_hash,"productionEligible":False},indent=2))
if __name__=="__main__": main()
