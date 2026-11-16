#!/usr/bin/env python3
"""R27 offline source-quality contact sheets and visual review gallery.

Works on R26 staging artifacts only. Uses actual original JPEG files, not
reconstructed/upscaled placeholders. Writes a local index.html plus one strip
per template. No network or provider API calls. Does not approve images.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps

TEMPLATES=('editorial','product-3d','cinematic','architecture','agency','fashion','gallery','saas')

def make_gallery(staging,storyboard,out):
    staging,storyboard,out=Path(staging),Path(storyboard),Path(out)
    assets=json.loads((staging/'replacement.json').read_text(encoding='utf-8'))
    scenes=json.loads(storyboard.read_text(encoding='utf-8'))['replacements']
    scene_map={(r['template'],r['chapter']):r for r in scenes}
    if len({(r.get('template'),r.get('chapter')) for r in assets})!=len(assets):
        raise ValueError('Duplicate review scene')
    output=[]
    by_template={t:[] for t in TEMPLATES}
    for row in assets:
        key=(row['template'],row['chapter'])
        if key not in scene_map:raise ValueError('Unknown review chapter '+str(key))
        path=staging/row['file']
        if path.name!=row['file']:raise ValueError('Invalid image file path')
        raw=path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=row.get('sha256'):
            raise ValueError('Image hash mismatch '+row['file'])
        with Image.open(path) as image:
            image.load()
            if list(image.size)!=row['nativeSourceDimensions']:
                raise ValueError('Image dimensions mismatch '+row['file'])
            if image.width<1600 or image.height<900:
                raise ValueError('Low-native-resolution review image '+row['file'])
            thumb=ImageOps.fit(image.convert('RGB'),(512,288),method=Image.Resampling.LANCZOS)
        by_template[key[0]].append((row,scene_map[key],thumb))
    out.mkdir(parents=True,exist_ok=True)
    styles="body{background:#101316;color:#e9edf0;font:15px system-ui;margin:0 auto;padding:30px;max-width:1200px}h1{letter-spacing:-.05em}h2{margin:48px 0 14px}.note{color:#aab3b7}.sheet{width:100%;border:1px solid #353c42;border-radius:12px}.meta{font-size:13px;color:#b2bbc2}.warning{color:#f0c99c}.nav{display:flex;gap:12px;flex-wrap:wrap}.nav a{color:#afdbe9}.card{border:1px solid #343b3f;margin:12px 0;padding:15px;border-radius:10px}.status{color:#f0c99c}"
    sections=[]
    report=[]
    for template in TEMPLATES:
        entries=sorted(by_template[template],key=lambda v:v[0]['chapter'])
        if not entries:continue
        strip=Image.new('RGB',(512*len(entries),328),'#101316')
        pen=ImageDraw.Draw(strip)
        cards=[]
        for i,(row,scene,thumb) in enumerate(entries):
            strip.paste(thumb,(i*512,0))
            pen.text((i*512+15,295),f"{template} / {row['chapter']}  {row['nativeSourceDimensions'][0]}x{row['nativeSourceDimensions'][1]}",fill='#f6f6f6')
            cards.append(f'<div class="card"><b>CH {row["chapter"]} — {html.escape(scene["chapterTitle"])}</b><p class="meta">{html.escape(scene["subject"])}</p><p class="meta">File: {html.escape(row["file"])} · native: {row["nativeSourceDimensions"][0]}×{row["nativeSourceDimensions"][1]} · sha256: {row["sha256"][:16]}</p></div>')
            report.append({'template':template,'chapter':row['chapter'],'file':row['file'],
                           'sha256':row['sha256'],'native':row['nativeSourceDimensions'],
                           'sourceRecorded':row.get('sourceType')})
        strip_name=f'{template}-review-strip.jpg'
        strip.save(out/strip_name,format='JPEG',quality=88,optimize=True)
        sections.append(f'<section id="{template}"><h2>{template} — {len(entries)} scene(s)</h2><img class="sheet" src="{strip_name}" alt="{template} contact strip" />'+''.join(cards)+'</section>')
    links=''.join(f'<a href="#{t}">{t}</a>' for t in TEMPLATES if by_template[t])
    body='<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R27 Source Visual Review</title><style>'+styles+'</style></head><body><h1>R27 / Original Image Review</h1><p class="warning">REVIEW ONLY — no automated image aesthetic approval. These are real staging images.</p><nav class="nav">'+links+'</nav>'+''.join(sections)+'</body></html>'
    (out/'index.html').write_text(body,encoding='utf-8')
    (out/'inventory.json').write_text(json.dumps({'schema':'motion-studio-r27-gallery-v1','count':len(report),
       'artDirectionStatus':'HOLD','assets':report},indent=2,ensure_ascii=False)+chr(10),encoding='utf-8')
    return {'reviewedForFileIntegrity':len(report),'templateStrips':len(sections),'artDirectionApproved':False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('staging',type=Path)
    p.add_argument('--storyboard',type=Path,default=Path(__file__).resolve().parent/'r26-storyboard.json')
    p.add_argument('--out',type=Path,default=Path(__file__).resolve().parent/'r27-review-gallery')
    args=p.parse_args()
    print(json.dumps(make_gallery(args.staging,args.storyboard,args.out),indent=2))
if __name__=='__main__':main()
