#!/usr/bin/env python3
from pathlib import Path
import re,json,sys
base=Path(__file__).parent
editor=base/'Motion-Studio-Editor.html'
html=editor.read_text()
results={
 'editor_exists':editor.is_file(),
 'offline_editor_single_file':len(html)>100000 and 'window.MotionTemplates' in html,
 'source_glb_fixture':(base/'Sample-Textured-Animated.glb').is_file(),
 'offline_build_script':(base/'build-offline-three.mjs').is_file(),
 'three_dependencies_pinned':json.loads((base/'package.json').read_text())['dependencies']['three']=='0.180.0',
 'r11_browser_suite':False,
 'standard_three_bundled':False,
 'gpu_pbr_verified':False,
 'safari_mobile_device_verified':False,
 'visual_reference_accepted':False,
}
test=base/'R11_TEST.json'
if test.exists():
 t=json.loads(test.read_text())
 results['r11_browser_suite']=all(t.get(x) for x in ('editor_loaded','exported_file','chapter_progress_changes','mobile_no_overflow','reduced_motion_respected','glb_original_embedded','texture_animation_metadata_preserved')) and not t['script_errors']
o=base/'Motion-Studio-Editor-OFFLINE.html'
if o.exists():
 s=o.read_text()
 results['standard_three_bundled']=len(s)>300000 and 'window.MotionThreeOfflineModule = null;' not in s and 'WebGLRenderer' in s
status='ENGINEERING_TESTED' if results['r11_browser_suite'] else 'ENGINEERING_TEST_FAILED'
if not results['standard_three_bundled']:status+=' / THREE_NOT_BUNDLED'
results['release_status']='NOT_PRODUCTION_READY' if not all([results['standard_three_bundled'],results['gpu_pbr_verified'],results['safari_mobile_device_verified'],results['visual_reference_accepted']]) else 'PRODUCTION_READY'
(base/'R11_RELEASE_GATE.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps(results,ensure_ascii=False,indent=2))
if '--require-production' in sys.argv and results['release_status']!='PRODUCTION_READY':sys.exit(2)
if not results['r11_browser_suite']:sys.exit(1)
