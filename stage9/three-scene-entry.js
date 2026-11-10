// Standalone GPU renderer for Stage 9 exported GLB sections; bundled by esbuild.
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
(async function bootMotionThree(){
  const host=document.querySelector('.viewport')||document.body;
  const source=document.getElementById('embedded-model')?.textContent?.trim()||'';
  const status={engine:'three',threeVersion:THREE.REVISION,webgl2:false,pbr:false,meshCount:0,materialCount:0,textureCount:0,animationClips:0,frames:0,visiblePixels:0,pixelDifference:0,animationMoved:false,animationRotationSamples:[],rendererName:null,renderWidth:0,renderHeight:0,drawSamples:0,drawTotalMs:0,drawMaxMs:0,error:null,progress:0};
  window.__motionThreeStatus=status;
  let gl;
  try {gl=document.createElement('canvas').getContext('webgl2');}catch(e){}
  if(!gl){status.error='WebGL2 unavailable: Canvas fallback remains active';return;}
  let renderer;
  const canvas=document.createElement('canvas');canvas.id='motion-three-webgl2';
  canvas.style.cssText='position:absolute;inset:0;width:100%;height:100%;z-index:5;pointer-events:none;opacity:0;transition:opacity .25s;';
  host.style.position='relative';host.appendChild(canvas);
  try{
    renderer=new THREE.WebGLRenderer({canvas,alpha:true,antialias:true,powerPreference:'high-performance'});
    const ctx=renderer.getContext();
    status.webgl2=typeof WebGL2RenderingContext!=='undefined'&&ctx instanceof WebGL2RenderingContext;
    status.rendererName=String(ctx.getParameter(ctx.RENDERER)||'unknown');
    renderer.outputColorSpace=THREE.SRGBColorSpace;
    renderer.toneMapping=THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure=1.15;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));
    const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(36,1,.05,100);
    camera.position.set(0,0,5.8);
    scene.add(new THREE.AmbientLight(0xffffff,1.25));
    const key=new THREE.DirectionalLight(0xffebda,3.4);key.position.set(4,5,6);scene.add(key);
    const fill=new THREE.DirectionalLight(0x9fbaff,2);fill.position.set(-4,1,-3);scene.add(fill);
    let object,mixer=null,duration=0,trackedNode=null;
    if(source){
      if(!/^[A-Za-z0-9+/=]+$/.test(source))throw Error('Invalid base64 GLB');
      const binary=atob(source),bytes=new Uint8Array(binary.length);
      for(let i=0;i<binary.length;i++)bytes[i]=binary.charCodeAt(i);
      const gltf=await new Promise((yes,no)=>new GLTFLoader().parse(bytes.buffer,'',yes,no));
      object=gltf.scene;
      object.traverse(node=>{
        if(!node.isMesh)return;status.meshCount++;
        for(const mat of (Array.isArray(node.material)?node.material:[node.material])){
          if(!mat)continue;
          if(mat.isMeshStandardMaterial||mat.isMeshPhysicalMaterial)status.materialCount++;
          for(const f of ['map','normalMap','roughnessMap','metalnessMap','emissiveMap','aoMap']) if(mat[f]?.isTexture)status.textureCount++;
        }
      });
      status.animationClips=gltf.animations.length;
      if(gltf.animations.length){
        trackedNode=object.getObjectByProperty('isMesh',true)||object.children[0]||object;
        mixer=new THREE.AnimationMixer(object);
        for(const clip of gltf.animations){mixer.clipAction(clip).play();duration=Math.max(duration,clip.duration);}
      }
    }else {
      object=new THREE.Mesh(new THREE.TorusKnotGeometry(.85,.24,160,24),new THREE.MeshPhysicalMaterial({color:0xc49d87,metalness:.8,roughness:.21,clearcoat:.65}));
      status.meshCount=1;status.materialCount=1;
    }
    const bounds=new THREE.Box3().setFromObject(object),center=bounds.getCenter(new THREE.Vector3()),size=bounds.getSize(new THREE.Vector3());
    const scale=2.6/Math.max(size.x,size.y,size.z,.0001);
    object.position.sub(center).multiplyScalar(scale);object.scale.multiplyScalar(scale);
    scene.add(object);status.pbr=status.materialCount>0;
    let progress=0;
    function recordDraw(start){
      const elapsed=performance.now()-start;
      status.drawSamples++;
      status.drawTotalMs=Number((status.drawTotalMs+elapsed).toFixed(3));
      status.drawMaxMs=Math.max(status.drawMaxMs,Number(elapsed.toFixed(3)));
    }
    function changeProgress(p){
      progress=Math.min(1,Math.max(0,Number(p)||0));status.progress=progress;
      if(mixer&&duration){
        mixer.setTime(progress*duration);
        if(trackedNode){
          const q=trackedNode.quaternion;
          const snap=[q.x,q.y,q.z,q.w].map(v=>Number(v.toFixed(5))).join(',');
          if(!status.animationRotationSamples.includes(snap))status.animationRotationSamples.push(snap);
          status.animationMoved=status.animationRotationSamples.length>1;
        }
      }
    }
    window.addEventListener('message',event=>{if(event.data?.type==='motion-studio-scroll'){changeProgress(event.data.progress);if(renderer){try{object.rotation.y=progress*Math.PI*2+.25;const drawStarted=performance.now();renderer.render(scene,camera);recordDraw(drawStarted);status.frames++;}catch(error){status.error=String(error);}}}});
    const resize=()=>{const w=Math.max(1,host.clientWidth),h=Math.max(1,host.clientHeight);renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();};
    resize();window.addEventListener('resize',resize);
    function update(){
      if(!renderer)return;
      object.rotation.y=progress*Math.PI*2+.25;
      try{
        const drawStarted=performance.now();renderer.render(scene,camera);recordDraw(drawStarted);status.frames++;
        if(status.frames<=5||status.frames%30===0){
          const g=renderer.getContext(),w=g.drawingBufferWidth,h=g.drawingBufferHeight;
          status.renderWidth=w;status.renderHeight=h;let visible=0,spread=0,last=-1;
          for(let py=1;py<=8;py++)for(let px=1;px<=8;px++){
            const sample=new Uint8Array(4);
            g.readPixels(Math.floor(w*px/9),Math.floor(h*py/9),1,1,g.RGBA,g.UNSIGNED_BYTE,sample);
            const rgb=sample[0]+sample[1]+sample[2];
            if(sample[3]>0&&rgb>15)visible++;
            if(last>=0)spread+=Math.abs(rgb-last);last=rgb;
          }
          status.visiblePixels=Math.max(status.visiblePixels,visible);
          status.pixelDifference=Math.max(status.pixelDifference,spread);
        }
        if(status.frames===1){canvas.style.opacity='1';document.documentElement.dataset.motion3dRenderer='three-webgl2';}
      }catch(error){status.error=String(error);canvas.style.opacity='0';renderer.dispose();renderer=null;return;}
      requestAnimationFrame(update);
    }
    update();
  }catch(error){status.error=String(error?.stack||error);canvas.remove();renderer?.dispose();}
})();