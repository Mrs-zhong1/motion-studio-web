import test from 'node:test';import assert from 'node:assert/strict';import {R45_CONTRACT,R45_CSS,applyR45TemplateComposition} from '../r45-scene-composition.mjs';
const fixture='<!doctype html><html><head></head><body><script>function exportDocument(){return "<html><head></head><body></body></html>"};window.MotionStudioUnified={undo:0};</script></body></html>';
test('R45 covers eight scene families',()=>{assert.equal(R45_CONTRACT.families.length,8);assert.equal(R45_CONTRACT.composition,'scene-integrated');assert.equal(R45_CONTRACT.persistentSplitColumns,false);for(const f of ['print','object','film','plan','play','runway','museum','system'])assert.ok(R45_CSS.includes('data-r38-family="'+f+'"'))});
test('Agency project index sits in normal flow between hero and next case',()=>{assert.match(R45_CSS,/r43-agency-index\{position:relative!important/);assert.match(R45_CSS,/r43-agency-index button\{min-height:72px/);assert.match(R45_CSS,/grid-template-columns:repeat\(2,minmax\(0,1fr\)\)!important/)});
test('SaaS workflow is a balanced desktop grid and stacks on mobile',()=>{assert.match(R45_CSS,/r43-saas-workflow\{display:grid!important;grid-template-columns:minmax\(260px/);assert.match(R45_CSS,/r43-saas-workflow\{grid-template-columns:1fr!important/);assert.match(R45_CSS,/r43-saas-preview\{width:100%!important/)});
test('R45 styles editor and standalone export',()=>{const out=applyR45TemplateComposition(fixture);assert.match(out,/id="r45-scene-composition-css"/);assert.match(out,/id="r45-composition-source"/);assert.match(out,/r45-export-composition/);assert.throws(()=>applyR45TemplateComposition(out),/duplicate/)});
test('R45 fails closed if export hook is missing',()=>assert.throws(()=>applyR45TemplateComposition('<html><head></head><body></body></html>'),/hook missing/));
test('R45 family rules use real CSS line breaks, not escaped nbody selectors',()=>{
 assert.doesNotMatch(R45_CSS,/\\nbody/);
 for(const family of ['play','print','object','film','plan','runway','museum','system'])
  assert.ok(R45_CSS.includes('\nbody[data-r38-family="'+family+'"]'), 'missing independent '+family+' selector');
});
