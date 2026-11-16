"""R15: verify distinct complete chapter composition in real standalone HTML."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/"Motion-Studio-Stage15-Meshopt-OFFLINE.html"
TEMPLATES=("editorial","product-3d","cinematic","architecture","agency","fashion","gallery","saas")
AUTHORED_SIX=("cinematic","architecture","agency","fashion","gallery","saas")

def test_r15():
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
            editor=browser.new_page(viewport={"width":1440,"height":900})
            editor.goto(f"http://127.0.0.1:{server.server_port}/{EDITOR.name}",wait_until="domcontentloaded")
            assert editor.locator("[data-template-card]").count()==8
            assert editor.locator(".r15-scene-mark").count()==0
            for name in TEMPLATES:
                await_art=editor.evaluate("(id)=>ensureTemplatePhoto(id)",name)
                html=editor.evaluate("(id)=>buildTemplatePreviewDocument(id)",name)
                assert f'data-template="{name}"' in html,name
                preview=browser.new_page(viewport={"width":1440,"height":900})
                errors=[];preview.on("pageerror",lambda e:errors.append(str(e)))
                preview.set_content(html,wait_until="domcontentloaded",timeout=60000)
                if name=="product-3d":
                    assert preview.locator(".section.designed-chapter").count()==4
                    assert preview.locator(".r15-scene-mark").count()==4
                    assert preview.locator(".section iframe").count()==5
                else:
                    chapters=4 if name=="editorial" else 5
                    assert preview.locator(".s1-story-stage").count()==1,name
                    assert preview.locator(".s1-story-anchor").count()==chapters,name
                    assert preview.locator(".s1-scene-image").count()==chapters,name
                    assert preview.locator(".section iframe").count()==0,name
                    assert preview.locator(".r15-scene-mark").count()==0,name
                    assert preview.locator(".s1-story-stage").get_attribute("data-story-profile")==name
                    preview.evaluate("""()=>scrollTo(0,document.querySelectorAll('.s1-story-anchor')[2].offsetTop)""")
                    preview.wait_for_function("""()=>document.querySelector('.s1-story-stage')?.dataset.storyIndex==='2'""",timeout=12000)
                    assert preview.locator(".s1-scene-image").nth(2).evaluate("el=>getComputedStyle(el).clipPath")!="none"
                    preview.set_viewport_size({"width":390,"height":844})
                    assert preview.evaluate("document.documentElement.scrollWidth<=innerWidth+32"),name
                assert not errors,(name,errors)
                preview.close()
            browser.close()
    finally:
        server.shutdown();server.server_close()

if __name__=="__main__":
    test_r15()
    print("R15 PASS: eight narratives and three multi-act geometry/mobile exports")
