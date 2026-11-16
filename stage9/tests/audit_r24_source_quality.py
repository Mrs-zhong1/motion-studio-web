"""R24 source-native image-quality gate. No synthetic sharpness claim.

Reports image quality risk using original source dimensions, not upscaled output.
Use --enforce to block any remaining low-source-resolution chapter. No fabricated
image sharpness, aesthetic rating or human approval.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'ai-assets'/'manifest.json'
REPORT=ROOT/'R24_MEDIA_QUALITY_GATE.json'
TEMPLATES=('editorial','product-3d','cinematic','architecture','agency','fashion','gallery','saas')
EXPECTED={'editorial':4,**{x:5 for x in TEMPLATES if x!='editorial'}}

def run(enforce=False):
    data=json.loads(MANIFEST.read_text())
    rows=data.get('assets',[])
    issues=[]
    if len(rows)!=39: issues.append(f'Expected 39 source entries, found {len(rows)}')
    scene_counts=Counter(r.get('template') for r in rows)
    for template,count in EXPECTED.items():
        if scene_counts.get(template)!=count:
            issues.append(f'{template}: expected {count} chapters, found {scene_counts.get(template,0)}')
    evidence=[]
    seen=set()
    for item in rows:
        t=item.get('template')
        ch=item.get('chapter')
        key=(t,ch)
        if key in seen: issues.append(f'Duplicate chapter {key}')
        seen.add(key)
        native=item.get('nativeSourceDimensions') or [0,0]
        target=item.get('presentationDimensions') or [0,0]
        if not isinstance(native,list) or len(native)!=2 or not isinstance(target,list) or len(target)!=2:
            issues.append(f'{key}: invalid dimension metadata')
            continue
        nw,nh=native; tw,th=target
        if min(nw,nh,tw,th)<=0: issues.append(f'{key}: missing positive dimension')
        sx=round(tw/nw,3) if nw else None
        sy=round(th/nh,3) if nh else None
        enlarged=max(sx or 0,sy or 0)
        source_pixels=nw*nh
        upscale=enlarged>1.25
        short_side=min(nw,nh)<720
        ratio_shift=abs((nw/nh)-(tw/th))>0.25 if nh and th else True
        collage=item.get('sourceType')=='crop-of-AI-generated-collage'
        risk=any((upscale,short_side,ratio_shift,collage))
        if not item.get('sha256') or len(item['sha256'])!=64:
            issues.append(f'{key}: source SHA256 missing')
        if not item.get('commercialUseTermsChecked'):
            issues.append(f'{key}: source commercial terms not reviewed')
        evidence.append({
          'template':t,'chapter':ch,'file':item.get('file'),
          'sourceType':item.get('sourceType'),'nativeSourceDimensions':native,
          'presentationDimensions':target,'nativePixels':source_pixels,
          'scaleX':sx,'scaleY':sy,'maxEnlargement':enlarged,
          'collageDerived':collage,'nativeShortSideUnder720':short_side,
          'enlargedOver125Percent':upscale,'aspectRatioShift':ratio_shift,
          'requiresSourceReplacementReview':risk})
    flagged=[x for x in evidence if x['requiresSourceReplacementReview']]
    summary={'totalScenes':len(evidence),'uniqueChapters':len(seen),
       'collageDerived':sum(x['collageDerived'] for x in evidence),
       'needsReplacementReview':len(flagged),
       'passedSourceQualityScreen':len(evidence)-len(flagged),
       'structuralErrors':issues,
       'productionReady':not issues and not flagged and len(evidence)==39,
       'humanArtDirection':'HOLD',
       'limitations':'Dimensions and origin prove possible upscaling/collage risks, not perceptual blur, beauty or actual subjective art direction.'}
    result={'schema':'motion-studio-r24-source-quality-v1','summary':summary,
       'flaggedChapters':flagged,'allScenes':evidence}
    REPORT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(summary,ensure_ascii=False))
    if issues: raise SystemExit('R24 structural media validation failed: '+str(issues))
    if enforce and flagged: raise SystemExit(f'R24 PRODUCTION HOLD: {len(flagged)} chapters require native-resolution review')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--enforce',action='store_true')
    run(parser.parse_args().enforce)
