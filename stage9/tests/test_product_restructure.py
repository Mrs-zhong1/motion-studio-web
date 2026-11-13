"""Product-level R1/R2 acceptance for the template-first Motion Studio shell."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
EDITOR = ROOT / "Motion-Studio-Stage15-Meshopt-OFFLINE.html"
BROWSER = os.environ.get("MOTION_BROWSER", "chromium").strip().lower()
SCREENSHOT_DIR = os.environ.get("MOTION_SCREENSHOT_DIR")


def capture(page, name):
    if SCREENSHOT_DIR:
        target = Path(SCREENSHOT_DIR)
        target.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(target / f"{name}-{BROWSER}.png"))


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
            capture(page, "template-library")

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
            capture(page, "immersive-preview")
            frame.locator(".page-head").hover()
            page.mouse.wheel(0, 700)
            page.locator("#templatePreviewFrame").element_handle().content_frame().wait_for_function(
                "scrollY > 0"
            )

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

            draft_before = page.evaluate("JSON.stringify(project)")
            page.locator("#previewClose").click()
            assert page.locator("#templatePreview").is_hidden()
            assert page.evaluate("JSON.stringify(project)") == draft_before
            page.locator("[data-template-card='product-3d']").click()

            page.locator("#previewUse").click()
            assert page.locator("#editorView").is_visible()
            assert page.locator("#discoveryView").is_hidden()
            assert page.evaluate("registry.length") == 20
            assert page.evaluate("project.templateId") == "product-3d"
            assert page.locator("#chapterList [data-chapter-id]").count() == page.evaluate(
                "project.sections.length"
            )
            capture(page, "visual-editor")
            assert page.locator("#chapterList .chapter-thumb[data-effect]").count() == 5
            before_order = page.evaluate("project.sections.map(s => s.uid)")
            page.locator("#chapterList [data-chapter-id]").last.drag_to(
                page.locator("#chapterList [data-chapter-id]").first
            )
            after_order = page.evaluate("project.sections.map(s => s.uid)")
            assert after_order[0] == before_order[-1]

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
            camera_before = page.evaluate("JSON.stringify(project.sections[0].camera)")
            page.locator("#modeToggle").click()
            assert not page.locator("body").evaluate(
                "el => el.classList.contains('simple-mode')"
            )
            assert page.evaluate("JSON.stringify(project.sections[0].camera)") == camera_before

            page.locator("#zoomIn").click()
            assert page.locator("#zoomReadout").inner_text() == "110%"

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
            for template_id in template_shapes:
                page.locator("#backToLibrary").click()
                page.locator(f"[data-template-card='{template_id}']").click()
                page.locator("#templatePreviewFrame").content_frame.locator(
                    "section.section"
                ).first.wait_for()
                page.locator("#previewUse").click()
                changed_title = f"Acceptance {template_id}"
                page.locator("#projectName").fill(changed_title)
                with page.expect_download() as saved:
                    page.locator("#saveProject").click()
                saved_project = json.loads(saved.value.path().read_text(encoding="utf8"))
                assert saved_project["templateId"] == template_id
                assert saved_project["title"] == changed_title
                with page.expect_download() as exported:
                    page.locator("#exportPage").click()
                exported_html = exported.value.path().read_text(encoding="utf8")
                assert changed_title in exported_html
                assert f'data-template="{template_id}"' in exported_html
                assert exported_html.count('<section class="section') == len(
                    saved_project["sections"]
                )
                page.locator("#openFile").set_input_files(
                    {
                        "name": "roundtrip.json",
                        "mimeType": "application/json",
                        "buffer": json.dumps(saved_project).encode("utf8"),
                    }
                )
                assert page.evaluate("project.templateId") == template_id
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    test_product_restructure()
    print(f"Motion Studio product restructure passed in {BROWSER}")
