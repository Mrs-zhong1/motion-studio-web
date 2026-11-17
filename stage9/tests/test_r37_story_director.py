"""R37 real narrative-direction test: real single stage and scroll hold.

Unlike token/style tests, this checks actual computed layouts, hidden nested
micro-demo, sticky viewport hold, one visible title, nav and export. 100% review-
only: original collage images remain a release HOLD.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import json,threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/'Motion-Studio-Stage15-Meshopt-OFFLINE.html'
RESULT=ROOT/'R37_STORY_DIRECTOR_RESULT.json'
def run():
 report={'status':'FAIL','artDirection':'HOLD','tests':[],'errors':[]}
 srv=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
 threading.Thread(target=srv.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
   for width,height in [(1440,900),(390,844)]:
    page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
    errors=[];page.on('pageerror',lambda exc:errors.append(str(exc)))
    page.goto(f'http://127.0.0.1:{srv.server_port}/{EDITOR.name}',wait_until='domcontentloaded')
    page.locator('[data-template-card="cinematic"]').click()
    frame=page.locator('#templatePreviewFrame').content_frame
    frame.locator('.r37-stage').first.wait_for()
    count=frame.locator('.r37-stage').count()
    assert count==5,('R37 stages',count)
    frame.locator('html[data-r37-director="single-stage"]').wait_for()
    sec=frame.locator('.page[data-template="cinematic"] > section.section.r37-scene').nth(2)
    values=sec.evaluate("""s=>{
     const stage=s.querySelector('.r37-stage'),heading=stage.querySelector('.designed-chapter-heading');
     const art=stage.querySelector('.section-art'),iframe=stage.querySelector('iframe');
     return {stagePosition:getComputedStyle(stage).position,
       sectionHeight:s.getBoundingClientRect().height,viewport:innerHeight,
       iframeDisplay:getComputedStyle(iframe).display,
       badgeDisplay:getComputedStyle(stage.querySelector('.badge')).display,
       headingCount:stage.querySelectorAll('[data-chapter-title]').length,
       artWidth:art.getBoundingClientRect().width,
       viewportWidth:innerWidth,navWidth:document.querySelector('.r14-story-rail').getBoundingClientRect().width,
       labelDisplay:getComputedStyle(document.querySelector('.r36-nav-caption')).display}
    }""")
    assert values['stagePosition']=='sticky',values
    assert values['sectionHeight']>=values['viewport']*1.45,values
    assert values['iframeDisplay']=='none',values
    assert values['badgeDisplay']=='none',values
    assert values['headingCount']==1,values
    assert values['artWidth']>values['viewportWidth']*.90,values
    assert values['navWidth']<=60,values
    assert values['labelDisplay']=='none',values
    # A sticky stage must hold the same viewport position when scroll changes
    # within its long scene. Measure position after jumping into its corridor.
    measurements=sec.evaluate("""async s=>{
      // The exported page enables html{scroll-behavior:smooth}. Force
      // deterministic scroll measurements, not a 170ms partial tween.
      document.documentElement.style.setProperty('scroll-behavior','auto','important');
      const y=s.getBoundingClientRect().top+window.scrollY;
      window.scrollTo(0,y+100);
      await new Promise(r=>setTimeout(r,170));
      const a=s.querySelector('.r37-stage').getBoundingClientRect().top;
      window.scrollTo(0,y+Math.min(innerHeight*.5,360));
      await new Promise(r=>setTimeout(r,170));
      const b=s.querySelector('.r37-stage').getBoundingClientRect().top;
      return {topAt100:a,topAt360:b,progress:s.dataset.r16Progress,\n       scroller:document.scrollingElement?.tagName,scrollY:window.scrollY,\n       scrollHeight:document.scrollingElement?.scrollHeight,clientHeight:document.scrollingElement?.clientHeight,\n       parentOverflows:Array.from((function*(el){while(el&&el!==document.documentElement){yield el;el=el.parentElement}})(s)).map(e=>[e.className,getComputedStyle(e).overflowY,getComputedStyle(e).position])}
    }""")
    assert abs(measurements['topAt100']-measurements['topAt360'])<5,measurements
    # Native R16 still calculates camera progress, no extra independent clock.
    assert measurements['progress'] is not None,measurements
    assert not errors,errors
    report['tests'].append({'viewport':[width,height],**values,**measurements,'errors':errors})
    page.close()
   browser.close()
  report['status']='PASS'
 except Exception as exc:
  report['errors'].append(str(exc))
 finally:
  srv.shutdown();srv.server_close()
  RESULT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+chr(10),encoding='utf-8')
  print(json.dumps(report,ensure_ascii=False,indent=2))
 assert report['status']=='PASS',report
if __name__=='__main__':run()
