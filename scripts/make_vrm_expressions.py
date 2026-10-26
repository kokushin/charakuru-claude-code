# "$BLENDER" -b --factory-startup --python-exit-code 1 --python make_vrm_expressions.py -- \
#     <kit_root> <avatar.blend> <expressions.blend> <out.vrm> [--face Head] [--no-mouth] [--reference-vrm <avatar.vrm>]
# Copies the finished expression keys (EA_*) from the kit's expression work Blend
# (work/expression-authoring/exports/expressions.blend) onto the same face mesh of the app-saved
# exports/avatar.blend, binds them as VRM 1.0 expressions and exports a separate VRM.
#  --no-mouth       eye and brow keys only; the mouth keeps its modelled shape (use when the mouth keys were
#                   tried and not adopted). Keys that never moved (e.g. an untouched EA_aa) are skipped anyway.
#  --reference-vrm  the app-exported VRM (default: avatar.vrm next to avatar.blend). Only the meshes it contains
#                   are exported, so helper meshes such as the weight-transfer donor body never leak into the VRM.
# exports/avatar.vrm is never touched. The app writes name/author/license straight into its VRM, so copy them
# afterwards with: node patch_vrm.mjs out.vrm out.vrm --meta-from <project>/exports/avatar.vrm
import bpy, sys, json, struct, argparse, importlib.util
from pathlib import Path
ap = argparse.ArgumentParser()
ap.add_argument('kit'); ap.add_argument('avatar_blend'); ap.add_argument('expr_blend'); ap.add_argument('out_vrm')
ap.add_argument('--face', default='Head'); ap.add_argument('--no-mouth', action='store_true'); ap.add_argument('--reference-vrm')
args = ap.parse_args(sys.argv[sys.argv.index('--') + 1:])
MOUTH_KEYS = {'aa', 'ih', 'ou', 'ee', 'oh', 'happy_mouth', 'angry_mouth', 'sad_mouth', 'relaxed_mouth', 'surprised_mouth'}

ref = Path(args.reference_vrm or Path(args.avatar_blend).with_name('avatar.vrm'))
assert ref.is_file(), f'{ref} not found: export the VRM from the app first (it is also the metadata source)'
raw = ref.read_bytes(); n = struct.unpack_from('<I', raw, 12)[0]
gltf = json.loads(raw[20:20 + n])
keep = {node['name'] for node in gltf['nodes'] if 'mesh' in node}
print('REFERENCE MESHES', sorted(keep))

spec = importlib.util.spec_from_file_location('mt', Path(args.kit) / 'scripts/mtoon-export.py')
mt = importlib.util.module_from_spec(spec); spec.loader.exec_module(mt); mt.enable_vrm()
bpy.ops.wm.open_mainfile(filepath=args.avatar_blend)
face = bpy.data.objects[args.face]
assert face.name in keep, f'{face.name} is not in {ref}'
with bpy.data.libraries.load(args.expr_blend, link=False) as (src, dst):
    dst.meshes = list(src.meshes)
def basis_error(me):
    return max((a.co - b.co).length for a, b in zip(me.shape_keys.key_blocks[0].data, face.data.vertices))
donors = [me for me in dst.meshes if me and me.shape_keys and len(me.vertices) == len(face.data.vertices)
          and any(k.name.startswith('EA_') for k in me.shape_keys.key_blocks)]
assert donors, f'no expression mesh with {len(face.data.vertices)} vertices in {args.expr_blend}'
donor = min(donors, key=basis_error); err = basis_error(donor)
assert err < 1e-5, f'basis differs from the face mesh: {err}'
if not face.data.shape_keys:
    face.shape_key_add(name='Basis', from_mix=False)
base = donor.shape_keys.key_blocks[0]
skipped = {}
for k in donor.shape_keys.key_blocks:
    name = k.name[3:]
    if not k.name.startswith('EA_'):
        continue
    if k.name == 'EA_happy':   # the kit's empty legacy key
        skipped[name] = 'legacy'; continue
    if args.no_mouth and name in MOUTH_KEYS:
        skipped[name] = 'no_mouth'; continue
    if max((a.co - b.co).length for a, b in zip(k.data, base.data)) < 1e-6:
        skipped[name] = 'unchanged'; continue
    nk = face.data.shape_keys.key_blocks.get(name) or face.shape_key_add(name=name, from_mix=False)
    for d, s in zip(nk.data, k.data): d.co = s.co.copy()
    nk.value = 0
for me in dst.meshes:
    if me and me.users == 0: bpy.data.meshes.remove(me)
keys = {k.name for k in face.data.shape_keys.key_blocks}
print('KEYS', sorted(keys)); print('SKIPPED', skipped)

rig = next(o for o in bpy.data.objects if o.type == 'ARMATURE' and o.data.vrm_addon_extension.spec_version == '1.0')
ex = rig.data.vrm_addon_extension.vrm1.expressions
bound = {}
def bind(expr, weights, blink='none', mouth='none', label=None):
    expr.morph_target_binds.clear()
    used = [k for k in weights if k in keys]
    for key in used:
        b = expr.morph_target_binds.add(); b.node.mesh_object_name = face.name; b.index = key; b.weight = weights[key]
    # an expression without keys must not block blinking or the mouth
    expr.override_blink, expr.override_mouth = (blink, mouth) if used else ('none', 'none')
    bound[label] = used
p = ex.preset
bind(p.blink, {'blink': 1}, label='blink'); bind(p.blink_left, {'blink_L': 1}, label='blinkLeft')
bind(p.blink_right, {'blink_R': 1}, label='blinkRight')
for v in ('aa', 'ih', 'ou', 'ee', 'oh'):
    bind(getattr(p, v), {v: 1}, label=v)
# emotions combine eye + mouth + brow keys; they contain eye shapes, so blink is blended (blocked for surprise)
bind(p.happy, {'happy_eye': 1, 'happy_mouth': 1, 'brow_happy': 0.6}, blink='blend', mouth='blend', label='happy')
bind(p.angry, {'angry_eye': 1, 'angry_mouth': 1, 'brow_angry': 1}, blink='blend', mouth='blend', label='angry')
bind(p.sad, {'sad_eye': 1, 'sad_mouth': 1, 'brow_sad': 1}, blink='blend', mouth='blend', label='sad')
bind(p.relaxed, {'relaxed_eye': 1, 'relaxed_mouth': 1, 'brow_relaxed': 1}, blink='blend', mouth='blend', label='relaxed')
bind(p.surprised, {'surprised_eye': 1, 'surprised_mouth': 1, 'brow_surprised': 1}, blink='block', mouth='blend', label='surprised')
ex.custom.clear()
c = ex.custom.add(); c.custom_name = 'smile'   # closed-eye smile
bind(c, {'blink': 1, 'happy_mouth': 1, 'brow_happy': 0.6}, blink='block', mouth='blend', label='smile')
print('BOUND', bound)
# export exactly the meshes of the app-exported VRM (allow-list, not a name filter)
meshes = [o for o in bpy.data.objects if o.type == 'MESH' and o.name in keep]
missing = keep - {o.name for o in meshes}
assert not missing, f'meshes of {ref} not found in {args.avatar_blend}: {sorted(missing)}'
bpy.ops.object.select_all(action='DESELECT')
for o in [rig, *meshes]:
    o.hide_set(False); o.select_set(True)
bpy.context.view_layer.objects.active = rig
out = Path(args.out_vrm).resolve(); out.parent.mkdir(parents=True, exist_ok=True); out.unlink(missing_ok=True)
res = bpy.ops.export_scene.vrm(filepath=str(out), armature_object_name=rig.name, export_only_selections=True,
                               export_invisibles=False, use_addon_preferences=False)
assert 'FINISHED' in res and out.is_file(), f'VRM export failed: {res}'
print('EXPORT', out, 'meshes', [o.name for o in meshes])
print('INSPECT', mt.inspect_vrm(out))
