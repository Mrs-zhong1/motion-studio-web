import test from 'node:test';
import assert from 'node:assert/strict';
import {R43_PILOTS,r43CSS,r43Runtime,applyR43TemplatePilots} from '../r43-immersive-template-pilots.mjs';

test('R43 defines two deliberately different interaction models',()=>{
 assert.equal(R43_PILOTS.agency.model,'project-index');
 assert.equal(R43_PILOTS.saas.model,'workflow-demo');
 assert.notEqual(R43_PILOTS.agency.layout,R43_PILOTS.saas.layout);
 assert.notEqual(R43_PILOTS.agency.interaction,R43_PILOTS.saas.interaction);
});
test('R43 keeps the template as one canvas and does not add permanent sidebars',()=>{
 assert.match(r43CSS,/r43-agency-index/);
 assert.match(r43CSS,/r43-saas-workflow/);
 assert.doesNotMatch(r43CSS,/grid-template-columns:\s*minmax\(0,\s*\d+fr\)\s+minmax\(0,\s*\d+fr\)/);
 assert.doesNotMatch(r43Runtime,/position:\s*fixed/);
});
test('R43 injects only into Agency and SaaS exported projects and preserves other templates',()=>{
 const fixture='<html><head></head><body><script>function exportDocument(){return "<html><head></head><body><main class=page></main></body></html>"};const project={templateId:"agency"};window.MotionStudioUnified={undo:0};</script></body></html>';
 const out=applyR43TemplatePilots(fixture);
 assert.match(out,/r43-template-pilot-css/);
 assert.match(out,/r43-template-pilot-runtime/);assert.match(out,/window\.MotionStudioUnified=\{undo:/);assert.doesNotMatch(out,/r43-template-pilot-director/);
 assert.match(out,/const id=project&&project.templateId/);
 assert.throws(()=>applyR43TemplatePilots(out),/duplicate/);
});
test('Agency pilot reuses the source hero and avoids duplicate title/status navigation',()=>{
 assert.doesNotMatch(r43Runtime,/WORK THAT <em>MOVES<\/em> PEOPLE/);
 assert.doesNotMatch(r43Runtime,/SELECT A CASE · SCROLL TO EXPLORE/);
 assert.match(r43Runtime,/sections\[0\]\.after\(index\)/);
});
test('Agency project index follows scroll position and keyboard focus',()=>{
 assert.match(r43Runtime,/new IntersectionObserver/);
 assert.match(r43Runtime,/button\.addEventListener\('focus'/);
 assert.match(r43Runtime,/const setActive=/);
});
test('R43 runtime provides scene-linked case navigation and an actionable SaaS workflow',()=>{
 assert.match(r43Runtime,/scrollIntoView/);
 assert.match(r43Runtime,/Capture/);
 assert.match(r43Runtime,/Shape/);
 assert.match(r43Runtime,/Deliver/);
 assert.match(r43Runtime,/aria-pressed/);
});
