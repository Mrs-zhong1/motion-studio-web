"""R16 — actual scroll-scrub chapter reveals in exported websites."""
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/"Motion-Studio-Stage15-Meshopt-OFFLINE.html"
TEMPLATES=("editorial","product-3d","cinematic","architecture","agency","fashion","gallery","saas")

def test_r16():
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
            editor=browser.new_page(viewport={"width":1440,"height":900})
            editor.goto(f"http://127.0.0.1:{server.server_port}/{EDITOR.name}",wait_until="domcontentloaded")
            assert editor.locator(".r16-story-ready").count()==0
            for template in TEMPLATES:
                exported=editor.evaluate("(id)=>buildTemplatePreviewDocument(id)",template)
                if template in ("cinematic","editorial"):
                    assert ('data-r39-film="continuous"' if template=="cinematic" else 'data-e42-editorial="coherent-print"') in exported,template
                    continue
                assert "installR16StoryTransitions" in exported,template
                assert f'.page[data-template="{template}"] .section.designed-chapter .section-art' in exported,template
            # Test actual scroll and computed clips, not only source selectors.
            # Hydrate real bundled image data just as previewTemplate() does.
            editor.evaluate("async()=>await ensureTemplatePhoto('architecture')")
            html=editor.evaluate("(id)=>buildTemplatePreviewDocument(id)","architecture")
            page=browser.new_page(viewport={"width":1440,"height":900})
            errors=[];page.on("pageerror",lambda error:errors.append(str(error)))
            page.set_content(html,wait_until="domcontentloaded",timeout=60000)
            assert page.locator("body.r16-story-ready").count()==1
            chapter=page.locator(".section.designed-chapter[data-index='2']")
            chapter.wait_for()
            metrics=lambda:chapter.evaluate("""sec=>{
                const image=sec.querySelector('.section-art');
                return {clip:getComputedStyle(image).clipPath,
                        reveal:parseFloat(image.style.getPropertyValue('--r16-reveal')),
                        progress:Number(sec.dataset.r16Progress),
                        redraw:Number(document.documentElement.dataset.r16RedrawCount),
                        scrollWidth:document.documentElement.scrollWidth,viewport:innerWidth}
            }""")
            before=metrics()
            assert before["reveal"]<=2.0,before
            chapter.scroll_into_view_if_needed(timeout=10000)
            page.wait_for_function("""()=>Number(document.querySelector('.section[data-index="2"]').dataset.r16Progress)>.75""",timeout=12000)
            after=metrics()
            assert after["reveal"]>before["reveal"]+50,(before,after)
            assert after["clip"]!="none",after
            assert after["redraw"]>before["redraw"],(before,after)
            page.set_viewport_size({"width":390,"height":844})
            chapter.scroll_into_view_if_needed(timeout=10000)
            page.wait_for_timeout(180)
            mobile=metrics()
            assert mobile["scrollWidth"]<=mobile["viewport"]+32,mobile
            page.emulate_media(reduced_motion="reduce")
            page.wait_for_timeout(150)
            assert chapter.locator(".section-art").evaluate("e=>getComputedStyle(e).clipPath")=="none"
            assert not errors,errors
            page.close()
            browser.close()
    finally:
        server.shutdown();server.server_close()

if __name__=="__main__":
    test_r16()
    print("R16 PASS — distinct template CSS, real scroll-driven clip progress, mobile, reduced motion")
