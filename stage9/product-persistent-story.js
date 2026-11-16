// S4 persistent product model: ONE actual WebGL renderer across a full story.
// Original implementation; uses project's existing offline Three.js GLB assets.
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
(async()=>{
 const data=document.getElementById('motion-product-story-data');
 if(!data)return;
 const report={mode:'persistent-product-story',active:false,webgl2:false,loaded:false,
   canvasCount:0,sceneUuid:null,meshCount:0,frameCount:0,renderedPixels:0,
   sceneIndex:0,progress:0,modelSourceCount:0,cameraSamples:[],errors:[],
   reducedMotion:matchMedia('(prefers-reduced-motion:reduce)').matches};
 window.__motionProductStory=report;
 let config;
 try{config=JSON.parse(data.textContent||'{}');}catch(e){report.errors.push(String(e));return;}
 const model=config.glb;
 const sections=[...document.querySelectorAll('.page > .section')];
 if(!model||!sections.length){report.errors.push('No product GLB or story sections');return;}
 const modelBytes=new Uint8Array(Math.floor(model.length*.75));
 try{
   if(!/^[A-Za-z0-9+/=]+$/.test(model))throw Error('Invalid GLB payload');
   const raw=atob(model),binary=new Uint8Array(raw.length);
   for(let i=0;i<raw.length;i++)binary[i]=raw.charCodeAt(i);
   const canvas=document.createElement('canvas');
   canvas.id='motion-product-story-canvas';
   canvas.setAttribute('aria-label','Persistent 3D product presentation');
   canvas.style.cssText='position:fixed;inset:0;z-index:16;width:100vw;height:100vh;pointer-events:none;opacity:0;transition:opacity .2s';
   document.body.append(canvas);
   const renderer=new THREE.WebGLRenderer({canvas,alpha:true,antialias:true,powerPreference:'high-performance'});
   const gl=renderer.getContext();
   report.webgl2=gl instanceof WebGL2RenderingContext;
   renderer.outputColorSpace=THREE.SRGBColorSpace;
   renderer.toneMapping=THREE.ACESFilmicToneMapping;
   renderer.toneMappingExposure=1.04;
   const scene=new THREE.Scene();report.sceneUuid=scene.uuid;
   const camera=new THREE.PerspectiveCamera(38,1,.05,150);
   scene.add(new THREE.HemisphereLight(0xe8f4ff,0x222638,2.1));
   const key=new THREE.DirectionalLight(0xffdcc7,3.2);key.position.set(4,6,7);scene.add(key);
   const rim=new THREE.DirectionalLight(0xa9dcff,2.4);rim.position.set(-4,2,-5);scene.add(rim);
   const pmrem=new THREE.PMREMGenerator(renderer);
   const env=pmrem.fromScene(new RoomEnvironment(),.05);
   scene.environment=env.texture;pmrem.dispose();
   const loader=new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
   const asset=await new Promise((resolve,reject)=>loader.parse(binary.buffer,'',resolve,reject));
   const root=asset.scene;
   const bounds=new THREE.Box3().setFromObject(root);
   const center=bounds.getCenter(new THREE.Vector3()),size=bounds.getSize(new THREE.Vector3());
   const scale=2.6/Math.max(.001,size.x,size.y,size.z);
   root.position.sub(center).multiplyScalar(scale);root.scale.setScalar(scale);
   scene.add(root);root.traverse(x=>{if(x.isMesh)report.meshCount++});
   const mixer=asset.animations.length?new THREE.AnimationMixer(root):null;
   let duration=0;
   for(const clip of asset.animations){mixer.clipAction(clip).play();duration=Math.max(duration,clip.duration)}
   report.modelSourceCount=1;report.loaded=true;
   const clamp=x=>Math.max(0,Math.min(1,x));
   const smooth=x=>x*x*(3-2*x);
   const profile=[
      {x:0,y:0,z:6.2,yaw:-28,pitch:7,fov:38,spin:-.5},
      {x:0,y:0,z:4.5,yaw:15,pitch:0,fov:34,spin:.6},
      {x:-.15,y:.12,z:3.35,yaw:48,pitch:12,fov:35,spin:1.5},
      {x:0,y:0,z:4.1,yaw:125,pitch:-9,fov:37,spin:2.5},
      {x:0,y:0,z:5.7,yaw:330,pitch:4,fov:38,spin:3.5}
   ];
   const keys=sections.map((_,i)=>{
      const k=(config.cameras||[])[i];
      const base=profile[Math.min(i,profile.length-1)];
      if(!k||!k.advanced||!Array.isArray(k.path)||k.path.length!==3)return base;
      const m=k.path[1];
      return {...base,x:(m.x||0)/130,y:(m.y||0)/130,
       z:Math.max(2,Math.min(10,(m.zoom?520/m.zoom:base.z))),
       yaw:base.yaw+(m.tilt||0)*.6};
   });
   let anchors=[],scheduled=0,lastState=-1;
   function measure(){anchors=sections.map(el=>el.offsetTop+el.offsetHeight*.5);}
   function render(){
     scheduled=0;
     const focus=scrollY+innerHeight*.5;
     let ix=0;while(ix<anchors.length-2&&focus>anchors[ix+1])ix++;
     const a=anchors[ix],b=anchors[Math.min(ix+1,anchors.length-1)];
     let mix=ix===anchors.length-1?0:clamp((focus-a)/Math.max(1,b-a));
     if(report.reducedMotion)mix=mix<.5?0:1;
     const t=smooth(mix);
     const from=keys[ix],to=keys[Math.min(ix+1,keys.length-1)];
     const lerp=k=>from[k]+(to[k]-from[k])*t;
     const progress=clamp((focus-anchors[0])/Math.max(1,anchors.at(-1)-anchors[0]));
     camera.position.set(lerp('x'),lerp('y'),lerp('z'));
     camera.lookAt(0,0,0);camera.fov=lerp('fov');camera.updateProjectionMatrix();
     root.rotation.y=lerp('yaw')*Math.PI/180;
     root.rotation.x=lerp('pitch')*Math.PI/180;
     if(mixer&&duration)mixer.setTime(duration*progress);
     const visible=focus>=anchors[0]-innerHeight*.8&&focus<=anchors.at(-1)+innerHeight*.8;
     canvas.style.opacity=visible?'1':'0';report.active=visible;
     renderer.render(scene,camera);report.frameCount++;
     report.sceneIndex=ix;report.progress=progress;
     if(report.cameraSamples.length<120)report.cameraSamples.push({
       chapter:ix,blend:Number(t.toFixed(4)),distance:Number(camera.position.z.toFixed(3)),
       rotation:Number(root.rotation.y.toFixed(3)),progress:Number(progress.toFixed(3))});
     if(report.frameCount<=6&&report.webgl2){
       const x=Math.floor(gl.drawingBufferWidth*.5),y=Math.floor(gl.drawingBufferHeight*.5),pix=new Uint8Array(4);
       gl.readPixels(x,y,1,1,gl.RGBA,gl.UNSIGNED_BYTE,pix);
       if(pix[3]&&pix[0]+pix[1]+pix[2]>20)report.renderedPixels++;
     }
     if(ix!==lastState&&window.parent!==window){
       lastState=ix;window.parent.postMessage({type:'motion-studio-preview-state',chapter:ix,total:sections.length},'*');
     }
   }
   function request(){if(!scheduled)scheduled=requestAnimationFrame(render)}
   const resize=()=>{renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.5));
       renderer.setSize(innerWidth,innerHeight,false);camera.aspect=innerWidth/Math.max(1,innerHeight);
       camera.updateProjectionMatrix();measure();request()};
   window.addEventListener('scroll',request,{passive:true});
   window.addEventListener('resize',resize,{passive:true});
   window.addEventListener('message',event=>{
      if(event.source!==window.parent||event.data?.type!=='motion-studio-preview-goto')return;
      const chapter=event.data.chapter;
      if(Number.isInteger(chapter)&&chapter>=0&&chapter<sections.length)
        sections[chapter].scrollIntoView({behavior:'instant'});
   });
   document.addEventListener('visibilitychange',request);
   canvas.addEventListener('webglcontextlost',e=>{
     e.preventDefault();report.errors.push('WebGL context lost');
     report.active=false;canvas.style.opacity='0';
   });
   resize();
 }catch(err){report.errors.push(String(err?.stack||err));}
})();
