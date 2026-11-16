"""R15-02: photo batch workflow, real files, rollback, export & save invariants."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import struct
import threading
import zlib
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/"Motion-Studio-Stage15-Meshopt-OFFLINE.html"

def make_png(r,g,b):
    def chunk(t,data):return struct.pack("!I",len(data))+t+data+struct.pack("!I",zlib.crc32(t+data)&0xffffffff)
    pixels=b"".join(b"\x00"+bytes([r,g,b])*24 for _ in range(24))
    return b"\x89PNG\r\n\x1a\n"+chunk(b'IHDR',struct.pack("!2I5B",24,24,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(pixels))+chunk(b'IEND',b'')

def test_r15_asset_batch():
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
            page=browser.new_page(viewport={"width":1440,"height":900},accept_downloads=True)
            errors=[];page.on("pageerror",lambda err:errors.append(str(err)))
            page.goto(f"http://127.0.0.1:{server.server_port}/{EDITOR.name}",wait_until="domcontentloaded")
            page.locator('[data-template-card="cinematic"]').click()
            page.locator("#previewUse").click()
            original=page.evaluate("JSON.parse(JSON.stringify(project))")
            assert original["templateId"]=="cinematic"
            assert len(original["sections"])==5
            page.locator('[data-asset-tier-button="l4"]').click()
            assert page.locator("#r15BulkImageButton").is_visible()
            files=[{"name":f"scene-{i}.png","mimeType":"image/png","buffer":make_png(*rgb)}
                   for i,rgb in enumerate(((230,20,70),(30,160,80),(30,80,205)))]
            page.locator("#r15BulkImageInput").set_input_files(files)
            page.wait_for_function("()=>document.querySelector('#r15BulkImageResult').textContent.includes('已更新 3')")
            result=page.evaluate("JSON.parse(JSON.stringify(project))")
            assert result["templateId"]==original["templateId"]
            assert len(result["sections"])==len(original["sections"])
            for i in range(3):
                assert result["sections"][i]["image"].startswith("data:image/jpeg;base64,"),i
                assert result["sections"][i]["text"]==original["sections"][i]["text"]
                assert result["sections"][i]["id"]==original["sections"][i]["id"]
            assert len(set(result["sections"][i]["image"] for i in range(3)))==3
            assert result["sections"][3]["image"]==original["sections"][3]["image"]
            with page.expect_download() as saved:
                page.locator("#saveProject").click()
            assert saved.value.path().stat().st_size>3000
            exported=page.evaluate("exportDocument()")
            assert exported.count('class="s1-scene-image"')==5
            assert exported.count('src="data:image/jpeg;base64,')>=3
            assert 'class="s1-story-stage"' in exported
            assert 'installR14Navigator' in exported
            assert result["sections"][0]["image"] in exported
            # Batch failure must not silently overwrite even the first section.
            before=page.evaluate("JSON.stringify(project)")
            invalid=[files[0],{"name":"not-image.txt","mimeType":"text/plain","buffer":b"not an image"}]
            page.locator("#r15BulkImageInput").set_input_files(invalid)
            page.wait_for_function("()=>document.querySelector('#r15BulkImageResult').textContent.includes('导入失败')")
            assert page.evaluate("JSON.stringify(project)")==before
            assert not errors,errors
            browser.close()
    finally:
        server.shutdown();server.server_close()

if __name__=="__main__":
    test_r15_asset_batch()
    print("R15-02 PASS: batch real PNGs -> embedded JPEG -> HTML export -> atomic rollback")
