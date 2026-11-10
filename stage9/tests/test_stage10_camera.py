"""Stage10 editor camera UI, project roundtrip, shared scene camera parity in real browser."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json, traceback
ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'Motion-Studio-Stage9-THREE-OFFLINE.html'
OUT=ROOT/'STAGE10-CAMERA-RESULT.json'
res={'pass':False,'source':'Stage10 bundled editor GitHub Actions Chromium SwiftShader','hardwareGpuTested':False,'safariTested':False,'errors':[]}
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-webgl','--enable-unsafe-swiftshader'])
  page=browser.new_page(viewport={'width':1330,'height':900},accept_downloads=True)
  page.on('pageerror',lambda e:res['errors'].append('editor: '+str(e)+' | STACK: '+str(e.stack)))
  page.set_content(HTML.read_text(encoding='utf-8'),wait_until='domcontentloaded')
  res['componentCount']=page.evaluate('registry.length')
  for fixture in ['Sample-Dual-Material.glb','Sample-Textured-Animated.glb']:
   page.locator('.comp[data-id="offline-glb-scene"] button').click()
   page.locator('#stage9GlbInput').set_input_files(str(ROOT.parent/fixture))
   page.wait_for_timeout(150)
  res['glbCount']=page.evaluate("project.sections.filter(s=>s.id==='offline-glb-scene'&&s.glb).length")
  res['controlsVisible']=page.locator('#stage10CameraPanel [data-camera3d]').count()
  # Edit second GLB chapter; every property must persist in the section state.
  values={'x':1.5,'y':0.8,'z':7.2,'yaw':26,'pitch':-14,'roll':12,'fov':59}
  for key,value in values.items():
   page.locator('[data-camera3d="'+key+'"]').evaluate("(el,val)=>{el.value=String(val);el.dispatchEvent(new Event('input',{bubbles:true}));}",value)
  res['edited']=page.evaluate("project.sections.filter(s=>s.id==='offline-glb-scene')[1].camera3d")
  page.locator('#stage10CameraPreview').click()
  res['previewHasSharedMarkup']=page.locator('#stage10PreviewFrame').evaluate("el=>el.srcdoc.includes('motion-shared-scene-data') && el.srcdoc.includes('stage9SharedEngineURL')===false && el.srcdoc.includes('data:text/javascript;base64,')")
  page.wait_for_timeout(1100)
  previewStates=[]
  for frame in page.frames[1:]:
   try:
    state=frame.evaluate("window.__motionSharedThree ? {models:window.__motionSharedThree.loadedModels,webgl2:window.__motionSharedThree.webgl2,error:window.__motionSharedThree.error,canvasCount:document.querySelectorAll('#motion-shared-three-canvas').length,frames:window.__motionSharedThree.renderFrames} : null")
    if state:previewStates.append(state)
   except Exception as ex:res['errors'].append('preview frame inspect: '+str(ex))
  res['previewGpuStates']=previewStates
  res['previewGpuLoaded']=any(x.get('webgl2') and x.get('models')==2 and x.get('canvasCount')==1 and not x.get('error') for x in previewStates)
  # Camera data exported as standalone project JSON; reload it to prove persistence.
  with page.expect_download() as dl:page.locator('#saveProject').click()
  saved=ROOT/'STAGE10-CAMERA-PROJECT.json';dl.value.save_as(saved)
  res['jsonSaved']=saved.exists() and saved.stat().st_size>1000
  page.locator('#openFile').set_input_files(str(saved))
  page.wait_for_timeout(400)
  res['reloaded']=page.evaluate("project.sections.filter(s=>s.id==='offline-glb-scene')[1].camera3d")
  with page.expect_download() as dl:page.locator('#exportPage').click()
  exported=ROOT/'STAGE10-CAMERA-EXPORTED.html';dl.value.save_as(exported)
  res['exportBytes']=exported.stat().st_size
  exp=browser.new_page(viewport={'width':1180,'height':680})
  exp.on('pageerror',lambda e:res['errors'].append('export: '+str(e)+' | STACK: '+str(e.stack)))
  exp.set_content(exported.read_text(encoding='utf-8'),wait_until='domcontentloaded')
  exp.wait_for_function("window.__motionSharedThree?.loadedModels===2 || !!window.__motionSharedThree?.error",timeout=20000)
  res['sharedStart']=exp.evaluate("({cameraKeys:window.__motionSharedThree.cameraKeyframes,sceneId:window.__motionSharedThree.sceneUuid,loadedModels:window.__motionSharedThree.loadedModels,context:window.__motionSharedThree.webgl2,error:window.__motionSharedThree.error,canvasCount:document.querySelectorAll('#motion-shared-three-canvas').length})")
  anchors=exp.evaluate('window.__motionSharedThreeControl.anchors()')
  samples=[]
  for frac in [0,.25,.5,.75,1]:
   midpoint=anchors[0]+(anchors[-1]-anchors[0])*frac
   exp.evaluate('(y)=>window.scrollTo(0,Math.max(0,y-innerHeight*.5))',midpoint)
   exp.wait_for_timeout(110)
   samples.append(exp.evaluate('window.__motionSharedThreeControl.update()'))
  res['cameraSamples']=samples
  res['sharedEnd']=exp.evaluate("({sceneId:window.__motionSharedThree.sceneUuid,frames:window.__motionSharedThree.renderFrames,pixels:window.__motionSharedThree.visiblePixels,contextLost:window.__motionSharedThree.contextLost,error:window.__motionSharedThree.error})")
  exp.screenshot(path=str(ROOT/'STAGE10-CAMERA-CAPTURE.png'))
  # Only compare edit and roundtrip to requested values and camera optics.
  keys=res['sharedStart']['cameraKeys']
  r0,rn=samples[0],samples[-1]
  res['pass']=(
   res['componentCount']==20 and res['glbCount']==2 and res['controlsVisible']==7
   and all(abs(res['edited'][k]-value)<.001 for k,value in values.items())
   and all(abs(res['reloaded'][k]-value)<.001 for k,value in values.items())
   and res['jsonSaved'] and res['previewHasSharedMarkup'] and res['previewGpuLoaded']
   and len(keys)==2 and all(abs(keys[1][k]-value)<.001 for k,value in values.items())
   and res['sharedStart']['canvasCount']==1 and res['sharedStart']['context'] and res['sharedStart']['loadedModels']==2
   and res['sharedStart']['sceneId']==res['sharedEnd']['sceneId']
   and rn['x']>r0['x']+2.5 and rn['y']>r0['y']+.3 and rn['fov']>r0['fov']+8
   and rn['yaw']>r0['yaw']+6 and rn['pitch']<r0['pitch']-3
   and res['sharedEnd']['frames']>=5 and res['sharedEnd']['pixels']>0
   and not res['sharedEnd']['contextLost'] and not res['sharedEnd']['error'] and not res['errors']
  )
  exp.close();page.close();browser.close()
except Exception:
 res['errors'].append(traceback.format_exc(limit=5))
finally:
 OUT.write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(res,ensure_ascii=False,indent=2))
assert res['pass'],'Stage10 camera editor-to-export parity failed'
