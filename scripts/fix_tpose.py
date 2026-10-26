# "$BLENDER" -b --factory-startup --python-exit-code 1 --python fix_tpose.py -- <kit_root> <in.blend> <out.blend> [--no-colliders]
# Makes the rest pose a true T-pose. VRM / VRMA motions add their rotations on top of a rest pose whose arms are
# horizontal; if the rig's arms hang below horizontal, every motion inherits that offset and the arms sink into
# the body or skirt. Steps:
#  1. pose: rotate upper arm, lower arm and hand on each side so each bone points straight along world +-X
#  2. bake that pose into every mesh bound to the rig (vertex positions; only the rig's armature modifier is
#     evaluated; meshes with shape keys must not be weighted to the arms or anything below them)
#  3. apply the pose as the new rest pose (weights unchanged)
#  4. re-seat upper-arm capsule colliders and add lower-arm capsules + hand spheres in a collider group 'Arms'
#     (add 'Arms' to the chains' collider groups in the kit's spring config afterwards). Skipped when an 'Arms'
#     group already exists, so running the script twice adds nothing.
# Bones are found through the VRM 1.0 humanoid mapping, so rig and bone names do not matter.
import bpy, sys, importlib.util
from pathlib import Path
from mathutils import Vector, Matrix
args = sys.argv[sys.argv.index('--') + 1:]
kit, inb, outb = args[:3]; colliders = '--no-colliders' not in args
spec = importlib.util.spec_from_file_location('mt', Path(kit) / 'scripts/mtoon-export.py')
mt = importlib.util.module_from_spec(spec); spec.loader.exec_module(mt); mt.enable_vrm()
bpy.ops.wm.open_mainfile(filepath=inb)   # only after the VRM add-on is registered (avoids a crash)
rig = next(o for o in bpy.data.objects if o.type == 'ARMATURE' and o.data.vrm_addon_extension.spec_version == '1.0')
hb = rig.data.vrm_addon_extension.vrm1.humanoid.human_bones
ARM = {s: [getattr(hb, f'{side}_{n}').node.bone_name for n in ('upper_arm', 'lower_arm', 'hand')] for s, side in (('L', 'left'), ('R', 'right'))}
assert all(all(ARM[s]) for s in ARM), f'humanoid arm bones not mapped: {ARM}'
# every bone the pose moves: the arm chain and everything below it (fingers, hand accessories)
moved = {c.name for s in ARM for b in [rig.data.bones[ARM[s][0]]] for c in [b, *b.children_recursive]}
bound = [o for o in bpy.data.objects if o.type == 'MESH' and any(m.type == 'ARMATURE' and m.object == rig for m in o.modifiers)]
for o in bound:
    if o.data.shape_keys:
        weighted = any(o.vertex_groups[g.group].name in moved and g.weight > 0 for v in o.data.vertices for g in v.groups)
        assert not weighted, f'{o.name} has shape keys and arm weights; bake per shape key instead'
# meshes rigidly parented to an arm bone are not baked (the VRM add-on's collider empties are fine)
pinned = [o.name for o in bpy.data.objects if o.type == 'MESH' and o.parent == rig and o.parent_type == 'BONE' and o.parent_bone in moved]
assert not pinned, f'meshes parented to arm bones need manual handling: {pinned}'
for o in bpy.context.selected_objects: o.select_set(False)
rig.hide_set(False); rig.select_set(True); bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode='POSE')
pb = rig.pose.bones
to_rig = rig.matrix_world.inverted().to_3x3()   # world +-X expressed in the armature's own space
def report(tag):
    for s in ARM:
        for n in ARM[s]:
            b = pb[n]; d = (rig.matrix_world.to_3x3() @ (b.tail - b.head)).normalized(); print(tag, n, 'world dir', tuple(round(c, 3) for c in d))
report('BEFORE')
for s, sign in (('L', 1), ('R', -1)):   # VRM models face -Y, so the model's left arm points to world +X
    target = (to_rig @ Vector((sign, 0, 0))).normalized()
    for n in ARM[s]:
        b = pb[n]; bpy.context.view_layer.update()
        R = (b.tail - b.head).normalized().rotation_difference(target).to_matrix().to_4x4()
        b.matrix = Matrix.Translation(b.head) @ R @ Matrix.Translation(-b.head) @ b.matrix
        bpy.context.view_layer.update()
report('AFTER')
bpy.ops.object.mode_set(mode='OBJECT')
for o in bound:
    if o.data.shape_keys:
        continue
    # evaluate only this rig's armature deformation: other modifiers would be baked in or change the vertex count
    others = [m for m in o.modifiers if not (m.type == 'ARMATURE' and m.object == rig) and m.show_viewport]
    for m in others: m.show_viewport = False
    try:
        dg = bpy.context.evaluated_depsgraph_get(); dg.update()
        ev = o.evaluated_get(dg); me = ev.to_mesh()
        assert len(me.vertices) == len(o.data.vertices), f'{o.name}: evaluated vertex count differs'
        shifts = [(v.co - e.co).length for v, e in zip(o.data.vertices, me.vertices)]
        for v, e in zip(o.data.vertices, me.vertices): v.co = e.co.copy()
        ev.to_mesh_clear(); o.data.update()
    finally:
        for m in others: m.show_viewport = True
    print('BAKED', o.name, 'moved vertices (>0.1 mm)', sum(d > 1e-4 for d in shifts), 'max shift m', round(max(shifts, default=0), 5))
bpy.context.view_layer.objects.active = rig; rig.select_set(True)
bpy.ops.object.mode_set(mode='POSE'); bpy.ops.pose.select_all(action='SELECT')
bpy.ops.pose.armature_apply(selected=False)
bpy.ops.object.mode_set(mode='OBJECT')
sb = rig.data.vrm_addon_extension.spring_bone1
if colliders and any(g.vrm_name == 'Arms' for g in sb.collider_groups):
    print('ARMS GROUP EXISTS, colliders left as they are')
elif colliders:
    for c in sb.colliders:
        if c.node.bone_name in (ARM['L'][0], ARM['R'][0]) and c.shape_type == 'Capsule':
            c.shape.capsule.offset = (0, 0, 0); c.shape.capsule.tail = (0, rig.data.bones[c.node.bone_name].length, 0)
    def add(bone, kind, r, a=(0, 0, 0), b=None):
        bpy.ops.vrm.add_spring_bone1_collider(armature_object_name=rig.name)
        c = sb.colliders[-1]; c.node.bone_name = bone
        if kind == 'sphere': c.shape_type = 'Sphere'; c.shape.sphere.offset = a; c.shape.sphere.radius = r
        else: c.shape_type = 'Capsule'; c.shape.capsule.offset = a; c.shape.capsule.tail = b; c.shape.capsule.radius = r
        return c
    new = []
    for s in ARM:
        lower, hand = ARM[s][1], ARM[s][2]
        new.append(add(lower, 'capsule', 0.04, (0, 0, 0), (0, rig.data.bones[lower].length, 0)))
        new.append(add(hand, 'sphere', 0.045, (0, rig.data.bones[hand].length * 0.6, 0)))
    bpy.ops.vrm.add_spring_bone1_collider_group(armature_object_name=rig.name)
    g = sb.collider_groups[-1]; g.vrm_name = 'Arms'; gi = len(sb.collider_groups) - 1
    for c in new:
        bpy.ops.vrm.add_spring_bone1_collider_group_collider(armature_object_name=rig.name, collider_group_index=gi)
        g.colliders[-1].collider_uuid = c.uuid
print('GROUPS', [(x.vrm_name, len(x.colliders)) for x in sb.collider_groups])
res = bpy.ops.wm.save_as_mainfile(filepath=outb, copy=True)
assert 'FINISHED' in res, f'save failed: {res}'
print('SAVED', outb)
