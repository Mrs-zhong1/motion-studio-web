#!/usr/bin/env python3
"""R32 production-native media audit.

Always inspects the ACTUAL committed JPEG/PNG bytes and source metadata.
Exit 0 in report mode with accurate HOLD; --require-release exits 1 unless
all 39 sources meet the production resolution/provenance screen. Technical
quality pass is necessary but never substitutes human art-direction signoff.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from PIL import Image,UnidentifiedImageError

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'stage9'/'ai-assets'
TEMPLATES=('editorial','product-3d','cinematic','architecture','agency','fashion','gallery','saas')

def audit(asset_dir=ASSETS):
    root=Path(asset_dir)
    manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    records=manifest.get('assets',[])
    errors=[];scenes=[];seen=set();hashes=set()
    expected={(t,c) for t in TEMPLATES for c in range(1,5 if t=='editorial' else 6)}
    if len(records)!=39:errors.append(f'expected 39 chapters; found {len(records)}')
    for asset in records:
        template=asset.get('template');chapter=asset.get('chapter');key=(template,chapter)
        if key not in expected:errors.append(f'unexpected chapter {key}')
        if key in seen:errors.append(f'duplicate chapter {key}')
        seen.add(key)
        filename=asset.get('file','')
        if not isinstance(filename,str) or Path(filename).name!=filename or not filename.endswith(('.jpg','.jpeg','.png')):
            errors.append(f'unsafe filename {filename!r}');continue
        path=root/filename
        if not path.is_file():
            errors.append(f'missing image {filename}');continue
        raw=path.read_bytes()
        digest=hashlib.sha256(raw).hexdigest()
        if digest!=asset.get('sha256'):errors.append(f'invalid SHA256 {filename}')
        if digest in hashes:errors.append(f'duplicate image bytes {filename}')
        hashes.add(digest)
        try:
            with Image.open(path) as im:
                im.load()
                if im.format not in ('PNG','JPEG'):raise ValueError('not PNG/JPEG')
                dimensions=[int(im.width),int(im.height)]
        except (OSError,ValueError,UnidentifiedImageError) as e:
            errors.append(f'undecodable original {filename}: {type(e).__name__}')
            continue
        native=asset.get('nativeSourceDimensions')
        target=asset.get('presentationDimensions')
        dimension_valid=(isinstance(native,list) and len(native)==2 and all(isinstance(x,int) and x>0 for x in native))
        target_valid=(isinstance(target,list) and len(target)==2 and all(isinstance(x,int) and x>0 for x in target))
        if not dimension_valid or not target_valid:
            errors.append(f'invalid original/target dimensions {filename}');continue
        original=(asset.get('sourceType')=='individual-generation' and asset.get('trueHighResolutionGenerated') is True)
        native_enough=(native[0]>=1280 and native[1]>=720)
        amplification=max(target[0]/native[0],target[1]/native[1])
        upscale_ok=amplification<=1.25
        output_ok=(dimensions[0]>=1280 and dimensions[1]>=720)
        # Original pixel size is a provenance claim: a resized JPEG can still
        # report 1600x900. Never infer native resolution from output size.
        risk=[]
        if not original:risk.append('collage_or_not_independently_generated')
        if not native_enough:risk.append('source_native_resolution_insufficient')
        if not upscale_ok:risk.append('upscaled_output_cannot_restore_original_pixels')
        if not output_ok:risk.append('committed_image_output_too_small')
        if not asset.get('commercialUseTermsChecked'):risk.append('usage_terms_not_checked')
        if not all(asset.get(x) for x in ('generationSystem','generationDate','sourceReference','termsUrl')):risk.append('source_provenance_incomplete')
        scenes.append({'template':template,'chapter':chapter,'file':filename,
          'imagePixels':dimensions,'sourceNativePixels':native,'presentationPixels':target,
          'maxSourceAmplification':round(amplification,3),'origin':asset.get('sourceType'),
          'sourceSha256':digest,'sourceReference':asset.get('sourceReference'),
          'technicalRisk':risk,'productionImageCandidate':not risk})
    if seen!=expected:errors.append('incomplete original chapter coverage')
    eligible=[x for x in scenes if x['productionImageCandidate']]
    flagged=[x for x in scenes if x['technicalRisk']]
    summary={'expectedImages':39,'decodedAndCheckedImages':len(scenes),
             'independentGenerationCount':sum(x['origin']=='individual-generation' for x in scenes),
             'collageOrOtherSources':sum(x['origin']!='individual-generation' for x in scenes),
             'technicalCandidateImages':len(eligible),
             'flaggedImages':len(flagged),
             'structuralErrors':errors,
             'productionMediaEligible':not errors and not flagged and len(scenes)==39,
             'humanArtDirection':'HOLD',
             'status':'HOLD' if flagged or errors else 'SOURCE_TECHNICALLY_ELIGIBLE_REQUIRES_HUMAN_REVIEW'}
    by_template=[]
    for template in TEMPLATES:
        rows=[x for x in scenes if x['template']==template]
        by_template.append({'template':template,'chapters':len(rows),
          'flagged':sum(bool(x['technicalRisk']) for x in rows),
          'individualOriginals':sum(x['origin']=='individual-generation' for x in rows),
          'flaggedChapters':[x['chapter'] for x in rows if x['technicalRisk']]})
    return {'schema':'motion-studio-r32-media-audit-v1',
      'summary':summary,'byTemplate':by_template,'scenes':scenes,
      'limitations':['Decodable bytes and recorded provenance do not verify generated artwork subject continuity',
                     'A resized/upscaled file can pass image pixel checks; native source origin is audited separately',
                     'Technical media eligibility does not provide professional art-direction signoff']}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--assets',type=Path,default=ASSETS)
    p.add_argument('--out',type=Path)
    p.add_argument('--require-release',action='store_true')
    args=p.parse_args()
    report=audit(args.assets)
    print(json.dumps(report['summary'],indent=2,ensure_ascii=False))
    for row in report['byTemplate']:
        print(f"{row['template']}: {row['individualOriginals']} individual, {row['flagged']} flagged: {row['flaggedChapters']}")
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+chr(10),encoding='utf-8')
    if args.require_release and not report['summary']['productionMediaEligible']:
        raise SystemExit('R32 FAIL CLOSED: insufficient verified original high-resolution art')
if __name__=='__main__':main()
