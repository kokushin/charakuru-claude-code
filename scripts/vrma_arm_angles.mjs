// node vrma_arm_angles.mjs <file.vrma> : actual arm directions in the VRMA clip. For each sampled frame, the
// world rotation of each node is composed from parents (animated rotation where present, else node rest),
// and the upper/lower arm direction (vector to the child joint) is reported as degrees below horizontal
// plus how far it reaches sideways (x) vs forward/back (z). Also reports the clip's rest-pose arm angle.
import fs from 'node:fs';
const buf = fs.readFileSync(process.argv[2]);
const jsonLen = buf.readUInt32LE(12); const json = JSON.parse(buf.subarray(20, 20 + jsonLen).toString('utf8'));
const bin = buf.subarray(20 + jsonLen + 8);
const human = json.extensions.VRMC_vrm_animation.humanoid.humanBones;
const boneNode = Object.fromEntries(Object.entries(human).map(([k, v]) => [k, v.node]));
const acc = i => { const a = json.accessors[i], bv = json.bufferViews[a.bufferView]; const n = { SCALAR: 1, VEC3: 3, VEC4: 4 }[a.type];
  return new Float32Array(bin.buffer.slice(bin.byteOffset + (bv.byteOffset || 0) + (a.byteOffset || 0), bin.byteOffset + (bv.byteOffset || 0) + (a.byteOffset || 0) + a.count * n * 4)); };
const qmul = (a, b) => [a[3]*b[0]+a[0]*b[3]+a[1]*b[2]-a[2]*b[1], a[3]*b[1]-a[0]*b[2]+a[1]*b[3]+a[2]*b[0], a[3]*b[2]+a[0]*b[1]-a[1]*b[0]+a[2]*b[3], a[3]*b[3]-a[0]*b[0]-a[1]*b[1]-a[2]*b[2]];
const rot = (q, v) => { const p = qmul(qmul(q, [v[0], v[1], v[2], 0]), [-q[0], -q[1], -q[2], q[3]]); return [p[0], p[1], p[2]]; };
const parent = {}; json.nodes.forEach((n, i) => (n.children || []).forEach(c => parent[c] = i));
const anim = json.animations[0]; const tracks = {};
for (const ch of anim.channels) if (ch.target.path === 'rotation') tracks[ch.target.node] = acc(anim.samplers[ch.sampler].output);
const frames = Math.max(...Object.values(tracks).map(t => t.length / 4));
const local = (n, f) => { const t = tracks[n]; if (t && f !== null) { const i = Math.min(f, t.length / 4 - 1) * 4; return [t[i], t[i+1], t[i+2], t[i+3]]; } return json.nodes[n].rotation || [0, 0, 0, 1]; };
const world = (n, f) => { let q = local(n, f); for (let p = parent[n]; p !== undefined; p = parent[p]) q = qmul(local(p, f), q); return q; };
const report = (bone, childBone) => {
  const n = boneNode[bone], c = boneNode[childBone]; const t = json.nodes[c].translation;
  const ang = f => { const d = rot(world(n, f), t); const L = Math.hypot(...d); return [Math.asin(-d[1] / L) * 180 / Math.PI, d[0] / L, d[2] / L]; };
  const rest = ang(null); let lo = 999, hi = -999;
  for (let f = 0; f < frames; f++) { const a = ang(f)[0]; lo = Math.min(lo, a); hi = Math.max(hi, a); }
  console.log(bone.padEnd(14), `rest ${rest[0].toFixed(1)}° below horizontal | clip ${lo.toFixed(1)}..${hi.toFixed(1)}° below horizontal`);
};
report('leftUpperArm', 'leftLowerArm'); report('leftLowerArm', 'leftHand'); report('rightUpperArm', 'rightLowerArm'); report('rightLowerArm', 'rightHand');
