import assert from 'node:assert/strict';
import {normalizeCameraPath11,evaluateCameraPath11} from '../stage11-camera-curve.js';
const base=[
 {at:0,x:0,y:0,z:5.5,yaw:0,pitch:0,roll:0,fov:42,tension:0},
 {at:50,x:3,y:1.5,z:7,yaw:28,pitch:-10,roll:4,fov:65,tension:0},
 {at:100,x:0,y:0,z:5.5,yaw:0,pitch:0,roll:0,fov:42,tension:0}
];
const original=normalizeCameraPath11(base),stiff=normalizeCameraPath11(base.map(p=>({...p,tension:1})));
assert.equal(original.length,3);assert.equal(stiff.length,3);
const mid=evaluateCameraPath11(original,50);
assert.equal(mid.x,3);assert.equal(mid.y,1.5);
assert.equal(evaluateCameraPath11(stiff,0).fov,42);
assert.equal(evaluateCameraPath11(stiff,100).fov,42);
const natural=evaluateCameraPath11(original,20);
const flattened=evaluateCameraPath11(stiff,20);
assert(Math.abs(natural.x-flattened.x)>.01,'tangent tension must visibly affect spline');
assert(Math.abs(natural.y-flattened.y)>.01,'Y curve must be affected');
const lhs=evaluateCameraPath11(stiff,49.999),rhs=evaluateCameraPath11(stiff,50.001);
assert(Math.abs(lhs.x-rhs.x)<.001,'tension knot must remain continuous');
assert.equal(normalizeCameraPath11(base.map(x=>({...x,tension:9})))[0].tension,1);
assert.equal(normalizeCameraPath11(base.map(x=>({...x,tension:-4})))[0].tension,0);
for(let t=0;t<=100;t++){const p=evaluateCameraPath11(stiff,t);for(const k of ['x','y','z','yaw','pitch','roll','fov'])assert(Number.isFinite(p[k]));}
console.log('Stage12 tangent tension and spline bounds: PASS',JSON.stringify({natural:natural.x,flattened:flattened.x}));
