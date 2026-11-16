import assert from 'node:assert/strict';
import {mkdtemp, mkdir, writeFile, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
import {loadAIChapterAssets} from './ai-chapter-assets.mjs';

const root=await mkdtemp(join(tmpdir(),'motion-ai-gate-'));
try{
  assert.equal(await loadAIChapterAssets(root),null);
  await assert.rejects(()=>loadAIChapterAssets(root,{required:true}),/manifest unavailable/);
  const dir=join(root,'ai-assets');
  await mkdir(dir);
  await writeFile(join(dir,'manifest.json'),JSON.stringify({assets:[]}));
  await assert.rejects(()=>loadAIChapterAssets(root,{required:true}),/exactly 39/);
  const rows=[];
  for(const template of ['editorial','product-3d','cinematic','architecture','agency','fashion','gallery','saas']){
    const count=template==='editorial'?4:5;
    for(let i=1;i<=count;i++){
      const name=template+'-'+i+'.png';
      const bytes=Buffer.alloc(1400, i+23);
      await writeFile(join(dir,name),bytes);
      rows.push({template,chapter:i,file:name,source:'AI_GENERATED',commercialUseTermsChecked:true,sha256:createHash('sha256').update(bytes).digest('hex')});
    }
  }
  await writeFile(join(dir,'manifest.json'),JSON.stringify({assets:rows}));
  const pack=await loadAIChapterAssets(root,{required:true});
  assert.equal(Object.values(pack.data).reduce((acc,x)=>acc+x.length,0),39);
  assert.equal(pack.data.editorial[0].source.startsWith('ai-generated://'),true);
  rows[0].commercialUseTermsChecked=false;
  await writeFile(join(dir,'manifest.json'),JSON.stringify({assets:rows}));
  await assert.rejects(()=>loadAIChapterAssets(root,{required:true}),/origin\/usage evidence missing/);
  console.log('AI asset bundle contract PASS: 39 slots, source and usage checks, fail-closed.');
}finally{await rm(root,{recursive:true,force:true})}
