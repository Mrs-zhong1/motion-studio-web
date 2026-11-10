"""Stage14 3MiB valid GLB, compressed-extension rejection, camera Undo/Redo,
shared-context scroll/resize stress. Cloud software WebGL only.
"""
import json,struct,traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT.parent/'Sample-Textured-Animated.glb'
OUT=ROOT/'STAGE14-STRESS-RESULT.json'
result={'pass':False,'hardwareGpuTested':False,'safariTested':False,'gpuMemoryLeakVerified':False,'tests':{},'errors':[]}
def make_large():
    raw=SOURCE.read_bytes()
    assert raw[:4]==b'glTF'
    offset=12;chunks=[]
    while offset<len(raw):
        size,kind=struct.unpack_from('<I4s',raw,offset);offset+=8
        chunks.append((kind,raw[offset:offset+size]));offset+=size
    assert chunks[0][0]==b'JSON' and chunks[1][0]==b'BIN\x00'
    # Add legitimate BIN padding (GLB container remains compliant; original
    # glTF buffers[0].byteLength still reflects actual referenced buffer data).
    old=chunks[1][1];add=3*1024*1024-len(raw)
    add+=(-add)%4
    assert add>0
    chunks[1]=(b'BIN\x00',old+b'\x00'*add)
    size=12+sum(8+len(data) for _,data in chunks)
    large=struct.pack('<4sII',b'glTF',2,size)
    for kind,data in chunks:large+=struct.pack('<I4s',len(data),kind)+data
    assert len(large)>2*1024*1024 and len(large)<4*1024*1024
    return large
def malformed_extension(name):
    doc={'asset':{'version':'2.0'},'meshes':[],'extensionsUsed':[name],'extensionsRequired':[name]}
    j=json.dumps(doc,separators=(',',':')).encode()
    j+=b' '*((-len(j))%4)
    return struct.pack('<4sII',b'glTF',2,20+len(j))+struct.pack('<I4s',len(j),b'JSON')+j
try:
 with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-webgl','--enable-unsafe-swiftshader'])
    page=browser.new_page(viewport={'width':1330,'height':900},accept_downloads=True)
    page.on('pageerror',lambda e:result['errors'].append('editor: '+str(e)))
    page.set_content((ROOT/'Motion-Studio-Stage14-Stability-OFFLINE.html').read_text(encoding='utf8'),wait_until='domcontentloaded')
    page.locator('.comp[data-id="offline-glb-scene"] button').click()
    big=make_large();result['tests']['largeBytes']=len(big)
    page.locator('#stage9GlbInput').set_input_files({'name':'large-padded-compliant.glb','mimeType':'model/gltf-binary','buffer':big})
    page.wait_for_timeout(500)
    result['tests']['largeImported']=page.evaluate("project.sections.find(s=>s.id==='offline-glb-scene').glb.length")>3_000_000
    initial=page.evaluate("project.sections.find(s=>s.id==='offline-glb-scene').glb")
    rejected=[]
    for ext in ['KHR_draco_mesh_compression','KHR_texture_basisu','EXT_meshopt_compression']:
      page.locator('#stage9GlbInput').set_input_files({'name':ext+'.glb','mimeType':'model/gltf-binary','buffer':malformed_extension(ext)})
      page.wait_for_timeout(120)
      rejected.append(page.evaluate("project.sections.find(s=>s.id==='offline-glb-scene').glb")==initial)
    page.locator('#stage9GlbInput').set_input_files({'name':'overlimit.glb','mimeType':'model/gltf-binary','buffer':b'!'*(4*1024*1024+8)})
    page.wait_for_timeout(120)
    result['tests']['unsupportedExtensionsRejected']=all(rejected)
    result['tests']['over4MBRejected']=page.evaluate("project.sections.find(s=>s.id==='offline-glb-scene').glb")==initial
    page.locator('.comp[data-id="offline-glb-scene"] button').click()
    page.locator('#stage9GlbInput').set_input_files(str(SOURCE))
    page.wait_for_timeout(350)
    uid=page.evaluate("project.sections.filter(s=>s.id==='offline-glb-scene'&&s.glb)[0].uid")
    page.evaluate('(uid)=>selectSection(uid)',uid)
    page.locator('#stage11Enable').click()
    page.locator('#stage11KeySelect').select_option('1')
    page.locator('[data-stage13-handle="handleOut"][data-axis="y"]').fill('1.3')
    page.locator('[data-stage13-handle="handleOut"][data-axis="y"]').dispatch_event('change')
    changed=page.evaluate("(uid)=>project.sections.find(s=>s.uid===uid).cameraPath11[1].handleOut.y",uid)
    page.evaluate("restoreHistory('undo')")
    undone=page.evaluate("(uid)=>project.sections.find(s=>s.uid===uid).cameraPath11[1].handleOut?.y",uid)
    page.evaluate("restoreHistory('redo')")
    redone=page.evaluate("(uid)=>project.sections.find(s=>s.uid===uid).cameraPath11[1].handleOut.y",uid)
    result['tests']['undoRedo']={'changed':changed,'undone':undone,'redone':redone,'passed':changed==1.3 and undone!=1.3 and redone==1.3}
    with page.expect_download() as dl:page.locator('#exportPage').click()
    exported=ROOT/'STAGE14-STRESS-EXPORTED.html';dl.value.save_as(exported)
    result['tests']['exportBytes']=exported.stat().st_size
    view=browser.new_page(viewport={'width':1180,'height':680})
    view.on('pageerror',lambda e:result['errors'].append('export: '+str(e)))
    view.on('request',lambda r:result.setdefault('remoteRequests',[]).append(r.url) if r.url.startswith(('http://','https://')) else None)
    view.set_content(exported.read_text(encoding='utf8'),wait_until='domcontentloaded')
    view.wait_for_function('window.__motionSharedThree?.loadedModels===2 || Boolean(window.__motionSharedThree?.error)',timeout=20000)
    anchors=view.evaluate('window.__motionSharedThreeControl.anchors()')
    for i in range(120):
      focus=anchors[0]+(anchors[-1]-anchors[0])*(i%41)/40
      view.evaluate("(focus)=>{window.scrollTo(0,Math.max(0,focus-innerHeight*.5));window.__motionSharedThreeControl.update();}",focus)
      if i%20==0:
        view.set_viewport_size({'width':1180-(i%60)*2,'height':680-(i%40)})
    result['tests']['sharedStress']=view.evaluate("({webgl2:window.__motionSharedThree.webgl2,canvas:document.querySelectorAll('#motion-shared-three-canvas').length,models:window.__motionSharedThree.loadedModels,frames:window.__motionSharedThree.renderFrames,error:window.__motionSharedThree.error,contextLost:window.__motionSharedThree.contextLost,sceneId:window.__motionSharedThree.sceneUuid})")
    view.screenshot(path=str(ROOT/'STAGE14-STRESS-CAPTURE.png'))
    result['pass']=(
      page.evaluate('registry.length')==20
      and result['tests']['largeImported'] and result['tests']['unsupportedExtensionsRejected']
      and result['tests']['over4MBRejected'] and result['tests']['undoRedo']['passed']
      and result['tests']['sharedStress']['webgl2'] and result['tests']['sharedStress']['canvas']==1
      and result['tests']['sharedStress']['models']==2 and result['tests']['sharedStress']['frames']>=120
      and not result['tests']['sharedStress']['error'] and not result['tests']['sharedStress']['contextLost']
      and not result['errors'] and not result.get('remoteRequests')
    )
    view.close();page.close();browser.close()
except Exception:
 result['errors'].append(traceback.format_exc(limit=6))
finally:
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(result,ensure_ascii=False,indent=2))
assert result['pass'],'Stage14 stress, undo/redo or model compatibility acceptance failed'
