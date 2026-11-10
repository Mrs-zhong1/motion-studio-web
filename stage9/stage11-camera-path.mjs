// Stage11 keyframe editor: layered over Stage10 in the offline builder.
export function addCameraEditorStage11(source){
 const once=(a,b)=>{if(source.split(a).length!==2)throw Error('Stage11 anchor mismatch: '+a.slice(0,70));source=source.replace(a,b)};
 const schema=String.raw`function normStage11Path(raw){
  if(!Array.isArray(raw))return [];
  const points=raw.slice(0,8).map((v)=>{
    const p=normStage10Camera(v),at=Number(v?.at);
    return {...p,at:Number.isFinite(at)?Math.max(0,Math.min(100,at)):0};
  }).sort((a,b)=>a.at-b.at);
  for(let i=1;i<points.length;i++)if(points[i].at<=points[i-1].at)points[i].at=Math.min(100,points[i-1].at+0.01);
  return points.length>=2&&points[0].at===0&&points.at(-1).at===100?points:[];
 }
 `;
 once("function normSection(s)",schema+"function normSection(s)");
 once("camera3d:normStage10Camera(s.camera3d),glb:","camera3d:normStage10Camera(s.camera3d),cameraPath11:normStage11Path(s.cameraPath11),glb:");
 once("camera3d:normStage10Camera(s.camera3d)}","camera3d:normStage10Camera(s.camera3d),cameraPath11:normStage11Path(s.cameraPath11),uid:s.uid}");
 // Stage10 sliders share same active WebGL preview as Stage11.
 once("if(output)output.textContent=input.value;saveDraft();","if(output)output.textContent=input.value;saveDraft();window.stage11NotifyCamera?.(s);");
 const ui=String.raw`if(s.id==='offline-glb-scene'){
   const panel=document.createElement('section');
   panel.id='stage11CameraPanel';panel.className='camera-path';
   p.appendChild(panel);
   const labels={x:'X 水平偏移',y:'Y 垂直偏移',z:'Z 距离',yaw:'Yaw 偏航',pitch:'Pitch 俯仰',roll:'Roll 翻滚',fov:'FOV 焦距视角'};
   const limits={x:[-4,4,.1],y:[-4,4,.1],z:[2,12,.1],yaw:[-120,120,1],pitch:[-80,80,1],roll:[-90,90,1],fov:[22,90,1]};
   if(!Array.isArray(s.cameraPath11))s.cameraPath11=[];
   let selected=0,drag=null;
   function ensure(){
     if(s.cameraPath11.length<2){
       const base=normStage10Camera(s.camera3d);
       const chapters=project.sections.filter(x=>x.id==='offline-glb-scene'&&x.glb);
       const chapterIndex=chapters.findIndex(x=>x.uid===s.uid);
       const dest=normStage10Camera(chapters[chapterIndex+1]?.camera3d||s.camera3d);
       const mid={};for(const key of Object.keys(base))mid[key]=(base[key]+dest[key])/2;
       mid.x=Math.max(-4,Math.min(4,mid.x+.8));
       s.cameraPath11=[{...base,at:0},{...mid,at:50},{...dest,at:100}];
     }
   }
   function notify(){
     saveDraft();
     const frame=document.getElementById('stage10PreviewFrame');
     if(frame?.contentWindow&&frame.srcdoc)frame.contentWindow.postMessage({
       type:'motion-stage11-camera-patch',uid:s.uid,path:s.cameraPath11,camera3d:s.camera3d
     },'*');
   }
   window.stage11NotifyCamera=notify;
   function plot(){
     const path=s.cameraPath11;if(path.length<2)return '';
     const px=k=>16+k.at*3.06,py=k=>110-(k.x+4)*11;
     const line=path.map((k,i)=>(i?'L':'M')+px(k).toFixed(2)+' '+py(k).toFixed(2)).join(' ');
     return '<svg id="stage11Track" viewBox="0 0 340 132" style="width:100%;height:140px;touch-action:none;border:1px solid #586a77;border-radius:8px;background:#142431" role="img" aria-label="3D 镜头轨迹：横轴为滚动时间，纵轴为镜头 X 偏移">'
      +'<path d="M16 66H322" stroke="#456075" stroke-dasharray="3 5"/><path d="'+line+'" fill="none" stroke="#d5ef96" stroke-width="2.5"/>'
      +path.map((k,i)=>'<circle data-keypoint="'+i+'" cx="'+px(k)+'" cy="'+py(k)+'" r="'+(i===selected?8:6)+'" fill="'+(i===selected?'#d9ef9a':'#80c4df')+'" stroke="#193142" stroke-width="2"/>').join('')+'</svg>';
   }
   function refresh(){
     const path=s.cameraPath11;
     panel.innerHTML='<h3>Stage 11 · 3D 镜头轨迹与时间轴</h3><p class="small">每章的轨迹控制从当前 GLB 到下一 GLB 的过渡，最多 8 点。拖动圆点：左右改时间（端点固定），上下改 X；选择节点编辑七项镜头参数；改动即时发送到共享 3D 预览。</p>'
       +'<div class="selected-controls"><button type="button" id="stage11Enable">'+(path.length?'重置为三点轨迹':'启用三点轨迹')+'</button><button type="button" id="stage11Add" '+(path.length>=8?'disabled':'')+'>＋ 增加关键帧</button><button type="button" id="stage11Delete" '+(path.length<=2?'disabled':'')+'>删除选中帧</button></div>'
       +(path.length?plot()+'<div class="field"><label>当前关键帧 <select id="stage11KeySelect">'+path.map((k,i)=>'<option value="'+i+'" '+(i===selected?'selected':'')+'>帧 '+(i+1)+' · '+k.at.toFixed(1)+'%</option>').join('')+'</select></label></div>'
       +'<div class="field"><label>时间点 <output id="stage11TimeOut">'+path[selected].at.toFixed(1)+'%</output></label><input id="stage11Time" type="range" min="'+(selected===0?0:path[selected-1].at+.5)+'" max="'+(selected===path.length-1?100:path[selected+1].at-.5)+'" step=".5" value="'+path[selected].at+'" '+(selected===0||selected===path.length-1?'disabled':'')+'></div>'
       +'<div class="cp-grid">'+Object.entries(limits).map(([key,[min,max,step]])=>'<label>'+labels[key]+' <output id="stage11Value_'+key+'">'+path[selected][key]+'</output><input data-stage11-param="'+key+'" type="range" min="'+min+'" max="'+max+'" step="'+step+'" value="'+path[selected][key]+'"></label>').join('')+'</div>'
       :'<p class="small">尚未启用轨迹，将使用 Stage 10 的章节级镜头关键帧。</p>');
     panel.querySelector('#stage11Enable').onclick=()=>{s.cameraPath11=[];ensure();selected=1;refresh();notify()};
     panel.querySelector('#stage11Add').onclick=()=>{
       ensure();if(s.cameraPath11.length>=8)return;
       const path=s.cameraPath11;let index=Math.max(1,Math.min(selected,path.length-2));
       // Pick widest time gap to guarantee a distinct insertion.
       let width=-1;for(let j=0;j<path.length-1;j++){const gap=path[j+1].at-path[j].at;if(gap>width){width=gap;index=j;}}
       const left=path[index],right=path[index+1],v={};
       for(const k of Object.keys(limits))v[k]=(left[k]+right[k])/2;
       v.at=(left.at+right.at)/2;path.splice(index+1,0,v);selected=index+1;refresh();notify();
     };
     panel.querySelector('#stage11Delete').onclick=()=>{
       if(s.cameraPath11.length<=2||selected===0||selected===s.cameraPath11.length-1)return;
       s.cameraPath11.splice(selected,1);selected=Math.max(0,selected-1);refresh();notify();
     };
     if(!path.length)return;
     panel.querySelector('#stage11KeySelect').onchange=e=>{selected=Number(e.target.value);refresh()};
     panel.querySelector('#stage11Time').oninput=e=>{
       path[selected].at=Number(e.target.value);panel.querySelector('#stage11TimeOut').textContent=e.target.value+'%';redrawSvg();notify();
     };
     panel.querySelectorAll('[data-stage11-param]').forEach(el=>el.oninput=e=>{
       const key=el.dataset.stage11Param;path[selected][key]=Number(el.value);panel.querySelector('#stage11Value_'+key).textContent=el.value;
       panel.querySelector('#stage11Track').outerHTML=plot();notify();
     });
     const svg=panel.querySelector('#stage11Track');
     function redrawSvg(){if(!svg)return;const doc=new DOMParser().parseFromString(plot(),'image/svg+xml');svg.innerHTML=doc.documentElement.innerHTML;}
     svg.onpointerdown=e=>{
       const circle=e.target.closest('[data-keypoint]');if(!circle)return;
       selected=Number(circle.dataset.keypoint);drag={pointerId:e.pointerId};svg.setPointerCapture(e.pointerId);
     };
     svg.onpointermove=e=>{
       if(!drag)return;const bounds=svg.getBoundingClientRect(),p=s.cameraPath11[selected];
       const x=Math.max(0,Math.min(1,((e.clientX-bounds.left)/Math.max(1,bounds.width)*340-16)/306));
       const y=Math.max(0,Math.min(1,(e.clientY-bounds.top)/Math.max(1,bounds.height)));
       if(selected>0&&selected<path.length-1)p.at=Math.max(path[selected-1].at+.5,Math.min(path[selected+1].at-.5,x*100));
       p.x=Math.max(-4,Math.min(4,(110-y*132)/11-4));
       const circles=svg.querySelectorAll('[data-keypoint]');circles.forEach((c,i)=>{c.setAttribute('cx',16+path[i].at*3.06);c.setAttribute('cy',110-(path[i].x+4)*11);});
       redrawSvg();notify();
     };
     svg.onpointerup=()=>{if(drag){drag=null;refresh();}};
     svg.onpointercancel=()=>{drag=null;refresh()};
   }
   refresh();
 }
 `;
 once(" $('moveUp').onclick=",ui+" $('moveUp').onclick=");
 return source;
}
