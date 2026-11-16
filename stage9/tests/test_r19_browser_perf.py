"""R19 Web-only browser performance and overflow evidence (Chromium CI).
Not a native phone, hardware GPU or real-user field performance benchmark.
"""
import json
import math
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/"Motion-Studio-Stage15-Meshopt-OFFLINE.html"
OUTPUT=ROOT/"R19_BROWSER_PERF.json"

def measure(frame):
    return frame.evaluate("""async () => {
        const times=[];
        let prior=0;
        await new Promise(resolve=>{
            const sample=t=>{
                if(prior)times.push(t-prior);
                prior=t;
                if(times.length >= 100) resolve();
                else requestAnimationFrame(sample);
            };
            requestAnimationFrame(sample);
        });
        const sorted=[...times].sort((a,b)=>a-b);
        const percentile=p=>sorted[Math.min(sorted.length-1,Math.floor((sorted.length-1)*p))];
        return {sampleFrames:times.length,medianFrameMs:Math.round(percentile(.5)*100)/100,
            p95FrameMs:Math.round(percentile(.95)*100)/100,
            longFramesOver50ms:times.filter(x=>x>50).length,
            viewportWidth:innerWidth,documentWidth:document.documentElement.scrollWidth,
            prefersReducedMotion:matchMedia('(prefers-reduced-motion: reduce)').matches};
    }""")

def run():
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    evidence={"schema":"motion-studio-r19-browser-performance-v1","environment":"CI headless Chromium software/browser",
              "notNativeHardware":True,"samples":[],"errors":[]}
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=["--no-sandbox","--use-gl=angle",
                "--use-angle=swiftshader","--enable-webgl","--enable-unsafe-swiftshader"])
            for viewport in ({"width":1440,"height":900},{"width":390,"height":844}):
                page=browser.new_page(viewport=viewport)
                errors=[]
                page.on("pageerror",lambda e:errors.append(str(e)))
                page.goto(f"http://127.0.0.1:{server.server_port}/{EDITOR.name}",
                          wait_until="domcontentloaded")
                page.locator('[data-template-card="cinematic"]').click()
                page.locator('#templatePreviewFrame').wait_for(state="visible")
                stage=page.frame_locator('#templatePreviewFrame')
                stage.locator('section.section').first.wait_for()
                report=measure(page.frame(name=page.locator('#templatePreviewFrame').get_attribute('name')) if
                    page.locator('#templatePreviewFrame').get_attribute('name') else
                    page.locator('#templatePreviewFrame').element_handle().content_frame())
                report["preset"]=f"{viewport['width']}x{viewport['height']}"
                report["pageErrors"]=errors
                evidence["samples"].append(report)
                page.close()
            browser.close()
    finally:
        server.shutdown();server.server_close()
    evidence["pass"]=all(x["sampleFrames"]>=100 and x["documentWidth"]<=x["viewportWidth"]+32
        and x["p95FrameMs"]<120 and not x["pageErrors"] for x in evidence["samples"])
    OUTPUT.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(evidence,ensure_ascii=False,indent=2))
    assert evidence["pass"],"R19 browser viewport performance regression"
if __name__=="__main__":
    run()
