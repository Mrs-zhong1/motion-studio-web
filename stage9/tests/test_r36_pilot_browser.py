"""R36 pilot real Chromium acceptance: shared stage + collapsible rail.

Images are still from current source pack; test does not approve its visual
quality. This is an automated geometry/interaction check, not art direction.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import json,threading
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/'Motion-Studio-Stage15-Meshopt-OFFLINE.html'
OUTPUT=ROOT/'R36_PILOT_VISUAL_TEST.json'

def run():
 report={'status':'FAIL','checks':[],'errors':[],'screenshots':[],'humanArtDirection':'HOLD'}
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
 threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
   for template in ('product-3d','cinematic','editorial'):
    for width,height in ((1440,900),(390,844)):
     page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
     js_errors=[]
     page.on('pageerror',lambda e:js_errors.append(str(e)))
     page.goto(f'http://127.0.0.1:{server.server_port}/{EDITOR.name}',wait_until='domcontentloaded')
     assert page.locator('#discoveryView').is_visible()
     page.locator(f'[data-template-card="{template}"]').click()
     iframe=page.locator('#templatePreviewFrame').content_frame
     iframe.locator('section.section').first.wait_for()
     iframe.locator('.r14-story-rail').wait_for()
     is_pilot=template in ('product-3d','cinematic')
     assert iframe.locator('style#r36-fullstage-css').count()==(1 if is_pilot else 0)
     assert iframe.locator('.r36-nav-toggle').count()==(1 if is_pilot else 0)
     assert iframe.locator('.r14-rail-chapters > button').count()>=4
     if is_pilot:
      nav=iframe.locator('.r14-story-rail')
      nav.evaluate("(el)=>el.scrollIntoView({block:'nearest'})")
      assert not nav.evaluate("(el)=>el.classList.contains('r36-open')")
      assert nav.evaluate("(el)=>el.getBoundingClientRect().width")<60
      toggle=iframe.locator('.r36-nav-toggle')
      toggle.click()
      assert nav.evaluate("(el)=>el.classList.contains('r36-open')")
      assert toggle.get_attribute('aria-expanded')=='true'
      iframe.locator('body').press('Escape')
      assert toggle.get_attribute('aria-expanded')=='false'
      if template=='cinematic':
       section=iframe.locator('section.section.designed-chapter').nth(1)
      else:
       section=iframe.locator('section.section.designed-chapter').first
      section.scroll_into_view_if_needed()
      geometry=section.evaluate("""(el)=>{
       const art=el.querySelector('.section-art'), frame=el.querySelector('iframe');
       const a=art?.getBoundingClientRect(),f=frame?.getBoundingClientRect(),s=el.getBoundingClientRect();
       return {display:getComputedStyle(el).display,sectionW:s.width,
         artW:a?.width,artH:a?.height,frameW:f?.width,frameH:f?.height,
         frameLeft:f?.left-s.left,artLeft:a?.left-s.left,
         overflow:document.documentElement.scrollWidth-innerWidth}
      }""")
      assert geometry['display']=='block',geometry
      assert geometry['artW']>=geometry['sectionW']*.95,geometry
      if template=='cinematic':
       assert iframe.locator('style#r37-final-style').count()==1
       assert iframe.locator('.r37-stage').count()==5
       assert iframe.locator('.r37-scene').count()==5
       assert geometry['frameW']==0,geometry  # redundant mini-demo hidden
       assert iframe.locator('.r37-stage .designed-chapter-heading').count()==5
      else:
       assert geometry['frameW']>=geometry['sectionW']*.54,geometry
      assert geometry['overflow']<=32,geometry
      assert iframe.locator('body').evaluate("el=>el.dataset.motionTemplate")==template
      report['checks'].append({'template':template,'viewport':[width,height],'stage':geometry,'nav':'collapsed and keyboard operable'})
     else:
      report['checks'].append({'template':template,'viewport':[width,height],'unchanged':True})
     export=page.evaluate("""(t)=>{ const doc=MotionStudioUnified.createProjectFromTemplate(t);
       MotionStudioUnified.load(doc,{resetHistory:true});return MotionStudioUnified.build()}""",template)
     assert ('id="r36-fullstage-css"' in export)==is_pilot
     assert ('id="r36-fullstage-runtime"' in export)==is_pilot
     assert ('id="r37-final-style"' in export)==is_pilot
     assert ('id="r37-final-runtime"' in export)==(template=='cinematic')
     assert not js_errors,js_errors
     page.close()
   browser.close()
  report['status']='PASS'
 except Exception as exc:
  report['errors'].append(str(exc))
 finally:
  server.shutdown();server.server_close()
  OUTPUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+chr(10),encoding='utf-8')
  print(json.dumps(report,ensure_ascii=False,indent=2))
 assert report['status']=='PASS',report
if __name__=='__main__':run()
