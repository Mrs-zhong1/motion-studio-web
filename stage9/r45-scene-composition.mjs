export const R45_CONTRACT=Object.freeze({families:['print','object','film','plan','play','runway','museum','system'],composition:'scene-integrated',persistentSplitColumns:false});
export const R45_CSS=`
body[data-r38-family] .page .section{position:relative!important;isolation:isolate!important;overflow:hidden}
body[data-r38-family] .page .section .section-art{z-index:0!important}
body[data-r38-family] .page .section .designed-chapter-heading{position:absolute!important;z-index:5!important;width:auto!important;max-width:78%!important}
body[data-r38-family] .page .section::after{content:"";position:absolute;inset:0;z-index:1;pointer-events:none;background:linear-gradient(180deg,#07100b12,transparent 38%,#07100b70)}
html[data-r43-template="agency"] .page{position:relative!important}
html[data-r43-template="agency"] .page .section{min-height:100svh!important}
html[data-r43-template="agency"] .page .section .section-art{inset:0!important;width:100%!important;height:100%!important;max-width:none!important;clip-path:none!important;transform:none!important;object-fit:cover!important}
html[data-r43-template="agency"] .page .section::after{background:linear-gradient(90deg,#101719bd,transparent 85%),linear-gradient(0deg,#101719dc,transparent 55%)!important}
html[data-r43-template="agency"] .page>.r43-agency-intro{position:absolute!important;z-index:14!important;top:13vh!important;left:6vw!important;width:78vw!important;margin:0!important;font-size:clamp(52px,10vw,150px)!important;line-height:.82!important;pointer-events:none}
html[data-r43-template="agency"] .page>.r43-scene-control{position:absolute!important;z-index:15!important;top:4vh!important;left:6vw!important;width:auto!important;margin:0!important;padding:0!important}
html[data-r43-template="agency"] .page>.r43-agency-index{position:absolute!important;z-index:16!important;left:6vw!important;right:6vw!important;bottom:6vh!important;width:auto!important;margin:0!important;display:grid!important;grid-template-columns:repeat(5,minmax(0,1fr))!important;gap:8px!important}
html[data-r43-template="agency"] .r43-agency-index button{min-height:72px!important;padding:12px!important;background:#101719c9!important;backdrop-filter:blur(14px)!important;border-color:#ffffff55!important}
html[data-r43-template="agency"] .page .section .designed-chapter-heading{left:6vw!important;bottom:22vh!important;top:auto!important;width:70vw!important;max-width:78%!important;color:#fff!important;font-size:clamp(36px,6vw,92px)!important;text-shadow:0 3px 24px #0009!important}
html[data-r43-template="saas"] .r43-saas-shell{width:min(100% - 48px,1320px)!important;margin:4vh auto 8vh!important;border-radius:28px!important}
html[data-r43-template="saas"] .r43-saas-workflow{display:flex!important;flex-direction:column!important;align-items:stretch!important;gap:28px!important;padding:clamp(24px,5vw,68px)!important;min-height:0!important}
html[data-r43-template="saas"] .r43-saas-copy{width:100%!important;max-width:none!important;position:relative!important;z-index:2!important}
html[data-r43-template="saas"] .r43-saas-copy h2{max-width:14ch!important;font-size:clamp(38px,6.6vw,88px)!important;line-height:.91!important}
html[data-r43-template="saas"] .r43-saas-preview{width:100%!important;min-height:clamp(240px,34vw,440px)!important;border-radius:22px!important;padding:clamp(20px,4vw,42px)!important}
body[data-r38-family="play"] .page .section .section-art{inset:0!important;width:100%!important;height:100%!important;max-width:none!important;clip-path:none!important;transform:none!important;object-fit:cover!important}\nbody[data-r38-family="play"] .page .section .designed-chapter-heading{left:6%!important;bottom:20%!important;top:auto!important;max-width:78%!important}\nbody[data-r38-family="print"] .page .section .section-art{inset:5% 7% 8%!important;width:86%!important;height:78%!important;max-width:none!important;clip-path:none!important;opacity:.78!important}
body[data-r38-family="print"] .page .section .designed-chapter-heading{left:9%!important;bottom:12%!important;top:auto!important;max-width:72%!important;font-size:clamp(38px,7vw,104px)!important}
body[data-r38-family="object"] .page .section .section-art{inset:5% 12% 8%!important;width:76%!important;height:82%!important;max-width:none!important;clip-path:none!important;transform:none!important}
body[data-r38-family="object"] .page .section .designed-chapter-heading{left:6%!important;bottom:8%!important;top:auto!important;max-width:60%!important}
body[data-r38-family="film"] .page .section .section-art{inset:0!important;width:100%!important;height:100%!important;max-width:none!important;clip-path:none!important;transform:none!important;filter:brightness(.76)!important}
body[data-r38-family="film"] .page .section .designed-chapter-heading{left:8%!important;bottom:12%!important;top:auto!important;width:78%!important;font-size:clamp(40px,7vw,104px)!important}
body[data-r38-family="plan"] .page .section .section-art{inset:8% 8% 12%!important;width:84%!important;height:76%!important;max-width:none!important;clip-path:none!important;transform:none!important;opacity:.72!important}
body[data-r38-family="plan"] .page .section .designed-chapter-heading{left:8%!important;bottom:8%!important;top:auto!important;max-width:72%!important}
body[data-r38-family="runway"] .page .section .section-art{inset:0 22%!important;width:56%!important;height:100%!important;max-width:none!important;clip-path:none!important;transform:none!important}
body[data-r38-family="runway"] .page .section .designed-chapter-heading{left:6%!important;bottom:13%!important;top:auto!important;max-width:65%!important;font-family:Georgia,serif!important;font-style:italic!important}
body[data-r38-family="museum"] .page .section .section-art{inset:7% 16% 13%!important;width:68%!important;height:76%!important;max-width:none!important;clip-path:none!important;border:14px solid #fdfdf9!important}
body[data-r38-family="museum"] .page .section .designed-chapter-heading{left:7%!important;bottom:6%!important;top:auto!important;max-width:80%!important}
body[data-r38-family="system"] .page .section .section-art{inset:8% 7% 12%!important;width:86%!important;height:72%!important;max-width:none!important;clip-path:none!important;transform:none!important}
body[data-r38-family="system"] .page .section .designed-chapter-heading{left:8%!important;bottom:7%!important;top:auto!important;max-width:72%!important}
@media(max-width:760px){html[data-r43-template="agency"] .page>.r43-agency-intro{top:12vh!important;left:18px!important;width:90vw!important;font-size:clamp(48px,14vw,84px)!important}html[data-r43-template="agency"] .page>.r43-agency-index{left:14px!important;right:14px!important;bottom:3vh!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:5px!important}html[data-r43-template="agency"] .r43-agency-index button{min-height:54px!important;padding:8px!important}html[data-r43-template="agency"] .page>.r43-agency-index li:last-child{grid-column:1/-1}html[data-r43-template="agency"] .page .section .designed-chapter-heading{left:18px!important;bottom:30vh!important;width:88vw!important;font-size:clamp(32px,9vw,54px)!important}html[data-r43-template="saas"] .r43-saas-workflow{gap:20px!important;padding:22px!important}body[data-r38-family] .page .section .designed-chapter-heading{left:6%!important;bottom:8%!important;max-width:88%!important;font-size:clamp(30px,9vw,54px)!important}body[data-r38-family="runway"] .page .section .section-art{inset:4% 12%!important;width:76%!important;height:88%!important}}
@media(prefers-reduced-motion:reduce){body[data-r38-family] .page .section .section-art{transform:none!important}}
`;
export function applyR45TemplateComposition(html){
 if(typeof html!=='string'||!html.includes('</head>')||!html.includes('</body>'))throw Error('R45 requires complete editor HTML');
 if(html.includes('id="r45-scene-composition-css"'))throw Error('R45 duplicate injection');
 if(!html.includes('function exportDocument('))throw Error('R45 exportDocument hook missing');
 const hook=`;(function(){const previous=exportDocument;exportDocument=function(){const result=previous();if(!result||!result.includes('</head>'))return result;const css=document.getElementById('r45-scene-composition-css').textContent;return result.replace('</head>','<style id="r45-export-composition">'+css+'</style></head>')}})();`;
 const apiAnchor='window.MotionStudioUnified={undo:';
 if(!html.includes(apiAnchor))throw Error('R45 public API insertion anchor missing');
 let output=html.replace(apiAnchor,hook+apiAnchor);
 const bodyClose=output.lastIndexOf('</body>');
 const headClose=output.indexOf('</head>');
 if(bodyClose<0||headClose<0)throw Error('R45 actual document closing tags missing');
 output=output.slice(0,bodyClose)+'<script type="text/plain" id="r45-composition-source">'+R45_CSS+'</script>'+output.slice(bodyClose);
 return output.slice(0,headClose)+'<style id="r45-scene-composition-css">'+R45_CSS+'</style>'+output.slice(headClose);
}