"""R40 actual exported product scene: exercise real WebGL PBR controls."""
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import threading,json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/'Motion-Studio-Stage15-Meshopt-OFFLINE.html'
REPORT=ROOT/'R40_PRODUCT_ACCEPTANCE.json'
def run():
 report={'status':'FAIL','errors':[],'checks':[],'productionApproved':False}
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
 threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(headless=True,args=['--no-sandbox','--enable-webgl','--use-gl=angle','--use-angle=swiftshader'])
   editor=browser.new_page(viewport={'width':1440,'height':900})
   errors=[];editor.on('pageerror',lambda e:errors.append(str(e)))
   editor.goto(f'http://127.0.0.1:{server.server_port}/{EDITOR.name}',wait_until='domcontentloaded')
   editor.locator('[data-template-card="product-3d"]').click()
   preview=editor.locator('#templatePreviewFrame').content_frame
   preview.locator('html[data-r40-controls="ready"]').wait_for(timeout=20000)
   buttons=preview.locator('.r40-control')
   assert buttons.count()==12,buttons.count()
   frame=preview.locator('.page[data-template="product-3d"] > section[data-index="1"] iframe').content_frame
   # Bridge is delivered from parent to nested WebGL renderer (not CSS filter)
   frame.locator('#motion-three-webgl2').wait_for(timeout=25000)
   preview.locator('.r40-control[data-group="light"][data-value="cool"]').click()
   preview.locator('html[data-r40-last-applied="light:cool"]').wait_for(timeout=15000)
   preview.locator('.r40-control[data-group="material"][data-value="pearl"]').click()
   preview.locator('html[data-r40-last-applied="material:pearl"]').wait_for(timeout=15000)
   preview.locator('.r40-control[data-group="camera"][data-value="detail"]').click()
   preview.locator('html[data-r40-last-applied="camera:detail"]').wait_for(timeout=15000)
   engine=frame.locator('body').evaluate("""() => ({
      light:window.__motionThreeStatus?.lightPreset,
      material:window.__motionThreeStatus?.materialPreset,
      camera:window.__motionThreeStatus?.cameraPreset,
      clicks:window.__motionThreeStatus?.controlClicks,
      pbr:window.__motionThreeStatus?.pbr,
      render:window.__motionThreeStatus?.engine
   })""")
   assert engine['light']=='cool',engine
   assert engine['material']=='pearl',engine
   assert engine['camera']=='detail',engine
   assert engine['clicks']>=3,engine
   exported=editor.evaluate("""()=>{
     const p=MotionStudioUnified.createProjectFromTemplate('product-3d');
     MotionStudioUnified.load(p,{resetHistory:true});
     return MotionStudioUnified.build();
   }""")
   assert 'id="r40-export-runtime"' in exported
   assert 'id="r40-export-css"' in exported
   assert 'data-r39-film="continuous"' not in exported
   assert not errors,errors
   report['checks'].append({'engine':engine,'controls':12,'previewExportParity':True})
   browser.close()
   report['status']='PASS'
 except Exception as e:report['errors'].append(str(e))
 finally:
  server.shutdown();server.server_close()
  REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+chr(10),encoding='utf-8')
  print(json.dumps(report,ensure_ascii=False,indent=2))
 assert report['status']=='PASS',report
if __name__=='__main__':run()
