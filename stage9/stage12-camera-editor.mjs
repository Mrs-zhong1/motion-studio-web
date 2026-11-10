// Stage12 editor integration. Applied after Stage10/11, preserving Stage9 20 components.
export function addCameraEditorStage12(source){
 const anchor="     panel.querySelector('#stage11Enable').onclick=";
 if(source.split(anchor).length!==2)throw Error('Stage12 Stage11 camera panel hook changed');
 const insert=String.raw\`
     const stage12Controls=document.createElement('div');
     stage12Controls.id='stage12ViewportControls';
     stage12Controls.style.cssText='padding:12px;margin:12px 0;border:1px solid #536a78;border-radius:10px;background:#122333';
     stage12Controls.innerHTML='<h3>Stage 12 · 真实 Three.js 空间轨迹视口</h3>'
       +'<p class="small">开启后在下方共享 WebGL 预览里显示三维轨迹和球形控制点。拖动球体沿指定 X/Y/Z 轴调整空间位置，保留关键帧时间；切换前/顶/侧视图查看不同方向。</p>'
       +'<div class="selected-controls"><button type="button" id="stage12Toggle">开启空间 Gizmo</button><button id="stage12ViewFront" type="button">前视</button><button id="stage12ViewTop" type="button">顶视</button><button id="stage12ViewSide" type="button">侧视</button></div>'
       +'<div class="selected-controls"><button id="stage12AxisX" type="button">拖动 X</button><button id="stage12AxisY" type="button">拖动 Y</button><button id="stage12AxisZ" type="button">拖动 Z</button></div>'
       +'<p class="small" id="stage12Status">编辑模式未开启。需要至少两个已导入的 GLB 章节，并先启用 Stage 11 轨迹。</p>';
     panel.appendChild(stage12Controls);
     const active=window.__motionStage12State||{enabled:false,uid:s.uid,axis:'x',view:'front'};
     if(active.uid!==s.uid){active.enabled=false;active.uid=s.uid;}
     window.__motionStage12State=active;
     const status=()=>{const el=document.getElementById('stage12Status');if(el)el.textContent=active.enabled?'空间编辑已开启 · '+active.view+' · 轴 '+active.axis+' · 鼠标拖动预览中的球形轨迹节点':'空间编辑关闭；导出网页不显示辅助线';};
     status();
     function pushMode(){
       const frame=document.getElementById('stage10PreviewFrame');
       if(!frame?.srcdoc||!frame.contentWindow)return;
       const payload={type:'motion-stage12-gizmo-mode',uid:s.uid,enabled:active.enabled,axis:active.axis,view:active.view,selected,path:s.cameraPath11};
       let tries=0;
       const send=()=>{
         if(!frame.contentWindow||!active.enabled)return;
         try{
           if(frame.contentWindow.__motionStage12Gizmo){frame.contentWindow.postMessage(payload,'*');return}
         }catch(err){}
         if(++tries<80)setTimeout(send,100);
       };
       if(!active.enabled){frame.contentWindow.postMessage(payload,'*');return}
       send();
     }
     window.__motionStage12Current={
       uid:s.uid,
       receive:(msg,event)=>{
         const frame=document.getElementById('stage10PreviewFrame');
         if(!frame||event.source!==frame.contentWindow||msg.uid!==s.uid)return;
         if(!Array.isArray(msg.path))return;
         const validated=normStage11Path(msg.path);
         if(validated.length<2)return;
         s.cameraPath11=validated;
         selected=Math.max(0,Math.min(validated.length-1,Number(msg.index)||0));
         saveDraft();refresh();
       }
     };
     if(!window.__motionStage12MessageInstalled){
       window.__motionStage12MessageInstalled=true;
       window.addEventListener('message',event=>{
         if(event.data?.type!=='motion-stage12-gizmo-change')return;
         window.__motionStage12Current?.receive(event.data,event);
       });
     }
     panel.querySelector('#stage12Toggle').onclick=()=>{
       if(s.cameraPath11.length<2){status();return}
       active.enabled=!active.enabled;
       const wrap=document.getElementById('stage10PreviewWrap');
       if(active.enabled&&wrap?.style.display==='none')document.getElementById('stage10CameraPreview')?.click();
       panel.querySelector('#stage12Toggle').textContent=active.enabled?'关闭空间 Gizmo':'开启空间 Gizmo';
       status();pushMode();
     };
     panel.querySelector('#stage12Toggle').textContent=active.enabled?'关闭空间 Gizmo':'开启空间 Gizmo';
     for(const view of ['Front','Top','Side']){
       panel.querySelector('#stage12View'+view).onclick=()=>{active.view=view.toLowerCase();status();pushMode();};
     }
     for(const axis of ['X','Y','Z']){
       panel.querySelector('#stage12Axis'+axis).onclick=()=>{active.axis=axis.toLowerCase();status();pushMode();};
     }
 \`;
 source=source.replace(anchor,insert+"\n"+anchor);
 return source;
}
