"""R18: real browser imports complete AI asset folder and rejects altered bytes."""
import hashlib
import json
import tempfile
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_r15_asset_batch import make_png

ROOT=Path(__file__).resolve().parents[1]
PAGE=ROOT/"Motion-Studio-Stage15-Meshopt-OFFLINE.html"
IDS=["editorial","product-3d","cinematic","architecture","agency","fashion","gallery","saas"]

def make_folder(directory):
    entries=[]
    for template in IDS:
        for chapter in range(1,5 if template=="editorial" else 6):
            filename=f"{template}-{chapter}.png"
            data=make_png((chapter*31+len(template)*7)%256,(chapter*47)%256,(len(template)*19)%256)+bytes([chapter])*1400
            (directory/filename).write_bytes(data)
            entries.append({"template":template,"chapter":chapter,"file":filename,
                "source":"AI_GENERATED","commercialUseTermsChecked":True,
                "sha256":hashlib.sha256(data).hexdigest()})
    (directory/"manifest.json").write_text(json.dumps({"assets":entries}))
    return entries

def test_full_folder_import():
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
      with tempfile.TemporaryDirectory(prefix="motion-ai-folder-") as tmp:
       directory=Path(tmp)/"ai-assets";directory.mkdir()
       entries=make_folder(directory)
       with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
        page=browser.new_page()
        page.goto(f"http://127.0.0.1:{server.server_port}/{PAGE.name}",wait_until="domcontentloaded")
        page.locator("#aiAssetFolder").set_input_files(str(directory))
        page.wait_for_function("""() => document.querySelector('#aiAssetImportStatus')?.textContent.includes('AI 原创 39 张已加载')""")
        assert page.evaluate("()=>Object.keys(templateOfflinePhotoBundles).length")==8
        sources=page.evaluate("""async()=>{
          await ensureTemplatePhoto('fashion');
          return templateAssetAuditCache.get('fashion').map(x=>x.kind);
        }""")
        assert sources==["ai-generated-image"]*5,sources
        assert page.evaluate("()=>templateThumbnailImages.fashion.startsWith('data:image/')")
        before=page.evaluate("()=>templateOfflinePhotoBundles.editorial[0].source")
        # Mutate only one image: atomic import must reject and retain all previous media.
        wrong=directory/"editorial-1.png"
        wrong.write_bytes(wrong.read_bytes()+b"corruption")
        page.locator("#aiAssetFolder").set_input_files(str(directory))
        page.wait_for_function("""() => document.querySelector('#aiAssetImportStatus')?.textContent.includes('素材 SHA-256 不匹配')""")
        assert page.evaluate("()=>templateOfflinePhotoBundles.editorial[0].source")==before
        assert page.evaluate("()=>registry.length")==20
        browser.close()
    finally:
      server.shutdown();server.server_close()

if __name__=="__main__":
  test_full_folder_import()
  print("R18 complete AI folder import 39/39 and atomic SHA rejection PASS")
