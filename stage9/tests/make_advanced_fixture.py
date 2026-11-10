"""Generate a self-contained glTF 2.0 GLB for Stage9: 2-joint skin, morph target, 2 clips.
Standard-library only; deterministic (no Blender/network). All bufferViews are 4-byte aligned.
"""
from pathlib import Path
import json,struct,math
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT.parent/'Sample-Skinned-Morph-MultiClip.glb'
buf=bytearray()
views=[]
access=[]
def view(payload,target=None):
    while len(buf)%4:buf.append(0)
    off=len(buf);buf.extend(payload)
    obj={'buffer':0,'byteOffset':off,'byteLength':len(payload)}
    if target is not None:obj['target']=target
    views.append(obj)
    return len(views)-1
def acc(values,kind,component=5126,target=None,mins=None,maxs=None):
    formats={5126:'f',5123:'H',5121:'B'}
    fmt=formats[component]
    count_components={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[kind]
    assert len(values)%count_components==0
    n=len(values)//count_components
    raw=struct.pack('<'+fmt*len(values),*values)
    v=view(raw,target)
    a={'bufferView':v,'componentType':component,'count':n,'type':kind}
    if mins is not None:a['min']=mins
    if maxs is not None:a['max']=maxs
    access.append(a)
    return len(access)-1
# Large enough to survive low-resolution pixel sampling at 1100×460.
pos=acc([-0.8,-0.8,0,0.8,-0.8,0,0.8,0.8,0,-0.8,0.8,0],'VEC3',target=34962,mins=[-0.8,-0.8,0],maxs=[0.8,0.8,0])
norm=acc([0,0,1]*4,'VEC3',target=34962)
idx=acc([0,1,2,0,2,3],'SCALAR',5123,34963)
# Lower vertices bound to RootJoint; upper vertices bound to ArmJoint.
joints=acc([0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0],'VEC4',5121,34962)
weights=acc([1,0,0,0]*4,'VEC4',target=34962)
# Positive/negative delta on upper vertices to make morph highly visible.
morph=acc([0,0,0,0,0,0,0.75,0,0,-0.75,0,0],'VEC3',target=34962)
def inv_t(y):
    return [1,0,0,0,0,1,0,0,0,0,1,0,0,-y,0,1]
inverse=acc(inv_t(0)+inv_t(0.4),'MAT4')
times=acc([0.0,0.5,1.0],'SCALAR',mins=[0.0],maxs=[1.0])
rot=[]
for deg in [0,38,-32]:
    rad=math.radians(deg)/2
    rot += [0,0,math.sin(rad),math.cos(rad)]
rotation=acc(rot,'VEC4')
morph_anim=acc([0,1,0.25],'SCALAR')
model={
 'asset':{'version':'2.0','generator':'Motion Studio Stage9 deterministic fixture'},
 'scene':0,'scenes':[{'nodes':[0,1]}],
 'nodes':[
  {'name':'MorphSkinnedPanel','mesh':0,'skin':0,'weights':[0]},
  {'name':'RootJoint','children':[2]},
  {'name':'ArmJoint','translation':[0,0.4,0]}
 ],
 'meshes':[{'name':'SkinMorphPanel','weights':[0],'primitives':[{
  'attributes':{'POSITION':pos,'NORMAL':norm,'JOINTS_0':joints,'WEIGHTS_0':weights},
  'indices':idx,'material':0,'targets':[{'POSITION':morph}]}],
  'extras':{'targetNames':['WingFlex']}}],
 'skins':[{'name':'TwoJointSkin','joints':[1,2],'skeleton':1,'inverseBindMatrices':inverse}],
 'materials':[{'name':'PBR Copper','doubleSided':True,'pbrMetallicRoughness':{
  'baseColorFactor':[0.92,0.42,0.25,1],'metallicFactor':0.36,'roughnessFactor':0.38}}],
 'animations':[
  {'name':'BoneSwivel','samplers':[{'input':times,'output':rotation,'interpolation':'LINEAR'}],
   'channels':[{'sampler':0,'target':{'node':2,'path':'rotation'}}]},
  {'name':'MorphPulse','samplers':[{'input':times,'output':morph_anim,'interpolation':'LINEAR'}],
   'channels':[{'sampler':0,'target':{'node':0,'path':'weights'}}]}
 ],
 'buffers':[{'byteLength':len(buf)}],
 'bufferViews':views,'accessors':access
}
j=json.dumps(model,ensure_ascii=False,separators=(',',':')).encode('utf-8')
while len(j)%4:j+=b' '
while len(buf)%4:buf.append(0)
total=12+8+len(j)+8+len(buf)
blob=struct.pack('<4sII',b'glTF',2,total)+struct.pack('<I4s',len(j),b'JSON')+j+struct.pack('<I4s',len(buf),b'BIN\x00')+buf
assert len(blob)==total
DEST.write_bytes(blob)
# Parse the actual binary back to enforce determinism and basic GLB invariants.
binary=DEST.read_bytes()
assert binary[:4]==b'glTF' and struct.unpack_from('<I',binary,8)[0]==len(binary)
length,typ=struct.unpack_from('<I4s',binary,12)
assert typ==b'JSON'
parsed=json.loads(binary[20:20+length])
assert len(parsed['skins'])==1 and len(parsed['animations'])==2
assert parsed['meshes'][0]['primitives'][0]['targets']
print(json.dumps({'fixture':str(DEST),'bytes':len(binary),'joints':2,'morphTargets':1,'clips':[a['name'] for a in parsed['animations']]}))
