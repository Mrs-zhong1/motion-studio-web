import hashlib,json,tempfile,unittest,sys
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from validate_r26_media import validate

class R26MediaValidatorTests(unittest.TestCase):
 def test_33_unique_native_assets_pass_technical_checks_but_stay_on_hold(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); rows=[]
   for i in range(33):
    name=f"scene-{i:02}.png"; path=root/name
    Image.new("RGB",(1600,900),(i*7%255,i*11%255,i*13%255)).save(path)
    raw=path.read_bytes()
    rows.append({"file":name,"sha256":hashlib.sha256(raw).hexdigest(),
     "nativeSourceDimensions":[1600,900],"sourceType":"procedural-3d-render",
     "generationSystem":"Blender test scene","sourceReference":"test.py#scene",
     "generationDate":"2026-11-19T00:00:00Z","thirdPartyAssets":False,
     "embeddedThirdPartyAssets":False,"humanVisualReviewApproved":False,"productionEligible":False})
   manifest=root/"replacement.json";manifest.write_text(json.dumps(rows))
   result=validate(root,manifest)
   self.assertTrue(result["technicalPass"])
   self.assertFalse(result["releaseEligible"])
   self.assertEqual(result["actual"],33)
   self.assertEqual(result["uniqueHashes"],33)
   self.assertEqual(len(result["holds"]),66)
 def test_missing_rights_metadata_fails_for_open_photo(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); path=root/"photo.png"
   Image.new("RGB",(1600,900),(1,2,3)).save(path)
   row={"file":"photo.png","sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
    "nativeSourceDimensions":[1600,900],"sourceType":"open-licensed-photography",
    "humanVisualReviewApproved":False,"productionEligible":False}
   manifest=root/"replacement.json";manifest.write_text(json.dumps([row]))
   result=validate(root,manifest)
   self.assertFalse(result["technicalPass"])
   self.assertTrue(any("originalSourceUrl" in e for e in result["errors"]))

 def test_cc_by_sa_requires_compatibility_review_and_nc_nd_are_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); path=root/"photo.png"
   Image.new("RGB",(1600,900),(30,60,90)).save(path)
   row={"file":"photo.png","sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
    "nativeSourceDimensions":[1600,900],"sourceType":"open-licensed-photography",
    "originalSourceUrl":"https://example.org/photo","creator":"Photographer",
    "licenseId":"CC-BY-SA-4.0","licenseUrl":"https://creativecommons.org/licenses/by-sa/4.0/",
    "attribution":"Photo by Photographer, CC BY-SA 4.0","downloadedAt":"2026-11-19T00:00:00Z",
    "humanVisualReviewApproved":False,"productionEligible":False}
   manifest=root/"replacement.json";manifest.write_text(json.dumps([row]))
   missing_review=validate(root,manifest)
   self.assertFalse(missing_review["technicalPass"])
   self.assertTrue(any("compatibility review" in e for e in missing_review["errors"]))
   row["shareAlikeCompatibilityReviewed"]=True
   manifest.write_text(json.dumps([row]))
   reviewed=validate(root,manifest)
   self.assertTrue(reviewed["technicalPass"],reviewed["errors"])
   row["licenseId"]="CC-BY-NC-4.0"
   manifest.write_text(json.dumps([row]))
   rejected=validate(root,manifest)
   self.assertFalse(rejected["technicalPass"])
   self.assertTrue(any("NC/ND" in e for e in rejected["errors"]))

if __name__=="__main__":unittest.main()
