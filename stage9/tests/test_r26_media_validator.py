import hashlib,json,tempfile,unittest
from pathlib import Path
from PIL import Image
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
     "humanVisualReviewApproved":False,"productionEligible":False})
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

if __name__=="__main__":unittest.main()
