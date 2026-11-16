"""R18 browser test: AI media provenance survives template load, save and reload."""
import base64
import json
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_r15_asset_batch import make_png

ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/"Motion-Studio-Stage15-Meshopt-OFFLINE.html"

def test_ai_provenance():
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
            page=browser.new_page(accept_downloads=True)
            errors=[]
            page.on("pageerror",lambda e:errors.append(str(e)))
            page.goto(f"http://127.0.0.1:{server.server_port}/{EDITOR.name}",wait_until="domcontentloaded")
            images=["data:image/png;base64,"+base64.b64encode(make_png(42+i*11,120+i*17,70+i*31)).decode("ascii") for i in range(5)]
            page.evaluate("""images=>{
                templateOfflinePhotoBundles.cinematic=images.map((media,i)=>({
                   media,source:'ai-generated://cinematic/'+(i+1)+'/'+String(i+1).repeat(16)
                }));
                templatePhotoCache.clear();templateAssetAuditCache.clear();
            }""",images)
            page.evaluate("async()=>await ensureTemplatePhoto('cinematic')")
            rows=page.evaluate("()=>templateAssetAuditCache.get('cinematic')")
            assert len(rows)==5 and all(r["kind"]=="ai-generated-image" for r in rows),rows
            project=page.evaluate("()=>createProjectFromTemplate('cinematic')")
            page.evaluate("(x)=>loadProject(x)",project)
            saved=page.evaluate("()=>JSON.parse(JSON.stringify(window.project))")
            assert all(s["imageMeta"]["kind"]=="ai-generated-image" for s in saved["sections"])
            assert all(s["imageMeta"]["source"].startswith("ai-generated://") for s in saved["sections"])
            page.evaluate("(x)=>loadProject(x)",saved)
            assert page.evaluate("()=>r15MediaAudit().counts.aiGenerated")==5
            assert page.evaluate("()=>r15MediaAudit().counts.photography")==0
            assert not errors,errors
            browser.close()
    finally:
        server.shutdown();server.server_close()

if __name__=="__main__":
    test_ai_provenance()
    print("R18 AI source metadata browser round-trip PASS")
