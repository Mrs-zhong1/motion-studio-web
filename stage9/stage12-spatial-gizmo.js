// Stage 12: actual Three.js spatial trajectory / gizmo, reusing shared Scene and Renderer.
// Only enters edit mode inside editor preview after an explicit parent-window message.
import * as THREE from 'three';
import {normalizeCameraPath11,evaluateCameraPath11} from './stage11-camera-curve.js';
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
export function installStage12Gizmo({scene,renderer,canvas,records,diag,render}){
 const group=new THREE.Group();
 group.name='Stage12SpatialTrajectoryGizmo';
 group.visible=false;
 scene.add(group);
 const handles=[],segments=[],axisHelpers=[];
 const overview=new THREE.PerspectiveCamera(47,1,.1,150);
 const raycaster=new THREE.Raycaster();
 const pointer=new THREE.Vector2();
 const colors={x:0xe87575,y:0x82d7a1,z:0x8bb9f4};
 let enabled=false,axis='x',view='front',targetIndex=0,drag=null,selection=0;
 const data={mode:false,view,axis,handleCount:0,dragCount:0,patchCount:0,trajectoryPoints:0,selected:0,sceneId:diag.sceneUuid,rendererShared:true,handleScreen:[],axisArrowsCount:0};
 window.__motionStage12Gizmo=data;
 function clear(){
   for(const h of handles){group.remove(h);h.geometry.dispose();h.material.dispose()}
   for(const line of segments){group.remove(line);line.geometry.dispose();line.material.dispose()}
   for(const a of axisHelpers){group.remove(a);for(const obj of [a.line,a.cone]){obj.geometry?.dispose();obj.material?.dispose();}}
   handles.length=0;segments.length=0;axisHelpers.length=0;
 }
 function keyWorld(index,k){
   const a=records[index],b=records[Math.min(index+1,records.length-1)];
   const t=k.at/100;
   return new THREE.Vector3(THREE.MathUtils.lerp(a.worldX,b.worldX,t*t*(3-2*t))+k.x,k.y,k.z);
 }
 const chooseCamera=()=>{
   const a=records[targetIndex],b=records[Math.min(targetIndex+1,records.length-1)];
   const centerX=(a.worldX+b.worldX)/2;
   if(view==='top')overview.position.set(centerX,18,6);
   else if(view==='side')overview.position.set(centerX+18,4,6);
   else overview.position.set(centerX,1,22);
   overview.lookAt(centerX,0,5);
   overview.aspect=canvas.width/Math.max(1,canvas.height);
   overview.updateProjectionMatrix();
 };
 function rebuild(){
   clear();
   const path=normalizeCameraPath11(records[targetIndex]?.source?.cameraPath11);
   if(path.length<2){data.handleCount=0;return}
   const points=[];
   for(let at=0;at<=100;at+=2){
     const value=evaluateCameraPath11(path,at);if(value)points.push(keyWorld(targetIndex,{...value,at}));
   }
   const geometry=new THREE.BufferGeometry().setFromPoints(points);
   const material=new THREE.LineBasicMaterial({color:0xd7f093,depthTest:false,transparent:true,opacity:.95});
   const line=new THREE.Line(geometry,material);line.renderOrder=8;group.add(line);segments.push(line);
   for(let i=0;i<path.length;i++){
     const pos=keyWorld(targetIndex,path[i]);
     const handle=new THREE.Mesh(
       new THREE.SphereGeometry(.22,16,12),
       new THREE.MeshBasicMaterial({color:i===selection?0xffe2a3:0x82ccef,depthTest:false,depthWrite:false})
     );
     handle.position.copy(pos);handle.userData.keyframeIndex=i;
     handle.renderOrder=9;group.add(handle);handles.push(handle);
   }
   const origin=handles[Math.min(selection,handles.length-1)]?.position;
   if(origin){
     const axes=[['x',new THREE.Vector3(1,0,0)],['y',new THREE.Vector3(0,1,0)],['z',new THREE.Vector3(0,0,1)]];
     for(const [name,dir] of axes){
       const arrow=new THREE.ArrowHelper(dir,origin,.85,colors[name],.2,.12);
       for(const obj of [arrow.line,arrow.cone]){
         if(obj.material){obj.material.depthTest=false;obj.material.depthWrite=false}
         obj.renderOrder=10;
       }
       group.add(arrow);axisHelpers.push(arrow);
     }
   }
   data.axisArrowsCount=axisHelpers.length;
   overview.updateMatrixWorld();
   const rect=canvas.getBoundingClientRect();
   data.handleScreen=handles.map((h,i)=>{const v=h.position.clone().project(overview);return {index:i,x:(v.x+1)*rect.width/2,y:(1-v.y)*rect.height/2}});
   data.handleCount=handles.length;data.trajectoryPoints=points.length;data.selected=selection;
 }
 function emitChange(){
   const rec=records[targetIndex];
   diag.stage11PathCounts=records.map(r=>r.source.cameraPath11.length);
   data.patchCount++;
   if(window.parent&&window.parent!==window)window.parent.postMessage({
     type:'motion-stage12-gizmo-change',uid:rec.source.uid,path:rec.source.cameraPath11,
     index:selection,axis,view
   },'*');
 }
 function onDown(e){
   if(!enabled||e.button!==0)return;
   const rect=canvas.getBoundingClientRect();
   pointer.x=((e.clientX-rect.left)/rect.width)*2-1;
   pointer.y=-((e.clientY-rect.top)/rect.height)*2+1;
   raycaster.setFromCamera(pointer,overview);
   const found=raycaster.intersectObjects(handles,false)[0];
   if(!found)return;
   selection=found.object.userData.keyframeIndex;data.selected=selection;
   drag={id:e.pointerId,x:e.clientX,y:e.clientY};
   canvas.setPointerCapture(e.pointerId);
   e.preventDefault();
   rebuild();render();
 }
 function onMove(e){
   if(!drag||drag.id!==e.pointerId)return;
   const path=records[targetIndex].source.cameraPath11,k=path[selection];
   const dx=e.clientX-drag.x,dy=e.clientY-drag.y;
   drag.x=e.clientX;drag.y=e.clientY;
   // Constraints are intentional: 1 axis at a time, preserves t and other attributes.
   // Perspective view is a guide; precise values are edited with the numeric sliders.
   const factor=view==='side'?.06:.04;
   if(axis==='x')k.x=clamp(k.x+dx*factor,-4,4);
   if(axis==='y')k.y=clamp(k.y-dy*factor,-4,4);
   if(axis==='z')k.z=clamp(k.z-dy*factor,2,12);
   data.dragCount++;emitChange();rebuild();render();
   e.preventDefault();
 }
 const endDrag=(e)=>{if(!drag||drag.id!==e.pointerId)return;drag=null;if(canvas.hasPointerCapture(e.pointerId))canvas.releasePointerCapture(e.pointerId)};
 canvas.addEventListener('pointerdown',onDown);
 canvas.addEventListener('pointermove',onMove);
 canvas.addEventListener('pointerup',endDrag);
 canvas.addEventListener('pointercancel',endDrag);
 const onMessage=event=>{
   if(event.data?.type!=='motion-stage12-gizmo-mode'&&event.data?.type!=='motion-stage12-gizmo-refresh')return;
   if(window.parent!==window&&event.source!==window.parent)return;
   const msg=event.data;
   if(msg.type==='motion-stage12-gizmo-mode'){
     enabled=!!msg.enabled;
     view=['front','top','side'].includes(msg.view)?msg.view:'front';
     axis=['x','y','z'].includes(msg.axis)?msg.axis:'x';
     const next=records.findIndex(r=>r.source.uid===msg.uid);
     if(next>=0)targetIndex=next;
     selection=clamp(Number(msg.selected)||0,0,7);
     group.visible=enabled;
     canvas.style.pointerEvents=enabled?'auto':'none';
     data.mode=enabled;data.axis=axis;data.view=view;
   }
   if(msg.path&&records[targetIndex]){
     const valid=normalizeCameraPath11(msg.path);
     if(valid.length>=2)records[targetIndex].source.cameraPath11=valid;
   }
   chooseCamera();rebuild();render();
 };
 window.addEventListener('message',onMessage);
 function updateAspect(){chooseCamera()}
 function dispose(){
   window.removeEventListener('message',onMessage);
   canvas.removeEventListener('pointerdown',onDown);
   canvas.removeEventListener('pointermove',onMove);
   canvas.removeEventListener('pointerup',endDrag);
   canvas.removeEventListener('pointercancel',endDrag);
   clear();scene.remove(group);
 }
 return {getCamera:()=>enabled?overview:null,updateAspect,refresh:()=>{if(enabled){chooseCamera();rebuild()}},dispose,diag:data};
}
