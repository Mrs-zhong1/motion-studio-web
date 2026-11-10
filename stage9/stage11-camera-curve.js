// Stage11 curve evaluator, browser/node compatible. No Three.js imports.
// Hermite form of cubic Bezier with shared tangent at interior knots.
export const CAMERA11_KEYS=['x','y','z','yaw','pitch','roll','fov'];
export const CAMERA11_LIMITS={x:[-4,4],y:[-4,4],z:[2,12],yaw:[-120,120],pitch:[-80,80],roll:[-90,90],fov:[22,90]};
const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
const finite=(n,def=0)=>Number.isFinite(Number(n))?Number(n):def;
export function normalizeCameraPath11(raw){
 if(!Array.isArray(raw)||raw.length<2||raw.length>8)return [];
 const p=raw.map(obj=>{const item={at:clamp(finite(obj?.at),0,100)};
   for(const k of CAMERA11_KEYS){const [low,high]=CAMERA11_LIMITS[k];item[k]=clamp(finite(obj?.[k],k==='z'?5.5:k==='fov'?42:0),low,high);}
   item.tension=clamp(finite(obj?.tension,0),0,1);return item;
 }).sort((a,b)=>a.at-b.at);
 if(Math.abs(p[0].at)>1e-6||Math.abs(p.at(-1).at-100)>1e-6)return [];
 for(let i=1;i<p.length;i++)if(p[i].at-p[i-1].at<.1)return [];
 return p;
}
export function evaluateCameraPath11(path,at){
 const p=normalizeCameraPath11(path);if(p.length<2)return null;
 const progress=clamp(finite(at),0,100);
 let i=0;while(i<p.length-2&&progress>p[i+1].at)i++;
 const a=p[i],b=p[i+1],step=b.at-a.at,u=clamp((progress-a.at)/step,0,1),u2=u*u,u3=u2*u;
 const out={};
 for(const key of CAMERA11_KEYS){
   const prev=p[Math.max(i-1,0)],next=p[Math.min(i+2,p.length-1)];
   const mA=i===0?(b[key]-a[key])/step:(b[key]-prev[key])/(b.at-prev.at);
   const mB=i+2>=p.length?(b[key]-a[key])/step:(next[key]-a[key])/(next.at-a.at);
   const v=(2*u3-3*u2+1)*a[key]+(u3-2*u2+u)*step*mA*(1-a.tension)+(-2*u3+3*u2)*b[key]+(u3-u2)*step*mB*(1-b.tension);
   const [lo,hi]=CAMERA11_LIMITS[key];out[key]=clamp(v,lo,hi);
 }
 return out;
}
