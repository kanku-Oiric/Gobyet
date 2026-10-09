"""Berserker Hero v3 (kostum `berserker-hero`, kanvas 128x96): rombak dari awal atas arahan pemilik.

Arah (dari pemilik; gambar referensi tidak disimpan di repo):
  - model badan mengikuti referensi pertama: prajurit mesin chibi, helm dan jambul sangat besar tanpa leher, satu pelindung bahu raksasa
    dengan sirip tanduk dan panel "wajah" kecil, bahu satunya bundar, perut berpola sisik heksagonal, sepatu pendek bercakar, ekor kipas
    panah melengkung di belakang;
  - BASIS BUKAN GOBYET: tidak ada kepala, wajah, telinga, atau bulu Gobyet. Kepala adalah helm penuh bermata cahaya;
  - kepala referensi pertama dipertahankan (jambul menyapu ke belakang, pita V di atas wajah, sirip samping, rahang bergrill) tetapi
    coraknya mengikuti referensi kedua: besi hitam, garis merah darah, salib merah menyala di visor;
  - zirah dan senjata mengikuti referensi kedua: pelat hitam bergaris merah, pedang hitam raksasa berinti api merah;
  - sedikit modern: strip cahaya, panel rapi, ventilasi, baut; kesan mekanis tetap.
Bentuk dan nada warna turunan, bukan salinan piksel. "Merah darah" hanya warna dan corak: tidak ada darah, luka, atau kematian brutal.

Rig: bentuk besar digambar dari poligon bernada tiga (`solid3`, cahaya kiri atas), detail kecil dari piksel eksplisit. `PartCanvas` mencatat
pemilik tiap piksel supaya bagian yang terlihat dapat diukur. Emosi dibawa oleh visor (lengan salib), alis V, dan grill mulut.
"""
import math

import monkey
from monkey import ellipse, rect, edge, chain

import hero as H
from hero import PartCanvas, part, poly, thick, bezier, inner, solid3, ik, SwordFrame, floor_clip, FLOOR

# ------------------------------------------------------------------ palet (11 kunci baru; efek memakai kunci HERO_PAL v1)
HERO3_PAL = {
    "n0": (14, 12, 18), "n1": (28, 26, 34), "n2": (46, 44, 56), "n3": (78, 76, 92), "n4": (130, 128, 148),     # besi hitam: garis tepi ... baja terang
    "q0": (54, 6, 16), "q1": (104, 10, 26), "q2": (166, 18, 34), "q3": (222, 38, 44), "q4": (255, 112, 86),    # merah darah: gelap ... menyala
    "wh": (255, 232, 214),                                                                                       # inti putih-hangat cahaya
}
monkey.PAL_HERO.update({k: v for k, v in HERO3_PAL.items() if k not in monkey.PAL_HERO})
assert not set(HERO3_PAL) & (set(monkey.PAL) | set(monkey.PAL_EXT) | set(H.HERO_PAL)), "kunci palet hero3 bentrok"

IRON, STEELL = ("n1", "n2", "n3"), ("n2", "n3", "n4")
OUT, ROUT = "n0", "q0"
RED, REDB = ("q0", "q1", "q2"), ("q1", "q2", "q3")

# ------------------------------------------------------------------ ukuran badan
UPPER, FORE = 8.0, 8.5
LEG = 10.0
THIGH, SHIN = 5.0, 5.0
SH_X, SH_Y = 17.0, 8.0            # sendi bahu: +- SH_X dari tengah dada, SH_Y di atas pusat dada
HEAD_DY = 24.0                    # pusat helm di atas pusat dada


# ================================================================== bentuk dasar
def blade_poly(p0, p1, p2, w0, n=14, w1=0.0, taper=0.85):
    """Bilah runcing melengkung: garis tengah bezier p0-p1-p2, lebar w0 di pangkal menyusut ke w1 di ujung."""
    pts = bezier(p0, p1, p2, n)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        a = pts[max(0, i - 1)]
        b = pts[min(len(pts) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / d, dx / d
        t = i / float(len(pts) - 1)
        w = (w1 + (w0 - w1) * (1.0 - t) ** taper) * 0.5
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return poly(left + right[::-1])


def arrow(cx, cy, ang, L, w):
    """Kepala panah (chevron cekung): ujung di depan, dua sayap lebar di belakang, takik di tengah; satu poligon agar tepinya bersih."""
    ca, sa = math.cos(ang), math.sin(ang)
    tip = (cx + ca * L * 0.55, cy + sa * L * 0.55)
    back = (cx - ca * L * 0.45, cy - sa * L * 0.45)
    wl = (back[0] - sa * w * 0.5, back[1] + ca * w * 0.5)
    wr = (back[0] + sa * w * 0.5, back[1] - ca * w * 0.5)
    notch = (cx - ca * L * 0.12, cy - sa * L * 0.12)
    return poly([tip, wl, notch, wr])


def flat(cv, mask, base, outline, light=None, name=None):
    """Isi rata dengan garis tepi 1 px, sorotan opsional di tepi atas-kiri."""
    if name:
        part(cv, name)
    ring = edge(mask)
    body = mask - ring
    cv.fill(body, base)
    if light:
        cv.fill({(x, y) for (x, y) in body if (x - 1, y) in ring or (x, y - 1) in ring}, light)
    cv.fill(ring, outline)
    return body


def bolts(cv, pts, c="n4"):
    keep = cv.part
    for (x, y) in pts:
        cv.put(int(x), int(y), c)
    cv.part = keep


def px(cv, pts, c, name=None):
    """Piksel eksplisit (daftar (x, y))."""
    if name:
        part(cv, name)
    for (x, y) in pts:
        cv.put(int(x), int(y), c)


def hline(x0, x1, y):
    return [(x, y) for x in range(int(x0), int(x1) + 1)]


def vline(x, y0, y1):
    return [(x, y) for y in range(int(y0), int(y1) + 1)]


def tr(pts, cx, cy):
    return [(cx + x, cy + y) for x, y in pts]


def rim_pass3(cv):
    """Rim light 1 px: piksel besi tepat di bawah garis tepi besi menjadi baja terang (tepi atas bagian besi)."""
    iron = {"n1", "n2", "n3"}
    for (x, y), c in list(cv.px.items()):
        if c in iron and cv.px.get((x, y - 1)) == OUT:
            cv.px[(x, y)] = "n4" if c == "n3" else "n3"
    return cv


# ================================================================== kepala: helm penuh (pusat (0,0) = pusat helm)
CREST = (   # (pangkal, kendali, ujung, lebar pangkal): bilah jambul menyapu ke belakang-atas (kiri), satu tegak, satu pendek ke depan
    ((-6, -13), (-21, -21), (-35, -21), 7.5),
    ((-3, -15), (-15, -27), (-25, -30), 7.5),
    ((0, -16), (-8, -28), (-13, -35), 7.0),
    ((3, -16), (2, -28), (-1, -36), 6.5),
    ((6, -15), (11, -25), (10, -33), 5.0),
)


def crest(cv, cx, cy, sway=0.0):
    """Jambul bilah merah darah menyapu ke belakang-atas (digambar di belakang helm); sway menggeser ujung (piksel)."""
    for k, (p0, p1, p2, w0) in enumerate(CREST):
        tip = (p2[0] - sway * (0.4 + 0.12 * k), p2[1] + sway * 0.12 * (k % 3))
        ctl = (p1[0] - sway * 0.25, p1[1])
        m = blade_poly((cx + p0[0], cy + p0[1]), (cx + ctl[0], cy + ctl[1]), (cx + tip[0], cy + tip[1]), w0, taper=0.62)
        tone = RED if k % 2 == 0 else ("q0", "q1", "q2")
        solid3(cv, m, tone, ROUT, depth=1, name="crest")
        mid = bezier((cx + p0[0], cy + p0[1]), (cx + ctl[0], cy + ctl[1]), (cx + tip[0], cy + tip[1]), 14)
        for i in range(2, 11):                                 # urat terang di sepanjang bilah
            x, y = mid[i]
            if (int(x), int(y)) in m and (int(x), int(y) + 1) in m:
                cv.put(int(x), int(y), "q3" if (k % 2 and i % 3 == 0) else ("q2" if k % 2 else "q1"))


EYE_STYLES = {
    # (kemiringan ujung luar: negatif = ujung luar naik, tebal, kecerahan 0..2, panjang)
    "look": (0.0, 3, 2, 8), "angry": (-3.0, 3, 2, 8), "rage": (-4.0, 4, 2, 9), "wide": (0.0, 4, 2, 8), "dim": (1.5, 2, 0, 7),
    "tired": (2.5, 2, 0, 6), "shut": (0.0, 1, 0, 7), "glare": (-2.0, 2, 2, 9),
}


def visor(cv, hx, hy, eyes="look"):
    """Visor salib: batang tegak di tengah dan lengan datar yang menjadi mata; lengan miring, tebal, redup mengubah ekspresi."""
    part(cv, "visor")
    if eyes == "x":                                            # defeated: visor padam, dua tanda silang redup
        for y in range(hy - 3, hy + 9):
            cv.put(hx, y, "q0")
        for s in (-1, 1):
            for i in range(-2, 3):
                cv.put(hx + s * 7 + i, hy + 1 + i, "q1")
                cv.put(hx + s * 7 + i, hy + 1 - i, "q1")
            cv.put(hx + s * 7, hy + 1, "q2")
        return
    tilt, thick_, bright, length = EYE_STYLES[eyes]
    # batang tegak
    for y in range(hy - 3, hy + 9):
        cv.put(hx - 1, y, "q1")
        cv.put(hx + 1, y, "q1")
        cv.put(hx, y, "q3" if bright else "q1")
    if bright:
        for y in (hy + 0, hy + 1, hy + 2):
            cv.put(hx, y, "q4")
    cv.put(hx, hy + 1, "wh" if bright == 2 else "q3")
    # lengan mata
    for s in (-1, 1):
        for i in range(length):
            x = hx + s * (2 + i)
            y0 = hy + 1 + int(round(tilt * i / float(length - 1)))
            rows = list(range(thick_))
            top = y0 - thick_ // 2
            for r in rows:
                yy = top + r
                if thick_ == 1:
                    c = "q2" if bright else "q1"
                elif thick_ == 2:
                    c = (("q3", "q2"), ("q2", "q1"), ("q1", "q0"))[2 - bright][r]
                elif r == 0 or r == thick_ - 1:
                    c = "q1" if bright else "q0"
                elif bright == 2:
                    c = "q4" if abs(i - length * 0.35) < length * 0.35 and r == thick_ // 2 else "q3"
                else:
                    c = "q2" if bright else "q1"
                cv.put(x, yy, c)
        if bright == 2 and eyes != "shut":                     # titik inti putih di dekat batang tegak
            cv.put(hx + s * 4, hy + 1 + int(round(tilt * 2 / float(length - 1))), "wh")


def grill(cv, hx, hy, mouth="closed"):
    """Grill mulut di bawah visor: tiga celah (tertutup) atau celah terbuka bercahaya (teriak)."""
    part(cv, "grill")
    if mouth == "shout":
        cv.fill(rect(hx - 4, hy + 8, 9, 5), OUT)
        cv.fill(rect(hx - 3, hy + 9, 7, 3), "q2")
        cv.fill(rect(hx - 2, hy + 10, 5, 1), "q4")
        for x in (hx - 1, hx + 1):
            cv.fill(rect(x, hy + 9, 1, 3), OUT)
        return
    for i, (w, dy) in enumerate(((7, 8), (5, 10), (3, 12))):  # lebar celah menyempit ke dagu
        cv.fill(rect(hx - w // 2, hy + dy, w, 1), OUT)
        cv.fill(rect(hx - w // 2, hy + dy + 1, w, 1), "q1")


def helm3(cv, hx, hy, eyes="look", mouth="closed", sway=0.0):
    """Helm penuh: kubah gelap bertepi V di atas wajah, garis V merah (alis), visor salib menyala di pelat wajah gelap, sayap pipi,
    cakram telinga mekanis, rahang meruncing dengan grill."""
    shell = poly(tr([(-6, -15), (6, -15), (11.5, -14), (15.5, -10), (17, -4), (16.5, 3), (13, 9), (9, 13.5), (5.5, 16), (-5.5, 16), (-9, 13.5),
                     (-13, 9), (-16.5, 3), (-17, -4), (-15.5, -10), (-11.5, -14)], hx, hy))
    wing_r = poly(tr([(15, -11), (21, -15), (26, -13), (22, -8), (25, -3), (18, -2), (15, -4)], hx, hy))
    solid3(cv, wing_r, IRON, OUT, depth=1, name="fin")
    px(cv, [(hx + 20 + i, hy - 11 - (i // 3)) for i in range(0, 5)], "q2", "fin")
    solid3(cv, shell, IRON, OUT, depth=2, name="helm")
    # pelat wajah gelap di bawah garis V (ujung luar tinggi, tengah rendah)
    vtop = lambda x: -9.0 + 6.0 * (1.0 - min(1.0, abs(x) / 16.0))
    plate = poly(tr([(-16, vtop(-16)), (-8, vtop(-8)), (0, vtop(0)), (8, vtop(8)), (16, vtop(16)), (13, 9), (9, 13.5), (5.5, 16), (-5.5, 16),
                     (-9, 13.5), (-13, 9)], hx, hy))
    part(cv, "visor_plate")
    cv.fill(plate - edge(plate), "n1")
    for x in range(-15, 16):                                  # garis V merah (alis): terang di atas, gelap di bawah
        y = int(round(vtop(x)))
        cv.put(hx + x, hy + y + 1, "q0")
    part(cv, "brow_band")
    for x in range(-15, 16):
        y = int(round(vtop(x)))
        cv.put(hx + x, hy + y - 1, "q3" if abs(x) % 4 else "q4")
        cv.put(hx + x, hy + y, "q2")
    # kubah: plat sensor di atas, jahitan miring, baut
    plate_top = poly(tr([(-3.5, -19), (3.5, -19), (5, -12), (-5, -12)], hx, hy))
    solid3(cv, plate_top, STEELL, OUT, depth=1, name="sensor")
    px(cv, vline(hx, hy - 18, hy - 13), "q3", "sensor")
    px(cv, [(hx - 6 - i, hy - 13 + i) for i in range(0, 5)] + [(hx + 6 + i, hy - 13 + i) for i in range(0, 5)], "n0", "helm")
    bolts(cv, [(hx - 10, hy - 10), (hx + 10, hy - 10), (hx - 14, hy - 6), (hx + 14, hy - 6)])
    for s in (-1, 1):                                         # cakram telinga mekanis, ventilasi pipi
        disc = ellipse(hx + s * 16.5, hy + 1.5, 3.2, 3.6)
        solid3(cv, disc, STEELL, OUT, depth=1, name="ear_disc")
        cv.put(hx + s * 16 + (0 if s > 0 else -1), hy + 1, "q3")
        px(cv, [(hx + s * 13, hy + 5 + i) for i in range(0, 3)] + [(hx + s * 12, hy + 5 + i) for i in range(0, 3)], "n0", "cheek")
        px(cv, [(hx + s * 11, hy + 8 + i) for i in range(0, 3)], "q1", "cheek")
    part(cv, "cheek")                                          # pelat pipi: jahitan tegak, sorot tipis, lampu indikator merah
    for s in (-1, 1):
        px(cv, vline(hx + s * 7, hy + 4, hy + 11), "n0")
        px(cv, vline(hx + s * 7 - s, hy + 4, hy + 10), "n2")
        px(cv, [(hx + s * 10, hy + 6)], "q2")
        px(cv, hline(hx + s * 7 + (1 if s > 0 else -4), hx + s * 7 + (4 if s > 0 else -1), hy + 12), "n0")
    visor(cv, hx, hy, eyes)
    grill(cv, hx, hy, mouth)
    part(cv, "chin")
    cv.fill(hline(hx - 3, hx + 3, hy + 15), "q1")


def collar(cv, tcx, tcy):
    """Gorget: pelat lebar di bawah helm dengan paku pendek di belakang (kiri)."""
    for bx, by, tx, ty, w in ((-14, -9, -25, -17, 4.5), (-15, -5, -28, -7, 5.0), (-14, -1, -25, 3, 4.5)):
        m = blade_poly((tcx + bx, tcy + by), (tcx + (bx + tx) / 2.0, tcy + (by + ty) / 2.0 - 1.5), (tcx + tx, tcy + ty), w, n=8, taper=0.7)
        solid3(cv, m, STEELL, OUT, depth=1, name="collar")
    g = poly([(tcx - 16, tcy - 10), (tcx + 16, tcy - 10), (tcx + 14, tcy - 3), (tcx + 7, tcy - 1), (tcx - 7, tcy - 1), (tcx - 14, tcy - 3)])
    solid3(cv, g, STEELL, OUT, depth=1, name="collar")
    px(cv, hline(tcx - 7, tcx + 7, tcy - 5), "q2", "collar")
    bolts(cv, [(tcx - 12, tcy - 7), (tcx + 11, tcy - 7)])


# ================================================================== badan
def chest(cv, tcx, tcy):
    """Dada hitam bergaris merah: pelat berbingkai merah tipis, garis V dari bahu ke tengah, garis tengah, inti cahaya."""
    m = poly([(tcx - 16.5, tcy - 11), (tcx + 16.5, tcy - 11), (tcx + 18, tcy - 4), (tcx + 14.5, tcy + 3.5), (tcx + 9, tcy + 6),
              (tcx - 9, tcy + 6), (tcx - 14.5, tcy + 3.5), (tcx - 18, tcy - 4)])
    body = solid3(cv, m, IRON, OUT, depth=2, name="chest")
    part(cv, "chest")
    cx = int(round(tcx))
    # bingkai merah tipis di dalam tepi
    ring2 = edge(body)
    cv.fill(ring2, "q1")
    # garis V dari bahu ke tengah, garis tengah
    for s in (-1, 1):
        for i in range(0, 12):
            x = cx + s * (14 - i)
            y = int(tcy - 6 + i * 0.8)
            cv.put(x, y, "q2")
    cv.fill(vline(cx, int(tcy + 2), int(tcy + 5)), "q2")
    # inti cahaya di tengah dada
    cv.fill(rect(cx - 1, int(tcy + 1), 3, 3), "q1")
    cv.put(cx, int(tcy + 2), "q4")
    cv.put(cx, int(tcy + 1), "q3")
    bolts(cv, [(tcx - 13, tcy - 8), (tcx + 12, tcy - 8), (tcx - 13, tcy + 1), (tcx + 12, tcy + 1)])
    return m


def belly(cv, tcx, tcy):
    """Perut: panel sisik heksagonal merah darah di bawah dada, sabuk dengan gesper bercahaya."""
    top = int(round(tcy + 5))
    m = poly([(tcx - 12, top - 1), (tcx + 12, top - 1), (tcx + 11, top + 4.5), (tcx - 11, top + 4.5)])
    solid3(cv, m, RED, ROUT, depth=1, name="belly")
    part(cv, "belly")
    for (x, y) in inner(m):
        row = y // 3
        off = 2 * (row % 2)
        lx, ly = (x + off) % 4, y % 3
        if lx == 0 or ly == 0:
            cv.put(x, y, "q0")
        elif lx == 1 and ly == 1:
            cv.put(x, y, "q3")
        else:
            cv.put(x, y, "q2" if (lx + ly) % 2 else "q1")
    belt = rect(int(round(tcx - 12)), top + 4, 24, 3)
    solid3(cv, belt, IRON, OUT, depth=1, name="belt")
    buckle = poly([(tcx - 3.5, top + 3), (tcx + 3.5, top + 3), (tcx + 4.5, top + 6), (tcx, top + 8), (tcx - 4.5, top + 6)])
    solid3(cv, buckle, REDB, ROUT, depth=1, name="buckle")
    part(cv, "buckle")
    cv.put(int(tcx), top + 5, "q4")
    return top + 7


def hip_plates(cv, tcx, by):
    """Pelat pinggul bersudut di kiri dan kanan (pengganti rok), ujung bergaris merah."""
    for s, w in ((-1, 7.5), (1, 6.5)):
        m = poly([(tcx + s * 5, by - 1), (tcx + s * (5 + w), by - 1), (tcx + s * (5 + w + 1.5), by + 4), (tcx + s * (5 + w - 2), by + 6), (tcx + s * 5, by + 3)])
        solid3(cv, m, IRON, OUT, depth=1, name="hip_plate")
        px(cv, [(int(tcx + s * (5 + w * 0.5)) + i, int(by + 4)) for i in range(-2, 3)], "q2", "hip_plate")


# ================================================================== pelindung bahu
def pauldron_big(cv, sx, sy):
    """Pelindung bahu raksasa (sisi kiri layar): cangkang bersudut, dua sirip tanduk tinggi, panel wajah mesin kecil (dua jendela mata merah),
    cincin berinti merah, tiga cakar merah di bawah."""
    fin1 = poly([(sx - 24, sy - 9), (sx - 29, sy - 29), (sx - 13, sy - 10)])
    fin2 = poly([(sx - 16, sy - 10), (sx - 9, sy - 35), (sx - 1, sy - 11)])
    solid3(cv, fin1, IRON, OUT, depth=1, name="horn_fin")
    solid3(cv, fin2, IRON, OUT, depth=1, name="horn_fin")
    part(cv, "horn_fin")
    cv.fill({(int(sx - 9), int(sy - 29 + i)) for i in range(0, 14)}, "q2")
    cv.fill({(int(sx - 26), int(sy - 22 + i)) for i in range(0, 8)}, "q2")
    shell = poly([(sx - 26, sy - 10), (sx - 3, sy - 12), (sx + 1, sy - 5), (sx + 1, sy + 7), (sx - 4, sy + 14), (sx - 22, sy + 14), (sx - 27, sy + 6)])
    body = solid3(cv, shell, IRON, OUT, depth=2, name="pauldron_big")
    part(cv, "pauldron_big")
    cv.fill(edge(body), "q1")
    # panel wajah mesin: bingkai, dua mata merah persegi, mulut
    face = rect(int(sx - 24), int(sy - 5), 12, 9)
    solid3(cv, face, STEELL, OUT, depth=1, name="face_panel")
    part(cv, "face_panel")
    for ex in (sx - 22, sx - 17):
        cv.fill(rect(int(ex), int(sy - 3), 3, 3), "q3")
        cv.put(int(ex) + 1, int(sy - 2), "wh")
    cv.fill(hline(int(sx - 22), int(sx - 16), int(sy + 1)), OUT)
    ring = ellipse(sx - 6, sy + 3, 4.6, 4.6)
    solid3(cv, ring, STEELL, OUT, depth=1, name="ring")
    part(cv, "ring")
    cv.fill(ellipse(sx - 6, sy + 3, 2.0, 2.0), "q2")
    cv.put(int(sx - 7), int(sy + 2), "q4")
    cv.fill({(x, int(sy + 9)) for (x, y) in body if y == int(sy + 9)}, OUT)
    bolts(cv, [(sx - 25, sy - 8), (sx - 5, sy - 9), (sx - 23, sy + 11), (sx - 4, sy + 11)])
    for bx in (-20, -13, -7):
        sp = poly([(sx + bx - 2.5, sy + 14), (sx + bx + 2.5, sy + 14), (sx + bx, sy + 21)])
        solid3(cv, sp, REDB, ROUT, depth=1, name="claw")


def pauldron_small(cv, sx, sy):
    """Pelindung bahu sisi senjata: cakram bundar berlapis cincin dengan paku kecil di atas."""
    sp = poly([(sx - 1.5, sy - 8.5), (sx + 2, sy - 15), (sx + 5, sy - 8.5)])
    solid3(cv, sp, IRON, OUT, depth=1, name="horn_fin")
    m = ellipse(sx + 2, sy + 1, 8.8, 9.6)
    body = solid3(cv, m, IRON, OUT, depth=2, name="pauldron_small")
    part(cv, "pauldron_small")
    cv.fill(edge(body), "q1")
    ring = ellipse(sx + 2, sy + 1, 5.0, 5.4)
    solid3(cv, ring, STEELL, OUT, depth=1, name="ring")
    part(cv, "ring")
    cv.fill(ellipse(sx + 2, sy + 1, 2.2, 2.4), "q2")
    cv.put(int(sx + 1), int(sy), "q4")
    bolts(cv, [(sx - 4, sy - 5), (sx + 8, sy - 5), (sx - 4, sy + 7), (sx + 8, sy + 7)])


# ================================================================== lengan, tangan, kaki
def gauntlet(cv, hx, hy, r=5.4):
    """Kepalan baja besar: cangkang terang, buku jari bergaris, manset merah, titik cahaya; kontras dengan lengan hitam supaya genggaman terbaca."""
    m = ellipse(hx, hy, r, r * 0.95)
    solid3(cv, m, STEELL, OUT, name="gauntlet")
    part(cv, "gauntlet")
    cv.fill({(int(hx) + dx, int(hy) - 2) for dx in range(-3, 4)}, OUT)                        # celah buku jari
    cv.fill({(int(hx) + dx, int(hy) - 3) for dx in range(-2, 3)}, "n4")
    cv.fill({(int(hx) - 4, int(hy) + d) for d in (0, 1, 2, 3)}, "q2")                         # manset merah
    cv.put(int(hx) + 1, int(hy) + 1, "q3")


def boot(cv, fx, fy, toe=1):
    """Sepatu besar: telapak lebar, penutup ujung terpisah, tiga cakar merah di depan, bibir merah di pergelangan."""
    sole = fy + 3.2
    m = poly([(fx - 6, sole - 9), (fx + 3.5, sole - 9), (fx + 5.5, sole - 5.5), (fx + 9 * toe, sole - 4), (fx + 10 * toe, sole - 0.2), (fx - 7, sole - 0.2)])
    solid3(cv, m, IRON, OUT, name="boot")
    part(cv, "boot")
    cap = poly([(fx + 4.5, sole - 5.2), (fx + 9 * toe, sole - 4), (fx + 10 * toe, sole - 0.4), (fx + 4.5, sole - 0.4)])
    solid3(cv, cap, STEELL, OUT, depth=1, name="boot")
    cv.fill({(int(fx - 5) + i, int(sole) - 8) for i in range(8)}, "q2")
    cv.fill({(int(fx - 6) + i, int(sole) - 2) for i in range(11)}, OUT)
    for k in range(3):                                                                         # cakar belakang
        sp = poly([(fx - 6.5, sole - 8 + k * 2.6), (fx - 6.5, sole - 5.6 + k * 2.6), (fx - 10.5, sole - 6.8 + k * 2.6)])
        solid3(cv, sp, REDB, ROUT, depth=1, name="claw")


def leg(cv, hip, foot, bend=-1):
    knee = ik(hip, (foot[0], foot[1]), THIGH, SHIN, bend)
    solid3(cv, thick([hip, knee], 4.7, 4.3), IRON, OUT, name="thigh")
    solid3(cv, thick([knee, (foot[0], foot[1] - 0.5)], 4.2, 3.9), IRON, OUT, name="shin")
    kc = poly([(knee[0] - 1, knee[1] - 4.5), (knee[0] + 4.6, knee[1] - 1.5), (knee[0] + 4.6, knee[1] + 2.5), (knee[0] - 1, knee[1] + 4.5),
               (knee[0] - 4.2, knee[1] + 1.5), (knee[0] - 4.2, knee[1] - 1.5)])
    solid3(cv, kc, STEELL, OUT, depth=1, name="knee")
    part(cv, "knee")
    cv.put(int(knee[0]), int(knee[1]), "q3")
    return knee


# ================================================================== ekor kipas panah
def tail_fan(cv, center, phase=0.0, rot=0.0, k=1.0):
    """Ekor kipas panah: dua busur panah merah menyala yang mengelilingi bagian belakang bahu (kiri dan atas), ujung panah mengikuti busur.
    center = pusat busur (di belakang pelindung bahu raksasa); phase menggoyang kipas; rot memutar; k menskala jari-jari."""
    cxx, cyy = center
    sw = math.sin(phase) * 4.0 + rot
    for kk, (r, n, size, a0, a1) in enumerate(((30.0 * k, 5, 11.0, 168.0, 248.0), (40.0 * k, 6, 12.5, 172.0, 258.0))):
        for i in range(n):
            t = (i + 0.5) / n
            th = math.radians(a0 + sw * 0.6 + (a1 - a0) * t + sw * t)
            x, y = cxx + math.cos(th) * r, cyy + math.sin(th) * r
            ang = th + math.pi / 2.0
            sz = size * (0.8 + 0.35 * t)
            m = arrow(x, y, ang, sz, sz * 0.9)
            lit, mid, dark = (("q4", "q3", "q2") if kk == 0 else ("q3", "q2", "q1"))
            part(cv, "tail_arrow")
            for (ax, ay) in m:                                   # tanpa garis tepi: tiga nada rata, terang di tepi atas-kiri, gelap di bawah-kanan
                c = mid
                if (ax - 1, ay) not in m or (ax, ay - 1) not in m:
                    c = lit
                elif (ax + 1, ay) not in m or (ax, ay + 1) not in m:
                    c = dark
                cv.put(ax, ay, c)


# ================================================================== pedang hitam raksasa berinti api merah
BLADE_START, BLADE_LEN, BLADE_HW = 8.0, 40.0, 9.5


def sword3(cv, sf, glow=1):
    """Pedang agung: bilah lebar hitam dengan inti api bergelombang (pinggir merah menyala, inti hitam), pelindung baja, gagang dan pomel.
    glow 0..2 mengatur kecerahan api. Semua digambar di sumbu u (sepanjang pedang) dan v (melintang) lalu diputar oleh `sf`."""
    ca, sa = sf.ca, sf.sa
    u0, L, hw = BLADE_START, BLADE_LEN, BLADE_HW
    tipu = u0 + L
    blade = poly(sf.pts([(u0, -hw), (tipu - 8, -hw), (tipu, 0), (tipu - 8, hw), (u0, hw)]))
    ring = edge(blade)
    part(cv, "weapon")
    for (x, y) in blade:
        dx, dy = x + 0.5 - sf.gx, y + 0.5 - sf.gy
        u = dx * ca + dy * sa
        v = -dx * sa + dy * ca
        av = abs(v)
        taper = hw if u < tipu - 8 else max(0.0, hw * (tipu - u) / 8.0)
        core = (4.0 + 1.5 * math.sin(u * 0.62)) * (min(1.0, taper / hw) if taper < hw else 1.0)
        if (x, y) in ring:
            c = ROUT
        elif av < core:                                          # inti hitam
            c = "n2" if av < 0.7 else "n1"
            if v < -0.7 and av > core - 1.3:
                c = "n3"
        elif av < core + 1.4:                                    # tepi inti: merah gelap
            c = "q0" if glow else "q1"
        else:                                                    # api
            if glow == 0:
                c = "q1"
            else:
                edge_d = taper - av
                c = "q3" if edge_d > 1.6 else "q2"
                if glow == 2 and abs(math.sin(u * 0.62 + 1.5)) > 0.86 and edge_d > 2.4:
                    c = "q4"
        cv.put(x, y, c)
    # kilatan api yang menjulur di luar tepi (deterministik)
    for u in (14, 22, 30, 37):
        for side in (-1, 1):
            if (u + side) % 3 == 0 and glow:
                for k in (0, 1):
                    x, y = sf.w(u + k * 0.4, side * (hw + 1.2 + k))
                    cv.put(int(x), int(y), "q2" if k == 0 else "q1")
    # lambang berlian merah di pangkal bilah
    for du, dv, c in ((12, 0, "q4"), (11, 0, "q3"), (13, 0, "q3"), (12, -1, "q2"), (12, 1, "q2")):
        x, y = sf.w(du, dv)
        cv.put(int(x), int(y), c if glow else "q1")
    # pelindung: palang hitam dengan ujung baja dan garis merah
    guard = poly(sf.pts([(3, -hw - 4.5), (u0, -hw - 4.5), (u0, hw + 4.5), (3, hw + 4.5)]))
    solid3(cv, guard, IRON, OUT, depth=1, name="weapon")
    for v in range(-int(hw + 3), int(hw + 3) + 1):
        x, y = sf.w(5.5, v)
        cv.put(int(x), int(y), "q2" if abs(v) < hw + 1 else "n4")
    for s in (-1, 1):
        for du in (3.5, 6.5):
            x, y = sf.w(du, s * (hw + 4))
            cv.put(int(x), int(y), "n4")
    grip = poly(sf.pts([(-12, -2.0), (3, -2.0), (3, 2.0), (-12, 2.0)]))
    solid3(cv, grip, IRON, OUT, depth=1, name="weapon")
    for u in (-9, -5, -1):
        x, y = sf.w(u, 0)
        cv.put(int(x), int(y), "q2")
    pom = ellipse(*sf.w(-14.5, 0), 3.0, 3.0)
    solid3(cv, pom, STEELL, OUT, depth=1, name="weapon")
    x, y = sf.w(-14.5, 0)
    cv.put(int(x), int(y), "q3")


# ================================================================== pose dan geometri
def pose(**kw):
    p = dict(cx=64, lean=0.0, crouch=0.0, dy=0.0, hdx=0.0, hdy=0.0,
             fl=(-9.0, 0.0), fr=(9.0, 0.0),
             grip=None, ang=0.0, sword_layer="front", lh_u=-6.5, lh=None, rh=None, glow=1,
             eyes="look", mouth="closed", sway=0.0, tail_phase=0.0, tail_rot=0.0, tail_k=1.0, twist=0.0, fx=(),
             legs_front=False, toe_l=1, toe_r=1)
    p.update(kw)
    return p


def geometry(p):
    cx, lean = p["cx"], p["lean"]
    hip_y = FLOOR - 3 - LEG + p["crouch"] + p["dy"]
    tcy = hip_y - 14.0
    tcx = cx + lean * 0.5
    g = dict(hip_y=hip_y, tcx=tcx, tcy=tcy,
             sh_l=(tcx - SH_X + p["twist"], tcy - SH_Y), sh_r=(tcx + SH_X + p["twist"] * 0.3, tcy - SH_Y),
             head=(tcx + lean * 0.4 + p["hdx"], tcy - HEAD_DY + p["hdy"]),
             hip_l=(cx - 6.5, hip_y), hip_r=(cx + 6.5, hip_y))
    g["foot_l"] = (cx + p["fl"][0], FLOOR - 3 - p["fl"][1])
    g["foot_r"] = (cx + p["fr"][0], FLOOR - 3 - p["fr"][1])
    if p["grip"] is not None:
        sf = SwordFrame(p["grip"][0], p["grip"][1], p["ang"])
        g["sword"] = sf
        g["rh"] = p["rh"] or sf.w(0, 0)
        g["lh"] = p["lh"] or sf.w(p["lh_u"], 0)
    else:
        g["sword"] = None
        g["rh"] = p["rh"]
        g["lh"] = p["lh"]
    reach = UPPER + FORE - 0.4
    for side, sh in (("lh", g["sh_l"]), ("rh", g["sh_r"])):
        h = g[side]
        if h is not None:
            d = math.hypot(h[0] - sh[0], h[1] - sh[1])
            if d > reach:
                g[side] = (sh[0] + (h[0] - sh[0]) * reach / d, sh[1] + (h[1] - sh[1]) * reach / d)
    return g


def draw_hero(cv, p):
    """Urutan: ekor, pedang (bila di belakang), kaki, dada, perut, pelat pinggul, kerah, jambul, pelindung bahu raksasa, lengan,
    pedang (di depan), sarung tangan, helm, efek, rim light."""
    g = geometry(p)
    tcx, tcy = g["tcx"], g["tcy"]
    tail_fan(cv, (g["sh_l"][0] - 8.0, g["sh_l"][1] + 4.0), p["tail_phase"], p["tail_rot"], p["tail_k"])
    if g["sword"] and p["sword_layer"] == "back":
        sword3(cv, g["sword"], p["glow"])
    if not p["legs_front"]:
        _legs(cv, g, p)
    chest(cv, tcx, tcy)
    by = belly(cv, tcx, tcy)
    hip_plates(cv, tcx, by - 2)
    if p["legs_front"]:
        _legs(cv, g, p)
    collar(cv, tcx, tcy)
    hx, hy = g["head"]
    ihx, ihy = int(round(hx)), int(round(hy))
    crest(cv, ihx, ihy, p["sway"])
    arms = []
    for side, sh, hand in (("l", g["sh_l"], g["lh"]), ("r", g["sh_r"], g["rh"])):
        if hand is None:
            continue
        elbow = ik(sh, hand, UPPER, FORE, 1)
        arms.append((side, sh, elbow, hand))
        solid3(cv, thick([sh, elbow], 3.9, 3.6), IRON, OUT, depth=1, name="upper_arm")
    pauldron_big(cv, g["sh_l"][0], g["sh_l"][1])
    pauldron_small(cv, g["sh_r"][0], g["sh_r"][1])
    for side, sh, elbow, hand in arms:
        fore = thick([(elbow[0] + (hand[0] - elbow[0]) * 0.15, elbow[1] + (hand[1] - elbow[1]) * 0.15),
                      (elbow[0] + (hand[0] - elbow[0]) * 0.88, elbow[1] + (hand[1] - elbow[1]) * 0.88)], 4.0, 3.7)
        solid3(cv, fore, IRON, OUT, name="vambrace")
        solid3(cv, ellipse(elbow[0], elbow[1], 3.3, 3.3), STEELL, OUT, name="elbow")
    if g["sword"] and p["sword_layer"] == "front":
        sword3(cv, g["sword"], p["glow"])
    for side, sh, elbow, hand in arms:
        gauntlet(cv, hand[0], hand[1])
    helm3(cv, ihx, ihy, p["eyes"], p["mouth"], p["sway"])
    for f in p["fx"]:
        f(cv, g)
    rim_pass3(cv)
    return g


def _legs(cv, g, p):
    for hip, foot, bend, toe in ((g["hip_l"], g["foot_l"], -1, p["toe_l"]), (g["hip_r"], g["foot_r"], -1, p["toe_r"])):
        leg(cv, hip, foot, bend)
        boot(cv, foot[0], foot[1], toe)


def render_pose(p):
    cv = PartCanvas()
    draw_hero(cv, p)
    return floor_clip(cv)


# ------------------------------------------------------------------ tiga pose kunci
def pose_idle():
    """Berdiri tegak, pedang agung ditancapkan di sisi kanan, satu tangan di gagang setinggi bahu."""
    return pose(cx=66, lean=1.0, grip=(94, 47), ang=82.0, lh=(66 - 14, 74), tail_phase=0.4, tail_k=0.82, eyes="look", mouth="closed")


def pose_run_peak():
    """Puncak langkah: melayang, badan condong, kaki depan terangkat menekuk, kaki belakang terlempar; pedang diacungkan ke depan-atas."""
    cx = 60
    p = pose(cx=cx, lean=12.0, crouch=3.0, dy=-6.0, fl=(-16.0, 4.0), fr=(13.0, 12.0), eyes="angry", mouth="closed", tail_phase=1.8, tail_rot=8.0,
             tail_k=0.82, hdy=1.0, hdx=2.0)
    p.update(grip=(cx + 31.0, 60.0), ang=-50.0, lh=(cx + 2.0, 70.0), sword_layer="front")
    return p


def pose_smash_hit():
    """Tumbukan attack-smash: lunge rendah, ujung bilah menghantam sisi atas balok kayu di lantai."""
    cx = 48
    p = pose(cx=cx, lean=10.0, crouch=6.0, fl=(-14.0, 0.0), fr=(15.0, 0.0), eyes="rage", mouth="shout", tail_phase=2.6, tail_rot=10.0, tail_k=0.64, hdy=0.0, twist=5.0)
    gx, gy, ang = 81.0, 58.0, 40.0
    p.update(grip=(gx, gy), ang=ang, lh=(cx + 1.0, 72.0), glow=2)
    sf = SwordFrame(gx, gy, ang)
    ux = (FLOOR - 11 - gy) / math.sin(math.radians(ang))
    hx, hy = sf.w(ux, 0)
    p["fx"] = [lambda cv, g: H.fx_dust(cv, hx + 3, FLOOR - 1, 1, 1.0),
               lambda cv, g: H.wood_block(cv, hx + 3, FLOOR, 16, 11),
               lambda cv, g: H.fx_smear(cv, gx, gy, 34, -34, 40, 2),
               lambda cv, g: H.fx_burst(cv, hx - 1, hy - 2, 6),
               lambda cv, g: H.fx_chips(cv, hx + 1, FLOOR - 10, 1, seed=3, n=9, power=1.0)]
    return p


KEYPOSES = {"idle": pose_idle, "run": pose_run_peak, "attack-smash": pose_smash_hit}
