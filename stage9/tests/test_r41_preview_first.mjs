import test from 'node:test';import assert from 'node:assert/strict';
import {applyR41PreviewFirst,r41CSS} from '../r41-preview-first-layout.mjs';
test('replaces 34/66 preview with a single visual stage and optional drawer',()=>{
 const original="function setImmersivePreview(enabled){const overlay=$('templatePreview');overlay.classList.toggle('immersive-preview',!!enabled);const button=$('previewImmersive');button.setAttribute('aria-pressed',String(!!enabled));button.textContent=enabled?'退出沉浸':'沉浸预览';button.title=enabled?'返回模板说明和网页双栏预览':'整页展示交互网页';}";
 const close="if($('templatePreview').classList.contains('immersive-preview'))setImmersivePreview(false);else closeTemplatePreview();";
 const toggle="$('previewImmersive').onclick=()=>setImmersivePreview(!$('templatePreview').classList.contains('immersive-preview'));";
 const html='<html><head></head><body><aside class="preview-product-info"></aside><button id="previewImmersive">沉浸预览</button><script>'+original+close+toggle+'</script></body></html>';
 const out=applyR41PreviewFirst(html);
 assert.match(out,/id="r41-preview-first-css"/);
 assert.match(out,/id="previewTemplateInfo"/);
 assert.match(out,/r41-info-open/);
 assert.match(out,/沉浸预览/); // original button text remains, runtime changes on open
 assert.ok(r41CSS.includes('grid-template-columns:minmax(0,1fr)!important'));
 assert.ok(r41CSS.includes('.preview-overlay.r41-info-open .preview-product-info'));
 assert.match(out,/button.textContent=enabled\?'隐藏介绍':'模板信息'/);
 assert.throws(()=>applyR41PreviewFirst(out),/duplicate/);
});
