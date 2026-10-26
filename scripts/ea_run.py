# "$BLENDER" -b --factory-startup --python-exit-code 1 --python ea_run.py -- <kit_root> <work_dir> <snippet.py>
# Opens the expression work copy (after enabling the VRM add-on, which avoids a Blender crash on VRM data),
# attaches the kit's expression-studio helper as `helper`, then executes the snippet with `helper`,
# `studio`, `bpy`, `json`, `Vector` in scope. Snippets call helper.save() themselves when they change shapes.
import bpy, sys, json, importlib.util
from pathlib import Path
from mathutils import Vector
kit, work, snippet = sys.argv[sys.argv.index('--') + 1:]
spec = importlib.util.spec_from_file_location('mt', Path(kit) / 'scripts/mtoon-export.py')
mt = importlib.util.module_from_spec(spec); spec.loader.exec_module(mt); mt.enable_vrm()
bpy.ops.wm.open_mainfile(filepath=str(Path(work) / 'current.blend'))
spec = importlib.util.spec_from_file_location('expression_studio', Path(kit) / 'scripts/expression-studio.py')
studio = importlib.util.module_from_spec(spec); sys.modules['expression_studio'] = studio; spec.loader.exec_module(studio)
helper = studio.attach(work)
def show(label, value):
    print('OUT', label, json.dumps(value, ensure_ascii=False, default=str)[:4000])
exec(Path(snippet).read_text(encoding='utf-8'), dict(helper=helper, studio=studio, bpy=bpy, json=json, Vector=Vector, show=show))
print('EA_DONE')
