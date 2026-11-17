import test from 'node:test';
import assert from 'node:assert/strict';
import {buildR39Film,injectR39Film,r39Runtime,r39CSS} from '../r39-cinematic-timeline.mjs';

const make=(n)=>({title:'Film test',templateId:'cinematic',sections:Array.from({length:n},(_,i)=>({
 uid:'act-'+(i+1),id:'pinned-story',
 text:'Unique act '+(i+1),image:'data:image/png;base64,aGVsbG8=',imageFocusX:i*10,imageFocusY:50
}))});
test('Five authored acts compile into ONE sticky stage, 5 images, 5 unique titles and 5 menu stops',()=>{
 const doc=buildR39Film(make(5));
 assert.match(doc,/data-r39-film="continuous"/);
 assert.equal((doc.match(/class="r39-frame"/g)||[]).length,5);
 assert.equal((doc.match(/class="r39-caption"/g)||[]).length,5);
 assert.equal((doc.match(/data-seek="/g)||[]).length,5);
 assert.equal((doc.match(/class="r39-stage"/g)||[]).length,1);
 assert.equal((doc.match(/class="r39-story"/g)||[]).length,1);
 assert.equal((doc.match(/<h1>/g)||[]).length,5);
 assert.ok(doc.includes('Unique act 5'));
 assert.ok(!doc.includes('r14-story-rail'));
 assert.ok(!doc.includes('r16-linked-chapter'));
 assert.ok(!doc.includes('r37-stage'));
});
test('Three-act and altered content reuse the exact same general camera runtime',()=>{
 const small=buildR39Film(make(3));
 assert.equal((small.match(/class="r39-frame"/g)||[]).length,3);
 assert.ok(small.includes('03 / 03'));
 const changed=make(5);changed.sections[1].text='MY CUSTOM SCENE';changed.sections[1].image='data:image/jpeg;base64,custom';
 const doc=buildR39Film(changed);
 assert.ok(doc.includes('MY CUSTOM SCENE'));
 assert.ok(doc.includes('data:image/jpeg;base64,custom'));
 assert.equal(doc.match(/class="r39-caption"/g).length,5);
});
test('Cinematic export does not inject remote scripts and respects motion preferences',()=>{
 assert.ok(r39CSS.includes('prefers-reduced-motion:reduce'));
 assert.ok(r39Runtime.includes('progress*(n-1)'));
 assert.ok(r39Runtime.includes('requestAnimationFrame(update)'));
 assert.ok(r39Runtime.includes('data-seek'));
 assert.doesNotMatch(buildR39Film(make(5)),/<script src=/);
 const html='<html><head></head><body><script id="r38-editor-director"></script></body></html>';
 const injected=injectR39Film(html);
 assert.match(injected,/id="r39-film-editor"/);
 assert.match(injected,/previous=exportDocument/);
 assert.throws(()=>injectR39Film(injected),/duplicate/);
});
