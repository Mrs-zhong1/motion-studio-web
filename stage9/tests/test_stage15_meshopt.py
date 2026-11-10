"""Verify genuinely meshopt compressed GLB renders in single+shared offline Three.js engines."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,traceback
R=Path(__file__).resolve().parents[1]
OUT=R/'STAGE15-MESHOPT-RESULT.json'
FIX=R.parent/'Sample-Meshopt-Compressed.glb'
result={'pass':False,'source':'GitHub Actions Chromium SwiftShader software WebGL','realCompressedFixture':False,'single':{},'shared':{},'errors':[]}
try:
 assert FIX.exists() and FIX.stat().st_size>150
 raw=FIX.read_bytes()
 assert b'EXT_meshopt_compression' in raw
 result['realCompressedFixture']=True
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-webgl','--enable-unsafe-swiftshader'])
  ed=browser.new_page(viewport={'width':1280,'height':760},accept_downloads=True)
  ed.on('pageerror',lambda e:result['errors'].append('editor:'+str(e)))
  ed.set_content((R/'Motion-Studio-Stage15-Meshopt-OFFLINE.html').read_text(encoding='utf8'),wait_until='domcontentloaded')
  ed.locator('.comp[data-id="offline-glb-scene"] button').click()
  ed.locator('#stage9GlbInput').set_input_files(str(FIX))
  ed.wait_for_timeout(220)
  result['single']['importedBytes']=ed.evaluate("project.sections.filter(s=>s.id==='offline-glb-scene')[0].glb.length")
  with ed.expect_download() as dl:ed.locator('#exportPage').click()
  target=R/'STAGE15-MESHOPT-SINGLE-EXPORTED.html';dl.value.save_as(target)
  page=browser.new_page(viewport={'width':1180,'height':720})
  page.on('pageerror',lambda e:result['errors'].append('single:'+str(e)))
  page.on('request',lambda req:result.setdefault('remoteRequests',[]).append(req.url) if req.url.startswith(('http://','https://')) else None)
  page.set_content(target.read_text(encoding='utf8'),wait_until='domcontentloaded')
  page.wait_for_timeout(1100)
  f=None
  for candidate in page.frames[1:]:
   try:
    if candidate.evaluate('Boolean(window.__motionThreeStatus)'):f=candidate;break
   except:pass
  assert f,'Real single Three.js GLB renderer missing'
  for p in [.03,.34,.7,.98]:
   f.evaluate("(x)=>window.postMessage({type:'motion-studio-scroll',progress:x},'*')",p)
   page.wait_for_timeout(130)
  stat=f.evaluate('window.__motionThreeStatus')
  result['single'].update({k:stat.get(k) for k in ['webgl2','meshCount','materialCount','pbr','visiblePixels','pixelDifference','frames','error']})
  page.screenshot(path=str(R/'STAGE15-MESHOPT-CAPTURE.png'))
  # A second GLB must be loaded into the same real shared WebGL scene.
  ed.locator('.comp[data-id="offline-glb-scene"] button').click()
  ed.locator('#stage9GlbInput').set_input_files(str(R.parent/'Sample-Dual-Material.glb'))
  ed.wait_for_timeout(260)
  with ed.expect_download() as dl:ed.locator('#exportPage').click()
  shared=R/'STAGE15-MESHOPT-SHARED-EXPORTED.html';dl.value.save_as(shared)
  sh=browser.new_page(viewport={'width':1180,'height':690})
  sh.on('pageerror',lambda e:result['errors'].append('shared:'+str(e)))
  sh.on('request',lambda req:result.setdefault('remoteRequests',[]).append(req.url) if req.url.startswith(('http://','https://')) else None)
  sh.set_content(shared.read_text(encoding='utf8'),wait_until='domcontentloaded')
  sh.wait_for_function('window.__motionSharedThree?.loadedModels===2 || Boolean(window.__motionSharedThree?.error)',timeout=20000)
  sh.wait_for_timeout(120)
  result['shared']=sh.evaluate("({webgl2:window.__motionSharedThree.webgl2,models:window.__motionSharedThree.loadedModels,meshCounts:window.__motionSharedThree.modelMeshCounts,canvas:document.querySelectorAll('#motion-shared-three-canvas').length,visible:window.__motionSharedThree.visiblePixels,error:window.__motionSharedThree.error})")
  sh.screenshot(path=str(R/'STAGE15-MESHOPT-SHARED-CAPTURE.png'))
  result['componentCount']=ed.evaluate('registry.length')
  result['pass']=(
   result['realCompressedFixture'] and result['componentCount']==20
   and result['single'].get('importedBytes',0)>100 and result['single'].get('webgl2')
   and result['single'].get('meshCount',0)>=1
   and result['single'].get('materialCount',0)>=1
   and result['single'].get('pbr')
   and result['single'].get('visiblePixels',0)>2
   and result['single'].get('pixelDifference',0)>15
   and result['single'].get('frames',0)>=4 and not result['single'].get('error')
   and result['shared'].get('webgl2') and result['shared'].get('models')==2
   and result['shared'].get('canvas')==1 and result['shared'].get('meshCounts',[0])[0]>=1
   and not result['shared'].get('error')
   and not result['errors'] and not result.get('remoteRequests')
  )
  sh.close();page.close();ed.close();browser.close()
except Exception:
 result['errors'].append(traceback.format_exc(limit=6))
finally:
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(result,ensure_ascii=False,indent=2))
assert result['pass'],'Genuine meshopt compressed GLB offline WebGL verification failed'
