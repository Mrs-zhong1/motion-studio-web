"""R11: offline web product on mobile viewport, reduced motion and fallback.

Chromium software WebGL2 in CI only; not native mobile hardware validation.
"""
import json
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/"Motion-Studio-Stage15-Meshopt-OFFLINE.html"
REPORT=ROOT/"R11_MOBILE_ACCEPTANCE.json"

def load_product(browser,url,viewport,reduce_motion=None):
    page=browser.new_page(viewport=viewport,reduced_motion=reduce_motion)
    page.goto(url,wait_until="domcontentloaded",timeout=60000)
    page.locator("[data-template-card='product-3d']").click()
    page.locator("#previewUse").click()
    page.wait_for_function("() => project.templateId==='product-3d'",timeout=30000)
    assert page.locator("#editorView").is_visible()
    assert page.evaluate("project.sections.length")>=3
    exported=page.evaluate("exportDocument()")
    assert "data:text/javascript;base64," in exported
    return page,exported

def wait_status(frame,page):
    canvas=frame.locator("#motion-three-webgl2")
    canvas.wait_for(state="attached",timeout=45000)
    for i in range(90):
        result=canvas.evaluate("el=>window.__motionThreeStatus||null")
        if result and (result["frames"]>=2 or result.get("error")):return canvas,result
        page.wait_for_timeout(180)
    raise AssertionError("Three.js renderer did not settle: "+repr(result))

def run():
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    data={"status":"FAIL","testType":"Chromium software WebGL2 simulated mobile","realDevice":False}
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=[
                "--no-sandbox","--use-gl=angle","--use-angle=swiftshader",
                "--enable-webgl","--enable-unsafe-swiftshader"])
            address=f"http://127.0.0.1:{server.server_port}/{FILE.name}"
            source,html=load_product(browser,address,{"width":390,"height":780},"reduce")
            exported=browser.new_page(viewport={"width":390,"height":780},device_scale_factor=2,reduced_motion="reduce")
            errors=[]
            exported.on("pageerror",lambda exc:errors.append(str(exc)))
            exported.set_content(html,wait_until="domcontentloaded")
            assert exported.evaluate("document.documentElement.scrollWidth<=window.innerWidth+3")
            section=exported.locator('section[data-index="1"]')
            section.scroll_into_view_if_needed()
            frame=exported.frame_locator('section[data-index="1"] iframe')
            canvas,status=wait_status(frame,exported)
            data["initial"]=status
            assert status["webgl2"] and status["modelTriangles"]>=10000,status
            assert status["environmentReady"] and status["pbr"],status
            assert status["reducedMotion"],status
            assert status["quality"]=="mobile",status
            assert status["pixelRatio"]<=1.01,status
            assert status["renderMsAvg"]>0 and status["drawSamples"]>=2,status
            assert 0<status["renderWidth"]<=900,status
            assert frame.locator("#motion-r9-controls").is_visible()
            frame.locator("#motion-r9-controls button",has_text="Pearl").click()
            frame.locator("#motion-r9-controls button",has_text="Detail").click()
            after=canvas.evaluate("el=>window.__motionThreeStatus")
            assert after["materialPreset"]=="pearl" and after["cameraPreset"]=="detail",after
            assert after["controlClicks"]>=2
            assert not errors,errors
            # Capture the real mobile WebGL scene, not the portfolio cover image.
            evidence=Path("/tmp/motion-studio-visual-audit")
            evidence.mkdir(parents=True,exist_ok=True)
            canvas.screenshot(path=str(evidence/"r11-mobile-product.png"),animations="disabled")
            data["mobile"]=after
            exported.close();source.close()

            # Hardware-unavailable fallback: WebGL2 API deliberately hidden.
            fallback=browser.new_context(viewport={"width":390,"height":780})
            fallback.add_init_script("""Object.defineProperty(window,
                'WebGL2RenderingContext',{value:undefined,configurable:true});""")
            alt=fallback.new_page()
            alt.goto(address,wait_until="domcontentloaded")
            alt.locator("[data-template-card='product-3d']").click()
            alt.locator("#previewUse").click()
            offline=alt.evaluate("exportDocument()")
            result=fallback.new_page();result.set_content(offline,wait_until="domcontentloaded")
            result.locator('section[data-index="1"]').scroll_into_view_if_needed()
            fallback_frame=result.frame_locator('section[data-index="1"] iframe')
            fallback_frame.locator("#view").wait_for(state="attached",timeout=20000)
            result.wait_for_timeout(400)
            fallback_status=fallback_frame.locator("#view").evaluate(
                "el=>window.__motionThreeStatus||null")
            assert fallback_status and "WebGL2 unavailable" in fallback_status["error"],fallback_status
            assert fallback_frame.locator("#view").is_visible()
            data["fallback"]={"error":fallback_status["error"],"canvasVisible":True}
            fallback.close()
            browser.close()
            data["status"]="PASS"
    finally:
        server.shutdown();server.server_close()
        REPORT.write_text(json.dumps(data,ensure_ascii=False,indent=2))
        print("R11_MOBILE_ACCEPTANCE="+json.dumps(data,ensure_ascii=False))
    assert data["status"]=="PASS"

if __name__=="__main__":run()
