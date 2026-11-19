"""R42 browser story: visually verify editorial four real magazine spreads,
animation and independent full-bleed photo without duplicated dark mini-demo.
"""
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import threading,json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/'Motion-Studio-Stage15-Meshopt-OFFLINE.html'
REPORT=ROOT/'R42_EDITORIAL_ACCEPTANCE.json'
def run():
 report={'status':'FAIL','checks':[],'errors':[],'releaseApproved':False}
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
 threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
   for w,h in ((1440,900),(390,844)):
    page=browser.new_page(viewport={'width':w,'height':h})
    errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
    page.goto(f'http://127.0.0.1:{server.server_port}/{EDITOR.name}',wait_until='domcontentloaded')
    page.locator('[data-template-card="editorial"]').click()
    frame=page.locator('#templatePreviewFrame').content_frame
    frame.locator('html[data-e42-editorial="coherent-print"]').wait_for(timeout=20000)
    assert frame.locator('.e42-spread').count()==4
    assert frame.locator('.e42-image').count()==4
    assert frame.locator('.e42-type h1').count()==4
    assert frame.locator('.e42-progress button').count()==4
    assert frame.locator('iframe').count()==0
    # Parent preview chapter controls must genuinely move the embedded page,
    # not merely change the toolbar counter.
    if w>=760:
     page.locator('#r17PreviewNext').click()
     frame.locator('html[data-e42-active="2"]').wait_for(timeout=10000)
     assert page.locator('#r17PreviewPosition').inner_text().strip().startswith('02 /')
     page.locator('#r17PreviewPrev').click()
     frame.locator('html[data-e42-active="1"]').wait_for(timeout=10000)
    assert frame.locator('.r14-story-rail').count()==0
    assert frame.locator('.r38-marker').count()==0
    scenes=frame.locator('.e42-image').evaluate_all("""imgs=>imgs.map(img=>({
       complete:img.complete,loaded:img.naturalWidth>0,src:img.getAttribute('src').startsWith('data:image/'),
       photo:img.getBoundingClientRect().width}))""")
    assert all(x['loaded'] and x['src'] and x['photo']>=100 for x in scenes),scenes
    assert frame.locator('html').evaluate('el=>el.scrollWidth<=innerWidth+32')
    for i in range(4):
     frame.locator('html').evaluate("el=>el.style.setProperty('scroll-behavior','auto','important')")
     frame.locator('.e42-spread').nth(i).evaluate("""el=>{
       scrollTo({top:scrollY+el.getBoundingClientRect().top,behavior:'instant'})
     }""")
     frame.locator(f'html[data-e42-active="{i+1}"]').wait_for(timeout=10000)
     props=frame.locator('.e42-spread').nth(i).evaluate("""el=>({
      title:el.querySelector('.e42-type h1').textContent,
      sticky:getComputedStyle(el.querySelector('.e42-sticky')).position,
      progress:el.style.getPropertyValue('--e42-progress')})""")
     assert props['sticky']=='sticky',props
     assert props['title'] and props['progress']!='',props
    frame.locator('.e42-progress button[data-seek="1"]').click()
    frame.locator('html[data-e42-active="2"]').wait_for(timeout=10000)
    exported=page.evaluate("""()=>{
      const p=MotionStudioUnified.createProjectFromTemplate('editorial');
      MotionStudioUnified.load(p,{resetHistory:true});
      return MotionStudioUnified.build();
    }""")
    assert 'data-e42-editorial="coherent-print"' in exported
    assert exported.count('class="e42-image"')==4
    assert exported.count('class="e42-spread"')==4
    assert '<iframe' not in exported
    edited=page.evaluate("""()=>{
      const p=MotionStudioUnified.createProjectFromTemplate('editorial');
      p.sections[1].text='USER PRINT COPY';
      p.sections[1].image='data:image/png;base64,testing';
      MotionStudioUnified.load(p,{resetHistory:true});
      return MotionStudioUnified.build();
    }""")
    assert 'USER PRINT COPY' in edited
    assert 'data:image/png;base64,testing' in edited
    assert not errors,errors
    report['checks'].append({'viewport':[w,h],'scenes':scenes,'scrollChapters':4,'noIsolatedIframe':True,'previewExportParity':True})
    page.close()
   browser.close()
  report['status']='PASS'
 except Exception as exc:report['errors'].append(str(exc))
 finally:
  server.shutdown();server.server_close()
  REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+chr(10),encoding='utf-8')
  print(json.dumps(report,ensure_ascii=False,indent=2))
 assert report['status']=='PASS',report
if __name__=='__main__':run()
