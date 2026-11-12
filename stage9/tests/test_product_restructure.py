"""Product-level R1/R2 acceptance for the template-first Motion Studio shell."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
EDITOR = ROOT / "Motion-Studio-Stage15-Meshopt-OFFLINE.html"
BROWSER = os.environ.get("MOTION_BROWSER", "chromium").strip().lower()


def test_product_restructure():
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(ROOT))
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as pw:
            engine = getattr(pw, BROWSER)
            launch = {"headless": True}
            if BROWSER == "chromium":
                launch["args"] = ["--no-sandbox"]
            browser = engine.launch(**launch)
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(
                f"http://127.0.0.1:{server.server_port}/{EDITOR.name}",
                wait_until="domcontentloaded",
            )

            assert page.locator("#discoveryView").is_visible()
            assert page.locator("[data-template-card]").count() == 8
            assert page.locator("[data-template-card='editorial']").count() == 1
            assert page.locator("[data-template-card='product-3d']").count() == 1

            page.locator("[data-template-card='product-3d']").click()
            assert page.locator("#templatePreview").is_visible()
            assert page.locator("#previewClose").is_visible()
            assert page.locator("#previewDesktop").is_visible()
            assert page.locator("#previewMobile").is_visible()
            assert page.locator("#previewReplay").is_visible()
            assert page.locator("#previewUse").is_visible()
            frame = page.locator("#templatePreviewFrame").content_frame
            frame.locator("section.section").first.wait_for()
            assert frame.locator("section.section").count() >= 4
            assert frame.locator("html").evaluate("el => el.scrollHeight > innerHeight")

            page.locator("#previewMobile").click()
            assert page.locator("#previewDevice").evaluate(
                "el => el.classList.contains('mobile')"
            )
            replay_before = page.locator("#templatePreviewFrame").get_attribute("srcdoc")
            page.locator("#previewReplay").click()
            frame.locator("section.section").first.wait_for()
            replay_after = page.locator("#templatePreviewFrame").get_attribute("srcdoc")
            assert replay_before and replay_after
            assert "3D Product Experience" in replay_after

            page.locator("#previewUse").click()
            assert page.locator("#editorView").is_visible()
            assert page.locator("#discoveryView").is_hidden()
            assert page.evaluate("registry.length") == 20
            assert page.evaluate("project.templateId") == "product-3d"
            assert page.locator("#chapterList [data-chapter-id]").count() == page.evaluate(
                "project.sections.length"
            )

            assert page.locator("[data-asset-tier]").count() == 3
            assert page.locator("[data-asset-tier='l1']").is_visible()
            page.locator("[data-asset-tier-button='l3']").click()
            assert page.locator("#componentList .comp").count() == 20

            for selector in (".editor-left", ".canvas-viewport", ".editor-right"):
                overflow = page.locator(selector).evaluate(
                    "el => getComputedStyle(el).overflowY"
                )
                assert overflow in ("auto", "scroll")

            assert page.locator("body").evaluate("el => el.classList.contains('simple-mode')")
            page.locator("#modeToggle").click()
            assert not page.locator("body").evaluate(
                "el => el.classList.contains('simple-mode')"
            )

            page.locator("#timelineToggle").click()
            assert page.locator("#editorTimeline").evaluate(
                "el => el.classList.contains('collapsed')"
            )
            page.locator("#togglePanels").click()
            assert page.locator("body").evaluate(
                "el => el.classList.contains('panels-hidden')"
            )

            template_shapes = page.evaluate(
                """() => Object.fromEntries(
                    MotionStudioUnified.templates.map(t => {
                      const p = MotionStudioUnified.createProjectFromTemplate(t.id);
                      return [t.id, p.sections.map(s => s.id).join('|')];
                    })
                )"""
            )
            assert len(template_shapes) == 8
            assert len(set(template_shapes.values())) == 8
            template_exports = page.evaluate(
                """() => MotionStudioUnified.templates.map(t => {
                    const project = MotionStudioUnified.createProjectFromTemplate(t.id);
                    MotionStudioUnified.load(project, {resetHistory: true});
                    const html = MotionStudioUnified.build();
                    return {
                      id: t.id,
                      sectionCount: project.sections.length,
                      renderedCount: (html.match(/<section class=\"section/g) || []).length,
                      hasTitle: html.includes(t.name),
                      hasRemoteScript: /<script[^>]+src=[\"']https?:/.test(html)
                    };
                })"""
            )
            assert all(
                item["sectionCount"] == item["renderedCount"]
                and item["hasTitle"]
                and not item["hasRemoteScript"]
                for item in template_exports
            )
            legacy_template = page.evaluate(
                """() => {
                    const legacy = MotionStudioUnified.createProjectFromTemplate('editorial');
                    delete legacy.templateId;
                    MotionStudioUnified.load(legacy, {resetHistory: true});
                    return MotionStudioUnified.getProject().templateId;
                }"""
            )
            assert legacy_template == "custom"
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    test_product_restructure()
    print(f"Motion Studio product restructure passed in {BROWSER}")
