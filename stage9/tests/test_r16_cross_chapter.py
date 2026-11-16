"""R16-03..06: adjacent color bridges, reduced motion, performance and export."""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
import threading
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/"Motion-Studio-Stage15-Meshopt-OFFLINE.html"
IDS=("editorial","product-3d","cinematic","architecture","agency","fashion","gallery","saas")

def test_r16_bridges():
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
            editor=browser.new_page(viewport={"width":1440,"height":900})
            editor.goto(f"http://127.0.0.1:{server.server_port}/{EDITOR.name}",wait_until="domcontentloaded")
            assert editor.locator(".r16-linked-chapter").count()==0
            for template in IDS:
                html=editor.evaluate("(id)=>buildTemplatePreviewDocument(id)",template)
                assert "r16BridgeCss" not in html, "Raw variable name must be interpolated away"
                assert "r16-linked-chapter" in html
                assert f'.page[data-template="{template}"]' in html
            editor.evaluate("async()=>await ensureTemplatePhoto('cinematic')")
            html=editor.evaluate("(id)=>buildTemplatePreviewDocument(id)","cinematic")
            page=browser.new_page(viewport={"width":1440,"height":900})
            errors=[];page.on("pageerror",lambda e:errors.append(str(e)))
            page.set_content(html,wait_until="domcontentloaded",timeout=60000)
            sections=page.locator(".page > section.section")
            assert sections.count()==5
            assert page.locator(".r16-linked-chapter").count()==sections.count()
            assert page.locator("nav.r14-story-rail").count()==1
            section=sections.nth(1)
            marker=section.locator(".r15-scene-mark")
            assert marker.count()==1
            expected=page.evaluate("""()=>{
              const a=document.querySelectorAll('.page > section.section');
              return getComputedStyle(a[2]).backgroundColor;
            }""")
            def measure():
                return section.evaluate("""s=>{
                  const before=getComputedStyle(s,'::before');
                  return {
                    nextColor:s.style.getPropertyValue('--r16-bridge-color'),
                    bridge:Number(s.dataset.r16Bridge),
                    incoming:parseFloat(s.style.getPropertyValue('--r16-incoming')),
                    visualOpacity:before.opacity,
                    backdrop:before.backgroundImage,
                    markerOpacity:getComputedStyle(s.querySelector('.r15-scene-mark')).opacity,
                    redraw:Number(document.documentElement.dataset.r16RedrawCount||0),
                    bodyWidth:document.documentElement.scrollWidth,
                    viewport:window.innerWidth
                  };
                }""")
            assert measure()["nextColor"]==expected
            # Compare same chapter at two scroll positions, keeping viewport scrolling
            # within a realistic full-page journey.
            page.evaluate("""()=>{
              const s=document.querySelectorAll('.page > section.section')[1];
              scrollTo(0,scrollY+s.getBoundingClientRect().bottom-innerHeight*.8);
            }""")
            page.wait_for_timeout(180)
            early=measure()
            page.evaluate("""()=>{
              const s=document.querySelectorAll('.page > section.section')[1];
              scrollTo(0,scrollY+s.getBoundingClientRect().bottom-innerHeight*.15);
            }""")
            page.wait_for_timeout(180)
            late=measure()
            assert late["bridge"]>early["bridge"]+.12,(early,late)
            assert late["visualOpacity"]!=early["visualOpacity"],(early,late)
            assert late["redraw"]>early["redraw"]
            assert late["backdrop"]!="none"
            page.set_viewport_size({"width":390,"height":844})
            page.wait_for_timeout(180)
            mobile=measure()
            assert mobile["bodyWidth"]<=mobile["viewport"]+32,mobile
            page.emulate_media(reduced_motion="reduce")
            page.wait_for_timeout(180)
            reduced=measure()
            assert reduced["bridge"]==0,reduced
            assert section.evaluate("s=>getComputedStyle(s,'::before').display")=="none"
            assert reduced["markerOpacity"]=="1",reduced
            assert not errors,errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()

if __name__=="__main__":
    test_r16_bridges()
    print("R16-03..06 PASS: all eight exports, adjacent chapter bridges, mobile, nav, motion safety")
