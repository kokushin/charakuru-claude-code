# python3 grid_crop.py <render.png> <out.png> <x0> <y0> <x1> <y1> <session.json | frame_px> [scale]
# Crops a region given in session-camera pixel coordinates (the expression session's camera.size, read from its
# session.json or given in pixels) from a higher-resolution render of the same camera, enlarges it and overlays a
# grid labelled in those coordinates (lines every 5 px, labels every 25 px). Read eye landmarks off it for
# helper.set_blink_pixels().
import sys, json; from PIL import Image, ImageDraw
src, out = sys.argv[1:3]; x0, y0, x1, y1 = map(int, sys.argv[3:7])
frame = json.load(open(sys.argv[7], encoding='utf-8'))['camera']['size'] if sys.argv[7].endswith('.json') else int(sys.argv[7])
k = float(sys.argv[8]) if len(sys.argv) > 8 else 4
im = Image.open(src).convert('RGB'); f = im.size[0] / frame
c = im.crop((int(x0*f), int(y0*f), int(x1*f), int(y1*f))).resize((int((x1-x0)*k), int((y1-y0)*k)), Image.LANCZOS)
d = ImageDraw.Draw(c)
for x in range(x0 - x0 % 5, x1 + 1, 5):
    u = (x - x0) * k; strong = x % 25 == 0
    d.line([(u, 0), (u, c.size[1])], fill=(0, 230, 230) if strong else (0, 110, 110), width=1)
    if strong: d.text((u + 2, 2), str(x), fill=(255, 255, 0))
for y in range(y0 - y0 % 5, y1 + 1, 5):
    v = (y - y0) * k; strong = y % 25 == 0
    d.line([(0, v), (c.size[0], v)], fill=(0, 230, 230) if strong else (0, 110, 110), width=1)
    if strong: d.text((2, v + 2), str(y), fill=(255, 255, 0))
c.save(out)
