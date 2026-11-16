"""R33 real-web Cinematic continuity after native photo import: no motion mock."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import json,tempfile,threading
from playwright.sync_api import sync_playwright
from test_r30_cinematic_trial import large_png

ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/'Motion-Studio-Stage15-Meshopt-OFFLINE.html'
REPORT=ROOT/'R33_NATIVE_SCROLL_ACCEPTANCE.json'
def run():
    observations={'schema':'motion-studio-r33-scroll-v1','browser':'chromium',
                  'pass':False,'checks':{},'errors':[]}
    with tempfile.TemporaryDirectory() as tmp:
        images=[]
        for index in (1,2):
            path=Path(tmp)/f'r33-{index:02d}.png'
            path.write_bytes(large_png(2+index*30))
            images.append(str(path))
        server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
        threading.Thread(target=server.serve_forever,daemon=True).start()
        try:
            with sync_playwright() as pw:
                browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
                page=browser.new_page(viewport={'width':1440,'height':900})
                js_errors=[]
                page.on('pageerror',lambda e:js_errors.append(str(e)))
                page.goto(f'http://127.0.0.1:{server.server_port}/{EDITOR.name}',wait_until='domcontentloaded')
                page.locator('[data-template-card="cinematic"]').click()
                page.wait_for_function("()=>templatePhotoCache.has('cinematic')")
                page.locator('#r30TrialFiles').set_input_files(images)
                page.wait_for_function("()=>document.querySelector('#r30TrialPreviewStatus').textContent.includes('已替换 Cinematic')")
                observations['checks']['two_images_imported']=True
                frame=page.locator('#templatePreviewFrame').content_frame
                art=frame.locator('.section.designed-chapter').nth(2)
                frame.locator('body.r16-story-ready').wait_for(timeout=15000)
                frame.locator('style#r31-export-story-continuity').wait_for()
                first=art.evaluate("(el)=>({r:el.dataset.r16Progress,opacity:getComputedStyle(el.querySelector('.section-art')).opacity})")
                observations['checks']['native_image_not_dimmed']=float(first['opacity'])>=.85
                art.evaluate("(el)=>el.scrollIntoView({block:'center',behavior:'instant'})")
                frame.locator('html').evaluate("(el)=>el.ownerDocument.defaultView.dispatchEvent(new Event('scroll'))")
                frame.locator('html').evaluate("(el)=>new Promise(res=>setTimeout(res,250))")
                second=art.evaluate("(el)=>({r:el.dataset.r16Progress,reveal:el.querySelector('.section-art').style.getPropertyValue('--r16-reveal'),opacity:getComputedStyle(el.querySelector('.section-art')).opacity})")
                observations['checks']['real_scroll_updates_r16_progress']=float(second['r'])>float(first['r'])
                observations['checks']['real_scroll_reveals_photo']=float(second['reveal'].rstrip('%'))>=60
                observations['checks']['photo_stays_visible']=float(second['opacity'])>=.85
                page.locator('#previewMobile').click()
                observations['checks']['390px_mode']=page.locator('#previewDevice').evaluate("(el)=>el.classList.contains('mobile')")
                page.locator('#previewUse').click()
                export=page.evaluate("()=>MotionStudioUnified.build()")
                observations['checks']['export_has_same_cinematic_style']='id="r31-export-story-continuity"' in export
                observations['checks']['export_has_one_story_system']='installR16StoryTransitions' in export and export.count('function installR16StoryTransitions()')==1
                observations['checks']['no_page_js_exceptions']=not js_errors
                observations['errors']=js_errors
                observations['pass']=all(observations['checks'].values())
                browser.close()
        except Exception as exc:
            observations['errors'].append(str(exc))
        finally:
            server.shutdown();server.server_close()
    REPORT.write_text(json.dumps(observations,ensure_ascii=False,indent=2)+chr(10),encoding='utf-8')
    print(json.dumps(observations,ensure_ascii=False,indent=2))
    assert observations['pass'],observations
if __name__=='__main__':run()
