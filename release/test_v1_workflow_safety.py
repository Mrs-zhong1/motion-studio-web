"""V1 production workflow safety: no artifact drift, no forced Pages rewrite."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DEPLOY=(ROOT/'.github/workflows/web-release-pages.yml').read_text()
ROLLBACK=(ROOT/'.github/workflows/v1-pages-rollback.yml').read_text()
PREFLIGHT=(ROOT/'release/v1_release_preflight.py').read_text()
class WorkflowSafety(unittest.TestCase):
    def test_production_checks_before_deployment(self):
        self.assertIn('branches: [main]',DEPLOY)
        self.assertIn('workflow_dispatch',DEPLOY)
        self.assertIn('V1_APPROVED_SOURCE_SHA',DEPLOY)
        self.assertIn('v1_release_preflight.py --phase candidate',DEPLOY)
        self.assertIn('audit_r32_real_media.py --require-release',DEPLOY)
        self.assertIn("MOTION_REQUIRE_AI_ASSETS: '1'",DEPLOY)
        self.assertIn('test_r33_native_scroll_acceptance.py',DEPLOY)
        self.assertIn('test_r30_cinematic_trial.py',DEPLOY)
    def test_publish_exact_tested_file_without_erasing_review_sites(self):
        self.assertIn('Build EXACT offline HTML once',DEPLOY)
        self.assertIn('cp Motion-Studio-Stage15-Meshopt-OFFLINE.html',DEPLOY)
        self.assertIn('r18-ai-review/index.html',DEPLOY)
        self.assertIn('git push origin HEAD:gh-pages',DEPLOY)
        self.assertNotIn('git push --force',DEPLOY)
        self.assertNotIn('git push -f',DEPLOY)
        self.assertNotIn('git init -b gh-pages',DEPLOY)
        self.assertIn('served_html_matches_tested_release', (ROOT/'stage9/tests/test_live_deployment.py').read_text())
    def test_rollback_is_manual_sha_bounded_and_non_destructive(self):
        self.assertIn('workflow_dispatch',ROLLBACK)
        self.assertIn('ROLLBACK_PRODUCTION_ROOT',ROLLBACK)
        self.assertIn('merge-base --is-ancestor',ROLLBACK)
        self.assertIn('r18-ai-review/index.html',ROLLBACK)
        self.assertNotIn('git push --force',ROLLBACK)
        self.assertIn('sha256',ROLLBACK)
        self.assertIn('git push origin HEAD:gh-pages',ROLLBACK)
    def test_release_signoff_is_externally_sha_bound(self):
        self.assertIn('approved_source_sha!=source_sha',PREFLIGHT)
        self.assertIn('human',PREFLIGHT.lower())
        self.assertIn('productionMediaEligible',PREFLIGHT)
if __name__=='__main__':unittest.main()
