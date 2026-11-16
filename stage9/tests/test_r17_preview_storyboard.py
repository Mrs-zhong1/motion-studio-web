"""R17: actual two-way accessible preview storyboard through sandboxed iframe."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/"Motion-Studio-Stage15-Meshopt-OFFLINE.html"
TEMPLATES=("editorial","product-3d","cinematic","architecture","agency","fashion","gallery","saas")

def test_r17_preview():
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
            page=browser.new_page(viewport={"width":1440,"height":900})
            errors=[];page.on("pageerror",lambda error:errors.append(str(error)))
            page.goto(f"http://127.0.0.1:{server.server_port}/{EDITOR.name}",wait_until="domcontentloaded")
            assert page.locator("#discoveryView").is_visible()
            for name in TEMPLATES:
                card=page.locator(f'[data-template-card="{name}"]')
                card.focus()
                card.click()
                modal=page.locator("#templatePreview")
                assert modal.is_visible() and modal.get_attribute("role")=="dialog"
                assert modal.get_attribute("aria-modal")=="true"
                assert modal.get_attribute("aria-labelledby")=="previewTitle"
                page.wait_for_function("""()=>!document.querySelector('#templatePreview').hasAttribute('aria-busy')""",timeout=45000)
                frame=page.frame_locator("#templatePreviewFrame")
                frame.locator("nav.r14-story-rail").wait_for(timeout=30000)
                total=page.evaluate("r17PreviewTotal")
                assert total==(4 if name=="editorial" else 5),name
                page.wait_for_function("()=>document.querySelector('#r17PreviewPosition').textContent.trim().startsWith('01 /')",timeout=15000)
                assert page.locator("#r17PreviewPrev").is_disabled()
                page.locator("#r17PreviewNext").click()
                page.wait_for_function("()=>r17PreviewChapter===1",timeout=15000)
                assert "02 / " in page.locator("#r17PreviewPosition").inner_text()
                page.locator("#previewMobile").click()
                assert page.locator("#previewDevice").evaluate("el=>el.classList.contains('mobile')")
                page.locator("#previewImmersive").click()
                assert page.locator("#templatePreview").evaluate("el=>el.classList.contains('immersive-preview')")
                assert page.locator(".r17-preview-chapters").is_visible()
                page.locator("#previewDesktop").click()
                assert not page.locator("#previewDevice").evaluate("el=>el.classList.contains('mobile')")
                page.keyboard.press("Escape")
                assert modal.is_hidden()
                assert card.evaluate("el=>el===document.activeElement"),name
                assert page.locator("#templatePreviewFrame").get_attribute("srcdoc")==""
            assert not errors,errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()

if __name__=="__main__":
    test_r17_preview()
    print("R17 PASS: 8 real sandbox previews, two-way chapter nav, mobile/immersive, Escape focus")
