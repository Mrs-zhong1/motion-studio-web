"""Visual-render audit of all 8 built-in templates in the bundled offline browser editor.

Checks inspect the actual exported preview frame, rather than a CSS mockup.
Screenshots are created in the runner (MOTION_SCREENSHOT_DIR controls location),
while structured JSON evidence is printed to CI logs and GitHub Job Summary.
A pass is a rendering/geometry smoke test, not subjective design approval.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import hashlib
import json
import os
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
EDITOR = ROOT / "Motion-Studio-Stage15-Meshopt-OFFLINE.html"
OUTPUT = ROOT / "TEMPLATE_VISUAL_AUDIT.json"
SCREENSHOTS = Path(os.environ.get("MOTION_SCREENSHOT_DIR", "/tmp/motion-studio-visual-audit"))
TEMPLATES = ["editorial", "product-3d", "cinematic", "architecture",
             "agency", "fashion", "gallery", "saas"]


def run_audit():
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0),
        partial(SimpleHTTPRequestHandler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    result = {"source": EDITOR.name, "screenshots_saved_in_runner": str(SCREENSHOTS),
              "templates": [], "browser": "chromium", "status": "running"}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
            page = browser.new_page(viewport={"width": 1440, "height": 900},
                                    device_scale_factor=1)
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"http://127.0.0.1:{server.server_port}/{EDITOR.name}",
                      wait_until="domcontentloaded", timeout=30000)
            assert page.locator("#discoveryView").is_visible()
            assert page.locator("[data-template-card]").count() == 8
            initial_project = page.evaluate("JSON.stringify(project)")
            for template_id in TEMPLATES:
                card = page.locator(f'[data-template-card="{template_id}"]')
                assert card.count() == 1, f"Missing gallery card for {template_id}"
                card.click()
                page.wait_for_function("(id) => templatePhotoCache.has(id)",
                                       arg=template_id, timeout=30000)
                preview = page.locator("#templatePreviewFrame")
                frame = preview.content_frame
                frame.locator("section.section").first.wait_for(timeout=30000)
                total_sections = page.evaluate(
                    "(id) => templateSets[id].sections.length", template_id)
                assert frame.locator("section.section").count() == total_sections
                for device, width, height in (("desktop", 1440, 900), ("mobile", 390, 844)):
                    page.set_viewport_size({"width": width, "height": height})
                    # The mobile button narrows the embedded preview to device width.
                    if device == "mobile":
                        page.locator("#previewMobile").click()
                    else:
                        page.locator("#previewDesktop").click()
                    frame.locator(".section-art").first.wait_for(timeout=10000)
                    geometry = frame.locator("body").evaluate("""body => {
                       const doc = body.ownerDocument;
                       const arts = Array.from(doc.querySelectorAll('.section-art'));
                       const sections = Array.from(doc.querySelectorAll('section.section'));
                       const visible = arts.filter(node => {
                         const s = getComputedStyle(node), r = node.getBoundingClientRect();
                         return s.backgroundImage.startsWith('url("data:image/') &&
                                Number(s.opacity) >= .85 && r.width > 45 && r.height > 45;
                       });
                       const bad = sections.filter(s => {
                         const r = s.getBoundingClientRect();
                         return r.width < 160 || r.height < 220;
                       }).length;
                       return {
                         documentWidth: doc.documentElement.scrollWidth,
                         viewportWidth: doc.documentElement.clientWidth,
                         sectionCount: sections.length,
                         photoCount: arts.length,
                         visiblyRenderedPhotos: visible.length,
                         collapsedSections: bad,
                         imageWidths: arts.map(e=>Math.round(e.getBoundingClientRect().width))
                       };
                    }""")
                    geometry["template"] = template_id
                    geometry["device"] = device
                    shot = frame.locator("section.section").first.screenshot(
                        animations="disabled", timeout=30000)
                    geometry["firstSectionPngSHA256"] = hashlib.sha256(shot).hexdigest()[:16]
                    (SCREENSHOTS / f"{template_id}-{device}.png").write_bytes(shot)
                    assert geometry["photoCount"] == total_sections, geometry
                    assert geometry["visiblyRenderedPhotos"] == total_sections, geometry
                    assert geometry["collapsedSections"] == 0, geometry
                    # More than 32px indicates unintended horizontal layout overflow.
                    assert geometry["documentWidth"] <= geometry["viewportWidth"] + 32, geometry
                    result["templates"].append(geometry)
                page.locator("#previewClose").click()
                assert page.locator("#templatePreview").is_hidden()
            assert page.evaluate("JSON.stringify(project)") == initial_project
            assert not errors, errors
            browser.close()
        result["status"] = "pass"
    except Exception as err:
        result["status"] = "fail"
        result["error"] = str(err)
        raise
    finally:
        OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print("VISUAL_AUDIT_JSON=" + json.dumps(result, ensure_ascii=False))
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    run_audit()
