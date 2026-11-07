// Motion Studio standards renderer - Three.js r180 (progressive enhancement)
// Network imports only. Offline exported HTML uses the existing Canvas renderer.
import * as THREE from 'three';
import {GLTFLoader} from 'https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/loaders/GLTFLoader.js';
const root=document.querySelector('.template-orbit');
const legacy=document.getElementById('webgl-canvas');
const hud=document.getElementById('ms-render-kind');
const cfgTag=document.getElementById('motion3d-config');
const sceneConfig=cfgTag?JSON.parse(cfgTag.textContent):{};
const source=sceneConfig.source;
if(root&&legacy){
  let renderer;
  let model=null;
  const canvas=document.createElement('canvas');
  canvas.className='webgl-scene'; canvas.id='ms-three-canvas';
  canvas.setAttribute('aria-label','Three.js GLTF PBR model');
  canvas.style.cssText='opacity:0;transition:opacity .6s ease;z-index:3;touch-action:pan-y';
  let scene=new THREE.Scene();
  let camera=new THREE.PerspectiveCamera(36,1,.05,120);
  camera.position.set(0,0,5.5);
  let mixer=null;
  let orbitX=0,orbitY=0,dragging=false,startX=0,startY=0;
  const keys=window.matchMedia('(prefers-reduced-motion: reduce)');
  const clock=new THREE.Clock();
  try{
    renderer=new THREE.WebGLRenderer({canvas,alpha:true,antialias:true,powerPreference:'high-performance'});
    renderer.outputColorSpace=THREE.SRGBColorSpace;
    renderer.toneMapping=THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure=1.3;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));
    const hemi=new THREE.HemisphereLight(0xf3d9c6,0x302234,2.25);scene.add(hemi);
    const key=new THREE.DirectionalLight(0xffead1,4);key.position.set(3,5,5);scene.add(key);
    const fill=new THREE.DirectionalLight(0xd7a6e9,2.3);fill.position.set(-4,-1,-2);scene.add(fill);
    const rim=new THREE.PointLight(0xffa98f,32,15);rim.position.set(1,-2,3);scene.add(rim);
    const place=(g)=>{
      model=g;
      const bounds=new THREE.Box3().setFromObject(g);
      const size=bounds.getSize(new THREE.Vector3());
      const center=bounds.getCenter(new THREE.Vector3());
      // The box center includes the root's original translation. Scale the
      // (root position - world center) vector to recenter even off-origin GLBs.
      const max=Math.max(size.x,size.y,size.z,1e-3);
      const factor=2.8/max;
      g.position.sub(center).multiplyScalar(factor);
      g.scale.multiplyScalar(factor);
      scene.add(g);
    };
    if(source){
      if(!/^data:model\/gltf-binary;base64,[A-Za-z0-9+/=]+$/.test(source))throw Error('Invalid embedded GLB');
      const payload=atob(source.split(',')[1]);const bytes=new Uint8Array(payload.length);
      for(let i=0;i<payload.length;i++)bytes[i]=payload.charCodeAt(i);
      const gltf=await new Promise((resolve,reject)=>new GLTFLoader().parse(bytes.buffer,'',resolve,reject));
      place(gltf.scene);
      let meshCount=0, textureMaps=0, physicalMaterials=0;
      gltf.scene.traverse(node=>{
        if(!node.isMesh)return;
        meshCount++;
        for(const mat of (Array.isArray(node.material)?node.material:[node.material])){
          if(!mat)continue;
          if(mat.isMeshStandardMaterial||mat.isMeshPhysicalMaterial)physicalMaterials++;
          for(const field of ['map','normalMap','roughnessMap','metalnessMap','emissiveMap','aoMap']){
            if(mat[field]?.isTexture)textureMaps++;
          }
        }
      });
      canvas.dataset.gltfMeshCount=String(meshCount);
      canvas.dataset.textureMaps=String(textureMaps);
      canvas.dataset.physicalMaterials=String(physicalMaterials);
      if(gltf.animations.length){mixer=new THREE.AnimationMixer(gltf.scene);for(const clip of gltf.animations)mixer.clipAction(clip).play();}
      canvas.dataset.gltfAnimations=String(gltf.animations.length);
    }else{
      const mat=new THREE.MeshPhysicalMaterial({color:0xc79585,metalness:.9,roughness:.23,clearcoat:.75,clearcoatRoughness:.17,side:THREE.DoubleSide});
      place(new THREE.Mesh(new THREE.TorusKnotGeometry(1,.3,240,32),mat));
      canvas.dataset.gltfAnimations='0';canvas.dataset.textureMaps='0';canvas.dataset.gltfMeshCount='1';canvas.dataset.physicalMaterials='1';
    }
    legacy.parentElement.insertBefore(canvas,legacy.nextSibling);
    const pointer=(e)=>{if(!dragging)return;orbitY+=(e.clientX-startX)*.006;orbitX=Math.max(-1.1,Math.min(1.1,orbitX+(e.clientY-startY)*.006));startX=e.clientX;startY=e.clientY;};
    canvas.addEventListener('pointerdown',(e)=>{dragging=true;startX=e.clientX;startY=e.clientY;canvas.setPointerCapture(e.pointerId)});
    canvas.addEventListener('pointermove',pointer);
    canvas.addEventListener('pointerup',()=>dragging=false);
    canvas.addEventListener('pointercancel',()=>dragging=false);
    canvas.tabIndex=0;
    canvas.addEventListener('keydown',e=>{if(e.key==='r'||e.key==='R'){orbitX=orbitY=0;e.preventDefault()};if(e.key==='ArrowLeft'){orbitY-=.13;e.preventDefault()}if(e.key==='ArrowRight'){orbitY+=.13;e.preventDefault()}if(e.key==='ArrowUp'){orbitX-=.13;e.preventDefault()}if(e.key==='ArrowDown'){orbitX+=.13;e.preventDefault()}});
    const resize=()=>{const rect=canvas.getBoundingClientRect();const w=Math.max(1,Math.round(rect.width)),h=Math.max(1,Math.round(rect.height));renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();};
    resize();window.addEventListener('resize',resize,{passive:true});
    let frames=0;let live=true;
    canvas.addEventListener('webglcontextlost',()=>{live=false;canvas.style.opacity='0';legacy.style.visibility='visible';if(hud)hud.textContent='GPU context lost / Canvas fallback';});
    const tick=()=>{
      if(!live)return;
      requestAnimationFrame(tick);
      const dt=Math.min(clock.getDelta(),.1);
      const progress=window.scrollY/Math.max(1,document.documentElement.scrollHeight-innerHeight);
      if(mixer&&!keys.matches)mixer.update(dt);
      canvas.dataset.animationTime=String(mixer?mixer.time:0);
      if(model){model.rotation.y=orbitY+progress*2.4+(keys.matches?0:performance.now()*.00009);model.rotation.x=orbitX+progress*.55;}
      camera.position.z=5.5-progress*.75;
      renderer.render(scene,camera);
      frames++;canvas.dataset.frameCount=String(frames);
      if(frames===2){canvas.style.opacity='1';legacy.style.visibility='hidden';const backup=document.getElementById('webgl-fallback');if(backup)backup.hidden=true;if(hud)hud.textContent='THREE.JS r180 / PBR'+(mixer?' / ANIMATED':'');}
    };tick();
  }catch(err){
    if(renderer)renderer.dispose();
    canvas.remove();
    if(hud)hud.textContent='Canvas fallback (Three: '+String(err.message).slice(0,55)+')';
  }
}
