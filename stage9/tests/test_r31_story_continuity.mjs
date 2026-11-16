import test from 'node:test';
import assert from 'node:assert/strict';
import {applyR31StoryContinuity,r31SeamCSS} from '../r31-cinematic-continuity.mjs';
test('R31 integrates only cinematic visual continuity with R16 values',()=>{
 const html='<html><head></head><body><script>const registry=20;const r16=1;</script></body></html>';
 const updated=applyR31StoryContinuity(html);
 assert.ok(updated.includes('id="r31-story-continuity"'));
 assert.ok(updated.includes('id="r31-story-export-parity"'));
 assert.ok(updated.includes('const registry=20;const r16=1'));
 assert.equal((updated.match(/id="r31-story-continuity"/g)||[]).length,1);
 assert.ok(updated.lastIndexOf('r31-story-export-parity')>updated.lastIndexOf('const registry=20'));
 assert.throws(()=>applyR31StoryContinuity(updated),/double injection/);
 assert.match(r31SeamCSS,/page\[data-template="cinematic"\]/);
 assert.match(r31SeamCSS,/--r16-incoming/);
 assert.match(r31SeamCSS,/prefers-reduced-motion:reduce/);
 assert.ok(!r31SeamCSS.includes('requestAnimationFrame'));
 assert.ok(!r31SeamCSS.includes('@import'));
});
test('R31 rejects partial HTML',()=>{
 assert.throws(()=>applyR31StoryContinuity('<head></head>'),/complete HTML/);
});
