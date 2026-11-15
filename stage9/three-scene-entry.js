// Standalone GPU renderer for Stage 9 exported GLB sections; bundled by esbuild.
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
(async function bootMotionThree(){
  const host=document.querySelector('.viewport')||document.body;
  const source=document.getElementById('embedded-model')?.textContent?.trim()||'';
  const status={engine:'three',threeVersion:THREE.REVISION,webgl2:false,pbr:false,meshCount:0,materialCount:0,textureCount:0,animationClips:0,frames:0,visiblePixels:0,pixelDifference:0,animationMoved:false,animationRotationSamples:[],skinnedMeshCount:0,morphMeshCount:0,boneCount:0,morphInfluenceSamples:[],boneRotationSamples:[],animationClipNames:[],rendererName:null,renderWidth:0,renderHeight:0,drawSamples:0,drawTotalMs:0,drawMaxMs:0,error:null,progress:0,studioLighting:false,shadowEnabled:false,dragMoves:0,dragYaw:0,dragPitch:0,studioMeshes:0,modelTriangles:0,zoom:5.8,environmentReady:false,proceduralTextureCount:0,lightPreset:'warm',materialPreset:'original',cameraPreset:'hero',controlClicks:0,renderMsAvg:0,renderMsMax:0,estimatedFps:0,pausedFrames:0,visible:true,contextLost:false,reducedMotion:false,quality:'desktop',pixelRatio:1,frameBudgetMs:33.3,renderSamples:0};
  window.__motionThreeStatus=status;
  // Avoid allocating a throwaway WebGL2 context during feature detection.
  if(typeof WebGL2RenderingContext==='undefined'){
    status.error='WebGL2 unavailable: Canvas fallback remains active';return;
  }
  let renderer;
  const canvas=document.createElement('canvas');canvas.id='motion-three-webgl2';
  canvas.style.cssText='position:absolute;inset:0;width:100%;height:100%;z-index:5;pointer-events:auto;touch-action:pan-y;cursor:grab;opacity:0;transition:opacity .25s;';
  host.style.position='relative';host.appendChild(canvas);
  const reducedMotion=window.matchMedia('(prefers-reduced-motion: reduce)');
  status.reducedMotion=reducedMotion.matches;
  const isMobile=()=>Math.min(window.innerWidth||1200,host.clientWidth||1200)<600||
    (window.matchMedia('(pointer: coarse)').matches&&window.innerWidth<900);
  let running=true,visible=true,lastFrame=0;
  const visibility=new IntersectionObserver(items=>{
    visible=!!items[0]?.isIntersecting;status.visible=visible;
  },{threshold:0.01});
  visibility.observe(canvas);
  document.addEventListener('visibilitychange',()=>{if(document.hidden)lastFrame=0});
  canvas.addEventListener('webglcontextlost',e=>{
    e.preventDefault();status.contextLost=true;status.error='WebGL context lost: Canvas fallback remains active';
    running=false;canvas.style.opacity='0';
    document.documentElement.dataset.motion3dRenderer='fallback';
  });
  try{
    renderer=new THREE.WebGLRenderer({canvas,alpha:true,antialias:true,powerPreference:'high-performance'});
    const ctx=renderer.getContext();
    status.webgl2=typeof WebGL2RenderingContext!=='undefined'&&ctx instanceof WebGL2RenderingContext;
    status.rendererName=String(ctx.getParameter(ctx.RENDERER)||'unknown');
    renderer.outputColorSpace=THREE.SRGBColorSpace;
    renderer.toneMapping=THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure=1.05;
    renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
    status.shadowEnabled=true;
    const applyQuality=()=>{
      const mobile=isMobile();status.quality=mobile?'mobile':'desktop';
      const ratio=Math.min(window.devicePixelRatio||1,mobile?1:1.5);
      renderer.setPixelRatio(ratio);status.pixelRatio=ratio;
      key.shadow.mapSize.set(mobile?512:1024,mobile?512:1024);
      status.frameBudgetMs=mobile?50:33.3; // target, not a hardware FPS claim
    };
    renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,1.5));
    const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(36,1,.05,100);
    camera.position.set(0,0,5.8);
    // Original studio-light rig: large softboxes, warm key, cool rim and
    // a subtle receiving floor. No HDRI assets or external network requests.
    scene.add(new THREE.HemisphereLight(0xd9edff,0x202632,1.35));
    const key=new THREE.DirectionalLight(0xffdfc2,3.0);
    key.position.set(3.5,6,5);key.castShadow=true;
    key.shadow.mapSize.set(1024,1024);key.shadow.camera.left=-4;
    key.shadow.camera.right=4;key.shadow.camera.top=4;
    key.shadow.camera.bottom=-4;key.shadow.normalBias=.045;
    scene.add(key);
    const fill=new THREE.DirectionalLight(0xa9d9ff,1.65);fill.position.set(-5,1,2.5);scene.add(fill);
    const rim=new THREE.DirectionalLight(0xfff2da,2.0);rim.position.set(1.5,3,-5);scene.add(rim);
    const bounce=new THREE.PointLight(0xb3cfef,20,13,2);bounce.position.set(-2,-2,3);scene.add(bounce);
    status.studioLighting=true;
    // Original PMREM environment (generated locally, no external HDRI).
    const pmrem=new THREE.PMREMGenerator(renderer);
    const envTarget=pmrem.fromScene(new RoomEnvironment(),.06);
    scene.environment=envTarget.texture;
    pmrem.dispose();
    status.environmentReady=!!scene.environment;
    // Fine-grain original normal and roughness maps.
    function surfaceMap(normal){
      const layer=document.createElement('canvas');layer.width=layer.height=96;
      const ctx=layer.getContext('2d'),img=ctx.createImageData(96,96);
      for(let y=0;y<96;y++)for(let x=0;x<96;x++){
        const n=((x*73+y*151+x*y*17)%29)-14,i=(y*96+x)*4;
        img.data[i]=normal?128+n:226+n;
        img.data[i+1]=normal?128-n:226+n;
        img.data[i+2]=normal?248:226+n;img.data[i+3]=255;
      }
      ctx.putImageData(img,0,0);
      const map=new THREE.CanvasTexture(layer);
      map.wrapS=map.wrapT=THREE.RepeatWrapping;map.repeat.set(2,2);
      map.colorSpace=THREE.NoColorSpace;return map;
    }
    const grain=surfaceMap(true),roughnessTexture=surfaceMap(false);
    status.proceduralTextureCount=2;
    let object,mixer=null,duration=0,trackedNode=null,boneNode=null,morphNode=null;
    if(source){
      if(!/^[A-Za-z0-9+/=]+$/.test(source))throw Error('Invalid base64 GLB');
      const binary=atob(source),bytes=new Uint8Array(binary.length);
      for(let i=0;i<binary.length;i++)bytes[i]=binary.charCodeAt(i);
      const gltfLoader=new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
      const gltf=await new Promise((yes,no)=>gltfLoader.parse(bytes.buffer,'',yes,no));
      object=gltf.scene;
      object.traverse(node=>{
        if(node.isBone)status.boneCount++;if(!node.isMesh)return;status.meshCount++;if(node.isSkinnedMesh)status.skinnedMeshCount++;if(node.morphTargetInfluences?.length)status.morphMeshCount++;
        for(const mat of (Array.isArray(node.material)?node.material:[node.material])){
          if(!mat)continue;
          if(mat.isMeshStandardMaterial||mat.isMeshPhysicalMaterial)status.materialCount++;
          for(const f of ['map','normalMap','roughnessMap','metalnessMap','emissiveMap','aoMap']) if(mat[f]?.isTexture)status.textureCount++;
        }
      });
      object.traverse(node=>{
        if(!node.isMesh)return;
        node.castShadow=true;node.receiveShadow=true;
        const index=node.geometry?.index?.count||node.geometry?.getAttribute('position')?.count||0;
        status.modelTriangles+=Math.floor(index/3);
      });
      status.animationClips=gltf.animations.length;status.animationClipNames=gltf.animations.map(c=>c.name);
      boneNode=null;morphNode=null;object.traverse(n=>{if(n.isBone)boneNode=n;if(!morphNode&&n.isMesh&&n.morphTargetInfluences?.length)morphNode=n;});
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
    const pbrMaterials=[];
    object.traverse(node=>{
      if(!node.isMesh)return;
      for(const mat of (Array.isArray(node.material)?node.material:[node.material])){
        if(!mat?.isMeshStandardMaterial&&!mat?.isMeshPhysicalMaterial)continue;
        if(!pbrMaterials.includes(mat))pbrMaterials.push(mat);
        mat.envMapIntensity=1.45;
        if(!mat.normalMap)mat.normalMap=grain;
        if(!mat.roughnessMap)mat.roughnessMap=roughnessTexture;
        mat.normalScale?.set(.12,.12);
        mat.needsUpdate=true;
      }
    });
    status.textureCount+=status.proceduralTextureCount;
    // Shadow-catching circular display platform: intentionally beneath the
    // model, so it never blocks a user's view or intercepts pointer input.
    const plinth=new THREE.Mesh(new THREE.CylinderGeometry(1.58,1.66,.10,96),
      new THREE.MeshStandardMaterial({color:0x253139,metalness:.28,roughness:.53}));
    plinth.position.y=-1.65;plinth.receiveShadow=true;
    const accent=new THREE.Mesh(new THREE.TorusGeometry(1.59,.014,10,96),
      new THREE.MeshBasicMaterial({color:0xb2cbd2}));
    accent.rotation.x=Math.PI/2;accent.position.y=-1.585;
    const floor=new THREE.Mesh(new THREE.PlaneGeometry(12,12),
      new THREE.MeshStandardMaterial({color:0x101920,metalness:.02,roughness:.85,transparent:true,opacity:.78}));
    floor.rotation.x=-Math.PI/2;floor.position.y=-1.72;floor.receiveShadow=true;
    scene.add(plinth,accent,floor);status.studioMeshes=3;
    let dragYaw=0,dragPitch=0,dragging=false,lastX=0,lastY=0,zoom=5.8;
    canvas.addEventListener('pointerdown',e=>{
      if(e.button!==0)return;
      dragging=true;lastX=e.clientX;lastY=e.clientY;
      canvas.setPointerCapture?.(e.pointerId);canvas.style.cursor='grabbing';
    });
    canvas.addEventListener('pointermove',e=>{
      if(!dragging)return;
      const dx=e.clientX-lastX,dy=e.clientY-lastY;
      lastX=e.clientX;lastY=e.clientY;
      dragYaw+=dx*.009;dragPitch=THREE.MathUtils.clamp(dragPitch+dy*.006,-.65,.65);
      status.dragMoves++;status.dragYaw=dragYaw;status.dragPitch=dragPitch;
    });
    const stopDrag=()=>{dragging=false;canvas.style.cursor='grab'};
    canvas.addEventListener('pointerup',stopDrag);
    canvas.addEventListener('pointercancel',stopDrag);
    canvas.addEventListener('lostpointercapture',stopDrag);
    canvas.addEventListener('dblclick',()=>{dragYaw=0;dragPitch=0;zoom=5.8;status.dragYaw=0;status.dragPitch=0;status.zoom=zoom});
    canvas.addEventListener('wheel',e=>{
      if(!e.ctrlKey&&!e.metaKey)return; // never hijack normal page scroll
      e.preventDefault();zoom=THREE.MathUtils.clamp(zoom+e.deltaY*.004,4,8);
      camera.position.z=zoom;status.zoom=zoom;
    },{passive:false});
    const orient=()=>{object.rotation.y=progress*Math.PI*2+.25+dragYaw;object.rotation.x=dragPitch};
    // In-scene controls mutate the actual Three.js scene.
    const toolbar=document.createElement('div');
    toolbar.id='motion-r9-controls';
    toolbar.setAttribute('aria-label','3D studio controls');
    toolbar.style.cssText='position:absolute;top:12px;right:12px;z-index:9;display:flex;flex-wrap:wrap;max-width:255px;gap:5px;padding:9px;border:1px solid #ffffff33;border-radius:13px;background:#0a141bcc;backdrop-filter:blur(10px);pointer-events:auto';
    host.appendChild(toolbar);
    const preset=(label,fn)=>{
      const b=document.createElement('button');b.type='button';b.textContent=label;
      b.style.cssText='padding:6px 9px;border:1px solid #ffffff45;border-radius:7px;color:#eef6f7;background:#263743;cursor:pointer;font:600 10px system-ui';
      b.addEventListener('click',()=>{fn();status.controlClicks++});
      toolbar.appendChild(b);return b;
    };
    preset('Warm',()=>{key.color.set(0xffdfc2);fill.color.set(0xa9d9ff);renderer.toneMappingExposure=1.05;status.lightPreset='warm'});
    preset('Cool',()=>{key.color.set(0xbce4ff);fill.color.set(0xe0f0ff);renderer.toneMappingExposure=1.14;status.lightPreset='cool'});
    preset('Neutral',()=>{key.color.set(0xffffff);fill.color.set(0xe8ecff);renderer.toneMappingExposure=1;status.lightPreset='neutral'});
    const originalColors=pbrMaterials.map(mat=>mat.color.clone());
    preset('Original',()=>{pbrMaterials.forEach((mat,i)=>mat.color.copy(originalColors[i]));status.materialPreset='original'});
    preset('Graphite',()=>{pbrMaterials.forEach((mat,i)=>{if(i<2)mat.color.set(0x373f45)});status.materialPreset='graphite'});
    preset('Pearl',()=>{pbrMaterials.forEach((mat,i)=>{if(i<2)mat.color.set(0xd4d7d4)});status.materialPreset='pearl'});
    preset('Front',()=>{dragYaw=-.25;dragPitch=0;status.dragYaw=dragYaw;status.dragPitch=0;status.cameraPreset='front'});
    preset('Angle',()=>{dragYaw=.68;dragPitch=-.16;status.dragYaw=dragYaw;status.dragPitch=dragPitch;status.cameraPreset='angle'});
    preset('Detail',()=>{zoom=4.3;camera.position.z=zoom;status.zoom=zoom;status.cameraPreset='detail'});

    let progress=0;
    const mobileHint=document.createElement('p');
    mobileHint.id='motion-r11-hint';
    mobileHint.textContent='Drag to rotate · Double click to reset · Ctrl/⌘ + wheel to zoom';
    mobileHint.style.cssText='position:absolute;z-index:8;bottom:8px;left:12px;right:12px;margin:0;color:#e9f3f4;font:500 11px system-ui;pointer-events:none;text-shadow:0 1px 5px #07121a';
    host.appendChild(mobileHint);
    function recordDraw(start){
      const elapsed=performance.now()-start;
      status.drawSamples++;
      status.drawTotalMs=Number((status.drawTotalMs+elapsed).toFixed(3));
      status.drawMaxMs=Math.max(status.drawMaxMs,Number(elapsed.toFixed(3)));
      status.renderMsMax=status.drawMaxMs;
      status.renderMsAvg=Number((status.drawTotalMs/status.drawSamples).toFixed(3));
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
        if(boneNode){const q=boneNode.quaternion;const snap=[q.x,q.y,q.z,q.w].map(v=>Number(v.toFixed(5))).join(',');if(!status.boneRotationSamples.includes(snap))status.boneRotationSamples.push(snap);}
        if(morphNode){const snap=morphNode.morphTargetInfluences.map(v=>Number(v.toFixed(5))).join(',');if(!status.morphInfluenceSamples.includes(snap))status.morphInfluenceSamples.push(snap);}
      }
    }
    window.addEventListener('message',event=>{if(event.data?.type==='motion-studio-scroll'){changeProgress(event.data.progress);if(renderer){try{orient();const drawStarted=performance.now();renderer.render(scene,camera);recordDraw(drawStarted);status.frames++;}catch(error){status.error=String(error);}}}});
    const resize=()=>{
      const w=Math.max(1,host.clientWidth),h=Math.max(1,host.clientHeight);
      applyQuality();renderer.setSize(w,h,false);
      camera.aspect=w/h;camera.updateProjectionMatrix();
    };
    resize();window.addEventListener('resize',resize);
    function update(timestamp=performance.now()){
      if(!renderer||!running)return;
      if(!visible||document.hidden){
        status.pausedFrames++;lastFrame=0;
        requestAnimationFrame(update);return;
      }
      const minInterval=reducedMotion.matches?100:status.frameBudgetMs*.5;
      if(lastFrame&&timestamp-lastFrame<minInterval){
        requestAnimationFrame(update);return;
      }
      if(lastFrame&&timestamp>lastFrame){
        const instant=1000/(timestamp-lastFrame);
        status.estimatedFps=Number((status.estimatedFps*.86+instant*.14).toFixed(1));
      }
      lastFrame=timestamp;
      orient();
      try{
        const drawStarted=performance.now();renderer.render(scene,camera);recordDraw(drawStarted);status.frames++;
        status.renderSamples++;
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
  }catch(error){
    status.error=String(error?.stack||error);running=false;
    visibility.disconnect();canvas.remove();renderer?.dispose();
    document.documentElement.dataset.motion3dRenderer='fallback';
  }
})();