from pathlib import Path
from playwright.sync_api import sync_playwright
import json,os
root=Path(__file__).resolve().parents[1]
out=root/'Motion-Studio-Stage9-THREE-OFFLINE.html'
if not out.exists():raise SystemExit('Offline bundle missing: run npm run build')
res={'buildExists':True,'gpuAccepted':False,'errors':[]}
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-webgl','--enable-unsafe-swiftshader'])
 page=browser.new_page(viewport={'width':1440,'height':900},accept_downloads=True)
 page.on('pageerror',lambda e:res['errors'].append({'message':str(e),'stack':str(e.stack)}))
 page.set_content(out.read_text(),wait_until='domcontentloaded')
 page.wait_for_timeout(600)
 res['componentCount']=page.evaluate('registry.length')
 page.locator('#resumeProject').click()
 page.locator('[data-asset-tier-button="l3"]').click()
 page.locator('.comp[data-id="offline-glb-scene"] button').click()
 page.locator('#stage9GlbInput').set_input_files(str(root.parent/'Sample-Textured-Animated.glb'))
 page.wait_for_timeout(1700)
 res['editorModelBytes']=page.evaluate('project.sections.find(s=>s.id==="offline-glb-scene").glb.length')
 with page.expect_download() as dl:page.locator('#exportPage').click()
 path=root/'STAGE9-THREE-EXPORTED.html';dl.value.save_as(path)
 res['exportBytes']=path.stat().st_size
 exp=browser.new_page(viewport={'width':1200,'height':850})
 exp.on('pageerror',lambda e:res['errors'].append({'message':'export:'+str(e),'stack':str(e.stack)}))
 exp.set_content(path.read_text(),wait_until='domcontentloaded')
 exp.wait_for_timeout(2500)
 statuses=[]
 frames=[]
 for f in exp.frames[1:]:
  try:
   v=f.evaluate('window.__motionThreeStatus || null')
   if v:statuses.append(v);frames.append(f)
  except Exception as e:res['errors'].append('iframe:'+str(e))
 res['exportedFrames']=len(exp.frames)
 res['frameScripts']=[{'title':f.evaluate('document.title'),'scriptCount':f.evaluate('document.scripts.length'),'scriptPreview':f.evaluate('Array.from(document.scripts).map(x=>x.textContent.slice(0,70))')} for f in exp.frames[1:]]
 if frames:
  target=frames[0]
  target.evaluate("window.postMessage({type:'motion-studio-scroll',progress:0.05}, '*')")
  exp.wait_for_timeout(180)
  res['animationAtStart']=target.evaluate('window.__motionThreeStatus.animationRotationSamples.slice(-1)[0] || null')
  target.evaluate("window.postMessage({type:'motion-studio-scroll',progress:0.8}, '*')")
  exp.wait_for_timeout(180)
  res['animationAtEnd']=target.evaluate('window.__motionThreeStatus.animationRotationSamples.slice(-1)[0] || null')
  res['exportThreeStatuses']=[f.evaluate('window.__motionThreeStatus') for f in frames]
 else:res['exportThreeStatuses']=statuses
 res['gpuAccepted']=not res['errors'] and any(s.get('webgl2') and s.get('pbr') and s.get('textureCount',0)>0 and s.get('animationClips',0)>0 and s.get('frames',0)>1 and s.get('visiblePixels',0)>=2 and s.get('pixelDifference',0)>20 and s.get('animationMoved') and res.get('animationAtStart')!=res.get('animationAtEnd') and not s.get('error') for s in res['exportThreeStatuses'])
 exp.screenshot(path=str(root/'STAGE9-THREE-EXPORT.png'))
 browser.close()
(root/'STAGE9-THREE-BROWSER-RESULT.json').write_text(json.dumps(res,ensure_ascii=False,indent=2))
print(json.dumps(res,ensure_ascii=False,indent=2))
assert res['componentCount']==20 and res['editorModelBytes']>0 and res['exportBytes']>0,'Stage9 editor/export regression'
assert res['gpuAccepted'],'WebGL/PBR/texture/GLB animation/visible pixel acceptance failed; NOT release ready'
