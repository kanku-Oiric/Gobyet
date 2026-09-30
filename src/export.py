"""Ekspor Gobyet (animasi dasar + kostum): GIF transparan (x8) ke gif/, sprite sheet PNG (x1, x4) ke sheets/,
dan pack/manifest.json (peta kostum x state, lihat src/pack.py).

    pip install Pillow
    python3 src/export.py
"""
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monkey import PAL, W, H  # noqa: E402
import costumes  # noqa: E402
import pack  # noqa: E402
import scenes  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYS = sorted(PAL)
PALETTE = [0, 0, 0] + [v for k in KEYS for v in PAL[k]]
INDEX = {k: i + 1 for i, k in enumerate(KEYS)}


def indexed(cv, scale):
    """Frame berpalet dengan indeks 0 transparan (GIF tidak punya alfa parsial)."""
    im = Image.new("P", (W, H), 0)
    im.putpalette(PALETTE + [0] * (768 - len(PALETTE)))
    for (x, y), c in cv.px.items():
        im.putpixel((x, y), INDEX[c])
    return im.resize((W * scale, H * scale), Image.NEAREST)


def main():
    os.makedirs(os.path.join(ROOT, "gif"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "sheets"), exist_ok=True)
    for name, (fn, n, ms) in {**scenes.SCENES, **costumes.SCENES}.items():
        frames = [fn(i) for i in range(n)]
        gif = [indexed(cv, 8) for cv in frames]
        path = os.path.join(ROOT, "gif", name + ".gif")
        gif[0].save(path, save_all=True, append_images=gif[1:], duration=[ms(i) for i in range(n)],
                    loop=0, transparency=0, disposal=2, optimize=False)
        for scale in (1, 4):
            sheet = Image.new("RGBA", (W * scale * n, H * scale), (0, 0, 0, 0))
            for i, cv in enumerate(frames):
                sheet.paste(cv.image(scale), (i * W * scale, 0))
            sheet.save(os.path.join(ROOT, "sheets", "%s%s.png" % (name, "" if scale == 1 else "@4x")))
        print("%-13s %2d frame  %.1f detik  %d KB" % (name, n, sum(ms(i) for i in range(n)) / 1000, os.path.getsize(path) // 1024))
    write_manifest()


def write_manifest():
    """pack/manifest.json: peta kostum x state -> asset, dengan frame dan durasi dari SCENES."""
    import json

    os.makedirs(os.path.join(ROOT, "pack"), exist_ok=True)
    data = pack.manifest({**scenes.SCENES, **costumes.SCENES})
    path = os.path.join(ROOT, "pack", "manifest.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    n = sum(len(v) for v in data["cells"].values())
    print("pack/manifest.json  %d sel asli, %d kostum, %d state" % (n, len(data["costumes"]), len(data["states"])))


if __name__ == "__main__":
    main()
