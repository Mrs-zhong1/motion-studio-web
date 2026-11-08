import {readFile,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {build} from 'esbuild';
const dir=resolve(new URL('.',import.meta.url).pathname);
let src=await readFile(resolve(dir,'three-pbr-module.js'),'utf8');
const source="https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/loaders/GLTFLoader.js";
if(!src.includes(source))throw Error('Unexpected Three.js module source: GLTFLoader path differs');
src=src.replace(source,'three/addons/loaders/GLTFLoader.js');
const result=await build({
  stdin:{contents:src,resolveDir:dir,sourcefile:'motion-three-pbr-offline.js',loader:'js'},
  bundle:true,format:'esm',platform:'browser',target:['es2022'],minify:true,write:false,
  legalComments:'inline',logLevel:'warning',
});
const moduleCode=result.outputFiles[0].text;
if(moduleCode.length<100000||/from\s*['"]https?:/.test(moduleCode)||/import\s*\(\s*['"]https?:/.test(moduleCode))throw Error('Incomplete or externally dependent Three.js bundle');
// Escaping '<' inside JSON prevents terminating the editor <script> unexpectedly.
const safeLiteral=JSON.stringify(moduleCode).replace(/</g,'\\u003c');
const original=await readFile(resolve(dir,'Motion-Studio-Editor.html'),'utf8');
if(!moduleCode.includes('gltfMeshCount')||!moduleCode.includes('textureMaps')||!moduleCode.includes('animationTime'))throw Error('Three renderer instrumentation missing; cannot run strict acceptance');
const needle='window.MotionThreeOfflineModule = null;';
if(!original.includes(needle))throw Error('Editor offline injection point not found');
const output=original.replace(needle,()=> 'window.MotionThreeOfflineModule = '+safeLiteral+';');
const target=resolve(dir,'Motion-Studio-Editor-OFFLINE.html');
await writeFile(target,output);
await writeFile(resolve(dir,'THIRD_PARTY_THREE_LICENSE.txt'),await readFile(resolve(dir,'node_modules/three/LICENSE'),'utf8'));
await writeFile(resolve(dir,'three-bundle-stats.json'),JSON.stringify({threeVersion:'0.180.0',sourceBytes:moduleCode.length,htmlBytes:Buffer.byteLength(output),built:true},null,2));
console.log('Built:',target,'Three module bytes:',moduleCode.length,'HTML bytes:',Buffer.byteLength(output));
console.log('This is not a GPU visual verification. Open the HTML on a WebGL-enabled browser and run the visual tests.');
