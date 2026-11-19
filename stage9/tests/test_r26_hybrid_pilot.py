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
 def test_all_33_storyboard_slots_can_render_without_network(self):
  with tempfile.TemporaryDirectory() as td:
   out=Path(td)/"all"
   run=subprocess.run([sys.executable,str(ROOT/"r26_hybrid_pilot.py"),"--all","--out",str(out)],
    check=True,capture_output=True,text=True)
   report=json.loads(run.stdout)
   self.assertEqual(report["generated"],33)
   self.assertEqual(len(list(out.glob("*.png"))),33)
if __name__=="__main__":unittest.main()
