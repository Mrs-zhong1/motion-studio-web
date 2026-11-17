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
    observations={'schema':'motion-studio-r33-to-r39-continuous-film-v2','browser':'chromium',
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
                frame.locator('html[data-r39-film="continuous"]').wait_for(timeout=15000)
                observations['checks']['five_images_in_single_stage']=frame.locator('.r39-frame').count()==5 and frame.locator('.r39-stage').count()==1
                frame.locator('html').evaluate("(el)=>el.style.setProperty('scroll-behavior','auto','important')")
                frame.locator('#r39-story').evaluate("""(el)=>{
                   window.scrollTo({top:el.offsetTop+Math.max(1,el.offsetHeight-innerHeight)*.5,behavior:'instant'})
                }""")
                frame.locator('html[data-r39-chapter="3"]').wait_for(timeout=10000)
                third=frame.locator('.r39-frame[data-index="2"]').evaluate("(el)=>({opacity:Number(el.style.opacity),loaded:el.complete&&el.naturalWidth>0})")
                observations['checks']['real_scroll_reveals_third_scene']=third['opacity']>.95
                observations['checks']['native_third_scene_loaded']=third['loaded']
                # R30 image import must change the real scene image, not only cache.
                src=frame.locator('.r39-frame[data-index="1"]').get_attribute('src')
                observations['checks']['uploaded_photo_reaches_stage']=src.startswith('data:image/png;base64,')
                page.locator('#previewMobile').click()
                observations['checks']['390px_mode']=page.locator('#previewDevice').evaluate("(el)=>el.classList.contains('mobile')")
                page.locator('#previewUse').click()
                exported=page.evaluate("()=>MotionStudioUnified.build()")
                observations['checks']['export_has_same_5_act_film']='data-r39-film="continuous"' in exported and exported.count('class="r39-frame"')==5
                observations['checks']['export_has_one_story_system']='id="r39-story"' in exported and 'function installR16StoryTransitions()' not in exported
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
