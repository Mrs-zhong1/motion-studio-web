"""Actual official R39 output in real Chromium, not isolated two-scene ZIP."""
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import json,threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/'Motion-Studio-Stage15-Meshopt-OFFLINE.html'
REPORT=ROOT/'R39_FILM_ACCEPTANCE.json'
def run():
 report={'status':'FAIL','fiveActs':[],'errors':[],'productionApproved':False}
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
 threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
   for w,h in ((1440,900),(390,844)):
    editor=browser.new_page(viewport={'width':w,'height':h})
    errors=[]
    editor.on('pageerror',lambda e:errors.append(str(e)))
    editor.goto(f'http://127.0.0.1:{server.server_port}/{EDITOR.name}',wait_until='domcontentloaded')
    editor.locator('[data-template-card="cinematic"]').click()
    frame=editor.locator('#templatePreviewFrame').content_frame
    frame.locator('#r39-stage').wait_for(timeout=15000)
    assert frame.locator('.r39-frame').count()==5
    assert frame.locator('.r39-caption').count()==5
    assert frame.locator('#r39-chapter-menu [data-seek]').count()==5
    assert frame.locator('.r37-stage').count()==0
    editor.locator('#r17PreviewNext').click()
    frame.locator('html[data-r39-chapter="2"]').wait_for(timeout=10000)
    assert editor.locator('#r17PreviewPosition').inner_text().strip().startswith('02 /')
    editor.locator('#r17PreviewPrev').click()
    frame.locator('html[data-r39-chapter="1"]').wait_for(timeout=10000)
    # Every distinct act must actually become the sole visible image/title
    # at its own scroll waypoint, rather than merely existing in the DOM.
    frame.locator('html').evaluate("(el)=>el.style.setProperty('scroll-behavior','auto','important')")
    for index in range(5):
     frame.locator('#r39-story').evaluate("""(el,i)=>{
      const range=Math.max(1,el.offsetHeight-innerHeight);
      window.scrollTo({top:el.offsetTop+(i/4)*range,behavior:'instant'});
     }""",index)
     frame.locator('html[data-r39-chapter="'+str(index+1)+'"]').wait_for(timeout=10000)
     actual=frame.locator('.r39-frame[data-index="'+str(index)+'"]').evaluate("el=>Number(el.style.opacity)")
     title=frame.locator('.r39-caption[data-index="'+str(index)+'"]').evaluate("el=>Number(el.style.opacity)")
     assert actual>.96,(index,actual)
     assert title>.96,(index,title)
     if w==1440:
      frame.locator('html').screenshot(path=str(ROOT/('R39_ACT_'+str(index+1).zfill(2)+'_DESKTOP.png')))

    frame.locator('#r39-menu-toggle').click()
    assert frame.locator('#r39-menu-toggle').get_attribute('aria-expanded')=='true'
    frame.locator('#r39-chapter-menu button').last.click()
    assert frame.locator('#r39-menu-toggle').get_attribute('aria-expanded')=='false'
    frame.locator('html[data-r39-chapter="5"]').wait_for(timeout=10000)
    doc=editor.evaluate("""()=>{
      const project=MotionStudioUnified.createProjectFromTemplate('cinematic');
      MotionStudioUnified.load(project,{resetHistory:true});
      return MotionStudioUnified.build();
    }""")
    assert 'data-r39-film="continuous"' in doc
    assert doc.count('class="r39-frame"')==5
    assert doc.count('class="r39-caption"')==5
    assert 'r14-story-rail' not in doc
    assert 'id="r39-chapter-menu"' in doc
    edited=editor.evaluate("""()=>{
      const p=MotionStudioUnified.createProjectFromTemplate('cinematic');
      p.sections[2].text='MY CUSTOM THIRD ACT';
      p.sections[2].image='data:image/png;base64,aGVsbG8=';
      MotionStudioUnified.load(p,{resetHistory:true});
      return MotionStudioUnified.build();
    }""")
    assert 'MY CUSTOM THIRD ACT' in edited
    assert 'data:image/png;base64,aGVsbG8=' in edited
    assert edited.count('class="r39-frame"')==5
    assert not errors,errors
    report['fiveActs'].append({'viewport':[w,h],'chapterMenu':5,'scenes':5,'exportMatch':True,'customTextAndImage':True})
    editor.close()
   browser.close()
  report['status']='PASS'
 except Exception as ex:
  report['errors'].append(str(ex))
 finally:
  server.shutdown();server.server_close()
  REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+chr(10),encoding='utf-8')
  print(json.dumps(report,ensure_ascii=False,indent=2))
 assert report['status']=='PASS',report
if __name__=='__main__':run()
