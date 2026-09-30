#!/usr/bin/env python3
"""Validasi Gobyet Character Pack. Pustaka standar + Pillow (sudah dipakai export).

    python3 src/validate_pack.py [--gate D | --all] [--palette-study]

--gate X hanya membatasi tabel beat yang dicetak; semua pemeriksaan GAGAL selalu dijalankan untuk
seluruh manifest. --all mencetak tabel beat semua aset baru.

V1  Hash: aset asli (pack/sha256-asli.txt) dan aset yang disetujui (pack/sha256-disetujui.txt) identik byte.
V2  Manifest dan schema: kostum (group, base, caption, applies), setiap sel berlaku, keyframe valid,
    file yang dirujuk ada dan ukurannya cocok; sheet4x opsional untuk aset baru mulai Gerbang D.
V3  Palet, kanvas, alfa: sheet hanya dari PAL (aset lama) atau PAL + PAL_EXT (aset baru); alfa 0/255;
    sheet4x = sheet 1x diperbesar; setiap frame GIF hasil decode = frame sheet diperbesar 8x, total
    durasi sama, loop tak hingga.
V4  Loop seam: selisih frame terakhir->pertama <= 1,25 x selisih maksimum antar-frame berurutan.
    Aset terkunci di atas ambang = DIKETAHUI; aset lain = GAGAL.
V5  Siluet (IoU mask buram frame kunci): idle antar kostum dasar (> 0,90 dilaporkan); defeated vs idle
    per kostum (<= 0,85; GAGAL untuk aset baru yang belum terkunci); varian vs saudara sefaksi.
V6  Warna dominan dari piksel kostum saja (piksel yang berbeda dari Normal idle pada posisi sama, di luar
    warna tubuh) dan jarak warna antar kostum dasar (CIE76 Delta E); pasangan terdekat.
V7  Ukuran prop di 1x (target heuristik >= 6x6).
V8  Audit teks: semua pemanggil mini_text (termasuk impor langsung dan alias) diinstrumentasi; glyph hanya
    dari MINI; maksimal 3 karakter kecuali pengecualian yang disahkan pemilik.
V9  Audit tarian: dance-* tepat 16 frame x 120 ms, seam lulus, perubahan pose terbesar ada di beat.
V10 Ukuran per gerbang, anggaran 16 MB dari kondisi awal Fase 2 lanjutan, dan proyeksi sampai selesai.
Beat per rentang frame dicetak untuk aset baru (ekspresi dan teks yang benar-benar digambar).
Keluar dengan kode 1 bila ada pemeriksaan wajib yang gagal.
"""
import hashlib
import json
import os
import subprocess
import sys
from collections import Counter

from PIL import Image, ImageSequence

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import monkey  # noqa: E402
import pack  # noqa: E402
import export  # noqa: E402  (mendaftarkan semua modul adegan)
from costumes import CX, CY  # noqa: E402

W, H = monkey.W, monkey.H
PAL_RGB = {tuple(v) for v in monkey.PAL.values()}
EXT_RGB = PAL_RGB | {tuple(v) for v in monkey.PAL_EXT.values()}
REV = {tuple(v): k for k, v in list(monkey.PAL.items()) + list(monkey.PAL_EXT.items())}
FAILS = []
LOCK_FILES = ("sha256-asli.txt", "sha256-disetujui.txt")  # terkunci: seam di atas ambang = DIKETAHUI
MADE_FILE = "sha256-dibuat.txt"  # aset gerbang yang sudah dibuat tetapi belum disetujui: hash wajib tetap
GROUPS = ("core", "role", "domain", "fantasy", "theology", "special")
SEAM_FACTOR = 1.25
DANCE_FRAMES, DANCE_MS = 16, 120
BUDGET_BYTES = 16 * 1024 * 1024
WARN_BYTES = 15 * 1024 * 1024  # ambang peringatan pemilik: proyeksi di atasnya = STOP-DARURAT
BUDGET_BASE_COMMIT = "dd78be8"  # kondisi awal Fase 2 lanjutan (Gerbang C terkunci)

# V8: pengecualian aturan <= 3 karakter yang disahkan pemilik, per awalan nama animasi.
TEXT_EXCEPTIONS = {
    "scientist-": {"E=mc"},     # papan tulis asli rambut-einstein, statis (tidak ditulis ulang per frame)
    "normal-gblk-": {"GBLK"},   # papan tanda GBLK
}
STATIC_TEXT = {"E=mc"}  # papan Scientist: harus di posisi yang sama pada setiap frame yang memuatnya
VISIBLE_AT_KEYFRAME = {"GBLK"}  # papan GBLK boleh bergerak, tetapi di frame kunci tidak boleh tertutup


def pixels(im):
    """Daftar piksel; get_flattened_data bila tersedia (getdata deprecated di Pillow baru)."""
    return list(im.get_flattened_data()) if hasattr(im, "get_flattened_data") else list(im.getdata())


def fail(msg):
    FAILS.append(msg)
    print("  GAGAL: " + msg)


def rel(path):
    return os.path.relpath(path, ROOT)


def load_manifest():
    with open(os.path.join(ROOT, "pack", "manifest.json"), encoding="utf-8") as fh:
        return json.load(fh)


def cell_path(p):
    return os.path.normpath(os.path.join(ROOT, "pack", p))


def cells(m):
    for costume, row in m["cells"].items():
        for state, cell in row.items():
            yield costume, state, cell


def frames_of(sheet_path, scale=1):
    im = Image.open(sheet_path).convert("RGBA")
    fw = W * scale
    return [im.crop((i * fw, 0, (i + 1) * fw, H * scale)) for i in range(im.width // fw)]


def keyframe_image(cell):
    return frames_of(cell_path(cell["sheet"]))[cell["keyframe"]]


def locked_files():
    out = set()
    for name in LOCK_FILES:
        path = os.path.join(ROOT, "pack", name)
        if os.path.exists(path):
            out |= {line.split(None, 1)[1].strip() for line in open(path, encoding="utf-8") if line.strip()}
    return out


def is_locked(cell, locked):
    return rel(cell_path(cell["sheet"])) in locked


def is_modern(cell):
    return cell.get("origin") == "baru" and cell.get("gate") not in pack.LEGACY_GATES


def base_costumes(m):
    """Kostum dasar: tanpa base, atau group special (normal-gblk berinduk normal tapi kostum dasar)."""
    return [c for c in m["costumes"] if not c.get("base") or c.get("group") == "special"]


# ------------------------------------------------------------------ V1
def check_hashes():
    print("\n[V1] Hash aset yang dikunci dan aset yang sudah dibuat")
    for name in LOCK_FILES + (MADE_FILE,):
        path = os.path.join(ROOT, "pack", name)
        if not os.path.exists(path):
            print("  %s: tidak ada (dilewati)" % name)
            continue
        ok = bad = 0
        for line in open(path, encoding="utf-8"):
            if not line.strip():
                continue
            digest, f = line.split(None, 1)
            full = os.path.join(ROOT, f.strip())
            if not os.path.exists(full):
                fail("%s: %s hilang" % (name, f.strip()))
                bad += 1
            elif hashlib.sha256(open(full, "rb").read()).hexdigest() != digest:
                fail("%s: %s BERUBAH" % (name, f.strip()))
                bad += 1
            else:
                ok += 1
        print("  %s: %d identik, %d berubah/hilang" % (name, ok, bad))


# ------------------------------------------------------------------ V2 + V3
def gif_timeline_matches(cell, gif_path, sheet_frames):
    """Setiap frame GIF hasil decode = frame sheet (diperbesar 8x) yang aktif pada waktu mulainya."""
    starts, t = [], 0
    for d in cell["durations_ms"]:
        starts.append(t)
        t += d
    gif = Image.open(gif_path)
    loop = gif.info.get("loop")
    t, n, bad = 0, 0, []
    big = {}
    for fr in ImageSequence.Iterator(gif):
        idx = max(i for i, s in enumerate(starts) if s <= t)
        if idx not in big:
            big[idx] = sheet_frames[idx].resize((W * 8, H * 8), Image.NEAREST).convert("RGBa").tobytes()
        if fr.convert("RGBA").convert("RGBa").tobytes() != big[idx]:
            bad.append(n)
        t += fr.info.get("duration", 0)
        n += 1
    return n, t, loop, bad


def check_manifest_and_palette(m):
    print("\n[V2] Manifest dan schema, [V3] palet, kanvas, alfa, isi GIF")
    ids = [c["id"] for c in m["costumes"]]
    states = [s["id"] for s in m["states"]]
    for c in m["costumes"]:
        if c.get("group") not in GROUPS:
            fail("%s: group tidak dikenal %r" % (c["id"], c.get("group")))
        if "base" in c and c["base"] not in ids:
            fail("%s: base %r tidak ada di daftar kostum" % (c["id"], c["base"]))
        if "caption" in c and not isinstance(c["caption"], str):
            fail("%s: caption bukan string" % c["id"])
        for st, rule in c.get("applies", {}).items():
            if st not in states or rule not in ("required", "optional"):
                fail("%s: applies %s=%r tidak valid" % (c["id"], st, rule))
    applicable = sum(len(c.get("applies", {})) for c in m["costumes"])
    n = 0
    for costume, state, cell in cells(m):
        n += 1
        tag = "%s/%s" % (costume, state)
        entry = next((c for c in m["costumes"] if c["id"] == costume), None)
        if entry is None or state not in entry.get("applies", {}):
            fail("%s: sel terisi tetapi tidak berlaku menurut applies" % tag)
        if cell.get("origin") not in ("asli", "baru"):
            fail("%s: origin tidak valid" % tag)
        if cell.get("origin") == "baru":
            if not cell.get("gate"):
                fail("%s: sel baru tanpa gate" % tag)
            if cell.get("source") != "%s-%s" % (costume, state):
                fail("%s: nama file bukan <kostum>-<state> (%s)" % (tag, cell.get("source")))
        k = cell.get("keyframe")
        if not isinstance(k, int) or not 0 <= k < cell["frames"]:
            fail("%s: keyframe %r tidak valid" % (tag, k))
        if len(cell["durations_ms"]) != cell["frames"] or cell.get("loop") is not True:
            fail("%s: durations/loop tidak cocok dengan jumlah frame" % tag)
        keys = ["sheet", "gif"] + (["sheet4x"] if "sheet4x" in cell else [])
        if "sheet4x" not in cell and not is_modern(cell):
            fail("%s: aset lama wajib punya sheet4x" % tag)
        paths = {key: cell_path(cell[key]) for key in keys}
        missing = [key for key, p in paths.items() if not os.path.exists(p)]
        if missing:
            fail("%s: file hilang %s" % (tag, missing))
            continue
        allowed = EXT_RGB if is_modern(cell) else PAL_RGB
        one = Image.open(paths["sheet"]).convert("RGBA")
        if one.size != (W * cell["frames"], H):
            fail("%s: ukuran sheet 1x %s" % (tag, one.size))
        if "sheet4x" in paths:
            four = Image.open(paths["sheet4x"]).convert("RGBA")
            if four.size != (W * 4 * cell["frames"], H * 4) or four.tobytes() != one.resize(four.size, Image.NEAREST).tobytes():
                fail("%s: sheet 4x bukan pembesaran nearest dari sheet 1x" % tag)
        alphas = {a for (_, _, _, a) in pixels(one)}
        if not alphas <= {0, 255}:
            fail("%s: alfa parsial %s" % (tag, sorted(alphas - {0, 255})[:5]))
        colors = {(r, g, b) for (r, g, b, a) in pixels(one) if a}
        if not colors <= allowed:
            fail("%s: warna di luar palet yang diizinkan %s" % (tag, sorted(colors - allowed)[:5]))
        gw, gh = Image.open(paths["gif"]).size
        if (gw, gh) != (W * 8, H * 8):
            fail("%s: ukuran GIF %sx%s" % (tag, gw, gh))
            continue
        gn, gt, loop, bad = gif_timeline_matches(cell, paths["gif"], frames_of(paths["sheet"]))
        if gn > cell["frames"] or gt != sum(cell["durations_ms"]) or loop != 0 or bad:
            fail("%s: GIF %d frame/%d ms/loop %r, frame beda %s vs manifest %d frame/%d ms" % (
                tag, gn, gt, loop, bad[:5], cell["frames"], sum(cell["durations_ms"])))
    print("  %d kostum, %d state, %d sel berlaku, %d sel terisi; %d gagal" % (len(ids), len(states), applicable, n, len(FAILS)))


# ------------------------------------------------------------------ V4
def diff(a, b):
    return sum(1 for p, q in zip(pixels(a), pixels(b)) if p != q)


def check_seams(m):
    print("\n[V4] Loop seam (piksel berbeda; seam = frame terakhir -> frame pertama)")
    print("  ambang = %.2f x selisih maksimum antar-frame berurutan di aset itu sendiri" % SEAM_FACTOR)
    print("  %-26s %-8s %6s %7s %6s  %s" % ("sel", "status", "maks", "ambang", "seam", "hasil"))
    locked = locked_files()
    for costume, state, cell in cells(m):
        fr = frames_of(cell_path(cell["sheet"]))
        steps = [diff(fr[i], fr[i + 1]) for i in range(len(fr) - 1)]
        seam = diff(fr[-1], fr[0])
        limit = SEAM_FACTOR * max(steps)
        lk = is_locked(cell, locked)
        ok = seam <= limit
        verdict = "lulus" if ok else ("DIKETAHUI (terkunci, tidak diubah)" if lk else "GAGAL")
        print("  %-26s %-8s %6d %7.1f %6d  %s" % (costume + "/" + state, "terkunci" if lk else "baru", max(steps), limit, seam, verdict))
        if not ok and not lk:
            fail("%s/%s: loop seam %d > %.1f" % (costume, state, seam, limit))


# ------------------------------------------------------------------ V5
def mask(im):
    return {i for i, (_, _, _, a) in enumerate(pixels(im)) if a}


def iou(a, b):
    return len(a & b) / float(len(a | b))


def check_silhouettes(m):
    print("\n[V5] Siluet: IoU mask buram frame kunci")
    print("  catatan: semua kostum memakai kepala dan badan yang sama, jadi IoU dasar antar-kostum sudah tinggi")
    masks = {c["id"]: mask(keyframe_image(m["cells"][c["id"]]["idle"]))
             for c in base_costumes(m) if "idle" in m["cells"].get(c["id"], {})}
    names = list(masks)
    print("  a) idle antar kostum dasar (> 0,90 = kandidat terlalu mirip)")
    print("  %-10s" % "" + "".join("%7s" % n[:6] for n in names))
    flagged = []
    for a in names:
        print("  %-10s" % a[:10] + "".join("%7.2f" % iou(masks[a], masks[b]) for b in names))
        flagged += [(a, b, iou(masks[a], masks[b])) for b in names if a < b and iou(masks[a], masks[b]) > 0.90]
    top = sorted(((iou(masks[a], masks[b]), a, b) for i, a in enumerate(names) for b in names[i + 1:]), reverse=True)[:3]
    print("  tertinggi: %s" % ", ".join("%s-%s %.2f" % (a, b, v) for v, a, b in top))
    print("  pasangan > 0,90: %s" % (", ".join("%s-%s %.2f" % f for f in flagged) if flagged else "tidak ada"))
    print("  b) defeated vs idle pada kostum yang sama (<= 0,85)")
    locked = locked_files()
    found = False
    for costume, row in m["cells"].items():
        if "defeated" in row and "idle" in row:
            found = True
            v = iou(mask(keyframe_image(row["defeated"])), mask(keyframe_image(row["idle"])))
            lk = is_locked(row["defeated"], locked)
            verdict = "lulus" if v <= 0.85 else ("DIKETAHUI (terkunci)" if lk else "GAGAL")
            print("    %-20s %.2f  %s" % (costume, v, verdict))
            if v > 0.85 and not lk:
                fail("%s: IoU defeated vs idle %.2f > 0,85" % (costume, v))
    if not found:
        print("    belum ada kostum dengan idle dan defeated")
    print("  c) varian vs saudara sefaksi (dilaporkan)")
    fams = {}
    for c in m["costumes"]:
        if c.get("base") and c.get("group") == "fantasy" and "idle" in m["cells"].get(c["id"], {}):
            fams.setdefault(c["base"], []).append(c["id"])
    if not fams:
        print("    belum ada varian dengan idle")
    for base, members in fams.items():
        group = ([base] if "idle" in m["cells"].get(base, {}) else []) + members
        vm = {x: mask(keyframe_image(m["cells"][x]["idle"])) for x in group}
        for i, a in enumerate(group):
            for b in group[i + 1:]:
                print("    %-20s %-20s %.2f" % (a, b, iou(vm[a], vm[b])))


# ------------------------------------------------------------------ V6
BODY_KEYS = set("KBbFfEM")  # garis tepi, bulu, kulit, telinga dalam, hidung/mulut: sama di semua kostum
EYE_PIXELS = {"W": 16, "P": 8}  # putih mata dan pupil dua mata terbuka, dikurangkan dari hitungan


def lab(rgb):
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in rgb)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t):
        return t ** (1 / 3.0) if t > 0.008856 else 7.787 * t + 16 / 116.0
    return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))


def delta_e(a, b):
    return sum((p - q) ** 2 for p, q in zip(lab(a), lab(b))) ** 0.5


def costume_colors(m, costume):
    """(state, Counter kunci palet) dari piksel kostum saja: piksel buram frame kunci yang berbeda dari
    Normal idle pada posisi sama, di luar warna tubuh; piksel mata dikurangkan."""
    row = m["cells"].get(costume, {})
    order = [s["id"] for s in m["states"]]
    state = "idle" if "idle" in row else sorted(row, key=order.index)[0]
    ref = pixels(keyframe_image(m["cells"]["normal"]["idle"]))
    cur = pixels(keyframe_image(row[state]))
    fx = effect_mask(costume, state, row[state]["keyframe"])
    counts = Counter(REV[p[:3]] for i, (p, q) in enumerate(zip(cur, ref))
                     if p[3] and p != q and fx.get((i % W, i // W)) != REV[p[:3]])
    for k in list(counts):
        if k in BODY_KEYS:
            del counts[k]
    for k, n in EYE_PIXELS.items():
        counts[k] = max(0, counts[k] - n)
    return state, +counts


def effect_mask(costume, state, keyframe):
    """Piksel efek bersama yang bukan pakaian, per posisi: aura kostum teologi (identik untuk Pak Haji dan
    Priest menurut 7.2e, jadi tidak bisa menjadi pembeda warna). Kostum lain: kosong."""
    try:
        import theology
    except ModuleNotFoundError:
        return {}
    if costume not in theology.COSTUMES:
        return {}
    return theology.aura_mask(*theology.aura_params(state, keyframe))


def dominants(m):
    out = {}
    for c in base_costumes(m):
        if not m["cells"].get(c["id"]):
            continue
        if c["id"] == "normal":
            out["normal"] = ("idle", "B", None, 100)
            continue
        state, counts = costume_colors(m, c["id"])
        ranked = counts.most_common()
        total = sum(counts.values()) or 1
        out[c["id"]] = (state, ranked[0][0], ranked[1][0] if len(ranked) > 1 else None, 100 * ranked[0][1] // total)
    return out


def check_colors(m):
    print("\n[V6] Warna dominan dari piksel kostum saja dan jarak warna (CIE76 Delta E; target >= 15)")
    print("  metode: frame kunci idle (atau sel pertama bila belum ada idle); piksel yang berbeda dari Normal idle")
    print("  pada posisi sama; warna tubuh (%s) tidak dihitung; 16 W + 8 P (mata) dikurangkan." % "".join(sorted(BODY_KEYS)))
    print("  Kostum teologi: piksel aura (mask identik untuk keduanya, 7.2e) tidak dihitung sebagai pakaian.")
    print("  Normal tidak berkostum: warnanya bulu B.")
    dom = dominants(m)
    for c in base_costumes(m):
        if c["id"] not in dom:
            print("  %-18s belum ada aset (dilewati)" % c["id"])
            continue
        state, k1, k2, share = dom[c["id"]]
        print("  %-18s %-10s dominan %s %-15s %3d%%   kedua %s" % (
            c["id"], "(" + state + ")", k1, str(monkey.rgb(k1)), share, ("%s %s" % (k2, monkey.rgb(k2))) if k2 else "-"))
    names = list(dom)
    pairs = sorted((delta_e(monkey.rgb(dom[a][1]), monkey.rgb(dom[b][1])), a, b) for i, a in enumerate(names) for b in names[i + 1:])
    print("  pasangan terdekat:")
    for d, a, b in pairs[:8]:
        print("    %-18s %-18s %s vs %s  Delta E %5.1f%s" % (a, b, dom[a][1], dom[b][1], d, "  < 15" if d < 15 else ""))
    fams = {}
    for c in m["costumes"]:
        if c.get("base") and c.get("group") == "fantasy" and m["cells"].get(c["id"]):
            fams.setdefault(c["base"], []).append(c["id"])
    for base, members in fams.items():
        acc = {x: costume_colors(m, x)[1].most_common(1)[0][0] for x in members}
        print("  aksen varian %s (target Delta E >= 10 antar saudara): %s" % (base, ", ".join("%s=%s" % kv for kv in acc.items())))
        for i, a in enumerate(members):
            for b in members[i + 1:]:
                d = delta_e(monkey.rgb(acc[a]), monkey.rgb(acc[b]))
                print("    %-20s %-20s Delta E %5.1f%s" % (a, b, d, "  < 10" if d < 10 else ""))


def palette_study(m):
    """Bagian 6.1: berapa warna dominan berbeda (Delta E >= 15) yang tersedia, dibanding kebutuhan."""
    print("\n[Studi palet 6.1] warna dominan berbeda dengan Delta E >= 15")
    def greedy(keys, fixed=()):
        best = []
        for start in range(len(keys)):
            chosen = list(fixed)
            for k in keys[start:] + keys[:start]:
                if all(delta_e(monkey.rgb(k), monkey.rgb(c)) >= 15 for c in chosen):
                    chosen.append(k)
            if len(chosen) - len(fixed) > len(best):
                best = chosen[len(fixed):]
        return best
    body_only = set("KFfEMb")
    pal_keys = sorted(k for k in monkey.PAL if k not in body_only)
    print("  PAL: %d kunci; tanpa warna kulit/garis tepi (%s): %d kunci" % (len(monkey.PAL), "".join(sorted(body_only)), len(pal_keys)))
    free = greedy(pal_keys)
    print("  himpunan terbesar (greedy) yang saling >= 15 di PAL: %d warna: %s" % (len(free), " ".join(free)))
    dom = dominants(m)
    fixed = sorted({v[1] for v in dom.values()})
    print("  dominan kostum yang sudah punya aset (%d kostum, %d warna): %s" % (len(dom), len(fixed), " ".join(fixed)))
    extra = greedy([k for k in pal_keys if k not in fixed], fixed=fixed)
    need = len(base_costumes(m)) - len(dom)
    print("  warna PAL tambahan yang >= 15 dari semua dominan itu dan satu sama lain: %d (%s)" % (len(extra), " ".join(extra)))
    print("  kebutuhan: %d kostum dasar tanpa aset -> %s" % (need, "CUKUP" if len(extra) >= need else "KURANG %d" % (need - len(extra))))
    if monkey.PAL_EXT:
        ext = greedy(sorted(monkey.PAL_EXT), fixed=fixed + extra)
        print("  dengan PAL_EXT (%s): tambahan %d (%s) -> total tersedia %d" % (
            " ".join(sorted(monkey.PAL_EXT)), len(ext), " ".join(ext), len(extra) + len(ext)))


# ------------------------------------------------------------------ V7
def props():
    import roles
    import domains
    table = {
        "referee: peluit": lambda cv: roles.whistle(cv, 32, 23),
        "referee: papan klip": lambda cv: roles.clipboard(cv, 20, 20),
        "judge: palu": lambda cv: roles.gavel(cv, 30, 30, 78),
        "judge: landasan": lambda cv: roles.sound_block(cv, 30, 30),
        "judge: papan skor": lambda cv: roles.score_paddle(cv, 20, 10),
        "skeptic: monokel": lambda cv: roles.monocle(cv, 32, 14),
        "skeptic: stempel": lambda cv: roles.stamp(cv, 28, 20),
        "skeptic: kertas bercap": lambda cv: roles.paper(cv, 28, 20, mark=True),
        "champion: piala": lambda cv: roles.trophy(cv, 26, 20),
        "champion: medali": lambda cv: roles.medal(cv, 31.5, 20.5),
        "greek: gulungan terbuka": lambda cv: domains.open_scroll(cv, 20, 10, 9),
        "greek: gulungan menggelinding": lambda cv: domains.rolling_scroll(cv, 20, 30, 0),
        "academic: topi toga": lambda cv: domains.mortarboard(cv, 32, 30),
        "academic: ijazah terbuka": lambda cv: domains.open_diploma(cv, 20, 20),
        "academic: ijazah kusut": lambda cv: domains.crumpled_diploma(cv, 30, 30),
        "normal: pisang": lambda cv: monkey.banana(cv, 30, 30),
    }
    table.update(getattr(domains, "PROPS", {}))
    import importlib
    for mod in ("special", "fantasy", "theology"):  # modul kostum Gerbang G dan sesudahnya (yang sudah ada)
        try:
            table.update(getattr(importlib.import_module(mod), "PROPS", {}))
        except ModuleNotFoundError:
            pass
    return table


def check_props():
    print("\n[V7] Ukuran prop di 1x (kotak pembatas, digambar sendirian; target heuristik >= 6x6)")
    for name, draw in props().items():
        cv = monkey.Canvas()
        draw(cv)
        xs = [x for x, _ in cv.px]
        ys = [y for _, y in cv.px]
        w, h = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
        print("  %-30s %2dx%-2d  %s" % (name, w, h, "ok" if min(w, h) >= 6 else "di bawah 6x6"))


# ------------------------------------------------------------------ V8 + beat
def _patch_everywhere(original, replacement):
    """Ganti setiap atribut modul yang menunjuk ke fungsi `original` (impor langsung, alias, dll)."""
    patched = []
    for mod in list(sys.modules.values()):
        d = getattr(mod, "__dict__", None)
        if not isinstance(d, dict):
            continue
        for key, val in list(d.items()):
            if val is original:
                d[key] = replacement
                patched.append((d, key))
    return patched


def instrumented(fn, n, ms):
    """Jalankan fungsi frame sambil mencatat ekspresi kepala dan setiap panggilan mini_text per frame.
    Teks dengan glyph yang tidak ada di MINI dicatat lalu dilewati (tidak menghentikan audit)."""
    real_head, real_text = monkey.head, monkey.mini_text
    log = []

    def head(cv, cx, cy, eyes="look", brows="flat", mouth="frown", face="F", tilt=0):
        log.append(("head", eyes, brows, mouth))
        return real_head(cv, cx, cy, eyes=eyes, brows=brows, mouth=mouth, face=face, tilt=tilt)

    def mini_text(cv, s, x, y, c):
        log.append(("text", s, x, y, c))
        if all(ch in monkey.MINI for ch in s):
            return real_text(cv, s, x, y, c)
        return None

    patched = _patch_everywhere(real_head, head) + _patch_everywhere(real_text, mini_text)
    rows = []
    try:
        for i in range(n):
            del log[:]
            fn(i)
            heads = [e for e in log if e[0] == "head"]
            h = heads[-1] if heads else ("head", "-", "-", "-")
            texts = [e[1:4] for e in log if e[0] == "text"]
            rows.append((i, int(ms(i)), h[1], h[2], h[3], texts))
    finally:
        for d, key in patched:
            d[key] = real_head if d[key] is head else real_text
    return rows


def text_violations(name, rows):
    allowed_long = set()
    for prefix, strings in TEXT_EXCEPTIONS.items():
        if name.startswith(prefix):
            allowed_long |= strings
    out = []
    positions = {}
    for i, _, _, _, _, texts in rows:
        for s, x, y in texts:
            bad = [ch for ch in s if ch not in monkey.MINI]
            if bad:
                out.append("f%d teks %r memakai glyph di luar MINI %s" % (i, s, bad))
            elif len(s) > 3 and s not in allowed_long:
                out.append("f%d teks %r lebih dari 3 karakter" % (i, s))
            if s in STATIC_TEXT:
                positions.setdefault(s, set()).add((x, y))
    for s, pos in positions.items():
        if len(pos) > 1:
            out.append("teks %r tidak statis (posisi berubah: %s)" % (s, sorted(pos)[:4]))
    return out


def hidden_text_pixels(fn, keyframe, text):
    """Jumlah piksel glyph `text` yang tertimpa gambar lain di frame kunci (0 = terbaca utuh)."""
    real = monkey.mini_text
    spots = []

    def spy(cv, s, x, y, c):
        if s == text:
            spots.append((x, y, c))
        return real(cv, s, x, y, c)
    patched = _patch_everywhere(real, spy)
    try:
        cv = fn(keyframe)
    finally:
        for d, key in patched:
            d[key] = real
    covered = 0
    for x, y, c in spots:
        for i, ch in enumerate(text):
            for ry, row in enumerate(monkey.MINI[ch]):
                for rx, v in enumerate(row):
                    p = (x + i * 6 + rx, y + ry)
                    if v == "1" and 0 <= p[0] < W and 0 <= p[1] < H and cv.px.get(p) != c:
                        covered += 1
    return len(spots), covered


def check_texts_and_beats(m, gate, show_all):
    print("\n[V8] Audit teks (semua pemanggil mini_text diinstrumentasi) dan beat per rentang frame")
    scenes_all = export.all_scenes()
    for costume, state, cell in cells(m):
        if cell["origin"] != "baru" or cell["source"] not in scenes_all:
            continue
        rows = instrumented(*scenes_all[cell["source"]])
        texts = sorted({s for r in rows for s, _, _ in r[5]})
        for v in text_violations(cell["source"], rows):
            fail("%s/%s: %s" % (costume, state, v))
        for special_text in VISIBLE_AT_KEYFRAME & set(texts):
            found, covered = hidden_text_pixels(scenes_all[cell["source"]][0], cell["keyframe"], special_text)
            if not found or covered:
                fail("%s/%s: teks %r di frame kunci f%d tertutup %d piksel (atau tidak ada)" % (costume, state, special_text, cell["keyframe"], covered))
            elif not show_all and gate and cell.get("gate") == gate:
                print("  %s/%s: %r utuh di frame kunci f%d" % (costume, state, special_text, cell["keyframe"]))
        if not show_all and (not gate or cell.get("gate") != gate):
            continue
        print("  %s/%s  (%d frame, %d ms, kunci f%d)  teks: %s" % (
            costume, state, len(rows), sum(r[1] for r in rows), cell["keyframe"], ", ".join(repr(t) for t in texts) or "-"))
        runs = []
        for r in rows:
            key = (r[2], r[3], r[4], "".join(sorted({s for s, _, _ in r[5]})))
            if runs and runs[-1][0] == key:
                runs[-1][1].append(r[0])
                runs[-1][2] += r[1]
            else:
                runs.append([key, [r[0]], r[1]])
        for key, idx, ms_ in runs:
            span = "f%d" % idx[0] if len(idx) == 1 else "f%d-%d" % (idx[0], idx[-1])
            print("    %-7s %5d ms  mata=%-7s alis=%-7s mulut=%-6s%s" % (
                span, ms_, key[0], key[1], key[2], ("  teks=" + key[3]) if key[3] else ""))


# ------------------------------------------------------------------ audit teologi (keputusan pemilik 11c)
THEO_TEXT_ALLOWED = {"."}
CROSS_KEY = "y"  # warna kalung salib Priest; tidak boleh muncul di mana pun selain salib itu
BATIK_KEYS = set("Uu")  # kain batik kondangan
DARK_CAP_KEYS = set("Llq")  # peci atau kopiah hitam
BEARD_KEYS = set("HhmWSgG")  # rambut atau janggut putih dan abu (janggut Greek: H/h)
LEAF_KEYS = set("VvkZ")  # daun zaitun Greek (V/v) dan hijau lain
CHIN_ZONE = {(x, y) for x in range(CX - 5, CX + 5) for y in range(CY + 5, CY + 8)}  # di dalam kepala, di bawah mulut
CROWN_ZONE = {(x, y) for x in range(CX - 13, CX + 14) for y in range(0, CY - 3)}  # di atas alis
CAP_ZONE = {(x, y) for x in range(CX - 10, CX + 11) for y in range(0, CY - 4)}


def theology_frames(scenes_all, names):
    """Render semua frame sambil mencatat setiap panggilan aura: [(nama, i, px, [(kosong_sebelum, mask)])]."""
    import theology
    real = theology.aura
    calls = []

    def spy(cv, level=1, pulse=0, shimmer=0):
        empty = not cv.px
        mask = real(cv, level, pulse, shimmer)
        calls.append((empty, dict(mask)))
        return mask
    patched = _patch_everywhere(real, spy)
    out = []
    try:
        for name in names:
            fn, n, ms = scenes_all[name]
            for i in range(n):
                del calls[:]
                cv = fn(i)
                out.append((name, i, dict(cv.px), list(calls)))
    finally:
        for d, key in patched:
            d[key] = real
    return out


def zone_hits(px, zone, keys):
    return sorted(p for p in zone if px.get(p) in keys)


def check_theology():
    print("\n[VT] Audit teologi 7.2 (keputusan pemilik 11c: pemeriksaan i-vi, wajib lulus)")
    try:
        import theology
    except ModuleNotFoundError:
        print("  belum ada modul teologi")
        return
    scenes_all = export.all_scenes()
    a, b = theology.COSTUMES
    st = {c: sorted(n[len(c) + 1:] for n in scenes_all if n.startswith(c + "-")) for c in (a, b)}
    print("  state %s: %s | %s: %s" % (a, ", ".join(st[a]) or "-", b, ", ".join(st[b]) or "-"))
    if not st[a] and not st[b]:
        print("  belum ada aset teologi")
        return

    # (ii) jumlah state, frame, dan durasi identik
    bad = [] if st[a] == st[b] else ["daftar state berbeda"]
    for s_ in sorted(set(st[a]) & set(st[b])):
        (_, na, ma), (_, nb, mb) = scenes_all["%s-%s" % (a, s_)], scenes_all["%s-%s" % (b, s_)]
        da, db = [int(ma(i)) for i in range(na)], [int(mb(i)) for i in range(nb)]
        if na != nb or da != db:
            bad.append("%s: %d frame %s vs %d frame %s" % (s_, na, da[:4], nb, db[:4]))
        else:
            print("  (ii) %-9s %2d frame, durasi %s ms, sama untuk keduanya" % (s_, na, sorted(set(da))))
    for x in bad:
        fail("teologi (ii): " + x)
    print("  (ii) %s" % ("lulus" if not bad else "GAGAL"))

    names = ["%s-%s" % (c, s_) for c in (a, b) for s_ in st[c]]
    frames = theology_frames(scenes_all, names)
    by = {(name, i): (px, calls) for name, i, px, calls in frames}

    # (i) mask aura identik, digambar paling awal, warna C/n/O, tidak di atas kepala
    bad = []
    for s_ in sorted(set(st[a]) & set(st[b])):
        n = scenes_all["%s-%s" % (a, s_)][1]
        vis = {a: 0, b: 0}
        sizes = []
        for i in range(n):
            ca, cb = by[("%s-%s" % (a, s_), i)][1], by[("%s-%s" % (b, s_), i)][1]
            if len(ca) != 1 or len(cb) != 1:
                bad.append("%s f%d: aura digambar %d/%d kali (harus 1)" % (s_, i, len(ca), len(cb)))
                continue
            (ea, ma), (eb, mb) = ca[0], cb[0]
            if ma != mb:
                bad.append("%s f%d: mask aura berbeda (%d vs %d piksel)" % (s_, i, len(ma), len(mb)))
            if not (ea and eb):
                bad.append("%s f%d: aura tidak digambar paling awal (bukan di belakang badan)" % (s_, i))
            if set(ma.values()) - set(theology.AURA_COLORS):
                bad.append("%s f%d: warna aura di luar C/n/O: %s" % (s_, i, sorted(set(ma.values()) - set("CnO"))))
            if ma and min(y for _, y in ma) < CY:
                bad.append("%s f%d: aura naik di atas pusat kepala (y %d)" % (s_, i, min(y for _, y in ma)))
            sizes.append(len(ma))
            for c in (a, b):
                px, calls = by[("%s-%s" % (c, s_), i)]
                vis[c] += sum(1 for p, col in calls[0][1].items() if px.get(p) == col)
        if sizes:
            print("  (i)  %-9s mask aura %d-%d piksel per frame, identik di %d frame; terlihat rata-rata %s %d, %s %d" % (
                s_, min(sizes), max(sizes), n, a, vis[a] // n, b, vis[b] // n))
    for x in bad:
        fail("teologi (i): " + x)
    print("  (i)  %s" % ("lulus" if not bad else "GAGAL"))

    # (iii) teks hanya "." (dan hanya di thinking)
    bad = []
    for name in names:
        rows = instrumented(*scenes_all[name])
        texts = {s for r in rows for s, _, _ in r[5]}
        state = name.split("-", 2)[-1] if name.startswith("pak-haji") else name.split("-", 1)[1]
        extra = {t for t in texts if set(t) - THEO_TEXT_ALLOWED}
        if extra or (texts and state != "thinking"):
            bad.append("%s: teks %s" % (name, sorted(texts)))
        print("  (iii) %-20s teks mini_text: %s" % (name, ", ".join(repr(t) for t in sorted(texts)) or "tidak ada (titik digambar sebagai piksel)"))
    for x in bad:
        fail("teologi (iii): " + x)
    print("  (iii) %s" % ("lulus" if not bad else "GAGAL"))

    # (iv) warna salib hanya di Priest, sekitar 3x4; buku polos
    bad = []
    boxes = set()
    for (name, i), (px, _) in sorted(by.items()):
        ys = [p for p, c in px.items() if c == CROSS_KEY]
        if name.startswith(a):
            if ys:
                bad.append("%s f%d: %d piksel warna salib" % (name, i, len(ys)))
            continue
        if not ys:
            bad.append("%s f%d: salib tidak terlihat" % (name, i))
            continue
        w = max(x for x, _ in ys) - min(x for x, _ in ys) + 1
        h = max(y for _, y in ys) - min(y for _, y in ys) + 1
        boxes.add((w, h, len(ys)))
        if w > 3 or h > 4 or len(ys) > 6:
            bad.append("%s f%d: piksel warna salib %dx%d (%d piksel), lebih dari 3x4" % (name, i, w, h, len(ys)))
    book = monkey.Canvas()
    theology.plain_book(book, 20, 20)
    book_keys = set(book.px.values())
    if book_keys - set("DCK"):
        bad.append("buku Priest memuat warna selain sampul/halaman/tepi: %s" % sorted(book_keys - set("DCK")))
    print("  (iv) warna salib %r: %s 0 piksel di semua frame; %s kotak %s; buku polos warna %s" % (
        CROSS_KEY, a, b, ", ".join("%dx%d (%d px)" % bx for bx in sorted(boxes)) or "-", "".join(sorted(book_keys))))
    for x in bad:
        fail("teologi (iv): " + x)
    print("  (iv) %s (glyph: hanya lewat mini_text yang diinstrumentasi di iii)" % ("lulus" if not bad else "GAGAL"))

    # (v) tanpa janggut putih panjang dan tanpa mahkota daun; (vi) tanpa kopiah hitam dan tanpa batik
    bad5, bad6 = [], []
    white_cap = []
    for (name, i), (px, _) in sorted(by.items()):
        beard = zone_hits(px, CHIN_ZONE, BEARD_KEYS)
        crown = zone_hits(px, CROWN_ZONE, LEAF_KEYS)
        if beard:
            bad5.append("%s f%d: %d piksel putih/abu di dagu" % (name, i, len(beard)))
        if crown:
            bad5.append("%s f%d: %d piksel hijau daun di atas alis" % (name, i, len(crown)))
        dark = zone_hits(px, CAP_ZONE, DARK_CAP_KEYS)
        batik = [p for p, c in px.items() if c in BATIK_KEYS]
        if dark:
            bad6.append("%s f%d: %d piksel hitam di area kopiah" % (name, i, len(dark)))
        if batik:
            bad6.append("%s f%d: %d piksel warna batik" % (name, i, len(batik)))
        if name.startswith(a):
            white_cap.append(len(zone_hits(px, CAP_ZONE, set("W"))))
    if white_cap and min(white_cap) < 20:
        bad6.append("kopiah putih %s tidak terlihat utuh (min %d piksel W)" % (a, min(white_cap)))
    # kontrol positif: pemeriksaan yang sama pada aset lama yang memang berjanggut, bermahkota, berpeci, berbatik
    ctrl = {}
    for src in ("greek-philosopher-idle", "kondangan"):  # kepala Greek di cx 36 (zona digeser +4)
        if src in scenes_all:
            px = scenes_all[src][0](0).px
            ctrl[src] = (len(zone_hits(px, {(x + 4, y) for x, y in CHIN_ZONE}, BEARD_KEYS)),
                         len(zone_hits(px, {(x + 4, y) for x, y in CROWN_ZONE}, LEAF_KEYS)),
                         len(zone_hits(px, CAP_ZONE, DARK_CAP_KEYS)), sum(1 for c in px.values() if c in BATIK_KEYS))
    print("  (v)  dagu (%d piksel zona) tanpa %s; di atas alis tanpa %s: %s" % (
        len(CHIN_ZONE), "".join(sorted(BEARD_KEYS)), "".join(sorted(LEAF_KEYS)), "lulus" if not bad5 else "GAGAL"))
    print("  (vi) area kopiah tanpa %s, tanpa warna batik %s; kopiah putih %s min %s piksel W: %s" % (
        "".join(sorted(DARK_CAP_KEYS)), "".join(sorted(BATIK_KEYS)), a, min(white_cap) if white_cap else "-",
        "lulus" if not bad6 else "GAGAL"))
    expect = {"greek-philosopher-idle": (0, 1), "kondangan": (2, 3)}  # indeks yang harus > 0 di aset lama itu
    for src, hits in ctrl.items():
        need = [hits[k] for k in expect[src]]
        print("  kontrol positif %-22s janggut %d, daun %d, kopiah hitam %d, batik %d piksel -> %s" % (
            (src,) + hits + ("terdeteksi" if all(need) else "TIDAK terdeteksi",)))
        if not all(need):
            fail("teologi: pemeriksaan tidak mendeteksi kontrol positif %s (pemeriksaan rusak)" % src)
    for x in bad5:
        fail("teologi (v): " + x)
    for x in bad6:
        fail("teologi (vi): " + x)


# ------------------------------------------------------------------ V9
def check_dances(m):
    print("\n[V9] Audit tarian (dance-*: %d frame x %d ms, pose besar di beat f0/f4/f8/f12)" % (DANCE_FRAMES, DANCE_MS))
    found = False
    for costume, state, cell in cells(m):
        if not state.startswith("dance-"):
            continue
        found = True
        tag = "%s/%s" % (costume, state)
        if cell["frames"] != DANCE_FRAMES or any(d != DANCE_MS for d in cell["durations_ms"]):
            fail("%s: bukan %d frame x %d ms" % (tag, DANCE_FRAMES, DANCE_MS))
            continue
        fr = frames_of(cell_path(cell["sheet"]))
        steps = [diff(fr[i], fr[(i + 1) % DANCE_FRAMES]) for i in range(DANCE_FRAMES)]
        beat = [steps[i] for i in (3, 7, 11, 15)]
        other = [steps[i] for i in range(DANCE_FRAMES) if i not in (3, 7, 11, 15)]
        ok = min(beat) > max(other)
        print("  %-24s transisi beat %s, lainnya maks %d  %s" % (tag, beat, max(other), "lulus" if ok else "GAGAL"))
        if not ok:
            fail("%s: perubahan pose di beat (%d) tidak lebih besar dari di luar beat (%d)" % (tag, min(beat), max(other)))
    if not found:
        print("  belum ada aset tarian")


# ------------------------------------------------------------------ V10
def git_sizes(commit, prefixes=("gif/", "sheets/")):
    try:
        out = subprocess.run(["git", "-C", ROOT, "ls-tree", "-r", "-l", commit], capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    total = 0
    for line in out.splitlines():
        meta, path = line.split("\t", 1)
        if path.startswith(prefixes):
            total += int(meta.split()[3])
    return total


def check_sizes(m, gate):
    print("\n[V10] Ukuran")
    originals = [os.path.getsize(cell_path(c["gif"])) for _, _, c in cells(m) if c["origin"] == "asli"]
    originals += [os.path.getsize(cell_path(x["gif"])) for x in m.get("extras", [])]
    limit = max(originals)
    print("  GIF pra-Fase 2 terbesar: %d byte (batas per GIF baru, dihitung setelah optimize)" % limit)
    per_gate = {}
    for costume, state, cell in cells(m):
        if cell["origin"] != "baru":
            continue
        g = os.path.getsize(cell_path(cell["gif"]))
        if g > limit:
            print("  MELEBIHI: %s/%s GIF %d byte > %d (dilaporkan sesuai keputusan pemilik 9)" % (costume, state, g, limit))
        total = sum(os.path.getsize(cell_path(cell[k])) for k in ("gif", "sheet", "sheet4x") if k in cell)
        per_gate.setdefault(cell["gate"], []).append((costume + "/" + state, g, total))
    for gt in [g for g in ("A", "B", "C", "D", "E", "G", "H", "I", "J", "F") if g in per_gate]:
        rows = per_gate[gt]
        print("  gerbang %s: %2d aset, GIF terbesar %6d byte, total file %8d byte" % (
            gt, len(rows), max(r[1] for r in rows), sum(r[2] for r in rows)))
    if gate and gate not in per_gate:
        fail("gerbang %s tidak punya aset di manifest" % gate)
    applicable = sum(len(c.get("applies", {})) for c in m["costumes"])
    filled = sum(1 for _ in cells(m))
    remaining = applicable - filled
    modern = [c for _, _, c in cells(m) if is_modern(c)]
    basis = modern or [c for _, _, c in cells(m) if c["origin"] == "baru"]
    avg_gif = sum(os.path.getsize(cell_path(c["gif"])) for c in basis) / float(len(basis))
    avg_sheet = sum(os.path.getsize(cell_path(c[k])) for c in basis for k in ("sheet", "sheet4x") if k in c) / float(len(basis))

    def dir_total(d):
        return sum(os.path.getsize(os.path.join(ROOT, d, f)) for f in os.listdir(os.path.join(ROOT, d)))
    now_gif, now_sheet = dir_total("gif"), dir_total("sheets")
    base_gif, base_sheet = git_sizes(BUDGET_BASE_COMMIT, ("gif/",)), git_sizes(BUDGET_BASE_COMMIT, ("sheets/",))
    print("  sel berlaku %d, terisi %d, tersisa %d" % (applicable, filled, remaining))
    print("  rata-rata per aset profil baru: GIF %d byte, sheet %d byte (%d aset)" % (avg_gif, avg_sheet, len(basis)))
    if base_gif is None:
        print("  anggaran: tidak terbukti (git ls-tree %s gagal)" % BUDGET_BASE_COMMIT)
        return
    grown_gif, grown_sheet = now_gif - base_gif, now_sheet - base_sheet
    proj_gif, proj_sheet = grown_gif + avg_gif * remaining, grown_sheet + avg_sheet * remaining
    projection = proj_gif + proj_sheet
    print("  %-7s %10s %10s %12s %14s" % ("", "dd78be8", "sekarang", "pertambahan", "proyeksi akhir"))
    print("  %-7s %10d %10d %12d %14d" % ("GIF", base_gif, now_gif, grown_gif, proj_gif))
    print("  %-7s %10d %10d %12d %14d" % ("sheet", base_sheet, now_sheet, grown_sheet, proj_sheet))
    print("  proyeksi pertambahan total: %d byte (%.2f MB); ambang peringatan %.0f MB, batas keras %.0f MB" % (
        projection, projection / 1048576.0, WARN_BYTES / 1048576.0, BUDGET_BYTES / 1048576.0))
    print("  opsi D (GIF aset baru dibuat saat rilis, tidak disimpan): hemat %d byte sekarang, %d byte di akhir" % (
        sum(os.path.getsize(cell_path(c["gif"])) for c in modern), sum(os.path.getsize(cell_path(c["gif"])) for c in modern) + avg_gif * remaining))
    if projection > WARN_BYTES:
        fail("proyeksi ukuran %d byte melewati ambang peringatan %d byte (STOP-DARURAT)" % (projection, WARN_BYTES))


def main():
    gate = sys.argv[sys.argv.index("--gate") + 1] if "--gate" in sys.argv else None
    show_all = "--all" in sys.argv
    if "--theology-only" in sys.argv:  # pemeriksaan i-vi saja (dipakai sebelum state teologi lain dibuat)
        check_theology()
        print("\nHASIL: %s" % ("LULUS" if not FAILS else "%d GAGAL" % len(FAILS)))
        sys.exit(1 if FAILS else 0)
    m = load_manifest()
    check_hashes()
    check_manifest_and_palette(m)
    check_seams(m)
    check_silhouettes(m)
    check_colors(m)
    if "--palette-study" in sys.argv:
        palette_study(m)
    check_props()
    check_texts_and_beats(m, gate, show_all)
    check_theology()
    check_dances(m)
    check_sizes(m, gate)
    print("\nHASIL: %s" % ("LULUS" if not FAILS else "%d GAGAL" % len(FAILS)))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
