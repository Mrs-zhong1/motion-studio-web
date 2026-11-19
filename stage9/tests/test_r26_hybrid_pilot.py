import hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
class HybridPilotTests(unittest.TestCase):
 def test_four_native_independent_scenes_and_zero_paid_calls(self):
  with tempfile.TemporaryDirectory() as td:
   out=Path(td)/"pilot"
   run=subprocess.run([sys.executable,str(ROOT/"r26_hybrid_pilot.py"),"--out",str(out)],
    check=True,capture_output=True,text=True)
   report=json.loads(run.stdout)
   self.assertEqual(report["generated"],4)
   self.assertEqual(report["paidApiCalls"],0)
   self.assertFalse(report["productionEligible"])
   rows=json.loads((out/"replacement.json").read_text())
   self.assertEqual(len(rows),4)
   self.assertEqual(len({r["sha256"] for r in rows}),4)
   for row in rows:
    raw=(out/row["file"]).read_bytes()
    self.assertEqual(hashlib.sha256(raw).hexdigest(),row["sha256"])
    with Image.open(out/row["file"]) as im:
     self.assertEqual(im.size,(1600,900))
     self.assertEqual(im.format,"PNG")
    self.assertEqual(row["sourceType"],"procedural-vector-render")
    self.assertFalse(row["commercialUseTermsChecked"])
 def test_all_33_storyboard_slots_are_accounted_for(self):
  board=json.loads((ROOT/"r26-storyboard.json").read_text())
  rows=board["replacements"]
  self.assertEqual(len(rows),33)
  keys={(r["template"],r["chapter"]) for r in rows}
  self.assertEqual(len(keys),33)
  self.assertEqual(len({r["file"] for r in rows}),33)
 def test_blender_pilot_source_compiles_and_targets_real_storyboard_slots(self):
  source=(ROOT/"r26_blender_pilot.py").read_text()
  compile(source,str(ROOT/"r26_blender_pilot.py"),"exec")
  board=json.loads((ROOT/"r26-storyboard.json").read_text())
  slots={(r["template"],r["chapter"]) for r in board["replacements"]}
  expected={("editorial",2),("product-3d",3),("architecture",2),("agency",1)}
  self.assertTrue(expected.issubset(slots))
  for forbidden in ("requests.post(","GEMINI_API_KEY","fal.ai","replicate.com"):
   self.assertNotIn(forbidden,source)
if __name__=="__main__":unittest.main()
