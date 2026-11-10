from pathlib import Path
import json,re
root=Path(__file__).resolve().parents[1]
source=(root/'Motion-Studio-Unified-Editor.html').read_text()
assert 'offline-glb-scene' in source and 'stage9LabPage' in source
entry=(root/'three-scene-entry.js').read_text()
assert "three/addons/loaders/GLTFLoader.js" in entry
assert 'MeshPhysicalMaterial' in entry and 'AnimationMixer' in entry
assert 'renderer.render(scene,camera)' in entry
out=root/'Motion-Studio-Stage9-THREE-OFFLINE.html'
assert out.exists(),'Offline HTML not built'
html=out.read_text()
assert len(html)>len(source)+100000
assert 'stage9ThreeEngine=atob("' in html
assert "return page.replace('</body>'" in html
manifest=json.loads((root/'BUILD_MANIFEST.json').read_text())
assert manifest['offline'] and manifest['engineBytes']>100000
assert (root/'THREE_LICENSE.txt').exists()
print('Stage9 real offline Three.js bundle: source and injected output accepted. GPU still requires separate browser test.')
