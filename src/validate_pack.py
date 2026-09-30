#!/usr/bin/env python3
"""Validasi Gobyet Character Pack (Fase 2, bagian 7). Pustaka standar + Pillow (sudah dipakai export).

    python3 src/validate_pack.py [--gate B]

Pemeriksaan:
 1. Hash: aset pra-Fase 2 (pack/sha256-asli.txt) dan aset gerbang yang sudah disetujui
    (pack/sha256-disetujui.txt) identik byte.
 2. Manifest: setiap sel merujuk file yang ada; sel baru punya origin, gate, nama <kostum>-<state>.
 3. Palet: piksel buram sheet 1x/4x dan GIF hanya dari PAL; alfa sheet hanya 0/255; kanvas 64x48;
    sheet 4x sama persis dengan sheet 1x yang diperbesar nearest-neighbour.
 4. Loop seam: selisih frame terakhir->pertama <= 1,25 x selisih maksimum antar-frame berurutan
    di aset itu sendiri. Aset terkunci hash di atas ambang dilaporkan DIKETAHUI; aset lain GAGAL.
 5. Siluet: IoU mask buram frame kunci sel idle antar-kostum; > 0,90 ditandai "terlalu mirip".
 6. Ukuran: GIF baru <= GIF pra-Fase 2 terbesar; total pertambahan per gerbang; proyeksi sel tersisa.
 7. Teks gelembung aset baru hanya glyph mini_text yang ada, maksimal 3 karakter.
 8. Prop: kotak pembatas tiap prop digambar sendirian (target heuristik >= 6x6).
 9. Beat per rentang frame untuk aset baru (ekspresi dan teks yang benar-benar digambar).
10. Warna dominan kostum (di luar warna bulu/kulit/garis tepi yang sama di semua kostum) dan jarak
    warnanya antar-kostum (CIE76 Delta E di ruang Lab); pasangan terdekat dilaporkan.
Keluar dengan kode 1 bila ada pemeriksaan wajib yang gagal.
"""
import hashlib
import json
import os
import sys
from collections import Counter

from PIL import Image, ImageSequence

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import domains  # noqa: E402
import monkey  # noqa: E402
import roles  # noqa: E402

SCENE_MODULES = (roles, domains)  # modul aset baru Fase 2

W, H = monkey.W, monkey.H
PAL = {tuple(v) for v in monkey.PAL.values()}
FAILS = []
LOCK_FILES = ("sha256-asli.txt", "sha256-disetujui.txt")


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


# ------------------------------------------------------------------ 1
def check_hashes():
    print("\n[1] Hash aset yang dikunci")
    for name in LOCK_FILES:
        path = os.path.join(ROOT, "pack", name)
        if not os.path.exists(path):
            print("  %s: tidak ada (dilewati)" % name)
            continue
        ok = bad = 0
        for line in open(path, encoding="utf-8"):
            if not line.strip():
                continue
            digest, f = line.split(None, 1)
            f = f.strip()
            full = os.path.join(ROOT, f)
            if not os.path.exists(full):
                fail("%s: %s hilang" % (name, f))
                bad += 1
            elif hashlib.sha256(open(full, "rb").read()).hexdigest() != digest:
                fail("%s: %s BERUBAH" % (name, f))
                bad += 1
            else:
                ok += 1
        print("  %s: %d identik, %d berubah/hilang" % (name, ok, bad))


# ------------------------------------------------------------------ 2 + 3
def check_manifest_and_palette(m):
    print("\n[2] Manifest dan [3] palet/kanvas")
    n = 0
    for costume, state, cell in cells(m):
        n += 1
        tag = "%s/%s" % (costume, state)
        if cell.get("origin") not in ("asli", "baru"):
            fail("%s: origin tidak valid" % tag)
        if cell.get("origin") == "baru":
            if not cell.get("gate"):
                fail("%s: sel baru tanpa gate" % tag)
            if cell.get("source") != "%s-%s" % (costume, state):
                fail("%s: nama file bukan <kostum>-<state> (%s)" % (tag, cell.get("source")))
        paths = {k: cell_path(cell[k]) for k in ("sheet", "sheet4x", "gif")}
        missing = [k for k, p in paths.items() if not os.path.exists(p)]
        if missing:
            fail("%s: file hilang %s" % (tag, missing))
            continue
        one = Image.open(paths["sheet"]).convert("RGBA")
        four = Image.open(paths["sheet4x"]).convert("RGBA")
        if one.size != (W * cell["frames"], H):
            fail("%s: ukuran sheet 1x %s" % (tag, one.size))
        if four.size != (W * 4 * cell["frames"], H * 4):
            fail("%s: ukuran sheet 4x %s" % (tag, four.size))
        if four.tobytes() != one.resize(four.size, Image.NEAREST).tobytes():
            fail("%s: sheet 4x bukan pembesaran nearest dari sheet 1x" % tag)
        alphas = {a for (_, _, _, a) in pixels(one)}
        if not alphas <= {0, 255}:
            fail("%s: alfa parsial %s" % (tag, sorted(alphas - {0, 255})[:5]))
        colors = {(r, g, b) for (r, g, b, a) in pixels(one) if a}
        if not colors <= PAL:
            fail("%s: warna di luar PAL %s" % (tag, sorted(colors - PAL)[:5]))
        gif = Image.open(paths["gif"])
        gframes, total = 0, 0
        for fr in ImageSequence.Iterator(gif):
            gframes += 1
            total += fr.info.get("duration", 0)
            rgba = fr.convert("RGBA")
            if rgba.size != (W * 8, H * 8):
                fail("%s: ukuran GIF %s" % (tag, rgba.size))
                break
            gc = {(r, g, b) for (r, g, b, a) in pixels(rgba) if a}
            if not gc <= PAL:
                fail("%s: warna GIF di luar PAL %s" % (tag, sorted(gc - PAL)[:5]))
                break
        if gframes > cell["frames"] or total != sum(cell["durations_ms"]):
            fail("%s: GIF %d frame/%d ms vs manifest %d frame/%d ms" % (tag, gframes, total, cell["frames"], sum(cell["durations_ms"])))
    print("  %d sel diperiksa (sheet 1x, sheet 4x, GIF), %d gagal" % (n, len(FAILS)))


# ------------------------------------------------------------------ 4
def diff(a, b):
    return sum(1 for p, q in zip(pixels(a), pixels(b)) if p != q)


SEAM_FACTOR = 1.25


def locked_files():
    """File yang dikunci hash (aset asli + aset gerbang yang disetujui), relatif terhadap akar repo."""
    out = set()
    for name in LOCK_FILES:
        path = os.path.join(ROOT, "pack", name)
        if os.path.exists(path):
            out |= {line.split(None, 1)[1].strip() for line in open(path, encoding="utf-8") if line.strip()}
    return out


def check_seams(m):
    print("\n[4] Loop seam (piksel berbeda; seam = frame terakhir -> frame pertama)")
    print("  ambang = %.2f x selisih maksimum antar-frame berurutan di aset itu sendiri" % SEAM_FACTOR)
    print("  %-26s %-8s %6s %7s %6s  %s" % ("sel", "status", "maks", "ambang", "seam", "hasil"))
    locked = locked_files()
    for costume, state, cell in cells(m):
        fr = frames_of(cell_path(cell["sheet"]))
        steps = [diff(fr[i], fr[i + 1]) for i in range(len(fr) - 1)]
        seam = diff(fr[-1], fr[0])
        limit = SEAM_FACTOR * max(steps)
        is_locked = rel(cell_path(cell["sheet"])) in locked
        ok = seam <= limit
        verdict = "lulus" if ok else ("DIKETAHUI (terkunci, tidak diubah)" if is_locked else "GAGAL")
        print("  %-26s %-8s %6d %7.1f %6d  %s" % (costume + "/" + state, "terkunci" if is_locked else "baru",
                                                max(steps), limit, seam, verdict))
        if not ok and not is_locked:
            fail("%s/%s: loop seam %d > %.1f" % (costume, state, seam, limit))


# ------------------------------------------------------------------ 5
def check_silhouettes(m):
    print("\n[5] Siluet: IoU mask buram frame kunci sel idle (> 0,90 = kandidat terlalu mirip)")
    print("  catatan: semua kostum memakai kepala dan badan duduk yang sama, jadi IoU dasar antar-kostum sudah tinggi")
    masks = {}
    for costume, state, cell in cells(m):
        if state == "idle":
            fk = frames_of(cell_path(cell["sheet"]))[cell["keyframe"]]
            masks[costume] = {i for i, (_, _, _, a) in enumerate(pixels(fk)) if a}
    names = list(masks)
    print("  %-10s" % "" + "".join("%9s" % n[:8] for n in names))
    flagged = []
    for a in names:
        row = []
        for b in names:
            iou = len(masks[a] & masks[b]) / float(len(masks[a] | masks[b]))
            row.append("%9.2f" % iou)
            if a < b and iou > 0.90:
                flagged.append((a, b, iou))
        print("  %-10s" % a[:10] + "".join(row))
    print("  pasangan > 0,90: %s" % (", ".join("%s-%s %.2f" % f for f in flagged) if flagged else "tidak ada"))


# ------------------------------------------------------------------ 6
def check_sizes(m, gate):
    print("\n[6] Ukuran")
    originals = [os.path.getsize(cell_path(c["gif"])) for _, _, c in cells(m) if c["origin"] == "asli"]
    originals += [os.path.getsize(cell_path(x["gif"])) for x in m.get("extras", [])]
    limit = max(originals)
    print("  GIF pra-Fase 2 terbesar: %d byte" % limit)
    per_gate = {}
    for costume, state, cell in cells(m):
        if cell["origin"] != "baru":
            continue
        g = os.path.getsize(cell_path(cell["gif"]))
        if g > limit:
            fail("%s/%s: GIF %d byte > %d" % (costume, state, g, limit))
        total = sum(os.path.getsize(cell_path(cell[k])) for k in ("gif", "sheet", "sheet4x"))
        per_gate.setdefault(cell["gate"], []).append((costume + "/" + state, g, total))
    for gt in sorted(per_gate):
        rows = per_gate[gt]
        print("  gerbang %s: %d aset, GIF terbesar %d byte, total file (gif+sheet+4x) %d byte" % (
            gt, len(rows), max(r[1] for r in rows), sum(r[2] for r in rows)))
    if gate and gate not in per_gate:
        fail("gerbang %s tidak punya aset di manifest" % gate)
    rows = [r for g in per_gate.values() for r in g]
    if rows:
        applicable = sum(1 for c in m["costumes"] for st in m["states"] if not st.get("costumes") or c["id"] in st["costumes"])
        filled = sum(1 for _ in cells(m))
        avg = sum(r[2] for r in rows) / float(len(rows))
        four = [os.path.getsize(cell_path(c["sheet4x"])) for _, _, c in cells(m) if c["origin"] == "baru"]
        print("  rata-rata per aset baru (gif+sheet+4x): %d byte (GIF %d, sheet4x %d)" % (
            avg, sum(r[1] for r in rows) / len(rows), sum(four) / len(four)))
        print("  sel berlaku %d, terisi %d, tersisa %d; proyeksi tambahan bila semua diisi: %d byte" % (
            applicable, filled, applicable - filled, avg * (applicable - filled)))


# ------------------------------------------------------------------ 7 + 9
def scene(name):
    for mod in SCENE_MODULES:
        if name in mod.SCENES:
            return mod.SCENES[name]
    return None


def instrumented(name):
    """Jalankan adegan aset baru sambil mencatat ekspresi kepala dan teks gelembung per frame."""
    fn, n, ms = scene(name)
    real_head, real_text = monkey.head, monkey.mini_text
    log = []

    def head(cv, cx, cy, eyes="look", brows="flat", mouth="frown", face="F", tilt=0):
        log.append(("head", eyes, brows, mouth))
        return real_head(cv, cx, cy, eyes=eyes, brows=brows, mouth=mouth, face=face, tilt=tilt)

    def mini_text(cv, s, x, y, c):
        log.append(("text", s))
        return real_text(cv, s, x, y, c)

    for mod in SCENE_MODULES:
        mod.head, mod.mini_text = head, mini_text
    rows = []
    try:
        for i in range(n):
            del log[:]
            fn(i)
            h = [e for e in log if e[0] == "head"][-1]
            texts = [e[1] for e in log if e[0] == "text"]
            rows.append((i, int(ms(i)), h[1], h[2], h[3], texts))
    finally:
        for mod in SCENE_MODULES:
            mod.head, mod.mini_text = real_head, real_text
    return rows


def check_texts_and_beats(m, gate):
    print("\n[7] Teks gelembung aset baru dan [9] beat per rentang frame")
    for costume, state, cell in cells(m):
        if cell["origin"] != "baru" or scene(cell["source"]) is None:
            continue
        rows = instrumented(cell["source"])
        for _, _, _, _, _, texts in rows:
            for s in texts:
                if len(s) > 3 or any(ch not in monkey.MINI for ch in s):
                    fail("%s/%s: teks %r melanggar aturan glyph" % (costume, state, s))
        if gate and cell.get("gate") != gate:
            continue
        total = sum(r[1] for r in rows)
        print("  %s/%s  (%d frame, %d ms)" % (costume, state, len(rows), total))
        runs = []
        for r in rows:
            key = (r[2], r[3], r[4], "".join(r[5]))
            if runs and runs[-1][0] == key:
                runs[-1][1].append(r[0])
                runs[-1][2] += r[1]
            else:
                runs.append([key, [r[0]], r[1]])
        for key, idx, ms_ in runs:
            span = "f%d" % idx[0] if len(idx) == 1 else "f%d-%d" % (idx[0], idx[-1])
            print("    %-7s %5d ms  mata=%-7s alis=%-7s mulut=%-6s%s" % (
                span, ms_, key[0], key[1], key[2], ("  teks=" + key[3]) if key[3] else ""))


# ------------------------------------------------------------------ 8
PROPS = {
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


def check_props():
    print("\n[8] Ukuran prop (kotak pembatas, digambar sendirian; target heuristik >= 6x6)")
    for name, draw in PROPS.items():
        cv = monkey.Canvas()
        draw(cv)
        xs = [x for x, _ in cv.px]
        ys = [y for _, y in cv.px]
        w, h = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
        print("  %-24s %2dx%-2d  %s" % (name, w, h, "ok" if min(w, h) >= 6 else "di bawah 6x6"))


# ------------------------------------------------------------------ 10
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


def check_colors(m):
    print("\n[10] Warna dominan kostum dan jarak warna (CIE76 Delta E; < 10 mirip, < 25 dekat)")
    print("  metode: frame kunci sel idle (atau sel pertama bila belum ada idle); warna bulu/kulit/garis tepi")
    print("  (%s) tidak dihitung, piksel mata dikurangkan. Normal tidak berkostum: warnanya bulu B." % "".join(sorted(BODY_KEYS)))
    rev = {tuple(v): k for k, v in monkey.PAL.items()}
    order = [st["id"] for st in m["states"]]
    dom = {}
    for c in m["costumes"]:
        row = m["cells"].get(c["id"], {})
        if not row:
            print("  %-18s belum ada aset (dilewati)" % c["id"])
            continue
        state = "idle" if "idle" in row else sorted(row, key=order.index)[0]
        cell = row[state]
        fk = frames_of(cell_path(cell["sheet"]))[cell["keyframe"]]
        counts = Counter(rev[(r, g, b)] for (r, g, b, a) in pixels(fk) if a)
        if c["id"] == "normal":
            ranked = [("B", counts["B"])]
        else:
            for k, n in EYE_PIXELS.items():
                counts[k] = max(0, counts[k] - n)
            ranked = [(k, n) for k, n in counts.most_common() if k not in BODY_KEYS and n]
        total = sum(n for k, n in counts.items() if c["id"] == "normal" or k not in BODY_KEYS)
        dom[c["id"]] = ranked[0][0]
        print("  %-18s %-9s dominan %s %-15s %3d%%   kedua %s" % (
            c["id"], "(" + state + ")", ranked[0][0], str(monkey.PAL[ranked[0][0]]), 100 * ranked[0][1] // max(total, 1),
            ("%s %s" % (ranked[1][0], monkey.PAL[ranked[1][0]])) if len(ranked) > 1 else "-"))
    names = list(dom)
    pairs = sorted(((delta_e(monkey.PAL[dom[a]], monkey.PAL[dom[b]]), a, b) for i, a in enumerate(names) for b in names[i + 1:]))
    print("  %-10s" % "" + "".join("%7s" % n[:6] for n in names))
    for a in names:
        print("  %-10s" % a[:10] + "".join("%7.0f" % delta_e(monkey.PAL[dom[a]], monkey.PAL[dom[b]]) for b in names))
    print("  pasangan terdekat:")
    for d, a, b in pairs[:6]:
        print("    %-18s %-18s %s vs %s  Delta E %.1f" % (a, b, dom[a], dom[b], d))


def main():
    gate = None
    if "--gate" in sys.argv:
        gate = sys.argv[sys.argv.index("--gate") + 1]
    m = load_manifest()
    check_hashes()
    check_manifest_and_palette(m)
    check_seams(m)
    check_silhouettes(m)
    check_sizes(m, gate)
    check_texts_and_beats(m, gate)
    check_props()
    check_colors(m)
    print("\nHASIL: %s" % ("LULUS" if not FAILS else "%d GAGAL" % len(FAILS)))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
