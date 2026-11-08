#!/usr/bin/env python3
"""Strict end-to-end WebGL/PBR pipeline acceptance. Requires offline editor and WebGL.

Exit nonzero unless a user GLB with texture and animation is rendered by
Three.js in the *exported* standalone HTML, with zero network access.
"""
from pathlib import Path
import json,sys,traceback,time
from playwright.sync_api import sync_playwright
P=Path(__file__).resolve().parent
out={'webgl_context':False,'gpu_context':False,'hardware_gpu_verified':False,'offline_editor_present':False,'user_glb_uploaded':False,'export_created':False,
     'standalone_export_opens':False,'three_canvas_frames':0,'gltf_animation_clips':0,'texture_maps':0,'physical_materials':0,'animation_time':0,'mesh_count':0,
     'no_external_requests':True,'no_javascript_errors':True,'webgl_pipeline_pass':False,'production_gpu_pass':False,
     'errors':[],'network_requests':[]}
try:
 html=P/'Motion-Studio-Editor-OFFLINE.html'
 out['offline_editor_present']=html.is_file()
 if not html.is_file():raise RuntimeError('Missing real offline Three.js bundle. Run npm run build:offline in an online build environment.')
 with sync_playwright() as p:
  b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None,
       args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  try:
   ctx=b.new_context(accept_downloads=True,viewport={'width':1380,'height':850})
   page=ctx.new_page()
   def guard(route):
    u=route.request.url
    if u.startswith(('http:','https:')):
     out['no_external_requests']=False;out['network_requests'].append(u);route.abort()
    else:route.continue_()
   ctx.route('**/*',guard)
   page.on('pageerror',lambda e:out['errors'].append('editor: '+str(e)))
   page.set_content(html.read_text(),wait_until='domcontentloaded',timeout=30000)
   out['webgl_context']=page.evaluate("()=>{const c=document.createElement('canvas');try{return !!(c.getContext('webgl2')||c.getContext('webgl'))}catch(e){return false}}")
   if not out['webgl_context']:raise RuntimeError('WebGL context creation failed; PBR verification is blocked, not passed.')
   page.locator('#templateList .template-card').nth(1).click(timeout=6000)
   page.locator('#glbInput').set_input_files(str(P/'Sample-Textured-Animated.glb'))
   page.wait_for_timeout(700)
   out['user_glb_uploaded']=page.evaluate("()=>!!document.querySelector('#glbStatus')?.textContent.includes('已导入')")
   with page.expect_download(timeout=15000) as d:page.locator('#exportBtn').click(timeout=6000)
   path=P/'R12-THREE-OFFLINE-EXPORT.html';d.value.save_as(path)
   out['export_created']=path.is_file() and path.stat().st_size>100000
   q=ctx.new_page();q.on('pageerror',lambda e:out['errors'].append('export: '+str(e)))
   q.set_content(path.read_text(),wait_until='domcontentloaded',timeout=30000)
   out['standalone_export_opens']=q.locator('body.template-orbit').count()==1
   try:
    q.wait_for_function("()=>Number(document.querySelector('#ms-three-canvas')?.dataset.frameCount||0)>=3",timeout=17000)
   except Exception:pass
   info=q.evaluate("()=>{const d=document.querySelector('#ms-three-canvas')?.dataset||{};return {frames:Number(d.frameCount||0),animations:Number(d.gltfAnimations||0),textures:Number(d.textureMaps||0),physicalMaterials:Number(d.physicalMaterials||0),animationTime:Number(d.animationTime||0),meshCount:Number(d.gltfMeshCount||0),hud:document.querySelector('#ms-render-kind')?.textContent||'',legacy:document.querySelector('#webgl-canvas')?.dataset.renderer||''}}")
   out['three_canvas_frames']=info['frames'];out['gltf_animation_clips']=info['animations'];out['texture_maps']=info['textures'];out['physical_materials']=info['physicalMaterials'];out['animation_time']=info['animationTime'];out['mesh_count']=info['meshCount'];out['render_state']=info
   out['no_javascript_errors']=not out['errors']
   out['webgl_pipeline_pass']=(out['webgl_context'] and out['user_glb_uploaded'] and out['export_created'] and out['standalone_export_opens'] and out['mesh_count']>=1 and out['three_canvas_frames']>=3 and out['gltf_animation_clips']>=1 and out['texture_maps']>=1 and out['physical_materials']>=1 and out['animation_time']>0 and out['no_external_requests'] and out['no_javascript_errors'])
   # SwiftShader is a software WebGL implementation. This check is not hardware GPU proof.
   out['production_gpu_pass']=False
  finally:b.close()
except Exception as e:
 out['errors'].append(type(e).__name__+': '+str(e))
finally:
 (P/'R12_GPU_TEST.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
 print(json.dumps(out,ensure_ascii=False,indent=2))
 sys.exit(0 if out['webgl_pipeline_pass'] else 2)
