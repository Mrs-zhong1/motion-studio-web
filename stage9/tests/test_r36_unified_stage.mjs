import test from 'node:test';
import assert from 'node:assert/strict';
import {injectR36Pilot,pilotCss} from '../r36-unified-stage-pilots.mjs';

test('R36 only layers full-stage CSS onto R31 editor and preserves export injection',()=>{
 const source='<html><head><style id="r31-story-continuity"></style></head><body><script>const STORY_CHAPTERS=20;</script></body></html>';
 const html=injectR36Pilot(source);
 assert.ok(html.includes('id="r36-pilot-css"'));
 assert.ok(html.includes('id="r36-pilot-bootstrap"'));
 assert.ok(html.includes('id="r36-pilot-editor"'));
 assert.ok(html.includes('const STORY_CHAPTERS=20'));
 assert.ok(html.indexOf('r36-pilot-editor')>html.indexOf('STORY_CHAPTERS'));
 assert.equal((html.match(/id="r36-pilot-editor"/g)||[]).length,1);
 assert.throws(()=>injectR36Pilot(html),/duplicate injection/);
});
test('R36 keeps real R16 as its only chapter timeline, and two scoped pilot layouts',()=>{
 assert.match(pilotCss,/data-motion-template="product-3d"/);
 assert.match(pilotCss,/data-motion-template="cinematic"/);
 assert.ok(!pilotCss.includes('data-motion-template="fashion"'));
 assert.match(pilotCss,/\.r14-story-rail\.r36-open/);
 assert.match(pilotCss,/\.page \.section \.section-art/);
 assert.match(pilotCss,/prefers-reduced-motion:reduce/);
 assert.ok(!pilotCss.includes('requestAnimationFrame'));
});
