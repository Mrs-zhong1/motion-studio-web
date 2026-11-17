import test from 'node:test';
import assert from 'node:assert/strict';
import {R38_DIRECTIONS,r38CSS,r38Runtime,applyR38EightDirectors} from '../r38-eight-art-directions.mjs';

test('exactly eight distinct composition families and interaction systems',()=>{
 const templates=['editorial','product-3d','cinematic','architecture','agency','fashion','gallery','saas'];
 assert.deepEqual(Object.keys(R38_DIRECTIONS),templates);
 const families=Object.values(R38_DIRECTIONS).map(row=>row[0]);
 assert.equal(new Set(families).size,8);
 const interactions=Object.values(R38_DIRECTIONS).map(row=>row[3]);
 assert.equal(new Set(interactions).size,8);
 for(const family of families)assert.match(r38CSS,new RegExp('data-r38-family="'+family+'"'));
 for(const name of templates)assert.match(r38Runtime,new RegExp('"'+name+'"'));
});
test('all eight templates preserve actual photo and 3D elements, no universal layout overwrite',()=>{
 assert.match(r38CSS,/data-r38-family="print"/);
 assert.match(r38CSS,/data-r38-family="object"/);
 assert.match(r38CSS,/data-r38-family="film"/);
 assert.match(r38CSS,/data-r38-family="plan"/);
 assert.match(r38CSS,/data-r38-family="play"/);
 assert.match(r38CSS,/data-r38-family="runway"/);
 assert.match(r38CSS,/data-r38-family="museum"/);
 assert.match(r38CSS,/data-r38-family="system"/);
 assert.doesNotMatch(r38CSS,/body\[data-r38-family\] \.page \.section\s*\{/);
 assert.doesNotMatch(r38Runtime,/requestAnimationFrame/);
 assert.doesNotMatch(r38Runtime,/addEventListener\(['"]scroll/);
});
test('single insertion after R37 with HTML export preservation and dedup',()=>{
 const base='<html><head></head><body><script id="r37-editor-director">const ORIGINAL=1;</script></body></html>';
 const html=applyR38EightDirectors(base);
 assert.equal((html.match(/id="r38-editor-director"/g)||[]).length,1);
 assert.match(html,/id="r38-director-runtime"/);
 assert.match(html,/id="r38-director-css"/);
 assert.match(html,/ORIGINAL=1/);
 assert.match(html,/r38-export-style/);
 assert.match(html,/r38-export-runtime/);
 assert.throws(()=>applyR38EightDirectors(html),/duplicate injection/);
});
