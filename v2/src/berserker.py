"""Berserker Gobyet: pejuang dark fantasy berpedang raksasa (arketipe "pendekar pedang raksasa berzirah hitam").

Desain orisinal yang hanya memakai prinsip umum arketipe itu: zirah hitam yang babak belur dan asimetris, pedang
dua tangan selebar papan yang panjangnya melebihi tinggi badan, jubah pendek compang-camping, kuda-kuda rendah
yang agresif. Tidak menyalin desain karakter tertentu.

Identitas Gobyet tetap: kepala, wajah, telinga, mata, ekor, dan proporsi badan memakai rig v2 yang sama dengan
38 karakter lain (skala piksel sama). Yang besar hanya zirah dan pedang, jadi kanvasnya diperluas menjadi
144x100 (koordinat rig sama; jangkar kaki dan lantai tidak bergeser relatif terhadap badan).

Lapisan: karakter (badan + zirah), senjata, VFX diekspor terpisah (lihat char2.render(layer=...)).
Darah tidak pernah digambar di sheet karakter; darah adalah sprite VFX terpisah (vfx2.py) yang dimunculkan
mesin hanya saat serangan kena (event "hit").
"""
import math

import rig2 as R
import items2 as I
from char2 import Char
from rig2 import Frame2, solid, ellipse, rect, chain, inner, poly

# Kanvas: jendela koordinat rig (x0, y0, w, h). Jangkar kaki di gambar = (56, 95).
BOX = (-28, -36, 144, 100)
GX, GY = -BOX[0], -BOX[1]  # offset rig -> piksel gambar


# ------------------------------------------------------------------ pedang raksasa
BLADE_L = 40.0  # ujung bilah lurus; ujung tumpul berakhir di BLADE_L + 3.5
HANDLE = 9.5


def slab_sword(cv, grip, ang, p):
    """Pedang dua tangan selebar papan: gagang panjang berbalut kulit, pelindung tangan sederhana dari besi,
    pangkal bilah diperkuat paku keling, bilah besi gelap yang tebal dengan tepi aus, takik, dan goresan.
    grip = tangan kanan (dekat pelindung tangan); tangan kiri memegang gagang 4.5 px di belakangnya."""
    f = Frame2(grip, ang)
    part = p.get("_sword_part")  # None = utuh, "handle" = hanya gagang (dipakai saat bilah di belakang badan)
    # gagang
    solid(cv, f.rect(-HANDLE, 1.6, -1.3, 1.3), "le2", None)
    for u in (-8.0, -5.5, -3.0, -0.5):
        cv.fill(f.line([(u, -0.6), (u + 0.6, 0.6)], 0.45), "le1")
    solid(cv, f.ell(-HANDLE - 1.2, 0, 1.9, 1.9), "bk1", "bk2", shade_off=(1, 1))
    if part == "handle":
        _guard(cv, f)
        return
    # bilah: segi enam panjang dengan ujung tumpul miring, takik di tepi
    L = BLADE_L
    w = 4.7
    blade = f.poly([(3.0, -w), (L, -w), (L + 3.6, -1.4), (L + 3.6, 1.2), (L - 0.5, w), (3.0, w)])
    for (u, side) in ((15.0, -1), (27.0, 1), (33.5, -1)):
        blade -= f.poly([(u - 1.2, side * (w + 0.8)), (u, side * (w - 1.6)), (u + 1.2, side * (w + 0.8))])
    solid(cv, blade, "sw1", "sw2", shade_off=(1, 1))
    body = inner(blade)
    # tepi aus terang di sisi atas, tepi bawah gelap: bilah terbaca tebal
    cv.fill({q for q in f.line([(5.0, -w + 1.0), (L + 1.0, -w + 1.0)], 0.5) if q in body}, "ir1")
    cv.fill({q for q in f.line([(5.0, w - 1.0), (L - 1.0, w - 1.0)], 0.5) if q in body}, "sw2")
    # pangkal diperkuat: pelat gelap + dua paku keling
    cv.fill({q for q in f.rect(3.2, 7.6, -w + 1.2, w - 1.2) if q in body}, "bk2")
    for (u, v) in ((5.4, -1.8), (5.4, 1.8)):
        x, y = f.world(u, v)
        cv.put(int(x), int(y), "bk0")
    # goresan
    for seg in (((11.0, -0.8), (13.5, 0.4)), ((21.0, 0.8), (23.5, -0.6)), ((29.0, -0.4), (30.5, 0.9))):
        cv.fill({q for q in f.line(list(seg), 0.4) if q in body}, "sw2")
    _guard(cv, f)


def _guard(cv, f):
    """Pelindung tangan: palang besi aus sederhana (lebih terang dari sarung tangan supaya keduanya terpisah)."""
    m = f.rect(1.0, 3.3, -5.6, 5.6)
    solid(cv, m, "sw1", "sw2", shade_off=(1, 1))
    cv.fill({q for q in f.line([(1.6, -4.8), (1.6, 4.8)], 0.45) if q in inner(m)}, "ir1")


I.register("slab_sword", slab_sword)


def sword_point(grip, ang, u):
    """Titik dunia pada jarak u sepanjang pedang (untuk efek: percikan di ujung, jejak)."""
    a = math.radians(ang)
    return grip[0] + u * math.cos(a), grip[1] + u * math.sin(a)


TIP = BLADE_L + 3.6


# ------------------------------------------------------------------ zirah
def jag(n, a, b, amp, seed=0):
    """Tepi compang-camping deterministik: n titik dari a ke b dengan simpangan bergantian."""
    out = []
    for k in range(n + 1):
        t = k / float(n)
        x = a[0] + (b[0] - a[0]) * t
        y = a[1] + (b[1] - a[1]) * t
        d = amp * (1.0 if (k + seed) % 2 == 0 else -0.35) * (0.6 + 0.4 * ((k * 7 + seed * 3) % 5) / 4.0)
        out.append((x, y + d))
    return out


class Berserker(Char):
    id = "berserker"
    name = "Berserker Gobyet"
    category = "fantasy"
    faction = None
    role = "giant_sword"
    silhouette = ["giant_slab_greatsword", "asymmetric_black_armor", "big_left_pauldron", "torn_short_cloak",
                  "low_crouched_stance"]
    body = {"torso_w": 8.0, "torso_h": 6.8, "shoulder": 7.0}
    canvas = BOX
    tail_side = -1
    dmg = 0  # 0 normal, 1 damaged, 2 heavily damaged (visual saja)
    damage_levels = True
    note = ("Kanvas 144x100 (badan Gobyet tetap skala yang sama). Lapisan body/weapon/vfx, tiga tingkat kerusakan, "
            "durasi per frame, event hit/hitstop/screen_shake. Darah: sprite VFX terpisah, hanya saat kena.")

    def __init__(self, dmg=0):
        self.dmg = dmg
        Char.__init__(self)

    # ---- pegangan dua tangan: tangan kiri dikunci ke gagang setelah pose dibulatkan
    def post_pose(self, p):
        if p.get("two") and p.get("rw"):
            a = math.radians(p["rwa"])
            d = p.get("grip_gap", 6.0)
            rx, ry = p["rh"]
            p["lh"] = (int(round(rx - d * math.cos(a))), int(round(ry - d * math.sin(a))))
            p["grip2"] = True

    # ---- jubah pendek compang-camping di punggung
    def back(self, cv, g):
        p = g.p
        gs = p.get("ground_sword")
        if gs and not p.get("_no_weapon"):  # pedang tergeletak di lantai (defeat)
            slab_sword(cv, (gs[0], gs[1]), gs[2], p)
        if p.get("mode") == "sit" and p.get("cloak_off"):
            return
        sway = p.get("cape", 0.0)
        s = math.sin(sway) * 1.4
        lift = p.get("cloak_lift", 0.0)  # angin saat melompat/berlari: jubah terangkat ke belakang
        sx0, sy0 = g.sh[0]
        sx1, sy1 = g.sh[1]
        length = 10.0 - self.dmg * 1.5
        hem_y = g.tcy + length - lift * 0.6
        back_x = sx0 - 12.5 - lift * 1.2 + s
        top = [(sx1 - 1.0, sy1 - 2.0), (sx0 - 1.0, sy0 - 2.5)]
        side = [(sx0 - 6.0, sy0 + 0.5), (back_x, hem_y - 2.0 - lift * 0.5)]
        hem = jag(6, (back_x, hem_y - lift * 0.5), (g.tcx + 4.0 + s * 0.5, g.tcy + length - 2.5), 2.2, seed=self.dmg)
        m = poly(top + side + hem + [(sx1 + 1.5, sy1 + 4.0)])
        holes = {0: [], 1: [(-15.5, 4.5)], 2: [(-15.5, 4.5), (-11.5, 6.5), (-18.0, 2.0)]}[self.dmg]
        for (hx, hy) in holes:
            m -= ellipse(g.tcx + hx - lift * 0.4, g.tcy + hy - lift * 0.4, 1.1, 0.9)
        solid(cv, m, "cl1", "cl2", shade_off=(2, 2))
        # lipatan
        for k in (-4.0, -8.0):
            cv.fill({(x, y) for (x, y) in inner(m) if abs(x - (g.tcx + k + s * 0.3)) < 0.6 and y > g.tcy}, "cl2")

    # ---- kaki: celana gelap, pelindung lutut, greave, sepatu bot besar
    def legs(self, cv, g):
        p = g.p
        if p.get("mode") == "sit":
            for i, s in enumerate((-1, 1)):
                solid(cv, ellipse(g.tcx + s * 5.2, g.tcy + 5.7, 4.4, 2.9), "bk2", "bk3")
            for i, s in enumerate((-1, 1)):
                fx, fy = g.feet[i]
                self._boot(cv, fx, fy, s, small=True)
            return
        c = p["crouch"]
        for i, side in enumerate((-1, 1)):
            hx, hy = g.hips[i]
            fx, fy = g.feet[i]
            knee = ((hx + fx) / 2.0 + side * (0.6 + c * 0.55), (hy + fy) / 2.0 - c * 0.15)
            solid(cv, chain([(hx, hy), knee], 2.6), "bk3", None)
            solid(cv, chain([knee, (fx, fy - 2.0)], 2.4), "bk1", "bk2", shade_off=(1, 1))
            solid(cv, ellipse(knee[0], knee[1], 2.1, 1.9), "bk1", "bk2", shade_off=(1, 1))
            cv.put(int(knee[0]) - 1, int(knee[1]) - 1, "bk0")
        for i, side in enumerate((-1, 1)):
            fx, fy = g.feet[i]
            self._boot(cv, fx, fy, side)

    def _boot(self, cv, fx, fy, side, small=False):
        r = 3.0 if small else 3.7
        m = ellipse(fx + side * 1.3, fy, r, 2.1) | rect(int(round(fx)) - 2, int(round(fy)) - 4, 5, 4)
        solid(cv, m, "le2", "D", shade_off=(1, 1))
        # tutup jari besi dan lipatan atas bot
        cv.fill({(x, y) for (x, y) in inner(m) if y == int(round(fy)) - 3}, "D")
        tx = int(round(fx + side * 2.6))
        cv.fill({(tx, int(round(fy))), (tx - side, int(round(fy)))}, "bk1")

    def _waist(self, cv, g):
        """Sabuk kulit, bulu gelap di pinggul kiri, kain merah redup yang sobek di depan."""
        p = g.p
        if p.get("mode") == "sit":
            y = int(round(g.tcy + g.th - 1.5))
        else:
            y = int(round(g.hip_y - 1.5))
        cx = g.cx + p["lean"] * 0.3
        # bulu bergerigi menggantung di pinggul kiri (belakang)
        fur_pts = [(cx - 9.5, y - 1), (cx - 1.5, y - 1)] + [(cx - 2.0 - k * 1.6, y + (4.2 if k % 2 == 0 else 2.2)) for k in range(5)]
        fur_pts.append((cx - 10.0, y + 2.6))
        solid(cv, poly(fur_pts), "df1", "df2", shade_off=(1, 1))
        # kain merah redup: dua lidah sobek di depan kanan
        sw = math.sin(p.get("cape", 0.0)) * 0.8
        for k, (x0, ln) in enumerate(((cx + 2.0, 6.5 - self.dmg), (cx + 5.0, 4.8))):
            m = poly([(x0 - 1.4, y), (x0 + 1.6, y), (x0 + 1.2 + sw, y + ln), (x0 + 0.2 + sw, y + ln - 1.4),
                      (x0 - 0.8 + sw, y + ln + 0.6)])
            solid(cv, m, "mr1", "mr2", shade_off=(1, 1))
        # sabuk
        belt = {(x, yy) for x in range(int(cx - 9), int(cx + 9) + 1) for yy in (y - 1, y)}
        solid(cv, belt, "le1", "le2", shade_off=(0, 1))
        cv.fill(rect(int(cx) + 1, y - 1, 2, 2), "bk0")

    # ---- badan: pelat dada bersegmen, tali silang, kerah bulu
    def torso(self, cv, g):
        p = g.p
        tcx, tcy = g.tcx, g.tcy
        if p.get("mode") == "sit" and p.get("plate_off"):
            R.torso(cv, g)
            return
        if p.get("arm0_behind") and not p.get("hide_arm_0"):
            # lengan kiri (jauh) lewat di belakang dada: hanya lengan bawah dan sarung tangan yang terlihat
            pts = [g.sh[0]] + ([g.elbow[0]] if g.elbow[0] else []) + [g.hand[0]]
            solid(cv, chain(pts, 2.3), "bk2", None)
        m = ellipse(tcx, tcy, g.tw + 0.4, g.th + 0.4)
        solid(cv, m, "bk1", "bk2", shade_off=(2, 2))
        body = inner(m)
        cx = int(round(tcx))
        # tepi atas-kiri aus (cahaya kiri atas)
        cv.fill({(x, y) for (x, y) in body if ((x - 1, y) not in m or (x, y - 1) not in m) and x < tcx + 2 and y < tcy + 1}, "bk0")
        # segmen bawah (lame) dan rusuk tengah
        for dy in (2, 4):
            yy = int(round(tcy + dy))
            cv.fill({(x, yy) for (x, y) in body if y == yy and abs(x - tcx) < g.tw - 1}, "bk2")
        cv.fill({(cx, y) for (x, y) in body if x == cx and y < tcy + 1}, "bk2")
        # goresan dan penyok sesuai tingkat kerusakan (sisi kiri dada: tidak tertutup tangan saat memegang pedang)
        ty = int(round(tcy))
        scratches = [((cx + 3, ty - 2), (cx + 5, ty - 1))]
        if self.dmg >= 1:
            scratches += [((cx, ty - 4), (cx + 3, ty - 1)), ((cx + 2, ty - 4), (cx + 5, ty - 2)), ((cx + 4, ty + 1), (cx + 6, ty + 2))]
        for a, b in scratches:
            cv.fill({q for q in chain([a, b], 0.45) if q in body}, "bk0")
        if self.dmg >= 1:  # penyok: lekuk gelap dengan tepi terang
            cv.fill({(cx + 1, ty + 1), (cx + 2, ty + 1), (cx + 1, ty + 2)}, "bk3")
            cv.fill({(cx, ty), (cx + 1, ty)}, "bk0")
        if self.dmg >= 2:  # pelat sompal: bulu Gobyet terlihat di bawahnya, retak menjalar
            hole = poly([(tcx + 0.5, tcy - 1.0), (tcx + 4.5, tcy - 2.5), (tcx + 6.0, tcy + 1.0), (tcx + 3.5, tcy + 3.5),
                         (tcx + 0.5, tcy + 2.5)])
            hole &= body
            cv.fill(hole, "B")
            cv.fill({q for q in hole if (q[0] + 1, q[1] + 1) not in hole}, "b")
            cv.fill(R.edge(hole), "K")
            for pts in (((tcx + 1.0, tcy - 1.0), (tcx - 1.0, tcy - 4.0), (tcx - 2.0, tcy - 5.5)),
                        ((tcx + 5.0, tcy - 2.0), (tcx + 6.5, tcy - 4.0))):
                cv.fill({q for q in chain(list(pts), 0.45) if q in body}, "K")
        self._waist(cv, g)
        # pauldron (di bawah kepala, jadi kepala menutupi tepinya, bukan sebaliknya)
        self._pauldron_left(cv, g)
        self._shoulder_right(cv, g)
        # kerah bulu gelap
        hx = g.hx
        col = [(hx - 8.5, tcy - 5.0)] + [(hx - 8.0 + k * 2.0, tcy - 5.6 - (1.6 if k % 2 else 0.0)) for k in range(9)] + \
              [(hx + 8.5, tcy - 5.0), (hx + 6.0, tcy - 2.6), (hx - 6.0, tcy - 2.6)]
        solid(cv, poly(col), "df1", "df2", shade_off=(1, 1))

    def _pauldron_left(self, cv, g):
        """Pauldron kiri besar berlapis tiga: lapis bawah dulu, lapis atas menutupi."""
        sx, sy = g.sh[0]
        sx -= 1.0
        lames = [(sx - 2.2, sy + 4.4, 5.0, 2.3), (sx - 1.6, sy + 2.0, 5.8, 2.7), (sx - 1.0, sy - 0.8, 6.8, 4.0)]
        for k, (x, y, rx, ry) in enumerate(lames):
            m = ellipse(x, y, rx, ry)
            if self.dmg >= 2 and k == 0:  # lapis bawah hilang sebagian
                m = {q for q in m if q[0] > x - 1}
            if self.dmg >= 2 and k == 2:  # lapis atas sompal di tepi luar
                m -= poly([(x - 8.0, y - 4.0), (x - 2.5, y - 2.0), (x - 4.5, y + 0.5), (x - 8.0, y + 1.0)])
            solid(cv, m, "bk1", "bk2", shade_off=(1, 1))
            cv.fill({(xx, yy) for (xx, yy) in R.edge(m) if (xx, yy - 1) in m and yy > y}, "K")
        top = ellipse(lames[-1][0], lames[-1][1], lames[-1][2], lames[-1][3])
        if self.dmg >= 2:
            x, y = lames[-1][0], lames[-1][1]
            top -= poly([(x - 8.0, y - 4.0), (x - 2.5, y - 2.0), (x - 4.5, y + 0.5), (x - 8.0, y + 1.0)])
        inn = inner(top)
        cv.fill({(x, y) for (x, y) in inn if (x, y - 1) not in inn and x < sx + 2}, "bk0")
        # punggung tengah (rusuk) + paku keling
        ridge_y = int(round(sy - 2.0))
        cv.fill({(x, ridge_y) for x in range(int(sx - 4), int(sx + 3)) if (x, ridge_y) in inn}, "bk3")
        for dx in (-3, 0):
            cv.put(int(sx) + dx, int(round(sy + 0.5)), "bk0")
        if self.dmg >= 1:  # takik penyok di tepi luar
            cv.fill({(int(sx - 5), int(sy - 2)), (int(sx - 5), int(sy - 1)), (int(sx - 4), int(sy - 2))}, "K")
        if self.dmg >= 2:  # retak
            cv.fill({q for q in chain([(sx - 1.0, sy - 4.0), (sx - 2.0, sy - 1.5), (sx - 1.0, sy + 0.5)], 0.45) if q in inn}, "K")

    def _shoulder_right(self, cv, g):
        """Bahu kanan: hanya tali kulit dan cop kecil (asimetris)."""
        sx, sy = g.sh[1]
        solid(cv, ellipse(sx + 0.6, sy - 0.4, 2.7, 2.1), "bk1", "bk2", shade_off=(1, 1))
        cv.put(int(sx), int(sy) - 1, "bk0")

    # ---- lengan: kiri berzirah penuh, kanan lengan atas terbuka (bulu) + vambrace
    def arm(self, cv, g, i):
        if i == 0 and g.p.get("arm0_behind"):
            return
        pts = [g.sh[i]] + ([g.elbow[i]] if g.elbow[i] else []) + [g.hand[i]]
        if i == 0:
            solid(cv, chain(pts, 2.3), "bk2", None)
        else:
            solid(cv, chain(pts, 2.1), "B", None)
            # tali kulit di lengan atas
            sx, sy = g.sh[1]
            e = g.elbow[1] or g.hand[1]
            bx, by = sx + (e[0] - sx) * 0.45, sy + (e[1] - sy) * 0.45
            cv.fill({q for q in ellipse(bx, by, 2.2, 1.0) if q in chain(pts, 2.1)}, "le2")
        # vambrace: pelat lengan bawah (siku -> dekat tangan)
        e = g.elbow[i] or g.sh[i]
        hx, hy = g.hand[i]
        a = (e[0] + (hx - e[0]) * 0.15, e[1] + (hy - e[1]) * 0.15)
        b = (e[0] + (hx - e[0]) * 0.8, e[1] + (hy - e[1]) * 0.8)
        solid(cv, chain([a, b], 2.4), "bk1", "bk2", shade_off=(1, 1))
        if g.elbow[i]:
            solid(cv, ellipse(e[0], e[1], 2.0, 2.0), "bk1", "bk2", shade_off=(1, 1))

    def over_arm(self, cv, g, i):
        # bilah di punggung (rw_back): gagang tetap digambar di depan badan, di bawah tangan
        p = g.p
        if i == 1 and p.get("rw") and p.get("rw_back") and not p.get("_no_weapon"):
            slab_sword(cv, g.hand[1], p["rwa"], dict(p, _sword_part="handle"))

    def hand(self, cv, g, i):
        """Sarung tangan besi berat."""
        hx, hy = g.hand[i]
        m = ellipse(hx, hy, 2.6, 2.4)
        solid(cv, m, "bk1", "bk2", shade_off=(1, 1))
        ix, iy = int(round(hx)), int(round(hy))
        cv.fill({(ix - 1, iy - 1), (ix, iy - 1)}, "bk0")

    def build(self):
        from berserker_moves import build_states, BRIEF_NAMES
        build_states(self)
        self.aliases = dict(BRIEF_NAMES)


CHARS = [Berserker]
