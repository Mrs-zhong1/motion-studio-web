"""R9: the fully bundled Three.js renderer must produce a lit GLB scene and accept real drag input.

This suite checks the offline Stage15 export itself, not the lightweight Canvas renderer.
A software WebGL2 implementation may be used in CI; it does NOT establish native GPU speed.
"""
import json
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/"Motion-Studio-Stage15-Meshopt-OFFLINE.html"
REPORT=ROOT/"R9_STUDIO_3D_REPORT.json"

def run():
    server=ThreadingHTTPServer(("127.0.0.1",0),
        partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    data={"pass":False,"offline":True,"nativeGpuTested":False}
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=[
                "--no-sandbox","--use-gl=angle","--use-angle=swiftshader",
                "--enable-webgl","--enable-unsafe-swiftshader"])
            page=browser.new_page(viewport={"width":1280,"height":900})
            page.goto(f"http://127.0.0.1:{server.server_port}/{FILE.name}",
                      wait_until="domcontentloaded")
            page.locator('[data-template-card="product-3d"]').click()
            page.locator("#previewUse").click()
            page.wait_for_function("() => project.templateId==='product-3d'")
            html=page.evaluate("exportDocument()")
            document=browser.new_page(viewport={"width":1280,"height":900})
            remote=[]
            document.on("request",lambda req:remote.append(req.url)
                if req.url.startswith(("https://","http://")) else None)
            document.set_content(html,wait_until="domcontentloaded")
            scene=document.locator('section[data-index="1"]')
            scene.scroll_into_view_if_needed()
            frame=document.frame_locator('section[data-index="1"] iframe')
            view=frame.locator("#motion-three-webgl2")
            view.wait_for(state="attached",timeout=35000)
            for step in range(80):
                status=view.evaluate("el=>window.__motionThreeStatus || null")
                if status and (status["frames"]>=2 or status["error"]):break
                document.wait_for_timeout(200)
            data["before"]=status
            assert status and not status["error"],status
            assert status["webgl2"] and status["frames"]>=2,status
            assert status["pbr"] and status["materialCount"]>=2,status
            assert status["studioLighting"] and status["shadowEnabled"],status
            assert status["studioMeshes"]==3 and status["modelTriangles"]>=50,status
            bounds=view.bounding_box()
            assert bounds and bounds["width"]>150 and bounds["height"]>150,bounds
            x=bounds["x"]+bounds["width"]*.48
            y=bounds["y"]+bounds["height"]*.5
            document.mouse.move(x,y)
            document.mouse.down()
            document.mouse.move(x+85,y+45,steps=10)
            document.mouse.up()
            document.wait_for_timeout(250)
            after=view.evaluate("el=>window.__motionThreeStatus")
            data["after"]=after
            assert after["dragMoves"]>=2,after
            assert abs(after["dragYaw"])>.3 and abs(after["dragPitch"])>.1,after
            assert after["frames"]>status["frames"],(status,after)
            assert not remote,remote
            data["pass"]=True
            document.close();page.close();browser.close()
    finally:
        server.shutdown();server.server_close()
        REPORT.write_text(json.dumps(data,ensure_ascii=False,indent=2))
        print("R9_STUDIO_3D="+json.dumps(data,ensure_ascii=False))
    assert data["pass"]

if __name__=="__main__":run()
