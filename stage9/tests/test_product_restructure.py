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
            # R41: live work is full-width by DEFAULT; information is an
            # optional floating drawer and never resizes the preview canvas.
            info=page.locator("#previewImmersive")
            assert info.is_visible()
            assert info.get_attribute("aria-pressed")=="false"
            assert page.locator("#templatePreview").evaluate(
                "el=>el.classList.contains('immersive-preview')"
            )
            assert page.locator(".preview-product-info").is_hidden()
            viewport_before=page.locator("#previewDevice").bounding_box()
            assert viewport_before["width"]>=1440*.90,viewport_before
            info.click()
            assert info.get_attribute("aria-pressed")=="true"
            assert page.locator(".preview-product-info").is_visible()
            viewport_open=page.locator("#previewDevice").bounding_box()
            assert abs(viewport_open["width"]-viewport_before["width"])<3
            page.keyboard.press("Escape")
            assert info.get_attribute("aria-pressed")=="false"
            assert page.locator(".preview-product-info").is_hidden()
            assert page.locator("#templatePreview").is_visible()
            assert page.locator("#templateResultCount").inner_text() == "08"
            frame = page.locator("#templatePreviewFrame").content_frame
            frame.locator("section.section").first.wait_for()
            assert frame.locator("section.section").count() >= 4
            assert not frame.locator("section.section .badge").first.is_visible()
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
            assert not page.locator("#sections .section .badge").first.is_visible()
            capture(page, "visual-editor")
            assert page.locator("#chapterList .chapter-thumb[data-effect]").count() == 5
            before_order = page.evaluate("project.sections.map(s => s.uid)")
            page.locator("#chapterList [data-chapter-id]").last.drag_to(
                page.locator("#chapterList [data-chapter-id]").first
            )
            after_order = page.evaluate("project.sections.map(s => s.uid)")
            assert after_order[0] == before_order[-1]

            assert page.locator("[data-asset-tier]").count() == 4
            assert page.locator("[data-asset-tier-button='l4']").count() == 1
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
                      renderedCount: t.id==='cinematic'?(html.match(/class="r39-caption"/g)||[]).length:t.id==='editorial'?(html.match(/class="e42-spread"/g)||[]).length:(html.match(/<section class=\"section/g) || []).length,
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
                # Each template must be testable from a clean launch, even after
                # editing a legacy project and collapsing both side panels.
                page.goto(
                    f"http://127.0.0.1:{server.server_port}/{EDITOR.name}",
                    wait_until="domcontentloaded",
                )
                page.locator("#discoveryView").wait_for(state="visible")
                page.locator(f"[data-template-card='{template_id}']").click()
                page.locator("#templatePreviewFrame").wait_for(state="attached")
                preview_frame=page.locator("#templatePreviewFrame").content_frame
                if template_id=="cinematic":
                    preview_frame.locator(".r39-stage").wait_for()
                    assert preview_frame.locator(".r39-frame").count()==5
                elif template_id=="editorial":
                    preview_frame.locator(".e42-sticky").first.wait_for()
                    assert preview_frame.locator(".e42-spread").count()==4
                else:
                    preview_frame.locator("section.section").first.wait_for()
                page.locator("#previewUse").click()
                changed_title = f"Acceptance {template_id}"
                page.locator("#projectName").fill(changed_title)
                # R7: user-edited chapter copy must survive edit/save/export.
                chapter_text = f"R7 edited chapter {template_id}"
                page.evaluate("(t) => {project.sections[1].text=t;render()}", chapter_text)
                assert page.locator('#sections section.section[data-index="1"] [data-chapter-title]').count() == 1
                assert page.locator('#sections section.section[data-index="1"] [data-chapter-title]').text_content() == chapter_text, template_id
                with page.expect_download() as saved:
                    page.locator("#saveProject").click()
                saved_project = json.loads(saved.value.path().read_text(encoding="utf8"))
                assert saved_project["templateId"] == template_id
                assert saved_project["title"] == changed_title
                with page.expect_download() as exported:
                    page.locator("#exportPage").click()
                exported_html = exported.value.path().read_text(encoding="utf8")
                assert changed_title in exported_html
                if template_id=="cinematic":
                    assert 'data-r39-film="continuous"' in exported_html
                    assert exported_html.count('class="r39-caption"')==len(saved_project["sections"])
                    assert exported_html.count('class="r39-frame"')==len(saved_project["sections"])
                elif template_id=="editorial":
                    assert 'data-e42-editorial="coherent-print"' in exported_html
                    assert exported_html.count('class="e42-spread"')==len(saved_project["sections"])
                    assert exported_html.count('class="e42-image"')==len(saved_project["sections"])
                else:
                    assert f'data-template="{template_id}"' in exported_html
                    assert exported_html.count('<section class="section')==len(saved_project["sections"])
                assert chapter_text in exported_html
                assert saved_project["sections"][1]["text"] == chapter_text
                # Loading real standalone HTML in a second browser page catches
                # export styles or chapter motion silently omitted from output.
                if template_id in ("editorial", "product-3d", "cinematic"):
                    standalone = browser.new_page(viewport={"width": 1280,"height": 900})
                    export_errors = []
                    standalone.on("pageerror",lambda err:export_errors.append(str(err)))
                    standalone.set_content(exported_html,wait_until="domcontentloaded")
                    if template_id=="editorial":
                        assert standalone.locator('html[data-e42-editorial="coherent-print"]').count()==1
                        assert standalone.locator('.e42-spread').count()==len(saved_project["sections"])
                        assert standalone.locator('.e42-image').count()==len(saved_project["sections"])
                        assert standalone.locator('.e42-spread').nth(1).locator('.e42-type h1').text_content()==chapter_text
                        assert standalone.locator('iframe').count()==0
                    elif template_id=="cinematic":
                        assert standalone.locator('html[data-r39-film="continuous"]').count()==1
                        assert standalone.locator('.r39-frame').count()==len(saved_project["sections"])
                        assert standalone.locator('.r39-caption').count()==len(saved_project["sections"])
                        assert standalone.locator('.r39-caption[data-index="1"] h1').text_content()==chapter_text
                        assert standalone.locator('#r39-menu-toggle').is_visible()
                        assert standalone.locator('.r37-stage').count()==0
                    else:
                        assert standalone.locator("section.section").count()==len(saved_project["sections"])
                        heading=standalone.locator('section.section[data-index="1"] [data-chapter-title]')
                        assert heading.text_content().strip()==chapter_text
                        rendered=standalone.locator("section.section").nth(1)
                        rendered.scroll_into_view_if_needed()
                        standalone.wait_for_function("""() => {
                            const n=document.querySelectorAll('section.section')[1];
                            return n && n.style.getPropertyValue('--chapter-enter') !== '';
                        }""",timeout=12000)
                        actual=rendered.evaluate("""node=>{
                            const art=node.querySelector('.section-art'),motion=node.querySelector('iframe');
                            const a=art.getBoundingClientRect(),b=motion.getBoundingClientRect();
                            return {enter:Number(node.style.getPropertyValue('--chapter-enter')),
                               photo:getComputedStyle(art).backgroundImage.startsWith('url("data:image/'),
                               width:Math.round(a.width),frame:Math.round(b.width)};
                        }""")
                        assert actual["photo"] and actual["width"]>70,actual
                        assert actual["frame"]>70,actual
                        assert 0<=actual["enter"]<=1,actual
                    assert not export_errors,export_errors
                    standalone.close()
                # R20: verify file persistence after re-opening the actual Web app,
                # rather than relying on the same long-lived editing tab.
                page.goto(
                    f"http://127.0.0.1:{server.server_port}/{EDITOR.name}",
                    wait_until="domcontentloaded",
                )
                assert page.locator("#openFile").count() == 1, page.url
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
