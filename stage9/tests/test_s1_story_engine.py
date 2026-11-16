"""S1/S2 flagship: real continuous Editorial preview, reverse scroll & export."""
import json
import os
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/"Motion-Studio-Stage15-Meshopt-OFFLINE.html"

def test_editorial_story():
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    browser_id=os.environ.get("MOTION_BROWSER","chromium")
    try:
        with sync_playwright() as pw:
            browser=getattr(pw,browser_id).launch(headless=True,args=["--no-sandbox"] if browser_id=="chromium" else [])
            page=browser.new_page(viewport={"width":1440,"height":900},accept_downloads=True)
            errors=[]
            page.on("pageerror",lambda e:errors.append(str(e)))
            page.goto(f"http://127.0.0.1:{server.server_port}/{EDITOR.name}",wait_until="domcontentloaded")
            assert page.evaluate("registry.length")==20
            page.locator("[data-template-card='editorial']").click()
            page.locator("#templatePreviewFrame").wait_for(state="attached")
            frame=page.locator("#templatePreviewFrame").element_handle().content_frame()
            frame.locator(".s1-story-stage").wait_for(timeout=20000)
            assert page.locator("#previewImmersive").get_attribute("aria-pressed")=="true"
            assert frame.locator(".s1-scene-image").count()==4
            assert frame.locator(".s1-story-anchor").count()==4
            assert frame.locator(".section iframe").count()==0,"legacy independent demo frames still visible"
            assert all(x.startswith("data:image/") for x in frame.locator(".s1-scene-image").evaluate_all("(nodes)=>nodes.map(n=>n.getAttribute('src'))"))
            frame.evaluate("""()=>{
                const second=document.querySelectorAll('.s1-story-anchor')[2];
                scrollTo(0,second.offsetTop)
            }""")
            frame.wait_for_function("()=>document.querySelector('.s1-story-stage')?.dataset.storyIndex==='2'",timeout=12000)
            frame.evaluate("()=>scrollTo(0,0)")
            frame.wait_for_function("()=>document.querySelector('.s1-story-stage')?.dataset.storyIndex==='0'",timeout=12000)
            assert frame.locator(".r14-story-rail").count()==1,"Navigator event bridge must stay installed"
            assert frame.locator(".r14-story-rail").evaluate("(n)=>getComputedStyle(n).display")=="none"
            page.locator("#previewUse").click()
            assert page.evaluate("project.templateId")=="editorial"
            page.locator("#projectName").fill("Editorial Narrative Acceptance")
            with page.expect_download() as file:
                page.locator("#exportPage").click()
            html=file.value.path().read_text(encoding="utf8")
            assert "s1-story-stage" in html and "Editorial Narrative Acceptance" in html
            assert html.count('<section class="section s1-story-anchor"')==4
            assert '<section class="section designed-chapter"' not in html
            assert not errors,errors
            browser.close()
    finally:
        server.shutdown();server.server_close()

if __name__=="__main__":
    test_editorial_story()
    print("S1 continuous editorial story PASS",os.environ.get("MOTION_BROWSER","chromium"))
