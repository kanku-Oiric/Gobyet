"""Senjata dan prop v2. Setiap item: fn(cv, grip, ang, p) dengan grip = posisi tangan, ang = arah item
(0 = kanan, -90 = atas), p = pose (untuk parameter animasi seperti tarikan busur atau cahaya tongkat).

Ukuran sengaja besar: senjata adalah bagian siluet (brief bagian 3 dan 58). Gaya kartun, tanpa darah.
"""
import math

from rig2 import Frame2, solid, ellipse, rect, chain, inner, capsule, poly, puff, star, mini_text


def _f(grip, ang, flip=1):
    return Frame2(grip, ang, flip)


# ------------------------------------------------------------------ pedang dan pisau
def blade(cv, grip, ang, length=12, w=1.6, guard=3.2, handle=4.5, pommel="go1", steel=("S", "st1"), glint=None):
    f = _f(grip, ang)
    solid(cv, f.rect(-handle, 1.4, -0.95, 0.95), "le2", None)
    solid(cv, f.ell(-handle - 0.6, 0, 1.4, 1.4), pommel, None)
    tip = length + 2.8
    solid(cv, f.poly([(2.6, -w), (length, -w), (tip, 0), (length, w), (2.6, w)]), steel[0], steel[1], shade_off=(1, 1))
    if length > 8:
        cv.fill(f.line([(4.0, 0), (length - 1.5, 0)], 0.45), steel[1])
    solid(cv, f.rect(1.2, 2.8, -guard, guard), "go1", "go2", shade_off=(1, 1))
    if glint is not None:
        x, y = f.world(4 + glint * (length - 4), -w * 0.4)
        star(cv, int(x), int(y), "W")


def sword(cv, grip, ang, p):
    blade(cv, grip, ang, length=12, w=1.6, guard=3.0, handle=3.5, glint=p.get("glint"))


def greatsword(cv, grip, ang, p):
    blade(cv, grip, ang, length=23, w=2.7, guard=5.0, handle=6.0, glint=p.get("glint"))


def dagger(cv, grip, ang, p):
    blade(cv, grip, ang, length=8.0, w=1.5, guard=2.6, handle=2.8, pommel="st3", steel=("st0", "st2"))


def seax(cv, grip, ang, p):
    f = _f(grip, ang)
    solid(cv, f.rect(-3, 1.4, -0.9, 0.9), "wo2", None)
    solid(cv, f.poly([(1.6, -1.6), (7.5, -1.6), (9.5, 0.2), (1.6, 1.2)]), "st0", "st2", shade_off=(1, 1))


def cutlass(cv, grip, ang, p):
    f = _f(grip, ang)
    solid(cv, f.rect(-3.5, 1.2, -0.95, 0.95), "le2", None)
    pts_top, pts_bot = [], []
    for k in range(9):
        u = 2.0 + k * 1.45
        bend = -0.035 * (u - 2) ** 2
        wdt = 1.9 - k * 0.08
        pts_top.append((u, bend - wdt))
        pts_bot.append((u, bend + wdt * 0.7))
    pts = pts_top + [(15.5, -0.035 * 13.5 ** 2 - 1.4)] + pts_bot[::-1]
    solid(cv, f.poly(pts), "S", "st1", shade_off=(1, 1))
    solid(cv, f.line([(0.2, 2.6), (1.6, 3.0), (2.4, 1.2)], 0.8) | f.rect(1.0, 2.4, -2.2, 2.2), "go1", "go2", shade_off=(1, 1))


# ------------------------------------------------------------------ perisai (digambar di depan tangan)
def tower_shield(cv, grip, ang, p, emblem=True, field=("z", "1")):
    """Perisai menara besar 15x20: bingkai baja, bidang merah tua, belah ketupat emas."""
    gx, gy = grip
    x0, y0 = int(round(gx)) - 7, int(round(gy)) - 11
    m = rect(x0, y0, 15, 18) | {(x, y) for x in range(x0 + 1, x0 + 14) for y in range(y0 + 18, y0 + 20)}
    m |= {(x, y0 + 20) for x in range(x0 + 4, x0 + 11)}
    m -= {(x0, y0), (x0 + 14, y0)}
    solid(cv, m, "st2", "st3", shade_off=(1, 1))
    fld = inner(inner(m))
    cv.fill(fld, field[0])
    cv.fill({(x, y) for (x, y) in fld if (x - 2, y - 2) not in fld}, field[1])
    if emblem:
        cx, cy = x0 + 7, y0 + 9
        dia = {(x, y) for x in range(cx - 4, cx + 5) for y in range(cy - 5, cy + 6) if abs(x - cx) * 1.25 + abs(y - cy) <= 5}
        solid(cv, dia, "go1", "go2", shade_off=(1, 1))
    cv.fill({(x0 + 2, y0 + 2), (x0 + 3, y0 + 2), (x0 + 2, y0 + 3)}, "st0")


def kite_shield(cv, grip, ang, p, field=("z", "1")):
    gx, gy = grip
    cx, y0 = int(round(gx)), int(round(gy)) - 8
    m = set()
    for dy in range(17):
        half = 6 if dy < 8 else max(0, int(round(6 - (dy - 7) * 0.75)))
        m |= {(cx + dx, y0 + dy) for dx in range(-half, half + 1)}
    solid(cv, m, "st2", "st3", shade_off=(1, 1))
    fld = inner(inner(m))
    cv.fill(fld, field[0])
    cv.fill({(x, y) for (x, y) in fld if (x - 2, y - 2) not in fld}, field[1])
    cv.fill({(x, y) for (x, y) in fld if y in (y0 + 6, y0 + 7)}, "go1")


def round_shield(cv, grip, ang, p, r=7.5, field=("wo1", "wo2"), paint="cr1"):
    """Perisai bundar kayu Viking: papan kayu, cat setengah, umbo besi di tengah."""
    gx, gy = grip
    m = ellipse(gx, gy, r, r)
    solid(cv, m, "st3", None)
    fld = inner(m)
    cv.fill(fld, field[0])
    for (x, y) in fld:
        if (x - int(gx)) % 4 == 0:
            cv.put(x, y, field[1])
    if paint:
        cv.fill({(x, y) for (x, y) in fld if (x - gx) + (y - gy) < -1 and ((x - gx) ** 2 + (y - gy) ** 2) > 3}, paint)
    solid(cv, ellipse(gx, gy, 2.3, 2.3), "st1", "st3", shade_off=(1, 1))


def buckler(cv, grip, ang, p):
    gx, gy = grip
    solid(cv, ellipse(gx, gy, 4.2, 4.2), "st1", "st2", shade_off=(1, 1))
    solid(cv, ellipse(gx, gy, 1.5, 1.5), "go1", None)


# ------------------------------------------------------------------ busur dan panah
def bow(cv, grip, ang, p, half=15.0, wood=("wo1", "wo2"), arrow=True):
    """Busur panjang. p['draw'] = tarikan tali (0..8). Panah terpasang bila p['nock'] (default True)."""
    draw = p.get("draw", 0.0)
    f = _f(grip, ang)
    k = 3.0 + draw * 0.35
    stave = [(-k * (v / half) ** 2 + 0.8, v) for v in [-half + i * half / 6.0 for i in range(13)]]
    nock = (-1.5 - draw, 0.0)
    tip0, tip1 = stave[0], stave[-1]
    string = f.line([tip0, nock], 0.35) | f.line([nock, tip1], 0.35)
    cv.fill(string, "C")
    solid(cv, f.line(stave, 1.3), wood[0], None)
    cv.fill(f.line(stave[5:8], 0.9), "le2")
    if arrow and p.get("nock", True):
        a0, a1 = nock[0], max(nock[0] + 14, 9.0)
        cv.fill(f.line([(a0, 0), (a1, 0)], 0.5), "wo2")
        solid(cv, f.poly([(a1 - 0.5, -1.6), (a1 + 2.8, 0), (a1 - 0.5, 1.6)]), "st1", None)
        cv.fill(f.poly([(a0 - 0.5, -1.8), (a0 + 2.6, -0.4), (a0 + 2.6, 0.4), (a0 - 0.5, 1.8)]), "R")


def flatbow(cv, grip, ang, p):
    bow(cv, grip, ang, p, half=12.0, wood=("wo2", "le2"))


def arrow_flying(cv, x, y, length=12):
    cv.fill({(xx, y) for xx in range(int(x) - length, int(x))}, "wo2")
    solid(cv, poly([(x - 0.5, y - 1.6), (x + 3, y + 0.5), (x - 0.5, y + 2.6)]), "st1", None)
    cv.fill({(int(x) - length, y - 1), (int(x) - length + 1, y - 1), (int(x) - length, y + 1), (int(x) - length + 1, y + 1)}, "R")


def quiver(cv, x, y, ang=-70):
    f = _f((x, y), ang)
    solid(cv, f.rect(-6, 6, -2.4, 2.4), "le1", "le2", shade_off=(1, 1))
    cv.fill(f.rect(-4.5, -3.5, -2.4, 2.4), "go2")
    for v in (-1.4, 0.0, 1.4):
        solid(cv, f.poly([(6.5, v - 0.9), (9.5, v - 1.1), (9.5, v + 1.1), (6.5, v + 0.9)]), "R" if v else "W", None)


# ------------------------------------------------------------------ senjata galah dan tumpul
def halberd(cv, grip, ang, p):
    f = _f(grip, ang)
    solid(cv, f.line([(-13, 0), (25, 0)], 1.15), "wo1", None)
    solid(cv, f.poly([(18, 0.8), (25, 0.8), (27, 8.0), (24, 10.5), (20, 7.0)]), "st1", "st2", shade_off=(1, 1))
    solid(cv, f.poly([(24, -1.5), (31.5, 0), (24, 1.5)]), "st1", None)
    solid(cv, f.poly([(21, -0.8), (24, -0.8), (21.5, -4.5)]), "st2", None)
    cv.fill(f.rect(18.4, 19.4, -1.1, 1.1), "go1")


def mace(cv, grip, ang, p):
    f = _f(grip, ang)
    solid(cv, f.line([(-3, 0), (9, 0)], 1.0), "wo2", None)
    for a in range(0, 360, 60):
        r = math.radians(a)
        solid(cv, f.poly([(12 + math.cos(r) * 2, math.sin(r) * 2), (12 + math.cos(r + 0.5) * 2, math.sin(r + 0.5) * 2),
                          (12 + math.cos(r + 0.25) * 5.2, math.sin(r + 0.25) * 5.2)]), "st2", None)
    solid(cv, f.ell(12, 0, 3.4, 3.4), "st1", "st3", shade_off=(1, 1))


def axe(cv, grip, ang, p, big=False):
    f = _f(grip, ang)
    if big:
        solid(cv, f.line([(-7, 0), (23, 0)], 1.15), "wo1", None)
        solid(cv, f.poly([(15.5, 1.0), (22, 1.0), (25.5, 7.5), (22.5, 11.5), (17.5, 7.5)]), "st1", "st2", shade_off=(1, 1))
        cv.fill(f.line([(23.5, 8.5), (24.6, 6.5)], 0.5), "st0")
    else:
        solid(cv, f.line([(-3.5, 0), (15, 0)], 1.05), "wo1", None)
        solid(cv, f.poly([(10, 0.8), (15.5, 0.8), (18.5, 6.5), (15.5, 10.0), (11.5, 6.5)]), "st1", "st2", shade_off=(1, 1))
        cv.fill(f.line([(17, 7.5), (17.8, 5.5)], 0.5), "st0")


def greataxe(cv, grip, ang, p):
    axe(cv, grip, ang, p, big=True)


def spear(cv, grip, ang, p, back=14, front=22):
    f = _f(grip, ang)
    solid(cv, f.line([(-back, 0), (front, 0)], 0.85), "wo1", None)
    solid(cv, f.poly([(front - 0.5, -1.7), (front + 3.5, -2.0), (front + 8, 0), (front + 3.5, 2.0), (front - 0.5, 1.7)]),
          "st1", "st2", shade_off=(1, 1))
    cv.fill(f.rect(front - 2, front - 0.6, -1.2, 1.2), "le2")


def javelin(cv, grip, ang, p):
    spear(cv, grip, ang, p, back=9, front=15)


def staff(cv, grip, ang, p):
    """Tongkat penyihir: lebih tinggi dari Gobyet, ujung bengkok memegang permata bercahaya."""
    f = _f(grip, ang)
    solid(cv, f.line([(-14, 0), (17, 0), (19, -1.5), (20.5, -0.5)], 1.0), "wo1", None)
    glow = p.get("glow", 0.0)
    gx, gy = f.world(22.5, 0.6)
    if glow > 0.2:
        cv.fill({q for q in ellipse(gx, gy, 3.6 + glow * 2, 3.6 + glow * 2) if (q[0] + q[1]) % 2 == 0}, "glw" if p.get("gem") == "g" else "mag")
    solid(cv, ellipse(gx, gy, 2.6, 2.6), "3" if p.get("gem") != "g" else "Z", "4" if p.get("gem") != "g" else "v", shade_off=(1, 1))
    cv.put(int(gx) - 1, int(gy) - 1, "W")


def hammer(cv, grip, ang, p):
    f = _f(grip, ang)
    solid(cv, f.line([(-5, 0), (16, 0)], 1.2), "wo1", None)
    solid(cv, f.rect(14.5, 22, -6.5, 6.5), "st2", "st3", shade_off=(1, 1))
    cv.fill(f.rect(16, 17, -6.5, 6.5) | f.rect(19.5, 20.5, -6.5, 6.5), "st3")
    cv.fill(f.rect(15.2, 16, -5.5, -3.5), "st0")


def anchor(cv, grip, ang, p):
    """Jangkar besar sebagai senjata Buccaneer."""
    f = _f(grip, ang)
    solid(cv, f.line([(-3, 0), (18, 0)], 1.3), "st3", None)
    solid(cv, f.ell(-4.2, 0, 2.2, 2.2) - f.ell(-4.2, 0, 0.9, 0.9), "st3", None)
    solid(cv, f.line([(2.5, -6), (2.5, 6)], 1.0), "st3", None)
    arc = [(18 - 7 * (1 - math.cos(a)), 9 * math.sin(a)) for a in [math.radians(d) for d in range(-90, 91, 15)]]
    solid(cv, f.line(arc, 1.3), "st3", None)
    for v in (-9, 9):
        s = 1 if v > 0 else -1
        solid(cv, f.poly([(11, v - s * 0.5), (15.5, v + s * 0.5), (12, v - s * 3.0)]), "st3", None)
    cv.fill(f.line([(0, -0.5), (15, -0.5)], 0.4), "st2")


# ------------------------------------------------------------------ senjata api (prop kartun)
def pistol(cv, grip, ang, p):
    f = _f(grip, ang)
    solid(cv, f.poly([(-1.5, -1.0), (1.5, -1.6), (2.0, 1.6), (-2.5, 3.6), (-3.8, 2.8)]), "wo1", "wo2", shade_off=(1, 1))
    solid(cv, f.rect(0.5, 9.0, -2.4, -0.4), "st2", "st3", shade_off=(1, 1))
    cv.fill(f.rect(1.0, 2.0, -3.4, -2.4), "go1")


def blunderbuss(cv, grip, ang, p):
    f = _f(grip, ang)
    solid(cv, f.poly([(-7, 0.5), (-1, -1.4), (1, 2.0), (-6, 3.6)]), "wo1", "wo2", shade_off=(1, 1))
    solid(cv, f.poly([(0, -1.6), (11, -1.6), (14, -3.6), (14, 2.6), (11, 0.8), (0, 0.8)]), "go1", "go2", shade_off=(1, 1))


def rifle(cv, grip, ang, p):
    """Senapan panjang: popor kayu, laras panjang lebih dari 30 px (bagian utama siluet Sharpshooter)."""
    f = _f(grip, ang)
    solid(cv, f.poly([(-9, 1.0), (-8, -1.6), (-1, -1.2), (2, 0.6), (-3, 1.8), (-8, 3.4)]), "wo1", "wo2", shade_off=(1, 1))
    solid(cv, f.rect(-1, 14, -1.3, 0.9), "wo1", "wo2", shade_off=(1, 1))
    solid(cv, f.rect(0, 25, -2.0, -0.6), "st2", "st3", shade_off=(1, 1))
    cv.fill(f.rect(24, 25, -2.8, -2.0), "st3")
    cv.fill(f.rect(3, 4.5, -2.6, -2.0), "go1")


def powder_keg(cv, grip, ang, p):
    """Tong mesiu kecil kartun dengan sumbu (lit = sumbu menyala)."""
    gx, gy = grip
    x0, y0 = int(round(gx)) - 4, int(round(gy)) - 9
    m = rect(x0, y0, 8, 9) - {(x0, y0), (x0 + 7, y0), (x0, y0 + 8), (x0 + 7, y0 + 8)}
    m |= {(x0 - 1, y) for y in range(y0 + 2, y0 + 7)} | {(x0 + 8, y) for y in range(y0 + 2, y0 + 7)}
    solid(cv, m, "wo1", "wo2", shade_off=(1, 1))
    cv.fill({(x, y) for (x, y) in inner(m) if y in (y0 + 2, y0 + 6)}, "st3")
    cv.fill(rect(x0 + 2, y0 + 3, 4, 2), "K")
    mini = {(x0 + 3, y0 + 3), (x0 + 4, y0 + 4)}
    cv.fill(mini, "W")
    cv.fill({(x0 + 4, y0 - 1), (x0 + 5, y0 - 2), (x0 + 5, y0 - 3)}, "N")
    if p.get("lit"):
        cv.fill({(x0 + 5, y0 - 4), (x0 + 6, y0 - 5), (x0 + 4, y0 - 5)}, "Y")
        cv.put(x0 + 5, y0 - 5, "R")


def smoke_bomb(cv, grip, ang, p):
    gx, gy = grip
    solid(cv, ellipse(gx, gy - 2.5, 2.6, 2.6), "l", "L", shade_off=(1, 1))
    cv.fill({(int(gx) + 1, int(gy) - 6), (int(gx) + 2, int(gy) - 7)}, "N")
    cv.put(int(gx) - 1, int(gy) - 4, "s")


def telescope(cv, grip, ang, p):
    f = _f(grip, ang)
    solid(cv, f.rect(-2, 6, -1.6, 1.6), "go2", None)
    solid(cv, f.rect(5, 11, -1.3, 1.3), "go1", "go2", shade_off=(1, 1))
    solid(cv, f.rect(10, 15, -1.0, 1.0), "go1", None)
    cv.fill(f.rect(5, 5.8, -1.6, 1.6) | f.rect(10, 10.8, -1.3, 1.3), "le2")


def treasure_map(cv, grip, ang, p):
    """Peta harta terbuka 13x9: perkamen, garis putus-putus, tanda X merah."""
    gx, gy = grip
    x0, y0 = int(round(gx)) - 6, int(round(gy)) - 9
    m = rect(x0, y0, 13, 9)
    solid(cv, m, "cm1", "cm2", shade_off=(1, 1))
    for k in range(0, 8, 2):
        cv.put(x0 + 2 + k, y0 + 6 - k // 2, "le1")
    cv.fill({(x0 + 9, y0 + 2), (x0 + 11, y0 + 2), (x0 + 10, y0 + 3), (x0 + 9, y0 + 4), (x0 + 11, y0 + 4)}, "R")
    cv.fill({(x0, y0 + 2), (x0, y0 + 6), (x0 + 12, y0 + 3)}, "cm2")


def hook(cv, grip, ang, p):
    gx, gy = grip
    solid(cv, ellipse(gx, gy + 1, 2.2, 1.8), "le2", None)
    cv.fill(chain([(gx, gy - 1), (gx, gy - 4), (gx + 2, gy - 6), (gx + 4, gy - 5), (gx + 4, gy - 3)], 0.6), "st1")


def muzzle_puff(cv, x, y, k):
    """Kepulan kartun di ujung laras (tanpa peluru, tanpa sasaran)."""
    r = 1.6 + k * 1.1
    puff(cv, x + k * 2, y, r)
    puff(cv, x + k * 3 + 2, y - 2 - k, max(1.2, r - 0.8))


# ------------------------------------------------------------------ daftar item
# nama -> (fungsi, digambar di atas tangan?)
ITEMS = {
    "sword": (sword, False), "greatsword": (greatsword, False), "dagger": (dagger, False), "seax": (seax, False),
    "cutlass": (cutlass, False), "tower_shield": (tower_shield, True), "kite_shield": (kite_shield, True),
    "round_shield": (round_shield, True), "buckler": (buckler, True), "bow": (bow, False), "flatbow": (flatbow, False),
    "halberd": (halberd, False), "mace": (mace, False), "axe": (axe, False), "greataxe": (greataxe, False),
    "spear": (spear, False), "javelin": (javelin, False), "staff": (staff, False), "hammer": (hammer, False),
    "anchor": (anchor, False), "pistol": (pistol, False), "blunderbuss": (blunderbuss, False), "rifle": (rifle, False),
    "powder_keg": (powder_keg, True), "smoke_bomb": (smoke_bomb, True), "telescope": (telescope, False),
    "treasure_map": (treasure_map, True), "hook": (hook, True),
}


def register(name, fn, over_hand=False):
    ITEMS[name] = (fn, over_hand)
