# python3 contact.py out.png cell cols img... : grey-background contact sheet with file-name labels
# Needs Pillow (Blender's bundled Python works: pip install --target <dir> pillow, then PYTHONPATH=<dir>).
# Labels use a Japanese-capable system font when one is found; LABEL_FONT names another font file.
import sys, os
from PIL import Image, ImageDraw, ImageFont
FONTS = [os.environ.get('LABEL_FONT', ''), 'C:/Windows/Fonts/meiryo.ttc', 'C:/Windows/Fonts/YuGothM.ttc',
         '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc']
font = next((ImageFont.truetype(f, 14) for f in FONTS if f and os.path.exists(f)), ImageFont.load_default())
out, cell, cols = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); files = sys.argv[4:]
rows = (len(files) + cols - 1) // cols
sheet = Image.new('RGB', (cols * cell, rows * (cell + 24)), (150, 150, 150))
d = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    im = Image.open(f).convert('RGBA'); im.thumbnail((cell, cell))
    x, y = (i % cols) * cell, (i // cols) * (cell + 24)
    bg = Image.new('RGBA', (cell, cell), (150, 150, 150, 255)); bg.alpha_composite(im, ((cell - im.width) // 2, (cell - im.height) // 2))
    sheet.paste(bg.convert('RGB'), (x, y + 24)); d.text((x + 4, y + 3), os.path.basename(f), fill=(0, 0, 0), font=font)
sheet.save(out); print(out)
