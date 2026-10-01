"""Ekspor Gobyet v2: sprite sheet PNG 1x, GIF 4x, ikon aksesori, dan registry.json.

    python3 v2/src/export2.py            # semua karakter
    python3 v2/src/export2.py hacker     # hanya karakter tertentu (registry tetap ditulis lengkap)

Keluaran (relatif ke v2/):
    sheets/<id>/<state>.png   strip horizontal 64*n x 64, PNG berpalet, indeks 0 transparan
    gif/<id>/<state>.gif      256x256 transparan, durasi per frame, loop
    icons/<nama>.png          ikon aksesori 16x16 untuk konteks hibrida (satu sekunder)
    registry.json             data karakter, state, inti arena, fallback, jangkar
"""
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rig2 as R  # noqa: E402
import char2  # noqa: E402
import cast  # noqa: E402
import items2 as I  # noqa: E402
import props2  # noqa: E402,F401  (mendaftarkan prop)
import context2  # noqa: E402

V2 = os.path.dirname(HERE)
GIF_SCALE = 4
CORE = ("idle", "attack", "hit", "victory", "defeat")

# rantai fallback karakter (bagian 62): kelas -> basis faksi -> normal-gblk
FACTION_BASE = {"knights": "fantasy-knight", "vikings": "viking", "pirates": "fantasy-pirate"}
FALLBACK = {"viking": "fantasy-viking", "fantasy-viking": "normal-gblk", "fantasy-knight": "normal-gblk",
            "fantasy-pirate": "normal-gblk", "normal-gblk": None}


def fallback_of(ch):
    if ch.id in FALLBACK:
        return FALLBACK[ch.id]
    if ch.faction in FACTION_BASE and FACTION_BASE[ch.faction] != ch.id:
        return FACTION_BASE[ch.faction]
    return "normal-gblk"


def palette_frames(frames):
    keys = sorted({c for cv in frames for c in cv.px.values()})
    index = {k: i + 1 for i, k in enumerate(keys)}
    pal = [0, 0, 0] + [v for k in keys for v in R.rgb(k)]
    pal += [0] * (768 - len(pal))
    return index, pal


def indexed(cv, index, pal, scale=1):
    im = Image.new("P", (R.W, R.H), 0)
    im.putpalette(pal)
    px = im.load()
    for (x, y), c in cv.px.items():
        px[x, y] = index[c]
    return im.resize((R.W * scale, R.H * scale), Image.NEAREST) if scale != 1 else im


def write_sheet(frames, path):
    index, pal = palette_frames(frames)
    sheet = Image.new("P", (R.W * len(frames), R.H), 0)
    sheet.putpalette(pal)
    for i, cv in enumerate(frames):
        sheet.paste(indexed(cv, index, pal), (i * R.W, 0))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sheet.save(path, transparency=0, optimize=True)


def write_gif(frames, st, path):
    index, pal = palette_frames(frames)
    durs = [st.ms] * len(frames)
    if not st.loop and st.hold:
        durs[-1] += st.hold * st.ms
    # Frame kosong total ditulis Pillow dengan header rusak; durasinya digabung ke frame sebelumnya
    # (sheet PNG tetap menyimpan frame kosong itu).
    ims, ds = [], []
    for cv, d in zip(frames, durs):
        if not cv.px and ims:
            ds[-1] += d
            continue
        ims.append(indexed(cv, index, pal, GIF_SCALE))
        ds.append(d)
    durs = ds
    os.makedirs(os.path.dirname(path), exist_ok=True)
    ims[0].save(path, save_all=True, append_images=ims[1:], duration=durs, loop=0, transparency=0, disposal=2,
                optimize=False)


def acc_anchor(ch):
    """Titik ikon aksesori sekunder: di kanan atas kepala pada idle f0 (dibaca arena)."""
    st = "idle" if "idle" in ch.states else list(ch.states)[0]
    p = R.pose()
    p.update(ch.states[st].fn(0))
    char2.quantize(p)
    g = R.Geo(p, ch.body)
    return [int(g.hx + 11), int(g.hy - 16)]


def core_map(ch):
    core = {}
    for name, st in ch.states.items():
        if st.core and st.core not in core:
            core[st.core] = name
    for c in CORE:
        if c not in core and c in ch.states:
            core[c] = c
    return core


def write_icons():
    """Ikon 16x16 untuk aksesori sekunder (satu ikon per domain)."""
    out = {}
    for name, (item, kw, grip, ang) in context2.ICON_DRAW.items():
        cv = R.Canvas()
        I.ITEMS[item][0](cv, grip, ang, dict(kw))
        im = cv.image(1).crop((24, 24, 40, 40))
        path = os.path.join(V2, "icons", name + ".png")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        im.save(path, optimize=True)
        out[name] = "icons/%s.png" % name
    return out


def registry(only=None):
    chars = []
    for cid in cast.all_ids():
        ch = cast.get(cid)
        states = {}
        for name, st in ch.states.items():
            states[name] = {
                "frames": st.n, "ms": st.ms, "loop": st.loop, "hold": st.hold, "label": st.label,
                "sheet": "sheets/%s/%s.png" % (cid, name), "gif": "gif/%s/%s.gif" % (cid, name),
            }
        entry = {
            "id": cid, "name": ch.name, "category": ch.category, "faction": ch.faction, "role": ch.role,
            "silhouette": list(ch.silhouette), "fallback": fallback_of(ch), "core": core_map(ch),
            "acc_anchor": acc_anchor(ch), "states": states,
        }
        for extra in ("label", "caption"):
            if getattr(ch, extra, None) and isinstance(getattr(ch, extra), str):
                entry[extra] = getattr(ch, extra)
        chars.append(entry)
    return {
        "format": "gobyet-v2/1",
        "generated_by": "v2/src/export2.py",
        "canvas": {"w": R.W, "h": R.H},
        "anchor": {"x": R.RX, "baseline": R.BASE, "facing": "right"},
        "gif_scale": GIF_SCALE,
        "core_states": list(CORE),
        "root_fallback": "normal-gblk",
        "characters": chars,
    }


def main(argv):
    only = set(argv) or None
    n_states = 0
    for cid in cast.all_ids():
        if only and cid not in only:
            continue
        ch = cast.get(cid)
        for name, st in ch.states.items():
            frames = char2.frames(ch, name)
            write_sheet(frames, os.path.join(V2, "sheets", cid, name + ".png"))
            write_gif(frames, st, os.path.join(V2, "gif", cid, name + ".gif"))
            n_states += 1
        print("ok", cid, len(ch.states))
    icons = write_icons()
    reg = registry()
    reg["icons"] = icons
    with open(os.path.join(V2, "registry.json"), "w") as f:
        json.dump(reg, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write("\n")
    context2.write_json(os.path.join(V2, "context.json"))
    print("state ditulis:", n_states, "| karakter di registry:", len(reg["characters"]))


if __name__ == "__main__":
    main(sys.argv[1:])
