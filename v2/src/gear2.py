"""Kostum v2: helm, zirah, jubah, mantel, topi. Semua fungsi menerima Geo `g` supaya ikut pose.

Aturan wajah: helm dan topi tidak menutupi mata. Telinga Gobyet tetap menyembul di sisi helm.
"""
import math

import rig2 as R
from rig2 import solid, ellipse, rect, chain, inner, edge, poly, Frame2


# ================================================================== KNIGHT: baja
def great_helm(cv, g, plume=0.0, plume_c=("cr1", "cr2"), visor_up=False):
    """Helm besar (lebih besar dari kepala) dengan jendela wajah, alis baja, dan jambul merah melengkung."""
    hx, hy = g.ihead()
    shell = ellipse(hx, hy - 2.0, 11.2, 10.2) | rect(hx - 11, hy - 6, 23, 12)
    shell -= {(x, y) for (x, y) in shell if y > hy + 6}
    window = rect(hx - 7, hy - 4, 15, 12) - {(hx - 7, hy - 4), (hx + 7, hy - 4)}
    m = shell - window
    solid(cv, m, "st1", "st2", shade_off=(2, 2))
    cv.fill({(x, hy - 5) for x in range(hx - 8, hx + 9)}, "st3")
    cv.fill({(x, hy - 6) for x in range(hx - 8, hx + 9) if (x, hy - 6) in inner(m)}, "st0")
    for x in (hx - 9, hx + 9):
        cv.put(x, hy + 3, "st3")
    cv.fill({(hx - 5, hy - 10), (hx - 4, hy - 10), (hx - 5, hy - 9)}, "W")
    cv.fill({(hx, y) for y in range(hy - 11, hy - 6)}, "st2")
    # jambul
    sway = math.sin(plume) * 1.2
    pts = [(hx + 0.5, hy - 11.5), (hx - 2 + sway * 0.3, hy - 15.5), (hx - 7 + sway, hy - 16.5), (hx - 12 + sway, hy - 13.5),
           (hx - 13.5 + sway, hy - 9.5)]
    solid(cv, chain(pts, 2.3), plume_c[0], plume_c[1], shade_off=(1, 1))
    solid(cv, rect(hx - 1, hy - 13, 3, 3), "go1", "go2", shade_off=(1, 1))


def visor_helm(cv, g, plume=0.0):
    """Helm ksatria dongeng: kubah bulat, visor terangkat di dahi, lingkar emas, bulu putih tegak."""
    hx, hy = g.ihead()
    dome = {p for p in ellipse(hx, hy - 2.5, 10.4, 9.4) if p[1] <= hy - 3}
    sides = {(x, y) for (x, y) in ellipse(hx, hy - 1, 10.4, 9.0) if abs(x - hx) >= 8 and y <= hy + 4}
    solid(cv, dome | sides, "st1", "st2", shade_off=(2, 2))
    visor = poly([(hx - 8, hy - 5), (hx + 8, hy - 5), (hx + 6, hy - 9), (hx, hy - 10), (hx - 6, hy - 9)])
    solid(cv, visor, "st0", "st1", shade_off=(1, 1))
    cv.fill({(x, hy - 7) for x in range(hx - 5, hx + 6)}, "st3")
    cv.fill({(x, hy - 4) for x in range(hx - 9, hx + 10) if (x, hy - 4) in sides or abs(x - hx) < 9}, "go1")
    sway = math.sin(plume) * 1.0
    solid(cv, chain([(hx, hy - 11), (hx + sway, hy - 15), (hx + 2 + sway, hy - 18)], 1.7), "W", "smk", shade_off=(1, 1))


def kettle_hat(cv, g, tilt=0):
    """Topi baja bertepi lebar (pemanah): kubah rendah + tepi datar lebar, siluet beda dari helm besar."""
    hx, hy = g.ihead()
    hx += int(round(tilt))
    dome = {p for p in ellipse(hx, hy - 4.0, 8.4, 7.2) if p[1] <= hy - 4}
    brim = rect(hx - 14, hy - 5, 29, 2) | rect(hx - 12, hy - 3, 25, 1)
    solid(cv, dome | brim, "st1", "st2", shade_off=(1, 1))
    cv.fill({(x, hy - 5) for x in range(hx - 13, hx + 14)}, "st0")
    cv.fill({(hx - 4, hy - 9), (hx - 3, hy - 9), (hx - 4, hy - 8)}, "W")


def nasal_bascinet(cv, g, tilt=0):
    """Helm runcing (bascinet) dengan pelindung hidung pendek dan rantai di leher (Man-at-Arms)."""
    hx, hy = g.ihead()
    pts = [(hx - 10.5, hy - 1), (hx - 9.5, hy - 7), (hx - 5, hy - 11.5), (hx + 1 + tilt, hy - 17.5), (hx + 6, hy - 11.5),
           (hx + 10, hy - 7), (hx + 11, hy - 1), (hx + 8, hy - 4.5), (hx - 8, hy - 4.5)]
    m = poly(pts)
    solid(cv, m, "st1", "st2", shade_off=(2, 2))
    cv.fill({(x, hy - 5) for x in range(hx - 8, hx + 9)}, "st3")
    cv.fill(rect(hx - 1, hy - 5, 2, 4), "st2")
    cv.fill({(hx - 1, hy - 5), (hx, hy - 5)}, "st3")
    cv.fill({(hx - 4, hy - 10), (hx - 3, hy - 10), (hx - 3, hy - 11)}, "W")


def mail_coif(cv, g):
    """Rantai di bawah dagu dan bahu (Man-at-Arms)."""
    hx, hy = g.ihead()
    m = {p for p in ellipse(hx, hy + 8.5, 10.0, 3.6)}
    solid(cv, m, "st2", "st3", shade_off=(1, 1))
    for (x, y) in inner(m):
        if (x + y) % 2 == 0:
            cv.put(x, y, "st1")


def pauldron(cv, x, y, side, big=1.0):
    """Pelindung bahu berlapis: lempeng atas besar + lempeng bawah."""
    rx, ry = 5.4 * big, 4.2 * big
    up = ellipse(x + side * 1.4 * big, y - 0.6, rx, ry)
    lo = ellipse(x + side * 1.8 * big, y + 3.2 * big, rx - 0.8, 2.4 * big)
    solid(cv, lo, "st1", "st2", shade_off=(1, 1))
    solid(cv, up, "st1", "st2", shade_off=(1, 1))
    cv.fill({(xx, yy) for (xx, yy) in inner(up) if (xx - 1, yy - 1) not in up or (xx - 2, yy - 2) not in up}, "st0")


def breastplate(cv, g, w=0.8, h=0.8, accent=None, belt="le2"):
    m = ellipse(g.tcx, g.tcy, g.tw + w, g.th + h)
    solid(cv, m, "st1", "st2", shade_off=(2, 2))
    cx = int(round(g.tcx))
    cv.fill({(cx, y) for y in range(int(g.tcy - g.th + 1), int(g.tcy + g.th - 1)) if (cx, y) in inner(m)}, "st0")
    cv.fill({(cx - 3, int(g.tcy - 3)), (cx - 4, int(g.tcy - 2)), (cx - 4, int(g.tcy - 3))}, "W")
    if accent:
        cv.fill({(x, y) for (x, y) in inner(m) if abs(x - g.tcx) <= 2 and y > g.tcy - 2}, accent[0])
        cv.fill({(cx, int(g.tcy + 1)), (cx - 1, int(g.tcy + 2)), (cx + 1, int(g.tcy + 2)), (cx, int(g.tcy + 3))}, "go1")
    by = int(round(g.tcy + g.th - 1))
    cv.fill({(x, y) for (x, y) in m if y in (by, by + 1)}, belt)
    cv.fill(rect(cx - 1, by, 3, 2), "go1")


def faulds(cv, g, w=9.5, rows=4, col=("st1", "st2")):
    """Rok pelat di pinggul: melebarkan siluet bawah."""
    top = int(round(g.hip_y - 2))
    m = set()
    for k in range(rows):
        half = w + k * 0.8
        m |= {(x, top + k) for x in range(int(g.cx - half), int(g.cx + half) + 1)}
    solid(cv, m, col[0], col[1], shade_off=(1, 1))
    cv.fill({(x, top + 2) for x in range(int(g.cx - w), int(g.cx + w) + 2)}, "st3")


def plate_legs(cv, g):
    R.legs(cv, g, fur="st2", boots=("st1", "st3"))
    for i, s in enumerate((-1, 1)):
        hx, hy = g.hips[i]
        fx, fy = g.feet[i]
        kx, ky = (hx + fx) / 2 + s * 0.6, (hy + fy) / 2
        solid(cv, ellipse(kx, ky, 2.4, 2.0), "st1", "st2", shade_off=(1, 1))


def plate_arm(cv, g, i, r=2.3):
    R.arm(cv, g, i, sleeve="st2", r=r)
    if g.elbow[i]:
        ex, ey = g.elbow[i]
        solid(cv, ellipse(ex, ey, 2.2, 2.2), "st1", "st2", shade_off=(1, 1))


def gauntlet(cv, g, i, r=2.5):
    hx, hy = g.hand[i]
    solid(cv, ellipse(hx, hy, r, r), "st1", "st2", shade_off=(1, 1))
    cv.put(int(hx) - 1, int(hy) - 1, "st0")


def tabard(cv, g, c=("z", "1"), length=7):
    """Tabard kain di atas zirah: memberi warna aksen faksi tanpa menutupi pelat bahu."""
    x0 = int(round(g.tcx - 4))
    y0 = int(round(g.tcy - 3))
    m = rect(x0, y0, 9, int(g.hip_y - y0 + length - 4))
    m |= {(x0 + 1 + k, int(g.hip_y + length - 4)) for k in range(7)}
    solid(cv, m, c[0], c[1], shade_off=(1, 1))
    cx = x0 + 4
    cv.fill({(cx, y0 + 3), (cx - 1, y0 + 4), (cx + 1, y0 + 4), (cx, y0 + 5)}, "go1")


# ================================================================== tudung dan jubah
def hood(cv, g, c=("l", "L"), mask=True, peak=True, shadow=True):
    """Tudung menutupi kepala dan telinga, wajah tetap terlihat; masker kain menutupi mulut (Assassin)."""
    hx, hy = g.ihead()
    outer = ellipse(hx, hy - 1.0, 12.4, 11.0)
    if peak:
        outer |= poly([(hx - 5, hy - 9), (hx + 1, hy - 15.5), (hx + 6, hy - 9)])
    outer -= {(x, y) for (x, y) in outer if y > hy + 7}
    opening = ellipse(hx, hy + 1.6, 8.6, 7.2)
    m = outer - opening
    solid(cv, m, c[0], c[1], shade_off=(2, 2))
    if shadow:
        cv.fill({(x, y) for (x, y) in opening if y <= hy - 3 and (x, y) in ellipse(hx, hy + 1.6, 8.6, 7.2)}, c[1])
    if mask:
        mm = {(x, y) for (x, y) in ellipse(hx, hy + 5.6, 8.0, 3.4) if y >= hy + 3}
        solid(cv, mm, c[1], None)
        cv.fill({(x, hy + 4) for x in range(hx - 6, hx + 7) if (x, hy + 4) in mm}, c[0])


def cape(cv, g, c=("z", "1"), length=13, sway=0.0, side=0, width=1.0):
    """Jubah di punggung. side: -1 = condong ke kiri (asimetris), 0 = simetris."""
    sx0, sy0 = g.sh[0]
    sx1, sy1 = g.sh[1]
    bottom = g.tcy + length
    s = math.sin(sway) * 1.5
    if side < 0:
        pts = [(sx0 - 1, sy0 - 1), (sx1 + 1, sy1 - 1), (sx1 + 2, bottom - 4), (g.tcx + 2 + s, bottom),
               (sx0 - 6 * width + s, bottom + 2), (sx0 - 5 * width, sy0 + 6)]
    else:
        pts = [(sx0 - 1, sy0 - 1), (sx1 + 1, sy1 - 1), (sx1 + 3 * width + s, bottom), (g.tcx + s, bottom + 1),
               (sx0 - 3 * width + s, bottom)]
    m = poly(pts)
    solid(cv, m, c[0], c[1], shade_off=(2, 2))
    return m


def cloak_front(cv, g, c=("l", "L"), side=-1, length=9):
    """Sisi jubah yang menyampir di depan bahu kiri (asimetris)."""
    sx, sy = g.sh[0]
    pts = [(sx - 4, sy - 2), (g.tcx + 2, sy - 1), (g.tcx + 1, sy + 3), (sx + 1, sy + length), (sx - 5, sy + length - 1)]
    m = poly(pts)
    solid(cv, m, c[0], c[1], shade_off=(1, 1))


def robe(cv, g, c=("3", "4"), flare=4.0, trim=None, length=0):
    """Jubah panjang sampai lantai: siluet trapesium (Wizard, Priest, Academic)."""
    top = g.tcy - g.th + 1
    bot = R.BASE - 2 + g.p["dy"] + length
    pts = [(g.tcx - g.tw + 0.5, top + 2), (g.tcx + g.tw - 0.5, top + 2), (g.cx + g.tw + flare, bot), (g.cx - g.tw - flare, bot)]
    m = poly(pts) | ellipse(g.tcx, g.tcy, g.tw + 0.4, g.th + 0.4)
    solid(cv, m, c[0], c[1], shade_off=(2, 2))
    if trim:
        cv.fill({(x, y) for (x, y) in m if y >= bot - 1 and (x, y) in inner(m)}, trim)
    return m


# ================================================================== VIKING: bulu dan kulit
def horned_helm(cv, g, horns=1.0, nasal=True, c=("st2", "st3"), band="le2"):
    hx, hy = g.ihead()
    dome = {p for p in ellipse(hx, hy - 3.2, 9.8, 8.6) if p[1] <= hy - 4}
    solid(cv, dome, c[0], c[1], shade_off=(1, 1))
    cv.fill({(x, hy - 5) for x in range(hx - 9, hx + 10) if (x, hy - 5) in dome or (x, hy - 4) in dome}, band)
    cv.fill({(hx, y) for y in range(hy - 11, hy - 5)}, band)
    if nasal:
        cv.fill(rect(hx - 1, hy - 5, 2, 4), c[1])
    for s in (-1, 1):
        base = (hx + s * 8.5, hy - 7.5)
        pts = [base, (hx + s * (11.5 + 1.5 * horns), hy - 9.5 - 2 * horns), (hx + s * (13 + 2 * horns), hy - 13 - 3.5 * horns),
               (hx + s * (12 + 2 * horns), hy - 16 - 4 * horns)]
        for k, (a, b) in enumerate(zip(pts, pts[1:])):
            solid(cv, R.capsule(a, b, 2.0 - k * 0.5), "C", "c", shade_off=(1, 1))
    cv.fill({(hx - 4, hy - 9), (hx - 3, hy - 9)}, "st0")


def conical_helm(cv, g):
    """Helm kerucut tanpa tanduk (Gestir)."""
    hx, hy = g.ihead()
    m = poly([(hx - 10, hy - 4), (hx - 8, hy - 9), (hx + 0.5, hy - 15), (hx + 8.5, hy - 9), (hx + 10.5, hy - 4)])
    solid(cv, m, "st2", "st3", shade_off=(1, 1))
    cv.fill({(x, hy - 5) for x in range(hx - 9, hx + 10)}, "le2")
    cv.fill(rect(hx - 1, hy - 5, 2, 4), "st3")
    cv.fill({(hx - 3, hy - 10), (hx - 2, hy - 11)}, "st0")


def cloth_cap(cv, g, c=("ol1", "ol2")):
    """Topi kain petani bertepi gulung (Bondi)."""
    hx, hy = g.ihead()
    m = {p for p in ellipse(hx, hy - 4.0, 9.6, 6.6) if p[1] <= hy - 4} | poly([(hx + 2, hy - 10), (hx + 9, hy - 12), (hx + 6, hy - 8)])
    solid(cv, m, c[0], c[1], shade_off=(1, 1))
    cv.fill({(x, hy - 5) for x in range(hx - 9, hx + 10)}, "fu1")
    cv.fill({(x, hy - 4) for x in range(hx - 9, hx + 10)}, "fu2")


def fur_mantle(cv, g, c=("fu1", "fu2"), big=1.0):
    """Mantel bulu tebal di bahu: tepi bergerigi (bukan pelat halus seperti Knight)."""
    pts = []
    n = 14
    for k in range(n + 1):
        a = math.pi + k * math.pi / n
        r = (11.5 + (1.6 if k % 2 else 0)) * big
        pts.append((g.tcx + math.cos(a) * r, g.tcy - 3.5 + math.sin(a) * 4.5 * big + (3.2 if k % 2 == 0 else 1.2)))
    pts += [(g.tcx + 8 * big, g.tcy + 1), (g.tcx - 8 * big, g.tcy + 1)]
    m = poly(pts)
    solid(cv, m, c[0], c[1], shade_off=(1, 1))
    for (x, y) in inner(m):
        if (x * 3 + y * 5) % 7 == 0:
            cv.put(x, y, "fu0")
    return m


def pelt_hood(cv, g, c=("fu1", "fu2")):
    """Kulit serigala sebagai tudung Berserker: moncong di atas kepala, telinga Gobyet tetap di samping."""
    hx, hy = g.ihead()
    m = {p for p in ellipse(hx, hy - 4.5, 10.4, 7.6) if p[1] <= hy - 4}
    m |= poly([(hx - 7, hy - 9), (hx - 9.5, hy - 15.5), (hx - 4, hy - 11)]) | poly([(hx + 3, hy - 11), (hx + 7.5, hy - 15.5), (hx + 6.5, hy - 9)])
    solid(cv, m, c[0], c[1], shade_off=(1, 1))
    cv.fill({(hx - 4, hy - 7), (hx + 3, hy - 7)}, "Y")
    cv.fill({(hx - 4, hy - 6), (hx + 3, hy - 6)}, "K")
    teeth = {(x, hy - 4) for x in range(hx - 7, hx + 7, 2)}
    cv.fill(teeth, "W")


def leather_vest(cv, g, c=("le1", "le2"), belt="le2", buckle="st1"):
    m = ellipse(g.tcx, g.tcy, g.tw + 0.6, g.th + 0.6)
    solid(cv, m, c[0], c[1], shade_off=(2, 2))
    cx = int(round(g.tcx))
    cv.fill({(cx, y) for y in range(int(g.tcy - g.th + 2), int(g.tcy + g.th - 2))}, c[1])
    by = int(round(g.tcy + g.th - 1.5))
    cv.fill({(x, y) for (x, y) in m if y in (by, by + 1)}, belt)
    cv.fill(rect(cx - 1, by, 3, 2), buckle)


def tunic_skirt(cv, g, c=("le1", "le2"), w=8.5, rows=4):
    top = int(round(g.hip_y - 2))
    m = set()
    for k in range(rows):
        half = w + k * 0.6
        m |= {(x, top + k) for x in range(int(g.cx - half), int(g.cx + half) + 1)}
    solid(cv, m, c[0], c[1], shade_off=(1, 1))


def wraps_legs(cv, g, c=("le1", "le2")):
    """Kaki dengan balutan kain (Viking): betis bergaris silang."""
    R.legs(cv, g, fur=c[0], boots=("le2", "K"))
    for i, s in enumerate((-1, 1)):
        hx, hy = g.hips[i]
        fx, fy = g.feet[i]
        for k in range(3):
            f = 0.35 + k * 0.18
            x, y = hx + (fx - hx) * f, hy + (fy - hy) * f
            cv.fill({(int(x) - 1, int(y)), (int(x), int(y) + 1), (int(x) + 1, int(y))}, c[1])


def braid_beard(cv, g, c=("X", "x")):
    """Janggut kepang di bawah dagu (Viking fantasi)."""
    hx, hy = g.ihead()
    m = ellipse(hx, hy + 8.0, 5.6, 2.6)
    for s in (-1, 1):
        m |= R.capsule((hx + s * 2.5, hy + 9), (hx + s * 3.0, hy + 14), 1.4)
    solid(cv, m, c[0], c[1], shade_off=(1, 1))
    for s in (-1, 1):
        cv.put(hx + s * 3, hy + 14, "go1")


# ================================================================== PIRATE
def tricorn_big(cv, g, c=("L", "l"), trim="go1", feather=None, tilt=0, lift=0):
    """Topi tricorn besar Captain (lebih lebar dari kepala), opsional bulu merah melengkung."""
    hx, hy = g.ihead()
    hx += int(round(tilt))
    hy -= lift
    crown = {p for p in ellipse(hx, hy - 6.5, 8.6, 6.0) if p[1] <= hy - 5}
    brim = poly([(hx - 16, hy - 9), (hx - 9, hy - 4), (hx + 9, hy - 4), (hx + 16, hy - 9), (hx + 12, hy - 3), (hx, hy - 2),
                 (hx - 12, hy - 3)])
    m = crown | brim
    solid(cv, m, c[0], c[1], shade_off=(1, 1))
    cv.fill({(x, y) for (x, y) in edge(brim) if y >= hy - 4}, trim)
    if feather:
        pts = [(hx - 3, hy - 9), (hx - 8, hy - 14), (hx - 14, hy - 15), (hx - 18, hy - 12)]
        solid(cv, chain(pts, 1.8), feather[0], feather[1], shade_off=(1, 1))
    solid(cv, ellipse(hx + 0.5, hy - 7.5, 2.2, 2.0), "W", None)
    cv.fill({(hx, hy - 8), (hx + 1, hy - 8)}, "K")


def wide_hat(cv, g, c=("D", "N"), band="cr1", tilt=0):
    """Topi bertepi lebar dan datar (Sharpshooter): siluet piringan, beda dari tricorn."""
    hx, hy = g.ihead()
    hx += int(round(tilt))
    crown = rect(hx - 6, hy - 12, 13, 8) - {(hx - 6, hy - 12), (hx + 6, hy - 12)}
    brim = {p for p in ellipse(hx, hy - 4.5, 17.0, 2.6)}
    solid(cv, brim, c[0], c[1], shade_off=(1, 1))
    solid(cv, crown, c[0], c[1], shade_off=(1, 1))
    cv.fill({(x, hy - 6) for x in range(hx - 5, hx + 6)}, band)


def bandana_v2(cv, g, c=("R", "T"), knot_flap=0.0):
    hx, hy = g.ihead()
    m = {p for p in ellipse(hx, hy - 4.0, 9.8, 6.8) if p[1] <= hy - 4}
    solid(cv, m, c[0], c[1], shade_off=(1, 1))
    for (x, y) in inner(m):
        if (x + y) % 4 == 0 and y < hy - 5:
            cv.put(x, y, "W")
    f = math.sin(knot_flap) * 1.2
    tails = R.capsule((hx - 9, hy - 6), (hx - 14, hy - 3 + f), 1.3) | R.capsule((hx - 9, hy - 5), (hx - 13, hy + 0 + f), 1.2)
    solid(cv, tails, c[0], c[1], shade_off=(1, 1))


def skull_cap(cv, g, c=("cr1", "cr2")):
    hx, hy = g.ihead()
    m = {p for p in ellipse(hx, hy - 4.0, 9.8, 6.4) if p[1] <= hy - 4}
    solid(cv, m, c[0], c[1], shade_off=(1, 1))


def long_coat(cv, g, c=("cr1", "cr2"), trim="go1", flare=5.0, length=0, open_front=True, lapel=None):
    """Mantel panjang berekor sampai betis: siluet melebar di bawah (Captain)."""
    top = g.tcy - g.th + 1
    bot = R.BASE - 4 + g.p["dy"] + length
    sway = g.p.get("coat_sway", 0.0)
    pts = [(g.tcx - g.tw - 0.5, top + 2), (g.tcx + g.tw + 0.5, top + 2), (g.cx + g.tw + flare + sway, bot),
           (g.cx + 3, bot - 2), (g.cx - 3, bot - 2), (g.cx - g.tw - flare + sway * 0.6, bot)]
    m = poly(pts) | ellipse(g.tcx, g.tcy, g.tw + 0.8, g.th + 0.6)
    solid(cv, m, c[0], c[1], shade_off=(2, 2))
    if open_front:
        shirt = poly([(g.tcx - 2.5, top + 2), (g.tcx + 2.5, top + 2), (g.tcx + 1.5, g.hip_y - 1), (g.tcx - 1.5, g.hip_y - 1)])
        cv.fill(inner(m) & shirt, lapel or "W")
    if trim:
        cv.fill({(x, y) for (x, y) in edge(m) if y > g.hip_y and (x, y - 1) in m}, trim)
        for k in range(3):
            cv.put(int(g.tcx) - 4, int(top + 4 + k * 3), trim)
            cv.put(int(g.tcx) + 4, int(top + 4 + k * 3), trim)
    return m


def short_vest(cv, g, c=("cr1", "cr2"), shirt=("W", "smk"), stripes=True):
    """Kaus belang + rompi pendek (Skirmisher)."""
    m = ellipse(g.tcx, g.tcy, g.tw + 0.4, g.th + 0.4)
    solid(cv, m, shirt[0], shirt[1], shade_off=(2, 2))
    if stripes:
        cv.fill({(x, y) for (x, y) in inner(m) if (y - int(g.tcy)) % 3 == 0}, "nv1")
    for s in (-1, 1):
        v = {(x, y) for (x, y) in m if s * (x - g.tcx) > 2.5}
        solid(cv, v, c[0], c[1], shade_off=(1, 1))
    by = int(round(g.tcy + g.th - 1.5))
    cv.fill({(x, y) for (x, y) in m if y in (by, by + 1)}, "le2")


def sash(cv, g, c=("R", "T")):
    by = int(round(g.tcy + g.th - 1.5))
    m = rect(int(g.tcx - g.tw), by - 1, int(2 * g.tw) + 1, 3)
    m |= R.capsule((g.tcx + g.tw - 1, by + 1), (g.tcx + g.tw + 1, by + 6), 1.0)
    solid(cv, m, c[0], c[1], shade_off=(1, 1))


def trousers(cv, g, c=("nv1", "nv2"), boots=("D", "K"), short=False):
    R.legs(cv, g, fur=c[0], boots=None if short else boots)


def crossbelts(cv, g, c="le2", buckle="go1"):
    top = g.tcy - g.th + 1
    for s in (-1, 1):
        cv.fill(R.capsule((g.tcx - s * 6, top + 2), (g.tcx + s * 6, g.tcy + g.th - 2), 0.9), c)
    cv.fill(rect(int(g.tcx) - 1, int(g.tcy) - 1, 3, 3), buckle)


def eyepatch(cv, g):
    hx, hy = g.ihead()
    ex = hx - 4
    cv.fill(rect(ex - 2, hy - 2, 4, 4), "L")
    cv.fill({(x, hy - 3 - (x - ex + 6) // 4) for x in range(hx - 9, ex - 1)}, "L")
    cv.fill({(x, hy - 3) for x in range(ex + 2, hx + 9)}, "L")
