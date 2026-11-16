"""R16-02 – real parallax layer geometry, not a static CSS declaration."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/"Motion-Studio-Stage15-Meshopt-OFFLINE.html"
TEMPLATES=("editorial","product-3d","cinematic","architecture","agency","fashion","gallery","saas")

def test_r16_multiplane():
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
            editor=browser.new_page(viewport={"width":1440,"height":900})
            editor.goto(f"http://127.0.0.1:{server.server_port}/{EDITOR.name}",wait_until="domcontentloaded")
            assert editor.locator("#discoveryView").is_visible()
            assert editor.locator(".r16-story-ready").count()==0
            for name in TEMPLATES:
                out=editor.evaluate("(id)=>buildTemplatePreviewDocument(id)",name)
                assert "const signatures=" in out,name
                assert f"data-template=\"{name}\"" in out,name
                assert "--r16-photo-y" in out,name
                assert "--r16-mist-x" in out,name
            editor.evaluate("async()=>await ensureTemplatePhoto('product-3d')")
            html=editor.evaluate("(id)=>buildTemplatePreviewDocument(id)","product-3d")
            page=browser.new_page(viewport={"width":1440,"height":900})
            errors=[];page.on("pageerror",lambda err:errors.append(str(err)))
            page.set_content(html,wait_until="domcontentloaded",timeout=60000)
            chapter=page.locator('.section.designed-chapter[data-index="2"]')
            chapter.wait_for()
            assert chapter.locator(".section-art").count()==1
            assert chapter.locator(".section-art .motion-atmosphere").count()==1
            def measure():
                return chapter.evaluate("""sec=>{
                  const art=sec.querySelector('.section-art');
                  const type=sec.querySelector('.designed-chapter-heading');
                  const haze=sec.querySelector('.motion-atmosphere');
                  const style=getComputedStyle(art);
                  return {
                    depth:Number(sec.dataset.r16Depth||0),
                    photoX:sec.style.getPropertyValue('--r16-photo-x'),
                    photoY:sec.style.getPropertyValue('--r16-photo-y'),
                    typeY:sec.style.getPropertyValue('--r16-type-y'),
                    mistX:sec.style.getPropertyValue('--r16-mist-x'),
                    artPosition:style.backgroundPosition,
                    typeTransform:getComputedStyle(type).transform,
                    hazeTransform:getComputedStyle(haze).transform,
                    redraw:Number(document.documentElement.dataset.r16RedrawCount||0),
                    totalWidth:document.documentElement.scrollWidth,
                    width:innerWidth
                  };
                }""")
            # Keep chapter visible and move it through two camera positions.
            page.evaluate("""()=>{
              const c=document.querySelector('.section.designed-chapter[data-index="2"]');
              window.scrollTo(0,window.scrollY+c.getBoundingClientRect().top-innerHeight*.76);
            }""")
            page.wait_for_timeout(180)
            early=measure()
            evidence=Path("/tmp/motion-studio-visual-audit")
            evidence.mkdir(parents=True,exist_ok=True)
            (evidence/"r16-cinematic-multiplane-early.png").write_bytes(
                page.screenshot(animations="disabled"))
            page.evaluate("""()=>{
              const c=document.querySelector('.section.designed-chapter[data-index="2"]');
              window.scrollTo(0,window.scrollY+c.getBoundingClientRect().top-innerHeight*.15);
            }""")
            page.wait_for_timeout(180)
            late=measure()
            (evidence/"r16-cinematic-multiplane-late.png").write_bytes(
                page.screenshot(animations="disabled"))
            assert abs(early["depth"]-late["depth"])>.12,(early,late)
            for prop in ("photoY","typeY","mistX","artPosition","typeTransform","hazeTransform"):
                assert early[prop]!=late[prop],(prop,early,late)
            assert late["redraw"]>early["redraw"],(early,late)
            page.set_viewport_size({"width":390,"height":844})
            page.wait_for_timeout(160)
            mobile=measure()
            assert mobile["totalWidth"]<=mobile["width"]+32,mobile
            page.emulate_media(reduced_motion="reduce")
            page.wait_for_timeout(160)
            reduced=measure()
            assert reduced["depth"]==0,reduced
            assert reduced["typeTransform"]=="none",reduced
            assert reduced["hazeTransform"]=="none",reduced
            assert not errors,errors
            browser.close()
    finally:
        server.shutdown();server.server_close()

if __name__=="__main__":
    test_r16_multiplane()
    print("R16-02 PASS: eight cameras, real scroll-depth/photo/type/atmosphere, mobile & reduced motion")
