import {Buffer} from 'node:buffer';
export function injectOfflineEngine(editor,engine){
 if(!engine||engine.length<100000)throw Error('Bundled engine too small');
 const signature='function stage9LabPage(conf){';
 if(!editor.includes(signature))throw Error('Stage9 GLB section renderer not found');
 if(editor.includes('stage9ThreeEngineURL='))throw Error('Already injected');
 const start=editor.indexOf(signature),end=editor.indexOf('\nfunction ',start+signature.length);
 if(end<0)throw Error('Unable to isolate Stage9 renderer function');
 const fn=editor.slice(start,end);
 const anchor='return stage9LabBase.replace(\'<script id="motion-stage8-runtime">\'';
 if(fn.split(anchor).length!==2)throw Error('Expected exactly one GLB injection anchor');
 const pos=fn.indexOf(anchor),stop=fn.indexOf(';',pos);
 if(stop<0)throw Error('GLB injection statement missing terminator');
 const orig=fn.slice(pos,stop+1);
 // An opaque data: JS module is still offline and avoids corrupting or prematurely
 // terminating iframe script elements when a large minified bundle is injected.
 const transformed=orig.replace('return stage9LabBase.replace(','const page=stage9LabBase.replace(')+
   "\n return page.replace('</body>','<script src=\"'+stage9ThreeEngineURL+'\"></'+'script></body>');";
 const encoded=Buffer.from(engine,'utf8').toString('base64');
 const result=editor.slice(0,start)+ 'const stage9ThreeEngineURL="data:text/javascript;base64,'+encoded+'";\n'+fn.slice(0,pos)+transformed+fn.slice(stop+1)+editor.slice(end);
 if(result===editor||!result.includes('stage9ThreeEngineURL'))throw Error('Injection failed');
 return result;
}