# "$BLENDER" -b --factory-startup --python-exit-code 1 --python inspect_rig.py -- <kit_root> <in.blend>
# Read-only: bone hierarchy (head/tail world), meshes with modifiers, vertex groups used, shape keys, materials.
import bpy, sys, importlib.util
from pathlib import Path
kit, inb = sys.argv[sys.argv.index('--') + 1:]
spec = importlib.util.spec_from_file_location('mt', Path(kit) / 'scripts/mtoon-export.py')
mt = importlib.util.module_from_spec(spec); spec.loader.exec_module(mt); mt.enable_vrm()
bpy.ops.wm.open_mainfile(filepath=inb)
for a in [o for o in bpy.data.objects if o.type == 'ARMATURE']:
    print('ARM', a.name, 'bones', len(a.data.bones))
    hum = getattr(a.data, 'vrm_addon_extension', None)
    mapping = {}
    try:
        for name, bone in a.data.vrm_addon_extension.vrm1.humanoid.human_bones.human_bone_name_to_human_bone().items():
            if bone.node.bone_name: mapping[bone.node.bone_name] = name
    except Exception as e:
        print('humanoid map err', e)
    for b in a.data.bones:
        h = a.matrix_world @ b.head_local; t = a.matrix_world @ b.tail_local
        print('B', b.name, '<', b.parent.name if b.parent else '-', [round(c, 3) for c in h], [round(c, 3) for c in t], mapping.get(b.name, ''))
for o in bpy.data.objects:
    if o.type != 'MESH': continue
    used = {}
    for v in o.data.vertices:
        for g in v.groups:
            if g.weight > 0.01: used[g.group] = used.get(g.group, 0) + 1
    names = sorted(((o.vertex_groups[i].name, n) for i, n in used.items()), key=lambda x: -x[1])
    print('MESH', o.name, 'verts', len(o.data.vertices), 'mods', [(m.type, getattr(m, 'object', None) and m.object.name) for m in o.modifiers],
          'keys', len(o.data.shape_keys.key_blocks) if o.data.shape_keys else 0, 'mats', [m.name for m in o.data.materials], 'parent', o.parent and o.parent.name)
    print('  groups', names[:40])
