#!/usr/bin/env python3
"""Validasi Gobyet Character Pack (Fase 2, bagian 7). Pustaka standar + Pillow (sudah dipakai export).

    python3 src/validate_pack.py [--gate B]

Pemeriksaan:
 1. Hash: aset pra-Fase 2 (pack/sha256-asli.txt) dan aset gerbang yang sudah disetujui
    (pack/sha256-disetujui.txt) identik byte.
 2. Manifest: setiap sel merujuk file yang ada; sel baru punya origin, gate, nama <kostum>-<state>.
 3. Palet: piksel buram sheet 1x/4x dan GIF hanya dari PAL; alfa sheet hanya 0/255; kanvas 64x48;
    sheet 4x sama persis dengan sheet 1x yang diperbesar nearest-neighbour.
 4. Loop seam: selisih frame terakhir->pertama <= selisih maksimum antar-frame berurutan
    (wajib untuk sel baru, dilaporkan untuk sel asli).
 5. Siluet: IoU mask buram frame 0 sel idle antar-kostum; > 0,90 ditandai "terlalu mirip".
 6. Ukuran: GIF baru <= GIF pra-Fase 2 terbesar; total pertambahan per gerbang.
 7. Teks gelembung aset baru hanya glyph mini_text yang ada, maksimal 3 karakter.
 8. Prop: kotak pembatas tiap prop digambar sendirian (target heuristik >= 6x6).
 9. Beat per rentang frame untuk aset baru (ekspresi dan teks yang benar-benar digambar).
Keluar dengan kode 1 bila ada pemeriksaan wajib yang gagal.
"""
import hashlib
import json
import os
import sys

from PIL import Image, ImageSequence

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import monkey  # noqa: E402
import roles  # noqa: E402

W, H = monkey.W, monkey.H
PAL = {tuple(v) for v in monkey.PAL.values()}
FAILS = []


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
    for name in ("sha256-asli.txt", "sha256-disetujui.txt"):
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


def check_seams(m):
    print("\n[4] Loop seam (piksel berbeda; seam = frame terakhir -> frame pertama)")
    print("  %-26s %-5s %8s %8s  %s" % ("sel", "asal", "maks", "seam", "hasil"))
    for costume, state, cell in cells(m):
        fr = frames_of(cell_path(cell["sheet"]))
        steps = [diff(fr[i], fr[i + 1]) for i in range(len(fr) - 1)]
        seam = diff(fr[-1], fr[0])
        ok = seam <= max(steps)
        verdict = "lulus" if ok else ("GAGAL" if cell["origin"] == "baru" else "melebihi (aset asli, hanya dilaporkan)")
        print("  %-26s %-5s %8d %8d  %s" % (costume + "/" + state, cell["origin"], max(steps), seam, verdict))
        if not ok and cell["origin"] == "baru":
            fail("%s/%s: loop seam %d > %d" % (costume, state, seam, max(steps)))


# ------------------------------------------------------------------ 5
def check_silhouettes(m):
    print("\n[5] Siluet: IoU mask buram frame 0 sel idle (> 0,90 = kandidat terlalu mirip)")
    masks = {}
    for costume, state, cell in cells(m):
        if state == "idle":
            f0 = frames_of(cell_path(cell["sheet"]))[0]
            masks[costume] = {i for i, (_, _, _, a) in enumerate(pixels(f0)) if a}
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


# ------------------------------------------------------------------ 7 + 9
def instrumented(name):
    """Jalankan adegan aset baru sambil mencatat ekspresi kepala dan teks gelembung per frame."""
    fn, n, ms = roles.SCENES[name]
    real_head, real_text = roles.head, roles.mini_text
    log = []

    def head(cv, cx, cy, eyes="look", brows="flat", mouth="frown", face="F", tilt=0):
        log.append(("head", eyes, brows, mouth))
        return real_head(cv, cx, cy, eyes=eyes, brows=brows, mouth=mouth, face=face, tilt=tilt)

    def mini_text(cv, s, x, y, c):
        log.append(("text", s))
        return real_text(cv, s, x, y, c)

    roles.head, roles.mini_text = head, mini_text
    rows = []
    try:
        for i in range(n):
            del log[:]
            fn(i)
            h = [e for e in log if e[0] == "head"][-1]
            texts = [e[1] for e in log if e[0] == "text"]
            rows.append((i, int(ms(i)), h[1], h[2], h[3], texts))
    finally:
        roles.head, roles.mini_text = real_head, real_text
    return rows


def check_texts_and_beats(m, gate):
    print("\n[7] Teks gelembung aset baru dan [9] beat per rentang frame")
    for costume, state, cell in cells(m):
        if cell["origin"] != "baru" or cell["source"] not in roles.SCENES:
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
    "champion: laurel emas": lambda cv: roles.gold_laurel(cv, 32, 20),
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
    print("\nHASIL: %s" % ("LULUS" if not FAILS else "%d GAGAL" % len(FAILS)))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
