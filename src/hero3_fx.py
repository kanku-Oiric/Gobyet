"""Efek dan properti untuk Berserker Hero v3, semuanya berpalet v3 (tanpa warna bulu atau wajah Gobyet).

Nama bagian (`part`) sama dengan efek v1 supaya pemeriksaan pemilik piksel di validator tetap berlaku: dust, chip, burst, smear, block, speed, sweat,
breath, spark, roar. Tambahan v3: rock (batu), ichor (tetes darah monster), glint (kilau bilah bersih), steam (uap dari topeng), ember (bara rage).

Warna: besi hitam `n0..n4`, merah `q0..q4`, inti cahaya `wh` (hero3.HERO3_PAL); batu `s1..s3`, kayu `w1..w3`, darah monster `m1..m3` (merah darah gelap)
(HERO3_FX_PAL, didaftarkan ke `monkey.PAL_HERO`). Semua deterministik (seed tetap), tanpa alfa parsial.
"""
import math
import random

import monkey
from monkey import ellipse, rect, edge

from hero import part, poly, solid3, FLOOR

HERO3_FX_PAL = {
    "s1": (62, 60, 66), "s2": (104, 100, 104), "s3": (158, 150, 142),         # batu dan debu: bayangan, dasar, sorotan (abu hangat)
    "w1": (84, 54, 36), "w2": (132, 88, 52), "w3": (180, 128, 76),            # kayu: bayangan, dasar, sorotan
    "m1": (74, 2, 12), "m2": (140, 10, 22), "m3": (232, 96, 88),             # darah monster: merah darah gelap, dasar, kilau basah (lebih gelap dari api bilah; kilau membedakan noda)
}
monkey.PAL_HERO.update({k: v for k, v in HERO3_FX_PAL.items() if k not in monkey.PAL_HERO})
assert not set(HERO3_FX_PAL) & (set(monkey.PAL) | set(monkey.PAL_EXT)), "kunci palet fx hero3 bentrok"

STONE, WOOD, ICHOR = ("s1", "s2", "s3"), ("w1", "w2", "w3"), ("m1", "m2", "m3")
OUT = "n0"


# ------------------------------------------------------------------ debu, serpihan, ledakan, sapuan
def fx_dust(cv, x, y, k, size=1.0):
    """Kepulan debu di lantai (y = baris lantai) yang melebar ke dua sisi (k = 0..3)."""
    for s_ in (-1, 1):
        for j in range(3):
            off = (4 + j * 4.0 + k * 3.0) * s_ * size
            r = (1.6 + j * 0.5 + k * 0.4) * size
            m = {q for q in ellipse(x + off, y - r * 0.7 - k * 0.8 - j * 0.6, r, r * 0.8) if q[1] < FLOOR}
            part(cv, "dust")
            ring = edge(m)
            cv.fill(m - ring, "s3" if k < 2 else "s2")
            cv.fill({(xx, yy) for (xx, yy) in m - ring if (xx + 1, yy + 1) in ring}, "s2")
            cv.fill(ring, "s2" if k < 2 else "s1")


def fx_chips(cv, x, y, k, seed=0, n=8, power=1.0):
    """Serpihan kayu dan batu beterbangan dari titik hantam."""
    rnd = random.Random(seed)
    for j in range(n):
        vx, vy = rnd.uniform(-3.4, 3.4) * power, rnd.uniform(3.0, 6.0) * power
        t = k + 0.6
        px_, py_ = x + vx * t, y - vy * t + 0.9 * t * t
        px_ = max(3.0, min(px_, 123.0))                                           # serpihan tidak keluar dari tepi kanvas
        if py_ >= FLOOR - 1:
            py_ = FLOOR - 2
        part(cv, "chip")
        c = ("w2", "w3", "s3", "w2")[j % 4]
        cv.fill(rect(int(px_), int(py_), 2, 2 if j % 3 == 0 else 1), c)
        if j % 3 == 0:
            cv.put(int(px_) + 2, int(py_), OUT)


def fx_burst(cv, x, y, r=7):
    """Kilatan hantam: inti putih-hangat dan percikan api merah."""
    part(cv, "burst")
    cv.fill(ellipse(x, y, r * 0.55, r * 0.5), "wh")
    for j in range(10):
        a = j * math.tau / 10 + 0.2
        for i in range(int(r * (0.7 if j % 2 else 1.1))):
            rr = r * 0.55 + i
            cv.put(int(x + math.cos(a) * rr), int(y + math.sin(a) * rr * 0.9), "q4" if i < 2 else "q3")


def fx_smear(cv, cx, cy, r, a0, a1, width=1, dither=True):
    """Busur terang tipis (smear) mengikuti bilah: dari sudut a0 ke a1 (derajat layar, 0 = kanan, 90 = bawah) di jari-jari r, memudar (dither) ke a0."""
    n = int(abs(a1 - a0) * math.pi / 180.0 * r * 1.6) + 2
    part(cv, "smear")
    for i in range(n + 1):
        t = i / float(n)
        a = math.radians(a0 + (a1 - a0) * t)
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
        if dither and t < 0.45 and (i % 2):
            continue
        for w in range(width):
            col = "wh" if t > 0.55 else "n4"
            cv.put(int(round(x - math.cos(a) * w)), int(round(y - math.sin(a) * w)), col)


def wood_block(cv, x, y_floor, w=18, h=10, crack=1):
    """Balok kayu di lantai (sasaran): sisi depan bergaris serat, sisi atas lebih terang. x = tengah.
    crack: 0 utuh, 1 retak kecil, 2 retak panjang dengan takik terbelah di atas."""
    x0, y0 = int(x - w / 2), int(y_floor - h)
    front = rect(x0, y0 + 3, w, h - 3)
    top = poly([(x0 + 1, y0 + 3), (x0 + 4, y0), (x0 + w + 2, y0), (x0 + w, y0 + 3)])
    solid3(cv, front, WOOD, OUT, depth=2, name="block")
    solid3(cv, top, ("w2", "w3", "w3"), OUT, name="block")
    part(cv, "block")
    for yy in (y0 + 5, y0 + 7):
        cv.fill({(xx, yy) for xx in range(x0 + 2, x0 + w - 2) if (xx + yy) % 5 != 0}, "w1")
    if crack >= 1:
        cv.fill({(x0 + w // 2 + dx, y0 + 3 + dy) for dx, dy in ((0, 0), (-1, 1), (0, 2), (1, 3))}, OUT)
    if crack >= 2:
        cv.fill({(x0 + w // 2 + dx, y0 + 3 + dy) for dx, dy in ((1, 4), (0, 5), (-1, 6), (0, 7))}, OUT)
        for dx in (-1, 0, 1):
            cv.px.pop((x0 + w // 2 + 1 + dx, y0), None)
            cv.put(x0 + w // 2 + 1 + dx, y0 + 1, OUT)


def fx_speed(cv, x, y, n=3, length=9):
    """Garis kecepatan di belakang (kiri) titik (x, y)."""
    part(cv, "speed")
    for k in range(n):
        yy = y + (k - (n - 1) / 2.0) * 5
        L = length - (k % 2) * 3
        for i in range(L):
            if i % 5 != 4:
                cv.put(int(x - i), int(yy), "wh" if k == 1 else "n4")


def fx_sweat(cv, x, y):
    """Setetes keringat pendingin (tetes terbalik 3 px) berwarna abu-putih dengan sorotan."""
    part(cv, "sweat")
    cv.fill({(x, y), (x - 1, y + 1), (x, y + 1), (x + 1, y + 1), (x - 1, y + 2), (x, y + 2), (x + 1, y + 2), (x, y + 3)}, "s3")
    cv.put(x - 1, y + 1, "wh")
    cv.fill({(x + 1, y + 2), (x, y + 3)}, "s2")


def fx_breath(cv, x, y, k):
    """Kepulan uap napas kecil yang membesar dan memudar (k = 0..2)."""
    part(cv, "breath")
    r = 1.4 + k * 0.9
    m = ellipse(x + k * 2.0, y - k * 0.8, r, r * 0.8)
    if k >= 2:
        m = {q for q in m if (q[0] + q[1]) % 2 == 0}
        cv.fill(m, "s3")
    else:
        cv.fill(m, "s3")
        cv.fill(edge(m), "s2")


def fx_steam(cv, x, y, k):
    """Uap pendek yang keluar dari celah topeng saat membuka atau menutup (k = 0..3 naik dan memudar)."""
    part(cv, "steam")
    for j, dx in enumerate((-2, 1, 4)):
        yy = y - k * 2 - j
        if (j + k) % 3 == 2:
            continue
        cv.fill({(x + dx, yy), (x + dx + 1, yy), (x + dx, yy - 1)}, "s3" if k < 2 else "s2")


def fx_embers(cv, x, y, k, seed=0, n=6, spread=14):
    """Bara merah menyala yang naik dari titik (x, y): piksel 1-2 px berwarna q4/q3/wh, memudar ke atas (k = 0..5)."""
    rnd = random.Random(seed * 13 + 5)
    part(cv, "spark")
    for j in range(n):
        ox = rnd.uniform(-spread, spread)
        rise = (3 + (k + j) % 5 * 2.5) + rnd.uniform(0, 4)
        px_, py_ = x + ox + math.sin((k + j) * 0.9) * 1.5, max(y - rise, 2.0)       # bara tidak keluar dari tepi atas kanvas
        c = ("q4", "wh", "q3", "q4", "q3", "q2")[(j + k) % 6]
        cv.put(int(px_), int(py_), c)
        if j % 2 == 0:
            cv.put(int(px_), int(py_) + 1, "q2")


def fx_roar(cv, x, y, k):
    """Garis kejut pendek yang memancar dari titik (x, y) ke kanan; k = 0..2 menggeser panjangnya."""
    part(cv, "roar")
    for j, a in enumerate((-38, -14, 10, 34)):
        r = math.radians(a)
        L = 5 + (j + k) % 3 * 2
        for i in range(L):
            cv.put(int(x + math.cos(r) * (8 + i)), int(y + math.sin(r) * (8 + i)), "wh" if i < L - 2 else "q4")


# ------------------------------------------------------------------ batu, darah monster, kilau
def rock(cv, x, y_floor, w=18, h=10):
    """Batu pijakan di lantai (x = tengah): bentuk tidak beraturan, sisi atas terang, retakan, satu kerikil di samping. h = tinggi puncak."""
    x0, base = int(x - w / 2), int(y_floor)
    pts = [(x0, base), (x0 + 0.5, base - h * 0.45), (x0 + 3, base - h * 0.8), (x0 + w * 0.42, base - h), (x0 + w * 0.7, base - h * 0.93),
           (x0 + w - 1.5, base - h * 0.6), (x0 + w, base - h * 0.2), (x0 + w, base)]
    m = poly(pts)
    solid3(cv, m, STONE, OUT, depth=2, name="rock")
    part(cv, "rock")
    cv.fill({(x0 + w // 2 - 2 + i, base - h + 2 + i // 2) for i in range(0, 4)}, "s1")             # retakan di puncak
    cv.fill({(x0 + w // 2 + 1, base - h + 5 + i) for i in range(0, 3)}, "s1")
    cv.fill({(x0 + 3 + i, base - 3) for i in range(0, 3)}, "s1")
    for dx, dy in ((4, 3), (w - 5, 4)):                                                              # bintik terang
        cv.put(x0 + dx, base - h + dy, "s3")
    peb = ellipse(x0 + w + 3.5, base - 1.5, 2.6, 1.7)
    solid3(cv, peb, STONE, OUT, depth=1, name="rock")


def fx_ichor_drip(cv, x, y, k):
    """Setetes darah monster jatuh dari ujung bilah ke lantai (k = 0..3 tinggi jatuh); membentuk bintik kecil di lantai saat k = 3."""
    part(cv, "ichor")
    if k < 3:
        yy = y + k * 3
        cv.fill({(x, yy), (x, yy + 1)}, "m2")
        cv.put(x, yy, "m3")
    else:
        cv.fill({(x - 1, FLOOR - 1), (x, FLOOR - 1), (x + 1, FLOOR - 1), (x, FLOOR - 2)}, "m2")
        cv.put(x - 1, FLOOR - 1, "m1")
        cv.put(x + 1, FLOOR - 1, "m1")


def fx_glint(cv, x, y, k):
    """Kilau bintang empat sinar pada bilah bersih (k = 0..2 membesar lalu mengecil)."""
    part(cv, "glint")
    arms = (1, 3, 2)[k % 3]
    cv.put(x, y, "wh")
    for d in range(1, arms + 1):
        for (dx, dy) in ((d, 0), (-d, 0), (0, d), (0, -d)):
            cv.put(x + dx, y + dy, "wh" if d == 1 else "n4")
