// R15-04: Embed secondary demo photographs into the *offline* HTML at build time.
// Builds never leave external image links as runtime dependencies. Failed downloads
// become explicit fallback entries in BUILD_MANIFEST rather than fake photos.
import {readFile} from 'node:fs/promises';
import {resolve} from 'node:path';

export function readDemoPhotoCatalog(source){
 const thumbs=source.match(/const templateThumbnailImages=\{([\s\S]*?)\};/)?.[1];
 const extras=source.match(/const templateExtraPhotos=\{([\s\S]*?)\};/)?.[1];
 if(!thumbs||!extras)throw Error('Template photography source catalog missing');
 const hero={};
 for(const match of thumbs.matchAll(/'([a-z0-9-]+)'\s*:\s*'(https:\/\/images\.unsplash\.com\/photo-[^']+)'/g))
  hero[match[1]]=match[2];
 const secondary={};
 for(const match of extras.matchAll(/'([a-z0-9-]+)'\s*:\s*\[([^\]]*)\]/g))
  secondary[match[1]]=[...match[2].matchAll(/'([a-z0-9-]+)'/g)].map(item=>item[1]);
 const ids=['editorial','product-3d','cinematic','architecture','agency','fashion','gallery','saas'];
 for(const id of ids)if(!hero[id]||!secondary[id]||secondary[id].length<3)
  throw Error('Missing complete photography sources for '+id);
 return {ids,hero,secondary};
}

export async function bundleChapterPhotos(source,root){
 const {ids,hero,secondary}=readDemoPhotoCatalog(source);
 const output={},results={};
 const download=async photo=>{
  const url='https://images.unsplash.com/'+photo+'?w=840&q=68&fm=jpg&fit=crop';
  // Build may run in a network-restricted environment. Preserve honest fallback.
  if(process.env.MOTION_SKIP_CHAPTER_PHOTO_NETWORK==='1')return null;
  try{
   const controller=new AbortController();
   const timeout=setTimeout(()=>controller.abort(),9500);
   try{
    const res=await fetch(url,{signal:controller.signal,headers:{'Accept':'image/jpeg'}});
    if(!res.ok||!String(res.headers.get('content-type')).startsWith('image/'))return null;
    const buffer=Buffer.from(await res.arrayBuffer());
    if(buffer.length<1000||buffer.length>450000||buffer[0]!==0xff||buffer[1]!==0xd8)return null;
    return 'data:image/jpeg;base64,'+buffer.toString('base64');
   }finally{clearTimeout(timeout)}
  }catch{return null}
 };
 // Bound the number of simultaneous external connections, avoiding CDNs' 429s.
 const tasks=[];
 for(const id of ids){
  output[id]=[];
  const heroFile=await readFile(resolve(root,'template-thumbnails',id+'.jpg'));
  output[id].push({media:'data:image/jpeg;base64,'+heroFile.toString('base64'),source:hero[id]});
  for(const photo of secondary[id]){
   tasks.push({id,photo,source:'https://images.unsplash.com/'+photo+'?w=1000&q=75',
      slot:output[id].push(null)-1});
  }
 }
 let cursor=0;
 await Promise.all(Array.from({length:4},async()=>{
  while(cursor<tasks.length){
   const t=tasks[cursor++];
   const media=await download(t.photo);
   output[t.id][t.slot]={media,source:t.source};
  }
 }));
 for(const id of ids){
  results[id]={bundledPhotos:output[id].filter(item=>item.media).length,
   fallbackChapters:output[id].filter(item=>!item.media).length,
   total:output[id].length};
 }
 return {data:output,audit:results};
}
