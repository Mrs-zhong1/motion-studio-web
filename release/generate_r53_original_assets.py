#!/usr/bin/env python3
"""Generate deterministic, original 16:9 visual assets for all R53 slots.

No external image API, stock photo, remote URL, font download, or third-party image is used.
All artwork is created from primitive drawing operations with Pillow.
Generation populates evidence only; it NEVER grants humanVisualApproval or productionEligible.
"""
import hashlib, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
REGISTER=ROOT/"release/R53_PRODUCTION_ASSET_REGISTER.json"
OUT=ROOT/"stage9/ai-assets"
GENERATOR=Path(__file__).resolve()
W,H=1600,900
PALETTES={
 "agency":((13,22,27),(218,255,103),(242,239,226)),
 "product-3d":((12,17,29),(96,190,255),(235,241,250)),
 "gallery":((22,20,29),(236,183,122),(245,239,226)),
 "saas":((14,39,29),(169,242,120),(239,247,235)),
 "architecture":((31,43,48),(208,190,155),(239,232,214)),
 "cinematic":((9,15,28),(231,107,73),(240,226,207)),
 "editorial":((37,31,27),(211,184,144),(245,237,220)),
 "fashion":((31,20,28),(224,147,166),(246,230,224)),
}
def mix(a,b,t): return tuple(round(a[i]*(1-t)+b[i]*t) for i in range(3))
def make_art(row):
    template=row["template"]; chapter=int(row["chapter"]); base,accent,light=PALETTES[template]
    seed=int(hashlib.sha256(row["slotId"].encode()).hexdigest()[:8],16); rng=random.Random(seed)
    im=Image.new("RGB",(W,H)); px=im.load()
    for y in range(H):
        t=y/(H-1)
        c=mix(base,tuple(max(0,int(v*.55)) for v in base),t*.8)
        for x in range(W): px[x,y]=mix(c,base,min(.18,abs(x-W*.5)/W*.12))
    d=ImageDraw.Draw(im,"RGBA")
    # Subtle grain/grid creates a designed surface without external textures.
    for x in range(0,W,80): d.line((x,0,x,H),fill=(*light,12),width=1)
    for y in range(0,H,80): d.line((0,y,W,y),fill=(*light,10),width=1)
    cx=int(W*(.48+rng.uniform(-.08,.08))); cy=int(H*(.48+rng.uniform(-.08,.08)))
    if template in ("agency","cinematic","fashion"):
        for i in range(8):
            x=int(W*(.18+i*.09)); y=int(H*(.18+rng.random()*.5))
            d.polygon([(x,y),(x+int(W*.22),y-int(H*.12)),(x+int(W*.17),y+int(H*.52)),(x-int(W*.04),y+int(H*.4))],fill=(*accent,20+i*3))
        d.ellipse((cx-210,cy-210,cx+210,cy+210),outline=(*accent,190),width=5)
        d.arc((cx-310,cy-310,cx+310,cy+310),20,300,fill=(*light,160),width=3)
    elif template in ("product-3d","gallery"):
        for i in range(6):
            r=70+i*44
            d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(*accent,180-i*18),width=3)
        d.polygon([(cx,cy-230),(cx+190,cy-90),(cx+145,cy+170),(cx,cy+260),(cx-160,cy+140),(cx-190,cy-100)],fill=(*accent,50),outline=(*light,210))
        d.line((cx-260,cy+260,cx+270,cy-250),fill=(*light,170),width=3)
    elif template=="saas":
        for i in range(4):
            x=180+i*300; y=230+(i%2)*80
            d.rounded_rectangle((x,y,x+230,y+360),radius=22,fill=(*light,16),outline=(*accent,170),width=3)
            d.rounded_rectangle((x+24,y+34,x+190,y+54),radius=8,fill=(*accent,190))
            for j in range(5): d.rounded_rectangle((x+24,y+95+j*42,x+190-rng.randint(0,55),y+108+j*42),radius=5,fill=(*light,85))
        d.line((280,700,1320,700),fill=(*accent,180),width=4)
    elif template=="architecture":
        horizon=610
        for i in range(7):
            x=120+i*205; height=220+rng.randint(0,280); width=120+rng.randint(0,70)
            d.rectangle((x,horizon-height,x+width,horizon),fill=(*accent,35),outline=(*light,170),width=3)
            for yy in range(horizon-height+30,horizon-15,45):
                for xx in range(x+18,x+width-12,35): d.rectangle((xx,yy,xx+12,yy+22),fill=(*light,100))
        d.line((70,horizon,1530,horizon),fill=(*accent,210),width=4)
    elif template=="editorial":
        d.rectangle((180,110,1420,790),outline=(*accent,190),width=3)
        d.rectangle((230,160,860,740),fill=(*accent,35))
        for i in range(12):
            y=205+i*42; d.line((930,y,1370-rng.randint(0,180),y),fill=(*light,120),width=5)
        d.ellipse((450,280,760,590),outline=(*light,180),width=4)
    # Chapter marker and abstract typography are intentionally original.
    d.rounded_rectangle((70,70,330,124),radius=26,fill=(*accent,235))
    d.text((92,86),f"{template.upper()} / {chapter:02d}",fill=base)
    d.text((72,820),"MOTION STUDY     •     ORIGINAL GENERATIVE ARTWORK",fill=(*light,180))
    # Controlled soft bloom keeps the graphic surfaces polished.
    glow=im.filter(ImageFilter.GaussianBlur(18))
    im=Image.blend(im,glow,.10)
    return im

def make_saas_svg(row):
    """Create native, editable SVG product-interface artwork for SaaS slots."""
    chapter=int(row["chapter"])
    seed=int(hashlib.sha256(row["slotId"].encode()).hexdigest()[:8],16)
    rng=random.Random(seed)
    accent="#a9f278" if chapter%2 else "#8de4c5"
    dark="#0e271d"; panel="#17382b"; pale="#eff7eb"; muted="#a9c3b2"
    cards=[]
    labels=[("CAPTURE","Signals collected","24 new signals"),("SHAPE","Work made clear","08 priorities"),("DELIVER","Ready to move","03 outcomes"),("INSIGHTS","Patterns surfaced","12 useful signals"),("REVIEW","Progress in view","96% complete")]
    for i,(tag,title,meta) in enumerate(labels):
        x=150+i*265; y=260+(i%2)*42
        bars="".join('<rect x="{0}" y="{1}" width="{2}" height="7" rx="3.5" fill="{3}" opacity=".7"/>'.format(x+24,y+160+j*25,130+rng.randint(0,55),muted) for j in range(5))
        cards.append('<g><rect x="{x}" y="{y}" width="225" height="340" rx="18" fill="{panel}" stroke="{accent}" stroke-opacity=".55"/><rect x="{a}" y="{b}" width="76" height="22" rx="11" fill="{accent}"/><text x="{c}" y="{d}" text-anchor="middle" font-size="10" font-weight="700" fill="{dark}">{tag}</text><text x="{e}" y="{f}" font-size="18" font-weight="700" fill="{pale}">{title}</text><text x="{g}" y="{h}" font-size="12" fill="{muted}">{meta}</text>{bars}<circle cx="{i}" cy="{j}" r="13" fill="{accent}" opacity=".9"/></g>'.format(x=x,y=y,panel=panel,accent=accent,a=x+22,b=y+22,c=x+60,d=y+37,dark=dark,tag=tag,e=x+22,f=y+94,pale=pale,g=x+22,h=y+122,muted=muted,meta=meta,title=title,bars=bars,i=x+184,j=y+292))
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900" role="img"><title>SaaS workflow composition {0}</title><desc>Original native vector interface study showing capture, shape and deliver.</desc><defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#102d22"/><stop offset="1" stop-color="#091b15"/></linearGradient><radialGradient id="glow"><stop stop-color="{1}" stop-opacity=".24"/><stop offset="1" stop-color="{1}" stop-opacity="0"/></radialGradient></defs><rect width="1600" height="900" fill="url(#bg)"/><circle cx="1260" cy="120" r="480" fill="url(#glow)"/><g opacity=".12" stroke="{2}"><path d="M0 180H1600M0 720H1600M120 0V900M1480 0V900"/></g><text x="100" y="110" fill="{1}" font-size="18" letter-spacing="5">MOTION STUDIO / SAAS</text><text x="100" y="185" fill="{2}" font-size="52" font-weight="700">A clearer way to move work forward.</text><text x="100" y="222" fill="{3}" font-size="18">ORIGINAL PRODUCT INTERFACE STUDY / {0:02d}</text>{4}<path d="M245 700H1360" stroke="{1}" stroke-width="3" stroke-opacity=".7"/><text x="100" y="790" fill="{3}" font-size="14" letter-spacing="3">CAPTURE → SHAPE → DELIVER</text><text x="100" y="835" fill="{2}" font-size="12" opacity=".65">GENERATED VECTOR ARTWORK · NO THIRD-PARTY ASSETS</text></svg>').format(chapter,accent,pale,muted,"".join(cards))


def main():
    doc=json.loads(REGISTER.read_text(encoding="utf-8")); rows=doc.get("assets",[])
    if len(rows)!=33: raise SystemExit(f"Expected 33 slots, got {len(rows)}")
    OUT.mkdir(parents=True,exist_ok=True)
    source_hash=hashlib.sha256(GENERATOR.read_bytes()).hexdigest()
    for row in rows:
        slot=row["slotId"]
        if row["template"]=="saas":
            filename=slot+".svg"; path=OUT/filename
            path.write_text(make_saas_svg(row),encoding="utf-8")
        else:
            filename=slot+".png"; path=OUT/filename
            image=make_art(row); image.save(path,"PNG",optimize=True)
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        row.update({
            "mediaClass":"procedural","sourceType":"procedural-original-generative-art",
            "file":filename,"sha256":digest,
            "sourceCodePath":"release/generate_r53_original_assets.py",
            "sourceCodeSha256":source_hash,"nativeDimensions":[W,H],
            "thirdPartyAssets":False,"commercialUseTermsChecked":True,
            "humanVisualApproval":False,"productionEligible":False,
            "reviewStatus":"GENERATED_REVIEW_REQUIRED"
        })
        for key in ("creator","sourcePageUrl","licenseId","licenseUrl","attribution","downloadedAtUtc","shareAlikeCompatibilityReviewed"):
            row.pop(key,None)
    doc["status"]="HOLD"
    doc["note"]="33 deterministic original procedural artworks generated from repository source; SaaS slots use native SVG and other slots use PNG. No external imagery or API. Human visual approval and production eligibility remain false until reviewed."
    REGISTER.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"generated":len(rows),"dimensions":[W,H],"sourceSha256":source_hash,"externalApis":False,"humanVisualApproval":False,"productionEligible":False},indent=2))
if __name__=="__main__": main()
