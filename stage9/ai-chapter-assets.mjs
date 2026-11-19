// Optional R18 AI chapter asset pack. Fail closed in AI-only production mode.
// Expected stage9/ai-assets/manifest.json with 39 unique entries and local files.
import {readFile} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {createHash} from 'node:crypto';
const IDS=['editorial','product-3d','cinematic','architecture','agency','fashion','gallery','saas'];
const COUNTS=Object.fromEntries(IDS.map(id=>[id,id==='editorial'?4:5]));
export async function loadAIChapterAssets(root,{required=false}={}){
  const directory=resolve(root,'ai-assets');
  let raw;
  try {raw=await readFile(join(directory,'manifest.json'),'utf8')}
  catch(e){if(!required&&e.code==='ENOENT')return null;throw new Error('AI media manifest unavailable: '+e.message)}
  let manifest;
  try{manifest=JSON.parse(raw)}catch(e){throw Error('AI media manifest is invalid JSON')}
  const rows=manifest.assets;
  if(!Array.isArray(rows)||rows.length!==39)throw Error('AI media pack must contain exactly 39 chapters');
  const bundles=Object.fromEntries(IDS.map(id=>[id,Array(COUNTS[id]).fill(null)]));
  const names=new Set();
  for(const row of rows){
    const {template,chapter,file,sha256,source,commercialUseTermsChecked}=row;
    if(!IDS.includes(template)||!Number.isInteger(chapter)||chapter<1||chapter>COUNTS[template])
      throw Error('Unexpected template/chapter in AI asset pack');
    if(source!=='AI_GENERATED'||commercialUseTermsChecked!==true)
      throw Error('AI media origin/usage evidence missing: '+template+' '+chapter);
    if(!/^[a-z0-9-]+\.(jpg|jpeg|png|webp)$/i.test(file)||names.has(file))
      throw Error('Unsafe or duplicate AI media file name: '+file);
    names.add(file);
    if(bundles[template][chapter-1])throw Error('Duplicate AI media chapter');
    const bytes=await readFile(join(directory,file));
    const digest=createHash('sha256').update(bytes).digest('hex');
    if(digest!==sha256||bytes.length<1000||bytes.length>5_000_000)
      throw Error('AI media content hash or size invalid: '+file);
    const ext=file.split('.').pop().toLowerCase();
    const mime=ext==='png'?'image/png':ext==='webp'?'image/webp':'image/jpeg';
    bundles[template][chapter-1]={media:'data:'+mime+';base64,'+bytes.toString('base64'),
      source:'ai-generated://'+template+'/'+chapter+'/'+sha256.slice(0,16)};
  }
  if(IDS.some(id=>bundles[id].some(row=>!row)))throw Error('AI media chapters incomplete');
  return {data:bundles,audit:Object.fromEntries(IDS.map(id=>[id,{
    bundledPhotos:COUNTS[id],fallbackChapters:0,total:COUNTS[id],origin:'AI_GENERATED'
  }]))};
}
