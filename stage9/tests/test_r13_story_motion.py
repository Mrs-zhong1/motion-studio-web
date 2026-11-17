"""R13 exported-page motion acceptance — true browser DOM, no screenshots-as-proof."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
EDITOR = ROOT / "Motion-Studio-Stage15-Meshopt-OFFLINE.html"


def test_r13_motion():
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
            page = browser.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="no-preference")
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"http://127.0.0.1:{server.server_port}/{EDITOR.name}", wait_until="domcontentloaded")
            assert page.locator("[data-template-card]").count() == 8
            for template in ("cinematic", "architecture", "agency", "fashion", "gallery", "saas", "editorial", "product-3d"):
                exported = page.evaluate("(id) => buildTemplatePreviewDocument(id)", template)
                if template=="cinematic":
                    assert 'data-r39-film="continuous"' in exported,template
                    assert exported.count('class="r39-frame"')==5,template
                    continue
                if template=="editorial":
                    assert 'data-e42-editorial="coherent-print"' in exported,template
                    assert exported.count('class="e42-image"')==4,template
                    assert '<iframe' not in exported,template
                    continue
                assert "installR13StoryMotion" in exported, template
                assert f'data-template="{template}"' in exported, template
                assert f'.page[data-template="{template}"] .section.designed-chapter .designed-chapter-heading::before' in exported, template
                assert f'.page[data-template="{template}"] .section.designed-chapter .motion-atmosphere' in exported, template
            # Execute the export after photo hydration, mirroring actual preview flow.
            # Bare template definitions have not loaded artwork yet.
            page.evaluate("async () => await ensureTemplatePhoto('agency')")
            exported = page.evaluate("(id) => buildTemplatePreviewDocument(id)", "agency")
            output = browser.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="no-preference")
            output_errors = []
            output.on("pageerror", lambda error: output_errors.append(str(error)))
            output.set_content(exported, wait_until="domcontentloaded")
            section = output.locator("section.designed-chapter").first
            section.wait_for()
            # R13-04: atmosphere is rendered within the real photo section,
            # distinctly styled for all eight templates, with no pointer blocking.
            assert section.locator(".section-art .motion-atmosphere").count() == 1
            overlay = section.locator(".motion-atmosphere")
            assert overlay.evaluate("e => getComputedStyle(e).pointerEvents") == "none"
            assert overlay.evaluate("e => getComputedStyle(e).position") == "absolute"
            assert overlay.evaluate("e => getComputedStyle(e).backgroundImage") != "none"
            assert section.evaluate("s=>getComputedStyle(s.querySelector('.designed-chapter-heading'),'::before').content") == '""'
            # Script calculates pointer displacement only for mouse/pen, not touch.
            dx = section.evaluate("""s=>{
              const r=s.getBoundingClientRect();
              s.dispatchEvent(new PointerEvent('pointermove',{clientX:r.right-3,clientY:r.bottom-3,pointerType:'mouse',bubbles:true}));
              return s.style.getPropertyValue('--motion-pointer-x');
            }""")
            assert dx.endswith("px") and float(dx[:-2]) > 0, dx
            section.evaluate("s=>s.dispatchEvent(new PointerEvent('pointerleave',{bubbles:true}))")
            assert section.evaluate("s=>s.style.getPropertyValue('--motion-pointer-x')") == "0px"
            output.evaluate("window.scrollTo(0,600);window.dispatchEvent(new Event('scroll'))")
            assert section.evaluate("s=>s.style.getPropertyValue('--motion-photo-depth')").endswith("px")
            output.emulate_media(reduced_motion="reduce")
            section.evaluate("""s=>{
              const r=s.getBoundingClientRect();
              s.dispatchEvent(new PointerEvent('pointermove',{clientX:r.right-3,clientY:r.bottom-3,pointerType:'mouse',bubbles:true}));
              window.dispatchEvent(new Event('scroll'));
            }""")
            assert section.evaluate("s=>s.style.getPropertyValue('--motion-pointer-x')") == "0px"
            assert section.evaluate("s=>s.style.getPropertyValue('--motion-photo-depth')") == "0px"
            assert not errors, errors
            assert not output_errors, output_errors
            output.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    test_r13_motion()
    print("R13 PASS: eight template signatures and actual exported pointer/scroll/reduced-motion")
