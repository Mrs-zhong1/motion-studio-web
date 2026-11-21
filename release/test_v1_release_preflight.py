"""V1 candidate and live production preflight tests (synthetic fixtures only)."""
import hashlib,json,sys,tempfile,unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parent))
from v1_release_preflight import examine
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'stage9'))
from audit_r32_real_media import TEMPLATES
SHA='a'*40
class CandidateTests(unittest.TestCase):
 def fixtures(self,root):
  release=root/'release';release.mkdir()
  assets=root/'stage9/ai-assets';assets.mkdir(parents=True)
  rows=[]
  for ti,t in enumerate(TEMPLATES):
   for chapter in range(1,5 if t=='editorial' else 6):
    filename=f'{t}-{chapter}.jpg'
    Image.new('RGB',(1600,900),(15+ti*24,chapter*31,20+ti*9)).save(assets/filename,'JPEG')
    raw=(assets/filename).read_bytes()
    rows.append(dict(template=t,chapter=chapter,file=filename,sha256=hashlib.sha256(raw).hexdigest(),
       source='AI_GENERATED',sourceType='individual-generation',trueHighResolutionGenerated=True,
       nativeSourceDimensions=[1600,900],presentationDimensions=[1600,900],
       generationSystem='fixture',generationDate='2026-11-16',
       sourceReference=filename,termsUrl='https://example.com/terms',
       commercialUseTermsChecked=True))
  (assets/'manifest.json').write_text(json.dumps({'assets':rows}))
  approvals={'sourceCommit':'old-stale-commit-can-not-possibly-match-its-own-file'}
  for key in ('artDirection','aiAssets','browserPerformance','productFlows','browserRegression','liveIntegrity'):
   approvals[key]={'status':'APPROVED','reviewer':'human reviewer' if key=='artDirection' else 'automation reviewer',
      'reviewedAt':'2026-11-16','evidenceUrl':'https://example.com/evidence'}
  approvals['aiAssets'].update(assetCount=39,verifiedOrigin='AI_GENERATED',usageTermsChecked=True)
  (release/'R18_R21_APPROVALS.json').write_text(json.dumps(approvals))
  return approvals,rows
 def test_two_phase_release_has_independent_sha_binding(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)
   approvals,rows=self.fixtures(root)
   self.assertEqual(examine(SHA,root=root)['status'],'HOLD')
   candidate=examine(SHA,root=root,approved_source_sha=SHA)
   self.assertEqual(candidate['status'],'PASS')
   self.assertEqual(examine(SHA,'live',root=root,approved_source_sha=SHA)['status'],'HOLD')
   approvals['liveIntegrity']['verifiedCommit']=SHA
   (root/'release/R18_R21_APPROVALS.json').write_text(json.dumps(approvals))
   self.assertEqual(examine(SHA,'live',root=root,approved_source_sha=SHA,verified_live_sha=SHA)['status'],'PASS')
   approvals['artDirection']['reviewer']='GitHub Actions bot'
   (root/'release/R18_R21_APPROVALS.json').write_text(json.dumps(approvals))
   self.assertEqual(examine(SHA,root=root,approved_source_sha=SHA)['status'],'FAIL')
   approvals['artDirection']['reviewer']='human reviewer'
   (root/'release/R18_R21_APPROVALS.json').write_text(json.dumps(approvals))
   rows[0]['sourceType']='crop-of-AI-generated-collage'
   (root/'stage9/ai-assets/manifest.json').write_text(json.dumps({'assets':rows}))
   self.assertEqual(examine(SHA,root=root,approved_source_sha=SHA)['status'],'HOLD')
if __name__=='__main__':unittest.main()
