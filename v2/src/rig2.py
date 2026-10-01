"""Rig v2 Gobyet: Gobyet berdiri, pose berbasis keyframe, dan bentuk yang bisa diputar.

Kepala tetap memakai `head()` dari rig v1 (src/monkey.py), jadi wajah, telinga, mata, dan ekspresi Gobyet
tidak berubah. Yang baru di v2:

- Badan berdiri (kaki pendek, telapak krem), karena kelas tempur butuh kuda-kuda, langkah, dan serangan.
- Pose sebagai dict angka (posisi tangan, condong, jongkok, angkat kaki, sudut senjata). Frame dibuat dengan
  interpolasi keyframe, sehingga loop menyambung mulus dan baseline kaki tidak melompat.
- Bentuk lokal (u sepanjang senjata, v tegak lurus) yang dirasterisasi pada sudut berapa pun, tanpa anti-aliasing.
  Setiap bentuk tetap diberi isi, bayangan kanan-bawah, dan garis tepi 1 px `K` seperti v1.

Kanvas 64x64. Jangkar: tengah kaki di x = RX, baris piksel kaki terbawah = BASE - 1.
"""
import math
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
import monkey as M  # noqa: E402
from monkey import ellipse, capsule, chain, rect, edge, solid  # noqa: E402,F401

W, H = 64, 64
RX, BASE = 28, 59

# Palet v2 = PAL + PAL_EXT v1 + warna bernama baru. Kunci baru berupa nama supaya tidak bentrok dengan kunci
# satu huruf v1.
PAL2 = dict(M.PAL)
PAL2.update(M.PAL_EXT)
PAL2.update({
    # baja (Knight): kebiruan supaya terbaca sebagai logam, beda dari kain abu
    "st0": (236, 240, 248), "st1": (190, 198, 214), "st2": (140, 150, 170), "st3": (92, 100, 120),
    # bulu hewan dan kulit (Viking)
    "fu0": (214, 196, 160), "fu1": (170, 146, 112), "fu2": (120, 98, 72),
    "le1": (128, 84, 50), "le2": (90, 58, 34),
    "wo1": (160, 112, 64), "wo2": (112, 76, 42),
    # bajak laut
    "nv1": (44, 60, 112), "nv2": (28, 38, 76), "cr1": (172, 38, 46), "cr2": (120, 24, 34),
    "go1": (240, 196, 72), "go2": (184, 134, 36),
    # efek
    "glw": (130, 255, 160), "mag": (190, 120, 255), "ma2": (130, 70, 210),
    "smk": (214, 214, 220), "sm2": (160, 160, 172),
    # kain tambahan
    "tl1": (60, 140, 140), "tl2": (36, 96, 98),  # teal
    "ol1": (120, 132, 64), "ol2": (84, 94, 40),  # zaitun
    "cm1": (238, 226, 196), "cm2": (206, 188, 150),  # perkamen
    "hz1": (255, 214, 64), "hz2": (40, 40, 40),  # helm proyek / garis
    "pk1": (236, 150, 170), "pk2": (190, 100, 124),
})


def rgb(c):
    return PAL2[c]


class Canvas:
    def __init__(self):
        self.px = {}

    def put(self, x, y, c):
        if 0 <= x < W and 0 <= y < H and c:
            self.px[(int(x), int(y))] = c

    def fill(self, pts, c):
        for p in pts:
            self.put(p[0], p[1], c)

    def image(self, scale=1, bg=None):
        im = Image.new("RGBA", (W, H), bg + (255,) if bg else (0, 0, 0, 0))
        for (x, y), c in self.px.items():
            im.putpixel((x, y), rgb(c) + (255,))
        return im.resize((W * scale, H * scale), Image.NEAREST) if scale != 1 else im


def inner(mask):
    return mask - edge(mask)


# ------------------------------------------------------------------ bentuk lokal yang bisa diputar
class Frame2:
    """Sistem koordinat lokal: titik asal `grip`, sumbu u ke arah `ang` derajat (0 = kanan, -90 = atas)."""

    def __init__(self, grip, ang, flip=1):
        self.gx, self.gy = grip
        a = math.radians(ang)
        self.ca, self.sa = math.cos(a), math.sin(a)
        self.flip = flip

    def world(self, u, v):
        v *= self.flip
        return self.gx + u * self.ca - v * self.sa, self.gy + u * self.sa + v * self.ca

    def local(self, x, y):
        dx, dy = x + 0.5 - self.gx, y + 0.5 - self.gy
        return dx * self.ca + dy * self.sa, (-dx * self.sa + dy * self.ca) * self.flip

    def mask(self, test, box):
        u0, u1, v0, v1 = box
        pts = [self.world(u, v) for u in (u0, u1) for v in (v0, v1)]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        out = set()
        for y in range(int(min(ys)) - 1, int(max(ys)) + 2):
            for x in range(int(min(xs)) - 1, int(max(xs)) + 2):
                u, v = self.local(x, y)
                if test(u, v):
                    out.add((x, y))
        return out

    def rect(self, u0, u1, v0, v1):
        return self.mask(lambda u, v: u0 <= u <= u1 and v0 <= v <= v1, (u0, u1, v0, v1))

    def ell(self, uc, vc, ru, rv):
        return self.mask(lambda u, v: ((u - uc) / ru) ** 2 + ((v - vc) / rv) ** 2 <= 1.0,
                         (uc - ru, uc + ru, vc - rv, vc + rv))

    def poly(self, pts):
        us, vs = [p[0] for p in pts], [p[1] for p in pts]

        def inside(u, v):
            c = False
            j = len(pts) - 1
            for i in range(len(pts)):
                ui, vi = pts[i]
                uj, vj = pts[j]
                if (vi > v) != (vj > v) and u < (uj - ui) * (v - vi) / (vj - vi + 1e-12) + ui:
                    c = not c
                j = i
            return c
        return self.mask(inside, (min(us), max(us), min(vs), max(vs)))

    def line(self, pts, r):
        return chain([self.world(u, v) for u, v in pts], r)


def poly(pts):
    """Poligon di koordinat kanvas."""
    return Frame2((0, 0), 0).poly(pts)


# ------------------------------------------------------------------ keyframe
def ease(x):
    return x * x * (3 - 2 * x)


def lerp(a, b, f):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return a + (b - a) * f
    if isinstance(a, tuple) and isinstance(b, tuple) and len(a) == len(b):
        return tuple(lerp(x, y, f) for x, y in zip(a, b))
    return a if f < 0.5 else b


def kf(t, keys, n, loop=True, smooth=True):
    """Interpolasi keyframe. keys = [(frame, dict), ...] urut naik, frame pertama 0. Bila loop, segmen terakhir
    menuju keys[0] di frame n. Nilai non-angka (ekspresi, nama senjata) mengikuti keyframe terdekat sebelumnya."""
    keys = [(f, dict(POSE, **d)) for f, d in keys]
    if loop:
        keys = keys + [(n, keys[0][1])]
    for (f0, a), (f1, b) in zip(keys, keys[1:]):
        if f0 <= t < f1:
            x = (t - f0) / float(f1 - f0)
            x = ease(x) if smooth else x
            out = dict(a)
            for k in set(a) | set(b):
                va, vb = a.get(k, b.get(k)), b.get(k, a.get(k))
                if isinstance(va, (int, float, tuple)) and not isinstance(va, bool) and type(va) is type(vb):
                    out[k] = lerp(va, vb, x)
                else:
                    out[k] = va
            return out
    return dict(keys[-1][1])


def wag(t, n, turns=1):
    return t * math.tau * turns / n


# ------------------------------------------------------------------ pose dan geometri
POSE = dict(
    dx=0.0, dy=0.0, crouch=0.0, lean=0.0, sx=4.0,
    lift_l=0.0, lift_r=0.0, fx_l=0.0, fx_r=0.0,
    rh=(10.0, 4.0), lh=(-10.0, 4.0), re=None, le=None,
    rw=None, rwa=0.0, lw=None, lwa=0.0,
    eyes="look", brows="flat", mouth="frown", face="F", tilt=0,
    hdx=0.0, hdy=0.0, tail=0.0, visible=True, alpha=1.0,
)


def pose(**kw):
    p = dict(POSE)
    p.update(kw)
    return p


class Geo:
    """Titik-titik tubuh dari pose. Semua koordinat kanvas (float)."""

    def __init__(self, p, body=None):
        body = body or {}
        self.p = p
        self.cx = RX + p["dx"]
        dy = p["dy"]
        c = p["crouch"]
        leg = body.get("leg", 8.0)
        self.foot_y = BASE - 2 + dy
        self.hip_y = BASE - 2 - leg + c + dy
        lean = p["lean"]
        self.tw = body.get("torso_w", 7.4)
        self.th = body.get("torso_h", 6.6)
        self.tcx = self.cx + lean * 0.45
        self.tcy = self.hip_y - self.th + 1.6
        self.sit = p.get("mode") == "sit"
        if self.sit:  # duduk di lantai seperti v1: paha dan telapak di depan badan
            self.tcy = BASE - 9.4 + dy + c * 0.3
            self.hip_y = self.tcy + 5.0
        self.top = self.tcy - self.th
        self.hx = self.cx + lean + p["hdx"]
        self.hy = self.tcy - 14.5 + p["hdy"]
        sx = p["sx"]
        self.feet = [(self.cx - sx + p["fx_l"], self.foot_y - p["lift_l"]),
                     (self.cx + sx + p["fx_r"], self.foot_y - p["lift_r"])]
        if self.sit:
            self.feet = [(self.tcx - 3.0, self.tcy + 7.7 - p["lift_l"]), (self.tcx + 3.0, self.tcy + 7.7 - p["lift_r"])]
        self.hips = [(self.cx - 3.0, self.hip_y), (self.cx + 3.0, self.hip_y)]
        sw = body.get("shoulder", 6.4)
        self.sh = [(self.tcx - sw, self.tcy - 3.6), (self.tcx + sw, self.tcy - 3.6)]
        self.hand = [(self.tcx + p["lh"][0], self.tcy + p["lh"][1]), (self.tcx + p["rh"][0], self.tcy + p["rh"][1])]
        self.elbow = [None, None]
        for i, key in enumerate(("le", "re")):
            e = p.get(key)
            if e is not None:
                self.elbow[i] = (self.tcx + e[0], self.tcy + e[1])
            else:
                self.elbow[i] = auto_elbow(self.sh[i], self.hand[i], -1 if i == 0 else 1)

    def ihead(self):
        return int(round(self.hx)), int(round(self.hy))


def auto_elbow(s, h, side):
    """Siku sedikit menekuk ke luar dan ke bawah supaya lengan tidak lurus kaku."""
    mx, my = (s[0] + h[0]) / 2.0, (s[1] + h[1]) / 2.0
    d = math.hypot(h[0] - s[0], h[1] - s[1])
    if d < 5:
        return None
    return (mx + side * 1.0, my + 0.8)


# ------------------------------------------------------------------ bagian tubuh dasar
def legs(cv, g, fur="B", foot="F", foot_shade="f", boots=None):
    """Kaki berdiri pendek. boots = (warna, bayangan) mengganti telapak krem dengan sepatu."""
    c = g.p["crouch"]
    for i, side in enumerate((-1, 1)):
        hx, hy = g.hips[i]
        fx, fy = g.feet[i]
        knee = ((hx + fx) / 2.0 + side * (0.6 + c * 0.55), (hy + fy) / 2.0 - c * 0.15)
        solid(cv, chain([(hx, hy), knee, (fx, fy - 1.6)], 2.3), fur, None)
    for i, side in enumerate((-1, 1)):
        fx, fy = g.feet[i]
        if boots:
            m = ellipse(fx + side * 0.9, fy, 3.2, 1.9) | rect(int(fx) - 2, int(fy) - 4, 5, 4)
            solid(cv, m, boots[0], boots[1], shade_off=(1, 1))
        else:
            solid(cv, ellipse(fx + side * 0.9, fy, 2.9, 1.7), foot, foot_shade, shade_off=(1, 1))


def sit_legs(cv, g, fur="B", foot="F", foot_shade="f", boots=None):
    """Paha dan telapak kaki posisi duduk (bentuk sitting_body v1)."""
    for i, s in enumerate((-1, 1)):
        fx, fy = g.feet[i]
        solid(cv, ellipse(g.tcx + s * 5.2, g.tcy + 5.7 - (g.foot_y - fy if False else 0), 4.2, 2.8), fur, "b" if fur == "B" else None)
    for i, s in enumerate((-1, 1)):
        fx, fy = g.feet[i]
        if boots:
            solid(cv, ellipse(fx, fy, 2.9, 1.7), boots[0], boots[1], shade_off=(1, 1))
        else:
            solid(cv, ellipse(fx, fy, 2.6, 1.5), foot, foot_shade, shade_off=(1, 1))


def torso(cv, g, fur="B", shade="b", belly=True):
    m = ellipse(g.tcx, g.tcy, g.tw, g.th)
    solid(cv, m, fur, shade)
    if belly:
        b = {p for p in ellipse(g.tcx, g.tcy + 0.8, g.tw - 2.6, g.th - 1.6) if p in inner(m)}
        cv.fill(b, "F")
        cv.fill({(x, y) for (x, y) in b if (x, y + 1) not in b}, "f")
    return m


def arm(cv, g, i, sleeve="B", hand="F", hand_shade="f", r=1.8, hand_r=2.0, sleeve_r=None):
    pts = [g.sh[i]] + ([g.elbow[i]] if g.elbow[i] else []) + [g.hand[i]]
    solid(cv, chain(pts, sleeve_r or r), sleeve, None)


def hand(cv, g, i, color="F", shade="f", r=2.0):
    hx, hy = g.hand[i]
    solid(cv, ellipse(hx, hy, r, r), color, shade, shade_off=(1, 1))


def tail(cv, g, phase=0.0, side=-1):
    M.tail(cv, (g.cx + side * 4.5, g.hip_y - 1.5), phase=phase, flip=side, length=8, curl=3.0)


def head(cv, g):
    p = g.p
    hx, hy = g.ihead()
    M.head(cv, hx, hy, eyes=p["eyes"], brows=p["brows"], mouth=p["mouth"], face=p["face"], tilt=p["tilt"])


# ------------------------------------------------------------------ efek
def puff(cv, x, y, r, c="smk", o="sm2"):
    solid(cv, ellipse(x, y, r, r * 0.85), c, None, outline=o)


def star(cv, x, y, c="Y", big=False):
    pts = {(x, y), (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)}
    if big:
        pts |= {(x - 2, y), (x + 2, y), (x, y - 2), (x, y + 2)}
    cv.fill(pts, c)
    if big:
        cv.put(x, y, "W")


def impact(cv, x, y, k=0, c="Y"):
    """Ledakan kartun 'pow' (tanpa darah): bintang bergerigi kuning dengan inti putih."""
    r0, r1 = 2.5 + k, 5.0 + k * 1.6
    pts = []
    for i in range(16):
        a = i * math.tau / 16
        r = r1 if i % 2 == 0 else r0
        pts.append((x + math.cos(a) * r, y + math.sin(a) * r))
    m = poly(pts)
    solid(cv, m, c, "O", outline="R", shade_off=(1, 1))
    cv.fill(ellipse(x, y, 1.4 + k * 0.4, 1.4 + k * 0.4), "W")


def speed_lines(cv, x, y, n=3, length=6, direction=-1, c="sm2", gap=3):
    for k in range(n):
        yy = y + (k - (n - 1) / 2.0) * gap
        L = length - (k % 2) * 2
        xs = range(int(x), int(x) + direction * L, direction)
        cv.fill({(xx, int(yy)) for xx in xs}, c)


def sweat(cv, x, y):
    cv.fill({(x, y), (x, y + 1), (x - 1, y + 2), (x + 1, y + 2), (x, y + 2), (x, y + 3)}, "I")
    cv.put(x, y + 3, "s")


def dust(cv, x, y, k=0):
    for dx, dy in ((-3 - k, 0), (-2 - k, -1), (3 + k, 0), (2 + k, -1), (-1, -2 - k // 2), (1, -2 - k // 2)):
        cv.put(x + dx, y + dy, "sm2")


def confetti(cv, seed, k, y0=4, y1=40):
    import random
    rnd = random.Random(seed)
    cols = ["R", "Y", "Z", "3", "pk1", "O"]
    for j in range(16):
        x = rnd.randrange(2, W - 2)
        y = y0 + (rnd.randrange(0, y1 - y0) + k * 3) % (y1 - y0)
        cv.fill({(x, y), (x + 1, y)} if j % 2 else {(x, y), (x, y + 1)}, cols[j % len(cols)])


def mini_text(cv, s, x, y, c):
    M.mini_text(cv, s, x, y, c)


def bubble(cv, x, y, w, h, fill="W", tail_dir=1):
    M.bubble(cv, x, y, w, h, fill, tail_dir)


def mark_bubble(cv, x, y, glyph, fill="W", c="K"):
    """Gelembung pikiran 11x9 dengan satu glyph (?, !, ...)."""
    bubble(cv, x, y, 11, 9, fill)
    if glyph == "...":
        for k in range(3):
            cv.put(x + 3 + k * 2, y + 5, c)
    else:
        mini_text(cv, glyph, x + 3, y + 2, c)
