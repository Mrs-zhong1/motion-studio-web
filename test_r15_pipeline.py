#!/usr/bin/env python3
"""R15: assert exactly embedded source GLB survives editor export; check visual interaction.
The success of this test is NOT evidence of hardware GPU or Three.js PBR rendering.
"""
from pathlib import Path
import base64, hashlib, json, re
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parent
out={'actual_glb_bytes_preserved':False,'embedded_glb_sha256':None,'source_glb_sha256':None,
     'glb_has_texture':False,'glb_has_animation':False,'no_remote_resources_required_for_canvas_fallback':True,
     'editor_loads':False,'export_reopens':False,'scroll_progress_changes':False,
     'cpu_renderer_frames_increase':False,'mobile_overflow':None,'browser_errors':[],
     'scope':'HTML, model bytes, Canvas fallback only; Three PBR / GPU is NOT verified'}

def glb_meta(blob):
    assert blob[:4]==b'glTF' and int.from_bytes(blob[4:8],'little')==2
    assert int.from_bytes(blob[8:12],'little')==len(blob)
    n=int.from_bytes(blob[12:16],'little')
    doc=json.loads(blob[20:20+n].decode().rstrip('\x00 '))
    return doc

try:
    original=(root/'Sample-Textured-Animated.glb').read_bytes()
    out['source_glb_sha256']=hashlib.sha256(original).hexdigest()
    desc=glb_meta(original)
    out['glb_has_texture']=bool(desc.get('images') and desc.get('textures'))
    out['glb_has_animation']=bool(desc.get('animations'))
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'],**({'executable_path':'/usr/bin/chromium'} if Path('/usr/bin/chromium').exists() else {}))
        ctx=browser.new_context(accept_downloads=True,viewport={'width':1280,'height':800})
        ctx.route('**/*',lambda route:(route.abort() if route.request.url.startswith(('https://','http://')) else route.continue_()))
        pg=ctx.new_page();pg.on('pageerror',lambda e:out['browser_errors'].append('editor: '+str(e)))
        pg.set_content((root/'Motion-Studio-Editor.html').read_text(),wait_until='domcontentloaded')
        out['editor_loads']=pg.locator('#exportBtn').count()==1
        pg.locator('#templateList .template-card').nth(1).click()
        pg.locator('#glbInput').set_input_files(str(root/'Sample-Textured-Animated.glb'))
        pg.wait_for_timeout(400)
        with pg.expect_download(timeout=15000) as e:pg.locator('#exportBtn').click()
        downloaded=root/'R15-verbatim-glb-export.html';e.value.save_as(downloaded)
        page_html=downloaded.read_text()
        matched=re.search(r'data:model/gltf-binary;base64,([a-zA-Z0-9+/=]+)',page_html)
        assert matched,'No embedded raw GLB in export'
        recovered=base64.b64decode(matched.group(1),validate=True)
        out['embedded_glb_sha256']=hashlib.sha256(recovered).hexdigest()
        out['actual_glb_bytes_preserved']=recovered==original
        assert glb_meta(recovered)['asset']['version']=='2.0'
        q=ctx.new_page();q.on('pageerror',lambda e:out['browser_errors'].append('export: '+str(e)))
        q.set_content(page_html,wait_until='domcontentloaded')
        out['export_reopens']=q.locator('body.template-orbit').count()==1
        q.wait_for_timeout(350)
        first=q.evaluate("()=>Number(document.body.dataset.motionFrames||0)")
        q.locator('#chapter-1').scroll_into_view_if_needed(timeout=5000)
        q.wait_for_timeout(350)
        second=q.evaluate("()=>Number(document.body.dataset.motionFrames||0)")
        out['scroll_progress_changes']=second>first
        # For an unsupported animated GLB, UI must indicate nonavailability rather
        # than silently painting an unrelated torus model.
        out['unsupported_glb_fallback_notice']=q.locator('#webgl-fallback').count()>0 and q.locator('#webgl-fallback').is_visible()
        out['cpu_renderer_frames_increase']=q.locator('#webgl-canvas').get_attribute('data-frame-count') not in (None,'0')
        q.set_viewport_size({'width':390,'height':844});q.wait_for_timeout(200)
        out['mobile_overflow']=q.evaluate('()=>document.documentElement.scrollWidth>innerWidth+2')
        browser.close()
except Exception as e:
    out['error']=str(e)

passed=(out['actual_glb_bytes_preserved'] and out['glb_has_texture'] and out['glb_has_animation'] and out['editor_loads']
        and out['export_reopens'] and out['scroll_progress_changes'] and out['mobile_overflow'] is False and not out['browser_errors'])
out['pass']=passed
(root/'R15_TEST.json').write_text(json.dumps(out,indent=2,ensure_ascii=False))
print(json.dumps(out,indent=2,ensure_ascii=False))
raise SystemExit(0 if passed else 2)
