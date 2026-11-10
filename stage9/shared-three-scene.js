import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
(async()=>{
 const script=document.getElementById('motion-shared-scene-data');
 if(!script)return;
 let chapters;
 try{chapters=JSON.parse(script.textContent||'[]');}catch(e){return;}
 const sources=(chapters||[]).map((c,i)=>({...c,index:i})).filter(c=>c.id==='offline-glb-scene'&&c.glb&&c.glb.length>=32);
 if(sources.length<2)return;
 const diag={mode:'one-shared-three-scene',context:'software-or-hardware-unverified',canvasCount:0,webgl2:false,loadedModels:0,modelMeshCounts:[],modelIds:[],renderFrames:0,visiblePixels:0,drawSamples:0,drawTotalMs:0,cameraSamples:[],sceneUuid:null,contextLost:false,animationClips:0,error:null,remoteRequests:0,active:false,modelStates:[]};
 window.__motionSharedThree=diag;
 const canvas=document.createElement('canvas');
 canvas.id='motion-shared-three-canvas';
 canvas.setAttribute('aria-hidden','true');
 canvas.style.cssText='position:fixed;inset:0;width:100vw;height:100vh;z-index:7;pointer-events:none;opacity:0;transition:opacity .16s;display:block';
 document.body.appendChild(canvas);
 const contextLost=e=>{e.preventDefault();diag.contextLost=true;diag.active=false;canvas.style.opacity='0'};
 canvas.addEventListener('webglcontextlost',contextLost,false);
 let renderer;
 try{
   renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true,powerPreference:'high-performance'});
   diag.webgl2=renderer.getContext() instanceof WebGL2RenderingContext;
   diag.canvasCount=document.querySelectorAll('#motion-shared-three-canvas').length;
   renderer.setPixelRatio(Math.min(2,window.devicePixelRatio||1));
   renderer.outputColorSpace=THREE.SRGBColorSpace;
   renderer.toneMapping=THREE.ACESFilmicToneMapping;
   const scene=new THREE.Scene();diag.sceneUuid=scene.uuid;
   scene.add(new THREE.AmbientLight(0xffffff,1.4));
   const key=new THREE.DirectionalLight(0xffe9cc,3);key.position.set(4,4,6);scene.add(key);
   const rim=new THREE.DirectionalLight(0xa3bbff,2);rim.position.set(-4,2,-3);scene.add(rim);
   const camera=new THREE.PerspectiveCamera(42,1,.1,100);
   let records=[];
   const loader=new GLTFLoader();
   for(let k=0;k<sources.length;k++){
     const c=sources[k];
     if(!/^[A-Za-z0-9+/=]+$/.test(c.glb))throw Error('Invalid shared GLB base64');
     const raw=atob(c.glb),bytes=new Uint8Array(raw.length);
     for(let i=0;i<raw.length;i++)bytes[i]=raw.charCodeAt(i);
     const parsed=await new Promise((ok,no)=>loader.parse(bytes.buffer,'',ok,no));
     const root=parsed.scene;
     const bounds=new THREE.Box3().setFromObject(root),center=bounds.getCenter(new THREE.Vector3()),size=bounds.getSize(new THREE.Vector3());
     const scale=2.5/Math.max(size.x,size.y,size.z,.001);
     const worldX=k*3.2;
     root.position.sub(center).multiplyScalar(scale);
     root.position.x+=worldX;
     root.scale.multiplyScalar(scale);
     scene.add(root);
     const mixer=parsed.animations.length?new THREE.AnimationMixer(root):null;
     let duration=0;for(const clip of parsed.animations){mixer.clipAction(clip).play();duration=Math.max(duration,clip.duration)}
     diag.animationClips+=parsed.animations.length;
     let meshes=0;root.traverse(x=>{if(x.isMesh)meshes++});
     records.push({source:c,root,mixer,duration,worldX,meshes});
     diag.modelIds.push(c.index);diag.modelMeshCounts.push(meshes);
     diag.loadedModels++;
   }
   const sections=[...document.querySelectorAll('.section')];
   const anchors=records.map(r=>{
     const element=sections[r.source.index];
     if(!element)throw Error('Shared section is missing');
     return element;
   });
   const clamp=(a,lo,hi)=>Math.max(lo,Math.min(hi,a));
   const ease=t=>t*t*(3-2*t);
   const baseline=[];
   function updateAnchors(){
     for(let i=0;i<anchors.length;i++){
       const r=anchors[i].getBoundingClientRect();
       baseline[i]=r.top+window.scrollY+r.height*.5;
     }
   }
   updateAnchors();
   const lerp=(a,b,t)=>a+(b-a)*t;
   const isReduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
   const modelMix=(idx,blend)=>{
     const a=records[idx],b=records[idx+1]||a;
     for(let j=0;j<records.length;j++){
       const r=records[j],weight=j===idx?1-blend:j===idx+1?blend:0;
       // Preserve both models during transitions, never swap WebGL contexts.
       r.root.visible=weight>.003;
       r.root.traverse(o=>{if(!o.isMesh)return;const materials=Array.isArray(o.material)?o.material:[o.material];for(const m of materials){if(m){m.transparent=true;m.opacity=weight;m.depthWrite=weight>.95}}});
     }
   };
   const update=()=>{
     const focus=window.scrollY+window.innerHeight*.5;
     let ix=0;
     while(ix<baseline.length-2&&focus>baseline[ix+1])ix++;
     const a=baseline[ix],b=baseline[Math.min(ix+1,baseline.length-1)];
     const raw=ix===baseline.length-1?0:clamp((focus-a)/Math.max(1,b-a),0,1);
     const t=ease(raw);
     const x=lerp(records[ix].worldX,records[Math.min(ix+1,records.length-1)].worldX,t);
     // The same camera object moves between physical models across chapters.
     camera.position.set(x,0,5.5);camera.lookAt(x,0,0);
     modelMix(ix,t);
     const progress=clamp((focus-baseline[0])/Math.max(1,baseline.at(-1)-baseline[0]),0,1);
     for(const r of records)if(r.mixer&&r.duration)r.mixer.setTime(r.duration*progress);
     const near3d=focus>=baseline[0]-window.innerHeight*.55&&focus<=baseline.at(-1)+window.innerHeight*.55;
     canvas.style.opacity=near3d?'1':'0';
     diag.active=near3d;
     const start=performance.now();
     renderer.render(scene,camera);diag.renderFrames++;
     diag.drawTotalMs=Number((diag.drawTotalMs+performance.now()-start).toFixed(3));diag.drawSamples++;
     if(diag.cameraSamples.length<120)diag.cameraSamples.push({x:Number(camera.position.x.toFixed(4)),y:0,z:5.5,segment:ix,blend:Number(t.toFixed(4)),focus:Math.round(focus)});
     if(diag.renderFrames<=8){
       const gl=renderer.getContext(),w=gl.drawingBufferWidth,h=gl.drawingBufferHeight;
       const px=new Uint8Array(4);
       let hits=0;
       for(let y=1;y<=6;y++)for(let x=1;x<=6;x++){gl.readPixels(Math.floor(w*x/7),Math.floor(h*y/7),1,1,gl.RGBA,gl.UNSIGNED_BYTE,px);if(px[3]>0&&px[0]+px[1]+px[2]>25)hits++;}
       diag.visiblePixels=Math.max(diag.visiblePixels,hits);
     }
     return {focus,segment:ix,blend:t,x,progress,near3d};
   };
   const resize=()=>{renderer.setSize(Math.max(1,innerWidth),Math.max(1,innerHeight),false);camera.aspect=innerWidth/Math.max(1,innerHeight);camera.updateProjectionMatrix();updateAnchors();update()};
   addEventListener('resize',resize,{passive:true});
   addEventListener('scroll',update,{passive:true});
   resize();
   // Hide per-chapter 3D iframe only after shared real WebGL is active.
   for(const el of anchors){el.dataset.sharedThree='true';const iframe=el.querySelector('iframe');if(iframe){iframe.style.opacity='0';iframe.style.pointerEvents='none';}}
   diag.active=true;
   window.__motionSharedThreeControl={update,resize,anchors:()=>[...baseline],records:()=>records.length,dispose:()=>{canvas.remove();renderer.dispose();}};
 }catch(err){diag.error=String(err?.stack||err);canvas.remove();renderer?.dispose();}
})();