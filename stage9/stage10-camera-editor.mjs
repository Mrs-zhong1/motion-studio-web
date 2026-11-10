import {Buffer} from 'node:buffer';
// Stage 10 integration, applied only during the bundled offline build.
// Preserves Stage 9 source and all 20 components. Per GLB chapter = one spatial camera keyframe.
export function addCameraEditorStage10(source){
  if (!source.includes('function normSection(s)')||!source.includes('function renderProps(){'))throw Error('Stage9 editor schema changed');
  const once=(a,b)=>{if(source.split(a).length!==2)throw Error('Stage10 anchor missing or ambiguous: '+a.slice(0,70));source=source.replace(a,b)};
  const normalizer=String.raw`function normStage10Camera(raw){
   const p=raw&&typeof raw==='object'?raw:{};
   const n=(key,low,high,def)=>{const value=Number(p[key]);return p[key]===undefined||p[key]===null||!Number.isFinite(value)?def:Math.max(low,Math.min(high,value))};
   return {x:n('x',-4,4,0),y:n('y',-4,4,0),z:n('z',2,12,5.5),yaw:n('yaw',-120,120,0),pitch:n('pitch',-80,80,0),roll:n('roll',-90,90,0),fov:n('fov',22,90,42)};
 }
 `;
  once('function normSection(s)',normalizer+'function normSection(s)');
  once("glb:typeof s.glb==='string'","camera3d:normStage10Camera(s.camera3d),glb:typeof s.glb==='string'");
  const ui=String.raw`if(s.id==='offline-glb-scene'){
  const controls=[['x','横向偏移 X',-4,4,.1],['y','高度 Y',-4,4,.1],['z','镜头距离 Z',2,12,.1],['yaw','偏航 Yaw',-120,120,1],['pitch','俯仰 Pitch',-80,80,1],['roll','翻滚 Roll',-90,90,1],['fov','视角 FOV',22,90,1]];
  const panel=document.createElement('section');panel.className='camera-path';panel.id='stage10CameraPanel';
  panel.innerHTML='<h3>Stage 10 · 共享 Three.js 镜头关键帧</h3><p class="small">每个 GLB 章节对应一帧空间镜头。导出后的多 GLB 网页将在章节中心之间连续插值。位置相对模型中心；旋转单位为度。</p>'
   +'<div class="cp-grid">'+controls.map(([k,label,min,max,step])=>'<label>'+label+' <output id="cam3dOut_'+k+'">'+s.camera3d[k]+'</output><input type="range" data-camera3d="'+k+'" min="'+min+'" max="'+max+'" step="'+step+'" value="'+s.camera3d[k]+'"></label>').join('')+'</div>'
   +'<div class="selected-controls"><button id="stage10CameraReset" type="button">重置本章镜头</button><button id="stage10CameraPreview" type="button">预览共享 3D 网页</button></div><div id="stage10PreviewWrap" style="display:none"><p class="small">以下为实际导出页面的内嵌预览，滚动预览框查看跨章节镜头；修改上方参数后点击刷新即可更新。</p><button id="stage10PreviewRefresh" type="button">刷新预览</button><iframe id="stage10PreviewFrame" title="共享 3D 镜头预览" style="width:100%;height:340px;border:1px solid #6b7b85;border-radius:9px;background:#0b1119"></iframe></div>';
  p.appendChild(panel);
  panel.querySelectorAll('[data-camera3d]').forEach(input=>input.oninput=()=>{
    const key=input.dataset.camera3d;s.camera3d[key]=Number(input.value);
    const output=document.getElementById('cam3dOut_'+key);if(output)output.textContent=input.value;saveDraft();
  });
  document.getElementById('stage10CameraReset').onclick=()=>{s.camera3d=normStage10Camera(null);renderProps();saveDraft()};
  const preview=()=>{const frame=document.getElementById('stage10PreviewFrame');if(frame)frame.srcdoc=exportDocument()};
  document.getElementById('stage10CameraPreview').onclick=()=>{const wrap=document.getElementById('stage10PreviewWrap');wrap.style.display=wrap.style.display==='none'?'block':'none';if(wrap.style.display==='block')preview()};
  document.getElementById('stage10PreviewRefresh').onclick=preview;
 }
 `;
  once(" $('moveUp').onclick=",ui+" $('moveUp').onclick=");
  // A project can be loaded from JSON; the normSection call above guarantees old documents migrate.
  once("glb:s.id==='offline-glb-scene'?s.glb:''","glb:s.id==='offline-glb-scene'?s.glb:'',camera3d:normStage10Camera(s.camera3d)");
  if(!source.includes('camera3d:normStage10Camera(s.camera3d)'))throw Error('Camera serialization missing');
  // Legacy Stage8 GLB canvas can paint before its async mesh is ready.
  // Guard GPU drawGPU() instead of suppressing the editor error globally.
  const match=source.match(/stage9LabBase=atob\("([A-Za-z0-9+/=]+)"\)/);
  if(!match)throw Error('Stage9 embedded GLB lab missing');
  let lab=Buffer.from(match[1],'base64').toString('utf8');
  const oldDraw='function drawGPU(){const w=canvas.width,h=canvas.height;';
  if(!lab.includes(oldDraw))throw Error('Legacy GLB drawGPU contract missing');
  lab=lab.replace(oldDraw,'function drawGPU(){if(!mesh||!mesh.groups||!gl)return;const w=canvas.width,h=canvas.height;');
  source=source.replace(match[1],Buffer.from(lab,'utf8').toString('base64'));
  return source;
}
