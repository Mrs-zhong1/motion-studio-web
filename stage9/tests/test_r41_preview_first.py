"""R41 production-shell browser contract: every template previews full-screen by
default; opening metadata must NOT shrink the artwork. Runs real Chromium.
"""
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import threading,json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/'Motion-Studio-Stage15-Meshopt-OFFLINE.html'
REPORT=ROOT/'R41_PREVIEW_FIRST_ACCEPTANCE.json'
TEMPLATES=['editorial','product-3d','cinematic','architecture','agency','fashion','gallery','saas']
def run():
 results={'status':'FAIL','templates':[],'errors':[],'releaseApproved':False}
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
 threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
   for name in TEMPLATES:
    page=browser.new_page(viewport={'width':1440,'height':900})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(f'http://127.0.0.1:{server.server_port}/{EDITOR.name}',wait_until='domcontentloaded')
    page.locator(f'[data-template-card="{name}"]').click()
    page.locator('#templatePreviewFrame').content_frame.locator('body').wait_for()
    assert page.locator('.preview-product-info').is_hidden(),name
    metrics=page.locator('#previewDevice').evaluate("""e=>({
      w:e.getBoundingClientRect().width,
      h:e.getBoundingClientRect().height,
      host:innerWidth,
      css:getComputedStyle(document.querySelector('.preview-product-layout')).gridTemplateColumns,
      iframe:e.querySelector('iframe').getBoundingClientRect().width
    })""")
    assert metrics['w']>=metrics['host']*.96,(name,metrics)
    assert abs(metrics['iframe']-metrics['w'])<4,(name,metrics)
    info=page.locator('#previewImmersive')
    assert info.inner_text()=='模板信息'
    info.click()
    assert page.locator('.preview-product-info').is_visible()
    assert info.get_attribute('aria-expanded')=='true'
    new_width=page.locator('#previewDevice').evaluate('e=>e.getBoundingClientRect().width')
    assert abs(new_width-metrics['w'])<4,(name,'drawer shifted canvas',new_width,metrics)
    page.keyboard.press('Escape')
    assert page.locator('.preview-product-info').is_hidden()
    assert page.locator('#templatePreview').is_visible()
    page.locator('#previewMobile').click()
    assert page.locator('#previewDevice').evaluate("el=>el.classList.contains('mobile')")
    page.locator('#previewDesktop').click()
    assert page.locator('#previewDevice').evaluate("el=>!el.classList.contains('mobile')")
    page.locator('#previewClose').click()
    assert page.locator('#templatePreview').is_hidden()
    assert not errors,(name,errors)
    results['templates'].append({'name':name,'viewport':1440,'stage':metrics['w'],'grid':metrics['css'],'drawerDoesNotResize':True})
    page.close()
   browser.close()
  results['status']='PASS'
 except Exception as e:results['errors'].append(str(e))
 finally:
  server.shutdown();server.server_close()
  REPORT.write_text(json.dumps(results,ensure_ascii=False,indent=2)+chr(10),encoding='utf-8')
  print(json.dumps(results,ensure_ascii=False,indent=2))
 assert results['status']=='PASS',results
if __name__=='__main__':run()
