# python3 label_grid.py <paths.json> <root> <out.png> <cols> <cell> [crop_top crop_bottom]
# Tiles captures listed in a {label: relative_path} json (UTF-8) with labels, optionally cropping vertically
# (fractions). Labels use a Japanese-capable system font when one is found; LABEL_FONT names another font file.
import sys, os, json; from PIL import Image, ImageDraw, ImageFont
FONTS = [os.environ.get('LABEL_FONT', ''), 'C:/Windows/Fonts/meiryo.ttc', 'C:/Windows/Fonts/YuGothM.ttc',
         '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc']
font = next((ImageFont.truetype(f, 13) for f in FONTS if f and os.path.exists(f)), ImageFont.load_default())
paths = json.load(open(sys.argv[1], encoding='utf-8')); root = sys.argv[2]; out = sys.argv[3]; cols = int(sys.argv[4]); cell = int(sys.argv[5])
t, b = (float(sys.argv[6]), float(sys.argv[7])) if len(sys.argv) > 7 else (0, 1)
items = list(paths.items()); rows = (len(items) + cols - 1) // cols
ch = int(cell * (b - t)); sheet = Image.new('RGB', (cols * cell, rows * (ch + 18)), (30, 30, 30)); d = ImageDraw.Draw(sheet)
for k, (label, rel) in enumerate(items):
    im = Image.open(root + '/' + rel).convert('RGB'); w, h = im.size
    im = im.crop((0, int(h * t), w, int(h * b))).resize((cell, ch), Image.LANCZOS)
    x, y = (k % cols) * cell, (k // cols) * (ch + 18); sheet.paste(im, (x, y + 18)); d.text((x + 4, y + 2), label, fill=(255, 255, 255), font=font)
sheet.save(out)
