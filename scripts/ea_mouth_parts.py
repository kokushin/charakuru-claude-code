# Snippet for scripts/ea_run.py — run after helper.transfer_mouth(). Makes separate inner-mouth components follow
# the transferred lip rims in every mouth key, and optionally enlarges the opening of chosen keys.
#
#   EA_ARGS='{"skin_seed":135,"upper_parts":[4932],"lower_parts":[4872],"inner_parts":[[0,0.6]],
#             "gain":{"aa":1.4,"ih":1.4,"ou":1.4,"ee":1.4,"oh":1.4,"surprised_mouth":1.4}}' \
#   "$BLENDER" -b --factory-startup --python-exit-code 1 --python ea_run.py -- <kit> <work> ea_mouth_parts.py
#   (PowerShell: $env:EA_ARGS='{...}'; & $env:BLENDER -b ... ; the numbers are examples from one model)
#
# upper_parts / lower_parts: seeds of components that sit against the upper / lower lip (they follow that arc).
# inner_parts: [seed, share] pairs that follow the lower arc by `share` (e.g. a tongue-like part).
# gain: scale of the skin displacement per key (the opening of a stitched seam is narrow and reads small).
#   Gains are relative to the transferred key: the applied gain is kept in <work>/ea_mouth_parts.json, so running
#   again with the same gain changes nothing, and a key transferred anew starts from 1 again.
# The arc motion is fitted with a quadratic in x before it is applied (following the polyline folds the parts into
# chevrons), and each part is tucked a little behind its lip as the mouth opens. Basis and other keys untouched.
import os, json, bmesh
import numpy as np
from mathutils import Vector

A = json.loads(os.environ.get('EA_ARGS', '{}'))
MOUTH_KEYS = ['happy_mouth', 'angry_mouth', 'sad_mouth', 'relaxed_mouth', 'surprised_mouth', 'aa', 'ih', 'ou', 'ee', 'oh']
TUCK_UP, TUCK_BACK, FULL_OPEN = A.get('tuck_up', 0.0015), A.get('tuck_back', 0.001), A.get('full_open', 0.004)
mouth = helper.state['mouth']; o = bpy.data.objects[mouth['object']]; kb = o.data.shape_keys.key_blocks
M3 = np.array(o.matrix_world.to_3x3()); Mi = np.linalg.inv(M3)
cam = helper.state['camera']; front = Vector(cam['front']).normalized(); up = Vector(cam['up']); up = np.array((up - front * up.dot(front)).normalized())
back = -np.array(front)
def component(seed):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
    seen = {seed}; stack = [seed]
    while stack:
        v = bm.verts[stack.pop()]
        for e in v.link_edges:
            j = e.other_vert(v).index
            if j not in seen: seen.add(j); stack.append(j)
    bm.free(); return sorted(seen)
basis = np.array([v.co for v in kb[0].data])
key_of = lambda name: kb[helper.state['keys'][name][o.name]]
present = [n for n in MOUTH_KEYS if o.name in helper.state['keys'].get(n, {})]   # transfer_mouth may cover only some
skin = component(int(A.get('skin_seed', mouth['skin_seed'])))
GAINS = helper.root / 'ea_mouth_parts.json'
applied = json.loads(GAINS.read_text(encoding='utf-8')) if GAINS.exists() else {}
spread = lambda co: float(np.abs(co[skin] - basis[skin]).sum())   # fingerprint of the key as this script left it
for name, g in A.get('gain', {}).items():
    if name not in present:
        show('gain_skipped', name); continue
    key = key_of(name); co = np.array([v.co for v in key.data]); last = applied.get(name)
    done = last['gain'] if last and abs(last['spread'] - spread(co)) <= 1e-9 * max(1.0, last['spread']) else 1.0
    co[skin] = basis[skin] + (co[skin] - basis[skin]) * (g / done)
    for v, c in zip(key.data, co): v.co = c
    applied[name] = dict(gain=g, spread=spread(np.array([v.co for v in key.data])))
parts = [(component(s), mouth['upper'], 1.0, 1) for s in A.get('upper_parts', [])]
parts += [(component(s), mouth['lower'], 1.0, -1) for s in A.get('lower_parts', [])]
parts += [(component(s), mouth['lower'], share, -1) for s, share in A.get('inner_parts', [])]
for name in present:
    key = key_of(name); co = np.array([v.co for v in key.data]); d = co - basis
    rise = (d @ M3.T) @ up
    gap = float(np.mean(rise[mouth['upper'][1:-1]]) - np.mean(rise[mouth['lower'][1:-1]]))
    open_k = float(np.clip(gap / FULL_OPEN, 0, 1))
    for ids, arc, share, sign in parts:
        ax = basis[arc, 0]; fit = [np.polyfit(ax, d[arc][:, j], 2) for j in range(3)]
        xs = np.clip(basis[ids, 0], ax.min(), ax.max())
        disp = np.stack([np.polyval(f, xs) for f in fit], 1) * share
        tuck = Mi @ (back * TUCK_BACK + up * sign * TUCK_UP) * open_k
        co[ids] = basis[ids] + disp + tuck
    for v, c in zip(key.data, co): v.co = c
o.data.update()
helper.save()
GAINS.write_text(json.dumps(applied, indent=2), encoding='utf-8')
show('mouth_parts', dict(parts=len(parts), gain=A.get('gain', {})))
