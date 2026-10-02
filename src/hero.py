"""Berserker Hero (kostum `berserker-hero`, kanvas 128x96): prajurit Gobyet berzirah besi hitam, helm tengkorak naga,
pedang agung bergelombang, tabard teal. Desain asli dari spesifikasi pemilik (tugas BERSERKER-HERO); tidak memakai
gambar referensi karakter mana pun.

Skala: kepala Gobyet digambar ulang pada skala 1,5x relatif `monkey.head` (proporsi, warna wajah, telinga, mata, mulut
sama; hanya lebih rapat detailnya) supaya helm, tanduk, dan bilah terbaca di 128x96. Semua perubahan rig aditif:
`monkey.Canvas(w, h)` dan `monkey.PAL_HERO`; nilai bawaan 64x48 tidak berubah.

Palet lokal 26 warna (batas 28) di `HERO_PAL`, dua garis tepi turunan (hangat untuk organik dan kain, dingin untuk besi),
bayangan lebih dingin dan sorotan lebih hangat, rim light biru baja 1 px pada tepi atas semua bagian besi.
"""
import math

import monkey
from monkey import Canvas, ellipse, chain, rect, edge

W, H = 128, 96
FLOOR = 90          # baris lantai (piksel kaki terbawah = FLOOR - 1)
RX = 56             # tengah badan di sumbu x pada pose berdiri

# ------------------------------------------------------------------ palet (26 warna)
HERO_PAL = {
    "o1": (42, 26, 34), "o2": (22, 26, 40),                      # garis tepi: hangat (bulu, kain, perunggu), dingin (besi)
    "fs": (104, 66, 58), "fb": (139, 90, 55), "fl": (172, 118, 70),   # bulu: bayangan dingin, dasar, sorotan hangat
    "ei": (201, 132, 96),                                        # dalam telinga
    "cs": (196, 138, 110), "cb": (226, 172, 128), "cl": (242, 196, 150),  # wajah krem
    "ra": (236, 140, 108), "rb": (206, 110, 84),                 # wajah merah (face="A"): dasar, bayangan
    "ew": (250, 247, 240), "mo": (86, 42, 28),                   # putih mata, hidung dan mulut
    "is": (32, 36, 54), "ib": (54, 60, 82), "il": (90, 98, 120),    # besi hitam: bayangan, dasar, sorotan
    "rm": (120, 158, 204),                                       # rim light biru baja
    "bs": (178, 160, 134), "bb": (232, 218, 186),                # tulang: gigi, tali gagang
    "zs": (24, 84, 92), "zb": (40, 128, 132), "zl": (118, 204, 192),  # teal: tabard, titik mata saat rage
    "ks": (116, 76, 38), "kb": (178, 126, 54), "kl": (228, 182, 96),  # perunggu: gesper, tepi pelat
    "pl": (218, 230, 244),                                       # sapuan terang tipis (smear)
}
IRON = ("is", "ib", "il")
FUR = ("fs", "fb", "fl")
FACE = ("cs", "cb", "cl")
FACE_RED = ("rb", "ra", "ra")
BONE = ("bs", "bb", "bb")
TEAL = ("zs", "zb", "zl")
BRONZE = ("ks", "kb", "kl")
monkey.PAL_HERO.update(HERO_PAL)
assert not set(HERO_PAL) & (set(monkey.PAL) | set(monkey.PAL_EXT)), "kunci palet hero bentrok"
assert len(HERO_PAL) <= 28


# ------------------------------------------------------------------ kanvas dengan pelacakan bagian
class PartCanvas(Canvas):
    """Canvas 128x96 yang mencatat bagian terakhir yang menulis tiap piksel (untuk mengukur bagian yang terlihat)."""

    def __init__(self):
        Canvas.__init__(self, W, H)
        self.owner = {}
        self.part = None

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h and c:
            k = (int(x), int(y))
            self.px[k] = c
            self.owner[k] = self.part


def part(cv, name):
    cv.part = name


# ------------------------------------------------------------------ geometri
def poly(pts):
    """Isi poligon (koordinat piksel, y ke bawah)."""
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    out, n = set(), len(pts)
    for y in range(int(min(ys)) - 1, int(max(ys)) + 2):
        py = y + 0.5
        for x in range(int(min(xs)) - 1, int(max(xs)) + 2):
            px, c, j = x + 0.5, False, n - 1
            for i in range(n):
                xi, yi = pts[i]
                xj, yj = pts[j]
                if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
                    c = not c
                j = i
            if c:
                out.add((x, y))
    return out


def thick(points, r0, r1=None):
    """Garis tebal berujung bulat dengan jari-jari menyusut dari r0 ke r1 sepanjang titik-titik."""
    r1 = r0 if r1 is None else r1
    out = set()
    n = len(points) - 1
    for i in range(n):
        ra = r0 + (r1 - r0) * i / n
        rb = r0 + (r1 - r0) * (i + 1) / n
        (x0, y0), (x1, y1) = points[i], points[i + 1]
        for k in range(int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1):
            t = k / max(1, int(max(abs(x1 - x0), abs(y1 - y0)) * 2))
            out |= ellipse(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, ra + (rb - ra) * t, ra + (rb - ra) * t)
    return out


def bezier(p0, p1, p2, n=14):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in (i / float(n) for i in range(n + 1))]


def inner(mask):
    return mask - edge(mask)


def solid3(cv, mask, tone, outline="o1", depth=1, name=None):
    """Isi tiga nada dengan cahaya dari kiri atas: sorotan di tepi atas-kiri, bayangan di tepi kanan-bawah, lalu garis
    tepi 1 px `outline` di tepi bentuk. tone = (bayangan, dasar, sorotan)."""
    if name:
        part(cv, name)
    shade, base, light = tone
    ring = edge(mask)
    body = mask - ring
    cv.fill(body, base)
    hl = {(x, y) for (x, y) in body if (x - 1, y) in ring or (x, y - 1) in ring or (x - 1, y - 1) in ring}
    sh = {(x, y) for d in range(1, depth + 1) for (x, y) in body if (x + d, y) in ring or (x, y + d) in ring}
    cv.fill(sh, shade)
    cv.fill(hl, light)
    cv.fill(ring, outline)
    return body


def rim_pass(cv):
    """Rim light biru baja 1 px: piksel besi tepat di bawah garis tepi dingin (tepi atas bagian besi). Dijalankan sekali
    di akhir gambar, jadi mencakup helm, pelat, bilah, dan semua bagian besi yang bertumpuk."""
    iron = set(IRON)
    for (x, y), c in list(cv.px.items()):
        if c in iron and cv.px.get((x, y - 1)) == "o2":
            cv.px[(x, y)] = "rm"
    return cv


# ================================================================== kepala Gobyet (skala 1,5x) dan helm
def _face_mask(cx, cy):
    return (ellipse(cx - 5.7, cy + 1.8, 6.6, 6.0) | ellipse(cx + 5.7, cy + 1.8, 6.6, 6.0) | ellipse(cx, cy + 6.9, 9.3, 5.1))


def head_hd(cv, cx, cy, eyes="look", brows="flat", mouth="frown", face="F", tilt=0):
    """Kepala Gobyet tampak depan: telinga, tengkorak berbulu, wajah bentuk hati, mata besar, alis, hidung, mulut.
    Sama dengan monkey.head (proporsi 1,5x): tengkorak 28,8x25,2, telinga di +-15,75, mata di +-6."""
    red = face == "A"
    ftone = FACE_RED if red else FACE
    for s in (-1, 1):
        ear = ellipse(cx + s * 15.75, cy + 2.2 + tilt * s * 0.7, 5.4, 5.7)
        solid3(cv, ear, FUR, "o1", depth=2, name="ear")
        cv.fill(ellipse(cx + s * 15.5, cy + 2.7 + tilt * s * 0.7, 3.0, 3.4) - edge(ear), "ei")
    skull = ellipse(cx, cy, 14.4, 12.6)
    solid3(cv, skull, FUR, "o1", depth=2, name="skull")
    fm = {p for p in _face_mask(cx, cy) if p in skull and p not in edge(skull)}
    part(cv, "face")
    cv.fill(fm, ftone[1])
    cv.fill({(x, y) for (x, y) in fm if (x, y + 1) not in fm or (x, y + 2) not in fm}, ftone[0])
    if not red:
        cv.fill({(x, y) for (x, y) in fm if ((x - 1, y - 1) not in fm or (x, y - 1) not in fm) and y > cy - 1}, ftone[2])
    ey = int(round(cy + 0.9))
    part(cv, "eye")
    for i, ex in enumerate((int(round(cx - 6.0)), int(round(cx + 6.0)))):
        if eyes in ("look", "wide", "down", "side", "left", "angry", "relief"):
            white = ellipse(ex, ey, 3.5, 3.2)
            if eyes == "wide":
                white = ellipse(ex, ey, 3.9, 3.9)
            elif eyes == "angry":
                white = ellipse(ex, ey + 0.4, 3.5, 2.7)
            elif eyes == "relief":
                white = {(x, y) for (x, y) in white if y >= ey - 1}
            cv.fill(white, "ew")
            px = {"look": 1, "wide": 0, "down": 0, "side": 2, "left": -2, "angry": 1, "relief": 0}[eyes]
            py = {"down": 1, "relief": 1}.get(eyes, 0)
            ps = rect(ex + px - 1, ey + py - 1, 3, 3) & white
            cv.fill(ps, "o1")
            if eyes not in ("angry", "relief") and (ex + px - 1, ey + py - 1) in ps:
                cv.put(ex + px - 1, ey + py - 1, "ew")                  # kilau mata
            cv.fill({p for p in edge(white) if p[1] < ey - 1}, "o1")       # garis kelopak atas
        elif eyes == "blink":
            cv.fill(rect(ex - 3, ey, 7, 1), "o1")
        elif eyes == "happy":
            cv.fill({(ex - 3, ey + 1), (ex - 2, ey), (ex - 1, ey - 1), (ex, ey - 1), (ex + 1, ey - 1), (ex + 2, ey), (ex + 3, ey + 1)}, "o1")
    part(cv, "brow")
    by = ey - 6
    for i, ex in enumerate((cx - 6.0, cx + 6.0)):
        d = 1 if i == 0 else -1                 # arah ke hidung
        if brows == "flat":
            a, b = (ex - 3.8, by + 0.5), (ex + 3.8, by + 0.5)
        elif brows == "angry":
            a, b = (ex - d * 3.8, by - 0.6), (ex + d * 3.6, by + 2.0)
        elif brows == "worried":
            a, b = (ex - d * 3.8, by + 1.6), (ex + d * 3.6, by - 0.8)
        else:  # up
            a, b = (ex - 3.8, by - 1.0), (ex + 3.8, by - 1.0)
        cv.fill(chain([a, b], 0.9), "o1")
    part(cv, "mouth")
    nx, ny = int(round(cx)), int(round(cy + 5.2))
    cv.fill({(nx - 2, ny), (nx - 1, ny), (nx, ny), (nx + 1, ny), (nx - 1, ny + 1), (nx, ny + 1)}, "mo")
    my = int(round(cy + 8.6))
    if mouth == "frown":
        cv.fill({(nx - 1, my), (nx, my), (nx - 3, my + 1), (nx - 2, my), (nx + 1, my), (nx + 2, my), (nx + 3, my + 1)}, "mo")
    elif mouth == "flat":
        cv.fill(rect(nx - 3, my, 7, 1), "mo")
    elif mouth == "smile":
        cv.fill({(nx - 3, my), (nx - 2, my + 1), (nx - 1, my + 1), (nx, my + 1), (nx + 1, my + 1), (nx + 2, my + 1), (nx + 3, my)}, "mo")
    elif mouth == "shout":
        cv.fill(rect(nx - 3, my - 1, 7, 5), "mo")
        cv.fill(rect(nx - 2, my - 1, 5, 1), "bb")
        cv.fill(rect(nx - 2, my + 2, 5, 1), "rb")
    elif mouth == "o":
        cv.fill({(nx - 1, my - 1), (nx, my - 1), (nx - 2, my), (nx + 1, my), (nx - 2, my + 1), (nx + 1, my + 1), (nx - 1, my + 2), (nx, my + 2)}, "mo")
    return {"ey": ey, "ex": (cx - 6.0, cx + 6.0), "nose": (nx, ny), "mouth": (nx, my)}


# --- helm tengkorak naga: titik lokal relatif pusat kepala (cx, cy), y ke bawah
DOME = [(-17.5, -3.0), (-18.5, -9.5), (-16.5, -16.5), (-11.5, -21.5), (-4.5, -24.0), (3.5, -23.5), (9.5, -21.0),
        (14.0, -16.0), (16.5, -10.0), (17.5, -3.5), (13.5, -4.8), (8.0, -6.8), (3.0, -8.2), (-3.0, -8.2), (-8.0, -6.8),
        (-13.5, -4.8)]
CREST_X = (-15.0, -9.5, -4.0)
HORN_A = ((-9.0, -14.0), (-22.0, -28.0), (-32.0, -14.0))          # tanduk panjang melengkung ke belakang
HORN_B = ((-3.0, -19.0), (-11.0, -36.0), (-24.0, -31.0))          # tanduk pendek, patah di ujung
HORN_B_KEEP = 19                                                  # jumlah titik bezier (dari 23) sebelum patah
SOCKETS = ((-7.6, -13.6, 3.6, 2.8), (7.8, -13.2, 3.6, 2.8))
JAW_L = [(-17.5, -3.5), (-17.6, 3.5), (-15.6, 9.0), (-11.6, 14.2), (-8.8, 10.4), (-10.2, 5.2), (-11.4, -0.5), (-13.5, -4.8)]


def _mirror(pts):
    return [(-x, y) for (x, y) in reversed(pts)]


def tr(pts, cx, cy):
    return [(cx + x, cy + y) for (x, y) in pts]


def _dome_top(x):
    """Tinggi atas kubah (y lokal) pada x lokal, interpolasi linear dari DOME."""
    top = DOME[:7]
    for (x0, y0), (x1, y1) in zip(top, top[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return -22.0


def helm(cv, cx, cy, rage=False):
    """Helm tengkorak naga dari besi hitam yang bertengger di kepala Gobyet: kubah dengan rongga mata, moncong, punggung
    bergerigi, dua tanduk melengkung ke belakang (satu patah di ujung), dan rahang terbuka menjadi pelindung pipi
    berderetan gigi krem. Wajah (mata, hidung, mulut) tetap terbuka."""
    # tanduk (di belakang kubah): A panjang melengkung ke belakang, B lebih pendek dan patah di ujung
    horn_a = thick(bezier(*tr(HORN_A, cx, cy), 22), 5.4, 1.0)
    solid3(cv, horn_a, IRON, "o2", depth=2, name="horn")
    pts_b = bezier(*tr(HORN_B, cx, cy), 22)[:HORN_B_KEEP]                                  # patah di t ~ 0,82
    horn_b = thick(pts_b, 4.6, 2.8)
    solid3(cv, horn_b, IRON, "o2", depth=2, name="horn")
    ex, ey = pts_b[-1]
    part(cv, "horn_break")
    brk = ellipse(ex, ey, 2.4, 2.4)
    cv.fill(brk, "o1")
    cv.fill(brk - edge(brk), "bb")
    # punggung bergerigi
    for bx in CREST_X:
        by = _dome_top(bx)
        spike = poly([(cx + bx - 2.2, cy + by + 3.5), (cx + bx + 4.4, cy + by + 3.5), (cx + bx - 2.0, cy + by - 5.6)])
        solid3(cv, spike, IRON, "o2", name="crest")
    # kubah
    solid3(cv, poly(tr(DOME, cx, cy)), IRON, "o2", depth=2, name="helm")
    # moncong: memanjang lurus ke depan dari dahi dan sedikit naik di ujung; lubang hidung di ujung, taring di bawah
    spine = bezier((cx + 3.0, cy - 18.5), (cx + 16.0, cy - 24.5), (cx + 29.0, cy - 22.5), 14)
    snout = thick(spine, 5.4, 3.2)
    solid3(cv, snout, IRON, "o2", depth=2, name="snout")
    part(cv, "snout")
    nx, ny = spine[-1]
    cv.fill(rect(int(nx) - 1, int(ny) - 2, 2, 2), "o2")                      # lubang hidung
    cv.fill(rect(int(nx) - 5, int(ny) - 3, 2, 2), "o2")
    for fx in (11.0, 17.0, 23.0):                                            # taring bawah moncong (gigi krem)
        part(cv, "fang")
        col = int(round(cx + fx))
        low = max(y for (x, y) in snout if x == col)
        cv.fill(rect(col, low - 1, 2, 4), "bb")
        cv.put(col, low + 3, "bs")
        cv.put(col + 1, low + 3, "bs")
    # sambungan pelat kubah: garis tepi dan sorotan
    part(cv, "helm_seam")
    for (sx, sy) in ((-1.0, -9.0), (-1.0, -10.0), (-1.0, -11.0), (-1.0, -12.0), (-1.0, -13.0), (-1.0, -14.0), (-1.0, -15.0)):
        cv.put(int(cx + sx), int(cy + sy), "is")
    # rongga mata
    for (sx, sy, rx, ry) in SOCKETS:
        sock = ellipse(cx + sx, cy + sy, rx, ry)
        part(cv, "socket")
        cv.fill(sock, "o2")
        cv.fill({(x, y) for (x, y) in sock if (x, y - 1) not in sock}, "is")
        cv.fill({(x, y - 1) for (x, y) in sock if (x, y - 1) not in sock}, "il")     # sorotan bibir rongga
        if rage:
            part(cv, "socket_glow")
            cv.fill(rect(int(round(cx + sx)) - 1, int(round(cy + sy)) - 1, 2, 2), "zl")
    # paku keling di pelat
    part(cv, "rivet")
    for (rx, ry) in ((-14.0, -8.0), (-4.5, -9.5), (14.0, -8.0), (-15.5, -14.5), (14.5, -14.0), (-6.5, -19.5), (6.0, -19.0)):
        cv.put(int(cx + rx), int(cy + ry), "il")
    # rahang terbuka -> pelindung pipi + gigi
    for side, jaw in ((-1, JAW_L), (1, _mirror(JAW_L))):
        solid3(cv, poly(tr(jaw, cx, cy)), IRON, "o2", depth=1, name="jaw")
        for k, ty in enumerate((1.4, 5.2, 9.0)):
            ix = -(10.6 - 0.5 * k)
            tx = int(round(cx + ix)) if side < 0 else int(round(cx - ix)) - 2
            tooth = rect(tx, int(round(cy + ty)), 2, 3)
            part(cv, "tooth%d%s" % (k, "L" if side < 0 else "R"))
            cv.fill(tooth, "bb")
            cv.fill({(x, y) for (x, y) in tooth if y == int(round(cy + ty)) + 2}, "bs")
    return cv


# ================================================================== pedang agung bergelombang
S_LEN = 54.0                      # ujung bilah dari tangan kanan (u = 0)
POMMEL_U = -15.4
LOBES = 5
LOBE0, PITCH = 8.0, 7.4           # awal lekuk dan jarak antar-puncak (u)
DEPTH = 4.6                        # kedalaman lekuk: puncak luk ke pinggang bilah (batas minimal 3 px)


def blade_base(u):
    """Setengah lebar pinggang bilah (di antara dua luk): melebar di tengah lalu meruncing."""
    a, b = LOBE0, LOBE0 + LOBES * PITCH
    return 2.4 + 1.2 * math.sin(math.pi * (u - a) / (b - a))


def blade_hw(u):
    """Setengah lebar bilah di posisi u: 5 luk berurutan berbentuk busur sinus (tonjolan di tiap sisi), lalu meruncing ke ujung."""
    a, b = LOBE0, LOBE0 + LOBES * PITCH
    if u < a:
        return 3.0
    if u <= b:
        k = int((u - a) / PITCH)
        ph = ((u - a) - k * PITCH) / PITCH
        return blade_base(u) + DEPTH * math.sin(math.pi * ph)
    t = (u - b) / (S_LEN - b)
    return max(0.0, blade_base(b) * (1.0 - t) ** 0.8)


class SwordFrame:
    """Sistem koordinat pedang: titik asal tangan kanan, u sepanjang pedang (0 = kanan, 90 = bawah), v tegak lurus."""

    def __init__(self, gx, gy, ang):
        self.gx, self.gy, self.ang = gx, gy, ang
        a = math.radians(ang)
        self.ca, self.sa = math.cos(a), math.sin(a)

    def w(self, u, v):
        return (self.gx + u * self.ca - v * self.sa, self.gy + u * self.sa + v * self.ca)

    def pts(self, pairs):
        return [self.w(u, v) for (u, v) in pairs]


def sword_parts(cv, g, parts=("blade", "guard", "grip")):
    """Gambar bagian pedang. g = SwordFrame. Urutan: bilah, pelindung, gagang, pommel."""
    if "blade" in parts:
        us = [6.0 + 0.5 * i for i in range(int((S_LEN - 6.0) / 0.5) + 1)]
        top = [g.w(u, -blade_hw(u)) for u in us]
        bot = [g.w(u, blade_hw(u)) for u in reversed(us)]
        blade = poly(top + bot)
        solid3(cv, blade, IRON, "o2", depth=2, name="blade")
        body = blade - edge(blade)
        # garis pamor tipis lebih terang sepanjang bilah, dan alur gelap di sisi lain
        part(cv, "blade")
        cv.fill({q for q in chain([g.w(7.5, -0.9), g.w(S_LEN - 7.0, -0.9)], 0.45) if q in body}, "il")
        cv.fill({q for q in chain([g.w(7.5, 1.1), g.w(S_LEN - 9.0, 1.1)], 0.45) if q in body}, "is")
    if "guard" in parts:
        # pelindung bentuk sayap: pelat lebar yang menyapu keluar dan ujungnya turun ke arah pommel (turun bila pedang tegak)
        for side in (-1, 1):
            wing = [(1.4, -2.0), (6.8, -3.2), (7.4, -7.6), (4.4, -11.4), (-1.0, -12.6), (-3.0, -11.0), (-0.6, -7.8), (0.2, -4.0)]
            solid3(cv, poly(g.pts([(u, v * -side) for (u, v) in wing])), IRON, "o2", name="guard")
        solid3(cv, poly(g.pts([(1.6, -3.8), (5.8, -3.8), (5.8, 3.8), (1.6, 3.8)])), BRONZE, "o1", name="guard_boss")
    if "grip" in parts:
        grip = poly(g.pts([(POMMEL_U + 1.5, -2.6), (2.4, -2.6), (2.4, 2.6), (POMMEL_U + 1.5, 2.6)]))
        part(cv, "grip")
        cv.fill(grip, "o1")
        cv.fill(grip - edge(grip), "bb")
        for k in range(0, 8):                                    # lilitan tali krem diagonal
            u = POMMEL_U + 2.6 + k * 2.0
            cv.fill({q for q in chain([g.w(u, -2.2), g.w(u + 1.0, 2.2)], 0.4) if q in grip - edge(grip)}, "bs")
        solid3(cv, ellipse(*g.w(POMMEL_U, 0), 2.7, 2.7), BRONZE, "o1", name="pommel")


# ================================================================== tubuh dan zirah
UPPER, FORE = 10.0, 9.5           # panjang lengan atas dan lengan bawah
LEG = 16.0                        # pinggul ke pusat pergelangan saat berdiri
THIGH, SHIN = 9.8, 9.4


def ik(a, b, l1, l2, bend):
    """Sendi dua tulang: dari titik a ke target b, sendi ke arah `bend` (+1 / -1 sisi tegak lurus)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    d = max(1e-6, math.hypot(dx, dy))
    d = min(d, l1 + l2 - 0.01)
    x = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, l1 * l1 - x * x))
    ux, uy = dx / math.hypot(dx, dy), dy / math.hypot(dx, dy)
    return (a[0] + ux * x - uy * h * bend, a[1] + uy * x + ux * h * bend)


def clip(m, keep):
    return {q for q in m if keep(q)}


def draw_tail(cv, base, phase=0.0, length=16, curl=5.0):
    """Ekor keriting Gobyet (lengkung S lalu spiral), digambar di belakang badan."""
    bx, by = base
    pts = []
    for i in range(14):
        t = i / 13.0
        pts.append((bx - t * length, by + 3.5 * math.sin(t * math.pi) + math.sin(t * 4 + phase) * 1.2))
    ex, ey = pts[-1]
    cx, cy = ex, ey - curl
    for i in range(1, 19):
        a = math.pi / 2 + (i / 18.0) * math.pi * 1.75
        rr = curl * (1 - i / 18.0 * 0.45)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    m = thick(pts, 1.9, 1.7)
    part(cv, "tail")
    ring = edge(m)
    cv.fill(m - ring, "fb")
    cv.fill({(x, y) for (x, y) in m - ring if (x, y + 1) in ring or (x + 1, y) in ring}, "fs")
    cv.fill(ring, "o1")


def gauntlet(cv, hx, hy, r=4.3):
    m = ellipse(hx, hy, r, r * 0.95)
    solid3(cv, m, IRON, "o2", name="gauntlet")
    part(cv, "gauntlet")
    cv.fill({(int(hx) + 1, int(hy) - 2), (int(hx) + 2, int(hy) - 1), (int(hx) + 2, int(hy)), (int(hx) - 1, int(hy) - 2)}, "il")   # buku jari
    cv.fill({(int(hx) - 3, int(hy) + d) for d in (1, 2)}, "kb")                                                                      # manset perunggu


def sabaton(cv, fx, fy, toe=1):
    """Sepatu pelat menghadap kanan; (fx, fy) = pusat pergelangan, telapak di fy + 3."""
    sole = fy + 3.2
    m = poly([(fx - 4.2, sole - 6.5), (fx + 3.0, sole - 6.5), (fx + 4.0, sole - 3.5), (fx + 8.6 * toe, sole - 2.2),
              (fx + 9.4 * toe, sole - 0.2), (fx - 5.0, sole - 0.2)])
    solid3(cv, m, IRON, "o2", name="sabaton")
    part(cv, "sabaton")
    cv.fill({(int(fx + 4), int(sole) - 3), (int(fx + 5), int(sole) - 3), (int(fx + 6), int(sole) - 2)}, "il")
    cv.fill({(int(fx - 3) + i, int(sole) - 5) for i in range(5)}, "kb")                     # bibir bronze di pergelangan


def leg(cv, hip, foot, bend=1):
    knee = ik(hip, (foot[0], foot[1]), THIGH, SHIN, bend)
    thigh = thick([hip, knee], 3.6, 3.3)
    solid3(cv, thigh, IRON, "o2", name="cuisse")
    shin = thick([knee, (foot[0], foot[1] - 0.5)], 3.2, 2.9)
    solid3(cv, shin, IRON, "o2", name="greave")
    kc = ellipse(knee[0] + 0.8, knee[1], 3.4, 3.1)
    solid3(cv, kc, BRONZE, "o1", name="knee")
    return knee


def pauldron_big(cv, sx, sy):
    """Bahu berpelindung: tiga pelat tumpuk yang terpisah jelas, dengan tepi bawah perunggu."""
    sx -= 2.5
    plates = [(sx - 4.6, sy + 7.4, 6.6, 2.9), (sx - 3.2, sy + 3.6, 8.0, 3.4), (sx - 1.6, sy - 0.6, 9.6, 4.6)]
    for k, (x, y, rx, ry) in enumerate(plates):
        m = ellipse(x, y, rx, ry)
        solid3(cv, m, IRON, "o2", depth=2, name="pauldron%d" % (k + 1))
        part(cv, "pauldron%d" % (k + 1))
        body = m - edge(m)
        if k == 2:                                                                                  # tepi perunggu pelat atas
            cv.fill({(xx, yy) for (xx, yy) in body if (xx, yy + 1) in edge(m) and yy > y}, "kb")
        cv.put(int(x - rx * 0.45), int(y - 1), "il")
        cv.put(int(x - rx * 0.45) + 1, int(y - 1), "il")
        cv.put(int(x + rx * 0.3), int(y - 1), "il")


def pauldron_small(cv, sx, sy):
    """Bahu satunya: satu pelat bertepi bergerigi kecil."""
    sx += 3.0
    top = [(sx + math.cos(math.pi * (1 - k / 14.0)) * 7.8, sy - 0.3 - math.sin(math.pi * (1 - k / 14.0)) * 4.6) for k in range(15)]
    low = [(sx + 7.8 - k * 2.6, sy + 1.2 + (2.6 if k % 2 == 0 else 0.6)) for k in range(7)]      # tepi bawah bergerigi
    m = poly([(sx - 7.8, sy + 1.0)] + top[::-1][1:-1] + [(sx + 7.8, sy + 1.0)] + low)
    solid3(cv, m, IRON, "o2", depth=2, name="pauldron_s")
    part(cv, "pauldron_s")
    body = m - edge(m)
    cv.fill({(x, y) for (x, y) in body if (x, y - 2) in edge(m) and y < sy}, "il")
    cv.put(int(sx - 2), int(sy - 1), "il")


def chest(cv, tcx, tcy):
    m = ellipse(tcx, tcy - 0.5, 11.2, 9.4)
    solid3(cv, m, IRON, "o2", depth=2, name="chest")
    part(cv, "chest")
    body = m - edge(m)
    cx = int(round(tcx))
    cv.fill({(cx, y) for (x, y) in body if x == cx and y > tcy - 8}, "o2")                         # garis tengah
    cv.fill({(cx - 1, y) for (x, y) in body if x == cx - 1 and y > tcy - 8}, "il")
    for yy in (int(tcy + 2), int(tcy + 5)):                                                         # lame bawah dada
        cv.fill({(x, yy) for (x, y) in body if y == yy and abs(x - tcx) > 1}, "o2")
    for (rx, ry) in ((-6, -4), (7, -4), (-8, 0), (9, 0), (-5, 7), (6, 7)):                          # paku keling
        if (int(tcx + rx), int(tcy + ry)) in body:
            cv.put(int(tcx + rx), int(tcy + ry), "il")
    cv.fill({(x, y) for (x, y) in body if (x, y - 1) in edge(m) and abs(x - tcx) < 5.5}, "kb")     # tepi leher perunggu


def skirt(cv, tcx, tcy):
    """Rok rantai pendek di bawah sabuk (cincin = pola catur)."""
    by = int(round(tcy + 7.0))
    sk = poly([(tcx - 11.4, by + 3), (tcx + 11.4, by + 3), (tcx + 12.4, by + 7.0), (tcx + 8, by + 6.0), (tcx + 4.5, by + 7.6),
               (tcx, by + 6.2), (tcx - 4.5, by + 7.6), (tcx - 8, by + 6.0), (tcx - 12.4, by + 7.0)])
    solid3(cv, sk, IRON, "o2", name="skirt")
    part(cv, "skirt")
    cv.fill({(x, y) for (x, y) in sk - edge(sk) if (x + y) % 2 == 0 and y > by + 3}, "il")
    return by


def belt(cv, tcx, by):
    """Sabuk lebar berbahan kulit dengan gesper perunggu."""
    b = rect(int(round(tcx - 11.6)), by, 24, 5)
    solid3(cv, b, FUR, "o1", name="belt")
    bk = rect(int(round(tcx)) - 3, by - 1, 7, 7)
    solid3(cv, bk, BRONZE, "o1", name="buckle")
    part(cv, "buckle")
    cv.fill(rect(int(round(tcx)) - 1, by + 2, 3, 2), "o1")
    cv.put(int(round(tcx)) - 1, by + 1, "kl")


def tabard(cv, tcx, by, sway=0.0, lift=0.0):
    """Tabard kain teal pendek di depan sabuk. sway = ayunan (px) ujung bawah; lift = terangkat saat berlari."""
    L = 16.0 - lift * 3
    pts = [(tcx - 6.0, by + 4.0), (tcx + 6.0, by + 4.0), (tcx + 7.4 + sway, by + L - 2), (tcx + 3.0 + sway * 1.1, by + L + 1.8),
           (tcx - 0.5 + sway * 1.1, by + L - 1), (tcx - 4.0 + sway, by + L + 1.8), (tcx - 7.4 + sway * 0.9, by + L - 2)]
    m = poly(pts)
    solid3(cv, m, TEAL, "o1", depth=2, name="tabard")
    part(cv, "tabard")
    body = m - edge(m)
    cv.fill({(int(round(tcx + sway * 0.4)), y) for (x, y) in body if y > by + 6 and x == int(round(tcx + sway * 0.4))}, "zs")  # lipatan tengah
    hem = {(x, y) for (x, y) in body if y >= by + L - 4 and (x, y + 1) in edge(m)}
    cv.fill(hem, "kb")                                                                              # tepi bawah perunggu
    return m


# ================================================================== perakitan pose
def pose(**kw):
    p = dict(cx=RX, lean=0.0, crouch=0.0, dy=0.0, hdx=0.0, hdy=0.0, tilt=0,
             fl=(-7.0, 0.0), fr=(7.0, 0.0),          # kaki: (dx dari cx, angkat dari lantai)
             grip=None, ang=0.0, sword_layer="front", lh_u=-6.5, lh=None, rh=None,
             eyes="look", brows="angry", mouth="frown", face="F", rage=False,
             sway=0.0, lift=0.0, tail_phase=0.0, twist=0.0, head_front=False, fx=())
    p.update(kw)
    return p


def geometry(p):
    cx, lean = p["cx"], p["lean"]
    hip_y = FLOOR - 3 - LEG + p["crouch"] + p["dy"]
    tcy = hip_y - 7.5
    tcx = cx + lean * 0.5
    g = dict(hip_y=hip_y, tcx=tcx, tcy=tcy,
             sh_l=(tcx - 10.5 + p["twist"], tcy - 5.4), sh_r=(tcx + 10.5 + p["twist"] * 0.3, tcy - 5.4),
             head=(tcx + lean * 0.4 + p["hdx"], tcy - 21.7 + p["hdy"]),
             hip_l=(cx - 4.8, hip_y), hip_r=(cx + 4.8, hip_y))
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
    for side, sh in (("lh", g["sh_l"]), ("rh", g["sh_r"])):             # tangan tidak boleh lepas dari lengan
        h = g[side]
        if h is not None:
            d = math.hypot(h[0] - sh[0], h[1] - sh[1])
            if d > reach:
                g[side] = (sh[0] + (h[0] - sh[0]) * reach / d, sh[1] + (h[1] - sh[1]) * reach / d)
    return g


def draw_hero(cv, p):
    """Gambar satu pose penuh. Urutan: ekor, pedang (bila di belakang), kaki, dada, rok, tabard, sabuk, kepala + helm,
    lengan atas, pelindung bahu, lengan bawah, pedang (bila di depan), sarung tangan, efek, lalu rim light."""
    g = geometry(p)
    tcx, tcy = g["tcx"], g["tcy"]
    draw_tail(cv, (p["cx"] - 8.0, g["hip_y"] - 2.0), p["tail_phase"])
    if g["sword"] and p["sword_layer"] == "back":
        sword_parts(cv, g["sword"])
    for hip, foot, bend in ((g["hip_l"], g["foot_l"], -1), (g["hip_r"], g["foot_r"], -1)):
        leg(cv, hip, foot, bend)
        sabaton(cv, foot[0], foot[1])
    chest(cv, tcx, tcy)
    by = skirt(cv, tcx, tcy)
    tabard(cv, tcx, by, p["sway"], p["lift"])
    belt(cv, tcx, by)
    hx, hy = g["head"]

    def head_all():
        head_hd(cv, int(round(hx)), int(round(hy)), eyes=p["eyes"], brows=p["brows"], mouth=p["mouth"], face=p["face"], tilt=p["tilt"])
        helm(cv, int(round(hx)), int(round(hy)), rage=p["rage"])
    if not p["head_front"]:
        head_all()
    arms = []
    for side, sh, hand in (("l", g["sh_l"], g["lh"]), ("r", g["sh_r"], g["rh"])):
        if hand is None:
            continue
        elbow = ik(sh, hand, UPPER, FORE, 1)
        arms.append((side, sh, elbow, hand))
        solid3(cv, thick([sh, elbow], 3.4, 3.1), FUR, "o1", depth=1, name="upper_arm")
    pauldron_big(cv, g["sh_l"][0], g["sh_l"][1])
    pauldron_small(cv, g["sh_r"][0], g["sh_r"][1])
    for side, sh, elbow, hand in arms:
        fore = thick([(elbow[0] + (hand[0] - elbow[0]) * 0.15, elbow[1] + (hand[1] - elbow[1]) * 0.15),
                      (elbow[0] + (hand[0] - elbow[0]) * 0.88, elbow[1] + (hand[1] - elbow[1]) * 0.88)], 3.5, 3.2)
        solid3(cv, fore, IRON, "o2", name="vambrace")
        solid3(cv, ellipse(elbow[0], elbow[1], 3.0, 3.0), IRON, "o2", name="elbow")
    if g["sword"] and p["sword_layer"] == "front":
        sword_parts(cv, g["sword"])
    for side, sh, elbow, hand in arms:
        gauntlet(cv, hand[0], hand[1])
    if p["head_front"]:                                          # kepala di depan tangan: wajah tidak pernah tertutup
        head_all()
    for f in p["fx"]:
        f(cv, g)
    rim_pass(cv)
    return g


# ================================================================== efek: smear, debu, serpihan, balok kayu, garis kecepatan
def fx_smear(cv, cx, cy, r, a0, a1, width=1, dither=True):
    """Busur terang tipis (smear) mengikuti bilah: dari sudut a0 ke a1 (derajat layar, 0 = kanan, 90 = bawah) di jari-jari
    r, memudar (dither) ke arah a0 (ekor)."""
    n = int(abs(a1 - a0) * math.pi / 180.0 * r * 1.6) + 2
    for i in range(n + 1):
        t = i / float(n)
        a = math.radians(a0 + (a1 - a0) * t)
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
        if dither and t < 0.45 and (i % 2):
            continue
        for w in range(width):
            col = "pl" if t > 0.55 else "rm"
            cv.put(int(round(x - math.cos(a) * w)), int(round(y - math.sin(a) * w)), col)


def fx_dust(cv, x, y, k, size=1.0):
    """Kepulan debu di lantai (y = baris lantai) yang melebar ke dua sisi (k = 0..3)."""
    for s_ in (-1, 1):
        for j in range(3):
            off = (4 + j * 4.0 + k * 3.0) * s_ * size
            r = (1.6 + j * 0.5 + k * 0.4) * size
            m = {q for q in ellipse(x + off, y - r * 0.7 - k * 0.8 - j * 0.6, r, r * 0.8) if q[1] < FLOOR}
            part(cv, "dust")
            ring = edge(m)
            cv.fill(m - ring, "bb" if k < 2 else "bs")
            cv.fill({(xx, yy) for (xx, yy) in m - ring if (xx + 1, yy + 1) in ring}, "bs")
            cv.fill(ring, "bs")


def fx_chips(cv, x, y, k, seed=0, n=8, power=1.0):
    """Serpihan kayu dan batu beterbangan dari titik hantam."""
    import random
    rnd = random.Random(seed)
    for j in range(n):
        vx, vy = rnd.uniform(-3.4, 3.4) * power, rnd.uniform(3.0, 6.0) * power
        t = k + 0.6
        px, py = x + vx * t, y - vy * t + 0.9 * t * t
        if py >= FLOOR - 1:
            py = FLOOR - 2
        part(cv, "chip")
        c = ("fb", "fl", "bb", "kb")[j % 4]
        cv.fill(rect(int(px), int(py), 2, 2 if j % 3 == 0 else 1), c)
        if j % 3 == 0:
            cv.put(int(px) + 2, int(py), "o1")


def fx_burst(cv, x, y, r=7):
    """Kilatan hantam: inti terang dan percikan perunggu."""
    part(cv, "burst")
    cv.fill(ellipse(x, y, r * 0.55, r * 0.5), "pl")
    for j in range(10):
        a = j * math.tau / 10 + 0.2
        for i in range(int(r * (0.7 if j % 2 else 1.1))):
            rr = r * 0.55 + i
            cv.put(int(x + math.cos(a) * rr), int(y + math.sin(a) * rr * 0.9), "kl" if i < 2 else "kb")


def wood_block(cv, x, y_floor, w=18, h=10):
    """Balok kayu di lantai (sasaran): sisi depan bergaris serat, sisi atas lebih terang. x = tengah."""
    x0, y0 = int(x - w / 2), int(y_floor - h)
    front = rect(x0, y0 + 3, w, h - 3)
    top = poly([(x0 + 1, y0 + 3), (x0 + 4, y0), (x0 + w + 2, y0), (x0 + w, y0 + 3)])
    solid3(cv, front, FUR, "o1", depth=2, name="block")
    solid3(cv, top, ("fb", "fl", "cl"), "o1", name="block")
    part(cv, "block")
    for yy in (y0 + 5, y0 + 7):
        cv.fill({(xx, yy) for xx in range(x0 + 2, x0 + w - 2) if (xx + yy) % 5 != 0}, "fs")
    cv.fill({(x0 + w // 2 + dx, y0 + 3 + dy) for dx, dy in ((0, 0), (-1, 1), (0, 2), (1, 3))}, "o1")   # retak


def fx_speed(cv, x, y, n=3, length=9):
    """Garis kecepatan di belakang (kiri) titik (x, y)."""
    part(cv, "speed")
    for k in range(n):
        yy = y + (k - (n - 1) / 2.0) * 5
        L = length - (k % 2) * 3
        for i in range(L):
            if i % 5 != 4:
                cv.put(int(x - i), int(yy), "pl" if k == 1 else "rm")


# ================================================================== tiga pose kunci (Fase B)
def pose_idle():
    """Berdiri tegak, ujung pedang bertumpu di lantai di depan, kedua tangan di gagang. Napas di puncak (kunci)."""
    return pose(cx=44, lean=1.0, grip=(63, 73), ang=20.0, lh_u=-10.0, sway=0.5, tail_phase=0.4)


def pose_run_peak():
    """Run di puncak langkah: melayang, badan condong ke depan, kaki depan terangkat dan menekuk, kaki belakang
    terlempar lurus; pedang diseret di belakang dengan tangan kiri, tangan kanan mengepal ke depan; tabard terbawa angin."""
    cx = 80
    p = pose(cx=cx, lean=9.0, crouch=2.0, dy=-8.0, fl=(-17.0, 3.0), fr=(15.0, 11.0),
             eyes="look", brows="angry", mouth="shout", sway=-8.0, lift=1.0, tail_phase=1.8, hdy=1.0)
    p.update(grip=(cx - 22.0, 78.0), ang=187.0, lh_u=0.0, rh=(cx + 20.0, 61.0), sword_layer="back")
    p["fx"] = [lambda cv, g: fx_dust(cv, cx - 25, FLOOR - 1, 0, 0.8),
               lambda cv, g: fx_dust(cv, cx - 40, FLOOR - 1, 2, 0.7),
               lambda cv, g: fx_speed(cv, cx - 16, 50, 3, 10)]
    return p


def pose_smash_hit():
    """Titik tumbukan attack-smash: lunge rendah, badan terpelintir ke depan, bilah menghantam balok kayu di lantai;
    smear, serpihan, debu. Kepala digambar di depan tangan supaya wajah tetap terlihat."""
    cx = 34
    gx, gy, ang = cx + 25, 67.0, 42.0
    p = pose(cx=cx, lean=13.0, crouch=8.0, fl=(-13.0, 0.0), fr=(14.0, 0.0), eyes="angry", brows="angry", mouth="shout",
             sway=4.0, lift=0.0, tail_phase=2.6, hdy=0.0, twist=6.0, head_front=True)
    p.update(grip=(gx, gy), ang=ang, lh_u=-7.0)
    sf = SwordFrame(gx, gy, ang)
    ux = (FLOOR - gy) / math.sin(math.radians(ang))            # jarak di bilah saat menyentuh lantai
    hx_, hy_ = sf.w(ux, 0)
    p["fx"] = [lambda cv, g: fx_dust(cv, hx_ + 5, FLOOR - 1, 1, 1.0),
               lambda cv, g: wood_block(cv, hx_ + 5, FLOOR, 18, 11),
               lambda cv, g: fx_smear(cv, gx, gy, 44, -38, 34, 2),
               lambda cv, g: fx_smear(cv, gx, gy, 33, -26, 30, 1),
               lambda cv, g: fx_burst(cv, hx_ - 1, hy_ - 12, 7),
               lambda cv, g: fx_chips(cv, hx_ + 1, FLOOR - 10, 1, seed=3, n=9, power=1.0)]
    return p


KEYPOSES = {"idle": pose_idle, "run": pose_run_peak, "attack-smash": pose_smash_hit}


def floor_clip(cv):
    """Garis tanah: tidak ada piksel di y >= FLOOR (pedang menancap dan kaki tidak menembus lantai)."""
    for k in [k for k in cv.px if k[1] >= FLOOR]:
        del cv.px[k]
        if hasattr(cv, "owner"):
            cv.owner.pop(k, None)
    return cv


def render_pose(p):
    cv = PartCanvas()
    draw_hero(cv, p)
    return floor_clip(cv)
