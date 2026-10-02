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
import vfx2  # noqa: E402

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
    x0, y0, w, h = cv.box
    im = Image.new("P", (w, h), 0)
    im.putpalette(pal)
    px = im.load()
    for (x, y), c in cv.px.items():
        px[x - x0, y - y0] = index[c]
    return im.resize((w * scale, h * scale), Image.NEAREST) if scale != 1 else im


def write_sheet(frames, path):
    index, pal = palette_frames(frames)
    w, h = frames[0].w, frames[0].h
    sheet = Image.new("P", (w * len(frames), h), 0)
    sheet.putpalette(pal)
    for i, cv in enumerate(frames):
        sheet.paste(indexed(cv, index, pal), (i * w, 0))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sheet.save(path, transparency=0, optimize=True)


def gif_durations(st):
    durs = st.durations()
    if not st.loop and st.hold:
        durs[-1] += st.hold * st.ms
    return durs


def write_gif(frames, st, path):
    index, pal = palette_frames(frames)
    durs = gif_durations(st)
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
    """Titik ikon aksesori sekunder: di kanan atas kepala pada idle f0 (dibaca arena), koordinat gambar sheet."""
    st = "idle" if "idle" in ch.states else list(ch.states)[0]
    p = R.pose()
    p.update(ch.states[st].fn(0))
    char2.quantize(p)
    g = R.Geo(p, ch.body)
    x0, y0 = (ch.canvas or (0, 0))[:2]
    return [int(g.hx + 11) - x0, int(g.hy - 16) - y0]


DAMAGE_LEVELS = ("normal", "damaged", "heavily_damaged")


def damaged(ch):
    """Karakter dengan tingkat kerusakan visual (Berserker): instance per tingkat."""
    if not getattr(ch, "damage_levels", None):
        return {}
    return {name: ch.__class__(dmg=k) for k, name in enumerate(DAMAGE_LEVELS) if k > 0}


def layer_paths(cid, name, prefix=""):
    return {lay: "sheets/%s/%slayers/%s.%s.png" % (cid, prefix, name, lay) for lay in char2.LAYERS}


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


def registry(only=None, shared=None):
    """shared[(cid, damage, state)] = lapisan yang identik dengan tingkat normal (berkas tidak ditulis ulang)."""
    shared = shared or {}
    chars = []
    for cid in cast.all_ids():
        ch = cast.get(cid)
        states = {}
        dmg = damaged(ch)
        variants = {}
        for name, st in ch.states.items():
            e = {
                "frames": st.n, "ms": st.ms, "loop": st.loop, "hold": st.hold, "label": st.label,
                "sheet": "sheets/%s/%s.png" % (cid, name), "gif": "gif/%s/%s.gif" % (cid, name),
            }
            if st.durs:
                e["durations"] = list(st.durs)
            if st.events:
                e["events"] = st.events
            if st.variant_of:
                e["variant_of"] = st.variant_of
                variants.setdefault(st.variant_of, [st.variant_of]).append(name)
            if ch.canvas:
                e["layers"] = layer_paths(cid, name)
            if dmg:
                e["damage"] = {}
                for lvl in dmg:
                    lp = layer_paths(cid, name, lvl + "/")
                    for lay in ("weapon", "vfx"):
                        if (cid, lvl, name, lay) in shared:
                            lp[lay] = e["layers"][lay]
                    e["damage"][lvl] = {"sheet": "sheets/%s/%s/%s.png" % (cid, lvl, name),
                                        "gif": "gif/%s/%s/%s.gif" % (cid, lvl, name), "layers": lp}
            states[name] = e
        entry = {
            "id": cid, "name": ch.name, "category": ch.category, "faction": ch.faction, "role": ch.role,
            "silhouette": list(ch.silhouette), "fallback": fallback_of(ch), "core": core_map(ch),
            "acc_anchor": acc_anchor(ch), "states": states,
        }
        if ch.canvas:
            x0, y0, w, h = ch.canvas
            entry["canvas"] = {"w": w, "h": h}
            entry["anchor"] = {"x": R.RX - x0, "baseline": R.BASE - y0, "facing": "right"}
        if variants:
            entry["variants"] = variants
        if getattr(ch, "aliases", None):
            entry["aliases"] = dict(ch.aliases)
        if dmg:
            entry["damage_levels"] = list(DAMAGE_LEVELS)
        for extra in ("label", "caption", "note"):
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
        "vfx": vfx_registry(),
        "blood": {"levels": vfx2.BLOOD_LEVELS, "default_level": 2, "only_on_hit": True,
                  "note": "darah hanya sprite VFX terpisah, bergaya piksel, singkat; tingkat 0 mematikannya"},
        "event_types": {"hit": "serangan kena di titik (x, y relatif jangkar, y=0 lantai); mesin memunculkan "
                               "darah sesuai tingkat bila target memang kena, lalu target recoil",
                        "hitstop": "bekukan penyerang dan target selama ms (hanya bila kena)",
                        "screen_shake": "getarkan kamera px piksel selama ms",
                        "vfx": "VFX sudah ada di lapisan vfx sheet (baked); nama sprite VFX terpisah untuk mesin "
                               "yang menggambar VFX sendiri",
                        "phase": "rentang frame tiap fase gerakan", "rage_on": "mode amuk aktif"},
    }


def vfx_registry():
    out = {}
    for s in vfx2.SPECS:
        out[s.name] = {"sheet": "vfx/%s.png" % s.name, "gif": "gif/vfx/%s.gif" % s.name, "frames": s.n,
                       "durations": list(s.durs), "loop": False, "canvas": {"w": s.size[0], "h": s.size[1]},
                       "anchor": {"x": s.anchor[0], "y": s.anchor[1]}, "kind": s.kind, "note": s.note}
        if s.blood_level is not None:
            out[s.name]["blood_level"] = s.blood_level
    for name, ev in vfx2.EVENT_KINDS.items():
        out[name] = dict(ev, kind="event")
    return out


class _St:
    def __init__(self, durs):
        self.durs, self.ms, self.loop, self.hold = durs, durs[0], False, 0

    def durations(self):
        return list(self.durs)


def write_vfx():
    for s in vfx2.SPECS:
        frames = [vfx2.render_spec(s, k) for k in range(s.n)]
        write_sheet(frames, os.path.join(V2, "vfx", s.name + ".png"))
        write_gif(frames, _St(s.durs), os.path.join(V2, "gif", "vfx", s.name + ".gif"))
    return len(vfx2.SPECS)


def export_all(ch, cid, name, prefix=""):
    """Komposit (sheet + GIF) dan lapisan body/weapon/vfx satu state. Kembalikan lapisan -> (path, piksel) untuk
    dibandingkan antar-tingkat kerusakan."""
    st = ch.states[name]
    allf = [char2.render_all(ch, name, i) for i in range(st.n)]
    comp = [a["composite"] for a in allf]
    write_sheet(comp, os.path.join(V2, "sheets", cid, prefix + name + ".png"))
    write_gif(comp, st, os.path.join(V2, "gif", cid, prefix + name + ".gif"))
    out = {}
    for lay in char2.LAYERS:
        frames = [a[lay] for a in allf]
        path = os.path.join(V2, "sheets", cid, prefix + "layers", "%s.%s.png" % (name, lay))
        write_sheet(frames, path)
        out[lay] = (path, [sorted(cv.px.items()) for cv in frames])
    return out


def main(argv):
    only = set(argv) or None
    n_states = 0
    for cid in cast.all_ids():
        if only and cid not in only:
            continue
        ch = cast.get(cid)
        dmg = damaged(ch)
        for name, st in ch.states.items():
            n_states += 1
            if not ch.canvas:
                frames = char2.frames(ch, name)
                write_sheet(frames, os.path.join(V2, "sheets", cid, name + ".png"))
                write_gif(frames, st, os.path.join(V2, "gif", cid, name + ".gif"))
            else:
                base_layers = export_all(ch, cid, name)
                for lvl, dch in dmg.items():
                    lay = export_all(dch, cid, name, lvl + "/")
                    for k in ("weapon", "vfx"):
                        if lay[k][1] == base_layers[k][1]:  # identik dengan normal: pakai berkas normal
                            os.remove(lay[k][0])
        print("ok", cid, len(ch.states))
    if only is None or "vfx" in only:
        print("vfx:", write_vfx())
    icons = write_icons()
    reg = registry(shared=_shared_from_disk())
    reg["icons"] = icons
    with open(os.path.join(V2, "registry.json"), "w") as f:
        json.dump(reg, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write("\n")
    context2.write_json(os.path.join(V2, "context.json"))
    print("state ditulis:", n_states, "| karakter di registry:", len(reg["characters"]))


def _shared_from_disk():
    """Saat ekspor sebagian: lapisan damage yang tidak punya berkas sendiri memakai berkas normal."""
    shared = {}
    for cid in cast.all_ids():
        ch = cast.get(cid)
        for lvl in damaged(ch):
            for name in ch.states:
                for k in ("weapon", "vfx"):
                    if not os.path.exists(os.path.join(V2, "sheets", cid, lvl, "layers", "%s.%s.png" % (name, k))):
                        shared[(cid, lvl, name, k)] = True
    return shared


if __name__ == "__main__":
    main(sys.argv[1:])
