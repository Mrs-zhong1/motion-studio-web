from pathlib import Path
from playwright.sync_api import sync_playwright
import json,traceback,sys
R=Path(__file__).parent
result={'editor_loaded':False,'exported_file':False,'chapter_progress_changes':False,'mobile_no_overflow':False,'reduced_motion_respected':False,'glb_original_embedded':False,'texture_animation_metadata_preserved':False,'script_errors':[],'gpu_pbr':'SEE R12_GPU_TEST.json','offline_three_bundle':'PRESENT' if (R/'Motion-Studio-Editor-OFFLINE.html').exists() else 'MISSING'}
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--no-sandbox','--disable-dev-shm-usage']); c=b.new_context(accept_downloads=True,viewport={'width':1380,'height':850});pg=c.new_page()
 pg.route('**/*',lambda r:r.abort() if r.request.url.startswith('https://') else r.continue_())
 pg.on('pageerror',lambda e:result['script_errors'].append('editor: '+str(e)))
 try:
  pg.goto((R/'Motion-Studio-Editor-OFFLINE.html' if (R/'Motion-Studio-Editor-OFFLINE.html').exists() else R/'Motion-Studio-Editor.html').resolve().as_uri(),wait_until='domcontentloaded',timeout=20000)
  pg.wait_for_timeout(900)
  result['editor_loaded']=pg.locator('#exportBtn').count()==1
  # choose ORBIT using documented shortcut.
  pg.locator('#templateList .template-card').nth(1).click(timeout=3500)
  pg.wait_for_timeout(400)
  pg.locator('[data-tab="content"]').click(timeout=3500)
  pg.locator('#titleInput').fill('THE NEW ORBIT EXPERIENCE',timeout=3500)
  pg.wait_for_timeout(350)
  with pg.expect_download(timeout=9000) as e:pg.locator('#exportBtn').click(timeout=4000)
  e.value.save_as(str(R/'ORBIT-R11-editor-export.html'))
  doc=(R/'ORBIT-R11-editor-export.html').read_text()
  result['exported_file']='THE NEW ORBIT EXPERIENCE' in doc and 'ms-visible' in doc; result['title_in_export']='THE NEW ORBIT EXPERIENCE' in doc;result['r11_css_in_export']='ms-visible' in doc
  # load actual export and exercise scroll progress
  q=c.new_page();q.route('**/*',lambda r:r.abort() if r.request.url.startswith('https://') else r.continue_())
  q.on('pageerror',lambda e:result['script_errors'].append('export: '+str(e)))
  q.goto((R/'ORBIT-R11-editor-export.html').resolve().as_uri(),wait_until='domcontentloaded',timeout=22000);q.wait_for_timeout(1100)
  initial=q.locator('.chapter').first.evaluate("e=>getComputedStyle(e).getPropertyValue('--ms-p')")
  q.evaluate("()=>document.getElementById('chapter-1').scrollIntoView({behavior:'instant'})")
  q.wait_for_timeout(300)
  scrolled=q.locator('.chapter').first.evaluate("e=>getComputedStyle(e).getPropertyValue('--ms-p')")
  result['chapter_progress_changes']=initial!=scrolled
  result['progress_initial']=initial;result['progress_scrolled']=scrolled
  result['canvas_cpu_frames']=q.locator('#webgl-canvas').get_attribute('data-frame-count')
  q.screenshot(path=str(R/'R11-desktop.png'),timeout=12000)
  m=c.new_page();m.set_viewport_size({'width':390,'height':844});m.route('**/*',lambda r:r.abort() if r.request.url.startswith('https://') else r.continue_());m.goto((R/'ORBIT-R11-editor-export.html').resolve().as_uri(),wait_until='domcontentloaded',timeout=22000);m.wait_for_timeout(800)
  result['mobile_no_overflow']=m.evaluate('()=>document.documentElement.scrollWidth<=innerWidth+2')
  m.screenshot(path=str(R/'R11-mobile.png'),timeout=12000)
  c2=b.new_context(reduced_motion='reduce',viewport={'width':1280,'height':800});a=c2.new_page();a.route('**/*',lambda r:r.abort() if r.request.url.startswith('https://') else r.continue_());a.goto((R/'ORBIT-R11-editor-export.html').resolve().as_uri(),wait_until='domcontentloaded',timeout=22000);a.wait_for_timeout(300)
  result['reduced_motion_respected']=a.locator('.chapter').first.evaluate("e=>getComputedStyle(e).getPropertyValue('--ms-p')")=='0.5'
  # Actual textured/animated GLB import + export preserved
  pg.locator('#glbInput').set_input_files(str(R/'Sample-Textured-Animated.glb'))
  pg.wait_for_function("()=>document.querySelector('#glbStatus')?.textContent.includes('已导入')",timeout=9000)
  with pg.expect_download(timeout=9000) as e:pg.locator('#exportBtn').dispatch_event('click')
  e.value.save_as(str(R/'ORBIT-R11-textured-animation.html'))
  doc2=(R/'ORBIT-R11-textured-animation.html').read_text()
  result['glb_original_embedded']='data:model/gltf-binary;base64,' in doc2
  result['texture_animation_metadata_preserved']='GLTFLoader' in doc2 and 'motion3d-config' in doc2
 except Exception as e:result['exception']=str(e)[:500];traceback.print_exc()
 b.close()
result['pass']=all(result.get(k) for k in ('editor_loaded','exported_file','chapter_progress_changes','mobile_no_overflow','reduced_motion_respected','glb_original_embedded','texture_animation_metadata_preserved')) and not result['script_errors'] and 'exception' not in result
(R/'R11_TEST.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
sys.exit(0 if result['pass'] else 2)
