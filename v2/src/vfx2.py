"""VFX v2: tebasan bulan sabit, jejak pedang, debu, hantaman, puing, percikan, retak tanah, dan darah bergaya.

Semua fungsi menggambar di koordinat dunia (rig) pada kanvas apa pun, jadi dipakai dua kali:
1. di dalam frame karakter (lapisan VFX Berserker), dan
2. sebagai sprite VFX terpisah (v2/vfx/<nama>.png) yang dimunculkan mesin pada event.

Darah: hanya sprite VFX terpisah, bergaya piksel (tetesan dan cipratan merah dengan tepi gelap), singkat
(4-6 frame), tingkat 1-3. Tanpa gore: tidak ada potongan tubuh, organ, atau luka realistis. Darah tidak pernah
digambar di sheet karakter; mesin memunculkannya hanya saat serangan kena (event "hit").
"""
import math
import random

from rig2 import ellipse, solid, poly, Canvas


def _put_if(cv, x, y, c, floor=None):
    if floor is None or y < floor:
        cv.put(int(round(x)), int(round(y)), c)


def _ang(a):
    return math.radians(a)


# ------------------------------------------------------------------ tebasan
def crescent(cv, cx, cy, r_out, a0, a1, thick, k=0, flat=1.0, cols=("sl1", "sl2", "sl3"), floor=None):
    """Bulan sabit tebasan dari sudut a0 (ekor) ke a1 (kepala), derajat layar (0 = kanan, 90 = bawah).
    Tebal maksimum dekat kepala, meruncing di kedua ujung. k = umur (0 segar, 1 menipis + dither, 2 serpih)."""
    span = a1 - a0
    if abs(span) < 1:
        return
    r_out = float(r_out)
    R = int(r_out + 2)
    fy = 1.0 / flat
    cut = {0: 0.0, 1: 0.35, 2: 0.6}.get(k, 0.8)
    for y in range(int(cy) - R, int(cy) + R + 1):
        for x in range(int(cx) - R, int(cx) + R + 1):
            dx, dy = x + 0.5 - cx, (y + 0.5 - cy) * fy
            d = math.hypot(dx, dy)
            if d > r_out or d < r_out - thick - 1:
                continue
            a = math.degrees(math.atan2(dy, dx))
            # posisi relatif sepanjang busur (0 = ekor, 1 = kepala), sudut dibungkus searah span
            rel = (a - a0) % 360.0 if span > 0 else (a0 - a) % 360.0
            t = rel / abs(span)
            if t < 0 or t > 1:
                continue
            if t < cut:
                continue
            th = thick * math.sin(math.pi * min(1.0, t ** 0.75)) if t < 0.97 else thick * 0.25
            th = max(th, 0.8)
            depth = (r_out - d) / th
            if depth < 0 or depth > 1:
                continue
            if depth < 0.28:
                c = cols[0]
            elif depth < 0.7:
                c = cols[1]
            else:
                c = cols[2]
                if (x + y) % 2:
                    continue
            if k >= 1 and t < cut + 0.25 and (x + y) % 2:
                continue
            if k >= 2 and c == cols[0]:
                c = cols[1]
            _put_if(cv, x, y, c, floor)


def sword_trail(cv, pivot, a0, a1, r_in, r_out, k=0, floor=None):
    """Jejak pedang (smear) di antara dua sudut pedang di sekitar pivot: pita lebar ber-dither, tepi luar terang."""
    crescent(cv, pivot[0], pivot[1], r_out, a0, a1, r_out - r_in, k=k, floor=floor)


def speed_lines(cv, x, y, n=4, length=10, direction=-1, gap=3, c="sl3", floor=None):
    for j in range(n):
        yy = y + (j - (n - 1) / 2.0) * gap
        L = length - (j % 2) * 3
        for i in range(L):
            if i % 4 != 3:
                _put_if(cv, x + direction * i, yy, c, floor)


# ------------------------------------------------------------------ debu, hantaman, puing, percikan
def dust(cv, x, y, k, size=1.0, seed=0, floor=None):
    """Kepulan debu tanah yang melebar ke samping dan memudar (k = 0..4)."""
    floor = floor if floor is not None else y + 1
    rnd = random.Random(seed)
    n = 3 if size < 1.2 else 4
    for j in range(n):
        for s in (-1, 1):
            off = (2.5 + j * 3.2 + k * 2.4 * size) * s + rnd.uniform(-0.6, 0.6)
            r = (1.6 + j * 0.5) * size * (1.0 + 0.25 * k) * (1.0 if k < 3 else 0.75)
            cy = y - r * 0.6 - k * 0.6 - j * 0.4
            m = {q for q in ellipse(x + off, cy, r, r * 0.8) if q[1] < floor}
            if k >= 3:
                m = {q for q in m if (q[0] + q[1] + k) % 2 == 0}
                cv.fill(m, "du2")
            else:
                solid(cv, m, "du1", "du2", outline="du2", shade_off=(1, 1))


def impact(cv, x, y, k, size=1.0, floor=None):
    """Kilat hantaman: inti putih + garis radial (k 0..3)."""
    if k == 0:
        m = {q for q in ellipse(x, y, 4.5 * size, 3.8 * size) if floor is None or q[1] < floor}
        solid(cv, m, "sl1", None, outline="sl2")
    if k <= 1:
        r = 4.5 * size + k * 4
        m = {q for q in ellipse(x, y, r + 1.2, (r + 1.2) * 0.8)} - ellipse(x, y, r, r * 0.8)
        cv.fill({q for q in m if floor is None or q[1] < floor}, "sl1" if k == 0 else "sl2")
    for j in range(10):
        a = j * math.tau / 10 + 0.3
        r0 = (6 + k * 4) * size
        r1 = r0 + (6 - k * 1.5) * size
        if k >= 2 and j % 2:
            continue
        for i in range(int(r1 - r0)):
            rr = r0 + i
            _put_if(cv, x + math.cos(a) * rr, y + math.sin(a) * rr * 0.8, "sl1" if i < 2 and k == 0 else "sl3", floor)


def impact_lines(cv, x, y, k, r0=10, r1=20, n=12, floor=None, c="sl3"):
    """Garis hantaman manga di sekitar titik (k 0..2)."""
    for j in range(n):
        if (j + k) % 3 == 2:
            continue
        a = j * math.tau / n + k * 0.13
        for i in range(int(r1 - r0) - k * 2):
            rr = r0 + k * 3 + i
            _put_if(cv, x + math.cos(a) * rr, y + math.sin(a) * rr * 0.7, c, floor)


def debris(cv, x, y, k, seed=0, n=7, power=1.0, floor=None):
    """Serpihan batu terlempar parabola dari titik hantaman (k 0..6)."""
    floor = floor if floor is not None else y + 1
    rnd = random.Random(seed)
    for j in range(n):
        vx = rnd.uniform(-3.0, 3.0) * power
        vy = rnd.uniform(4.2, 6.4) * power
        t = k + 0.6
        px = x + vx * t
        py = y - 1 - vy * t + 0.95 * t * t
        if py >= floor - 1:
            py = floor - 2  # mendarat
            if k >= 5:
                continue
        big = j % 3 == 0
        ix, iy = int(round(px)), int(round(py))
        m = {(ix, iy), (ix + 1, iy)}
        if big:
            m |= {(ix, iy - 1), (ix + 1, iy - 1), (ix + 2, iy)}
        m = {q for q in m if q[1] < floor}
        if not m:
            continue
        cv.fill(m, "rk1")
        low = max(q[1] for q in m)
        cv.fill({q for q in m if q[1] == low and q[0] > ix}, "rk2")
        if big:
            cv.fill({q for q in m if q[1] == low and q[0] == ix + 2}, "K")


def sparks(cv, x, y, k, seed=0, n=6, direction=None, floor=None):
    """Percikan logam (k 0..3): garis pendek kuning-putih yang terbang lalu padam."""
    rnd = random.Random(seed)
    for j in range(n):
        a = rnd.uniform(-math.pi, 0) if direction is None else _ang(direction + rnd.uniform(-40, 40))
        sp = rnd.uniform(2.0, 3.6)
        r = 1 + k * sp
        L = 2 if k < 2 else 1
        for i in range(L + 1):
            c = "W" if (i == 0 and k == 0) else ("Y" if k < 2 else "O")
            _put_if(cv, x + math.cos(a) * (r + i), y + math.sin(a) * (r + i) + 0.3 * k * k, c, floor)


def ground_impact(cv, x, y, k, size=1.0, floor=None, seed=0):
    """Hantaman tanah: retak di permukaan + gelombang kejut pipih + debu (k 0..7). y = baris lantai."""
    floor = floor if floor is not None else y + 1
    # retak: garis gelap bergerigi menyebar dari titik hantaman di permukaan lantai
    rnd = random.Random(seed)
    reach = min(k, 3) * 4 * size + 4
    if k <= 6:
        for s in (-1, 1):
            px, py = x, y
            steps = int(reach)
            for i in range(steps):
                px += s
                if rnd.random() < 0.35:
                    py = max(y - 1, min(y, py + rnd.choice((-1, 1))))
                cv.put(int(px), int(py), "K" if k < 5 else "rk2")
            # cabang retak
            bx = x + s * int(reach * 0.5)
            cv.put(bx, y - 1, "K" if k < 5 else "rk2")
            cv.put(bx + s, y - 2, "K" if k < 5 else "rk2")
    # gelombang kejut: elips pipih yang melebar (hanya setengah atas)
    if 1 <= k <= 5:
        rx = (6 + k * 6) * size
        ry = (1.6 + k * 0.6) * size
        ring = ellipse(x, y, rx + 1, ry + 1) - ellipse(x, y, rx, ry)
        cv.fill({q for q in ring if q[1] < floor and (k < 4 or (q[0] + q[1]) % 2 == 0)}, "sl2" if k < 3 else "sl3")
    if k <= 1:
        impact(cv, x, y - 3, k, size=size, floor=floor)
    if k >= 1:
        dust(cv, x, y, k - 1, size=size * 1.2, seed=seed, floor=floor)


def roar_lines(cv, x, y, k, floor=None):
    """Garis teriakan berbentuk kurung di depan mulut."""
    for j in range(3):
        r = 4 + j * 3 + (k % 2)
        for a in range(-40, 41, 8):
            aa = _ang(a)
            if (a // 8 + j) % 2 == 0:
                _put_if(cv, x + math.cos(aa) * r, y + math.sin(aa) * r, "sl3", floor)


def embers(cv, x, y, k, seed=0, n=8, spread=14, height=20, floor=None):
    """Bara amuk: partikel merah redup kecil yang naik dan padam (aksen halus, bukan aura penuh)."""
    rnd = random.Random(seed)
    for j in range(n):
        bx = x + rnd.uniform(-spread, spread)
        ph = (k + j * 3) % 8
        py = y - ph * height / 8.0
        c = "em1" if ph < 4 else "em2"
        if ph < 7:
            _put_if(cv, bx + math.sin(ph + j) * 1.2, py, c, floor)
            if ph < 2:
                _put_if(cv, bx + math.sin(ph + j) * 1.2, py + 1, "em2", floor)


def rage_rim(cv, pts, k):
    """Aura tipis: garis merah redup 1 px yang terputus-putus di sekeliling siluet (bukan cahaya merah penuh)."""
    for (x, y) in pts:
        if (x * 3 + y * 5 + k * 2) % 7 < 3:
            cv.put(x, y, "em2")


def sweat_drop(cv, x, y):
    cv.fill({(x, y), (x, y + 1), (x - 1, y + 2), (x + 1, y + 2), (x, y + 2), (x, y + 3)}, "I")
    cv.put(x, y + 3, "s")


def breath_puff(cv, x, y, k):
    r = 1.2 + k * 0.5
    m = ellipse(x + k * 1.5, y - k * 0.8, r, r * 0.8)
    if k >= 2:
        m = {q for q in m if (q[0] + q[1]) % 2 == 0}
        cv.fill(m, "smk")
    else:
        solid(cv, m, "smk", None, outline="sm2")


# ------------------------------------------------------------------ darah bergaya (sprite terpisah saja)
def _drop(cv, x, y, big, floor=None):
    x, y = int(round(x)), int(round(y))
    if big:
        m = {(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1), (x, y - 1)}
        m = {q for q in m if floor is None or q[1] < floor}
        cv.fill(m, "bl1")
        cv.fill({q for q in m if q[1] == y + 1}, "bl2")
        if (x, y - 1) in m:
            cv.put(x, y - 1, "bl0")
    else:
        _put_if(cv, x, y, "bl1", floor)


def blood_spray(cv, x, y, k, n=5, direction=0, cone=50, speed=2.6, seed=0, big_every=2, floor=None):
    """Tetesan merah yang terlempar searah tebasan lalu jatuh (gravitasi), makin kecil seiring umur k."""
    rnd = random.Random(seed)
    for j in range(n):
        a = _ang(direction + rnd.uniform(-cone, cone))
        sp = speed * rnd.uniform(0.7, 1.3)
        t = k + 0.7
        px = x + math.cos(a) * sp * t
        py = y + math.sin(a) * sp * t + 0.35 * t * t
        big = (j % big_every == 0) and k < 3
        if k >= 4 and j % 2:
            continue
        _drop(cv, px, py, big, floor)


def blood_splat(cv, x, y, k, r=3.0, floor=None):
    """Cipratan pusat kartun: bintang bulat kecil (k 0) lalu pecah jadi tetes (k >= 1). Bukan luka."""
    if k == 0:
        pts = []
        for i in range(10):
            a = i * math.tau / 10
            rr = r if i % 2 == 0 else r * 0.55
            pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
        m = {q for q in poly(pts) if floor is None or q[1] < floor}
        solid(cv, m, "bl1", "bl2", outline="bl3", shade_off=(1, 1))
        cv.put(int(x) - 1, int(y) - 1, "bl0")
    elif k == 1:
        for i in range(5):
            a = i * math.tau / 5 + 0.4
            _drop(cv, x + math.cos(a) * (r + 1.5), y + math.sin(a) * (r + 1.5), True, floor)


def blood_small(cv, x, y, k, direction=0, seed=1, floor=None):
    blood_spray(cv, x, y, k, n=4, direction=direction, cone=35, speed=2.2, seed=seed, big_every=3, floor=floor)


def blood_medium(cv, x, y, k, direction=0, seed=2, floor=None):
    if k <= 1:
        blood_splat(cv, x, y, k, r=2.4, floor=floor)
    blood_spray(cv, x, y, k, n=7, direction=direction, cone=45, speed=2.6, seed=seed, big_every=2, floor=floor)


def blood_burst(cv, x, y, k, direction=0, seed=3, floor=None):
    if k <= 1:
        blood_splat(cv, x, y, k, r=3.6, floor=floor)
    blood_spray(cv, x, y, k, n=10, direction=direction, cone=70, speed=3.0, seed=seed, big_every=2, floor=floor)
    blood_spray(cv, x, y, k, n=4, direction=direction + 180, cone=40, speed=1.6, seed=seed + 7, big_every=4, floor=floor)


def blood_arc(cv, cx, cy, r, a0, a1, k, seed=4, floor=None):
    """Tetesan mengikuti busur tebasan (searah ayunan), lalu jatuh."""
    rnd = random.Random(seed)
    n = 9
    for j in range(n):
        t = j / float(n - 1)
        a = _ang(a0 + (a1 - a0) * t)
        rr = r + rnd.uniform(-1.5, 1.5)
        x = cx + math.cos(a) * rr
        y = cy + math.sin(a) * rr + 0.4 * (k + 0.5) ** 2
        tang = a + (math.pi / 2 if a1 > a0 else -math.pi / 2)
        x += math.cos(tang) * k * 1.5
        if k >= 3 and j % 2:
            continue
        _drop(cv, x, y, j % 3 == 0 and k < 3, floor)


def blood_particles(cv, x, y, k, seed=5, n=10, floor=None):
    """Partikel halus 1 px yang melayang turun dan padam."""
    rnd = random.Random(seed)
    for j in range(n):
        px = x + rnd.uniform(-8, 8) + math.sin(k + j) * 0.8
        py = y + rnd.uniform(-6, 2) + k * 1.4
        if (j + k) % 4 == 3 or k >= 5:
            continue
        _put_if(cv, px, py, "bl1" if k < 3 else "bl2", floor)


def blood_ground(cv, x, y, k, seed=6, floor=None):
    """Bercak kecil di lantai (y = baris lantai): muncul, melebar sedikit, lalu memudar (dither)."""
    for j, (dx, w) in enumerate(((0, 3), (-6, 2), (5, 2), (9, 1))):
        if j > k + 1:
            continue
        ww = w + min(k, 2) * 0.5
        m = {(xx, y) for xx in range(int(x + dx - ww), int(x + dx + ww) + 1)}
        if k >= 4:
            m = {q for q in m if (q[0] + k) % 2 == 0}
        cv.fill(m, "bl2" if k < 3 else "bl3")
        if k < 3 and w >= 2:
            cv.put(int(x + dx), y, "bl1")


# ------------------------------------------------------------------ sprite VFX terpisah (untuk mesin)
class Spec:
    def __init__(self, name, n, fn, size, anchor, durs, kind, blood_level=None, note=""):
        self.name, self.n, self.fn, self.size, self.anchor = name, n, fn, size, anchor
        self.durs, self.kind, self.blood_level, self.note = durs, kind, blood_level, note


def _box(size, anchor):
    """Kanvas VFX: titik jangkar di (0, 0) koordinat dunia."""
    return (-anchor[0], -anchor[1], size[0], size[1])


SPECS = [
    Spec("slash_arc", 5, lambda cv, k: crescent(cv, 0, 0, 26, -150, 40, 9, k=max(0, k - 1)) if k < 4 else
         crescent(cv, 0, 0, 26, -150, 40, 9, k=3), (64, 64), (32, 32), [40, 40, 50, 60, 60], "slash",
         note="bulan sabit tebasan diagonal; jangkar = pusat putaran (bahu)"),
    Spec("sword_trail", 4, lambda cv, k: sword_trail(cv, (0, 0), -120, 30, 12, 30, k=k), (64, 64), (32, 32),
         [30, 40, 50, 60], "slash", note="smear pedang di antara dua sudut; jangkar = genggaman"),
    Spec("dust", 5, lambda cv, k: dust(cv, 0, 0, k, size=1.0, floor=1), (48, 16), (24, 15), [60, 60, 70, 80, 90],
         "ground", note="kepulan debu; jangkar = titik di lantai"),
    Spec("impact", 4, lambda cv, k: impact(cv, 0, 0, k), (48, 48), (24, 24), [40, 50, 60, 70], "impact",
         note="kilat hantaman"),
    Spec("debris", 7, lambda cv, k: debris(cv, 0, 0, k, seed=11, n=8, floor=1), (48, 32), (24, 31),
         [50, 50, 60, 60, 70, 70, 80], "ground", note="serpihan batu; jangkar = titik di lantai"),
    Spec("spark", 4, lambda cv, k: sparks(cv, 0, 0, k, seed=3, n=7), (24, 24), (12, 12), [30, 40, 50, 60], "impact",
         note="percikan logam"),
    Spec("ground_impact", 8, lambda cv, k: ground_impact(cv, 0, 0, k, size=1.0, floor=1, seed=9), (96, 40), (48, 39),
         [50, 60, 60, 70, 70, 80, 80, 90], "ground", note="retak + gelombang kejut + debu; jangkar = titik di lantai"),
    Spec("blood_small", 4, lambda cv, k: blood_small(cv, 0, 0, k), (32, 24), (8, 10), [50, 60, 60, 70], "blood", 1,
         note="tingkat 1: beberapa tetes searah tebasan"),
    Spec("blood_medium", 5, lambda cv, k: blood_medium(cv, 0, 0, k), (40, 28), (10, 12), [50, 50, 60, 60, 70], "blood",
         2, note="tingkat 2: cipratan kecil + tetes"),
    Spec("blood_burst", 6, lambda cv, k: blood_burst(cv, 0, 0, k), (48, 36), (18, 14), [40, 50, 50, 60, 60, 70], "blood",
         3, note="tingkat 3: cipratan bintang kartun + tetes ke dua arah"),
    Spec("blood_arc", 5, lambda cv, k: blood_arc(cv, 0, 0, 14, -120, 20, k), (48, 40), (24, 22), [40, 50, 60, 60, 70],
         "blood", 2, note="tetes mengikuti busur tebasan"),
    Spec("blood_particles", 6, lambda cv, k: blood_particles(cv, 0, 0, k), (32, 28), (16, 10), [60, 60, 60, 70, 70, 80],
         "blood", 1, note="partikel halus melayang turun"),
    Spec("blood_ground", 6, lambda cv, k: blood_ground(cv, 0, 0, k), (32, 4), (14, 0), [60, 70, 80, 90, 100, 120],
         "blood", 1, note="bercak kecil di lantai yang memudar; jangkar = baris lantai"),
]

# event bukan sprite: getaran layar dan hit-stop dijalankan mesin
EVENT_KINDS = {
    "screen_shake_trigger": {"type": "screen_shake", "note": "mesin menggetarkan kamera; px = amplitudo, ms = lama"},
    "hitstop": {"type": "hitstop", "note": "mesin membekukan penyerang dan target selama ms, hanya bila kena"},
}

BLOOD_LEVELS = {"0": [], "1": ["blood_small", "blood_particles"], "2": ["blood_medium", "blood_arc", "blood_ground"],
                "3": ["blood_burst", "blood_arc", "blood_ground"]}


def render_spec(spec, k):
    cv = Canvas(_box(spec.size, spec.anchor))
    spec.fn(cv, k)
    return cv
