# Snippet for scripts/ea_run.py — finds upper/lower lip arcs on a face whose lip seam has no hole (closed mouth
# pocket behind the lips, common on Tripo meshes), and optionally calls helper.prepare_mouth().
#
#   EA_ARGS='{"object":"Head","skin_seed":135,"center":[0,-0.075,1.124],"half":[0.015,0.012,0.006],"prepare":true}' \
#   "$BLENDER" -b --factory-startup --python-exit-code 1 --python ea_run.py -- <kit> <work> ea_mouth_arcs.py
#   (PowerShell: $env:EA_ARGS='{...}'; & $env:BLENDER -b ... ; the numbers are examples from one model)
#
# center / half: a box around the mouth (world centre; half extents along the session camera's right, depth and up).
# How it works (heuristic — always check the result with helper.capture_mouth_fit()):
#  * seam vertices are skin vertices in the box that have a neighbour clearly deeper than themselves (the pocket);
#    a vertex whose deep neighbour is above it belongs to the upper lip row, below it to the lower lip row.
#  * towards the corners the two rows are usually stitched together by small faces. If those stitches lie inside
#    the arcs, they stretch into white "fang" triangles when the mouth opens, so each corner is put at the
#    innermost stitch edge: the arcs only span the part of the seam where the rows are not connected.
import os, json, heapq, bmesh
from mathutils import Vector

A = json.loads(os.environ.get('EA_ARGS', '{}'))
OBJ = A.get('object', helper.state['objects'][0]); SEED = int(A['skin_seed'])
C = Vector(A['center']); HALF = A.get('half', [0.015, 0.012, 0.006]); DEEP = A.get('pocket_depth', 0.004)
cam = helper.state['camera']
front = Vector(cam['front']).normalized(); up = Vector(cam['up']); up = (up - front * up.dot(front)).normalized(); right = up.cross(front)
o = bpy.data.objects[OBJ]; M = o.matrix_world
bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
P = [M @ v.co for v in bm.verts]
nbr = lambda i: [e.other_vert(bm.verts[i]).index for e in bm.verts[i].link_edges]
skin = {SEED}; stack = [SEED]
while stack:
    for j in nbr(stack.pop()):
        if j not in skin: skin.add(j); stack.append(j)
def fr(i):
    d = P[i] - C
    return d.dot(right), d.dot(-front), d.dot(up)
band = [i for i in skin if all(abs(a) < h for a, h in zip(fr(i), HALF))]
U, L, both = set(), set(), set()
for i in band:
    x, y, z = fr(i)
    deep = [j for j in nbr(i) if j in skin and fr(j)[1] - y > DEEP]
    above = any(fr(j)[2] > z + 0.0015 for j in deep); below = any(fr(j)[2] < z - 0.0015 for j in deep)
    if above and below: both.add(i)
    elif above: U.add(i)
    elif below: L.add(i)
stitches = [(u, l) for u in U for l in nbr(u) if l in L]
show('seam', dict(upper_row=len(U), lower_row=len(L), corner_like=len(both), stitches=len(stitches)))
left = [s for s in stitches if max(fr(s[0])[0], fr(s[1])[0]) < 0]
rightside = [s for s in stitches if min(fr(s[0])[0], fr(s[1])[0]) > 0]
if not left or not rightside:
    raise ValueError('Could not find the stitched corners on both sides; widen "half" or check the box centre.')
uL, lL = max(left, key=lambda s: max(fr(s[0])[0], fr(s[1])[0]))
uR, lR = min(rightside, key=lambda s: min(fr(s[0])[0], fr(s[1])[0]))
def path(a, b, allowed):
    dist = {a: 0.0}; prev = {}; q = [(0.0, a)]
    while q:
        d, i = heapq.heappop(q)
        if i == b: break
        if d > dist[i]: continue
        for j in nbr(i):
            if j not in allowed: continue
            nd = d + (P[i] - P[j]).length
            if nd < dist.get(j, 1e9): dist[j] = nd; prev[j] = i; heapq.heappush(q, (nd, j))
    if b not in dist: raise ValueError(f'No path {a}->{b} inside the row; inspect the seam in wire view.')
    r = [b]
    while r[-1] != a: r.append(prev[r[-1]])
    return r[::-1]
upper = path(uL, uR, U | {uL, uR})
lower = [uL] + path(lL, lR, L) + [uR]
bad = [(a, b) for a in upper[1:-1] for b in nbr(a) if b in lower[1:-1]]
result = dict(upper=upper, lower=lower, corners=[uL, uR], width=round((P[uR] - P[uL]).length, 4), stitches_inside=bad)
show('mouth_arcs', result)
if bad:
    raise ValueError('Upper and lower arcs still share edges; move the corners inward.')
if A.get('prepare'):
    helper.prepare_mouth(OBJ, SEED, upper=upper, lower=lower)
    helper.save()
