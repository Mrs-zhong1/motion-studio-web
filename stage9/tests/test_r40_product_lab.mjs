import test from 'node:test';import assert from 'node:assert/strict';
import {r40CSS,r40Runtime,injectR40Product} from '../r40-product-lab.mjs';
test('R40 uses existing real shader/light controls and only product template',()=>{
 assert.match(r40Runtime,/motion-studio-product-control/);
 assert.match(r40Runtime,/motion-studio-product-applied/);
 assert.match(r40Runtime,/contentWindow\?\.postMessage/);
 assert.match(r40Runtime,/dataset\.motionTemplate!=='product-3d'/);
 for(const key of ['light','material','camera','backdrop'])assert.match(r40Runtime,new RegExp("'"+key+"'"));
 for(const val of ['warm','cool','neutral','original','graphite','pearl','front','angle','detail','noir','porcelain','cobalt'])
  assert.match(r40Runtime,new RegExp("'"+val+"'"));
 assert.match(r40CSS,/data-motion-template="product-3d"/);
});
test('R40 editor wrapper cannot replace existing Cinematic director',()=>{
 const base='<html><head></head><body><script id="r39-film-editor"></script></body></html>';
 const out=injectR40Product(base);
 assert.match(out,/id="r39-film-editor"/);
 assert.match(out,/id="r40-product-editor"/);
 assert.match(out,/id="r40-product-runtime"/);
 assert.match(out,/project.templateId!=='product-3d'/);
 assert.throws(()=>injectR40Product(out),/duplicate/);
});
