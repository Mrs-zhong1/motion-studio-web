// R30: opt-in two-image Cinematic story trial, integrated into the native
// preview → use-template → editor → JSON save/reopen → standalone HTML export.
// Does not rewrite existing R16 scroll/camera engine or 39 official assets.
export function injectR30CinematicTrial(html) {
 if(typeof html!=='string'||!html.includes('</body>')||!html.includes('id="previewUsePanel"')||!html.includes('id="importAIAssets"'))throw Error('R30 editor integration anchors missing');
 if(html.includes('id="r30TrialFiles"'))throw Error('R30 duplicate injection');
 const previewButton='<button id="r30TrialPreviewButton" type="button" class="r30-trial-button">导入双场景试片</button><span id="r30TrialPreviewStatus" class="r30-trial-status" role="status" aria-live="polite"></span>';
 const editorButton='<button id="r30TrialEditorButton" type="button" title="只更新 Cinematic 模板的第 2、3 章，不覆盖正式素材库">Cinematic 双场景试片</button><span id="r30TrialEditorStatus" class="r30-trial-status" role="status" aria-live="polite"></span>';
 const style=`<style id="r30-trial-controls">
.r30-trial-button,#r30TrialEditorButton{border:1px solid #cab98b;background:#f6eed9;color:#171b1d;border-radius:7px;padding:10px 13px;font-weight:700;cursor:pointer}
.r30-trial-button:focus-visible,#r30TrialEditorButton:focus-visible{outline:3px solid #a16d3a;outline-offset:3px}
.r30-trial-status{display:block;color:#7b7568;font-size:11px;line-height:1.5;max-width:290px}
#r30TrialEditorStatus{color:#d6deb9}
@media(max-width:700px){#r30TrialEditorButton{padding:8px 10px;font-size:10px}.r30-trial-button{width:100%;margin:6px 0}}
</style>`;
 const script=`<script id="r30-cinematic-trial-script">
(()=>{
const fileInput=document.getElementById('r30TrialFiles');
const previewButton=document.getElementById('r30TrialPreviewButton');
const editorButton=document.getElementById('r30TrialEditorButton');
const statuses=[document.getElementById('r30TrialPreviewStatus'),document.getElementById('r30TrialEditorStatus')];
let activeRequest=false;
function status(message){statuses.forEach(el=>{el.textContent=message;});}
function readDataURL(file){return new Promise((resolve,reject)=>{
 const reader=new FileReader();
 reader.onload=()=>resolve(String(reader.result||''));
 reader.onerror=()=>reject(Error('无法读取图片：'+file.name));
 reader.readAsDataURL(file);
});}
async function imageOriginal(file){
 if(!file||!['image/jpeg','image/png','image/webp'].includes(file.type))throw Error('仅支持 JPEG、PNG 或 WebP');
 if(file.size<1000||file.size>1700000)throw Error('每张原图需小于 1.7 MB（编辑与导出内嵌限制）');
 const bitmap=await createImageBitmap(file);
 const w=bitmap.width,h=bitmap.height;bitmap.close?.();
 if(w<1600||h<900||w/h<1.68||w/h>1.88)throw Error('请提供原生不低于 1600×900、接近 16:9 的独立图像');
 const data=await readDataURL(file);
 if(data.length>2450000||!/^data:image\/(jpeg|png|webp);base64,/.test(data))throw Error('原图数据过大或格式不支持');
 return data;
}
async function importTwo(files){
 if(activeRequest)return;
 if(files.length!==2)throw Error('请一次选择两张图片，按文件名排序后对应第 2、3 章');
 activeRequest=true;previewButton.disabled=editorButton.disabled=true;
 try{
 status('正在验证两张独立原图…');
 // Validate and decode both BEFORE updating any project or template state.
 const sorted=Array.from(files).sort((a,b)=>a.name.localeCompare(b.name));
 const data=await Promise.all(sorted.map(imageOriginal));
 if(data[0]===data[1])throw Error('两个章节需要不同的原图');
 await ensureTemplatePhoto('cinematic');
 const existing=templatePhotoCache.get('cinematic');
 if(!existing||existing.length!==5)throw Error('Cinematic 完整模板未准备好');
 const next=existing.slice();next[1]=data[0];next[2]=data[1];
 const audit=(templateAssetAuditCache.get('cinematic')||[]).slice();
 for(const i of [1,2])audit[i]={chapter:i+1,kind:'user-upload',source:null,rightsReviewed:false,sourceAttempted:true};
 // All-or-nothing gallery-level commit: do not alter the official AI bundle.
 templatePhotoCache.set('cinematic',next);
 templateAssetAuditCache.set('cinematic',audit);
 if(!$('templatePreview').hidden&&previewTemplateId==='cinematic'){
   r17RenderFilmstrip('cinematic');
   $('templatePreviewFrame').srcdoc=buildTemplatePreviewDocument('cinematic');
 }
 if(!$('editorView').hidden&&project.templateId==='cinematic'){
   project.sections[1].image=data[0];project.sections[2].image=data[1];
   for(const i of [1,2])project.sections[i].imageMeta={kind:'user-upload',source:null,rightsReviewed:false};
   recordHistory();render();persistDraftWithoutHistory();
 }
 status('已替换 Cinematic 第 2、3 章试片；可预览、编辑、保存 JSON 和导出 HTML。未改正式素材库。');
 }finally{activeRequest=false;previewButton.disabled=editorButton.disabled=false;fileInput.value='';}
}
previewButton.onclick=()=>{
 if(previewTemplateId!=='cinematic'){status('请先打开 Cinematic Journey 模板预览');return;}
 fileInput.click();
};
editorButton.onclick=()=>{
 if(project.templateId!=='cinematic'){status('请先选择 Cinematic Journey 模板');return;}
 fileInput.click();
};
fileInput.onchange=async event=>{
 const files=Array.from(event.target.files||[]);
 if(!files.length)return;
 try{await importTwo(files);}
 catch(err){status('导入失败：'+err.message);console.warn('R30 trial validation:',err.message);}
};
const baseExport=exportDocument;
exportDocument=function(){
 const output=baseExport();
 // Export the same R23 story art direction used in the template preview/editor.
 // R23 is appended to <head> during offline build but is not part of
 // document.styleSheets[0] read by the legacy exporter.
 const storyCSS=document.getElementById('r23-story-art-direction')?.textContent||'';
 const extra=storyCSS?'<style id="r30-export-story-parity">'+storyCSS+'</style>':'';
 const trial=project.templateId==='cinematic'&&project.sections[1]?.imageMeta?.kind==='user-upload'&&project.sections[2]?.imageMeta?.kind==='user-upload';
 return output.replace('</head>',extra+'</head>')
  .replace('<body ',trial?'<body data-r30-dual-scene="true" ':'<body ');
};
if(window.MotionStudioUnified)window.MotionStudioUnified.build=exportDocument;
window.MotionStudioR30={importTwo,originalImage:imageOriginal,getState:()=>({
 templateReady:!!templatePhotoCache.get('cinematic'),
 editorTemplate:project.templateId,
 hasTwoEditorImages:project.sections[1]?.imageMeta?.kind==='user-upload'&&project.sections[2]?.imageMeta?.kind==='user-upload'
})};
})();
</script>`;
 return html.replace('id="previewUsePanel"',previewButton+'<button id="previewUsePanel"')
  .replace('<button id="importAIAssets"',editorButton+'<button id="importAIAssets"')
  .replace(/<\\/body>\\s*<\\/html>\\s*$/,style+'<input id="r30TrialFiles" type="file" accept="image/jpeg,image/png,image/webp" multiple hidden>'+script+'</body></html>');
}
