#!/usr/bin/env python3
"""B1 local-only pilot for the 33 R25 replacement scenes.

Default is a dry-run. Generation is performed only with --run and invokes
MFLUX locally; this script contains no network API client and never writes to
stage9/ai-assets or creates an R25 replacement.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_BOARD = ROOT / "r26-storyboard.json"
DEFAULT_OUT = Path.home() / "MotionStudio-R26-B1-Pilot"
WIDTH, HEIGHT = 1792, 1008  # exact 16:9; both dimensions divisible by 16
SCENES = [
    ("editorial", 2),
    ("product-3d", 3),
    ("cinematic", 2),
    ("architecture", 2),
]
MODELS = {
    "flux2": {
        "label": "FLUX.2 Klein 4B",
        "command": "mflux-generate-flux2",
        "license": "Apache-2.0",
        "license_url": "https://huggingface.co/black-forest-labs/FLUX.2-klein-4B",
        "args": ["--model", "flux2-klein-4b", "--small-text-encoder",
                 "--steps", "4", "--quantize", "8", "--low-ram"],
    },
    "zimage": {
        "label": "Z-Image-Turbo",
        "command": "mflux-generate-z-image-turbo",
        "license": "Apache-2.0",
        "license_url": "https://huggingface.co/Tongyi-MAI/Z-Image-Turbo",
        "args": ["--model", "z-image-turbo", "--steps", "9",
                 "--quantize", "8", "--low-ram"],
    },
}


def load_scenes(path: Path) -> list[dict]:
    board = json.loads(path.read_text(encoding="utf-8"))
    if board.get("schema") != "motion-studio-r26-storyboard-v1":
        raise ValueError("Unexpected R26 storyboard schema")
    rows = {(row["template"], row["chapter"]): row
            for row in board.get("replacements", [])}
    if len(rows) != 33:
        raise ValueError("Storyboard must contain exactly 33 unique replacement scenes")
    missing = [key for key in SCENES if key not in rows]
    if missing:
        raise ValueError(f"Missing pilot scenes: {missing}")
    return [rows[key] for key in SCENES]


def build_prompt(row: dict) -> str:
    return (
        "Create ONE original, independent, premium art-directed photographic scene. "
        "Wide 16:9 cinematic composition, natural physical lighting, convincing "
        "materials and depth, refined professional color grading. "
        f"Template: {row['template']}; chapter {row['chapter']}; "
        f"story beat: {row['storyBeat']}. "
        f"Art direction: {row['artDirection']} "
        f"Single scene subject: {row['subject']}. "
        f"Framing: {row['framing']}. "
        f"Keep the {row['textSafeZone']} visually calm and low-detail for a separate "
        "HTML title overlay. The following title is context only and must NOT appear "
        f"as rendered text: {row['chapterTitle']}. "
        f"Negative requirements: {row['negative']} "
        "Do not create a collage, grid, split panel, contact sheet, border, watermark, "
        "logo, typography or multiple scenes."
    )


def preflight(out_dir: Path, models: list[str]) -> dict:
    if platform.system() != "Darwin" or platform.machine() not in ("arm64", "aarch64"):
        raise RuntimeError("Local generation requires an Apple Silicon Mac running macOS.")
    try:
        mem_bytes = int(subprocess.check_output(
            ["sysctl", "-n", "hw.memsize"], text=True).strip())
    except Exception as exc:
        raise RuntimeError("Could not read unified memory using sysctl.") from exc
    memory_gb = round(mem_bytes / (1024 ** 3), 1)
    if memory_gb < 20:
        raise RuntimeError(
            f"Detected {memory_gb} GB unified memory; this B1 profile requires 20 GB or more."
        )
    out_dir.mkdir(parents=True, exist_ok=True)
    free_gb = round(shutil.disk_usage(out_dir).free / (1024 ** 3), 1)
    if free_gb < 40:
        raise RuntimeError(
            f"Only {free_gb} GB free on the output volume; keep at least 40 GB free "
            "for model caches, temporary tensors and pilot outputs."
        )
    commands = {}
    for key in models:
        executable = MODELS[key]["command"]
        found = shutil.which(executable)
        if not found:
            raise RuntimeError(
                f"Missing {executable}. Install MFLUX first with: "
                "uv tool install --upgrade mflux"
            )
        commands[key] = found
    return {
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "unifiedMemoryGB": memory_gb,
        "freeDiskGB": free_gb,
        "mfluxCommands": commands,
    }


def command_for(model_key: str, row: dict, out_dir: Path, seed: int) -> list[str]:
    model = MODELS[model_key]
    target = out_dir / model_key / f"{row['template']}-{row['chapter']}.png"
    return [
        model["command"], *model["args"],
        "--width", str(WIDTH), "--height", str(HEIGHT),
        "--seed", str(seed), "--make-conf",
        "--prompt", build_prompt(row),
        "--output", str(target),
    ]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_pilot_manifest(output: Path, environment: dict, results: list[dict]) -> Path:
    manifest = {
        "schema": "motion-studio-r26-b1-local-pilot-v1",
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "environment": environment,
        "resolutionTarget": [WIDTH, HEIGHT],
        "results": results,
        "completedImages": sum(row.get("status") == "PASS" for row in results),
        "failedImages": sum(row.get("status") == "FAIL" for row in results),
        "releaseEligible": False,
        "notes": "Pilot evidence only. These files are not copied into stage9/ai-assets.",
    }
    manifest_path = output / "pilot-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                              encoding="utf-8")
    return manifest_path


def run(args: argparse.Namespace) -> int:
    scenes = load_scenes(args.storyboard)
    selected_models = ["flux2", "zimage"] if args.models == "both" else [args.models]
    output = args.out.expanduser().resolve()
    if args.run:
        environment = preflight(output, selected_models)
    else:
        # Planning must remain usable when MFLUX is not installed or PyPI is unreachable.
        environment = {
            "platform": platform.platform(),
            "architecture": platform.machine(),
            "preflight": "NOT_RUN (dry-run does not require MFLUX, model downloads, or free disk space)",
        }
    plan = []
    for model_key in selected_models:
        for index, row in enumerate(scenes):
            seed = 26000 + index
            command = command_for(model_key, row, output, seed)
            plan.append({
                "modelKey": model_key,
                "model": MODELS[model_key]["label"],
                "template": row["template"],
                "chapter": row["chapter"],
                "seed": seed,
                "output": str(output / model_key / f"{row['template']}-{row['chapter']}.png"),
                "command": command,
            })
    print(json.dumps({
        "stage": "B1_LOCAL_PILOT",
        "mode": "RUN" if args.run else "DRY_RUN_NO_GENERATION",
        "environment": environment,
        "resolution": [WIDTH, HEIGHT],
        "plannedImages": len(plan),
        "models": {
            key: {
                "label": MODELS[key]["label"],
                "license": MODELS[key]["license"],
                "licenseUrl": MODELS[key]["license_url"],
            } for key in selected_models
        },
        "plan": plan,
    }, ensure_ascii=False, indent=2))
    if not args.run:
        print("DRY RUN ONLY: no model weights downloaded and no images generated.")
        return 0

    results = []
    failed_models = set()
    for item in plan:
        model_key = item["modelKey"]
        if model_key in failed_models:
            continue
        target = Path(item["output"])
        target.parent.mkdir(parents=True, exist_ok=True)
        print(f"\n[B1] Generating {item['model']} / {item['template']}-{item['chapter']}",
              flush=True)
        started = time.monotonic()
        completed = subprocess.run(item["command"], check=False)
        elapsed = round(time.monotonic() - started, 2)
        failure = None
        dimensions = None
        if completed.returncode != 0:
            failure = f"MFLUX exit code {completed.returncode}"
        elif not target.is_file():
            failure = "MFLUX returned success but output file is missing"
        else:
            try:
                from PIL import Image
                with Image.open(target) as image:
                    image.load()
                    dimensions = list(image.size)
                if dimensions[0] < 1600 or dimensions[1] < 900:
                    failure = (
                        f"native output too small: {dimensions}; no upscaling is allowed"
                    )
                else:
                    ratio = dimensions[0] / dimensions[1]
                    if not 1.68 <= ratio <= 1.88:
                        failure = f"unexpected aspect ratio {ratio:.3f}"
            except Exception as exc:
                failure = f"output is not a readable image: {type(exc).__name__}: {exc}"

        if failure:
            failed_models.add(model_key)
            results.append({
                "status": "FAIL",
                "model": item["model"],
                "modelKey": model_key,
                "modelLicense": MODELS[model_key]["license"],
                "licenseUrl": MODELS[model_key]["license_url"],
                "template": item["template"],
                "chapter": item["chapter"],
                "file": str(target),
                "seconds": elapsed,
                "error": failure,
                "releaseEligible": False,
            })
            write_pilot_manifest(output, environment, results)
            print(f"[B1] FAIL {item['model']}: {failure}", file=sys.stderr, flush=True)
            print(f"[B1] Skipping remaining scenes for {item['model']}; testing other candidate if selected.",
                  flush=True)
            continue

        results.append({
            "status": "PASS",
            "model": item["model"],
            "modelKey": model_key,
            "modelLicense": MODELS[model_key]["license"],
            "licenseUrl": MODELS[model_key]["license_url"],
            "template": item["template"],
            "chapter": item["chapter"],
            "file": str(target),
            "nativeDimensions": dimensions,
            "sha256": sha256(target),
            "seed": item["seed"],
            "seconds": elapsed,
            "sourceType": "local-model-pilot",
            "releaseEligible": False,
            "reason": "B1 pilot only; visual review and R25 provenance validation remain required.",
        })
        write_pilot_manifest(output, environment, results)
        print(f"[B1] PASS dimensions={dimensions} seconds={elapsed} sha256={results[-1]['sha256'][:16]}",
              flush=True)

    manifest_path = write_pilot_manifest(output, environment, results)
    failed_count = sum(row.get("status") == "FAIL" for row in results)
    passed_count = sum(row.get("status") == "PASS" for row in results)
    print(f"\nB1 pilot finished: {passed_count} images passed, {failed_count} model failures.")
    print(f"Manifest: {manifest_path}")
    print("No project source assets were changed.")
    return 1 if failed_count else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--storyboard", type=Path, default=DEFAULT_BOARD)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--models", choices=("both", "flux2", "zimage"), default="both")
    parser.add_argument("--run", action="store_true",
                        help="actually run local inference and download missing model weights")
    args = parser.parse_args()
    try:
        return run(args)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"B1 stopped safely: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
