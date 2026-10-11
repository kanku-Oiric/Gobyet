"""Berserker Hero v2 (kostum `berserker-hero`, kanvas 128x96): revisi total body dan zirah atas arahan pemilik.

Arah (dari pemilik, referensi gambar tidak disimpan di repo):
  - body mengikuti proporsi referensi pertama: chibi, kepala dan helm sangat besar tanpa leher, bahu lebar, satu pelindung bahu
    raksasa bergaya mesin di sisi kiri layar dengan sirip tanduk dan palka, bahu satunya bundar, kaki pendek bersepatu besar,
    perut berpola sisik heksagonal, dan ekor kipas panah yang melengkung di belakang;
  - jambul, pita alis berbentuk V, dan bentuk helm dipertahankan, tetapi corak dan warnanya mengikuti referensi kedua
    (hitam dan merah darah); kesan mekanis dipertahankan dan dibuat sedikit modern (panel, baut, ventilasi, strip cahaya).
Ini bentuk dan nada warna turunan, bukan salinan piksel: semua bentuk digambar dari kode dan bagian-bagiannya milik desain ini.

Yang tetap dari v1: kepala Gobyet (`hero.head_hd`: bulu cokelat, telinga, mata, hidung, mulut) terlihat penuh di semua frame, kanvas 128x96,
pustaka rig (`PartCanvas`, `solid3`, `rim_pass`, `SwordFrame`), tanpa darah (merah hanya warna dan corak, bukan luka).

Fase Body: bentuk badan, kepala, dan helm. Pedang di sini hanya PENGGANTI (balok polos) agar pose terbaca; desain pedang dan corak zirah
penuh dikerjakan di Fase Armor.
"""
import math

import monkey
from monkey import ellipse, rect, edge, chain

import hero as H
from hero import PartCanvas, part, poly, thick, bezier, inner, solid3, rim_pass, ik, head_hd, SwordFrame, floor_clip, FLOOR

W, HGT = H.W, H.H

# ------------------------------------------------------------------ palet tambahan v2 (kunci baru; kunci v1 dipakai ulang)
HERO2_PAL = {
    "k0": (16, 14, 20),                                                                      # garis tepi besi: hitam turunan (bukan hitam murni)
    "k1": (30, 28, 36), "k2": (52, 50, 60), "k3": (86, 84, 98), "k4": (140, 138, 156),      # besi hitam netral: bayangan, dasar, sorotan, baja terang
    "dr": (74, 8, 22), "mr": (130, 12, 32), "br": (196, 24, 38), "hr": (240, 64, 56),     # merah darah: gelap, tengah, terang, menyala
    "gl": (255, 150, 112),                                                                   # inti cahaya merah (strip cahaya)
}
monkey.PAL_HERO.update({k: v for k, v in HERO2_PAL.items() if k not in monkey.PAL_HERO})
assert not set(HERO2_PAL) & (set(monkey.PAL) | set(monkey.PAL_EXT) | set(H.HERO_PAL)), "kunci palet hero2 bentrok"

IRON, STEELL, FUR, FACE = ("k1", "k2", "k3"), ("k2", "k3", "k4"), H.FUR, H.FACE
OUT = "k0"                                                                                   # garis tepi besi
RED, REDB = ("dr", "mr", "br"), ("mr", "br", "hr")

# ------------------------------------------------------------------ ukuran badan (chibi)
UPPER, FORE = 8.0, 8.5            # lengan atas dan bawah
LEG = 12.0                        # pinggul ke pusat pergelangan saat berdiri
THIGH, SHIN = 5.9, 5.5
SH_X, SH_Y = 15.5, 9.0            # sendi bahu: +- SH_X dari tengah dada, SH_Y di atas pusat dada
HEAD_DY = 24.0                    # pusat kepala di atas pusat dada


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
    """Kepala panah (chevron penuh): ujung di depan, dua sayap lebar di belakang, takik dangkal."""
    ca, sa = math.cos(ang), math.sin(ang)
    tip = (cx + ca * L * 0.55, cy + sa * L * 0.55)
    back = (cx - ca * L * 0.45, cy - sa * L * 0.45)
    wl = (back[0] - sa * w * 0.5, back[1] + ca * w * 0.5)
    wr = (back[0] + sa * w * 0.5, back[1] - ca * w * 0.5)
    notch = (cx - ca * L * 0.22, cy - sa * L * 0.22)
    mid_l = (cx - sa * w * 0.22, cy + ca * w * 0.22)
    mid_r = (cx + sa * w * 0.22, cy - ca * w * 0.22)
    return poly([tip, wl, notch, wr]) | poly([tip, mid_l, mid_r])


def rim_pass2(cv):
    """Rim light 1 px: piksel besi tepat di bawah garis tepi besi (tepi atas bagian besi) menjadi baja terang."""
    iron = set(IRON) | set(STEELL)
    for (x, y), c in list(cv.px.items()):
        if c in iron and c != "k4" and cv.px.get((x, y - 1)) == OUT:
            cv.px[(x, y)] = "k4"
    return cv


def flat(cv, mask, base, outline, light=None, name=None):
    """Isi rata dengan garis tepi 1 px (untuk bentuk kecil yang tidak muat tiga nada), sorotan opsional di tepi atas-kiri."""
    if name:
        part(cv, name)
    ring = edge(mask)
    body = mask - ring
    cv.fill(body, base)
    if light:
        cv.fill({(x, y) for (x, y) in body if (x - 1, y) in ring or (x, y - 1) in ring}, light)
    cv.fill(ring, outline)
    return body


def bolts(cv, pts, c="k4"):
    part_name = cv.part
    for (x, y) in pts:
        cv.put(int(x), int(y), c)
    cv.part = part_name


# ================================================================== helm dan kepala (koordinat lokal: (0,0) = pusat kepala)
def tr(pts, cx, cy):
    return [(cx + x, cy + y) for x, y in pts]


CREST = (   # (pangkal, kendali, ujung, lebar pangkal): bilah jambul menyebar ke belakang-atas dan ke atas
    ((-4, -12), (-17, -25), (-30, -26), 8.5),
    ((-2, -13), (-9, -28), (-19, -32), 8.5),
    ((1, -13), (0, -29), (-5, -35), 8.0),
    ((4, -12), (10, -26), (9, -33), 7.0),
    ((7, -10), (17, -20), (22, -27), 6.0),
)


def crest(cv, cx, cy, rage=False):
    """Jambul bilah merah darah (digambar di belakang kepala)."""
    for k, (p0, p1, p2, w0) in enumerate(CREST):
        m = blade_poly(*[(cx + x, cy + y) for x, y in (p0, p1, p2)], w0, taper=0.6)
        tone = RED if k % 2 == 0 else REDB
        solid3(cv, m, tone, "o1", depth=1, name="crest")
        # urat terang di sepanjang bilah
        mid = bezier((cx + p0[0], cy + p0[1]), (cx + p1[0], cy + p1[1]), (cx + p2[0], cy + p2[1]), 14)
        for i in range(2, 10):
            x, y = mid[i]
            if (int(x), int(y)) in m and (int(x), int(y) + 1) in m:
                cv.put(int(x), int(y), "hr" if k % 2 else "br")


def helm2(cv, cx, cy, rage=False):
    """Helm mesin dipakai seperti tudung di atas kepala Gobyet: tutup dahi, pita alis V dengan strip cahaya, sirip samping, pipi, kerah.
    Wajah (mata, hidung, mulut) dan telinga tidak pernah tertutup."""
    # tutup dahi: di atas garis V
    cap = poly(tr([(-16.5, -3.5), (-17.5, -9), (-14.5, -15), (-8, -18.5), (3, -19), (11, -16.5), (16, -11), (17, -4), (13, -8.5), (7, -11.5),
                   (0, -13), (-7, -11.5), (-13, -8.5)], cx, cy))
    solid3(cv, cap, IRON, OUT, depth=2, name="helm_cap")
    # pita alis V (lebih tebal) dengan strip cahaya merah di tengahnya
    band = poly(tr([(-18, -3.5), (-15, -9.5), (0, -14.5), (15, -9.5), (18, -3.5), (18, 0.5), (15, -4), (0, -9.2), (-15, -4), (-18, 0.5)], cx, cy))
    solid3(cv, band, STEELL, OUT, depth=1, name="brow_band")
    part(cv, "brow_glow")
    for x in range(-14, 15):
        yy = -11.0 + 4.6 * (abs(x) / 15.0)
        cv.put(int(round(cx + x)), int(round(cy + yy)), "hr")
    for x in (-1, 0, 1):
        cv.put(int(cx + x), int(round(cy - 11.0)), "gl")
    # sensor di tengah dahi: blok kecil bergaris merah
    part(cv, "sensor")
    cv.fill(rect(int(cx) - 2, int(cy) - 18, 5, 4), "k2")
    cv.fill(rect(int(cx) - 2, int(cy) - 18, 5, 1), "k3")
    cv.fill(rect(int(cx), int(cy) - 17, 1, 8), "hr")                                            # garis tegak: bersama pita V membentuk salib merah di dahi
    # baut di tutup dahi
    part(cv, "rivet")
    bolts(cv, [(cx - 10, cy - 9), (cx + 9, cy - 9), (cx - 13, cy - 13), (cx + 12, cy - 13)])
    # sirip samping (belakang besar, depan kecil), di atas telinga
    fin_b = poly(tr([(-16, -7), (-24, -13), (-34, -13), (-29, -6), (-33, 0), (-22, 0), (-16, -1)], cx, cy))
    solid3(cv, fin_b, IRON, OUT, depth=1, name="fin")
    cv.fill({(int(cx - 22 + dx), int(cy - 8 + dy)) for dx in range(-3, 4) for dy in range(0, 1)}, "br")
    fin_f = poly(tr([(16, -7), (22, -13), (28, -12), (25, -6), (27, -2), (19, -1), (16, -1)], cx, cy))
    solid3(cv, fin_f, IRON, OUT, depth=1, name="fin")
    cv.fill({(int(cx + 22 + dx), int(cy - 7)) for dx in range(-2, 3)}, "br")
    # pelat pipi di bawah telinga, membingkai wajah
    for s, pts in ((-1, [(-17.5, 7.5), (-14.5, 13.5), (-8, 16.5), (-10.5, 10), (-12, 5.5)]),
                   (1, [(17.5, 7.5), (14.5, 13.5), (8, 16.5), (10.5, 10), (12, 5.5)])):
        cheek = poly(tr(pts, cx, cy))
        solid3(cv, cheek, IRON, OUT, depth=1, name="cheek")
        bolts(cv, [(cx + s * 14, cy + 10)])
    # pelindung dagu: pelat sempit di bawah wajah menyambung ke kerah
    chin = poly(tr([(-9, 13.5), (9, 13.5), (11, 17.5), (6, 20), (-6, 20), (-11, 17.5)], cx, cy))
    solid3(cv, chin, IRON, OUT, depth=1, name="chin")
    part(cv, "chin_glow")
    cv.fill({(int(cx + x), int(cy + 16.5)) for x in range(-3, 4)}, "br")


def collar(cv, tcx, tcy):
    """Kerah: pelat gorget lebar di bawah kepala dengan tiga paku pendek di belakang (kiri) dan satu di depan, baja bukan bulu."""
    for bx, by, tx, ty, w in ((-13, -12, -23, -21, 4.5), (-14, -9, -26, -12, 5.0), (-12, -6, -23, -3, 4.5), (13, -11, 21, -18, 4.0)):
        m = blade_poly((tcx + bx, tcy + by), (tcx + (bx + tx) / 2.0, tcy + (by + ty) / 2.0 - 1.5), (tcx + tx, tcy + ty), w, n=8, taper=0.7)
        solid3(cv, m, STEELL, OUT, depth=1, name="collar")
    g = poly([(tcx - 15, tcy - 13), (tcx + 15, tcy - 13), (tcx + 13, tcy - 6.5), (tcx + 7, tcy - 4), (tcx - 7, tcy - 4), (tcx - 13, tcy - 6.5)])
    solid3(cv, g, STEELL, OUT, depth=1, name="collar")
    part(cv, "collar")
    cv.fill({(int(tcx + x), int(tcy - 8)) for x in range(-6, 7)}, "br")
    bolts(cv, [(tcx - 11, tcy - 10), (tcx + 10, tcy - 10)])


# ================================================================== badan
def chest(cv, tcx, tcy):
    """Dada: pelat lebar bergaris tengah, dua ventilasi bercahaya merah, baut; bahu menyambung ke sini."""
    m = poly([(tcx - 15.5, tcy - 12), (tcx + 15.5, tcy - 12), (tcx + 17.5, tcy - 5), (tcx + 14, tcy + 2.5), (tcx + 9, tcy + 5.5),
              (tcx - 9, tcy + 5.5), (tcx - 14, tcy + 2.5), (tcx - 17.5, tcy - 5)])
    body = solid3(cv, m, IRON, OUT, depth=2, name="chest")
    part(cv, "chest")
    cx = int(round(tcx))
    cv.fill({(cx, y) for (x, y) in body if x == cx and y > tcy - 10}, OUT)
    cv.fill({(cx - 1, y) for (x, y) in body if x == cx - 1 and y > tcy - 10}, "k3")
    # pelat dada atas: dua pelat miring bertemu di tengah (kesan wajah tengkorak yang disederhanakan: dua celah mata)
    for s in (-1, 1):
        part(cv, "vent")
        for dy in (0, 1):
            cv.fill({(int(tcx + s * 7 + dx), int(tcy - 3 + dy)) for dx in range(-3, 4)}, OUT)
        cv.fill({(int(tcx + s * 7 + dx), int(tcy - 3)) for dx in range(-2, 3)}, "mr")
        cv.fill({(int(tcx + s * 7 + dx), int(tcy - 3)) for dx in range(-1, 2)}, "hr")
    part(cv, "chest")
    cv.fill({(x, int(tcy + 1)) for (x, y) in body if y == int(tcy + 1) and abs(x - tcx) > 1}, OUT)
    bolts(cv, [(tcx - 13, tcy - 9), (tcx + 12, tcy - 9), (tcx - 11, tcy + 0), (tcx + 10, tcy + 0), (tcx - 3, tcy - 9), (tcx + 3, tcy - 9)])
    return m


def belly(cv, tcx, tcy):
    """Perut: panel sisik heksagonal (sel 4x3 bergeser tiap baris) merah darah di bawah dada, sabuk dengan gesper bercahaya."""
    top = int(round(tcy + 5))
    m = poly([(tcx - 12, top - 1), (tcx + 12, top - 1), (tcx + 11, top + 4.5), (tcx - 11, top + 4.5)])
    solid3(cv, m, RED, "o1", depth=1, name="belly")
    part(cv, "belly")
    for (x, y) in inner(m):
        row = y // 3
        off = 2 * (row % 2)
        lx, ly = (x + off) % 4, y % 3
        if lx == 0 or ly == 0:
            cv.put(x, y, "dr")
        elif lx == 1 and ly == 1:
            cv.put(x, y, "hr")
        else:
            cv.put(x, y, "br" if (lx + ly) % 2 else "mr")
    belt = rect(int(round(tcx - 12)), top + 4, 24, 3)
    solid3(cv, belt, IRON, OUT, depth=1, name="belt")
    buckle = poly([(tcx - 3.5, top + 3), (tcx + 3.5, top + 3), (tcx + 4.5, top + 6), (tcx, top + 8), (tcx - 4.5, top + 6)])
    solid3(cv, buckle, REDB, "o1", depth=1, name="buckle")
    part(cv, "buckle")
    cv.put(int(tcx), top + 5, "gl")
    return top + 7


def hip_plates(cv, tcx, by):
    """Pelat pinggul bersudut di kiri dan kanan (pengganti rok)."""
    for s, w in ((-1, 7.5), (1, 6.5)):
        m = poly([(tcx + s * 5, by - 1), (tcx + s * (5 + w), by - 1), (tcx + s * (5 + w + 1.5), by + 4), (tcx + s * (5 + w - 2), by + 6), (tcx + s * 5, by + 3)])
        solid3(cv, m, IRON, OUT, depth=1, name="hip_plate")
        bolts(cv, [(tcx + s * (5 + w * 0.5), by + 1)])


# ================================================================== pelindung bahu
def pauldron_big(cv, sx, sy):
    """Pelindung bahu raksasa bergaya mesin (sisi kiri layar): cangkang bersudut, dua sirip tanduk tinggi, palka berventilasi, cincin berinti
    merah, paku di bawah."""
    fin1 = poly([(sx - 24, sy - 9), (sx - 28, sy - 28), (sx - 13, sy - 10)])
    fin2 = poly([(sx - 16, sy - 10), (sx - 9, sy - 34), (sx - 1, sy - 11)])
    solid3(cv, fin1, STEELL, OUT, depth=1, name="horn_fin")
    solid3(cv, fin2, STEELL, OUT, depth=1, name="horn_fin")
    part(cv, "horn_fin")
    cv.fill({(int(sx - 9), int(sy - 28 + i)) for i in range(0, 12)}, "br")                  # urat merah di sirip tinggi
    shell = poly([(sx - 25, sy - 10), (sx - 3, sy - 12), (sx + 1, sy - 5), (sx + 1, sy + 7), (sx - 4, sy + 14), (sx - 22, sy + 14), (sx - 26, sy + 6)])
    body = solid3(cv, shell, IRON, OUT, depth=2, name="pauldron_big")
    part(cv, "pauldron_big")
    hatch = rect(int(sx - 23), int(sy - 4), 11, 7)
    solid3(cv, hatch, STEELL, OUT, depth=1, name="hatch")
    part(cv, "hatch")
    for i in range(3):
        cv.fill(rect(int(sx - 21) + i * 3, int(sy - 2), 2, 4), OUT)
        cv.fill(rect(int(sx - 21) + i * 3, int(sy - 1), 1, 2), "hr")
    ring = ellipse(sx - 6, sy + 3, 4.6, 4.6)
    solid3(cv, ring, STEELL, OUT, depth=1, name="ring")
    part(cv, "ring")
    cv.fill(ellipse(sx - 6, sy + 3, 2.0, 2.0), "br")
    cv.put(int(sx - 7), int(sy + 2), "gl")
    cv.fill({(x, int(sy + 9)) for (x, y) in body if y == int(sy + 9)}, OUT)
    bolts(cv, [(sx - 23, sy - 8), (sx - 5, sy - 9), (sx - 23, sy + 11), (sx - 4, sy + 11)])
    for k, bx in enumerate((-20, -13, -7)):
        sp = poly([(sx + bx - 2.5, sy + 14), (sx + bx + 2.5, sy + 14), (sx + bx, sy + 20)])
        solid3(cv, sp, REDB, "o1", depth=1, name="spike")


def pauldron_small(cv, sx, sy):
    """Pelindung bahu sisi senjata: cakram bundar berlapis cincin dengan paku kecil di atas."""
    sp = poly([(sx - 1.5, sy - 8.5), (sx + 2, sy - 15), (sx + 5, sy - 8.5)])
    solid3(cv, sp, STEELL, OUT, depth=1, name="horn_fin")
    m = ellipse(sx + 2, sy + 1, 8.6, 9.4)
    body = solid3(cv, m, IRON, OUT, depth=2, name="pauldron_small")
    part(cv, "pauldron_small")
    ring = ellipse(sx + 2, sy + 1, 5.0, 5.4)
    solid3(cv, ring, STEELL, OUT, depth=1, name="ring")
    part(cv, "ring")
    cv.fill(ellipse(sx + 2, sy + 1, 2.2, 2.4), "mr")
    cv.put(int(sx + 1), int(sy), "hr")
    bolts(cv, [(sx - 4, sy - 5), (sx + 8, sy - 5), (sx - 4, sy + 7), (sx + 8, sy + 7)])


# ================================================================== lengan, tangan, kaki
def gauntlet(cv, hx, hy, r=4.9):
    m = ellipse(hx, hy, r, r * 0.95)
    solid3(cv, m, IRON, OUT, name="gauntlet")
    part(cv, "gauntlet")
    cv.fill({(int(hx) + dx, int(hy) - 2) for dx in range(-2, 3)}, "k3")                       # buku jari
    cv.fill({(int(hx) - 3, int(hy) + d) for d in (1, 2, 3)}, "mr")                          # manset merah
    cv.put(int(hx) + 2, int(hy) - 1, "k4")


def boot(cv, fx, fy, toe=1):
    """Sepatu besar: telapak lebar, penutup ujung terpisah, tumit, tiga paku merah di belakang pergelangan."""
    sole = fy + 3.2
    m = poly([(fx - 6, sole - 9), (fx + 3.5, sole - 9), (fx + 5.5, sole - 5.5), (fx + 9 * toe, sole - 4), (fx + 10 * toe, sole - 0.2), (fx - 7, sole - 0.2)])
    solid3(cv, m, IRON, OUT, name="boot")
    part(cv, "boot")
    cap = poly([(fx + 4.5, sole - 5.2), (fx + 9 * toe, sole - 4), (fx + 10 * toe, sole - 0.4), (fx + 4.5, sole - 0.4)])
    solid3(cv, cap, STEELL, OUT, depth=1, name="boot")
    cv.fill({(int(fx - 5) + i, int(sole) - 8) for i in range(8)}, "br")                      # bibir merah di pergelangan
    cv.fill({(int(fx - 6) + i, int(sole) - 2) for i in range(11)}, OUT)                          # garis telapak
    for k in range(3):                                                                         # paku belakang
        sp = poly([(fx - 6.5, sole - 8 + k * 2.6), (fx - 6.5, sole - 5.6 + k * 2.6), (fx - 10.5, sole - 6.8 + k * 2.6)])
        solid3(cv, sp, REDB, "o1", depth=1, name="spike")


def leg(cv, hip, foot, bend=-1):
    knee = ik(hip, (foot[0], foot[1]), THIGH, SHIN, bend)
    solid3(cv, thick([hip, knee], 4.7, 4.3), IRON, OUT, name="thigh")
    solid3(cv, thick([knee, (foot[0], foot[1] - 0.5)], 4.2, 3.9), IRON, OUT, name="shin")
    kc = poly([(knee[0] - 1, knee[1] - 4.5), (knee[0] + 4.6, knee[1] - 1.5), (knee[0] + 4.6, knee[1] + 2.5), (knee[0] - 1, knee[1] + 4.5),
               (knee[0] - 4.2, knee[1] + 1.5), (knee[0] - 4.2, knee[1] - 1.5)])
    solid3(cv, kc, STEELL, OUT, depth=1, name="knee")
    part(cv, "knee")
    cv.put(int(knee[0]), int(knee[1]), "br")
    # piston tipis di sisi depan betis
    m = chain([(knee[0] + 3.2, knee[1] + 3), (foot[0] + 3.2, foot[1] - 4)], 0.5)
    cv.fill(m, "k4")
    return knee


# ================================================================== ekor kipas panah
def tail_fan(cv, base, phase=0.0, rot=0.0):
    """Ekor mekanis: batang bersegmen di belakang pinggul, lalu kipas panah merah: tiga busur sepusat (jari-jari 30, 38, 46) di sekitar
    pangkal ekor, panah menghadap searah busur (naik di belakang, lalu melengkung ke depan di atas). phase menggoyang kipas."""
    bx, by = base
    sw = math.sin(phase) * 5.0 + rot                             # derajat (rot: putar seluruh kipas; negatif = lebih mendatar ke belakang)
    stem = bezier((bx, by), (bx - 6, by + 2), (bx - 11, by - 4), 10)
    solid3(cv, thick(stem, 2.4, 2.0), IRON, OUT, depth=1, name="tail_stem")
    for i in (3, 6, 9):
        x, y = stem[i]
        cv.put(int(x), int(y), "br")
    px, py = bx - 3.0, by - 3.0                                   # pusat busur
    for k, (r, n, size) in enumerate(((35.0, 4, 13.0), (45.0, 5, 14.0))):
        a0, a1 = 184.0 + sw, 262.0 + sw * 1.5
        for i in range(n):
            t = (i + 0.5) / n
            th = math.radians(a0 + (a1 - a0) * t)
            x, y = px + math.cos(th) * r, py + math.sin(th) * r
            ang = th + math.pi / 2.0                              # arah singgung (naik di kiri, ke kanan di atas)
            sz = size * (0.78 + 0.38 * t)
            m = arrow(x, y, ang, sz, sz * 0.8)
            base_c = ("mr", "br", "hr")[min(2, int(t * 3))]
            flat(cv, m, base_c, "o1", light="hr" if t > 0.5 else "br", name="tail_arrow")


# ================================================================== pose dan geometri
def pose(**kw):
    p = dict(cx=70, lean=0.0, crouch=0.0, dy=0.0, hdx=0.0, hdy=0.0, tilt=0,
             fl=(-9.0, 0.0), fr=(9.0, 0.0),
             grip=None, ang=0.0, sword_layer="front", lh_u=-6.5, lh=None, rh=None,
             eyes="look", brows="angry", mouth="frown", face="F", rage=False,
             sway=0.0, lift=0.0, flare=0.0, tail_phase=0.0, tail_rot=0.0, twist=0.0, head_front=True, fx=(),
             legs_front=False, toe_l=1, toe_r=1)
    p.update(kw)
    return p


def geometry(p):
    cx, lean = p["cx"], p["lean"]
    hip_y = FLOOR - 3 - LEG + p["crouch"] + p["dy"]
    tcy = hip_y - 12.5
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


# ------------------------------------------------------------------ pedang PENGGANTI (Fase Body): balok polos agar pose terbaca
SWORD_LEN = 56.0


def weapon_placeholder(cv, sf):
    """Pengganti: bilah lebar polos (12 px) dengan ujung runcing, pelindung, dan gagang. BUKAN desain akhir (Fase Armor)."""
    hw = 6.0
    blade = poly(sf.pts([(6, -hw), (SWORD_LEN - 8, -hw), (SWORD_LEN, 0), (SWORD_LEN - 8, hw), (6, hw)]))
    solid3(cv, blade, IRON, OUT, depth=2, name="weapon")
    cv.fill(poly(sf.pts([(8, -1), (SWORD_LEN - 10, -1), (SWORD_LEN - 10, 1), (8, 1)])) & blade, "k2")
    guard = poly(sf.pts([(3, -hw - 3), (6, -hw - 3), (6, hw + 3), (3, hw + 3)]))
    solid3(cv, guard, STEELL, OUT, depth=1, name="weapon")
    grip = poly(sf.pts([(-14, -1.8), (3, -1.8), (3, 1.8), (-14, 1.8)]))
    solid3(cv, grip, IRON, OUT, depth=1, name="weapon")
    pom = ellipse(*sf.w(-15.5, 0), 2.8, 2.8)
    solid3(cv, pom, STEELL, OUT, depth=1, name="weapon")


def draw_hero(cv, p):
    """Urutan: ekor, pedang (bila di belakang), kaki, dada, perut, pelat pinggul, kerah, jambul, kepala + helm, lengan atas, pelindung bahu,
    lengan bawah, pedang (di depan), sarung tangan, kepala di depan (bila diminta), efek, rim light."""
    g = geometry(p)
    tcx, tcy = g["tcx"], g["tcy"]
    tail_fan(cv, (tcx - 12.0, g["hip_y"] - 4.0), p["tail_phase"], p["tail_rot"])
    if g["sword"] and p["sword_layer"] == "back":
        weapon_placeholder(cv, g["sword"])

    def legs():
        for hip, foot, bend, toe in ((g["hip_l"], g["foot_l"], -1, p["toe_l"]), (g["hip_r"], g["foot_r"], -1, p["toe_r"])):
            leg(cv, hip, foot, bend)
            boot(cv, foot[0], foot[1], toe)
    if not p["legs_front"]:
        legs()
    chest(cv, tcx, tcy)
    by = belly(cv, tcx, tcy)
    hip_plates(cv, tcx, by - 2)
    if p["legs_front"]:
        legs()
    collar(cv, tcx, tcy)
    hx, hy = g["head"]
    ihx, ihy = int(round(hx)), int(round(hy))

    def head_all():
        crest(cv, ihx, ihy, p["rage"])
        part(cv, "neck")
        cv.fill(poly([(ihx - 11, ihy + 5), (ihx + 11, ihy + 5), (ihx + 13, ihy + 22), (ihx - 13, ihy + 22)]), "k1")
        head_hd(cv, ihx, ihy, eyes=p["eyes"], brows=p["brows"], mouth=p["mouth"], face=p["face"], tilt=p["tilt"])
        helm2(cv, ihx, ihy, p["rage"])
    if not p["head_front"]:
        head_all()
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
        weapon_placeholder(cv, g["sword"])
    for side, sh, elbow, hand in arms:
        gauntlet(cv, hand[0], hand[1])
    if p["head_front"]:
        head_all()
    for f in p["fx"]:
        f(cv, g)
    rim_pass2(cv)
    return g


def head_only(p):
    """Jambul, leher, kepala, dan helm digambar sendirian di posisi pose p: acuan 'tidak tertutup apa pun' untuk memeriksa wajah dan telinga."""
    g = geometry(p)
    ihx, ihy = int(round(g["head"][0])), int(round(g["head"][1]))
    cv = PartCanvas()
    crest(cv, ihx, ihy, p["rage"])
    part(cv, "neck")
    cv.fill(poly([(ihx - 11, ihy + 5), (ihx + 11, ihy + 5), (ihx + 13, ihy + 22), (ihx - 13, ihy + 22)]), "k1")
    head_hd(cv, ihx, ihy, eyes=p["eyes"], brows=p["brows"], mouth=p["mouth"], face=p["face"], tilt=p["tilt"])
    helm2(cv, ihx, ihy, p["rage"])
    return cv


def render_pose(p):
    cv = PartCanvas()
    draw_hero(cv, p)
    return floor_clip(cv)


# ------------------------------------------------------------------ tiga pose kunci Fase Body
def pose_idle():
    """Berdiri tegak, ujung pedang di lantai di depan, kedua tangan di gagang."""
    return pose(cx=70, lean=1.0, grip=(91, 67), ang=44.0, lh_u=-9.0, lh=(70 - 13, 74), tail_phase=0.4)


def pose_run_peak():
    """Puncak langkah: melayang, badan condong, kaki depan terangkat menekuk, kaki belakang terlempar; pedang diseret di belakang, kepalan kanan ke depan."""
    cx = 82
    p = pose(cx=cx, lean=13.0, crouch=3.0, dy=-7.0, fl=(-17.0, 4.0), fr=(14.0, 12.0), eyes="look", brows="angry", mouth="shout", tail_phase=1.8, tail_rot=-22.0, hdy=1.0, hdx=2.0)
    p.update(grip=(cx - 21.0, 78.0), ang=186.0, lh_u=0.0, rh=(cx + 21.0, 57.0), sword_layer="back")
    return p


def pose_smash_hit():
    """Tumbukan attack-smash: lunge rendah, badan terpelintir ke depan, ujung bilah menghantam sisi atas balok kayu di lantai (bilah terlihat
    utuh dari genggaman ke balok, tidak terpotong tepi kanvas); kepala di depan supaya wajah terlihat."""
    cx = 56
    p = pose(cx=cx, lean=11.0, crouch=7.0, fl=(-14.0, 0.0), fr=(15.0, 0.0), eyes="angry", brows="angry", mouth="shout", tail_phase=2.6, tail_rot=24.0,
             hdy=0.0, twist=6.0, head_front=True)
    gx, gy, ang = cx + 24.0, 56.0, 50.0
    p.update(grip=(gx, gy), ang=ang, lh=(cx + 1.0, 75.0))
    sf = SwordFrame(gx, gy, ang)
    ux = (FLOOR - 11 - gy) / math.sin(math.radians(ang))   # ujung bilah tepat di sisi atas balok setinggi 11 px
    hx, hy = sf.w(ux, 0)
    p["fx"] = [lambda cv, g: H.fx_dust(cv, hx + 3, FLOOR - 1, 1, 1.0),
               lambda cv, g: H.wood_block(cv, hx + 3, FLOOR, 16, 11),
               lambda cv, g: H.fx_smear(cv, gx, gy, 34, -34, 40, 2),
               lambda cv, g: H.fx_burst(cv, hx - 1, hy - 2, 6),
               lambda cv, g: H.fx_chips(cv, hx + 1, FLOOR - 10, 1, seed=3, n=9, power=1.0)]
    return p


KEYPOSES = {"idle": pose_idle, "run": pose_run_peak, "attack-smash": pose_smash_hit}
