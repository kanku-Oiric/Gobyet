"""Pratinjau konfirmasi kena untuk Berserker: hantaman -> hit-stop -> darah -> target recoil -> percikan -> debu.

    python3 v2/tools/hit_confirm_preview.py [STATE] [TINGKAT_DARAH]     # default: leap_spin_slash 2

Membaca sheet hasil ekspor (registry.json) seperti mesin game: frame Berserker, event "hit"/"hitstop" state itu,
sheet hit lawan (Fantasy Knight, dicerminkan menghadap kiri), dan sprite VFX darah sesuai tingkat
(registry["blood"]["levels"]). Darah tidak ada di sheet karakter; di sini dimunculkan hanya pada frame "hit".
Keluaran: v2/preview/berserker-<state>-hit.gif (3x) dan .png (strip frame 1x).
"""
import json
import os
import sys

from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.dirname(HERE)
SCALE = 3
ENEMY = "fantasy-knight"


def load():
    with open(os.path.join(V2, "registry.json")) as f:
        return json.load(f)


def strip(path, w, h, n):
    im = Image.open(os.path.join(V2, path)).convert("RGBA")
    return [im.crop((i * w, 0, (i + 1) * w, h)) for i in range(n)]


def char_frames(reg, cid, state):
    c = {x["id"]: x for x in reg["characters"]}[cid]
    st = c["states"][state]
    cv = c.get("canvas", reg["canvas"])
    an = c.get("anchor", reg["anchor"])
    durs = st.get("durations") or [st["ms"]] * st["frames"]
    return strip(st["sheet"], cv["w"], cv["h"], st["frames"]), durs, an, st


def vfx_frames(reg, name):
    v = reg["vfx"][name]
    return strip(v["sheet"], v["canvas"]["w"], v["canvas"]["h"], v["frames"]), v


def white(im):
    """Kilat putih satu frame pada target saat hantaman (siluet putih)."""
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste((250, 247, 240, 255), mask=im.split()[3])
    return out


def main(argv):
    state = argv[0] if argv else "leap_spin_slash"
    level = argv[1] if len(argv) > 1 else "2"
    reg = load()
    bf, bdurs, ban, bst = char_frames(reg, "berserker", state)
    hits = [e for e in bst.get("events", []) if e["type"] == "hit"]
    stops = {e["frame"]: e["ms"] for e in bst.get("events", []) if e["type"] == "hitstop"}
    hit = hits[-1]  # pukulan terakhir (hantaman utama)
    ec = {x["id"]: x for x in reg["characters"]}[ENEMY]
    eidle, eidle_d, ean, _ = char_frames(reg, ENEMY, ec["core"]["idle"])
    ehit, ehit_d, _, _ = char_frames(reg, ENEMY, ec["core"]["hit"])
    eidle = [ImageOps.mirror(f) for f in eidle]
    ehit = [ImageOps.mirror(f) for f in ehit]
    names = reg["blood"]["levels"][level]
    blood = [(n, *vfx_frames(reg, n)) for n in names]
    spark, sv = vfx_frames(reg, "spark")

    W, H = 192, bf[0].size[1]
    base = ban["baseline"]
    bx = 8  # posisi kanvas Berserker
    ax = bx + ban["x"]  # jangkar Berserker di kanvas pratinjau
    hx, hy = ax + hit["x"], base + hit["y"]
    ex_anchor = hx + 8  # jangkar lawan sedikit di belakang titik kena
    ew = eidle[0].size[0]
    ex = ex_anchor - (ew - 1 - ean["x"])  # lawan dicerminkan: jangkar x ikut dicerminkan
    ey = base - ean["baseline"]

    timeline = []  # (frame berserker, gambar lawan, [(sprite, x, y)], durasi)
    hf = hit["frame"]
    n_after = max(len(bf) - hf - 1, len(ehit))
    for i in range(hf):
        timeline.append((bf[i], eidle[i % len(eidle)], [], bdurs[i], 0))
    # hantaman: frame kena, lawan berkilat putih
    timeline.append((bf[hf], white(eidle[hf % len(eidle)]), [], bdurs[hf], 0))
    # hit-stop: semua beku
    timeline.append((bf[hf], eidle[hf % len(eidle)], [], stops.get(hf, 80), 0))
    for k in range(n_after):
        i = min(hf + 1 + k, len(bf) - 1)
        fx = []
        for name, frs, v in blood:
            kk = k - (1 if name == "blood_ground" else 0)
            if 0 <= kk < len(frs):
                if name == "blood_ground":
                    fx.append((frs[kk], ex_anchor + 4 - v["anchor"]["x"], base - 1 - v["anchor"]["y"]))
                else:
                    fx.append((frs[kk], hx - v["anchor"]["x"], hy - v["anchor"]["y"]))
        if k < len(spark):
            fx.append((spark[k], hx - sv["anchor"]["x"] - 3, hy - sv["anchor"]["y"] - 4))
        eh = ehit[min(k, len(ehit) - 1)]
        d = bdurs[i] if hf + 1 + k < len(bf) else ehit_d[min(k, len(ehit_d) - 1)]
        timeline.append((bf[i], eh, fx, d, min(k + 1, 5) * 2))  # lawan terdorong mundur (knockback)

    frames, durs = [], []
    for b, e, fx, d, kb in timeline:
        im = Image.new("RGBA", (W, H), (236, 230, 218, 255))
        for x in range(W):
            im.putpixel((x, base), (196, 184, 168, 255))
        im.alpha_composite(e, (ex + kb, ey))
        im.alpha_composite(b, (bx, 0))
        for spr, x, y in fx:
            im.alpha_composite(spr, (int(x), int(y)))
        frames.append(im)
        durs.append(d)
    out = os.path.join(V2, "preview")
    os.makedirs(out, exist_ok=True)
    gif = os.path.join(out, "berserker-%s-hit.gif" % state)
    big = [f.convert("RGB").resize((W * SCALE, H * SCALE), Image.NEAREST) for f in frames]
    big[0].save(gif, save_all=True, append_images=big[1:], duration=durs, loop=0, optimize=False)
    sheet = Image.new("RGBA", (W * len(frames), H))
    for i, f in enumerate(frames):
        sheet.paste(f, (i * W, 0))
    sheet.save(os.path.join(out, "berserker-%s-hit.png" % state), optimize=True)
    print(gif, len(frames), "frame,", sum(durs), "ms; darah tingkat", level, names)


if __name__ == "__main__":
    main(sys.argv[1:])
