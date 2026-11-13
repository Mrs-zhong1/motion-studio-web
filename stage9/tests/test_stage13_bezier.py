"""Stage13 in/out cubic Bezier handles are real Three.js raycast controls and survive JSON/export."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,traceback
R=Path(__file__).resolve().parents[1]
OUT=R/'STAGE13-BEZIER-RESULT.json'
res={'pass':False,'environment':'GitHub Actions Chromium SwiftShader software WebGL','macHardwareTested':False,'safariTested':False,'errors':[]}
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-webgl','--enable-unsafe-swiftshader'])
  page=b.new_page(viewport={'width':1440,'height':960},accept_downloads=True)
  page.on('pageerror',lambda e:res['errors'].append('editor '+str(e)))
  page.set_content((R/'Motion-Studio-Stage13-Bezier-OFFLINE.html').read_text(encoding='utf8'),wait_until='domcontentloaded')
  page.locator('#resumeProject').click()
  page.locator('#modeToggle').click()
  page.locator('[data-asset-tier-button="l3"]').click()
  for name in ['Sample-Dual-Material.glb','Sample-Textured-Animated.glb']:
   page.locator('.comp[data-id="offline-glb-scene"] button').click()
   page.locator('#stage9GlbInput').set_input_files(str(R.parent/name))
   page.wait_for_timeout(180)
  res['components']=page.evaluate('registry.length')
  uid=page.evaluate("project.sections.filter(s=>s.id==='offline-glb-scene'&&s.glb)[0].uid")
  page.evaluate('(id)=>selectSection(id)',uid)
  page.locator('#stage11Enable').click()
  page.locator('#stage12Toggle').click()
  frame=None
  for _ in range(45):
   for f in page.frames[1:]:
    try:
     if f.evaluate('window.__motionStage12Gizmo?.mode && window.__motionStage12Gizmo?.tangentHandleCount>=2'):frame=f;break
    except:pass
   if frame:break
   page.wait_for_timeout(150)
  assert frame,'Real Three.js tangent controls unavailable'
  page.locator('#stage10PreviewFrame').scroll_into_view_if_needed()
  page.wait_for_timeout(250)
  res['beforeGizmo']=frame.evaluate("({scene:window.__motionSharedThree.sceneUuid,tangents:window.__motionStage12Gizmo.tangentHandleCount,handles:window.__motionStage12Gizmo.handleCount,tangentScreen:window.__motionStage12Gizmo.tangentScreen,webgl:window.__motionSharedThree.webgl2})")
  rec=page.evaluate('(id)=>project.sections.find(s=>s.uid===id).cameraPath11',uid)
  res['beforePath']=rec
  # Grab actual 3D outgoing tangent of mid keyframe using projected screen coordinates.
  tangent=next(t for t in res['beforeGizmo']['tangentScreen'] if t['index']==1 and t['side']=='handleOut')
  fr=page.locator('#stage10PreviewFrame').bounding_box()
  px=fr['x']+tangent['x'];py=fr['y']+tangent['y']
  page.mouse.move(px,py);page.mouse.down();page.mouse.move(px+25,py,steps=7);page.mouse.up()
  page.wait_for_timeout(420)
  res['afterPath']=page.evaluate('(id)=>project.sections.find(s=>s.uid===id).cameraPath11',uid)
  res['tangentDrag']=frame.evaluate("({count:window.__motionStage12Gizmo.tangentDragCount,scene:window.__motionSharedThree.sceneUuid,canvas:document.querySelectorAll('#motion-shared-three-canvas').length})")
  # Incoming Y handle via numeric editor; must not overwrite independent outgoing X.
  page.locator('#stage11KeySelect').select_option('1')
  page.locator('[data-stage13-handle="handleIn"][data-axis="y"]').fill('1.6')
  page.locator('[data-stage13-handle="handleIn"][data-axis="y"]').dispatch_event('change')
  page.wait_for_timeout(260)
  res['edited']=page.evaluate('(id)=>project.sections.find(s=>s.uid===id).cameraPath11',uid)
  with page.expect_download() as dl:page.locator('#saveProject').click()
  project=R/'STAGE13-BEZIER-PROJECT.json';dl.value.save_as(project)
  page.locator('#openFile').set_input_files(str(project))
  page.wait_for_timeout(320)
  res['restored']=page.evaluate('(id)=>project.sections.find(s=>s.uid===id).cameraPath11',uid)
  with page.expect_download() as dl:page.locator('#exportPage').click()
  exported=R/'STAGE13-BEZIER-EXPORTED.html';dl.value.save_as(exported)
  res['exportBytes']=exported.stat().st_size
  view=b.new_page(viewport={'width':1180,'height':680})
  view.on('pageerror',lambda e:res['errors'].append('export '+str(e)))
  view.on('request',lambda r:res.setdefault('externalRequests',[]).append(r.url) if r.url.startswith(('http://','https://')) else None)
  view.set_content(exported.read_text(encoding='utf8'),wait_until='domcontentloaded')
  view.wait_for_function("window.__motionSharedThree?.loadedModels===2 || !!window.__motionSharedThree?.error",timeout=20000)
  anchors=view.evaluate('window.__motionSharedThreeControl.anchors()')
  result=[]
  for frac in [.25,.5,.75]:
   y=anchors[0]+(anchors[-1]-anchors[0])*frac
   view.evaluate('(v)=>window.scrollTo(0,Math.max(0,v-innerHeight*.5))',y)
   view.wait_for_timeout(100)
   result.append(view.evaluate('window.__motionSharedThreeControl.update()'))
  res['cameraSamples']=result
  res['exportScene']=view.evaluate("({webgl:window.__motionSharedThree.webgl2,models:window.__motionSharedThree.loadedModels,scene:window.__motionSharedThree.sceneUuid,error:window.__motionSharedThree.error,gizmo:window.__motionStage12Gizmo?.mode,canvas:document.querySelectorAll('#motion-shared-three-canvas').length})")
  view.screenshot(path=str(R/'STAGE13-BEZIER-CAPTURE.png'))
  h=res['edited'][1]
  res['pass']=(
   res['components']==20 and res['beforeGizmo']['webgl'] and res['beforeGizmo']['tangents']>=3
   and res['tangentDrag']['count']>0 and res['tangentDrag']['scene']==res['beforeGizmo']['scene']
   and h.get('handleOut',{}).get('x',0)>.65 and abs(h.get('handleIn',{}).get('y',0)-1.6)<.01
   and res['restored']==res['edited']
   and res['exportScene']['webgl'] and res['exportScene']['models']==2
   and res['exportScene']['canvas']==1 and res['exportScene']['gizmo'] is False
   and not res['exportScene']['error'] and not res['errors'] and not res.get('externalRequests')
  )
  view.close();page.close();b.close()
except Exception:
 res['errors'].append(traceback.format_exc(limit=5))
finally:
 OUT.write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(res,ensure_ascii=False,indent=2))
assert res['pass'],'Stage13 Bezier handle browser test failed'
