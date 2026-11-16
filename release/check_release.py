#!/usr/bin/env python3
"""R18–R21 fail-closed release gate. Review builds remain permitted.

This is a verifier of recorded evidence, not an automated substitute for
human art direction, native hardware measurement, or media licensing.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDS = {"editorial", "product-3d", "cinematic", "architecture", "agency", "fashion", "gallery", "saas"}

def inspect(visual, approvals):
    failures, holds = [], []
    rows = visual.get("geometryAndImageEvidence", [])
    pairs = [(r.get("template"), r.get("viewport")) for r in rows]
    expected = {(i, v) for i in IDS for v in ("desktop", "mobile")}
    if len(rows) != 16 or set(pairs) != expected or len(set(pairs)) != 16:
        failures.append("R18: incomplete eight-template desktop/mobile evidence")
    if visual.get("automatedGate") != "PASS" or visual.get("blockingErrors"):
        failures.append("R18: prior automated evidence is not PASS")
    if visual.get("uniquePhotoSourceCount") != 39:
        failures.append("R18: missing unique chapter photography")
    for r in rows:
        key = f"{r.get('template')}/{r.get('viewport')}"
        if r.get("loadedPhotos") != r.get("chapters") or r.get("fallbacks") != 0:
            failures.append(f"R18: photo coverage failed: {key}")
        if r.get("horizontalOverflowPx", 9999) > 32:
            failures.append(f"R18: overflow failed: {key}")
        h = r.get("captureHashes", [])
        if len(h) != 3 or len(set(h)) != 3 or not all(isinstance(x, str) and len(x) >= 16 for x in h):
            failures.append(f"R18: distinct scene captures missing: {key}")
        if r.get("commercialRightsApproved") is not True:
            holds.append(f"R20: chapter images have no recorded commercial clearance: {key}")

    # Independent and explicit evidence. Strings with vague 'PASS' are not enough.
    for key, label in (
        ("artDirection", "R18: human full-flow art-direction signoff"),
        ("nativeDevice", "R19: physical-device frame-time and GPU report"),
        ("rightsRegister", "R20: per-asset rights and release register"),
        ("productFlows", "R20: edit/save/reopen/export acceptance"),
        ("browserRegression", "R21: pinned three-browser CI run"),
        ("liveIntegrity", "R21: deployed URL and SHA-256 match"),
    ):
        item = approvals.get(key, {})
        if not isinstance(item, dict) or item.get("status") != "APPROVED" or not item.get("evidenceUrl") or not item.get("reviewer") or not item.get("reviewedAt"):
            holds.append(label)
    # An approved rights register does not override explicitly uncleared evidence.
    result = "FAIL" if failures else ("HOLD" if holds else "PASS")
    return {"schema": "motion-studio-r18-r21-release-gate-v1", "result": result,
            "priorAutomatedGate": visual.get("automatedGate"), "failures": sorted(set(failures)),
            "holds": sorted(set(holds)), "productionEligible": result == "PASS"}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--visual", type=Path, default=ROOT / "stage9/visual-evidence/R17_QUALITY_GATE.json")
    p.add_argument("--approvals", type=Path, default=ROOT / "release/R18_R21_APPROVALS.json")
    p.add_argument("--mode", choices=("review", "production"), default="review")
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    try:
        evidence = json.loads(a.visual.read_text(encoding="utf-8"))
        approvals = json.loads(a.approvals.read_text(encoding="utf-8"))
        result = inspect(evidence, approvals)
    except (OSError, ValueError, TypeError) as err:
        print(f"Gate cannot read required evidence: {err}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["failures"]:
        return 1
    if a.mode == "production" and result["result"] != "PASS":
        print("BLOCKED: human/device/rights evidence incomplete; review deployment only.", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
