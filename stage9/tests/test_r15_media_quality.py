"""R15-04: real photo coverage reporting, provenance persistence, and download audit.

Uses browser-generated valid PNG fixtures to avoid CDN availability influencing
provenance correctness. The ordinary E2E still covers the actual template UI.
"""
import base64
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright
from test_r15_asset_batch import make_png

ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/"Motion-Studio-Stage15-Meshopt-OFFLINE.html"

def test_r15_media_quality():
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
            page=browser.new_page(viewport={"width":1440,"height":900},accept_downloads=True)
            errors=[];page.on("pageerror",lambda err:errors.append(str(err)))
            page.goto(f"http://127.0.0.1:{server.server_port}/{EDITOR.name}",wait_until="domcontentloaded")
            # Each built-in chapter must have its own candidate URL (5 for most
            # templates, 4 for editorial) rather than silently substituting an
            # illustration because there are no later photographic sources.
            all_sources=page.evaluate("""() => {
                const result={};
                for(const t of templateCatalog){
                    const urls=[templateThumbnailImages[t.id],...(templateExtraPhotos[t.id]||[])];
                    result[t.id]={chapters:t.sections.length,urls};
                }
                return result;
            }""")
            for name,record in all_sources.items():
                assert len(record["urls"])>=record["chapters"],(name,record)
                assert len(set(record["urls"][:record["chapters"]]))==record["chapters"],name
                assert all(url.startswith("https://images.unsplash.com/photo-") for url in record["urls"]),name

            fixture=["data:image/png;base64,"+base64.b64encode(
                make_png(40+i*37,90+i*21,120+i*13)).decode("ascii") for i in range(5)]
            page.evaluate("""images=>{
               const urls=[templateThumbnailImages.cinematic,...templateExtraPhotos.cinematic];
               const mapped=new Map(urls.map((url,i)=>[url,images[i]]));
               photoToInline=async url=>mapped.get(url)||'';
            }""",fixture)
            page.evaluate("async()=>{templatePhotoCache.delete('cinematic');await ensureTemplatePhoto('cinematic')}")
            audit=page.evaluate("()=>templateAssetAuditCache.get('cinematic')")
            assert len(audit)==5,audit
            assert all(row["kind"]=="unsplash-photo" and row["source"] for row in audit),audit
            result=page.evaluate("()=>createProjectFromTemplate('cinematic')")
            page.evaluate("data=>loadProject(data)",result)
            page.locator('[data-asset-tier-button="l4"]').click()
            coverage=page.locator("#r15MediaCoverage")
            assert coverage.is_visible()
            assert "真实摄影 5" in coverage.inner_text()
            assert "原创插画占位 0" in coverage.inner_text()
            assert "HOLD" in coverage.inner_text()
            assert page.locator(".r15-photo-source").count()==5
            with page.expect_download() as info:
                page.locator("#r15MediaAuditExport").click()
            manifest=json.loads(info.value.path().read_text(encoding="utf-8"))
            assert manifest["counts"]["photography"]==5
            assert manifest["counts"]["missing"]==0
            assert manifest["commercialReleaseStatus"]=="HOLD"
            assert all(ch["sourceUrl"] and ch["rightsReviewed"] is False for ch in manifest["chapters"])
            with page.expect_download() as info:
                page.locator("#saveProject").click()
            saved=json.loads(info.value.path().read_text(encoding="utf-8"))
            assert all(s["imageMeta"]["kind"]=="unsplash-photo" for s in saved["sections"])
            # Source provenance must survive closing/reopening with empty cache.
            page.evaluate("()=>{templatePhotoCache.clear();templateAssetAuditCache.clear()}")
            page.evaluate("data=>loadProject(data)",saved)
            assert page.evaluate("()=>r15MediaAudit().counts.photography")==5
            assert "真实摄影 5" in coverage.inner_text()
            assert page.locator(".r15-photo-source").count()==5
            # Valid images but duplicate content are explicitly called out.
            dupe=page.evaluate("()=>JSON.parse(JSON.stringify(project))")
            dupe["sections"][2]["image"]=dupe["sections"][1]["image"]
            page.evaluate("data=>loadProject(data)",dupe)
            assert page.evaluate("()=>r15MediaAudit().counts.duplicates")==1
            assert page.locator("#r15MediaCoverage").get_attribute("data-photo-quality")=="HOLD"
            assert not errors,errors
            browser.close()
    finally:
        server.shutdown();server.server_close()

if __name__=="__main__":
    test_r15_media_quality()
    print("R15-04 PASS: source coverage, rights HOLD, export, JSON round-trip, duplicates")
