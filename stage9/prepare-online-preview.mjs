import {readFile,mkdir,writeFile,readdir,rm} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const root=dirname(fileURLToPath(import.meta.url));
const source=resolve(root,'Motion-Studio-Stage15-Meshopt-OFFLINE.html');
const dir=resolve(root,'online-review-parts');
const html=await readFile(source,'utf8');
if(!html.includes('const stage9ThreeEngineURL=')||
   !html.includes('const stage9SharedEngineURL=')||
   !html.includes('stage9LabPage(')||
   !html.includes('templateCatalog'))throw Error('R9 online package is incomplete');
await rm(dir,{recursive:true,force:true});await mkdir(dir,{recursive:true});
// Each chunk is valid UTF-8 independently. This also permits GitHub's small
// content APIs to transport one fully built browser-only page without loss.
const points=Array.from(html),parts=[];
for(let index=0;index<points.length;index+=140000){
 const name='part-'+String(parts.length).padStart(3,'0')+'.txt';
 const chunk=points.slice(index,index+140000).join('');
 await writeFile(resolve(dir,name),chunk,'utf8');
 parts.push(name);
}
const sha256=createHash('sha256').update(html).digest('hex');
const manifest={schema:'motion-studio-online-preview-v1',title:'R9 bundled Three.js web editor',
 source:'Stage15 OFFLINE HTML — real Three.js included; no external 3D engine',
 page:'review-preview.html',parts,characters:points.length,utf8Bytes:Buffer.byteLength(html),sha256,
 buildMethod:'node stage9/build-offline.mjs then node stage9/prepare-online-preview.mjs'};
await writeFile(resolve(dir,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
console.log('R9 online review parts',parts.length,'bytes',manifest.utf8Bytes,'sha256',sha256);
