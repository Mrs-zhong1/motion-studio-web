import test from 'node:test';
import assert from 'node:assert/strict';
import {applyVisualRefinement,visualRefinementCSS} from '../visual-refinement-r22.mjs';

test('R22 injects exactly one style layer without disturbing story engine',()=>{
 const input='<!doctype html><html><head><title>Motion Studio</title></head><body><script>const storyTimeline={camera:1};</script></body></html>';
 const output=applyVisualRefinement(input);
 assert.equal((output.match(/id="r22-visual-refinement"/g)||[]).length,1);
 assert.match(output, /storyTimeline=\{camera:1\}/);
 assert.match(output, /<style id="r22-visual-refinement">/);
 assert.throws(()=>applyVisualRefinement(output),/duplicate injection/);
});
test('R22 responsive and reduced-motion contracts',()=>{
 for(const required of ['.discovery-header h1','.template-card','.preview-device','.editor-view','.template-art.has-image','max-width:820px','max-width:430px','prefers-reduced-motion:reduce','focus-visible']){
  assert.ok(visualRefinementCSS.includes(required),required);
 }
 assert.doesNotMatch(visualRefinementCSS,/@import|https?:\/\//);
});
test('R22 refuses invalid HTML instead of silently skipping',()=>{
 assert.throws(()=>applyVisualRefinement('<body></body>'),/head missing/);
});
