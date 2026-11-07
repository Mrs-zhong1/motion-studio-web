#!/usr/bin/env python3
"""Static safety checks for the source/bundler and the release workflow.
These are NOT a substitute for a browser GPU render test.
"""
from pathlib import Path
import re,base64,json,struct,subprocess,sys
root=Path(__file__).resolve().parent
editor=(root/'Motion-Studio-Editor.html').read_text()
module=(root/'three-pbr-module.js').read_text()
workflow=(root/'.github/workflows/build-web-offline.yml').read_text()
strict=(root/'test_gpu_pbr.py').read_text()
checks={}
m=re.search(r"const THREE_PBR_MODULE = '<script type=\"module\">' \+ atob\('([^']+)'\)",editor)
checks['online_renderer_module_matches_source']=bool(m and base64.b64decode(m.group(1)).decode()==module)
checks['no_silent_fake_pbr']=all(x in module for x in ('gltfMeshCount','textureMaps','physicalMaterials','animationTime'))
checks['strict_test_requires_real_textures_and_animation']=all(x in strict for x in ("out['texture_maps']>=1", "out['physical_materials']>=1", "out['animation_time']>0"))
checks['ci_step_id_matches_release_guard']=bool(re.search(r'(?m)^\s*id: gpu\s*$',workflow) and "steps.gpu.outcome != 'success'" in workflow and 'steps.webgl.outcome' not in workflow)
checks['ci_build_runs_actual_e2e']=bool('npm run build:offline' in workflow and 'python test_gpu_pbr.py' in workflow and 'continue-on-error: true' in workflow)
offline=root/'Motion-Studio-Editor-OFFLINE.html'
checks['offline_editor_content_valid_if_present']=not offline.exists() or (offline.stat().st_size>300000 and 'window.MotionThreeOfflineModule = null;' not in offline.read_text() and 'window.MotionThreeOfflineModule = ' in offline.read_text())
blob=(root/'Sample-Textured-Animated.glb').read_bytes()
chunk_size=struct.unpack_from('<I',blob,12)[0]
payload=json.loads(blob[20:20+chunk_size])
checks['sample_glb_contains_texture_and_animation']=bool(payload.get('images') and payload.get('textures') and payload.get('animations') and payload.get('meshes'))
checks['build_js_syntax']=subprocess.run(['node','--check',str(root/'build-offline-three.mjs')],capture_output=True).returncode==0
checks['source_js_parses_as_module']=subprocess.run(['node','--check','--input-type=module'],input=module,text=True,capture_output=True).returncode==0
result={'checks':checks,'pass':all(checks.values()),'production_ready':False,'important':'Contract checks do not prove WebGL/PBR image quality or GPU hardware.'}
(root/'R13_CONTRACT_TEST.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
sys.exit(0 if result['pass'] else 2)
