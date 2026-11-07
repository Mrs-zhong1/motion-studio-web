#!/usr/bin/env python3
"""Evidence-driven release checklist. Never marks GPU/visual review done by assumption."""
from pathlib import Path
import json,sys
root=Path(__file__).resolve().parent
base=json.loads((root/'R11_RELEASE_GATE.json').read_text())
gpu=json.loads((root/'R12_GPU_TEST.json').read_text()) if (root/'R12_GPU_TEST.json').exists() else {}
bundle=root/'Motion-Studio-Editor-OFFLINE.html'
checks={
 'editor_baseline_tested':bool(base.get('r11_browser_suite')),
 'offline_bundle_created':bundle.exists() and bundle.stat().st_size>300000,
 'offline_webgl_pbr_glb_animation_tested':bool(gpu.get('webgl_pipeline_pass')),
 'offline_no_external_requests':bool(gpu.get('webgl_pipeline_pass') and gpu.get('no_external_requests')),
 'real_hardware_gpu_tested':bool(gpu.get('hardware_gpu_verified')), 
 'safari_real_device_tested':False,
 'reference_visual_review_accepted':False,
}
result={'checks':checks,'status':'PRODUCTION_READY' if all(checks.values()) else 'NOT_PRODUCTION_READY',
 'gpu_evidence_file':'R12_GPU_TEST.json' if gpu else None,
 'remaining':[k for k,v in checks.items() if not v]}
(root/'R12_RELEASE_GATE.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
if '--require-production' in sys.argv and result['status']!='PRODUCTION_READY':sys.exit(2)
