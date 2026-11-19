import test from 'node:test';
import assert from 'node:assert/strict';
import {applyStoryArtDirection,storyArtDirectionCSS,storyTemplateIds} from '../story-art-direction-r23.mjs';
test('R23 all eight story genres have unique art-direction clauses',()=>{
 assert.equal(storyTemplateIds.length,8);
 assert.equal(new Set(storyTemplateIds).size,8);
 for(const id of storyTemplateIds) assert.ok(storyArtDirectionCSS.includes('.page[data-template="'+id+'"]'),id);
});
test('R23 shared output preserves story timeline and camera',()=>{
 const html='<html><head></head><body><script>const cameraPath=1,storyTimeline=2;</script></body></html>';
 const out=applyStoryArtDirection(html);
 assert.match(out,/cameraPath=1,storyTimeline=2/);
 assert.equal((out.match(/id="r23-story-art-direction"/g)||[]).length,1);
 assert.throws(()=>applyStoryArtDirection(out),/duplicate injection/);
});
test('R23 legibility, mobile, and motion preferences',()=>{
 assert.ok(storyArtDirectionCSS.includes('max-width:650px'));
 assert.ok(storyArtDirectionCSS.includes('prefers-reduced-motion:reduce'));
 assert.ok(storyArtDirectionCSS.includes('pointer-events:none'));
 assert.ok(storyArtDirectionCSS.includes('text-wrap:balance'));
 assert.ok(!/https?:\/\/|@import/i.test(storyArtDirectionCSS));
 assert.throws(()=>applyStoryArtDirection('bad'),/head missing/);
});
