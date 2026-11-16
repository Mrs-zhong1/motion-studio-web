"""Web-only release gate must never require native phone hardware."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from check_release import inspect

ROOT = Path(__file__).resolve().parents[1]
VISUAL = json.loads((ROOT / "stage9/visual-evidence/R17_QUALITY_GATE.json").read_text())
APPROVAL = json.loads((ROOT / "release/R18_R21_APPROVALS.json").read_text())

class ReleasePolicyTests(unittest.TestCase):
    def test_old_unsplash_photos_are_review_only(self):
        r = inspect(VISUAL, APPROVAL)
        self.assertEqual(r["result"], "HOLD")
        self.assertFalse(r["nativePhoneHardwareRequired"])
        self.assertTrue(any("AI-generated" in s for s in r["holds"]))
        self.assertFalse(any("physical-device" in s for s in r["holds"]))

    def test_missing_viewport_fails(self):
        x = copy.deepcopy(VISUAL)
        x["geometryAndImageEvidence"].pop()
        self.assertEqual(inspect(x, APPROVAL)["result"], "FAIL")

    def test_unproven_ai_asset_claim_fails(self):
        x = copy.deepcopy(APPROVAL)
        x["aiAssets"] = {"status":"APPROVED", "evidenceUrl":"https://example.com/proof",
          "reviewer":"test", "reviewedAt":"2026-11-16", "assetCount":39}
        self.assertEqual(inspect(VISUAL, x)["result"], "FAIL")

    def test_complete_browser_and_asset_evidence_can_pass(self):
        x = copy.deepcopy(APPROVAL)
        for key in ("artDirection", "aiAssets", "browserPerformance", "productFlows", "browserRegression", "liveIntegrity"):
            x[key] = {"status":"APPROVED", "evidenceUrl":"https://example.com/proof",
              "reviewer":"test", "reviewedAt":"2026-11-16"}
        x["aiAssets"].update(assetCount=39, verifiedOrigin="AI_GENERATED", usageTermsChecked=True)
        self.assertEqual(inspect(VISUAL, x)["result"], "FAIL")
        with tempfile.TemporaryDirectory() as directory:
            images=Path(directory)/"stage9"/"ai-assets"
            images.mkdir(parents=True)
            manifest=[]
            for name in sorted({"editorial", "product-3d", "cinematic", "architecture", "agency", "fashion", "gallery", "saas"}):
                for chapter in range(1, 5 if name=="editorial" else 6):
                    filename=f"{name}-{chapter}.jpg"
                    raw=(filename.encode()*240)[:1600]
                    (images/filename).write_bytes(raw)
                    manifest.append({"template":name,"chapter":chapter,"file":filename,
                        "source":"AI_GENERATED","commercialUseTermsChecked":True,
                        "sha256":hashlib.sha256(raw).hexdigest()})
            (images/"manifest.json").write_text(json.dumps({"assets":manifest}))
            self.assertEqual(inspect(VISUAL, x, directory)["result"], "PASS")
            (images/"editorial-1.jpg").write_bytes(b"corrupted")
            self.assertEqual(inspect(VISUAL, x, directory)["result"], "FAIL")

    def test_legacy_glb_test_selectors_are_unambiguous(self):
        ambiguous = '.comp[data-id="offline-glb-scene"] button'
        offenders=[]
        for path in (ROOT / "stage9/tests").glob("test_*.py"):
            if ambiguous in path.read_text(encoding="utf-8"):
                offenders.append(path.name)
        self.assertEqual(offenders, [], offenders)

    def test_broken_visual_evidence_fails(self):
        x = copy.deepcopy(VISUAL)
        x["geometryAndImageEvidence"][0]["fallbacks"]=1
        self.assertEqual(inspect(x, APPROVAL)["result"], "FAIL")

if __name__ == "__main__":
    unittest.main()
