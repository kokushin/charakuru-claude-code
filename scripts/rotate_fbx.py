# "$BLENDER" -b --factory-startup --python-exit-code 1 --python rotate_fbx.py -- <in.fbx> <out.fbx> <z_degrees>
# Orientation fix only, for unrigged returns (segmentation, retexture): imports like the kit (transforms baked
# into mesh data), rotates every mesh about the world Z axis (Blender's up axis, Y in Tripo / glTF) by
# <z_degrees>, and exports with the kit's FBX settings. No other change. A rigged FBX is refused: every non-mesh
# object is dropped on export, which would lose the armature.
import bpy, sys, math
from mathutils import Matrix
src, out, deg = sys.argv[sys.argv.index('--') + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=src, use_image_search=False, use_anim=False)
rigs = [o.name for o in bpy.context.scene.objects if o.type == 'ARMATURE']
assert not rigs, f'{src} is rigged ({rigs}); this script would drop the armature'
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
R = Matrix.Rotation(math.radians(float(deg)), 4, 'Z')
for o in meshes:
    if o.data.users > 1: o.data = o.data.copy()   # shared mesh data would be transformed once per user
    world = o.matrix_world.copy(); o.parent = None; o.matrix_world = Matrix.Identity(4); o.data.transform(R @ world)
for o in [o for o in bpy.context.scene.objects if o.type != 'MESH']: bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.object.select_all(action='DESELECT')
for o in meshes: o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
res = bpy.ops.export_scene.fbx(filepath=out, use_selection=True, object_types={'MESH'}, use_mesh_modifiers=False,
    bake_anim=False, add_leaf_bones=False, path_mode='COPY', embed_textures=True,
    axis_forward='-Z', axis_up='Y', bake_space_transform=True, apply_scale_options='FBX_SCALE_ALL')
assert 'FINISHED' in res, f'FBX export failed: {res}'
print('ROTATED', len(meshes), 'meshes by', deg, '->', out)
