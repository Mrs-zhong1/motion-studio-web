#!/usr/bin/env python3
"""R26: one standalone 2K image request per storyboard chapter.

Dry-run is retained for storyboard inspection only. Paid image generation is disabled
under the R26 zero-cost production decision.
No upscaling/collages: image source is a single model output, inspected at native
dimensions. Output is a staging folder only; does not alter committed originals.
"""
import argparse
import base64
import hashlib
import json
import os
import sys
import time
from datetime import datetime,timezone
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError,URLError
from urllib.request import Request,urlopen
from PIL import Image,UnidentifiedImageError

ROOT=Path(__file__).resolve().parent
BOARD=ROOT/'r26-storyboard.json'
ENDPOINT='https://generativelanguage.googleapis.com/v1beta/interactions'
MODEL='gemini-3.1-flash-image'
TERMS='https://ai.google.dev/gemini-api/terms'

def storyboard(path=BOARD):
    board=json.loads(Path(path).read_text(encoding='utf-8'))
    if board.get('schema')!='motion-studio-r26-storyboard-v1':raise ValueError('invalid storyboard schema')
    rows=board.get('replacements',[])
    if len(rows)!=33:raise ValueError('need exactly 33 individual scenes')
    expected={('editorial',i) for i in (2,3,4)}
    expected|={(t,i) for t in ('product-3d','cinematic','architecture','fashion','gallery') for i in (2,3,4,5)}
    expected|={(t,i) for t in ('agency','saas') for i in (1,2,3,4,5)}
    observed={(x.get('template'),x.get('chapter')) for x in rows}
    if len(observed)!=33 or observed!=expected:raise ValueError('chapter allocation differs from original 33 collage scenes')
    for x in rows:
        if x.get('file')!=f"{x['template']}-{x['chapter']}.jpg":raise ValueError('unsafe output filename')
        if any(not x.get(k) for k in ('subject','artDirection','framing','negative','chapterTitle','storyBeat','textSafeZone')):
            raise ValueError('missing artistic detail '+x['file'])
        if x.get('outputSize')!='2K' or x.get('outputAspectRatio')!='16:9':
            raise ValueError('image generation configuration drift '+x['file'])
    return rows

def prompt(row):
    return ('Generate ONE original standalone 2K photorealistic / art-directed image, 16:9 wide. '
       'This image is ONE scene in a coherent multi-chapter premium interactive web story. '
       f"Template: {row['template']}; chapter {row['chapter']} ({row['storyBeat']}). "
       f"Art direction across story: {row['artDirection']} "
       f"One scene only: {row['subject']}. "
       f"Composition: {row['framing']}. "
       f"Reserve visual space for a separately overlaid HTML title in the {row['textSafeZone']}. "
       'Create accurate material textures, natural illumination, sophisticated depth and controlled grading. '
       'The provided chapter title is only for context, do NOT render it in the image: '
       f"{row['chapterTitle']}. Negative requirements: {row['negative']} "
       'This must be a genuinely new independently generated image, not a crop, resize, collage or contact sheet.')

def extract_image(response):
    """Read current Interactions API model_output or output_image convenience field.

    Text-only completions, multiple images, and incomplete interactions are
    failures; never silently treat them as a successful generated original.
    """
    if response.get('status') not in (None,'completed'):
        raise ValueError('image interaction did not complete: '+str(response.get('status')))
    outputs=[c for step in response.get('steps',[]) if step.get('type')=='model_output'
             for c in step.get('content',[]) if c.get('type')=='image']
    if not outputs and isinstance(response.get('output_image'),dict):
        outputs=[response['output_image']]
    if len(outputs)!=1 or not outputs[0].get('data'):
        raise ValueError('expected exactly one standalone generated image')
    mime=outputs[0].get('mime_type')
    if mime and mime not in ('image/png','image/jpeg','image/webp'):
        raise ValueError('unexpected generated image MIME')
    return base64.b64decode(outputs[0]['data'],validate=True),response.get('id','')

def request_payload(row,model=MODEL):
    return {'model':model,'input':[{'type':'text','text':prompt(row)}],
            'response_format':{'type':'image','mime_type':'image/png','aspect_ratio':'16:9','image_size':'2K'}}

def generate(row,key,model=MODEL):
    body=json.dumps(request_payload(row,model)).encode()
    req=Request(ENDPOINT,data=body,headers={'x-goog-api-key':key,
        'Content-Type':'application/json'},method='POST')
    # Image requests may be billed even when the response is lost. Automatic
    # retries on timeout/429/5xx risk duplicate charges or divergent assets.
    # A failed request is recorded by the operator; rerun only consciously.
    try:
        with urlopen(req,timeout=120) as res:
            response=json.loads(res.read(24_000_000))
            return extract_image(response)
    except HTTPError as exc:
        raise RuntimeError('Gemini image request failed HTTP '+str(exc.code)+
                           '; not retried automatically to prevent duplicate charges') from None
    except (TimeoutError,URLError):
        raise RuntimeError('image request outcome unknown; inspect provider billing before manual rerun') from None

def process_image(raw):
    try:
        with Image.open(BytesIO(raw)) as img:
            img.load()
            width,height=img.size
            if width<1600 or height<900:
                raise ValueError(f'generated native dimensions {width}x{height} below required 1600x900')
            ratio=width/height
            if not 1.68<=ratio<=1.88:
                raise ValueError(f'generated aspect ratio {ratio:.3f} is not 16:9')
            if img.mode!='RGB':img=img.convert('RGB')
            output=BytesIO()
            # Preserve original pixel dimensions while meeting R25 5MB
            # staging limit. Adjust JPEG quality, never resize/upscale.
            for quality in (92,88,82,76):
                output.seek(0);output.truncate(0)
                img.save(output,format='JPEG',quality=quality,optimize=True,subsampling=0)
                data=output.getvalue()
                if 1000<=len(data)<=5_000_000:
                    return data,[width,height]
            raise ValueError('generated JPEG exceeds native asset size limit')
    except (UnidentifiedImageError,OSError) as exc:
        raise ValueError('invalid image bytes') from exc

def run(args):
    if args.generate:
        raise ValueError('Paid Gemini image generation is disabled by the R26 zero-cost hybrid plan; no API call was made')
    rows=storyboard(args.storyboard)
    selection=[x for x in rows if not args.template or x['template']==args.template]
    selection=selection[:args.limit]
    if not args.generate:
        print(json.dumps({'mode':'DRY_RUN_NO_API_CALLS','model':MODEL,'selected':len(selection),
          'scenes':[{'file':r['file'],'prompt':prompt(r)} for r in selection]},ensure_ascii=False,indent=2))
        return
    key=os.environ.get('GEMINI_API_KEY','')
    if not key:raise ValueError('GEMINI_API_KEY required; no paid calls were made')
    if args.authorize_cost!='GENERATE_IMAGES':
        raise ValueError('explicit --authorize-cost GENERATE_IMAGES required; no paid calls made')
    if not args.terms_checked:
        raise ValueError('review AI usage terms and pass --terms-checked; no paid calls made')
    args.out.mkdir(parents=True,exist_ok=True)
    metadata_path=args.out/'replacement.json'
    previous=json.loads(metadata_path.read_text()) if metadata_path.exists() else []
    by_name={r['file']:r for r in previous}
    for row in selection:
        name=row['file']
        if name in by_name and (args.out/name).is_file():
            image_bytes=(args.out/name).read_bytes()
            if hashlib.sha256(image_bytes).hexdigest()==by_name[name].get('sha256'):
                print('SKIP verified existing',name,flush=True);continue
        image,source_id=generate(row,key)
        converted,dimensions=process_image(image)
        # Save each source atomically, followed by a resumable staging manifest.
        temp=args.out/(name+'.tmp')
        temp.write_bytes(converted)
        temp.replace(args.out/name)
        timestamp=datetime.now(timezone.utc).isoformat()
        by_name[name]={
            'template':row['template'],'chapter':row['chapter'],'file':name,
            'source':'AI_GENERATED','sourceType':'individual-generation',
            'trueHighResolutionGenerated':True,'nativeSourceDimensions':dimensions,
            'generationSystem':MODEL,'generationDate':timestamp,
            'sourceReference':source_id or ('generated-'+hashlib.sha256(image).hexdigest()[:16]),
            'termsUrl':TERMS,'commercialUseTermsChecked':True,
            'sha256':hashlib.sha256(converted).hexdigest(),
            'promptSha256':hashlib.sha256(prompt(row).encode()).hexdigest(),
            'originalResponseSha256':hashlib.sha256(image).hexdigest()
        }
        metadata_path.write_text(json.dumps(list(by_name.values()),indent=2,ensure_ascii=False)+chr(10))
        print('STAGED',name,'native',dimensions,'sha256',by_name[name]['sha256'][:12],flush=True)
    print('Staged:',len(by_name),'/33 (NO repository assets were replaced; human review still required)')

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--storyboard',type=Path,default=BOARD)
    p.add_argument('--out',type=Path,default=ROOT/'r26-staging')
    p.add_argument('--template',choices=['editorial','product-3d','cinematic','architecture','agency','fashion','gallery','saas'])
    p.add_argument('--limit',type=int,choices=range(1,34),default=33)
    p.add_argument('--generate',action='store_true',help='perform paid network image generation')
    p.add_argument('--authorize-cost',default='')
    p.add_argument('--terms-checked',action='store_true')
    args=p.parse_args()
    try:run(args)
    except (ValueError,RuntimeError) as e:
        print('R26 stopped safely:',e,file=sys.stderr);return 1
    return 0
if __name__=='__main__':raise SystemExit(main())
