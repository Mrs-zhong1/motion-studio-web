#!/usr/bin/env python3
"""Contract test for the telemetry handoff between Three renderer and GPU e2e test.
No GPU or registry needed; this only validates data-extraction consistency.
"""
import json,re,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent
renderer=(P/'three-pbr-module.js').read_text()
test=(P/'test_gpu_pbr.py').read_text()
keys=['frameCount','gltfAnimations','textureMaps','physicalMaterials','animationTime','gltfMeshCount']
checks={key:{'written_by_renderer': bool(re.search(r'canvas\.dataset\.'+key+r'\s*=',renderer)),
             'read_by_test': bool(re.search(r'd\.'+key+r'\b',test))} for key in keys}
# Validate JS extract expression itself under node with an instrumented fake DOM.
match=re.search(r'info=q\.evaluate\("([^"]+)"\)',test)
if not match:
 checks['extraction_executes_in_node']=False
else:
 expression=match.group(1)
 js="const document={querySelector:(s)=>s==='#ms-three-canvas'?{dataset:{frameCount:'7',gltfAnimations:'1',textureMaps:'2',physicalMaterials:'2',animationTime:'0.75',gltfMeshCount:'3'}}:{textContent:'PBR',dataset:{renderer:'canvas'}}};const info=("+expression+")();console.log(JSON.stringify(info));"
 proc=subprocess.run(['node','--input-type=module','-e',js],capture_output=True,text=True)
 if proc.returncode==0:
  data=json.loads(proc.stdout)
  checks['extraction_executes_in_node']=(data['frames']==7 and data['animations']==1 and data['textures']==2 and data['physicalMaterials']==2 and data['animationTime']==0.75 and data['meshCount']==3)
 else: checks['extraction_executes_in_node']=False
out={'checks':checks,'passed':all((all(v.values()) if isinstance(v,dict) else v) for v in checks.values()),'scope':'instrumentation contract only; NO WebGL/PBR proof'}
(P/'R14_INSTRUMENTATION.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
raise SystemExit(0 if out['passed'] else 1)
