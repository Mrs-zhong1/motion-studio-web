"""Stage11 true WebGL timeline GUI/drag/JSON/live patch/export regression.
Cloud Chromium SwiftShader only, never a Mac hardware/Safari assertion.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,traceback
R=Path(__file__).resolve().parents[1]
HTML=R/'Motion-Studio-Stage11-Timeline-OFFLINE.html'
OUT=R/'STAGE11-TIMELINE-RESULT.json'
result={'pass':False,'stage':'11','webglEnvironment':'Ubuntu Chromium SwiftShader software WebGL','macHardwareTested':False,'safariTested':False,'errors':[]}
try:
 with sync_playwright() as p:
  b=p.chromium.launch(headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-webgl','--enable-unsafe-swiftshader'])
  editor=b.new_page(viewport={'width':1380,'height':950},accept_downloads=True)
  editor.on('pageerror',lambda e:result['errors'].append('editor: '+str(e)+'\n'+str(e.stack)))
  editor.set_content(HTML.read_text(encoding='utf8'),wait_until='domcontentloaded')
  result['componentCount']=editor.evaluate('registry.length')
  for fixture in ['Sample-Dual-Material.glb','Sample-Textured-Animated.glb']:
   editor.locator('.comp[data-id="offline-glb-scene"] button').click()
   editor.locator('#stage9GlbInput').set_input_files(str(R.parent/fixture))
   editor.wait_for_timeout(200)
  result['glbChapters']=editor.evaluate("project.sections.filter(x=>x.id==='offline-glb-scene'&&x.glb).length")
  # Activate first GLB to edit transition into the second GLB.
  uid=editor.evaluate("project.sections.filter(x=>x.id==='offline-glb-scene'&&x.glb)[0].uid")
  editor.evaluate("(uid)=>selectSection(uid)",uid)
  result['panelVisible']=editor.locator('#stage11CameraPanel').count()==1
  editor.locator('#stage11Enable').click()
  result['initialPoints']=editor.evaluate("(uid)=>project.sections.find(s=>s.uid===uid).cameraPath11.length",uid)
  editor.locator('#stage11Add').click()
  result['afterAdd']=editor.evaluate("(uid)=>project.sections.find(s=>s.uid===uid).cameraPath11.length",uid)
  editor.locator('#stage11Delete').click()
  result['afterDelete']=editor.evaluate("(uid)=>project.sections.find(s=>s.uid===uid).cameraPath11.length",uid)
  # Verify dragging the middle keypoint changes time or horizontal path coordinate.
  old=editor.evaluate("(uid)=>({...project.sections.find(s=>s.uid===uid).cameraPath11[1]})",uid)
  c=editor.locator('#stage11Track circle[data-keypoint="1"]')
  rect=c.bounding_box()
  assert rect,"Stage11 SVG point is missing"
  editor.mouse.move(rect['x']+rect['width']/2,rect['y']+rect['height']/2)
  editor.mouse.down()
  editor.mouse.move(rect['x']+rect['width']/2+25,rect['y']+rect['height']/2-14,steps=6)
  editor.mouse.up()
  moved=editor.evaluate("(uid)=>({...project.sections.find(s=>s.uid===uid).cameraPath11[1]})",uid)
  result['dragModified']=abs(moved['at']-old['at'])>.1 or abs(moved['x']-old['x'])>.05
  result['dragBefore']={'at':old['at'],'x':old['x']}
  result['dragAfter']={'at':moved['at'],'x':moved['x']}
  # Select middle frame and give it a distinct intentional camera shape.
  editor.locator('#stage11KeySelect').select_option('1')
  editor.locator('#stage11Time').evaluate("(el)=>{el.value='50';el.dispatchEvent(new Event('input',{bubbles:true}));}")
  camera={'x':3.2,'y':1.4,'z':7.3,'yaw':28,'pitch':-12,'roll':7,'fov':68}
  for key,val in camera.items():
   editor.locator(f'[data-stage11-param="{key}"]').evaluate("(el,value)=>{el.value=String(value);el.dispatchEvent(new Event('input',{bubbles:true}));}",val)
  # Open iframe preview after edits, then do another modification to prove live patches.
  editor.locator('#stage10CameraPreview').click()
  editor.wait_for_timeout(1800)
  preview=None
  for frame in editor.frames[1:]:
   try:
    if frame.evaluate('Boolean(window.__motionSharedThree?.loadedModels===2)'):preview=frame;break
   except:pass
  assert preview,'Editor iframe never loaded shared Three.js preview'
  before=preview.evaluate("({uuid:window.__motionSharedThree.sceneUuid,count:window.__motionSharedThree.stage11PatchCount,paths:window.__motionSharedThree.stage11PathCounts,models:window.__motionSharedThree.loadedModels,webgl:window.__motionSharedThree.webgl2,canvas:document.querySelectorAll('#motion-shared-three-canvas').length})")
  result['previewBefore']=before
  editor.locator('[data-stage11-param="x"]').evaluate("(el)=>{el.value='3.5';el.dispatchEvent(new Event('input',{bubbles:true}));}")
  editor.wait_for_timeout(500)
  after=preview.evaluate("({uuid:window.__motionSharedThree.sceneUuid,count:window.__motionSharedThree.stage11PatchCount,paths:window.__motionSharedThree.stage11PathCounts,models:window.__motionSharedThree.loadedModels,webgl:window.__motionSharedThree.webgl2,canvas:document.querySelectorAll('#motion-shared-three-canvas').length})")
  result['previewAfter']=after
  result['livePatched']=after['count']>before['count'] and before['uuid']==after['uuid'] and after['models']==2 and after['canvas']==1
  result['editedPath']=editor.evaluate("(uid)=>project.sections.find(s=>s.uid===uid).cameraPath11",uid)
  # Roundtrip through native project save/import.
  with editor.expect_download() as dl:editor.locator('#saveProject').click()
  saved=R/'STAGE11-TIMELINE-PROJECT.json';dl.value.save_as(saved)
  editor.locator('#openFile').set_input_files(str(saved))
  editor.wait_for_timeout(450)
  result['reloadedPath']=editor.evaluate("(uid)=>project.sections.find(s=>s.uid===uid).cameraPath11",uid)
  with editor.expect_download() as dl:editor.locator('#exportPage').click()
  exported=R/'STAGE11-TIMELINE-EXPORTED.html';dl.value.save_as(exported)
  result['exportBytes']=exported.stat().st_size
  view=b.new_page(viewport={'width':1180,'height':680})
  view.on('pageerror',lambda e:result['errors'].append('export: '+str(e)+'\n'+str(e.stack)))
  view.on('request',lambda r:result.setdefault('remoteRequests',[]).append(r.url) if r.url.startswith(('https://','http://')) else None)
  view.set_content(exported.read_text(encoding='utf8'),wait_until='domcontentloaded')
  view.wait_for_function('window.__motionSharedThree?.loadedModels===2 || Boolean(window.__motionSharedThree?.error)',timeout=20000)
  anchors=view.evaluate('window.__motionSharedThreeControl.anchors()')
  samples=[]
  for frac in [0,.25,.5,.75,1]:
   midpoint=anchors[0]+(anchors[-1]-anchors[0])*frac
   view.evaluate("(y)=>window.scrollTo(0,Math.max(0,y-innerHeight*.5))",midpoint)
   view.wait_for_timeout(120)
   samples.append(view.evaluate('window.__motionSharedThreeControl.update()'))
  result['exportCameraSamples']=samples
  result['exportShared']=view.evaluate("({id:window.__motionSharedThree.sceneUuid,webgl:window.__motionSharedThree.webgl2,models:window.__motionSharedThree.loadedModels,pathCounts:window.__motionSharedThree.stage11PathCounts,frames:window.__motionSharedThree.renderFrames,pixels:window.__motionSharedThree.visiblePixels,error:window.__motionSharedThree.error,canvas:document.querySelectorAll('#motion-shared-three-canvas').length})")
  view.screenshot(path=str(R/'STAGE11-TIMELINE-CAPTURE.png'))
  mid=samples[2]
  result['pass']=(
   result['componentCount']==20 and result['glbChapters']==2 and result['panelVisible']
   and result['initialPoints']==3 and result['afterAdd']==4 and result['afterDelete']==3
   and result['dragModified'] and result['livePatched']
   and len(result['editedPath'])==3 and result['reloadedPath']==result['editedPath']
   and len(result['editedPath'])<=8 and result['editedPath'][0]['at']==0 and result['editedPath'][-1]['at']==100
   and result['previewBefore']['webgl'] and result['previewAfter']['webgl']
   and result['exportShared']['webgl'] and result['exportShared']['models']==2
   and result['exportShared']['canvas']==1 and result['exportShared']['pathCounts'][0]==3
   and mid.get('stage11Custom') is True and mid['x']>3.2 and mid['y']>0.65
   and mid['fov']>54 and mid['yaw']>10
   and result['exportShared']['frames']>=5 and result['exportShared']['pixels']>0
   and not result['exportShared']['error'] and not result['errors'] and not result.get('remoteRequests')
  )
  view.close();editor.close();b.close()
except Exception:
 result['errors'].append(traceback.format_exc(limit=6))
finally:
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(result,ensure_ascii=False,indent=2))
assert result['pass'],'Stage11 visual timeline/editor/live camera regression failed'
