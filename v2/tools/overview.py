"""Ikhtisar beberapa karakter: satu baris per karakter, kolom = frame representatif tiap state + siluet idle.

    python3 v2/tools/overview.py out.png id1 id2 ...   (SC=3 default)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
from PIL import Image, ImageDraw  # noqa: E402
import cast  # noqa: E402
import char2  # noqa: E402

BG = (250, 247, 240)


def rep_frame(name, st):
    if name in ("idle",):
        return 0
    if st.core == "defeat" or name.startswith("defeat") or name in ("disappear", "fall", "leave"):
        return st.n - 1
    if st.core == "attack" or name in ("attack",):
        return int(st.n * 0.45)
    if st.core == "hit":
        return 3
    return st.n // 2


def overview(out, ids, sc=3):
    rows = []
    for cid in ids:
        ch = cast.get(cid)
        cells = []
        for name, st in ch.states.items():
            i = rep_frame(name, st)
            cells.append(("%s f%d" % (name, i), char2.render(ch, name, i).image(1)))
        fr = char2.render(ch, "idle", 0).image(1) if "idle" in ch.states else cells[0][1]
        a = fr.split()[3]
        sil = Image.new("RGBA", fr.size, (0, 0, 0, 0))
        sil.paste((20, 20, 20, 255), mask=a)
        cells.insert(0, ("siluet", sil))
        rows.append((cid, cells))
    cw, chh = 64 * sc + 4, 64 * sc + 14
    ncol = max(len(c) for _, c in rows)
    im = Image.new("RGB", (110 + ncol * cw, len(rows) * chh), BG)
    d = ImageDraw.Draw(im)
    for r, (cid, cells) in enumerate(rows):
        d.text((3, r * chh + chh // 2), cid, fill=(50, 30, 20))
        for c, (lab, fr) in enumerate(cells):
            x, y = 110 + c * cw, r * chh + 12
            fr = fr.resize((64 * sc, 64 * sc), Image.NEAREST)
            d.rectangle([x, y, x + 64 * sc - 1, y + 64 * sc - 1], outline=(228, 220, 206))
            im.paste(fr, (x, y), fr)
            d.text((x + 2, r * chh), lab, fill=(110, 90, 70))
    im.save(out)
    print(out, im.size)


if __name__ == "__main__":
    overview(sys.argv[1], sys.argv[2:], int(os.environ.get("SC", "3")))
