#!/usr/bin/env python3
"""Web-only Motion Studio R18–R21 release policy.

R17 visual evidence remains historical. Production requires rebuilt AI-first
asset evidence and browser E2E, but never native-phone/GPU device signoff.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDS = {"editorial", "product-3d", "cinematic", "architecture", "agency", "fashion", "gallery", "saas"}
REQUIRED = {
    "artDirection": "R18: full-flow visual design review",
    "aiAssets": "R18: 39-slot AI-generated media coverage and allowed-use record",
    "browserPerformance": "R19: desktop and 390px browser animation/performance evidence",
    "productFlows": "R20: preview/edit/save/reopen/export browser E2E",
    "browserRegression": "R21: Chromium/Firefox/WebKit CI evidence",
    "liveIntegrity": "R21: HTTPS deployment and tested artifact hash",
}

def inspect(visual, approvals):
    failures, holds = [], []
    rows = visual.get("geometryAndImageEvidence", [])
    pairs = [(r.get("template"), r.get("viewport")) for r in rows]
    expected = {(i, v) for i in IDS for v in ("desktop", "mobile")}
    if len(rows) != 16 or set(pairs) != expected or len(set(pairs)) != 16:
        failures.append("R17 baseline: incomplete eight-template desktop/mobile evidence")
    if visual.get("automatedGate") != "PASS" or visual.get("blockingErrors"):
        failures.append("R17 baseline: prior automated gate failed")
    for r in rows:
        key = f"{r.get('template')}/{r.get('viewport')}"
        if r.get("loadedPhotos") != r.get("chapters") or r.get("fallbacks") != 0:
            failures.append(f"R17 baseline: image fallback {key}")
        if r.get("horizontalOverflowPx", 9999) > 32:
            failures.append(f"R17 baseline: horizontal overflow {key}")
        hashes = r.get("captureHashes", [])
        if len(hashes) != 3 or len(set(hashes)) != 3:
            failures.append(f"R17 baseline: no distinct scene captures {key}")
    # R17 Unsplash photography is intentionally historical. Do not confuse
    # its third-party rights flags with the AI-original replacement workflow.
    for key, label in REQUIRED.items():
        item = approvals.get(key, {})
        if not isinstance(item, dict) or item.get("status") != "APPROVED" or not item.get("evidenceUrl") or not item.get("reviewer") or not item.get("reviewedAt"):
            holds.append(label)
    assets = approvals.get("aiAssets", {})
    if assets.get("status") == "APPROVED":
        if assets.get("assetCount") != 39 or assets.get("verifiedOrigin") != "AI_GENERATED" or assets.get("usageTermsChecked") is not True:
            failures.append("R18: AI asset attestation incomplete or use terms not checked")
    status = "FAIL" if failures else ("HOLD" if holds else "PASS")
    return {"schema": "motion-studio-r18-r21-web-release-gate-v2", "result": status,
            "r17AutomatedBaseline": visual.get("automatedGate"), "failures": sorted(set(failures)),
            "holds": sorted(set(holds)), "productionEligible": status == "PASS",
            "nativePhoneHardwareRequired": False, "legacyUnsplashAssetsNotApprovedForProduction": True}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--visual", type=Path, default=ROOT / "stage9/visual-evidence/R17_QUALITY_GATE.json")
    p.add_argument("--approvals", type=Path, default=ROOT / "release/R18_R21_APPROVALS.json")
    p.add_argument("--mode", choices=("review", "production"), default="review")
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    try:
        report = inspect(json.loads(a.visual.read_text(encoding="utf-8")), json.loads(a.approvals.read_text(encoding="utf-8")))
    except (OSError, ValueError, TypeError) as e:
        print(f"Missing or invalid release evidence: {e}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    if report["failures"] or (a.mode == "production" and not report["productionEligible"]):
        print("Production BLOCKED: AI-first assets / browser / visual E2E evidence outstanding.", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
