"""Unit tests for release policy; no browser or external dependencies required."""
import copy
import json
import unittest
from pathlib import Path
from check_release import inspect

ROOT = Path(__file__).resolve().parents[1]
VISUAL = json.loads((ROOT.parent / "stage9/visual-evidence/R17_QUALITY_GATE.json").read_text())
APPROVAL = json.loads((ROOT / "R18_R21_APPROVALS.json").read_text())

class ReleasePolicyTests(unittest.TestCase):
    def test_evidence_is_complete_but_release_held(self):
        out = inspect(VISUAL, APPROVAL)
        self.assertEqual(out["result"], "HOLD", out)
        self.assertFalse(out["failures"])
        self.assertFalse(out["productionEligible"])
        self.assertTrue(any("art-direction" in s for s in out["holds"]))
        self.assertTrue(any("commercial clearance" in s for s in out["holds"]))

    def test_missing_template_is_failure(self):
        evidence = copy.deepcopy(VISUAL)
        evidence["geometryAndImageEvidence"].pop()
        self.assertEqual(inspect(evidence, APPROVAL)["result"], "FAIL")

    def test_approval_without_source_evidence_never_overrides_rights(self):
        a = copy.deepcopy(APPROVAL)
        for name in ("artDirection", "nativeDevice", "rightsRegister", "productFlows", "browserRegression", "liveIntegrity"):
            a[name] = {"status":"APPROVED", "evidenceUrl":"https://example.com/evidence",
                       "reviewer":"test", "reviewedAt":"2026-11-16"}
        self.assertEqual(inspect(VISUAL, a)["result"], "HOLD")

    def test_image_fallback_fails(self):
        evidence = copy.deepcopy(VISUAL)
        evidence["geometryAndImageEvidence"][0]["fallbacks"] = 1
        self.assertEqual(inspect(evidence, APPROVAL)["result"], "FAIL")

if __name__ == "__main__":
    unittest.main()
