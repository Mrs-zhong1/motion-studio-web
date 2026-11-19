#!/usr/bin/env python3
"""Strict, provenance-first R26 staging validator. Technical PASS never grants release approval."""
import argparse, hashlib, json, sys
from pathlib import Path
from PIL import Image

EXPECTED=33
ALLOWED={"procedural-vector-render","procedural-3d-render","open-licensed-photography"}

def validate(root:Path, manifest_path:Path):
    rows=json.loads(manifest_path.read_text(encoding="utf-8"))
    errors=[]; holds=[]; hashes=set(); names=set()
    if len(rows)!=EXPECTED: errors.append(f"expected {EXPECTED} manifest rows, got {len(rows)}")
    for i,row in enumerate(rows):
        prefix=f"row[{i}]"
        name=row.get("file")
        if not name or name in names: errors.append(f"{prefix}: missing/duplicate filename {name!r}"); continue
        names.add(name); path=root/name
        if not path.is_file(): errors.append(f"{prefix}: missing asset {name}"); continue
        raw=path.read_bytes(); digest=hashlib.sha256(raw).hexdigest()
        if row.get("sha256")!=digest: errors.append(f"{prefix}: SHA-256 mismatch {name}")
        if digest in hashes: errors.append(f"{prefix}: duplicate asset bytes {name}")
        hashes.add(digest)
        try:
            with Image.open(path) as im:
                im.load(); width,height=im.size; fmt=im.format
        except Exception as exc:
            errors.append(f"{prefix}: unreadable image {name}: {exc}"); continue
        if fmt not in ("PNG","JPEG"): errors.append(f"{prefix}: unsupported image format {fmt}: {name}")
        if width<1600 or height<900: errors.append(f"{prefix}: below native minimum 1600x900: {name}")
        if abs(width/height-16/9)>0.015: errors.append(f"{prefix}: aspect ratio outside 16:9 tolerance: {name}")
        if row.get("nativeSourceDimensions") != [width,height]:
            errors.append(f"{prefix}: nativeSourceDimensions do not match actual file: {name}")
        kind=row.get("sourceType")
        if kind not in ALLOWED: errors.append(f"{prefix}: unsupported/missing sourceType: {name}")
        if kind in ("procedural-vector-render","procedural-3d-render"):
            for key in ("generationSystem","sourceReference","generationDate"):
                if not row.get(key): errors.append(f"{prefix}: missing {key}: {name}")
            if row.get("thirdPartyAssets") is not False:
                errors.append(f"{prefix}: procedural asset must explicitly state thirdPartyAssets=false: {name}")
        elif kind=="open-licensed-photography":
            for key in ("originalSourceUrl","creator","licenseId","licenseUrl","attribution","downloadedAt"):
                if not row.get(key): errors.append(f"{prefix}: missing rights field {key}: {name}")
            if row.get("licenseId") not in ("CC0","Public Domain","CC-BY","CC-BY-SA"):
                errors.append(f"{prefix}: license not in approved commercial-review set: {name}")
            if row.get("licenseId")=="CC-BY-SA" and row.get("shareAlikeCompatibilityReviewed") is not True:
                errors.append(f"{prefix}: CC-BY-SA compatibility review missing: {name}")
        if row.get("humanVisualReviewApproved") is not True:
            holds.append(f"{name}: human visual review pending")
        if row.get("productionEligible") is not True:
            holds.append(f"{name}: production eligibility not granted")
    return {"technicalPass":not errors,"releaseEligible":not errors and not holds,
            "expected":EXPECTED,"actual":len(rows),"uniqueHashes":len(hashes),
            "errors":errors,"holds":holds}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    a=p.parse_args()
    result=validate(a.root,a.manifest)
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return 0 if result["technicalPass"] else 1
if __name__=="__main__":sys.exit(main())
