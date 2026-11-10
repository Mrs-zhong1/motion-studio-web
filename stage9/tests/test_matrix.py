"""Stage 9 compatibility matrix: two real GLB fixtures, offline exports, WebGL, visual metrics.

Runs against the actual cloud-built standalone editor using software WebGL;
does not claim native macOS hardware GPU acceptance.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json, time, traceback
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'Motion-Studio-Stage9-THREE-OFFLINE.html'
RESULT=ROOT/'STAGE9-MATRIX-RESULT.json'
FIXTURES=[
 {"file":"Sample-Dual-Material.glb","min_materials":2,"min_textures":0,"min_animations":0},
 {"file":"Sample-Textured-Animated.glb","min_materials":1,"min_textures":1,"min_animations":1},
 {"file":"Sample-Skinned-Morph-MultiClip.glb","min_materials":1,"min_textures":0,"min_animations":2,"skinned":1,"morph":1,"bones":2},
]
result={"test":"Stage9 GLB compatibility matrix","source":"GitHub Actions cloud Chromium with SwiftShader","hardwareGpuTested":False,"safariTested":False,"results":[],"pass":False}
try:
 if not OUT.exists(): raise RuntimeError("Missing real offline HTML")
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=["--no-sandbox","--use-gl=angle","--use-angle=swiftshader","--enable-webgl","--enable-unsafe-swiftshader"])
  for spec in FIXTURES:
   item={"fixture":spec["file"],"errors":[],"remoteRequests":[],"passed":False}
   result["results"].append(item)
   try:
    fixture=ROOT.parent/spec["file"]
    assert fixture.exists(),f"Missing fixture: {fixture}"
    page=browser.new_page(viewport={"width":1366,"height":850},accept_downloads=True)
    page.on("pageerror",lambda err,entry=item:entry["errors"].append(str(err)))
    page.on("request",lambda req,entry=item:entry["remoteRequests"].append(req.url) if req.url.startswith(("http://","https://")) else None)
    page.set_content(OUT.read_text(encoding="utf-8"),wait_until="domcontentloaded")
    page.wait_for_timeout(250)
    item["components"]=page.evaluate("registry.length")
    page.locator('.comp[data-id="offline-glb-scene"] button').click()
    page.locator("#stage9GlbInput").set_input_files(str(fixture))
    page.wait_for_timeout(500)
    item["modelBase64Length"]=page.evaluate('project.sections.find(s=>s.id==="offline-glb-scene").glb.length')
    with page.expect_download() as dl: page.locator("#exportPage").click()
    exported=ROOT/("STAGE9-"+spec["file"].replace(".glb","") + "-EXPORTED.html")
    dl.value.save_as(exported)
    item["exportBytes"]=exported.stat().st_size
    exp=browser.new_page(viewport={"width":1100,"height":760})
    exp.on("pageerror",lambda err,entry=item:entry["errors"].append("export:"+str(err)))
    exp.on("request",lambda req,entry=item:entry["remoteRequests"].append(req.url) if req.url.startswith(("http://","https://")) else None)
    exp.set_content(exported.read_text(encoding="utf-8"),wait_until="domcontentloaded")
    exp.wait_for_timeout(1100)
    target=None
    for frame in exp.frames[1:]:
     try:
      if frame.evaluate("Boolean(window.__motionThreeStatus)"):target=frame;break
     except Exception: pass
    assert target,"No real Three.js renderer iframe was started"
    for pos in [0.02,.24,.76,.96]:
     target.evaluate("(p)=>window.postMessage({type:'motion-studio-scroll',progress:p},'*')",pos)
     exp.wait_for_timeout(90)
    item["renderer"]=target.evaluate("window.__motionThreeStatus")
    stat=item["renderer"]
    item["avgDrawMs"]=round(stat.get("drawTotalMs",0)/max(1,stat.get("drawSamples",0)),3)
    item["skinMorphPass"]=(
     (not spec.get("skinned") or stat.get("skinnedMeshCount",0)>=spec["skinned"])
     and (not spec.get("morph") or stat.get("morphMeshCount",0)>=spec["morph"])
     and (not spec.get("bones") or stat.get("boneCount",0)>=spec["bones"])
     and (not spec.get("skinned") or len(set(stat.get("boneRotationSamples",[])))>=2)
     and (not spec.get("morph") or len(set(stat.get("morphInfluenceSamples",[])))>=2)
    )
    item["modelPass"]=(
     item["components"]==20
     and item["modelBase64Length"]>1000
     and stat.get("webgl2")
     and stat.get("pbr")
     and stat.get("materialCount",0)>=spec["min_materials"]
     and stat.get("textureCount",0)>=spec["min_textures"]
     and stat.get("animationClips",0)>=spec["min_animations"]
     and stat.get("frames",0)>=4
     and stat.get("visiblePixels",0)>=2
     and stat.get("pixelDifference",0)>20
     and stat.get("drawSamples",0)>=4
     and item["skinMorphPass"]
     and not stat.get("error")
    )
    item["passed"]=bool(item["modelPass"] and not item["remoteRequests"] and not item["errors"])
    exp.screenshot(path=str(ROOT/("STAGE9-"+spec["file"].replace(".glb","")+"-CAPTURE.png")))
    exp.close();page.close()
   except Exception as e:
    item["errors"].append(str(e))
    item["traceback"]=traceback.format_exc(limit=3)
  # Separate mobile layout and existing UI smoke, do not conflate with graphics pass.
  mobile=browser.new_page(viewport={"width":390,"height":844},device_scale_factor=2)
  mobile.on("pageerror",lambda err:result.setdefault("mobileErrors",[]).append(str(err)))
  mobile.set_content(OUT.read_text(encoding="utf-8"),wait_until="domcontentloaded")
  result["mobile"]={
   "componentCount":mobile.evaluate("registry.length"),
   "documentWidth":mobile.evaluate("document.documentElement.scrollWidth"),
   "viewportWidth":mobile.evaluate("window.innerWidth"),
   "horizontalOverflow":mobile.evaluate("document.documentElement.scrollWidth>window.innerWidth+2")
  }
  mobile.close()
  browser.close()
 result["pass"]=all(t["passed"] for t in result["results"]) and result["mobile"]["componentCount"]==20
except Exception as e:
 result["fatalError"]=str(e)
finally:
 RESULT.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
 print(json.dumps(result,ensure_ascii=False,indent=2))
assert result["pass"],"Stage9 compatibility matrix failed (see STAGE9-MATRIX-RESULT.json)"
