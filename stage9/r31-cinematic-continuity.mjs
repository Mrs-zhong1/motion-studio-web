// R31 cinematic scroll seam art direction: visual refinement of the EXISTING
// R16 scroll variables; it does not install a second timeline or event loop.
export const r31SeamCSS = `
/* R31 - cinematic chapter shot continuity. Read only R16's current scroll values. */
body.r16-story-ready .page[data-template="cinematic"] .section.designed-chapter {
  --r31-warm:#dc9668;
  --r31-cool:#142234;
  isolation:isolate;
  background-color:var(--r31-cool);
}
body.r16-story-ready .page[data-template="cinematic"] .section.designed-chapter .section-art {
  background-size:cover!important;
  background-repeat:no-repeat!important;
  mix-blend-mode:normal;
  /* Do not dim real artwork: R16's clip-path already handles the reveal. */
  opacity:1!important;
  filter:contrast(1.08) saturate(.91);
  transition:opacity .075s linear,filter .1s linear;
  /* Existing clip-path masks and camera depth are preserved. */
}
body.r16-story-ready .page[data-template="cinematic"] .section.designed-chapter .motion-atmosphere {
  opacity:calc(.22 + (1 - var(--r16-incoming,1))*.23);
  mix-blend-mode:screen;
}
body.r16-story-ready .page[data-template="cinematic"] .section.designed-chapter .designed-chapter-heading {
  max-width:min(78%,940px);
  text-shadow:0 3px 36px rgba(1,8,16,.94),0 2px 6px rgba(0,0,0,.65);
}
body.r16-story-ready .page[data-template="cinematic"] .section.designed-chapter .designed-chapter-copy,
body.r16-story-ready .page[data-template="cinematic"] .section.designed-chapter .designed-chapter-description {
  text-shadow:0 2px 22px rgba(0,5,13,.95);
}
body.r16-story-ready .page[data-template="cinematic"] .section.designed-chapter .r15-scene-mark {
  color:#eed6bd;
  opacity:.91;
}
/* Camera movement + reveal remain motion-safe and readable on mobile. */
@media(max-width:720px){
 body.r16-story-ready .page[data-template="cinematic"] .section.designed-chapter .section-art {
  opacity:1!important;
  filter:contrast(1.06) saturate(.83);
 }
 body.r16-story-ready .page[data-template="cinematic"] .section.designed-chapter .designed-chapter-heading {
  max-width:91%;
  text-shadow:0 2px 24px rgba(0,5,12,.95);
 }
 /* R29 train-window continuation imported into Cinematic chapter 03:
    preserve the carriage/window edge alongside mountains on portrait screens.
    Keep original R16 camera offsets instead of replacing the motion engine. */
 body.r16-story-ready .page[data-template="cinematic"] .section.designed-chapter:nth-of-type(3) .section-art {
  background-position:
    calc(34% + var(--motion-pointer-x,0px) + var(--r16-photo-x,0px))
    calc(50% + var(--motion-pointer-y,0px) + var(--r16-photo-y,0px)) !important;
 }
}
@media(prefers-reduced-motion:reduce){
 body.r16-story-ready .page[data-template="cinematic"] .section.designed-chapter .section-art {
  opacity:1!important;
  clip-path:none!important;
  transition:none!important;
 }
 body.r16-story-ready .page[data-template="cinematic"] .section.designed-chapter .motion-atmosphere{
  transition:none!important;transform:none!important;
 }
}
`;
export function applyR31StoryContinuity(html){
 if(typeof html!=='string'||!html.includes('</head>')||!html.includes('</body></html>'))
  throw Error('R31 requires complete HTML');
 if(html.includes('id="r31-story-continuity"'))throw Error('R31 double injection');
 const style='<style id="r31-story-continuity">'+r31SeamCSS+'</style>';
 const script=`<script id="r31-story-export-parity">
(()=>{
 const originalExport=exportDocument;
 exportDocument=function(){
   const output=originalExport();
   const css=document.getElementById('r31-story-continuity')?.textContent||'';
   if(!css||output.includes('id="r31-export-story-continuity"'))return output;
   return output.replace('</head>','<style id="r31-export-story-continuity">'+css+'</style></head>');
 };
 if(window.MotionStudioUnified)window.MotionStudioUnified.build=exportDocument;
})();
</script>`;
 return html.replace('</head>',style+'</head>')
   .replace(/<\/body><\/html>$/,script+'</body></html>');
}
