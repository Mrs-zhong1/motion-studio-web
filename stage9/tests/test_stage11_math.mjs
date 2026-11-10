import assert from 'node:assert/strict';
import {normalizeCameraPath11,evaluateCameraPath11} from '../stage11-camera-curve.js';
const p=[
 {at:0,x:0,y:0,z:5.5,yaw:0,pitch:0,roll:0,fov:42},
 {at:30,x:3,y:1.5,z:8,yaw:30,pitch:-12,roll:5,fov:60},
 {at:100,x:1.5,y:.5,z:6,yaw:0,pitch:0,roll:0,fov:45}
];
const t=normalizeCameraPath11(p);
assert.equal(t.length,3);
assert.deepEqual(evaluateCameraPath11(t,0),Object.fromEntries(Object.entries(p[0]).filter(([k])=>k!=='at')));
assert.equal(evaluateCameraPath11(t,30).x,3);
assert.equal(evaluateCameraPath11(t,100).fov,45);
for(let a=0;a<=100;a++){const v=evaluateCameraPath11(t,a);for(const k of ['x','y','z','yaw','pitch','roll','fov'])assert(Number.isFinite(v[k]),k)}
const lhs=evaluateCameraPath11(t,30-1e-4),rhs=evaluateCameraPath11(t,30+1e-4);
assert(Math.abs(lhs.x-rhs.x)<.003,'path discontinuity at node');
assert.equal(normalizeCameraPath11([...p,{...p[2],at:100}]).length,0,'duplicate timestamp must fail');
assert.equal(normalizeCameraPath11(p.slice(1)).length,0,'missing zero endpoint must fail');
assert.equal(normalizeCameraPath11(Array(9).fill(p[0])).length,0,'exceed eight nodes must fail');
console.log('Stage11 cubic camera path interpolation and normalization PASS');
