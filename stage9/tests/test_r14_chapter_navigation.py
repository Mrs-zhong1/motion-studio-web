"""R14 exported chapter navigator: actual DOM and interaction smoke."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/"Motion-Studio-Stage15-Meshopt-OFFLINE.html"
TEMPLATES=("editorial","product-3d","cinematic","architecture","agency","fashion","gallery","saas")

def test_r14():
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    worker=threading.Thread(target=server.serve_forever,daemon=True)
    worker.start()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
            page=browser.new_page(viewport={"width":1440,"height":900})
            page.goto(f"http://127.0.0.1:{server.server_port}/{EDITOR.name}",wait_until="domcontentloaded")
            assert page.locator("#discoveryView").is_visible()
            assert page.locator(".r14-story-rail").count()==0, "Navigator must not cover editor/gallery UI"
            for template in TEMPLATES:
                exported=page.evaluate("(id)=>buildTemplatePreviewDocument(id)",template)
                assert "installR14Navigator" in exported, template
                assert "r14-story-rail" in exported, template
                assert f'data-template="{template}"' in exported, template
            exported=page.evaluate("(id)=>buildTemplatePreviewDocument(id)","product-3d")
            standalone=browser.new_page(viewport={"width":1440,"height":900})
            problems=[]
            standalone.on("pageerror",lambda error:problems.append(str(error)))
            standalone.set_content(exported,wait_until="domcontentloaded",timeout=60000)
            nav=standalone.locator("nav.r14-story-rail")
            nav.wait_for()
            expected=standalone.locator("section.section").count()
            assert nav.get_attribute("aria-label")=="Story chapters"
            assert nav.locator("button").count()==expected
            assert nav.locator('button[aria-current="step"]').count()==1
            assert nav.locator(".r14-rail-fill").count()==1
            assert nav.locator("button").first.get_attribute("aria-label").startswith("Go to chapter 1")
            last=nav.locator("button").last
            last.click()
            standalone.wait_for_function("""()=>document.querySelector('.r14-story-rail')?.dataset.activeChapter===String(document.querySelectorAll('.page > section.section').length)""",timeout=10000)
            assert standalone.evaluate("window.scrollY")>0
            fill=nav.locator(".r14-rail-fill").evaluate("el=>parseFloat(el.style.height)")
            assert fill>40,fill
            standalone.set_viewport_size({"width":390,"height":844})
            assert nav.is_visible()
            assert nav.locator("button").first.is_visible()
            assert not nav.locator(".r14-rail-label").first.is_visible()
            standalone.emulate_media(reduced_motion="reduce")
            first=nav.locator("button").first
            first.click()
            standalone.wait_for_function("()=>window.scrollY<100",timeout=10000)
            assert not problems,problems
            # The seven persistent story templates hide their duplicate R14 rail;
            # preview navigation is delegated to the parent toolbar.
            story_html=page.evaluate("(id)=>buildTemplatePreviewDocument(id)","cinematic")
            standalone.set_content(story_html,wait_until="domcontentloaded")
            assert standalone.locator(".s1-story-stage").count()==1
            # Persistent stories rely on parent toolbar chapter controls;
            # an old floating navigation rail is allowed only if hidden.
            hidden_nav=standalone.locator("nav.r14-story-rail")
            assert hidden_nav.count()==0 or hidden_nav.evaluate(
                "n=>getComputedStyle(n).display")=="none"
            standalone.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()

if __name__=="__main__":
    test_r14()
    print("R14 PASS: all eight exports, visible chapter navigation, scroll progress, mobile and reduced motion")
