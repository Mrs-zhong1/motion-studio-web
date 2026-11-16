"""S4: the editor must preview its edited narrative, not the template original."""
import os
import threading
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/"Motion-Studio-Stage15-Meshopt-OFFLINE.html"

def run():
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
            for name in ("editorial","fashion"):
                page.goto(f"http://127.0.0.1:{server.server_port}/{EDITOR.name}",wait_until="domcontentloaded")
                page.locator(f"[data-template-card='{name}']").click()
                page.locator("#previewUse").click()
                title="Live edited story "+name
                page.locator("#projectName").fill(title)
                copy="Edited narrative "+name+" chapter two"
                page.evaluate("""(txt)=>{
                    project.sections[1].text=txt;
                    const cam=project.sections[1].camera;
                    cam.advanced=true;
                    cam.path=[{at:0,x:-85,y:20,zoom:120,tilt:-18,opacity:100},
                              {at:50,x:45,y:-10,zoom:140,tilt:22,opacity:100},
                              {at:100,x:0,y:-30,zoom:100,tilt:0,opacity:100}];
                    render();
                }""",copy)
                assert page.locator("#sections").get_attribute("data-story-edit")=="true"
                assert page.locator("#sections .section iframe").first.evaluate(
                    "n=>getComputedStyle(n).visibility")=="hidden"
                page.locator("#playPreview").click()
                assert page.locator("#templatePreview").is_visible()
                assert page.locator("#templatePreview").get_attribute("data-project-preview")=="true"
                assert page.locator("#previewUse").is_hidden()
                frame=page.locator("#templatePreviewFrame").element_handle().content_frame()
                frame.locator(".s1-story-stage").wait_for()
                assert frame.locator(".s1-story-copy article").nth(1).locator("h2").text_content()==copy
                assert frame.locator(".s1-story-stage").get_attribute("data-story-profile")==name
                frame.evaluate("()=>scrollTo(0,document.querySelectorAll('.s1-story-anchor')[1].offsetTop)")
                frame.wait_for_function("()=>document.querySelector('.s1-story-stage')?.dataset.storyIndex==='1'")
                transform=frame.locator(".s1-scene-image").nth(1).evaluate("n=>n.style.transform")
                assert "rotateY(" in transform and "perspective(" in transform,transform
                assert page.locator("#previewTitle").text_content()==title
                page.locator("#r17PreviewNext").click()
                frame.wait_for_function("()=>document.querySelector('.s1-story-stage')?.dataset.storyIndex==='1'",timeout=12000)
                page.locator("#previewClose").click()
                assert page.locator("#templatePreview").is_hidden()
                assert page.locator("#previewUse").evaluate("node=>!node.hidden")
                assert page.locator("#templatePreview").evaluate("n=>!n.hasAttribute(\'data-project-preview\')")
                assert page.evaluate("project.sections[1].text")==copy
                assert page.evaluate("project.title")==title
                with page.expect_download() as d:
                    page.locator("#exportPage").click()
                exported=d.value.path().read_text(encoding="utf8")
                assert copy in exported and title in exported
                assert '<section class="section s1-story-anchor"' in exported
            assert page.evaluate("registry.length")==20
            assert not errors,errors
            browser.close()
    finally:
        server.shutdown();server.server_close()

if __name__=="__main__":
    run()
    print("S4 editable narrative preview and standalone export PASS")
