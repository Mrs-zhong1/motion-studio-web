"""U1-U4 regression: template-first discovery, inlined demo photos, blank project, 20 components."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import threading

ROOT = Path(__file__).resolve().parents[1]
EDITOR = ROOT / "Motion-Studio-Unified-Editor.html"
DEMO_JPEG = (ROOT / 'template-thumbnails' / 'editorial.jpg').read_bytes()

def test_u1_u4_regression():
    server = ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True,args=["--no-sandbox"])
            page = browser.new_page(viewport={"width":1440,"height":900})
            errors = []
            page.on("pageerror",lambda e:errors.append(str(e)))
            page.route("https://images.unsplash.com/**",lambda route: route.fulfill(status=200,body=DEMO_JPEG,content_type="image/jpeg",headers={"access-control-allow-origin":"*"}))
            page.goto(f"http://127.0.0.1:{server.server_port}/{EDITOR.name}",wait_until="domcontentloaded")
            assert page.locator("#discoveryView").is_visible()
            assert page.locator("[data-template-card]").count()==8
            page.locator("[data-template-card='editorial']").click()
            page.wait_for_function("() => templatePhotoCache.has('editorial')")
            page.locator("#templatePreviewFrame").wait_for(state="attached")
            page.locator("#previewUse").click()
            page.wait_for_function("() => project.templateId==='editorial'")
            assert page.evaluate("project.sections[0].image.startsWith('data:image/jpeg;base64,')"), page.evaluate("({has:templatePhotoCache.has('editorial'),sizes:templatePhotoCache.get('editorial')?.map(x=>x.length)})")
            assert page.evaluate("project.sections.length")>=3
            assert page.locator(".section.selected [data-canvas-image]").count()==1
            page.locator(".section.selected [data-canvas-image]").click()
            page.locator("#propImage").set_input_files({"name":"replacement.jpg","mimeType":"image/jpeg","buffer":DEMO_JPEG})
            page.wait_for_function("() => project.sections[0].image.startsWith('data:image/jpeg;base64,')")
            page.locator("#imageFocusX").fill("72")
            assert page.evaluate("project.sections[0].imageFocusX")==72
            assert page.locator(".section.selected .section-art").evaluate("(el)=>el.style.backgroundPosition.includes('72%')")
            assert page.evaluate("registry.length")==20
            assert page.locator("#editorTimeline").evaluate("(e)=>e.classList.contains('collapsed')")
            page.locator("#backToLibrary").click()
            page.locator("#discoveryBlank").click()
            page.wait_for_function("() => project.sections.length===0")
            assert page.locator("#emptyStartAdd").is_visible()
            page.locator("#emptyStartAdd").click()
            assert page.locator('[data-asset-tier="l2"]').is_visible()
            page.locator("[data-section-preset]").first.click()
            page.wait_for_function("() => project.sections.length===1")
            assert not errors,errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()

if __name__=="__main__":
    test_u1_u4_regression()
    print("U1-U4 visual flow regression passed")
