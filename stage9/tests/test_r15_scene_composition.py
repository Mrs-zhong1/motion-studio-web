"""R15: verify distinct complete chapter composition in real standalone HTML."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/"Motion-Studio-Stage15-Meshopt-OFFLINE.html"
TEMPLATES=("editorial","product-3d","cinematic","architecture","agency","fashion","gallery","saas")
AUTHORED_SIX=("cinematic","architecture","agency","fashion","gallery","saas")

def test_r15():
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
            editor=browser.new_page(viewport={"width":1440,"height":900})
            editor.goto(f"http://127.0.0.1:{server.server_port}/{EDITOR.name}",wait_until="domcontentloaded")
            assert editor.locator("[data-template-card]").count()==8
            assert editor.locator(".r15-scene-mark").count()==0
            for name in TEMPLATES:
                html=editor.evaluate("(id)=>buildTemplatePreviewDocument(id)",name)
                if name=='editorial':
                    assert 'data-e42-editorial="coherent-print"' in html,name
                    assert html.count('class="e42-spread"')==4,name
                    assert html.count('class="e42-type"')==4,name
                    assert '<iframe' not in html,name
                elif name=='cinematic':
                    assert 'data-r39-film="continuous"' in html,name
                    assert html.count('class="r39-frame"')==5,name
                    assert html.count('class="r39-caption"')==5,name
                else:
                    assert 'r15-scene-mark' in html,name
                    assert f'data-template="{name}"' in html,name
                    assert html.count('class="r15-scene-mark"')==(5 if name in AUTHORED_SIX else (3 if name=="editorial" else 4)),name
            for name in ("cinematic","agency","saas"):
                await_art=editor.evaluate("(id)=>ensureTemplatePhoto(id)",name)
                html=editor.evaluate("(id)=>buildTemplatePreviewDocument(id)",name)
                page=browser.new_page(viewport={"width":1440,"height":900},reduced_motion="no-preference")
                errors=[];page.on("pageerror",lambda error:errors.append(str(error)))
                page.set_content(html,wait_until="domcontentloaded",timeout=60000)
                if name=='cinematic':
                    assert page.locator('.r39-stage').count()==1
                    assert page.locator('.r39-frame').count()==5
                    assert page.locator('.r39-caption').count()==5
                    assert page.locator('.r37-stage').count()==0
                    page.set_viewport_size({'width':390,'height':844})
                    assert page.locator('.r39-stage').is_visible()
                    assert page.locator('html').evaluate('el=>el.scrollWidth<=innerWidth+32')
                    assert not errors,(name,errors)
                    page.close()
                    continue
                sections=page.locator("section.section.authored-six")
                assert sections.count()==5,(name,sections.count())
                assert sections.locator(".r15-scene-mark").count()==5,name
                assert sections.nth(0).locator(".r15-scene-mark").inner_text().strip()
                first=sections.nth(1)
                middle=sections.nth(2)
                dimensions=page.evaluate("""() => {
                    function measure(i){
                      const sec=document.querySelector('section.section[data-index="'+i+'"]');
                      const art=sec.querySelector('.section-art').getBoundingClientRect();
                      const stage=sec.querySelector('iframe').getBoundingClientRect();
                      return {artX:art.x,stageX:stage.x,width:art.width,stageWidth:stage.width,
                              minHeight:Math.min(art.height,stage.height),sectionWidth:sec.getBoundingClientRect().width};
                    }
                    return {scene1:measure(1),scene2:measure(2)}
                }""")
                if name=="cinematic":
                    # R37–R38 film no longer mounts unrelated iframe cards:
                    # the photographic image is the ONE full-stage visual.
                    assert page.locator('.r37-stage').count()==5,(name,dimensions)
                    assert all(x["width"]>=x["sectionWidth"]*.95 and x["stageWidth"]==0
                               for x in dimensions.values()),(name,dimensions)
                else:
                    assert dimensions["scene1"]["artX"]<dimensions["scene1"]["stageX"],(name,dimensions)
                    assert dimensions["scene2"]["artX"]>dimensions["scene2"]["stageX"],(name,dimensions)
                    assert all(x["minHeight"]>=200 and x["width"]>=70 and x["stageWidth"]>=70
                               for x in dimensions.values()),(name,dimensions)
                page.set_viewport_size({"width":390,"height":844})
                page.wait_for_timeout(150)
                mobile=middle.evaluate("""sec=>{
                  const a=sec.querySelector('.section-art').getBoundingClientRect();
                  const f=sec.querySelector('iframe').getBoundingClientRect();
                  return {artTop:a.top,frameTop:f.top,bodyWidth:document.documentElement.scrollWidth,
                          viewport:innerWidth,artW:a.width,frameW:f.width}
                }""")
                if name!='cinematic':
                    assert mobile["artTop"]<mobile["frameTop"],(name,mobile)
                else:
                    assert mobile["artW"]>=mobile["viewport"]*.95,(name,mobile)
                assert mobile["bodyWidth"]<=mobile["viewport"]+32,(name,mobile)
                assert not errors,(name,errors)
                page.close()
            browser.close()
    finally:
        server.shutdown();server.server_close()

if __name__=="__main__":
    test_r15()
    print("R15 PASS: eight narratives and three multi-act geometry/mobile exports")
