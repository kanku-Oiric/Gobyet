"""Prop karakter domain dan peran v2: buku, gulungan, papan, alat ukur, laptop, piala, papan GBLK.

Item tangan didaftarkan ke items2.ITEMS (fn(cv, grip, ang, p)). Papan dan meja adalah prop panggung yang
digambar di posisi kanvas tetap lewat fungsi biasa.
"""
import math

import rig2 as R
import items2 as I
from rig2 import solid, ellipse, rect, chain, inner, edge, poly, Frame2, mini_text

# font 3x5 untuk rumus dan angka di papan
F3 = {
    "0": ["111", "101", "101", "101", "111"], "1": ["010", "110", "010", "010", "111"], "2": ["111", "001", "111", "100", "111"],
    "3": ["111", "001", "011", "001", "111"], "4": ["101", "101", "111", "001", "001"], "5": ["111", "100", "111", "001", "111"],
    "6": ["111", "100", "111", "101", "111"], "7": ["111", "001", "010", "010", "010"], "8": ["111", "101", "111", "101", "111"],
    "9": ["111", "101", "111", "001", "111"], "+": ["000", "010", "111", "010", "000"], "-": ["000", "000", "111", "000", "000"],
    "=": ["000", "111", "000", "111", "000"], "x": ["000", "101", "010", "101", "000"], "y": ["000", "101", "010", "010", "010"],
    "a": ["000", "011", "101", "101", "011"], "b": ["100", "110", "101", "101", "110"], "c": ["000", "011", "100", "100", "011"],
    "p": ["000", "111", "101", "101", "101"],  # pi
    "s": ["111", "100", "010", "100", "111"],  # sigma
    "r": ["001", "001", "001", "101", "010"],  # akar
    "i": ["011", "010", "010", "010", "110"],  # integral
    "^": ["010", "101", "000", "000", "000"], "?": ["111", "001", "011", "000", "010"], "!": ["010", "010", "010", "000", "010"],
    "%": ["101", "001", "010", "100", "101"], "$": ["011", "110", "010", "011", "110"], ".": ["000", "000", "000", "000", "010"],
    "X": ["101", "101", "010", "101", "101"], "/": ["001", "001", "010", "100", "100"], "|": ["010", "010", "010", "010", "010"],
    "O": ["111", "101", "101", "101", "111"], "K": ["101", "110", "100", "110", "101"], " ": ["000", "000", "000", "000", "000"],
}


def text3(cv, s, x, y, c):
    for i, ch in enumerate(s):
        for ry, row in enumerate(F3[ch]):
            for rx, v in enumerate(row):
                if v == "1":
                    cv.put(x + i * 4 + rx, y + ry, c)


def sup2(cv, x, y, c):
    cv.fill({(x, y), (x + 1, y), (x + 1, y + 1), (x, y + 2), (x, y + 3), (x + 1, y + 3)}, c)


# ------------------------------------------------------------------ item tangan
def book_open(cv, grip, ang, p):
    """Buku terbuka 14x9 dipegang di depan dada; p['page'] membalik halaman."""
    gx, gy = grip
    x0, y0 = int(round(gx)) - 7, int(round(gy)) - 7
    cover = p.get("cover", ("cr1", "cr2"))
    m = rect(x0 - 1, y0 + 1, 16, 8)
    solid(cv, m, cover[0], cover[1], shade_off=(1, 1))
    for s, xs in ((0, x0), (1, x0 + 7)):
        pg = rect(xs, y0, 7, 8)
        solid(cv, pg, "W", "cm2", shade_off=(1, 1))
        for k in range(3):
            cv.fill({(xx, y0 + 2 + k * 2) for xx in range(xs + 1, xs + 6)}, "s")
    cv.fill({(x0 + 7, y) for y in range(y0, y0 + 8)}, "K")
    if p.get("page"):
        flip = rect(x0 + 7, y0 - 2, 5, 7)
        solid(cv, flip, "W", None)


def book_closed(cv, grip, ang, p):
    gx, gy = grip
    cover = p.get("cover", ("cr1", "cr2"))
    x0, y0 = int(round(gx)) - 5, int(round(gy)) - 7
    m = rect(x0, y0, 10, 12)
    solid(cv, m, cover[0], cover[1], shade_off=(1, 1))
    cv.fill({(x0 + 9, y) for y in range(y0 + 1, y0 + 11)}, "W")
    if p.get("sym") == "law":
        cv.fill({(x0 + 4, y0 + 3), (x0 + 5, y0 + 3), (x0 + 4, y0 + 4), (x0 + 5, y0 + 5), (x0 + 4, y0 + 6), (x0 + 5, y0 + 6),
                 (x0 + 4, y0 + 7), (x0 + 5, y0 + 8), (x0 + 4, y0 + 8)}, "go1")
    else:
        cv.fill(rect(x0 + 2, y0 + 3, 5, 1) | rect(x0 + 2, y0 + 5, 5, 1), "go1")


def book_stack(cv, grip, ang, p):
    gx, gy = grip
    cols = [("cr1", "cr2"), ("3", "4"), ("V", "v"), ("go1", "go2")]
    for k, c in enumerate(cols):
        x0, y0 = int(round(gx)) - 6 + (k % 2), int(round(gy)) - 4 - k * 4
        solid(cv, rect(x0, y0, 12, 4), c[0], c[1], shade_off=(1, 1))
        cv.fill({(x0 + 11, y0 + 1), (x0 + 11, y0 + 2)}, "W")


def scroll_open(cv, grip, ang, p):
    """Gulungan terbuka (Filsuf): dua gulungan kayu, perkamen bertulis."""
    gx, gy = grip
    w = p.get("scroll_w", 12)
    x0, y0 = int(round(gx)) - w // 2, int(round(gy)) - 10
    solid(cv, rect(x0, y0, w, 13), "cm1", "cm2", shade_off=(1, 1))
    for k in range(4):
        cv.fill({(xx, y0 + 3 + k * 2) for xx in range(x0 + 2, x0 + w - 2 - (k % 2) * 2)}, "le1")
    for yy in (y0 - 1, y0 + 13):
        solid(cv, rect(x0 - 1, yy, w + 2, 2), "wo1", "wo2", shade_off=(1, 1))


def scroll_rolled(cv, grip, ang, p):
    f = Frame2(grip, ang)
    solid(cv, f.rect(-6, 6, -1.8, 1.8), "cm1", "cm2", shade_off=(1, 1))
    cv.fill(f.rect(-1, 1, -1.8, 1.8), "cr1")


def timeline(cv, grip, ang, p):
    """Gulungan lini masa panjang (Sejarawan): perkamen 30x9 dengan titik peristiwa."""
    gx, gy = grip
    x0, y0 = int(round(gx)) - 2, int(round(gy)) - 6
    w = 26
    solid(cv, rect(x0, y0, w, 9), "cm1", "cm2", shade_off=(1, 1))
    cv.fill({(x, y0 + 4) for x in range(x0 + 2, x0 + w - 2)}, "le2")
    for k, c in enumerate(("R", "3", "V", "go2", "R")):
        x = x0 + 3 + k * 5
        cv.fill({(x, y0 + 3), (x, y0 + 5), (x - 1, y0 + 4), (x + 1, y0 + 4)}, c)
    for xx in (x0 - 1, x0 + w):
        solid(cv, rect(xx - 1, y0 - 1, 2, 11), "wo1", "wo2", shade_off=(1, 1))


def clipboard(cv, grip, ang, p):
    gx, gy = grip
    x0, y0 = int(round(gx)) - 5, int(round(gy)) - 11
    solid(cv, rect(x0, y0, 10, 13), "wo1", "wo2", shade_off=(1, 1))
    solid(cv, rect(x0 + 1, y0 + 2, 8, 10), "W", None, outline=None)
    for k in range(4):
        cv.fill({(xx, y0 + 4 + k * 2) for xx in range(x0 + 2, x0 + 8 - (k % 2) * 2)}, p.get("ink", "s"))
    solid(cv, rect(x0 + 3, y0 - 1, 4, 2), "st2", None)
    if p.get("check"):
        cv.fill({(x0 + 6, y0 + 9), (x0 + 7, y0 + 10), (x0 + 8, y0 + 8), (x0 + 9, y0 + 7)}, "V")


def notebook(cv, grip, ang, p):
    gx, gy = grip
    x0, y0 = int(round(gx)) - 4, int(round(gy)) - 9
    solid(cv, rect(x0, y0, 8, 10), p.get("nb", "tl1"), "tl2", shade_off=(1, 1))
    cv.fill({(x0 + 1, y) for y in range(y0 + 1, y0 + 9, 2)}, "W")
    solid(cv, rect(x0 + 3, y0 + 2, 4, 6), "W", None, outline=None)


def pen(cv, grip, ang, p):
    f = Frame2(grip, ang)
    cv.fill(f.line([(-1, 0), (6, 0)], 0.6), p.get("pen_c", "3"))
    cv.put(*[int(v) for v in f.world(6.8, 0)], c="K")


def quill(cv, grip, ang, p):
    f = Frame2(grip, ang)
    cv.fill(f.line([(0, 0), (9, 0)], 0.5), "K")
    solid(cv, f.poly([(3, -0.5), (9, -2.6), (11, -0.5), (9, 0.6)]), "W", None)


def chalk(cv, grip, ang, p):
    gx, gy = grip
    cv.fill({(int(gx) + 1, int(gy) - 2), (int(gx) + 2, int(gy) - 3)}, "W")


def magnifier(cv, grip, ang, p):
    """Kaca pembesar besar: gagang + bingkai emas + lensa."""
    f = Frame2(grip, ang)
    solid(cv, f.line([(-2, 0), (5, 0)], 1.1), "wo2", None)
    c = f.world(10, 0)
    ring = ellipse(c[0], c[1], 5.0, 5.0)
    solid(cv, ring, "go1", "go2", shade_off=(1, 1))
    lens = ellipse(c[0], c[1], 3.4, 3.4)
    cv.fill(lens, "I")
    cv.fill({(int(c[0]) - 1, int(c[1]) - 2), (int(c[0]) - 2, int(c[1]) - 1)}, "W")


def flask(cv, grip, ang, p):
    """Labu Erlenmeyer berisi cairan hijau, gelembung naik (p['bubble'])."""
    gx, gy = grip
    x, y = int(round(gx)), int(round(gy))
    m = poly([(x - 1.5, y - 10), (x + 1.5, y - 10), (x + 1.5, y - 6), (x + 5, y + 1), (x - 5, y + 1), (x - 1.5, y - 6)])
    solid(cv, m, "I", None)
    liq = {(xx, yy) for (xx, yy) in inner(m) if yy >= y - 3}
    cv.fill(liq, p.get("liquid", "Z"))
    b = p.get("bubble", 0)
    for k in range(3):
        yy = y - 6 - ((b + k * 3) % 8)
        cv.put(x + (k - 1), yy, "glw")
    cv.fill({(x - 2, y - 11), (x + 1, y - 11), (x - 1, y - 11), (x, y - 11)}, "K")


def gavel(cv, grip, ang, p):
    f = Frame2(grip, ang)
    solid(cv, f.line([(-2, 0), (7, 0)], 0.9), "wo1", None)
    solid(cv, f.rect(7, 10.5, -3.5, 3.5), "wo2", "le2", shade_off=(1, 1))


def papers(cv, grip, ang, p):
    gx, gy = grip
    x0, y0 = int(round(gx)) - 5, int(round(gy)) - 9
    solid(cv, rect(x0 + 2, y0 - 2, 9, 11), "cm2", None)
    solid(cv, rect(x0, y0, 9, 11), "W", "smk", shade_off=(1, 1))
    for k in range(4):
        cv.fill({(xx, y0 + 2 + k * 2) for xx in range(x0 + 2, x0 + 7)}, "s")


def diploma(cv, grip, ang, p):
    f = Frame2(grip, ang)
    solid(cv, f.rect(-7, 7, -1.9, 1.9), "W", "cm2", shade_off=(1, 1))
    cv.fill(f.rect(-1.2, 1.2, -1.9, 1.9), "cr1")


def calculator(cv, grip, ang, p):
    gx, gy = grip
    x0, y0 = int(round(gx)) - 4, int(round(gy)) - 10
    solid(cv, rect(x0, y0, 9, 12), "l", "L", shade_off=(1, 1))
    cv.fill(rect(x0 + 1, y0 + 1, 7, 3), "glw" if p.get("calc_on", True) else "k")
    for k in range(9):
        cv.put(x0 + 2 + (k % 3) * 2, y0 + 6 + (k // 3) * 2, "W" if k != p.get("key", -1) else "R")


def ledger(cv, grip, ang, p):
    gx, gy = grip
    x0, y0 = int(round(gx)) - 6, int(round(gy)) - 8
    solid(cv, rect(x0, y0, 12, 10), "V", "v", shade_off=(1, 1))
    solid(cv, rect(x0 + 1, y0 + 1, 10, 8), "W", None, outline=None)
    for k in range(3):
        cv.fill({(xx, y0 + 3 + k * 2) for xx in range(x0 + 2, x0 + 10)}, "s")
    cv.fill({(x0 + 7, y) for y in range(y0 + 1, y0 + 9)}, "R")


def laptop_side(cv, grip, ang, p):
    """Laptop terbuka dipegang di depan badan, layar menghadap Gobyet; punggung layar terlihat penonton,
    cahaya layar memantul di tepi (glow: 'Z' hijau, 'R' merah error)."""
    gx, gy = grip
    x0, y0 = int(round(gx)) - 9, int(round(gy)) - 12
    lid = rect(x0, y0, 18, 11) - {(x0, y0), (x0 + 17, y0)}
    solid(cv, lid, "L", None)
    cv.fill(rect(x0 + 1, y0 + 1, 16, 1), "l")
    for (dx, dy) in ((8, 4), (9, 4), (7, 5), (10, 5), (8, 6), (9, 6)):
        cv.put(x0 + dx, y0 + dy, "G")
    base = rect(x0 - 3, y0 + 11, 22, 2)
    solid(cv, base, "l", None)
    glow = p.get("glow", "Z")
    if glow:
        cv.fill({(x, y0 - 1) for x in range(x0 + 2, x0 + 16, 2)}, glow)


def wrench(cv, grip, ang, p):
    f = Frame2(grip, ang)
    solid(cv, f.line([(-2, 0), (9, 0)], 1.0), "st1", None)
    head = f.ell(10.5, 0, 3.0, 3.0) - f.rect(10.5, 14, -1.0, 1.0)
    solid(cv, head, "st1", "st2", shade_off=(1, 1))


def blueprint_roll(cv, grip, ang, p):
    f = Frame2(grip, ang)
    solid(cv, f.rect(-7, 7, -2.0, 2.0), "3", "4", shade_off=(1, 1))
    cv.fill(f.rect(-7, -6, -2, 2) | f.rect(6, 7, -2, 2), "W")


def tape_measure(cv, grip, ang, p):
    gx, gy = grip
    ext = int(p.get("tape", 0))
    solid(cv, ellipse(gx, gy - 1, 3.0, 3.0), "hz1", "y", shade_off=(1, 1))
    if ext:
        cv.fill({(int(gx) + 3 + k, int(gy) - 1) for k in range(ext)}, "Y")
        for k in range(0, ext, 3):
            cv.put(int(gx) + 3 + k, int(gy) - 2, "K")


def flag(cv, grip, ang, p):
    f = Frame2(grip, ang)
    solid(cv, f.line([(-3, 0), (14, 0)], 0.7), "wo2", None)
    wave = p.get("wave", 0.0)
    pts = [(9, 0.5), (14, 0.5), (13.5 + math.sin(wave), 7), (8.5 + math.sin(wave) * 0.6, 7)]
    m = f.poly(pts)
    solid(cv, m, p.get("flag_c", "hz1"), "y", shade_off=(1, 1))
    cv.fill({(x, y) for (x, y) in inner(m) if (x + y) % 4 < 2}, p.get("flag_c2", "R"))


def trophy(cv, grip, ang, p):
    """Piala emas besar 15x15 (Champion)."""
    gx, gy = grip
    x, y = int(round(gx)), int(round(gy))
    cup = poly([(x - 6, y - 14), (x + 6, y - 14), (x + 5, y - 8), (x + 2, y - 5), (x - 2, y - 5), (x - 5, y - 8)])
    stem = rect(x - 1, y - 5, 3, 3)
    base = rect(x - 4, y - 2, 9, 3)
    handles = R.capsule((x - 6, y - 12), (x - 8, y - 9), 0.9) | R.capsule((x + 6, y - 12), (x + 8, y - 9), 0.9)
    solid(cv, handles, "go1", None)
    solid(cv, cup | stem | base, "go1", "go2", shade_off=(1, 1))
    cv.fill({(x - 4, y - 13), (x - 4, y - 12), (x - 3, y - 13)}, "W")
    cv.fill(rect(x - 3, y - 1, 7, 1), "go2")


def whistle(cv, grip, ang, p):
    gx, gy = grip
    solid(cv, rect(int(gx) - 1, int(gy) - 2, 4, 3), "st1", None)


def tasbih(cv, grip, ang, p):
    """Tasbih kayu: untaian butir 2x2 menggantung dari tangan (gaya v1)."""
    gx, gy = grip
    k0 = int(p.get("bead", 0))
    for k in range(9):
        a = math.pi / 2 + (k - 4) * 0.42
        x, y = gx + math.cos(a) * 3.2, gy + 2 + math.sin(a) * 4.0
        cv.fill(rect(int(x), int(y), 2, 2), "le1" if k != k0 % 9 else "go1")


def inkblot(cv, grip, ang, p):
    """Kartu bercak tinta simetris (Psikolog)."""
    gx, gy = grip
    x0, y0 = int(round(gx)) - 6, int(round(gy)) - 10
    solid(cv, rect(x0, y0, 12, 10), "W", "smk", shade_off=(1, 1))
    cx = x0 + 6
    for (dx, dy) in ((1, 2), (2, 2), (1, 3), (2, 3), (3, 3), (1, 4), (2, 5), (3, 6), (1, 6), (2, 7), (4, 4)):
        cv.put(cx - 1 + dx, y0 + dy, "L")
        cv.put(cx - dx, y0 + dy, "L")


def smartphone(cv, grip, ang, p):
    gx, gy = grip
    solid(cv, rect(int(gx) - 2, int(gy) - 6, 5, 8), "L", None)
    cv.fill(rect(int(gx) - 1, int(gy) - 5, 3, 5), "I")


def banana(cv, grip, ang, p):
    import monkey as M
    M.banana(cv, int(grip[0]), int(grip[1]), bites=int(p.get("bites", 0)))


def coffee(cv, grip, ang, p):
    gx, gy = grip
    x0, y0 = int(round(gx)) - 3, int(round(gy)) - 6
    solid(cv, rect(x0, y0, 7, 7), "C", "c", shade_off=(1, 1))
    cv.fill(rect(x0 + 1, y0 + 1, 5, 1), "D")


def gblk_sign(cv, grip, ang, p):
    """Papan GBLK besar bertongkat: 31x13, teks 5x5 kontras tinggi (K di atas krem)."""
    f = Frame2(grip, ang)
    top = f.world(17, 0)
    solid(cv, chain([grip, top], 0.9), "wo1", None)
    tx, ty = int(round(top[0])), int(round(top[1]))
    w, h = 29, 11
    x0, y0 = tx - w // 2, ty - h + 1
    if p.get("sign_tilt"):
        y0 += 1
    m = rect(x0, y0, w, h)
    solid(cv, m, "n", "Y", shade_off=(1, 1))
    mini_text(cv, "GBLK", x0 + 3, y0 + 3, "K")


for _name, _fn, _over in [
    ("book_open", book_open, True), ("book_closed", book_closed, True), ("book_stack", book_stack, True),
    ("scroll_open", scroll_open, True), ("scroll_rolled", scroll_rolled, True), ("timeline", timeline, True),
    ("clipboard", clipboard, True), ("notebook", notebook, True), ("pen", pen, False), ("quill", quill, False),
    ("chalk", chalk, True), ("magnifier", magnifier, False), ("flask", flask, True), ("gavel", gavel, False),
    ("papers", papers, True), ("diploma", diploma, True), ("calculator", calculator, True), ("ledger", ledger, True),
    ("laptop_side", laptop_side, True), ("wrench", wrench, False), ("blueprint_roll", blueprint_roll, True),
    ("tape_measure", tape_measure, True), ("flag", flag, False), ("trophy", trophy, True), ("whistle", whistle, True),
    ("tasbih", tasbih, False), ("inkblot", inkblot, True), ("smartphone", smartphone, True), ("banana", banana, False),
    ("coffee", coffee, True), ("gblk_sign", gblk_sign, False),
]:
    I.register(_name, _fn, _over)


# ------------------------------------------------------------------ prop panggung (posisi kanvas)
def easel_board(cv, x0, y0, w=24, h=17, kind="formula", t=0, frame="wo1"):
    """Papan berkaki di kanan Gobyet. kind: formula, chart_up, chart_down, network, blueprint, evidence, crowd, terminal,
    timeline, blank, score."""
    legs = R.capsule((x0 + 4, y0 + h), (x0 + 1, R.BASE - 1), 0.8) | R.capsule((x0 + w - 4, y0 + h), (x0 + w - 1, R.BASE - 1), 0.8)
    solid(cv, legs, "wo2", None)
    surf = {"formula": ("k", "k"), "blueprint": ("3", "4"), "terminal": ("q", "q"), "evidence": ("le1", "le2")}.get(kind, ("W", "smk"))
    m = rect(x0, y0, w, h)
    solid(cv, m, frame, "wo2", shade_off=(1, 1))
    cv.fill(inner(m) - edge(inner(m)) if w > 6 else inner(m), surf[0])
    ix, iy = x0 + 2, y0 + 2
    if kind == "formula":
        text3(cv, "a", ix + 1, iy + 1, "W")
        sup2(cv, ix + 5, iy, "W")
        text3(cv, "+b", ix + 8, iy + 1, "W")
        sup2(cv, ix + 16, iy, "W")
        text3(cv, "=c", ix + 4, iy + 8, "W")
        sup2(cv, ix + 12, iy + 7, "W")
        if t:
            cv.fill({(ix + 15 + (t % 3), iy + 9)}, "Y")
    elif kind in ("chart_up", "chart_down"):
        cv.fill({(ix, y) for y in range(iy, y0 + h - 2)} | {(x, y0 + h - 3) for x in range(ix, x0 + w - 2)}, "K")
        lo, hi = y0 + h - 5, iy + 1
        pts = [(ix + 1, lo), (ix + 5, lo - 3), (ix + 9, lo - 1), (ix + 14, lo - 6), (ix + w - 5, hi)]
        if kind == "chart_down":
            pts = [(x, lo + hi - y) for (x, y) in pts]
        cv.fill(chain(pts[: 2 + min(3, t)] if t else pts, 0.6), "V" if kind == "chart_up" else "R")
        for k in range(4):
            cv.fill(rect(ix + 2 + k * 5, y0 + h - 4 - (k + 1) * 2, 2, (k + 1) * 2), "3")
    elif kind == "network":
        nodes = [(ix + 3, iy + 3), (ix + 12, iy + 2), (ix + 18, iy + 7), (ix + 8, iy + 10), (ix + 2, iy + 11), (ix + 15, iy + 12)]
        for a, b in ((0, 1), (1, 2), (0, 3), (3, 4), (3, 5), (2, 5), (1, 3)):
            cv.fill(chain([nodes[a], nodes[b]], 0.4), "s")
        for k, (x, y) in enumerate(nodes):
            solid(cv, ellipse(x, y, 1.8, 1.8), ("R", "3", "V", "go1", "pk1", "o")[k], None)
    elif kind == "blueprint":
        cv.fill({(x, iy + 2) for x in range(ix + 1, x0 + w - 3)} | {(ix + 1, y) for y in range(iy + 2, y0 + h - 3)}, "W")
        cv.fill({(x, y0 + h - 4) for x in range(ix + 1, x0 + w - 3)} | {(x0 + w - 4, y) for y in range(iy + 2, y0 + h - 3)}, "W")
        cv.fill(chain([(ix + 4, y0 + h - 4), (ix + 10, iy + 5), (ix + 16, y0 + h - 4)], 0.4), "W")
        text3(cv, "1/2", ix + 6, y0 + h - 9, "W")
    elif kind == "evidence":
        for k, (dx, dy, c) in enumerate(((2, 2, "W"), (12, 3, "W"), (6, 9, "cm1"), (15, 10, "W"))):
            solid(cv, rect(ix + dx, iy + dy - 1, 5, 4), c, None)
            cv.put(ix + dx + 2, iy + dy - 1, "R")
        cv.fill(chain([(ix + 4, iy + 1), (ix + 14, iy + 2), (ix + 8, iy + 8), (ix + 17, iy + 9)], 0.4), "R")
    elif kind == "crowd":
        for k in range(5):
            x = ix + 2 + k * 4
            solid(cv, ellipse(x, iy + 5 + (k % 2), 1.5, 1.5), ("R", "3", "V", "go1", "pk1")[k], None)
            cv.fill(rect(x - 1, iy + 7 + (k % 2), 3, 4), ("R", "3", "V", "go1", "pk1")[k])
        cv.fill(chain([(ix + 2, iy + 2), (ix + 10, iy + 1), (ix + 18, iy + 3)], 0.4), "s")
    elif kind == "terminal":
        cv.fill(rect(ix, iy, w - 4, 1), "l")
        for k in range(min(4, 1 + t % 5)):
            cv.fill({(x, iy + 3 + k * 2) for x in range(ix + 1, ix + 4 + (k * 5) % 12)}, "Z")
    elif kind == "error":
        cv.fill(inner(m) - edge(inner(m)), "q")
        cv.fill(rect(ix, iy, w - 4, 1), "R")
        text3(cv, "X", x0 + w // 2 - 1, iy + 3, "R")
        cv.fill({(x, iy + 10) for x in range(ix + 2, x0 + w - 4)}, "R")
    elif kind == "score":
        for k in range(3):
            text3(cv, ("8", "6", "9")[k], ix + 1, iy + k * 5, "K")
            cv.fill({(x, iy + 2 + k * 5) for x in range(ix + 5, ix + 5 + (6, 4, 8)[k])}, ("V", "go1", "3")[k])
    return m


def desk(cv, x0, y0, w=30, h=11, top=("wo1", "wo2"), front=("wo2", "le2")):
    """Meja di depan Gobyet (Judge): menutup kaki, menjadi bagian siluet."""
    solid(cv, rect(x0, y0 + 2, w, h), front[0], front[1], shade_off=(1, 1))
    solid(cv, rect(x0 - 2, y0, w + 4, 3), top[0], top[1], shade_off=(1, 1))
    cv.fill({(x0 + w // 2 - 3 + k, y0 + 6) for k in range(7)}, "go1")


def archive_box(cv, x0, y0, open_=False):
    solid(cv, rect(x0, y0, 14, 10), "X", "x", shade_off=(1, 1))
    solid(cv, rect(x0 + 4, y0 + 3, 6, 3), "W", None)
    if open_:
        solid(cv, rect(x0 + 2, y0 - 4, 4, 5), "W", "smk", shade_off=(1, 1))
        solid(cv, rect(x0 + 7, y0 - 3, 4, 4), "cm1", "cm2", shade_off=(1, 1))


def lightbulb(cv, x, y, on=True):
    m = ellipse(x, y, 3.6, 3.8) | rect(int(x) - 2, int(y) + 2, 4, 3)
    solid(cv, m, "Y" if on else "W", "O" if on else "smk", shade_off=(1, 1))
    cv.fill(rect(int(x) - 2, int(y) + 4, 4, 2), "st2")
    if on:
        for a in range(0, 360, 45):
            r = math.radians(a)
            cv.put(int(x + math.cos(r) * 6), int(y + math.sin(r) * 6), "Y")


def aura(cv, g, k=0):
    """Aura halus (sama persis untuk Pak Haji dan Priest, aturan 7.2): titik-titik emas jarang di sekeliling badan.
    Efek visual saja, bukan penanda argumen benar."""
    cx, cy = g.tcx, g.tcy - 6
    for a in range(0, 360, 20):
        r = math.radians(a + k * 10)
        for rr in (17,):
            x, y = cx + math.cos(r) * rr, cy + math.sin(r) * (rr + 2)
            if (a // 20 + k) % 3 == 0:
                cv.put(int(x), int(y), "Y")


def terminal_window(cv, x0, y0, t=0, kind="terminal", w=24, h=16):
    """Jendela terminal melayang (Hacker)."""
    m = rect(x0, y0, w, h)
    solid(cv, m, "l", None)
    cv.fill(inner(m), "q")
    cv.fill(rect(x0 + 1, y0 + 1, w - 2, 2), "l")
    cv.fill({(x0 + 2, y0 + 1), (x0 + 4, y0 + 1), (x0 + 6, y0 + 1)}, "R")
    if kind == "terminal":
        for k in range(min(5, 1 + t % 6)):
            cv.fill({(x, y0 + 5 + k * 2) for x in range(x0 + 2, x0 + 5 + (k * 7 + t) % 15)}, "Z")
    elif kind == "error":
        cv.fill(rect(x0 + 1, y0 + 1, w - 2, 2), "R")
        text3(cv, "X", x0 + w // 2 - 1, y0 + 5, "R")
        cv.fill({(x, y0 + 12) for x in range(x0 + 3, x0 + w - 3)}, "R")
    elif kind == "ok":
        cv.fill({(x0 + 7, y0 + 9), (x0 + 8, y0 + 10), (x0 + 9, y0 + 11), (x0 + 10, y0 + 10), (x0 + 11, y0 + 9), (x0 + 12, y0 + 8),
                 (x0 + 13, y0 + 7), (x0 + 14, y0 + 6)}, "Z")
        text3(cv, "OK", x0 + 8, y0 + 3, "Z") if False else None
    elif kind == "debug":
        for k in range(4):
            c = "R" if k == (t % 4) else "Z"
            cv.fill({(x, y0 + 5 + k * 2) for x in range(x0 + 2, x0 + 4 + (k * 5) % 12)}, c)


# ------------------------------------------------------------------ ikon aksesori kecil (konteks hibrida)
def mini_board(cv, grip, ang, p):
    gx, gy = int(grip[0]), int(grip[1])
    m = rect(gx - 7, gy - 5, 14, 10)
    solid(cv, m, "wo1", "wo2", shade_off=(1, 1))
    cv.fill(inner(m), "k")
    text3(cv, "x", gx - 5, gy - 3, "W")
    sup2(cv, gx - 1, gy - 4, "W")
    text3(cv, "=", gx + 2, gy - 3, "W")


def mini_laptop(cv, grip, ang, p):
    gx, gy = int(grip[0]), int(grip[1])
    scr = rect(gx - 6, gy - 7, 12, 9)
    solid(cv, scr, "L", None)
    cv.fill(inner(scr), "q")
    for k in range(3):
        cv.fill({(x, gy - 5 + k * 2) for x in range(gx - 4, gx - 1 + k * 2)}, "Z")
    solid(cv, rect(gx - 8, gy + 2, 16, 3), "l", None)


def mini_network(cv, grip, ang, p):
    gx, gy = grip
    nodes = [(gx - 5, gy - 4), (gx + 5, gy - 5), (gx, gy + 1), (gx - 5, gy + 5), (gx + 5, gy + 5)]
    for a, b in ((0, 2), (1, 2), (2, 3), (2, 4), (0, 1)):
        cv.fill(chain([nodes[a], nodes[b]], 0.4), "l")
    for k, (x, y) in enumerate(nodes):
        solid(cv, ellipse(x, y, 1.9, 1.9), ("R", "3", "V", "go1", "pk1")[k], None)


def mini_star(cv, grip, ang, p):
    gx, gy = grip
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = 6.5 if i % 2 == 0 else 2.8
        pts.append((gx + math.cos(a) * r, gy + math.sin(a) * r))
    solid(cv, poly(pts), "Y", "O", shade_off=(1, 1))


def mini_question(cv, grip, ang, p):
    gx, gy = int(grip[0]), int(grip[1])
    m = rect(gx - 6, gy - 6, 12, 12)
    solid(cv, m, "W", "smk", shade_off=(1, 1))
    mini_text(cv, "?", gx - 2, gy - 3, "R")


for _name, _fn in [("mini_board", mini_board), ("mini_laptop", mini_laptop), ("mini_network", mini_network),
                   ("mini_star", mini_star), ("mini_question", mini_question)]:
    I.register(_name, _fn, True)


def briefcase(cv, grip, ang, p):
    """Koper kerja Lawyer: kotak 13x9 bergagang, digantung di tangan (grip = gagang)."""
    gx, gy = int(round(grip[0])), int(round(grip[1]))
    cv.fill({(gx - 2, gy - 1), (gx - 2, gy), (gx + 2, gy - 1), (gx + 2, gy), (gx - 1, gy - 2), (gx, gy - 2), (gx + 1, gy - 2)}, "K")
    m = rect(gx - 6, gy + 1, 13, 9)
    solid(cv, m, "le2", "D", shade_off=(1, 1))
    cv.fill({(x, gy + 4) for x in range(gx - 5, gx + 6)}, "D")
    cv.fill(rect(gx - 1, gy + 3, 3, 2), "go1")


def armchair(cv, cx, seat_y, c=("le1", "le2")):
    """Kursi berlengan bersandaran tinggi (Psychologist duduk): siluet khas terapis."""
    cx = int(round(cx))
    back = rect(cx - 11, seat_y - 19, 23, 20) - {(cx - 11, seat_y - 19), (cx + 11, seat_y - 19), (cx - 10, seat_y - 19),
                                                  (cx + 10, seat_y - 19), (cx - 11, seat_y - 18), (cx + 11, seat_y - 18)}
    solid(cv, back, c[0], c[1], shade_off=(2, 2))
    for k in range(3):
        for s in (-1, 1):
            cv.put(cx + s * 5, seat_y - 15 + k * 5, "go2")
    for s in (-1, 1):
        legm = rect(cx + s * 10 - (1 if s < 0 else 0), seat_y + 5, 2, R.BASE - 1 - (seat_y + 5) + 1)
        solid(cv, legm, "wo2", None)
    seat = rect(cx - 12, seat_y, 25, 5)
    solid(cv, seat, c[0], c[1], shade_off=(1, 1))
    for s in (-1, 1):
        arm = rect(cx + s * 12 - 2, seat_y - 7, 5, 12) - {(cx + s * 12 - 2, seat_y - 7), (cx + s * 12 + 2, seat_y - 7)}
        solid(cv, arm, c[0], c[1], shade_off=(1, 1))


I.register("briefcase", briefcase, True)
