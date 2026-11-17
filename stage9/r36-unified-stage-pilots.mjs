// Pilot R36: an opt-in exported-page composition, not a second scroll engine.
// Only product-3d and cinematic templates are affected. Other six templates
// keep their exact exported HTML. Editor internals, R16 timeline and 20
// components remain unchanged.
export const pilotCss = String.raw`
body[data-motion-template="product-3d"],body[data-motion-template="cinematic"]{
  --r36-ink:#f6f4e9;--r36-edge:rgba(255,255,255,.14);
  background:#0c1217;color:var(--r36-ink)
}
/* One common visual stage: no hard cards, columns or photo/iframe borders. */
body[data-motion-template="product-3d"] .page,
body[data-motion-template="cinematic"] .page{background:transparent!important;border:0!important}
body[data-motion-template="product-3d"] .page .section,
body[data-motion-template="cinematic"] .page .section{
  position:relative!important;display:block!important;overflow:hidden!important;
  isolation:isolate;min-height:100svh!important;padding:0!important;
  background:radial-gradient(ellipse at 72% 32%,#26302c,#0d1318 75%)!important;
}
body[data-motion-template="cinematic"] .page .section{
  background:linear-gradient(155deg,#151c26,#090e16 80%)!important
}
/* Photo occupies the whole canvas. Existing R16 masks/camera continue to
   animate the exact same section-art element; no competing animation clock. */
body[data-motion-template="product-3d"] .page .section .section-art,
body[data-motion-template="cinematic"] .page .section .section-art{
  position:absolute!important;inset:0!important;
  display:block!important;width:100%!important;height:100%!important;
  grid-area:unset!important;grid-column:auto!important;grid-row:auto!important;
  background-size:cover!important;background-repeat:no-repeat!important;
  mix-blend-mode:normal!important;opacity:1!important;
  z-index:0!important;pointer-events:none!important;border:0!important;
}
/* Art direction across the SAME shared canvas, behind 3D and text. */
body[data-motion-template="product-3d"] .page .section::after,
body[data-motion-template="cinematic"] .page .section::after{
 content:"";position:absolute;inset:0;pointer-events:none;z-index:2;
 background:linear-gradient(90deg,rgba(5,9,15,.90) 0%,rgba(6,11,16,.67) 35%,rgba(6,11,15,.14) 82%),
 linear-gradient(0deg,rgba(4,8,12,.38),transparent 34%);
}
body[data-motion-template="cinematic"] .page .section::after{
 background:linear-gradient(90deg,rgba(4,8,15,.81) 0%,rgba(5,9,17,.43) 45%,transparent 82%),
 linear-gradient(0deg,rgba(4,8,14,.6),transparent 38%);
}
/* Keep WebGL/HTML interaction *in* the stage, without a rectangular opaque
   pane. iframe stays operable in exported pages. We do not fake 3D assets. */
body[data-motion-template="product-3d"] .page .section > iframe,
body[data-motion-template="cinematic"] .page .section > iframe{
  position:absolute!important;top:7%!important;right:3%!important;left:auto!important;
  width:58%!important;height:86%!important;max-width:none!important;
  grid-area:unset!important;grid-column:auto!important;grid-row:auto!important;
  z-index:3!important;pointer-events:auto!important;
  border:0!important;border-radius:0!important;background:transparent!important;
  box-shadow:none!important;mix-blend-mode:screen;
  -webkit-mask-image:linear-gradient(90deg,transparent 0%,#000 21%,#000 94%,transparent 100%);
  mask-image:linear-gradient(90deg,transparent 0%,#000 21%,#000 94%,transparent 100%);
}
/* The chapter text is editorial overlay, not a separate green pane. */
body[data-motion-template="product-3d"] .page .section .designed-chapter-heading,
body[data-motion-template="cinematic"] .page .section .designed-chapter-heading{
 position:absolute!important;top:clamp(110px,19vh,240px)!important;
 left:clamp(24px,6vw,120px)!important;right:auto!important;bottom:auto!important;
 width:min(48%,710px)!important;max-width:48%!important;
 grid-area:unset!important;grid-column:auto!important;grid-row:auto!important;
 z-index:6!important;display:block!important;padding:0!important;
 background:none!important;border:0!important;box-shadow:none!important;
 color:#f9f8f0!important;pointer-events:none!important
}
body[data-motion-template="product-3d"] .page .section .designed-chapter-heading h2,
body[data-motion-template="cinematic"] .page .section .designed-chapter-heading h2{
  font:800 clamp(38px,5.4vw,91px)/.98 system-ui,sans-serif!important;
  letter-spacing:-.07em!important;color:inherit!important;text-shadow:0 4px 42px #050a10cc;
  max-width:100%!important;overflow-wrap:break-word!important
}
body[data-motion-template="cinematic"] .page .section .designed-chapter-heading h2{
 font-family:Georgia,serif!important;font-style:italic;font-weight:500!important;
 letter-spacing:-.05em!important
}
body[data-motion-template="product-3d"] .page .section .r15-scene-mark,
body[data-motion-template="cinematic"] .page .section .r15-scene-mark{
 z-index:7!important;bottom:clamp(20px,5vh,60px)!important
}
/* Hero itself is also one stage rather than an iframe mounted in a column. */
body[data-motion-template="product-3d"] .page .section.designed-hero > iframe{
 left:0!important;right:0!important;top:0!important;width:100%!important;height:100%!important;
 mix-blend-mode:normal!important;mask-image:none!important;-webkit-mask-image:none!important;
}
body[data-motion-template="product-3d"] .page .section.designed-hero::after{
 background:linear-gradient(90deg,rgba(4,9,12,.55),transparent 78%);pointer-events:none
}
/* Existing navigation has all chapter buttons, but the list is collapsed
   until expressly requested. Slim progress and a small menu stay available. */
body[data-motion-template="product-3d"] .r14-story-rail,
body[data-motion-template="cinematic"] .r14-story-rail{
 position:fixed!important;right:clamp(12px,2.6vw,35px)!important;
 top:clamp(12px,3vh,36px)!important;bottom:auto!important;transform:none!important;
 display:flex!important;flex-direction:column!important;gap:0!important;
 width:48px!important;max-height:calc(100svh - 24px)!important;
 padding:0!important;border:1px solid var(--r36-edge)!important;
 border-radius:16px!important;background:rgba(9,16,23,.55)!important;
 color:#f4f5ed!important;backdrop-filter:blur(20px)!important;
 z-index:100!important;overflow:hidden!important;
 transition:width .25s ease,background .2s ease
}
body[data-motion-template="product-3d"] .r14-story-rail.r36-open,
body[data-motion-template="cinematic"] .r14-story-rail.r36-open{
 width:min(270px,calc(100vw - 24px))!important;background:rgba(8,15,21,.94)!important
}
body[data-motion-template="product-3d"] .r14-rail-track,
body[data-motion-template="cinematic"] .r14-rail-track{
 position:absolute!important;inset:0 0 0 auto!important;width:3px!important;
 min-height:40px!important;height:100%!important;flex:0 0 3px!important;
 background:#ffffff30!important;border-radius:0!important
}
body[data-motion-template="product-3d"] .r14-rail-fill,
body[data-motion-template="cinematic"] .r14-rail-fill{
 width:100%!important;background:#d4f5a4!important
}
body[data-motion-template="product-3d"] .r14-rail-chapters,
body[data-motion-template="cinematic"] .r14-rail-chapters{
 display:none!important;padding:4px 8px 14px!important;
 width:100%!important;max-height:min(65svh,540px)!important;
 overflow-y:auto!important
}
body[data-motion-template="product-3d"] .r14-story-rail.r36-open .r14-rail-chapters,
body[data-motion-template="cinematic"] .r14-story-rail.r36-open .r14-rail-chapters{display:grid!important}
.r14-story-rail .r36-nav-toggle{
 display:flex;align-items:center;justify-content:center;gap:8px;
 min-height:46px;width:100%;padding:9px!important;flex:0 0 46px;
 border:0;color:#f5f7ee;background:transparent;font:700 11px system-ui,sans-serif;
 cursor:pointer
}
.r14-story-rail.r36-open .r36-nav-toggle{justify-content:space-between;padding-inline:15px!important}
.r14-story-rail .r36-nav-toggle:focus-visible{outline:2px solid #d9ff67;outline-offset:-3px}
body[data-motion-template="product-3d"] .r14-story-rail.r36-open button.r14-rail-chapter,
body[data-motion-template="cinematic"] .r14-story-rail.r36-open button.r14-rail-chapter{
 width:100%;max-width:none;justify-content:flex-start;min-height:40px
}
@media(max-width:760px){
 body[data-motion-template="product-3d"] .page .section > iframe,
 body[data-motion-template="cinematic"] .page .section > iframe{
  left:0!important;right:0!important;top:25%!important;width:100%!important;
  height:66%!important;opacity:.8!important;
 }
 body[data-motion-template="product-3d"] .page .section .designed-chapter-heading,
 body[data-motion-template="cinematic"] .page .section .designed-chapter-heading{
  top:13%!important;left:6%!important;right:6%!important;
  width:88%!important;max-width:88%!important
 }
 body[data-motion-template="product-3d"] .page .section .designed-chapter-heading h2,
 body[data-motion-template="cinematic"] .page .section .designed-chapter-heading h2{
  font-size:clamp(30px,10vw,57px)!important
 }
 body[data-motion-template="product-3d"] .page .section::after,
 body[data-motion-template="cinematic"] .page .section::after{
  background:linear-gradient(180deg,rgba(4,9,14,.84),rgba(4,9,14,.23) 55%,rgba(4,9,14,.44))
 }
}
@media(prefers-reduced-motion:reduce){
 body[data-motion-template="product-3d"] .r14-story-rail,
 body[data-motion-template="cinematic"] .r14-story-rail{transition:none!important}
}
`;
export function injectR36Pilot(html){
 if(typeof html!=='string'||!html.includes('</body></html>')||!html.includes('id="r31-story-continuity"'))throw Error('R36 requires complete R31 offline editor');
 if(html.includes('id="r36-pilot-editor"'))throw Error('R36 duplicate injection');
 const browser = String.raw`<script id="r36-pilot-runtime">
(function(){
 const pilot=['product-3d','cinematic'].includes(document.body.dataset.motionTemplate);
 if(!pilot)return;
 const rail=document.querySelector('.r14-story-rail');
 if(!rail)return;
 rail.classList.add('r36-collapsible');
 const btn=document.createElement('button');
 btn.className='r36-nav-toggle';btn.type='button';
 btn.setAttribute('aria-expanded','false');
 btn.setAttribute('aria-label','Open story chapters');
 btn.innerHTML='<span aria-hidden="true">☷</span><span class="r36-nav-caption">CHAPTERS</span>';
 rail.insertBefore(btn,rail.firstChild);
 rail.querySelectorAll('.r14-rail-chapters > button').forEach(ch=>ch.classList.add('r14-rail-chapter'));
 const close=()=>{rail.classList.remove('r36-open');btn.setAttribute('aria-expanded','false');btn.setAttribute('aria-label','Open story chapters')};
 btn.addEventListener('click',()=>{const open=!rail.classList.contains('r36-open');
  rail.classList.toggle('r36-open',open);btn.setAttribute('aria-expanded',String(open));
  btn.setAttribute('aria-label',open?'Close story chapters':'Open story chapters')});
 rail.querySelectorAll('.r14-rail-chapters button').forEach(ch=>ch.addEventListener('click',close));
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&rail.classList.contains('r36-open')){e.preventDefault();e.stopImmediatePropagation();close()}},true);
 document.addEventListener('pointerdown',e=>{if(!rail.contains(e.target))close()},{passive:true});
})();
<\/script>`;
 // Use the current exportDocument chain: the same HTML drives immersive
 // preview, "use template", JSON project save and standalone HTML download.
 const embedScript = `<script id="r36-pilot-editor">
(function(){
 const previous=exportDocument;
 exportDocument=function(){
  const html=previous();
  if(!['product-3d','cinematic'].includes(project.templateId))return html;
  const css=document.getElementById('r36-pilot-css').textContent;
  const script=document.getElementById('r36-pilot-bootstrap').textContent;
  return html.replace('</head>','<style id="r36-fullstage-css">'+css+'</style></head>')
   .replace('</body>','<script id="r36-fullstage-runtime">'+script+'<'+'/script></body>');
 };
 if(window.MotionStudioUnified)window.MotionStudioUnified.build=exportDocument;
})();
</script>`;
 return html.replace('</head>','<style id="r36-pilot-css">'+pilotCss+'</style></head>')
 .replace(/<\/body><\/html>\s*$/,'<script type="text/plain" id="r36-pilot-bootstrap">'+browser.slice(browser.indexOf('>')+1,browser.lastIndexOf('<'))+'</script>'+embedScript+'</body></html>');
}
