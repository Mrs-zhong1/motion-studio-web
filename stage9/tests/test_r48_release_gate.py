"""R48: final candidate integrity gate after R47 and Chromium product E2E.

This is a candidate-quality gate only. It never approves deployment or production release.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EDITOR = ROOT / "Motion-Studio-Stage15-Meshopt-OFFLINE.html"
MANIFEST = ROOT / "BUILD_MANIFEST.json"
R47 = ROOT / "R47_ROUNDTRIP_PARITY.json"
E2E = ROOT / "WEB_PRODUCT_E2E_RESULT_chromium.json"
REPORT = ROOT / "R48_RELEASE_GATE.json"
EXPECTED = {"editorial", "product-3d", "cinematic", "architecture", "agency", "fashion", "gallery", "saas"}
result = {
    "status": "HOLD",
    "suite": "R48 reproducible candidate and release-integrity gate",
    "scope": "candidate-only; no deployment, publication, or production signoff",
    "checks": {},
    "evidence": {},
    "errors": [],
}

def check(name, condition, detail=None):
    result["checks"][name] = bool(condition)
    if detail is not None:
        result["evidence"][name] = detail
    if not condition:
        raise AssertionError(name + (": " + str(detail) if detail is not None else ""))

def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

try:
    check("built_editor_exists", EDITOR.is_file())
    check("build_manifest_exists", MANIFEST.is_file())
    check("r47_report_exists", R47.is_file())
    check("chromium_e2e_report_exists", E2E.is_file())

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    r47 = json.loads(R47.read_text(encoding="utf-8"))
    e2e = json.loads(E2E.read_text(encoding="utf-8"))

    templates = set(r47.get("templates", {}).keys())
    check("r47_all_eight_templates_pass", r47.get("pass") is True and templates == EXPECTED,
          {"pass": r47.get("pass"), "templates": sorted(templates)})
    check("chromium_product_e2e_pass", e2e.get("pass") is True,
          {"pass": e2e.get("pass"), "failed_checks": [k for k, v in e2e.get("checks", {}).items() if not v]})
    check("offline_build_manifest", manifest.get("offline") is True)
    check("three_engine_bundle_present", int(manifest.get("engineBytes", 0)) > 100000)
    check("shared_three_engine_bundle_present", int(manifest.get("sharedEngineBytes", 0)) > 100000)
    check("release_not_self_approved", manifest.get("releaseAccepted") is False)
    check("eight_template_catalog_in_build", all(t in EDITOR.read_text(encoding="utf-8") for t in EXPECTED))
    source = EDITOR.read_text(encoding="utf-8")
    check("r45_composition_css_in_editor", 'id="r45-scene-composition-css"' in source)
    check("r46_accessibility_css_in_editor", 'id="r46-responsive-accessibility-css"' in source)

    before_editor = sha(EDITOR)
    before_manifest = sha(MANIFEST)
    build = subprocess.run(["npm", "run", "build"], cwd=ROOT, check=True, text=True,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    after_editor = sha(EDITOR)
    after_manifest = sha(MANIFEST)
    check("reproducible_editor_build", before_editor == after_editor,
          {"before": before_editor, "after": after_editor})
    check("reproducible_build_manifest", before_manifest == after_manifest,
          {"before": before_manifest, "after": after_manifest})
    check("build_log_contains_inline_script_validation",
          "Validated generated executable inline scripts" in build.stdout,
          build.stdout[-1800:])

    result["status"] = "PASS_CANDIDATE_ONLY"
    result["evidence"]["candidate_html_sha256"] = after_editor
    result["evidence"]["manifest_sha256"] = after_manifest
    result["evidence"]["editor_bytes"] = EDITOR.stat().st_size
    result["evidence"]["build_manifest"] = manifest
except Exception as exc:
    result["errors"].append(str(exc))
    result["status"] = "FAIL"

REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
if result["status"] != "PASS_CANDIDATE_ONLY":
    sys.exit(1)
