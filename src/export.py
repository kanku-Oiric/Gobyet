"""Ekspor Gobyet (animasi dasar + kostum): GIF transparan (x8) ke gif/, sprite sheet PNG (x1, x4) ke sheets/,
dan pack/manifest.json (peta kostum x state, lihat src/pack.py).

    pip install Pillow
    python3 src/export.py
"""
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monkey import PAL, PAL_EXT, PAL_HERO, W, H, rgb  # noqa: E402
import costumes  # noqa: E402
import domains  # noqa: E402
import pack  # noqa: E402
import roles  # noqa: E402
import scenes  # noqa: E402
import special  # noqa: E402
import fantasy  # noqa: E402
import hero3_scenes  # noqa: E402
import theology  # noqa: E402
import variants  # noqa: E402
import pelengkap  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYS = sorted(PAL)
PALETTE = [0, 0, 0] + [v for k in KEYS for v in PAL[k]]
INDEX = {k: i + 1 for i, k in enumerate(KEYS)}


def local_palette(frames):
    """Palet lokal aset baru: hanya kunci yang dipakai di semua frame, urutan PAL, PAL_EXT, lalu PAL_HERO (masing-masing
    diurutkan). Menambah kunci PAL_EXT atau PAL_HERO yang tidak dipakai aset ini tidak mengubah byte aset ini."""
    used = set()
    for cv in frames:
        used |= set(cv.px.values())
    keys = [k for k in KEYS if k in used] + [k for k in sorted(PAL_EXT) if k in used] + [k for k in sorted(PAL_HERO) if k in used]
    palette = [0, 0, 0] + [v for k in keys for v in rgb(k)]
    return {k: i + 1 for i, k in enumerate(keys)}, palette


def indexed(cv, scale, index=None, palette=None):
    """Frame berpalet dengan indeks 0 transparan (GIF tidak punya alfa parsial)."""
    index, palette = index or INDEX, palette or PALETTE
    cw, ch = getattr(cv, "w", W), getattr(cv, "h", H)       # kanvas per animasi (default 64x48)
    im = Image.new("P", (cw, ch), 0)
    im.putpalette(palette + [0] * (768 - len(palette)))
    for (x, y), c in cv.px.items():
        im.putpixel((x, y), index[c])
    return im.resize((cw * scale, ch * scale), Image.NEAREST)


def all_scenes():
    merged = {}
    for mod in (scenes, costumes, roles, domains, special, fantasy, theology, variants, pelengkap, hero3_scenes):
        for name in mod.SCENES:
            assert name not in merged, "nama animasi ganda: " + name
        merged.update(mod.SCENES)
    return merged


def main(only=None):
    """only: awalan nama animasi; bila diberikan, hanya animasi itu yang diekspor ulang (manifest tetap ditulis lengkap)."""
    os.makedirs(os.path.join(ROOT, "gif"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "sheets"), exist_ok=True)
    assert not set(PAL) & set(PAL_EXT), "kunci PAL_EXT bertabrakan dengan PAL"
    assert not (set(PAL) | set(PAL_EXT)) & set(PAL_HERO), "kunci PAL_HERO bertabrakan dengan PAL atau PAL_EXT"
    for name, (fn, n, ms) in all_scenes().items():
        if only and not name.startswith(only):
            continue
        frames = [fn(i) for i in range(n)]
        new_profile = pack.modern(name)
        cw, ch, gscale = pack.canvas_of(name)
        if new_profile:  # aset baru mulai Gerbang D: palet lokal (PAL + PAL_EXT + PAL_HERO), optimize, tanpa sheet4x
            index, palette = local_palette(frames)
            gif = [indexed(cv, gscale, index, palette) for cv in frames]
        else:  # aset lama dan gerbang A-C: jalur lama, byte identik
            gif = [indexed(cv, gscale) for cv in frames]
        path = os.path.join(ROOT, "gif", name + ".gif")
        opts = dict(save_all=True, append_images=gif[1:], duration=[ms(i) for i in range(n)], transparency=0, disposal=2,
                    optimize=new_profile)
        if pack.loops(name):
            opts["loop"] = 0
        gif[0].save(path, **opts)
        for scale in ((1,) if new_profile else (1, 4)):
            sheet = Image.new("RGBA", (cw * scale * n, ch * scale), (0, 0, 0, 0))
            for i, cv in enumerate(frames):
                sheet.paste(cv.image(scale), (i * cw * scale, 0))
            sheet.save(os.path.join(ROOT, "sheets", "%s%s.png" % (name, "" if scale == 1 else "@4x")), optimize=(cw, ch) != (W, H))   # kanvas sendiri (hero): PNG dioptimalkan, piksel sama
        print("%-13s %2d frame  %.1f detik  %d KB" % (name, n, sum(ms(i) for i in range(n)) / 1000, os.path.getsize(path) // 1024))
    write_manifest()


def write_manifest():
    """pack/manifest.json: peta kostum x state -> asset, dengan frame dan durasi dari SCENES."""
    import json

    os.makedirs(os.path.join(ROOT, "pack"), exist_ok=True)
    data = pack.manifest(all_scenes())
    path = os.path.join(ROOT, "pack", "manifest.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    cells = [c for row in data["cells"].values() for c in row.values()]
    baru = sum(1 for c in cells if c["origin"] == "baru")
    print("pack/manifest.json  %d sel (%d asli, %d baru), %d kostum, %d state" % (
        len(cells), len(cells) - baru, baru, len(data["costumes"]), len(data["states"])))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
