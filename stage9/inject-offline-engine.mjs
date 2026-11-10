import {Buffer} from 'node:buffer';
export function injectOfflineEngine(editor,engine){
 if(!engine||engine.length<100000)throw Error('Bundled engine too small');
 const signature='function stage9LabPage(conf){';
 if(!editor.includes(signature))throw Error('Stage9 GLB section renderer not found');
 if(editor.includes('stage9ThreeEngine=atob('))throw Error('Already injected');
 const start=editor.indexOf(signature),end=editor.indexOf('\nfunction ',start+signature.length);
 if(end<0)throw Error('Unable to isolate Stage9 renderer function');
 const fn=editor.slice(start,end);
 const anchor='return stage9LabBase.replace(\'<script id="motion-stage8-runtime">\'';
 if(fn.split(anchor).length!==2)throw Error('Expected exactly one GLB injection anchor');
 const pos=fn.indexOf(anchor),stop=fn.indexOf(';',pos);
 if(stop<0)throw Error('GLB injection statement missing terminator');
 const orig=fn.slice(pos,stop+1);
 const transformed=orig.replace('return stage9LabBase.replace(','const page=stage9LabBase.replace(')+
   "\n return page.replace('</body>','<script>'+stage9ThreeEngine+'</'+'script></body>');";
 const embedded=Buffer.from(engine,'utf8').toString('base64');
 const result=editor.slice(0,start)+ 'const stage9ThreeEngine=atob("'+embedded+'");\n'+fn.slice(0,pos)+transformed+fn.slice(stop+1)+editor.slice(end);
 if(result===editor||!result.includes("return page.replace('</body>'"))throw Error('Injection failed');
 return result;
}