/** R44 preview-first single-canvas template experience. */
export const R44_CONTRACT=Object.freeze({preview:'single-canvas',metadata:'toolbar',chapterNavigation:'scene-overlay-filmstrip',persistentSidebars:false,responsive:true});
export const R44_CSS=String.raw`
#templatePreview .preview-product-layout{display:block!important;position:relative!important;min-height:0!important;height:calc(100dvh - 68px)!important;background:#080a08!important}
#templatePreview .preview-product-info{display:none!important}
#templatePreview .preview-device{height:100%!important;min-height:0!important;padding:0!important;display:flex!important;align-items:stretch!important;justify-content:stretch!important;background:#080a08!important}
#templatePreview .preview-device iframe{display:block;width:100%!important;height:100%!important;max-width:none!important;border:0!important;border-radius:0!important;box-shadow:none!important}
#templatePreview .preview-device.mobile{align-items:center!important;justify-content:center!important;padding:12px!important}
#templatePreview .preview-device.mobile iframe{width:min(390px,calc(100vw - 24px))!important;height:calc(100% - 24px)!important;max-height:850px;border:7px solid #333a35!important;border-radius:28px!important;box-shadow:0 20px 70px #0009!important}
#templatePreview #r17PreviewFilmstrip{position:absolute;z-index:8;left:50%;bottom:18px;transform:translateX(-50%);display:flex;gap:7px;max-width:min(92vw,860px);padding:8px 10px;background:#101612d9;border:1px solid #ffffff28;border-radius:14px;backdrop-filter:blur(16px);overflow-x:auto;scrollbar-width:thin}
#templatePreview #r17PreviewFilmstrip button{position:relative;flex:0 0 72px;width:72px;height:48px;border:1px solid #ffffff30;border-radius:6px;padding:0;overflow:hidden;background:#29332c}
#templatePreview #r17PreviewFilmstrip img{width:100%;height:100%;object-fit:cover}
#templatePreview #r17PreviewFilmstrip small{position:absolute;left:4px;bottom:3px;padding:2px 4px;background:#000a;color:#fff;font:9px ui-monospace,monospace}
#templatePreview #r17PreviewFilmstrip button[aria-current="step"]{outline:2px solid #d9ff67;outline-offset:2px}
#templatePreview .preview-toolbar{position:relative;z-index:12}
#templatePreview #r30TrialPreviewButton{position:absolute;z-index:10;right:18px;bottom:22px;max-width:190px;background:#f6eed9;color:#171b1d;border:1px solid #cab98b;border-radius:8px;padding:10px 13px;font-weight:700;box-shadow:0 8px 28px #0007}
#templatePreview #r30TrialPreviewStatus{position:absolute;z-index:10;right:18px;bottom:70px;max-width:260px;padding:6px 9px;border-radius:6px;background:#101612d9;color:#f4f0df;font-size:11px}
@media(max-width:760px){#templatePreview #r30TrialPreviewButton{right:10px;bottom:58px;max-width:150px;padding:8px 10px;font-size:11px}#templatePreview #r30TrialPreviewStatus{right:10px;bottom:105px;max-width:calc(100vw - 24px)}}
@media(max-width:760px){#templatePreview .preview-toolbar{height:auto;min-height:64px;grid-template-columns:1fr auto;padding:8px 10px;gap:6px}#templatePreview .preview-device-controls{grid-column:1;grid-row:2}#templatePreview .preview-actions{grid-column:2;grid-row:1/3;flex-wrap:wrap;max-width:48vw}#templatePreview .preview-actions button{font-size:10px;padding:7px}#templatePreview .preview-product-layout{height:calc(100dvh - 92px)!important}#templatePreview #r17PreviewFilmstrip{bottom:8px;max-width:calc(100vw - 18px);padding:6px}#templatePreview #r17PreviewFilmstrip button{flex-basis:56px;width:56px;height:40px}}
@media(prefers-reduced-motion:reduce){#templatePreview *{scroll-behavior:auto!important;transition-duration:0s!important}}
`;
export function applyR44TemplateExperience(html){
 if(typeof html!=='string'||!html.includes('</head>')||!html.includes('</body>'))throw Error('R44 requires complete editor HTML');
 if(html.includes('id="r44-single-canvas-css"'))throw Error('R44 duplicate injection');
 const anchor="r17RenderFilmstrip(id);$('previewClose').focus();";
 if(!html.includes(anchor))throw Error('R44 chapter filmstrip relocation anchor missing');
 let out=html.replace('</head>','<style id="r44-single-canvas-css">'+R44_CSS+'</style></head>');
 return out.replace(anchor,"r17RenderFilmstrip(id);const r44Strip=$('r17PreviewFilmstrip');if(r44Strip&&r44Strip.parentElement!==$('previewDevice'))$('previewDevice').append(r44Strip);const r30Button=$('r30TrialPreviewButton'),r30Status=$('r30TrialPreviewStatus');if(r30Button&&r30Button.parentElement!==$('previewDevice'))$('previewDevice').append(r30Button);if(r30Status&&r30Status.parentElement!==$('previewDevice'))$('previewDevice').append(r30Status);$('previewClose').focus();");
}
