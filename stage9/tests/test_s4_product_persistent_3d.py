"""S4: real one-GLB persistent product across all five story chapters."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import hashlib,json,threading
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
PAGE=ROOT/"Motion-Studio-Stage15-Meshopt-OFFLINE.html"

def run():
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
      with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=["--no-sandbox","--enable-webgl","--use-gl=angle","--use-angle=swiftshader","--disable-web-security"])
        page=browser.new_page(viewport={"width":1366,"height":850},accept_downloads=True)
        page.goto(f"http://127.0.0.1:{server.server_port}/{PAGE.name}",wait_until="domcontentloaded")
        page.locator("[data-template-card='product-3d']").click()
        page.locator("#previewUse").click()
        assert page.evaluate("project.templateId")=="product-3d"
        assert page.evaluate("project.sections.filter(x=>x.id==='offline-glb-scene'&&x.glb).length")==1
        html=page.evaluate("exportDocument()")
        assert "motion-product-story-data" in html
        assert "stage9ProductStoryURL" not in html
        assert 'motion-product-story-canvas' not in html  # created by real runtime
        assert 'motion-product-story-data' in html and 'data:text/javascript;base64,' in html
        out=browser.new_page(viewport={"width":1366,"height":850})
        errors=[];out.on("pageerror",lambda e:errors.append(str(e)))
        out.set_content(html,wait_until="domcontentloaded",timeout=60000)
        out.wait_for_function("()=>window.__motionProductStory?.loaded===true",timeout=50000)
        state=out.evaluate("window.__motionProductStory")
        assert state["webgl2"] and state["meshCount"]>=1,state
        assert state["modelSourceCount"]==1,state
        assert out.locator("#motion-product-story-canvas").count()==1
        before=out.evaluate("""()=>{
          const sections=[...document.querySelectorAll('.page > section.section')];
          scrollTo(0,sections[0].offsetTop);
          return sections.length;
        }""")
        assert before==5
        out.wait_for_function("()=>window.__motionProductStory.frameCount>=2",timeout=12000)
        out.evaluate("()=>scrollTo(0,document.querySelectorAll('.page > section.section')[3].offsetTop)")
        out.wait_for_function("()=>window.__motionProductStory.progress>.45",timeout=12000)
        after=out.evaluate("window.__motionProductStory")
        assert after["frameCount"]>state["frameCount"],after
        assert after["cameraSamples"][-1]["rotation"]!=after["cameraSamples"][0]["rotation"],after
        out.evaluate("()=>scrollTo(0,0)")
        out.wait_for_function("()=>window.__motionProductStory.progress<.1",timeout=12000)
        assert out.locator("#motion-product-story-canvas").count()==1
        assert not out.evaluate("window.__motionProductStory.errors")
        out.set_viewport_size({"width":390,"height":844})
        assert out.evaluate("document.documentElement.scrollWidth<=innerWidth+32")
        evidence=ROOT/"S4_PRODUCT_EVIDENCE";evidence.mkdir(exist_ok=True)
        (evidence/"product-persistent-webgl.png").write_bytes(out.screenshot(animations="disabled"))
        (evidence/"product-persistent-state.json").write_text(json.dumps(after,indent=2))
        assert not errors,errors
        browser.close()
    finally:
      server.shutdown();server.server_close()
if __name__=="__main__":
    run()
    print("S4 PASS: one real WebGL GLB through five chapters, continuous reversible camera")
