#!/usr/bin/env python3
"""R26 zero-cost hybrid visual pilot. Creates native 1600x900 procedural scene renders.

No image API, model download, stock image, remote asset, collage, or upscaling.
Outputs are review-only and never replace committed chapter media.
"""
import argparse, hashlib, json, math
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parent
BOARD=ROOT/"r26-storyboard.json"
PILOT_KEYS=[("editorial",2),("product-3d",3),("architecture",2),("agency",1)]
W,H=1600,900

PALETTES={
 "editorial":((28,34,31),(205,190,158),(116,126,104),(230,218,192)),
 "product-3d":((9,13,19),(52,65,78),(150,166,176),(218,227,230)),
 "architecture":((42,48,48),(197,181,151),(129,117,97),(235,226,205)),
 "agency":((26,18,25),(255,93,54),(250,202,46),(75,186,207)),
 "cinematic":((8,18,38),(26,54,83),(194,112,70),(224,187,133)),
 "fashion":((31,24,28),(111,75,73),(206,164,143),(231,214,194)),
 "gallery":((25,27,33),(105,118,138),(220,177,117),(226,224,215)),
 "saas":((12,24,35),(36,82,106),(91,179,190),(202,231,228)),
}

def gradient(base, lift):
 im=Image.new("RGB",(W,H),base); d=ImageDraw.Draw(im)
 for y in range(H):
  t=y/(H-1)
  color=tuple(max(0,min(255,int(base[i]*(1-t*.18)+lift[i]*(t*.18)))) for i in range(3))
  d.line((0,y,W,y),fill=color)
 return im

def polygon(draw, pts, fill, outline=None, width=1):
 draw.polygon(pts,fill=fill)
 if outline: draw.line(pts+[pts[0]],fill=outline,width=width,joint="curve")

def render(row,out):
 t=row["template"]; c=row["chapter"]; p=PALETTES[t]
 im=gradient(p[0],p[1]); glow=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(glow)
 # soft studio light and a grounded horizon
 d.ellipse((180,80,1050,780),fill=(*p[2],32))
 glow=glow.filter(ImageFilter.GaussianBlur(95)); im=Image.alpha_composite(im.convert("RGBA"),glow)
 shadow=Image.new("RGBA",(W,H),(0,0,0,0)); sd=ImageDraw.Draw(shadow)
 sd.ellipse((260,640,1160,805),fill=(0,0,0,115))
 shadow=shadow.filter(ImageFilter.GaussianBlur(38)); im=Image.alpha_composite(im,shadow)
 d=ImageDraw.Draw(im)
 # Keep the right third quiet for chapter titles unless storyboard says left.
 safe=row.get("textSafeZone","right third")
 subject_x=590 if safe=="right third" else 1050
 if t in ("product-3d","gallery","agency","fashion","saas"):
  # A single coherent sculptural subject with dimensional faces and contact shadows.
  if t=="product-3d":
   d.ellipse((subject_x-230,610,subject_x+290,735),fill=(4,7,10,210))
   d.rounded_rectangle((subject_x-210,310,subject_x+185,625),radius=105,fill=(35,45,54,255),outline=p[3],width=5)
   d.polygon([(subject_x-175,340),(subject_x-75,260),(subject_x+180,290),(subject_x+185,360)],fill=(100,119,130,255))
   d.rounded_rectangle((subject_x-160,390,subject_x+125,565),radius=74,fill=(17,25,32,255),outline=(145,163,173,255),width=4)
   for k in range(7):
    x=subject_x-112+k*34
    d.ellipse((x,448,x+9,457),fill=(185,202,207,220))
   d.arc((subject_x-180,285,subject_x+190,660),190,330,fill=(225,235,235,190),width=7)
  elif t=="agency":
   d.ellipse((subject_x-250,560,subject_x+260,720),fill=(0,0,0,95))
   d.rounded_rectangle((subject_x-205,325,subject_x+125,585),radius=92,fill=p[2],outline=(255,235,210,220),width=5)
   d.ellipse((subject_x-125,210,subject_x+220,510),fill=p[1],outline=(255,225,190,230),width=5)
   d.polygon([(subject_x-205,480),(subject_x-80,390),(subject_x+110,530),(subject_x+15,665)],fill=p[3])
   d.ellipse((subject_x+100,250,subject_x+270,420),outline=p[2],width=28)
  elif t=="gallery":
   d.rectangle((subject_x-250,580,subject_x+250,635),fill=(62,66,72,255))
   d.polygon([(subject_x-140,580),(subject_x-70,330),(subject_x+10,580)],fill=p[2])
   d.ellipse((subject_x-40,270,subject_x+180,500),fill=p[1],outline=p[3],width=5)
   d.rounded_rectangle((subject_x-210,430,subject_x-90,580),radius=58,fill=p[3])
  elif t=="fashion":
   d.ellipse((subject_x-90,205,subject_x+90,385),fill=p[2])
   polygon(d,[(subject_x-55,350),(subject_x+55,350),(subject_x+235,670),(subject_x-225,670)],p[1])
   for k in range(5):
    x=subject_x-170+k*68
    d.line((x,430,x+(-40+k*15),655),fill=p[3],width=5)
   d.ellipse((subject_x-260,655,subject_x+260,715),fill=(0,0,0,85))
  elif t=="saas":
   for k,(x,y,w,h) in enumerate([(subject_x-230,300,240,310),(subject_x+20,350,220,250),(subject_x-130,185,280,120)]):
    d.rounded_rectangle((x,y,x+w,y+h),radius=22,fill=(30,75,91,235),outline=p[3],width=3)
   for k in range(5):
    x=subject_x-190+k*48
    d.rounded_rectangle((x,505,x+26,550+((k*31+c*9)%70)),radius=8,fill=p[2])
 else:
  # Architectural / editorial / cinematic environment as layered spatial illustration.
  if t=="architecture":
   d.rectangle((250,525,1110,710),fill=(87,81,70,255))
   polygon(d,[(340,525),(340,300),(620,205),(900,300),(900,525)],(191,176,149,255),outline=(232,220,193,255),width=5)
   polygon(d,[(900,300),(1090,365),(1090,585),(900,525)],(112,105,92,255))
   d.rectangle((455,360,610,525),fill=(31,51,53,255),outline=(226,213,184,255),width=8)
   d.rectangle((680,330,820,525),fill=(34,48,49,255),outline=(226,213,184,255),width=8)
   d.polygon([(270,710),(1100,710),(1250,810),(180,810)],fill=(65,67,61,255))
  elif t=="editorial":
   d.polygon([(250,520),(900,520),(1080,690),(390,690)],fill=(214,204,181,255),outline=(245,236,214,255))
   d.rectangle((390,390,680,505),fill=(126,139,113,255))
   d.polygon([(730,430),(900,360),(990,500),(810,555)],fill=(178,130,83,255))
   d.ellipse((510,360,640,490),fill=(49,60,52,255))
   for k in range(5):
    d.line((330,570+k*17,870,570+k*17),fill=(151,142,122,200),width=3)
  else:
   # cinematic horizon, mist bands, mountain silhouettes and a single moon.
   for k in range(5):
    y=430+k*65
    d.ellipse((-120,y,1500,y+180),fill=(120,151,170,18+k*7))
   polygon(d,[(0,610),(250,390),(470,580),(720,300),(1030,610),(1320,410),(1600,620),(1600,900),(0,900)],(23,43,62,255))
   d.ellipse((subject_x-70,170,subject_x+70,310),fill=(223,180,133,220))
 # Fine restrained details; no typography, logos, UI or collage.
 for k in range(28):
  x=(k*173+c*47)%W; y=(k*97+c*31)%H
  if x>W*.72 and safe=="right third": continue
  if x<W*.28 and safe=="left third": continue
  d.ellipse((x,y,x+2,y+2),fill=(245,235,218,45))
 im.convert("RGB").save(out,format="PNG",optimize=True)
 return [W,H]

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--out",type=Path,default=ROOT/"r26-hybrid-pilot")
 ap.add_argument("--limit",type=int,default=4)
 ap.add_argument("--all",action="store_true")
 args=ap.parse_args()
 board=json.loads(BOARD.read_text())
 rows=board["replacements"]
 chosen=rows if args.all else [next(r for r in rows if (r["template"],r["chapter"])==k) for k in PILOT_KEYS]
 chosen=chosen[:args.limit] if not args.all else chosen
 args.out.mkdir(parents=True,exist_ok=True)
 manifest=[]
 for row in chosen:
  path=args.out/row["file"].replace(".jpg",".png")
  dims=render(row,path); raw=path.read_bytes()
  manifest.append({"template":row["template"],"chapter":row["chapter"],"file":path.name,
   "source":"PROCEDURAL_ORIGINAL","sourceType":"procedural-vector-render",
   "trueHighResolutionGenerated":True,"nativeSourceDimensions":dims,
   "generationSystem":"Motion Studio R26 deterministic Pillow scene renderer",
   "generationDate":datetime.now(timezone.utc).isoformat(),
   "sourceReference":"stage9/r26_hybrid_pilot.py#"+row["template"],
   "termsUrl":"https://github.com/Mrs-zhong1/motion-studio-web",
   "commercialUseTermsChecked":False,"sha256":hashlib.sha256(raw).hexdigest(),
   "reviewStatus":"HUMAN_VISUAL_REVIEW_REQUIRED","productionEligible":False})
 (args.out/"replacement.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
 print(json.dumps({"mode":"ZERO_COST_PROCEDURAL_REVIEW_ONLY","generated":len(manifest),
  "dimensions":[W,H],"files":[r["file"] for r in manifest],
  "paidApiCalls":0,"thirdPartyAssets":0,"productionEligible":False},indent=2))
if __name__=="__main__": main()
