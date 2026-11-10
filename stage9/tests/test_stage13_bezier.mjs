import assert from 'node:assert/strict';
import {normalizeCameraPath11,evaluateCameraPath11} from '../stage11-camera-curve.js';
const raw=[
 {at:0,x:0,y:0,z:5.5,yaw:0,pitch:0,roll:0,fov:42,tension:0},
 {at:50,x:2,y:0,z:5.5,yaw:0,pitch:0,roll:0,fov:42,tension:0},
 {at:100,x:0,y:0,z:5.5,yaw:0,pitch:0,roll:0,fov:42,tension:0}
];
const legacy=normalizeCameraPath11(raw);
const edited=normalizeCameraPath11(raw.map((p,i)=>i===1?{...p,handleIn:{x:-1.9,y:1.5},handleOut:{x:1.1,y:-.9}}:p));
assert.equal(legacy.length,3);assert.equal(edited.length,3);
const before=evaluateCameraPath11(legacy,25),after=evaluateCameraPath11(edited,25);
const before75=evaluateCameraPath11(legacy,75),after75=evaluateCameraPath11(edited,75);
assert(Math.abs(after.x-before.x)>.2,'incoming handle must change first segment');
assert(Math.abs(after75.x-before75.x)>.1,'outgoing handle must independently change next segment');
assert(Math.abs(after.y-before.y)>.15,'incoming Y handle must move spatial path');
assert(Math.abs(after75.y-before75.y)>.15,'outgoing Y handle must move spatial path');
assert.equal(evaluateCameraPath11(edited,50).x,2,'keyframe center must remain intact');
assert.equal(evaluateCameraPath11(legacy,0).x,0,'old project must remain valid');
assert.equal(normalizeCameraPath11([{...raw[0],handleOut:{x:999}},raw[1],raw[2]])[0].handleOut.x,8,'handle offset clamp');
console.log('Stage13 independent in/out Bezier handles pass',JSON.stringify({before,after,before75,after75}));
