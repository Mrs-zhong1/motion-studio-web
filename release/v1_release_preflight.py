#!/usr/bin/env python3
"""V1.0 fail-closed release candidate/production acceptance.

Candidate gate is run before deployment: all five pre-production signoffs
must be tied to the exact checkout SHA. Live integrity is verified only AFTER
deployment (two-phase release, avoiding impossible prior live approval).
The media audit decodes all 39 actual sources with Pillow. Neither test code
nor old R17 screenshots count as contemporary art-direction signoff.
"""
import argparse,json,os,sys
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'stage9'))
from audit_r32_real_media import audit
sys.path.insert(0,str(ROOT/'release'))
from check_release import verify_committed_ai_assets

PRE_KEYS=('artDirection','aiAssets','browserPerformance','productFlows','browserRegression')
BOT_TERMS=('github actions','github-actions','automated','bot','synthetic')

def examine(source_sha,phase='candidate',root=ROOT,approvals_path=None,approved_source_sha='',verified_live_sha=''):
    root=Path(root)
    approvals_path=Path(approvals_path or (root/'release/R18_R21_APPROVALS.json'))
    approvals=json.loads(approvals_path.read_text(encoding='utf-8'))
    result={'schema':'motion-studio-v1-prod-gate-v1','phase':phase,'sourceCommit':source_sha,
      'status':'HOLD','productionEligible':False,'failed':[],'holds':[],'verified':[]}
    if not isinstance(source_sha,str) or len(source_sha)!=40 or any(c not in '0123456789abcdef' for c in source_sha):
        result['failed'].append('No verified 40-character source commit SHA')
    # A source commit cannot contain its OWN SHA in the committed approvals JSON.
    # Instead, the explicit SHA approval is recorded as an external GitHub
    # Actions variable after reviewers approve that immutable commit.
    if approved_source_sha!=source_sha:
        result['holds'].append('GitHub V1_APPROVED_SOURCE_SHA must match the exact immutable candidate SHA')
    for key in PRE_KEYS:
        data=approvals.get(key) or {}
        if data.get('status')!='APPROVED':
            result['holds'].append(f'{key}: explicit signoff missing')
            continue
        if not all(isinstance(data.get(x),str) and data[x].strip() for x in ('reviewer','reviewedAt','evidenceUrl')):
            result['failed'].append(f'{key}: approval provenance incomplete')
            continue
        if key=='artDirection':
            reviewer=data['reviewer'].strip().lower()
            if any(word in reviewer for word in BOT_TERMS):
                result['failed'].append('artDirection must be reviewed by a person, not a CI robot')
            else:
                result['verified'].append('Human art direction signoff exists (not independently scored)')
        result['verified'].append(f'{key} signoff recorded')
    try:
        image=audit(root/'stage9/ai-assets')
        result['mediaAudit']=image['summary']
        if not image['summary']['productionMediaEligible']:
            result['holds'].append(f"R32 original images: {image['summary']['flaggedImages']} flagged scenes")
        result['failed'].extend(image['summary']['structuralErrors'])
    except (OSError,ValueError,TypeError,json.JSONDecodeError) as exc:
        result['failed'].append('Source media verification unavailable: '+str(exc))
    result['failed'].extend(verify_committed_ai_assets(root))
    if phase=='live':
        live=approvals.get('liveIntegrity') or {}
        if live.get('status')!='APPROVED' or not all(live.get(x) for x in ('evidenceUrl','reviewer','reviewedAt')):
            result['holds'].append('Production liveIntegrity approval and SHA-bound deployment check missing')
        elif verified_live_sha!=source_sha:
            result['holds'].append('Post-deploy verified live SHA must match exact deployed source commit')
    result['failed']=sorted(set(result['failed']))
    result['holds']=sorted(set(result['holds']))
    result['status']='FAIL' if result['failed'] else ('HOLD' if result['holds'] else 'PASS')
    result['productionEligible']=result['status']=='PASS'
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--phase',choices=['candidate','live'],default='candidate')
    p.add_argument('--source-sha',default=os.environ.get('GITHUB_SHA',''))
    p.add_argument('--approved-source-sha',default=os.environ.get('V1_APPROVED_SOURCE_SHA',''))
    p.add_argument('--verified-live-sha',default=os.environ.get('V1_VERIFIED_LIVE_SHA',''))
    p.add_argument('--out',type=Path)
    p.add_argument('--allow-hold',action='store_true',help='report-only for review; never use with production publish')
    args=p.parse_args()
    r=examine(args.source_sha,args.phase,approved_source_sha=args.approved_source_sha,verified_live_sha=args.verified_live_sha)
    print(json.dumps(r,ensure_ascii=False,indent=2))
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+chr(10),encoding='utf-8')
    return 0 if (r['productionEligible'] or args.allow_hold) else 1

if __name__=='__main__':raise SystemExit(main())
