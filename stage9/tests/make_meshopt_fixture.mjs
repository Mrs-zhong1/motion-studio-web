import fs from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {dirname,resolve} from 'node:path';
import {MeshoptEncoder,MeshoptDecoder} from 'meshoptimizer';
const dir=dirname(fileURLToPath(import.meta.url));
await Promise.all([MeshoptEncoder.ready,MeshoptDecoder.ready]);
const vertices=new Float32Array([-1.0,-.8,0, 1.0,-.8,0, 0,1.0,0]);
const uncompressed=new Uint8Array(vertices.buffer);
const encoded=MeshoptEncoder.encodeGltfBuffer(uncompressed,3,12,'ATTRIBUTES');
const decoded=new Uint8Array(uncompressed.length);
MeshoptDecoder.decodeGltfBuffer(decoded,3,12,encoded,'ATTRIBUTES');
if(!Buffer.from(decoded).equals(Buffer.from(uncompressed)))throw Error('Encoder/decoder fixture mismatch');
const offset=36,padded=(encoded.length+3)&~3;
const bin=Buffer.alloc(offset+padded);
Buffer.from(encoded).copy(bin,offset);
const gltf={
 asset:{version:'2.0',generator:'Motion Studio true Meshopt encoder regression'},
 extensionsUsed:['EXT_meshopt_compression'],
 extensionsRequired:['EXT_meshopt_compression'],
 scene:0,scenes:[{nodes:[0]}],nodes:[{mesh:0}],
 buffers:[{byteLength:bin.length}],
 bufferViews:[{
   buffer:0,byteOffset:0,byteLength:36,byteStride:12,
   extensions:{EXT_meshopt_compression:{
     buffer:0,byteOffset:offset,byteLength:encoded.length,
     count:3,byteStride:12,mode:'ATTRIBUTES',filter:'NONE'
   }}
 }],
 accessors:[{bufferView:0,componentType:5126,count:3,type:'VEC3',min:[-1,-.8,0],max:[1,1,0]}],
 materials:[{pbrMetallicRoughness:{baseColorFactor:[.72,.39,.27,1],roughnessFactor:.35,metallicFactor:.2},doubleSided:true}],
 meshes:[{primitives:[{attributes:{POSITION:0},material:0,mode:4}]}]
};
let json=Buffer.from(JSON.stringify(gltf),'utf8');
json=Buffer.concat([json,Buffer.alloc((4-json.length%4)%4,0x20)]);
const out=Buffer.alloc(12+8+json.length+8+bin.length);
out.write('glTF',0);out.writeUInt32LE(2,4);out.writeUInt32LE(out.length,8);
out.writeUInt32LE(json.length,12);out.write('JSON',16);json.copy(out,20);
const at=20+json.length;out.writeUInt32LE(bin.length,at);out.write('BIN\0',at+4);bin.copy(out,at+8);
const target=resolve(dir,'../Sample-Meshopt-Compressed.glb');
await fs.writeFile(target,out);
console.log(JSON.stringify({fixture:target,bytes:out.length,encoded:encoded.length,decoded:decoded.length,extension:gltf.extensionsRequired[0]},null,2));
