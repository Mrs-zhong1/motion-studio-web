// R37: genuine single-stage cinematic composition, adapted from the design
// patterns documented in greensock/gsap-skills (MIT) and Codrops seam work.
// This uses the EXISTING R16 scroll calculation; no downloaded JS packages,
// duplicate RAF loops or new paid dependencies.
export const r37Css=String.raw`
/* One coherent photographic stage, not a two-page panel montage. */
body[data-motion-template="cinematic"] .page{overflow:visible!important;transform:none!important}
body[data-motion-template="cinematic"] .page .section.r37-scene{
 height:175svh!important;min-height:175svh!important;
 overflow:visible!important;display:block!important;
 padding:0!important;position:relative!important;
}
body[data-motion-template="cinematic"] .r37-stage{
 position:sticky;top:0;width:100%;height:100svh;min-height:100svh;
 overflow:hidden;isolation:isolate;display:block;
 background:#0a1016;
}
/* Never expose the embedded unrelated micro-demo's SECOND heading/object. */
body[data-motion-template="cinematic"] .r37-stage > iframe,
body[data-motion-template="cinematic"] .r37-stage > .badge,
body[data-motion-template="cinematic"] .r37-stage > .caption{
 display:none!important;visibility:hidden!important;pointer-events:none!important;
}
body[data-motion-template="cinematic"] .r37-stage .section-art{
 position:absolute!important;inset:-4% -3%!important;
 width:106%!important;height:108%!important;max-width:none!important;
 background-repeat:no-repeat!important;background-size:cover!important;
 opacity:1!important;z-index:0!important;
 transform:translate3d(
  calc(var(--r16-photo-x,0px) + var(--r37-px,0px)),
  calc(var(--r16-photo-y,0px) + var(--r37-py,0px)),0)
  scale(calc(1.03 + var(--r16-incoming,1)*.035))!important;
 will-change:transform;pointer-events:none!important;
 filter:contrast(1.06) saturate(.92);
}
body[data-motion-template="cinematic"] .r37-stage::before{
 content:"";position:absolute;inset:0;z-index:2;pointer-events:none;
 background:linear-gradient(90deg,rgba(7,11,17,.78) 0%,rgba(7,11,17,.36) 54%,transparent 90%),
 linear-gradient(0deg,rgba(6,10,16,.55),transparent 35%,rgba(9,12,18,.22));
}
body[data-motion-template="cinematic"] .r37-stage::after{
 content:"";position:absolute;inset:0;pointer-events:none;z-index:3;
 border:clamp(8px,1.4vw,24px) solid rgba(4,8,14,.06);
}
/* Only ONE narrative title, aligned to the subject photo. */
body[data-motion-template="cinematic"] .r37-stage .designed-chapter-heading{
 position:absolute!important;top:auto!important;
 bottom:clamp(125px,17vh,210px)!important;left:clamp(24px,6vw,110px)!important;
 right:auto!important;width:min(56vw,860px)!important;max-width:min(56vw,860px)!important;
 z-index:9!important;transform:translate3d(0,var(--r16-type-y,0px),0);
 background:none!important;pointer-events:none!important;
 opacity:clamp(.48,calc(var(--r16-incoming,1)*1.7),1)!important;
}
body[data-motion-template="cinematic"] .r37-stage .designed-chapter-heading h2{
 font-family:Georgia,serif!important;font-size:clamp(38px,6.1vw,112px)!important;
 font-weight:500!important;letter-spacing:-.055em!important;
 line-height:.94!important;max-width:100%!important;
 text-transform:uppercase;color:#fffef7!important;
 text-shadow:0 3px 35px rgba(1,5,13,.6);margin:12px 0 18px!important;
}
body[data-motion-template="cinematic"] .r37-stage .designed-chapter-heading p{
 font:400 clamp(13px,1.2vw,19px)/1.55 system-ui,sans-serif!important;
 color:#e8e9e1!important;max-width:540px;
 text-shadow:0 2px 24px #030a12bd;
}
body[data-motion-template="cinematic"] .r37-stage .r15-scene-mark{
 position:absolute!important;z-index:8!important;
 bottom:clamp(22px,5vh,58px)!important;
 width:calc(100% - 2*clamp(24px,6vw,110px))!important;
 left:clamp(24px,6vw,110px)!important;
 background:none!important;border:0!important;
}
body[data-motion-template="cinematic"] .r37-stage .template-opening-mark,
body[data-motion-template="cinematic"] .r37-stage .template-closing-mark{
 z-index:8!important;pointer-events:none!important;
}
/* Truly compact, legible nav. Collapsed state does not cut off "CHAPTERS". */
body[data-motion-template="cinematic"] .r14-story-rail:not(.r36-open) .r36-nav-caption,
body[data-motion-template="product-3d"] .r14-story-rail:not(.r36-open) .r36-nav-caption{
 display:none!important;
}
body[data-motion-template="cinematic"] .r14-story-rail:not(.r36-open) .r36-nav-toggle,
body[data-motion-template="product-3d"] .r14-story-rail:not(.r36-open) .r36-nav-toggle{
 font-size:22px!important;line-height:1!important;padding:0!important;
}
@media(max-width:760px){
 body[data-motion-template="cinematic"] .page .section.r37-scene{
  height:150svh!important;min-height:150svh!important
 }
 body[data-motion-template="cinematic"] .r37-stage .section-art{
  background-position:50% 50%!important
 }
 body[data-motion-template="cinematic"] .r37-stage .designed-chapter-heading{
  left:6%!important;right:6%!important;width:88%!important;max-width:88%!important;
  bottom:clamp(135px,17vh,190px)!important;top:auto!important;
 }
 body[data-motion-template="cinematic"] .r37-stage .designed-chapter-heading h2{
  font-size:clamp(37px,9.8vw,70px)!important;line-height:.98!important
 }
 body[data-motion-template="cinematic"] .r37-stage::before{
  background:linear-gradient(0deg,rgba(3,7,12,.89),rgba(3,7,12,.08) 70%),
  linear-gradient(90deg,rgba(3,7,12,.35),transparent)
 }
}
@media(prefers-reduced-motion:reduce){
 body[data-motion-template="cinematic"] .r37-stage .section-art{
  transform:none!important;will-change:auto!important;
 }
 body[data-motion-template="cinematic"] .r37-stage .designed-chapter-heading{
  transform:none!important;opacity:1!important;
 }
}
`;

export const r37Runtime=String.raw`(function(){
 if(document.body.dataset.motionTemplate!=='cinematic')return;
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 const page=document.querySelector('.page[data-template="cinematic"]');
 const scenes=Array.from(document.querySelectorAll('.page[data-template="cinematic"] > section.section'));
 if(!scenes.length)return;
 // .page in the legacy editor CSS is overflow:hidden. A sticky child cannot
 // hold the viewport through that clipping ancestor. Cinematic exports need
 // the document (not .page) to own the vertical scroll.
 if(page){
  page.style.setProperty('overflow','visible','important');
  page.style.setProperty('transform','none','important');
 }
 for(const section of scenes){
  if(section.querySelector(':scope > .r37-stage'))continue;
  // R16 retains the same section and image references, so it continues to
  // drive --r16-incoming / camera parallax and the chapter navigator.
  const stage=document.createElement('div');
  stage.className='r37-stage';
  while(section.firstChild)stage.appendChild(section.firstChild);
  section.appendChild(stage);
  section.classList.add('r37-scene');
  section.style.setProperty('overflow','visible','important');
  section.style.setProperty('height','175svh','important');
  section.style.setProperty('min-height','175svh','important');
  // R36 pilot uses inline !important layout styles. Match that priority on
  // the new director geometry so browser capture cannot regress to split UI.
  const art=stage.querySelector('.section-art');
  if(art){
   art.style.setProperty('inset','-4% -3%','important');
   art.style.setProperty('width','106%','important');
   art.style.setProperty('height','108%','important');
   art.style.setProperty('transform','translate3d(calc(var(--r16-photo-x,0px) + var(--r37-px,0px)),calc(var(--r16-photo-y,0px) + var(--r37-py,0px)),0) scale(calc(1.03 + var(--r16-incoming,1)*.035))','important');
  }
  const heading=stage.querySelector('.designed-chapter-heading');
  if(heading){
   heading.style.setProperty('top','auto','important');
   heading.style.setProperty('bottom','clamp(125px,17vh,210px)','important');
   heading.style.setProperty('width','min(56vw,860px)','important');
   heading.style.setProperty('max-width','min(56vw,860px)','important');
  }
  for(const node of stage.querySelectorAll(':scope > iframe')){
   node.setAttribute('aria-hidden','true');
   node.setAttribute('tabindex','-1');
   node.style.setProperty('display','none','important');
  }
  if(!reduced.matches){
   stage.addEventListener('pointermove',event=>{
    if(event.pointerType==='touch')return;
    const box=stage.getBoundingClientRect();
    const x=((event.clientX-box.left)/Math.max(1,box.width)-.5)*14;
    const y=((event.clientY-box.top)/Math.max(1,box.height)-.5)*10;
    stage.style.setProperty('--r37-px',x.toFixed(2)+'px');
    stage.style.setProperty('--r37-py',y.toFixed(2)+'px');
   },{passive:true});
   stage.addEventListener('pointerleave',()=>{
    stage.style.setProperty('--r37-px','0px');
    stage.style.setProperty('--r37-py','0px');
   },{passive:true});
  }
 }
 // Recalculate R16 viewports after changing scene height. Do not register a
 // second continuous scroll handler or start another animation clock.
 dispatchEvent(new Event('resize'));
 document.documentElement.dataset.r37Director='single-stage';
})();`;

export function applyR37StoryDirector(html){
 if(typeof html!=='string'||!html.includes('id="r36-pilot-editor"')||!html.includes('</body></html>'))throw Error('R37 requires complete R36 offline editor');
 if(html.includes('id="r37-editor-director"'))throw Error('R37 duplicate injection');
 const injection=String.raw`<script id="r37-editor-director">
(function(){
 const previous=exportDocument;
 exportDocument=function(){
  let doc=previous();
  if(project.templateId!=='cinematic' && project.templateId!=='product-3d')return doc;
  const css=document.getElementById('r37-director-css').textContent;
  const runtime=document.getElementById('r37-director-runtime').textContent;
  doc=doc.replace('</head>','<style id="r37-final-style">'+css+'</style></head>');
  if(project.templateId==='cinematic')
   doc=doc.replace('</body>','<script id="r37-final-runtime">'+runtime+'<'+'/script></body>');
  return doc;
 };
 if(window.MotionStudioUnified)window.MotionStudioUnified.build=exportDocument;
})();
</script>`;
 return html.replace('</head>','<style id="r37-director-css">'+r37Css+'</style></head>')
  .replace(/<\/body><\/html>\s*$/,'<script type="text/plain" id="r37-director-runtime">'+r37Runtime+'</script>'+injection+'</body></html>');
}
