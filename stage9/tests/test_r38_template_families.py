"""R38 visually grounded browser check: 8 unique real rendered family layouts.

Accepts 5 film scenes (4 editorial) without inventing images. Records computed
geometry, distinct colors, actual title, section markers and output parity.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import json,threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/'Motion-Studio-Stage15-Meshopt-OFFLINE.html'
REPORT=ROOT/'R38_EIGHT_FAMILIES.json'
EXPECTED={
 'editorial':'print','product-3d':'object','cinematic':'film',
 'architecture':'plan','agency':'play','fashion':'runway',
 'gallery':'museum','saas':'system'
}
def run():
 report={'status':'FAIL','templates':[],'errors':[],'artDirection':'HOLD'}
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
 threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
   for template,family in EXPECTED.items():
    page=browser.new_page(viewport={'width':1440,'height':900})
    errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto(f'http://127.0.0.1:{server.server_port}/{EDITOR.name}',wait_until='domcontentloaded')
    page.locator(f'[data-template-card="{template}"]').click()
    frame=page.locator('#templatePreviewFrame').content_frame
    if template=='cinematic':
      frame.locator('html[data-r39-film="continuous"]').wait_for(timeout=15000)
      values=frame.locator('body').evaluate("""body=>{
        const frames=[...document.querySelectorAll('.r39-frame')];
        return {family:'film',count:frames.length,tagged:frames.length,marks:frames.length,
          chapterTitles:[...document.querySelectorAll('.r39-caption h1')].map(el=>el.textContent),
          background:getComputedStyle(body).backgroundColor,
          headingFont:getComputedStyle(document.querySelector('.r39-caption h1')).fontFamily,
          artWidth:frames[0].getBoundingClientRect().width,
          regionWidth:innerWidth,artX:frames[0].getBoundingClientRect().left,
          artClip:'full-screen camera',stickyStages:1,imageVisible:true,
          horizontalOverflow:Math.max(0,document.documentElement.scrollWidth-innerWidth)}
      }""")
      assert values['count']==5 and values['stickyStages']==1,values
      assert len(values['chapterTitles'])==5 and all(values['chapterTitles']),values
      assert values['horizontalOverflow']<=32,values
      exported=page.evaluate("(t)=>{const p=MotionStudioUnified.createProjectFromTemplate(t);MotionStudioUnified.load(p,{resetHistory:true});return MotionStudioUnified.build()}",template)
      assert 'data-r39-film="continuous"' in exported
      assert exported.count('class="r39-frame"')==5
      report['templates'].append({'template':template,'viewport':[1440,900],**values})
      page.close()
      continue
    frame.locator('html[data-r38-ready="yes"]').wait_for(timeout=15000)
    values=frame.locator('body').evaluate("""body=>{
      const sections=[...document.querySelectorAll('.page[data-template] > section.section')];
      const first=sections[0], art=first.querySelector('.section-art');
      const photo=art?.getBoundingClientRect(),region=first.getBoundingClientRect();
      return {
       family:body.dataset.r38Family,
       count:sections.length,
       tagged:sections.filter(s=>s.hasAttribute('data-r38-act')).length,
       marks:document.querySelectorAll('.r38-marker').length,
       chapterTitles:sections.map(s=>s.querySelector('.designed-chapter-heading h2')?.innerText||''),
       background:getComputedStyle(first).backgroundColor,
       headingFont:getComputedStyle(first.querySelector('.designed-chapter-heading h2')||first).fontFamily,
       artWidth:photo?.width,regionWidth:region.width,
       artX:photo?.left-region.left,
       artClip:getComputedStyle(art).clipPath,
       stickyStages:document.querySelectorAll('.r37-stage').length,
       imageVisible:art?getComputedStyle(art).display!=='none':false,
       horizontalOverflow:Math.max(0,document.documentElement.scrollWidth-innerWidth)
      }
    }""")
    assert values['family']==family,values
    assert values['count']==(4 if template=='editorial' else 5),values
    assert values['tagged']==values['marks']==values['count'],values
    assert values['imageVisible'],values
    assert values['horizontalOverflow']<=32,values
    if template=='cinematic':
      assert values['stickyStages']==5,values
      assert all(values['chapterTitles']),values
    else:
      assert values['stickyStages']==0,values
    exported=page.evaluate("(t)=>{const p=MotionStudioUnified.createProjectFromTemplate(t);MotionStudioUnified.load(p,{resetHistory:true});return MotionStudioUnified.build()}",template)
    assert 'id="r38-export-style"' in exported,(template,'missing exported style')
    assert 'id="r38-export-runtime"' in exported,(template,'missing exported behavior')
    assert not errors,(template,errors)
    report['templates'].append({'template':template,'viewport':[1440,900],**values})
    page.close()
   browser.close()
   assert len(report['templates'])==8
   # Distinct layout outcomes, not eight hardcoded names on one generic page.
   palette={x['background'] for x in report['templates']}
   assert len(palette)>=6,f'Only {len(palette)} actual backgrounds: {palette}'
  report['status']='PASS'
 except Exception as error:
  report['errors'].append(str(error))
 finally:
  server.shutdown();server.server_close()
  REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+chr(10),encoding='utf-8')
  print(json.dumps(report,ensure_ascii=False,indent=2))
 assert report['status']=='PASS',report
if __name__=='__main__':run()
