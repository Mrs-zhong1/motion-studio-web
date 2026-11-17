import test from 'node:test';
import assert from 'node:assert/strict';
import {applyR37StoryDirector,r37Css,r37Runtime} from '../r37-story-director.mjs';

test('R37 only affects the two active pilots and keeps a single R16 scroll engine',()=>{
 const source='<html><head></head><body><style id="r36-pilot-editor"></style><script>const original=1;</script></body></html>';
 const result=applyR37StoryDirector(source);
 assert.match(result,/id="r37-director-css"/);
 assert.match(result,/id="r37-director-runtime"/);
 assert.match(result,/id="r37-editor-director"/);
 assert.match(result,/const original=1/);
 assert.throws(()=>applyR37StoryDirector(result),/duplicate/);
 assert.match(r37Css,/data-motion-template="cinematic"/);
 assert.match(r37Css,/r36-nav-toggle/);
 assert.match(r37Css,/r37-stage/);
 assert.match(r37Css,/position:sticky/);
 assert.match(r37Css,/display:none!important/);
 assert.match(r37Runtime,/dataset\.motionTemplate!=='cinematic'/);
 assert.match(r37Runtime,/r16-incoming/);
 assert.ok(!r37Runtime.includes('requestAnimationFrame'));
 assert.ok(!r37Runtime.includes("addEventListener('scroll'"));
});
test('R37 rejects incomplete editor',()=>{
 assert.throws(()=>applyR37StoryDirector('<html></html>'),/requires complete/);
});
