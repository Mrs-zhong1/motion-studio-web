"""Stage12 real Three.js spatial viewport, axis-constrained gizmo, tension and JSON/export tests."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,traceback
R=Path(__file__).resolve().parents[1]
HTML=R/'Motion-Studio-Stage12-Spatial-Gizmo-OFFLINE.html'
OUT=R/'STAGE12-GIZMO-RESULT.json'
res={'pass':False,'stage':'12','environment':'GitHub Actions Ubuntu Chromium SwiftShader software WebGL','macHardwareTested':False,'safariTested':False,'errors':[]}
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-webgl','--enable-unsafe-swiftshader'])
  ed=browser.new_page(viewport={'width':1440,'height':960},accept_downloads=True)
  ed.on('pageerror',lambda e:res['errors'].append('editor: '+str(e)+' | '+str(e.stack)))
  ed.set_content(HTML.read_text(encoding='utf8'),wait_until='domcontentloaded')
  ed.locator('#resumeProject').click()
  ed.locator('#modeToggle').click()
  ed.locator('[data-asset-tier-button="l3"]').click()
  res['components']=ed.evaluate('registry.length')
  for fixture in ['Sample-Dual-Material.glb','Sample-Textured-Animated.glb']:
   ed.locator('.comp[data-id="offline-glb-scene"] button').click()
   ed.locator('#stage9GlbInput').set_input_files(str(R.parent/fixture))
   ed.wait_for_timeout(200)
  uid=ed.evaluate("project.sections.filter(s=>s.id==='offline-glb-scene'&&s.glb)[0].uid")
  ed.evaluate('(uid)=>selectSection(uid)',uid)
  res['stage12Panel']=ed.locator('#stage12ViewportControls').count()==1
  ed.locator('#stage11Enable').click()
  res['initialKeyframes']=ed.evaluate('(uid)=>project.sections.find(s=>s.uid===uid).cameraPath11.length',uid)
  ed.locator('#stage12Toggle').click()
  ed.wait_for_timeout(1200)
  frame=None
  for _ in range(50):
   for f in ed.frames[1:]:
    try:
     if f.evaluate('!!window.__motionStage12Gizmo?.mode && window.__motionSharedThree?.loadedModels===2'):
      frame=f;break
    except Exception: pass
   if frame:break
   ed.wait_for_timeout(160)
  assert frame,'Stage12 preview did not activate an actual shared WebGL Three.js gizmo'
  res['initialGizmo']=frame.evaluate("({state:window.__motionStage12Gizmo,sceneUuid:window.__motionSharedThree.sceneUuid,webgl2:window.__motionSharedThree.webgl2,models:window.__motionSharedThree.loadedModels,canvasCount:document.querySelectorAll('#motion-shared-three-canvas').length})")
  ed.locator('#stage10PreviewFrame').scroll_into_view_if_needed()
  ed.wait_for_timeout(300)
  # Get actual projected 3D sphere screen position and drag by browser mouse.
  handle=frame.evaluate('window.__motionStage12Gizmo.handleScreen[1]')
  frameRect=ed.locator('#stage10PreviewFrame').bounding_box()
  assert handle and frameRect,'Gizmo handle projection or viewport unavailable'
  res['handleProjection']=handle
  res['frameRect']=frameRect
  before=ed.evaluate("(uid)=>({...project.sections.find(s=>s.uid===uid).cameraPath11[1]})",uid)
  x=frameRect['x']+handle['x'];y=frameRect['y']+handle['y']
  ed.mouse.move(x,y);ed.mouse.down();ed.mouse.move(x+24,y,steps=7);ed.mouse.up()
  ed.wait_for_timeout(500)
  after=ed.evaluate("(uid)=>({...project.sections.find(s=>s.uid===uid).cameraPath11[1]})",uid)
  res['dragBefore']={'x':before['x'],'y':before['y'],'z':before['z']}
  res['dragAfter']={'x':after['x'],'y':after['y'],'z':after['z']}
  res['axisConstrainedX']=after['x']>before['x']+.15 and abs(after['y']-before['y'])<.001 and abs(after['z']-before['z'])<.001
  res['gizmoAfterDrag']=frame.evaluate('window.__motionStage12Gizmo')
  # Exercise a second axis and camera view, using real UI buttons.
  ed.locator('#stage12AxisY').click()
  ed.locator('#stage12ViewTop').click()
  ed.wait_for_timeout(350)
  res['axisView']=frame.evaluate("({axis:window.__motionStage12Gizmo.axis,view:window.__motionStage12Gizmo.view,scene:window.__motionStage12Gizmo.sceneId,handles:window.__motionStage12Gizmo.handleCount})")
  # Increase manual cubic tangent tension and ensure the project keeps it.
  ed.locator('#stage11KeySelect').select_option('1')
  ed.locator('#stage12Tension').evaluate("(el)=>{el.value='0.75';el.dispatchEvent(new Event('input',{bubbles:true}));}")
  res['tensionAfterEdit']=ed.evaluate('(uid)=>project.sections.find(s=>s.uid===uid).cameraPath11[1].tension',uid)
  res['previewAfterUpdates']=frame.evaluate("({mode:window.__motionStage12Gizmo.mode,patches:window.__motionSharedThree.stage11PatchCount,dragCount:window.__motionStage12Gizmo.dragCount,sceneId:window.__motionSharedThree.sceneUuid,canvas:document.querySelectorAll('#motion-shared-three-canvas').length})")
  ed.screenshot(path=str(R/'STAGE12-GIZMO-CAPTURE.png'))
  with ed.expect_download() as d:ed.locator('#saveProject').click()
  projectPath=R/'STAGE12-GIZMO-PROJECT.json';d.value.save_as(projectPath)
  ed.locator('#openFile').set_input_files(str(projectPath))
  ed.wait_for_timeout(450)
  res['reloaded']=ed.evaluate('(uid)=>project.sections.find(s=>s.uid===uid).cameraPath11',uid)
  with ed.expect_download() as d:ed.locator('#exportPage').click()
  exported=R/'STAGE12-GIZMO-EXPORTED.html';d.value.save_as(exported)
  res['exportBytes']=exported.stat().st_size
  view=browser.new_page(viewport={'width':1180,'height':680})
  view.on('pageerror',lambda e:res['errors'].append('export: '+str(e)+' | '+str(e.stack)))
  view.on('request',lambda request:res.setdefault('remoteRequests',[]).append(request.url) if request.url.startswith(('http:','https:')) else None)
  view.set_content(exported.read_text(encoding='utf8'),wait_until='domcontentloaded')
  view.wait_for_function('window.__motionSharedThree?.loadedModels===2 || Boolean(window.__motionSharedThree?.error)',timeout=20000)
  res['exportScene']=view.evaluate("({sceneId:window.__motionSharedThree.sceneUuid,models:window.__motionSharedThree.loadedModels,webgl2:window.__motionSharedThree.webgl2,canvasCount:document.querySelectorAll('#motion-shared-three-canvas').length,stage12Mode:window.__motionStage12Gizmo?.mode,stage12Handles:window.__motionStage12Gizmo?.handleCount,stage11Paths:window.__motionSharedThree.stage11PathCounts,error:window.__motionSharedThree.error})")
  view.close()
  res['pass']=(
   res['components']==20 and res['stage12Panel'] and res['initialKeyframes']==3
   and res['initialGizmo']['webgl2'] and res['initialGizmo']['models']==2 and res['initialGizmo']['canvasCount']==1
   and res['initialGizmo']['state']['handleCount']==3 and res['initialGizmo']['state']['axisArrowsCount']==3 and res['initialGizmo']['state']['trajectoryPoints']>=20
   and res['axisConstrainedX'] and res['gizmoAfterDrag']['dragCount']>=1
   and res['axisView']['axis']=='y' and res['axisView']['view']=='top'
   and res['previewAfterUpdates']['sceneId']==res['initialGizmo']['sceneUuid']
   and res['previewAfterUpdates']['canvas']==1 and res['previewAfterUpdates']['patches']>=1
   and abs(res['tensionAfterEdit']-.75)<.001
   and len(res['reloaded'])==3 and abs(res['reloaded'][1]['tension']-.75)<.001
   and res['exportScene']['webgl2'] and res['exportScene']['models']==2
   and res['exportScene']['canvasCount']==1 and not res['exportScene']['stage12Mode']
   and res['exportScene']['stage11Paths'][0]==3
   and not res['exportScene']['error'] and not res['errors'] and not res.get('remoteRequests')
  )
  ed.close();browser.close()
except Exception:
 res['errors'].append(traceback.format_exc(limit=7))
finally:
 OUT.write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(res,ensure_ascii=False,indent=2))
assert res['pass'],'Stage12 spatial Three.js gizmo and offline project/export gate failed'
