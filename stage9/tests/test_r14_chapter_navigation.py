"""R14 navigator regression migrated for R39 film vs unchanged six families.

The film's chapter drawer and one-stage scrubber are intentional; the
Editorial/other family still exposes the legacy R14 chapter rail.
"""
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/'Motion-Studio-Stage15-Meshopt-OFFLINE.html'
def test_r14():
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
 threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
   editor=browser.new_page(viewport={'width':1440,'height':900})
   editor.goto(f'http://127.0.0.1:{server.server_port}/{EDITOR.name}',wait_until='domcontentloaded')
   assert editor.locator('#discoveryView').is_visible()
   for name in ('editorial','product-3d','cinematic','architecture','agency','fashion','gallery','saas'):
    html=editor.evaluate("(id)=>buildTemplatePreviewDocument(id)",name)
    page=browser.new_page(viewport={'width':1440,'height':900})
    page.set_content(html,wait_until='domcontentloaded')
    if name=='editorial':
     assert page.locator('html[data-e42-editorial="coherent-print"]').count()==1
     assert page.locator('.e42-spread').count()==4
     assert page.locator('.r14-story-rail').count()==0
     assert page.locator('.e42-progress button').count()==4
     page.locator('.e42-progress button[data-seek="3"]').click()
     page.locator('html[data-e42-active="4"]').wait_for(timeout=10000)
    elif name=='cinematic':
     assert page.locator('html[data-r39-film="continuous"]').count()==1
     assert page.locator('.r39-frame').count()==5
     assert page.locator('.r14-story-rail').count()==0
     btn=page.locator('#r39-menu-toggle')
     btn.click()
     assert btn.get_attribute('aria-expanded')=='true'
     page.locator('#r39-chapter-menu [data-seek="4"]').click()
     page.locator('html[data-r39-chapter="5"]').wait_for(timeout=10000)
     assert btn.get_attribute('aria-expanded')=='false'
     page.set_viewport_size({'width':390,'height':844})
     assert btn.is_visible()
    else:
     nav=page.locator('nav.r14-story-rail')
     nav.wait_for()
     assert nav.locator('.r14-rail-chapters > button').count()==page.locator('section.section').count(),name
     assert nav.locator('button[aria-current="step"]').count()==1,name
     assert nav.locator('.r14-rail-fill').count()==1,name
    page.close()
   browser.close()
 finally:server.shutdown();server.server_close()
if __name__=='__main__':
 test_r14();print('R14→R39 PASS: five-act film drawer and distinct legacy gallery chapter navigators')
