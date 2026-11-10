"""Validate real shared WebGL scene across 2 GLB chapters and legacy single-GLB compatibility."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,traceback
R=Path(__file__).resolve().parents[1]
E=R/'Motion-Studio-Stage9-THREE-OFFLINE.html'
O=R/'STAGE9-SHARED-SCENE-RESULT.json'
result={"pass":False,"test":"one WebGL scene, two GLB chapters and continuous camera","environment":"GitHub Actions Chromium SwiftShader (software WebGL)","hardwareGpuTested":False,"safariTested":False,"errors":[]}
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=["--no-sandbox","--use-gl=angle","--use-angle=swiftshader","--enable-webgl","--enable-unsafe-swiftshader"])
  ed=browser.new_page(viewport={"width":1180,"height":720},accept_downloads=True)
  ed.on("pageerror",lambda e:result["errors"].append("editor:"+str(e)))
  ed.set_content(E.read_text(encoding="utf8"),wait_until="domcontentloaded")
  ed.wait_for_timeout(350)
  for fixture in ["Sample-Dual-Material.glb","Sample-Textured-Animated.glb"]:
   ed.locator('.comp[data-id="offline-glb-scene"] button').click()
   ed.locator("#stage9GlbInput").set_input_files(str(R.parent/fixture))
   ed.wait_for_timeout(150)
  result["count"]=ed.evaluate("registry.length")
  result["uploadedModelCount"]=ed.evaluate("project.sections.filter(s=>s.id==='offline-glb-scene'&&s.glb).length")
  with ed.expect_download() as dl:ed.locator("#exportPage").click()
  target=R/'STAGE9-SHARED-TWO-GLB-EXPORTED.html';dl.value.save_as(target)
  result["exportBytes"]=target.stat().st_size
  page=browser.new_page(viewport={"width":1180,"height":600})
  page.on("pageerror",lambda e:result["errors"].append("export:"+str(e)))
  page.on("request",lambda req:result.setdefault("externalRequests",[]).append(req.url) if req.url.startswith(("http:","https:")) else None)
  page.set_content(target.read_text(encoding="utf8"),wait_until="domcontentloaded")
  page.wait_for_function("window.__motionSharedThree?.loadedModels===2 || !!window.__motionSharedThree?.error",timeout=20000)
  page.wait_for_timeout(600)
  result["initial"]=page.evaluate("({status:window.__motionSharedThree,anchors:window.__motionSharedThreeControl?.anchors(),iframes:document.querySelectorAll('.section[data-shared-three] iframe').length,canvasCount:document.querySelectorAll('#motion-shared-three-canvas').length})")
  if not result["initial"]["status"].get("error"):
   anchors=result["initial"]["anchors"]
   # Probe three distinct scroll stops, the same camera/scene must be reused.
   probe=[]
   for frac in [0,.25,.5,.75,1]:
    mid=anchors[0]+(anchors[-1]-anchors[0])*frac
    page.evaluate("(mid)=>window.scrollTo(0,Math.max(0,mid-innerHeight*.5))",mid)
    page.wait_for_timeout(170)
    v=page.evaluate("window.__motionSharedThreeControl.update()")
    probe.append(v)
   result["cameraPositions"]=probe
   result["final"]=page.evaluate("window.__motionSharedThree")
   page.screenshot(path=str(R/'STAGE9-SHARED-SCENE.png'))
  else:result["final"]=result["initial"]["status"]
  t=result["final"]
  xs=[s["x"] for s in result.get("cameraPositions",[])]
  result["pass"]=(
   result["count"]==20 and result["uploadedModelCount"]==2
   and result["initial"]["canvasCount"]==1 and result["initial"]["iframes"]==2
   and t.get("webgl2") and t.get("loadedModels")==2
   and t.get("renderFrames",0)>=5 and t.get("visiblePixels",0)>=1
   and t.get("sceneUuid")==result["initial"]["status"].get("sceneUuid")
   and len(set(round(x,2) for x in xs))>=3
   and all(xs[i]<=xs[i+1]+1e-5 for i in range(len(xs)-1))
   and not t.get("error") and not t.get("contextLost")
   and not result["errors"] and not result.get("externalRequests")
  )
  browser.close()
except Exception:result["errors"].append(traceback.format_exc(limit=4))
finally:
 O.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf8")
 print(json.dumps(result,ensure_ascii=False,indent=2))
assert result["pass"],"Shared WebGL continuity acceptance not passed"
