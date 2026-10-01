"""Beberapa frame terpilih diperbesar: python3 v2/tools/frames_zoom.py out.png id:state:i [id:state:i ...]"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
from PIL import Image, ImageDraw  # noqa: E402
import cast  # noqa: E402
import char2  # noqa: E402

out = sys.argv[1]
specs = sys.argv[2:]
sc = int(os.environ.get("SC", "8"))
im = Image.new("RGB", (len(specs) * (64 * sc + 4), 64 * sc + 16), (250, 247, 240))
d = ImageDraw.Draw(im)
for k, spec in enumerate(specs):
    cid, st, i = spec.split(":")
    fr = char2.render(cast.get(cid), st, int(i)).image(sc)
    x = k * (64 * sc + 4)
    im.paste(fr, (x, 14), fr)
    d.text((x + 2, 1), spec, fill=(80, 60, 40))
im.save(out)
print(out)
