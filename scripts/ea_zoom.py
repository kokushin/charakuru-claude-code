# Snippet helper for scripts/ea_run.py:  exec(open('<skill>/scripts/ea_zoom.py', encoding='utf-8').read())
# zoomed(fn, center, scale, size, objects) narrows the expression session camera / rendered objects for one
# capture and restores them afterwards. capture() writes session.json while it runs, so the restored state is
# persisted again with helper.record(). Omitted center / scale / size keep the session camera's values.
# Camera rule: the capture camera sits at centre + 3*ortho_scale with a 0.1 m near clip, so keep scale >= 0.06
# (crop the image afterwards for a closer look) and keep the centre on the face (oblique views orbit it).
import copy
BASE_CAMERA = copy.deepcopy(helper.state['camera'])
def zoomed(fn, center=None, scale=None, size=None, objects=None, extra=()):
    ro = list(helper.state['render_objects']); objs = list(helper.state['objects'])
    if center is not None or scale is not None or size is not None:
        helper.state['camera'] = dict(BASE_CAMERA, center=list(BASE_CAMERA['center'] if center is None else center),
                                      ortho_scale=max(BASE_CAMERA['ortho_scale'] if scale is None else scale, 0.06),
                                      size=size or BASE_CAMERA['size'])
    if objects is not None:
        helper.state['render_objects'] = list(objects)
    helper.state['objects'] = objs + [n for n in extra if n not in objs]
    try:
        return fn()
    finally:
        helper.state['camera'] = copy.deepcopy(BASE_CAMERA); helper.state['render_objects'] = ro; helper.state['objects'] = objs
        helper.record('camera_restored')
