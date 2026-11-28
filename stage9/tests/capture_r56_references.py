#!/usr/bin/env python3
"""Capture exact-SHA first-screen evidence for the curated R56 public references.

This is a best-effort research artifact. It never downloads/reuses third-party assets
and never treats a screenshot as a license grant or a visual approval.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import traceback

from playwright.sync_api import sync_playwright

OUT = Path(os.environ.get("R56_REFERENCE_DIR", "/tmp/r56-reference-screenshots"))
CANDIDATE_SHA = os.environ.get("R56_REFERENCE_SHA") or None
VIEWPORTS = (("desktop", 1440, 900), ("mobile", 390, 844))
REFERENCES = (
    {"id": "pear", "templates": ["agency"], "url": "https://pear.no/", "label": "Pear — differentiated agency model and proof order"},
    {"id": "grande-charte", "templates": ["agency"], "url": "https://grandecharte.co/en", "label": "Grande Charte — agency narrative and service taxonomy"},
    {"id": "locomotive-work", "templates": ["agency"], "url": "https://locomotive.ca/en/work", "label": "Locomotive — filterable project archive"},
    {"id": "noomo-work", "templates": ["agency", "saas"], "url": "https://noomoagency.com/work", "label": "Noomo — case-led portfolio and Salesforce SaaS story"},
    {"id": "bruno-simon", "templates": ["agency"], "url": "https://bruno-simon.com/", "label": "Bruno Simon — navigable 3D portfolio and progressive controls"},
    {"id": "vercel-product-tour", "templates": ["saas"], "url": "https://vercel.com/product-tour", "label": "Vercel — staged self-guided product tour"},
    {"id": "vercel-tour-article", "templates": ["saas"], "url": "https://vercel.com/blog/designing-the-vercel-virtual-product-tour", "label": "Vercel — product-tour design rationale"},
    {"id": "threeui", "templates": ["saas"], "url": "https://threeui.com/", "label": "ThreeUI — source-backed component discovery"},
    {"id": "framer-product-demo", "templates": ["saas"], "url": "https://www.framer.com/marketplace/plugins/product-demo-builder/", "label": "Framer — clickable demo chapters and reopen/update workflow"},
)

def digest(path):
    raw = path.read_bytes()
    return hashlib.sha256(raw).hexdigest(), len(raw)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report = {
        "schema": "r56-reference-first-screen-evidence-v1",
        "candidateSha": CANDIDATE_SHA,
        "capturedAtUtc": datetime.now(timezone.utc).isoformat(),
        "viewports": [{"name": name, "width": width, "height": height} for name, width, height in VIEWPORTS],
        "references": [],
        "screenshotCount": 0,
        "status": "RUNNING",
        "rightsBoundary": "Reference-only screenshots. No third-party assets, source code, logos or copy are reused.",
    }
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=[
            "--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader",
            "--enable-webgl", "--enable-unsafe-swiftshader",
        ])
        for reference in REFERENCES:
            item = {**reference, "captures": []}
            for viewport_name, width, height in VIEWPORTS:
                page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
                page.set_default_navigation_timeout(30000)
                page.set_default_timeout(8000)
                page_errors = []
                console_errors = []
                page.on("pageerror", lambda error: page_errors.append(str(error)))
                page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
                response_status = None
                navigation_error = None
                try:
                    response = page.goto(reference["url"], wait_until="domcontentloaded", timeout=30000)
                    response_status = response.status if response else None
                    page.wait_for_timeout(1200)
                except Exception as error:
                    navigation_error = str(error)
                filename = f"{reference['id']}-{viewport_name}.png"
                path = OUT / filename
                screenshot_error = None
                try:
                    page.screenshot(path=str(path), full_page=False, animations="disabled", timeout=60000)
                except Exception as error:
                    screenshot_error = str(error)
                page_summary = {}
                try:
                    page_summary = page.evaluate("""() => ({
                        title: document.title,
                        textSample: (document.body?.innerText || '').trim().slice(0, 1400),
                        scrollWidth: document.documentElement?.scrollWidth || 0,
                        scrollHeight: document.documentElement?.scrollHeight || 0,
                        imageCount: document.images?.length || 0,
                        canvasCount: document.querySelectorAll('canvas').length,
                        iframeCount: document.querySelectorAll('iframe').length
                    })""")
                except Exception as error:
                    page_summary = {"inspectionError": str(error)}
                capture = {
                    "viewport": viewport_name,
                    "width": width,
                    "height": height,
                    "httpStatus": response_status,
                    "navigationError": navigation_error,
                    "screenshotError": screenshot_error,
                    "pageErrors": page_errors[:12],
                    "consoleErrors": console_errors[:12],
                    **page_summary,
                }
                if path.is_file() and path.stat().st_size > 1000:
                    sha, size = digest(path)
                    capture.update({"file": filename, "bytes": size, "sha256": sha, "status": "CAPTURED"})
                    report["screenshotCount"] += 1
                else:
                    capture.update({"file": None, "bytes": 0, "sha256": None, "status": "UNAVAILABLE"})
                item["captures"].append(capture)
                page.close()
            report["references"].append(item)
        browser.close()
    expected = len(REFERENCES) * len(VIEWPORTS)
    report["expectedScreenshotCount"] = expected
    report["status"] = "PASS" if report["screenshotCount"] == expected else ("PARTIAL" if report["screenshotCount"] else "FAIL")
    output = OUT / "R56_REFERENCE_SCREENSHOTS.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "candidateSha": CANDIDATE_SHA,
        "references": len(REFERENCES),
        "screenshots": report["screenshotCount"],
        "expected": expected,
        "report": str(output),
    }, ensure_ascii=False, indent=2))
    if report["screenshotCount"] == 0:
        raise SystemExit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "R56_REFERENCE_CAPTURE_ERROR.txt").write_text(traceback.format_exc(), encoding="utf-8")
        raise
