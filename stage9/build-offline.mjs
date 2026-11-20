import {readFile,writeFile} from 'node:fs/promises';
import {build,transform} from 'esbuild';
import {fileURLToPath} from 'node:url';
import {dirname,resolve} from 'node:path';
import {injectOfflineEngine} from './inject-offline-engine.mjs';
import {addCameraEditorStage10} from './stage10-camera-editor.mjs';
import {addCameraEditorStage11} from './stage11-camera-path.mjs';
import {addCameraEditorStage12} from './stage12-camera-editor.mjs';
import {bundleChapterPhotos} from './bundle-chapter-photos.mjs';
import {loadAIChapterAssets} from './ai-chapter-assets.mjs';
import {applyVisualRefinement} from './visual-refinement-r22.mjs';
import {applyStoryArtDirection} from './story-art-direction-r23.mjs';
import {injectR30CinematicTrial} from './r30-cinematic-trial.mjs';
import {applyR31StoryContinuity} from './r31-cinematic-continuity.mjs';
import {injectR36Pilot} from './r36-unified-stage-pilots.mjs';
import {applyR37StoryDirector} from './r37-story-director.mjs';
import {applyR38EightDirectors} from './r38-eight-art-directions.mjs';
import {injectR39Film} from './r39-cinematic-timeline.mjs';
import {injectR40Product} from './r40-product-lab.mjs';
import {applyR41PreviewFirst} from './r41-preview-first-layout.mjs';
import {injectR42Editorial} from './r42-editorial-story-spreads.mjs';
import {applyR43TemplatePilots} from './r43-immersive-template-pilots.mjs';
import {applyR44TemplateExperience} from './r44-single-canvas-preview.mjs';
import {applyR45TemplateComposition} from './r45-scene-composition.mjs';
import {applyR46ResponsiveAccessibility} from './r46-responsive-accessibility.mjs';
const root=dirname(fileURLToPath(import.meta.url));
const result=await build({entryPoints:[resolve(root,'three-scene-entry.js')],bundle:true,platform:'browser',format:'iife',target:'es2022',minify:true,write:false,legalComments:'inline'});
const engine=result.outputFiles[0].text;
if(engine.length<100000||/\bimport\s*\(/.test(engine))throw Error('Three.js bundle incomplete or has runtime dynamic imports');
const sharedBuild=await build({entryPoints:[resolve(root,'shared-three-scene.js')],bundle:true,platform:'browser',format:'iife',target:'es2022',minify:true,write:false,legalComments:'inline'});
const sharedEngine=sharedBuild.outputFiles[0].text;
if(sharedEngine.length<100000||/\bimport\s*\(/.test(sharedEngine))throw Error('Shared Three.js build is incomplete');
const thumbnailIds=['editorial','product-3d','cinematic','architecture','agency','fashion','gallery','saas'];
const thumbnailEntries=await Promise.all(thumbnailIds.map(async id=>[id,'data:image/jpeg;base64,'+await readFile(resolve(root,'template-thumbnails',id+'.jpg'),'base64')]));
let thumbnailData=JSON.stringify(Object.fromEntries(thumbnailEntries));
const source=await readFile(resolve(root,'Motion-Studio-Unified-Editor.html'),'utf8');
const thumbnailPattern=/const templateThumbnailImages=\{[\s\S]*?\};/;
if(!thumbnailPattern.test(source))throw Error('Template thumbnail declaration missing');
let injected=source;
const aiChapterPhotos=await loadAIChapterAssets(root,{required:process.env.MOTION_REQUIRE_AI_ASSETS==='1'});
const chapterPhotos=aiChapterPhotos || await bundleChapterPhotos(source,root);
if(aiChapterPhotos)thumbnailData=JSON.stringify(Object.fromEntries(thumbnailIds.map(id=>[id,aiChapterPhotos.data[id][0].media])));
injected=injected.replace(thumbnailPattern,'const templateThumbnailImages='+thumbnailData+';');
if(!injected.includes('const templateOfflinePhotoBundles={};'))throw Error('Offline photo bundle injection anchor missing');
injected=injected.replace('const templateOfflinePhotoBundles={};','const templateOfflinePhotoBundles='+JSON.stringify(chapterPhotos.data)+';');
injected=injected.replace(/const templateExtraPhotos=\{[\s\S]*?\};/,'const templateExtraPhotos={};');
const editor=applyR46ResponsiveAccessibility(applyR45TemplateComposition(applyR44TemplateExperience(applyR43TemplatePilots(injectR42Editorial(applyR41PreviewFirst(injectR40Product(injectR39Film(applyR38EightDirectors(applyR37StoryDirector(injectR36Pilot(applyR31StoryContinuity(injectR30CinematicTrial(applyStoryArtDirection(applyVisualRefinement(addCameraEditorStage12(addCameraEditorStage11(addCameraEditorStage10(injected))))))))))))))))));
let output=injectOfflineEngine(editor,engine);
const sharedUrl='const stage9SharedEngineURL="data:text/javascript;base64,'+Buffer.from(sharedEngine,'utf8').toString('base64')+'";\n';
if(!output.includes('const stage9ThreeEngineURL='))throw Error('Existing Stage9 renderer injection missing');
output=output.replace('const stage9ThreeEngineURL=',sharedUrl+'const stage9ThreeEngineURL=');

// Parse the exact inline-script payloads produced by the HTML parser before
// publishing build artifacts. This catches premature </script> termination
// and malformed template literals at their originating script index.
const inlineScriptPattern=/<script\b([^>]*)>([\s\S]*?)<\/script\s*>/gi;
let inlineScriptMatch,inlineScriptIndex=0;
while((inlineScriptMatch=inlineScriptPattern.exec(output))){
 const attrs=inlineScriptMatch[1],body=inlineScriptMatch[2];
 const isExternal=/\bsrc\s*=/i.test(attrs);
 const type=(attrs.match(/\btype\s*=\s*["']?([^\s"'>]+)/i)||[])[1]||'text/javascript';
 if(isExternal||!/(?:java|ecma)script/i.test(type)) {inlineScriptIndex++;continue;}
 try { await transform(body,{loader:'js',target:'es2022'}); }
 catch(error) {
  const detail=error.errors?.[0];
  const location=detail?.location?('line '+(detail.location.line||'?')+', column '+(detail.location.column||'?')+' '+(detail.text||'')):String(error.stack||error).split('\n').slice(0,3).join(' | ');
  throw new Error('Generated inline script syntax failure at index '+inlineScriptIndex+
   ' (id '+((attrs.match(/\bid\s*=\s*["']([^"']+)/i)||[])[1]||'none')+
   ', '+body.length+' chars): '+error.message+'; '+location);
 }
 inlineScriptIndex++;
}
console.log('Validated generated executable inline scripts',inlineScriptIndex);
await writeFile(resolve(root,'Motion-Studio-Stage9-THREE-OFFLINE.html'),output);
await writeFile(resolve(root,'Motion-Studio-Stage10-Camera-Editor-OFFLINE.html'),output);
await writeFile(resolve(root,'Motion-Studio-Stage11-Timeline-OFFLINE.html'),output);
await writeFile(resolve(root,'Motion-Studio-Stage12-Spatial-Gizmo-OFFLINE.html'),output);
await writeFile(resolve(root,'Motion-Studio-Stage13-Bezier-OFFLINE.html'),output);
await writeFile(resolve(root,'Motion-Studio-Stage14-Stability-OFFLINE.html'),output);
await writeFile(resolve(root,'Motion-Studio-Stage15-Meshopt-OFFLINE.html'),output);
await writeFile(resolve(root,'THREE_LICENSE.txt'),await readFile(resolve(root,'node_modules/three/LICENSE'),'utf8'));
await writeFile(resolve(root,'BUILD_MANIFEST.json'),JSON.stringify({three:'0.180.0',engineBytes:engine.length,sharedEngineBytes:sharedEngine.length,editorBytes:Buffer.byteLength(output),photoBundle:chapterPhotos.audit,aiOriginalMedia:!!aiChapterPhotos,offline:true,source:'Motion Studio Stage9-15, real offline MeshoptDecoder and 4MB GLB validation',releasePolicy:'web-browser-matrix',gpuAcceptanceRequired:false,gpuTested:false,macHardwareGpuOptional:true,requiredChecks:['web-product-e2e','offline-export','cross-browser-acceptance','deployment-smoke'],releaseAccepted:false},null,2));
console.log('Stage9 genuine offline Three.js bundle',engine.length,Buffer.byteLength(output));
console.log('R15 offline actual photo bundle inventory',JSON.stringify(chapterPhotos.audit));
