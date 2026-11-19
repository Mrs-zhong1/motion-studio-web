import test from 'node:test';import assert from 'node:assert/strict';
import {buildR42Editorial,injectR42Editorial,e42CSS,e42Runtime} from '../r42-editorial-story-spreads.mjs';
const project=()=>({templateId:'editorial',title:'Editorial Demo',sections:Array.from({length:4},(_,i)=>({text:'PRINT STORY '+(i+1),image:'data:image/jpeg;base64,section'+(i+1),imageFocusX:50,imageFocusY:40}))});
test('Four magazine spreads contain exactly one image and one title each, no dark iframe block',()=>{
 const html=buildR42Editorial(project());
 assert.match(html,/data-e42-editorial="coherent-print"/);
 assert.equal((html.match(/class="e42-spread"/g)||[]).length,4);
 assert.equal((html.match(/class="e42-photostage"/g)||[]).length,4);
 assert.equal((html.match(/class="e42-type"/g)||[]).length,4);
 assert.equal((html.match(/class="e42-image"/g)||[]).length,4);
 assert.equal((html.match(/data-seek="/g)||[]).length,4);
 assert.equal((html.match(/<h1>/g)||[]).length,4);
 for(let i=1;i<=4;i++)assert.ok(html.includes('PRINT STORY '+i));
 assert.doesNotMatch(html,/<iframe|r14-story-rail|r38-marker|r37-stage|designed-chapter-heading/);
});
test('Editorial supports user edited title and photo and accessible reduced motion',()=>{
 const p=project();p.sections[2].text='USER REPLACEMENT';p.sections[2].image='data:image/png;base64,replace';
 const html=buildR42Editorial(p);
 assert.match(html,/USER REPLACEMENT/);
 assert.match(html,/data:image\/png;base64,replace/);
 assert.ok(e42CSS.includes('prefers-reduced-motion:reduce'));
 assert.ok(e42CSS.includes('position:sticky'));
 assert.ok(e42Runtime.includes('requestAnimationFrame(update)'));
 assert.ok(e42Runtime.includes('data-seek'));
});
test('Editor export intercept only Editorial, leaving seven other art directions unchanged',()=>{
 const src='<html><head></head><body><style id="r41-preview-first-css"></style></body></html>';
 const html=injectR42Editorial(src);
 assert.match(html,/id="r42-editorial-director"/);
 assert.match(html,/project.templateId==="editorial"/);
 assert.match(html,/return old\(\)/);
 assert.throws(()=>injectR42Editorial(html),/duplicate/);
});
