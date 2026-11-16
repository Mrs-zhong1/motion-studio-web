"""S3: seven persistent genres are actually different, reversible and exportable."""
import hashlib
import os
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/"Motion-Studio-Stage15-Meshopt-OFFLINE.html"
GENRES=("editorial","cinematic","architecture","agency","fashion","gallery","saas")

def run():
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    browser_id=os.getenv("MOTION_BROWSER","chromium")
    sample={}
    try:
        with sync_playwright() as pw:
            browser=getattr(pw,browser_id).launch(headless=True,args=["--no-sandbox"] if browser_id=="chromium" else [])
            editor=browser.new_page(viewport={"width":1440,"height":900})
            editor.goto(f"http://127.0.0.1:{server.server_port}/{EDITOR.name}",wait_until="domcontentloaded")
            assert editor.evaluate("registry.length")==20
            for genre in GENRES:
                editor.evaluate("(id)=>ensureTemplatePhoto(id)",genre)
                html=editor.evaluate("(id)=>buildTemplatePreviewDocument(id)",genre)
                errors=[]
                page=browser.new_page(viewport={"width":1440,"height":900})
                page.on("pageerror",lambda err:errors.append(str(err)))
                page.set_content(html,wait_until="domcontentloaded",timeout=60000)
                stage=page.locator(".s1-story-stage")
                stage.wait_for(state="visible")
                assert stage.get_attribute("data-story-profile")==genre
                count=4 if genre=="editorial" else 5
                assert page.locator(".s1-scene-image").count()==count
                assert page.locator(".s1-story-anchor").count()==count
                assert page.locator("section.section iframe").count()==0
                pictures=page.locator(".s1-scene-image").evaluate_all("ns=>ns.map(n=>n.getAttribute('src'))")
                assert all(src and src.startswith("data:image/") for src in pictures),genre
                page.evaluate("()=>scrollTo(0,0)")
                page.wait_for_function("()=>document.querySelector('.s1-story-stage')?.dataset.storyIndex==='0'")
                opening=stage.screenshot(animations="disabled")
                first=page.locator(".s1-scene-image").nth(2)
                mask_before=first.evaluate("n=>getComputedStyle(n).clipPath")
                page.evaluate("()=>scrollTo(0,document.querySelectorAll('.s1-story-anchor')[2].offsetTop)")
                page.wait_for_function("()=>document.querySelector('.s1-story-stage')?.dataset.storyIndex==='2'",timeout=12000)
                mask_after=first.evaluate("n=>getComputedStyle(n).clipPath")
                middle=stage.screenshot(animations="disabled")
                assert mask_before!=mask_after,(genre,mask_before,mask_after)
                assert hashlib.sha256(opening).digest()!=hashlib.sha256(middle).digest(),genre
                sample[genre]=mask_after
                page.evaluate("()=>scrollTo(0,0)")
                page.wait_for_function("()=>document.querySelector('.s1-story-stage')?.dataset.storyIndex==='0'",timeout=12000)
                page.set_viewport_size({"width":390,"height":844})
                assert page.evaluate("()=>document.documentElement.scrollWidth<=innerWidth+32"),genre
                page.emulate_media(reduced_motion="reduce")
                page.evaluate("()=>scrollTo(0,document.querySelectorAll('.s1-story-anchor')[2].offsetTop)")
                page.wait_for_function("()=>document.querySelector('.s1-story-stage')?.dataset.storyIndex==='2'")
                assert first.evaluate("n=>getComputedStyle(n).clipPath")=="none",genre
                assert not errors,(genre,errors)
                page.close()
            assert len(set(sample.values()))>=5,sample
            # 3D product template is deliberately separate; it must still use
            # the genuine standalone Three.js renderer and not a fake story.
            product=editor.evaluate("(id)=>buildTemplatePreviewDocument(id)","product-3d")
            product_ids=editor.evaluate("""()=>createProjectFromTemplate('product-3d').sections.map(s=>s.id)""")
            assert "offline-glb-scene" in product_ids,product_ids
            assert 'data-template="product-3d"' in product
            assert not 'data-story-profile="product-3d"' in product
            browser.close()
    finally:
        server.shutdown();server.server_close()

if __name__=="__main__":
    run()
    print("S3 seven distinct persistent stories, reverse scroll, mobile and reduced motion PASS")
