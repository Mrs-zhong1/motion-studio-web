#!/usr/bin/env python3
"""R12 production-release evidence gate. Fail closed: no assertions without evidence."""
import argparse
import json
import sys
from pathlib import Path

REQUIRED = {
    "source_ci": "All current source E2E and offline 3D jobs pass at the exact release SHA",
    "pages_live_smoke": "HTTPS live editor, preview, export, and bundled WebGL scene pass at release SHA",
    "native_macos_safari": "Real macOS Safari visual/editor/export/3D and fallback hands-on test",
    "physical_mobile": "Real iPhone/Android touch, scroll, fallback and visibility test",
    "hardware_gpu_stability": "Hardware WebGL 30-minute stability, memory and thermal readings",
    "visual_design_signoff": "Human review of gallery, chapters, type, motion and 3D model against references",
    "media_license_signoff": "Itemized reusable media/model rights cleared for distribution",
}
def check(evidence):
    failures = []
    if not isinstance(evidence, dict):
        return ["Evidence must be a JSON object"]
    sha = evidence.get("release_sha")
    if not isinstance(sha, str) or len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha.lower()):
        failures.append("release_sha must be an exact 40-character Git commit SHA")
    entries = evidence.get("gates", {})
    if not isinstance(entries, dict):
        return failures + ["gates must be an object"]
    for key, requirement in REQUIRED.items():
        item = entries.get(key)
        if not isinstance(item, dict):
            failures.append(f"{key}: missing evidence ({requirement})")
            continue
        if item.get("status") != "pass":
            failures.append(f"{key}: status is not pass")
        if not isinstance(item.get("evidence_url"), str) or not item["evidence_url"].startswith(("https://", "http://")):
            failures.append(f"{key}: missing HTTP(S) evidence URL")
        if item.get("release_sha") != sha:
            failures.append(f"{key}: evidence not bound to exact release_sha")
        if not isinstance(item.get("reviewer"), str) or not item["reviewer"].strip():
            failures.append(f"{key}: human or test-owner attribution missing")
    return failures

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", default="stage9/R12_RELEASE_EVIDENCE.json")
    args = parser.parse_args()
    path = Path(args.evidence)
    if not path.is_file():
        print("R12 BLOCKED: no verified evidence file at", path)
        return 1
    try:
        evidence = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print("R12 BLOCKED: cannot parse evidence:", exc)
        return 1
    failures = check(evidence)
    if failures:
        print("R12 BLOCKED: production signoff forbidden")
        for issue in failures:
            print(" -", issue)
        return 1
    print("R12 EVIDENCE STRUCTURE PASS: review linked evidence manually before merge/release")
    return 0

if __name__ == "__main__":
    sys.exit(main())
