"""Karakter teknologi, spesial, dan peran turnamen v2: Hacker, Normal GBLK, Wizard, Referee, Judge, Skeptic,
Champion, Defeated.

Champion: label registry "TOURNAMENT WINNER", tidak pernah "ABSOLUTE TRUTH". Laurel emas di kepala tidak dipakai
karena keputusan pemilik di Gerbang B (laurel emas diganti medali); lihat laporan.
"""
import math

import rig2 as R
import gear2 as G
import items2 as I
import props2 as P
from char2 import Char
from rig2 import kf, wag, BASE, RX
from moves import (fx_impact, fx_dust, fx_item, fx_puff, fx_sparkle, fx_hand_sparkle, fx_speed, fx_mark, fx_stars_head,
                   fx_sweat, fx_confetti, fx_smoke_cloud, idle_loop, hit_fn, defeat_fall, victory_raise)
from domain import (DomainChar, st_read, st_write, st_think, st_present, st_point, st_shocked, st_eureka, st_confused,
                    st_search, st_compare, st_defeat_sit, shirt, trousers, glasses, talk, fx_board, fx_bulb)


# ================================================================== HACKER
def hoodie_hood(cv, g, c=("Q", "q")):
    """Tudung hoodie dengan dua tonjolan telinga (telinga Gobyet tetap terbaca di dalam tudung)."""
    hx, hy = g.ihead()
    outer = R.ellipse(hx, hy - 0.5, 11.6, 10.4) | R.ellipse(hx - 11, hy + 1, 3.6, 4.0) | R.ellipse(hx + 11, hy + 1, 3.6, 4.0)
    outer -= {(x, y) for (x, y) in outer if y > hy + 8}
    opening = R.ellipse(hx, hy + 1.6, 8.6, 7.4)
    m = outer - opening
    R.solid(cv, m, c[0], c[1], shade_off=(2, 2))
    for s in (-1, 1):
        cv.fill(R.ellipse(hx + s * 11, hy + 1.5, 1.6, 2.0), c[1])
    for s in (-1, 1):
        cv.fill(R.capsule((hx + s * 3, hy + 8), (hx + s * 3, hy + 13), 0.4), "W")


class Hacker(Char):
    id = "hacker"
    name = "Hacker Gobyet"
    category = "domain"
    role = "technology"
    silhouette = ["hoodie_with_ear_hood", "laptop", "floating_terminal", "screen_glow"]

    def legs(self, cv, g):
        trousers(cv, g, ("l", "L"), ("W", "smk"))

    def torso(self, cv, g):
        m = R.ellipse(g.tcx, g.tcy, g.tw + 0.8, g.th + 0.8)
        R.solid(cv, m, "Q", "q", shade_off=(2, 2))
        cv.fill({(x, y) for (x, y) in R.inner(m) if abs(x - g.tcx) <= 4 and int(g.tcy) + 2 <= y <= int(g.tcy) + 4}, "q")

    def head(self, cv, g):
        R.head(cv, g)
        glow = g.p.get("glow")
        if glow:
            hx, hy = g.ihead()
            cv.fill({(hx - 6, hy + 6), (hx - 5, hy + 7), (hx + 5, hy + 7), (hx + 6, hy + 6)}, glow if glow != "Z" else "glw")

    def headgear(self, cv, g):
        hoodie_hood(cv, g)

    def arm(self, cv, g, i):
        R.arm(cv, g, i, sleeve="Q", r=2.0)

    def build(self):
        base = dict(sx=3, rh=(2, 1), lh=(-3, 1), rw="laptop_side", glow="Z", eyes="down", mouth="flat")

        def term(kind="terminal", x=RX + 15, y=6):
            return lambda t, p: p.update(fx=p.get("fx", []) + [lambda cv, g, t=t: P.terminal_window(cv, x, y, t, kind)])

        def typing(speed):
            def fn(t):
                p = dict(base)
                p["lh"] = (-3, 1 - ((t * speed) % 2))
                p["rh"] = (2, 1 - ((t * speed + 1) % 2))
                p["tail"] = wag(t, 12)
                if t == 9 and speed == 1:
                    p["eyes"] = "blink"
                term()(t * speed, p)
                return p
            return fn
        self.add("idle", 12, typing(1), ms=140, core="idle", label="hoodie, laptop, terminal hijau bergulir")
        self.add("typing", 12, typing(2), ms=80, label="mengetik cepat")

        def debugging(t):
            p = dict(base, eyes="angry", brows="raised")
            p["lh"] = (-3, 1 - (t % 2))
            p["tail"] = wag(t, 12)
            term("debug")(t, p)
            return p
        self.add("debugging", 12, debugging, ms=120, label="menyipit memburu baris merah")

        def error(t):
            # layar error -> Gobyet melihat layar -> diam -> lalu menatap penonton
            p = dict(base, glow="R")
            if t < 3:
                p.update(eyes="down")
            elif t < 9:
                p.update(eyes="down", mouth="flat", brows="flat")
            else:
                p.update(eyes="look", mouth="flat", brows="flat", hdy=0)
            p["tail"] = 0.0
            term("error")(t, p)
            return p
        self.add("error", 14, error, ms=150, loop=False, hold=8,
                 label="layar error, menatap layar, diam, lalu menatap penonton")

        def panic(t):
            p = dict(base, glow="R", eyes="wide", brows="up", mouth="shout", dx=(1 if t % 2 else -1), lh=(-9, -8), rh=(9, -8),
                     rw=None)
            p["tail"] = wag(t, 6, 2)
            p["fx"] = [fx_sweat(), fx_item("laptop_side", RX + 2, BASE - 1, 0, glow="R")]
            term("error")(t, p)
            return p
        self.add("panic", 6, panic, ms=80, label="panik: tangan ke kepala, laptop di lantai")

        def success(t):
            p = kf(t, [(0, dict(base)), (3, dict(base, rh=(10, -10), rw=None, eyes="happy", mouth="smile", lh=(-3, 1))), (11, dict(base))], 12,
                   loop=False)
            p["tail"] = wag(t, 12)
            if t >= 3:
                p["fx"] = [fx_item("laptop_side", RX - 2, BASE - 1, 0)] if False else []
            term("ok")(t, p)
            return p
        self.add("success", 12, success, ms=110, loop=False, label="tanda centang hijau, tinju naik")
        self.add("hit", 10, hit_fn(dict(base, eyes="look")), ms=100, loop=False, core="hit", label="tersentak, laptop goyah")

        def attack(t):
            p = typing(3)(t)
            p.update(eyes="angry", brows="angry", mouth="smirk")
            if t >= 6:
                p["fx"] = p.get("fx", []) + [fx_impact(RX + 30, 30, (t - 6) % 3, "glw")]
            return p
        self.add("attack", 12, attack, ms=80, loop=False, core="attack", label="mengetik serangan: kode hijau menyala")
        up = dict(base, rh=(4, -14), lh=(-4, -14), eyes="happy", mouth="smile")
        self.add("victory", 16, victory_raise(base, up, sparkle_hand=None,
                                              extra=lambda t, p: term("ok")(t, p)), ms=110, core="victory",
                 label="laptop diangkat, terminal OK")

        def defeat(t):
            p = st_defeat_sit(dict(base, rw=None), drops=[("laptop_side", RX + 10, BASE + 1, 0, {"glow": "R"})])(t)
            if t >= 4:
                p["fx"] = p.get("fx", []) + [lambda cv, g: P.terminal_window(cv, RX + 15, 6, 0, "error")]
            return p
        self.add("defeat", 16, defeat, ms=120, loop=False, hold=10, core="defeat", label="laptop error, terduduk lesu")


# ================================================================== NORMAL GBLK
class NormalGBLK(Char):
    id = "normal-gblk"
    name = "Normal GBLK Gobyet"
    category = "special"
    role = "default"
    caption = "GBLK = Gamers Berkembang Lewat Kebodohan"
    silhouette = ["plain_gobyet", "big_gblk_sign"]
    fallback = None

    def build(self):
        base = dict(sx=3, rh=(10, 2), rw="gblk_sign", rwa=-90, lh=(-9, 4))
        self.add("idle", 12, idle_loop(base, 12, look=(4, 6)), ms=140, core="idle", label="papan GBLK besar")

        def think(t):
            p = st_think(base, hand=(-1, -5))(t)
            p["rw"] = "gblk_sign"
            p["rh"] = (10, 2)
            p["lh"] = (-1, -5) if 3 <= t <= 12 else (-9, 4)
            return p
        self.add("think", 16, think, ms=120, label="berpikir sambil memegang papan")

        def confused(t):
            p = st_confused(base)(t)
            p["rw"], p["rwa"] = "gblk_sign", -90
            p["lh"] = p["rh"]
            p["rh"] = (10, 2)
            return p
        self.add("confused", 12, confused, ms=120, label="bingung, garuk kepala")

        def raise_(t):
            up = dict(base, rh=(8, -8), rwa=-90, mouth="shout", eyes="look")
            p = kf(t, [(0, dict(base)), (3, up), (5, dict(up, rh=(9, -10))), (7, up), (9, dict(up, rh=(9, -10))), (11, dict(base))], 12)
            p["tail"] = wag(t, 12)
            return p
        self.add("sign_raise", 12, raise_, ms=100, core="attack", label="papan GBLK diacungkan tinggi")
        up = dict(base, rh=(8, -10), rwa=-90, lh=(-9, -10), eyes="happy", mouth="smile")
        self.add("victory", 16, victory_raise(base, up, sparkle_hand=None,
                                              extra=lambda t, p: p.update(fx=[fx_confetti(7, t)]) if t >= 4 else None),
                 ms=110, core="victory", label="papan terangkat, konfeti")
        self.add("hit", 10, hit_fn(base, recoil=dict(rwa=-110)), ms=100, loop=False, core="hit", label="terhuyung, papan miring")

        def defeat(t):
            p = st_defeat_sit(dict(base, rw=None))(t)
            if 2 <= t < 5:
                p["rw"], p["rwa"] = "gblk_sign", -90 + (t - 1) * 30
            elif t >= 5:
                p["fx"] = p.get("fx", []) + [fx_item("gblk_sign", RX - 8, BASE - 2, 0)]
            return p
        self.add("defeat", 16, defeat, ms=120, loop=False, hold=10, core="defeat", label="papan GBLK roboh, terduduk")

        # tarian: 16 frame x 120 ms, ganti pose besar pada f0, f4, f8, f12
        def dance(poses, confetti=False):
            def fn(t):
                b = t // 4
                p = dict(base, **poses[b % len(poses)])
                p["tail"] = wag(t, 16, 2)
                if confetti:
                    p["fx"] = [fx_confetti(11, t)]
                return p
            return fn
        d1 = [dict(lean=-3, dx=-1, rh=(10, 0), eyes="side"), dict(lean=0, crouch=1, mouth="smile"), dict(lean=3, dx=1, eyes="side", rh=(11, 0)),
              dict(lean=0, crouch=1, mouth="smile")]
        d2 = [dict(lh=(-9, -10), mouth="smile", dy=-1), dict(crouch=2), dict(lh=(-3, 4), rh=(8, -9), mouth="o", dy=-1), dict(crouch=2)]
        d3 = [dict(rwa=-120, lean=-2, eyes="happy"), dict(rwa=-90, crouch=1), dict(rwa=-60, lean=2, eyes="happy"), dict(rwa=-90, crouch=1)]
        self.add("dance_01", 16, dance(d1), ms=120, label="goyang kiri-kanan")
        self.add("dance_02", 16, dance(d2), ms=120, label="lompat kecil, tangan bergantian naik")
        self.add("dance_03", 16, dance(d3), ms=120, label="papan diayun kiri-kanan")
        self.add("victory_dance", 16, dance([dict(d2[0], eyes="happy"), d1[1], dict(d3[2], eyes="happy"), d1[3]], confetti=True), ms=120,
                 label="tarian kemenangan dengan konfeti")


# ================================================================== WIZARD
def wizard_hat(cv, g, droop=0.0, lift=0):
    hx, hy = g.ihead()
    hy -= lift
    brim = R.ellipse(hx, hy - 5, 15.5, 2.8)
    s = math.sin(droop) * 1.5
    cone = R.poly([(hx - 9, hy - 6), (hx + 9, hy - 6), (hx + 4 + s, hy - 16), (hx + 2 + s * 1.5, hy - 23), (hx + 7 + s * 2, hy - 27),
                   (hx + 0 + s * 1.5, hy - 24), (hx - 3 + s, hy - 16)])
    R.solid(cv, cone, "3", "4", shade_off=(2, 2))
    R.solid(cv, brim, "3", "4", shade_off=(1, 1))
    cv.fill({(x, hy - 7) for x in range(hx - 8, hx + 9)}, "go1")
    for (dx, dy) in ((-3, -12), (2, -17), (-1, -20)):
        R.star(cv, hx + dx + int(s), hy + dy, "Y")


class Wizard(Char):
    id = "wizard"
    name = "Wizard Gobyet"
    category = "fantasy"
    faction = "fantasy"
    role = "magic"
    silhouette = ["tall_pointed_hat", "floor_robe", "tall_staff", "spellbook"]

    def legs(self, cv, g):
        if g.p.get("mode") == "sit":
            R.sit_legs(cv, g, fur="3")
        else:
            R.legs(cv, g, fur="B")

    def torso(self, cv, g):
        if g.p.get("mode") == "sit":
            R.solid(cv, R.ellipse(g.tcx, g.tcy, g.tw + 0.8, g.th + 0.6), "3", "4", shade_off=(2, 2))
            return
        G.robe(cv, g, ("3", "4"), flare=5.0, trim="go1", length=0)
        cv.fill({(int(g.tcx), y) for y in range(int(g.tcy - 3), int(g.hip_y + 3))}, "go1")

    def head(self, cv, g):
        R.head(cv, g)
        if g.p.get("soot"):
            hx, hy = g.ihead()
            for (dx, dy) in ((-6, 3), (5, 4), (-2, 6), (3, -2), (-5, -1)):
                cv.put(hx + dx, hy + dy, "l")

    def headgear(self, cv, g):
        if not g.p.get("hat_off"):
            wizard_hat(cv, g, droop=g.p.get("tail", 0.0), lift=g.p.get("hat_lift", 0))

    def arm(self, cv, g, i):
        R.arm(cv, g, i, sleeve="3", r=2.2)

    def build(self):
        base = dict(sx=3, rh=(11, 3), rw="staff", rwa=-85, lh=(-9, 3), lw="book_closed", cover=("p", "j"), glow=0.3)
        self.add("idle", 12, idle_loop(base, 12, look=(4, 6), extra=lambda t, p: p.update(glow=0.3 + 0.3 * (t % 6 < 3))), ms=130,
                 core="idle", label="topi runcing tinggi, jubah sampai lantai, tongkat bercahaya")
        cast = dict(base, rh=(13, -8), rwa=-60, lh=(-9, -4), eyes="angry", brows="angry", mouth="shout", lean=1)

        def cast_f(t):
            p = kf(t, [(0, dict(base)), (4, cast), (11, cast)], 12, loop=False)
            p["glow"] = min(1.5, t * 0.15)
            p["tail"] = wag(t, 12)
            if t >= 4:
                p["fx"] = [lambda cv, g, t=t: _magic_ring(cv, g, t)]
            return p
        self.add("cast", 12, cast_f, ms=100, loop=False, core="attack", label="merapal mantra, permata makin terang")

        def success(t):
            p = dict(cast, glow=1.5, eyes="happy", mouth="smile")
            p["tail"] = wag(t, 12)
            k = min(t, 4)
            p["fx"] = [lambda cv, g, k=k, t=t: (_burst(cv, RX + 40, 12, k), R.star(cv, RX + 46 - t, 20 + t, "Y"))]
            return p
        self.add("spell_success", 12, success, ms=100, loop=False, label="mantra berhasil: ledakan bintang")

        def fail(t):
            if t < 3:
                p = dict(cast, glow=1.0)
            else:
                p = dict(base, eyes="blink" if t < 7 else "side", brows="worried", mouth="o", soot=t >= 5, hat_lift=0, glow=0.0,
                         tilt=1)
            p["tail"] = wag(t, 16)
            fx = []
            if 3 <= t <= 9:
                fx.append(fx_smoke_cloud(RX, 26, min(t - 3, 4) if t < 7 else max(0, 4 - (t - 6))))
            if t >= 10:
                fx.append(fx_mark("?"))
            p["fx"] = fx
            return p
        self.add("spell_fail", 16, fail, ms=110, loop=False, hold=6, label="mantra gagal: POOF, wajah jelaga, bingung")
        self.add("read", 12, st_read(dict(base, lw=None), "book_open", cover=("p", "j")), ms=140, label="membaca buku mantra")
        self.add("confused", 12, st_confused(dict(base, lw=None)), ms=120, label="bingung")
        self.add("hit", 10, hit_fn(base, recoil=dict(rwa=-100, hat_lift=2)), ms=100, loop=False, core="hit", label="terkejut, topi terangkat")
        up = dict(base, rh=(9, -14), rwa=-90, lh=(-9, -6), mouth="smile", eyes="happy", glow=1.5)

        def vic_extra(t, p):
            if 4 <= t <= 13:
                p["fx"] = [lambda cv, g, t=t: _burst(cv, RX + 18 + (t % 3) * 8, 6 + (t % 2) * 4, t % 4)]
        self.add("victory", 16, victory_raise(base, up, sparkle_hand=None, extra=vic_extra), ms=110, core="victory",
                 label="tongkat terangkat, kembang api sihir")

        def defeat(t):
            p = st_defeat_sit(dict(base, rw=None, lw=None), drops=[("staff", RX - 14, BASE - 3, 0, {"glow": 0.0})])(t)
            if 3 <= t <= 9:
                p["fx"] = p.get("fx", []) + [fx_smoke_cloud(RX + 2, BASE - 10, min(t - 3, 3))]
            p["soot"] = t >= 6
            return p
        self.add("defeat", 16, defeat, ms=120, loop=False, hold=10, core="defeat", label="tongkat jatuh, asap, terduduk")


def _magic_ring(cv, g, t):
    x, y = g.hand[1]
    x, y = x + 20 * math.cos(math.radians(-60)), y + 20 * math.sin(math.radians(-60)) + 3
    for k in range(6):
        a = t * 0.6 + k * math.tau / 6
        cv.put(int(x + math.cos(a) * 6), int(y + math.sin(a) * 4), "mag" if k % 2 else "Y")


def _burst(cv, x, y, k):
    for a in range(0, 360, 45):
        r = math.radians(a)
        for d in range(2 + k, 4 + k * 2):
            cv.put(int(x + math.cos(r) * d), int(y + math.sin(r) * d), "Y" if d % 2 else "mag")
    R.star(cv, int(x), int(y), "W", big=True)


# ================================================================== REFEREE
class Referee(DomainChar):
    id = "referee"
    name = "Referee Gobyet"
    category = "role"
    role = "tournament-control"
    silhouette = ["striped_shirt", "whistle", "flag"]
    sleeve = "W"

    def legs(self, cv, g):
        trousers(cv, g, ("L", "l"), ("L", "K"))

    def torso(self, cv, g):
        m = R.ellipse(g.tcx, g.tcy, g.tw + 0.4, g.th + 0.4)
        R.solid(cv, m, "W", "smk", shade_off=(2, 2))
        cv.fill({(x, y) for (x, y) in R.inner(m) if (x - int(g.tcx)) % 4 in (0, 1)}, "L")
        cv.fill(R.capsule((g.tcx - 3, g.tcy - 6), (g.tcx + 2, g.tcy - 1), 0.4), "R")
        R.solid(cv, R.rect(int(g.tcx) + 1, int(g.tcy) - 2, 4, 3), "st1", None)

    def build(self):
        base = dict(sx=3, rh=(11, 2), rw="flag", rwa=-80, lh=(-8, 4), wave=0.0)

        def idle_extra(t, p):
            p["wave"] = wag(t, 12)
        self.add("idle", 12, idle_loop(base, 12, look=(3, 8), extra=idle_extra), ms=130, core="idle", label="kaus belang, peluit, bendera")

        def walk(dir_, start):
            def fn(t):
                ph = t * math.tau / 8
                p = dict(base, dx=start + dir_ * t * 3, lift_l=max(0, math.sin(ph)) * 3, lift_r=max(0, -math.sin(ph)) * 3,
                         eyes="side" if dir_ > 0 else "left", mouth="flat", wave=wag(t, 4))
                p["tail"] = wag(t, 8)
                return p
            return fn
        self.add("enter", 12, walk(1, -36), ms=100, loop=False, label="masuk arena dari kiri")
        self.add("exit", 12, walk(1, 0), ms=100, loop=False, label="keluar arena ke kanan")

        def start(t):
            up = dict(base, rh=(8, -14), rwa=-90, lh=(-2, -3), mouth="chomp", eyes="angry", brows="up")
            p = kf(t, [(0, dict(base)), (3, up), (9, up), (11, dict(base))], 12, loop=False)
            p["wave"] = wag(t, 6)
            p["tail"] = wag(t, 12)
            if 3 <= t <= 9:
                p["fx"] = [lambda cv, g, t=t: _whistle_lines(cv, g, t)]
            return p
        self.add("signal_start", 12, start, ms=100, loop=False, label="bendera naik, peluit ditiup: mulai!")

        def stop(t):
            x = dict(base, rh=(-4, -12), lh=(4, -12), rw="flag", rwa=-60, mouth="chomp", eyes="angry", brows="angry")
            p = kf(t, [(0, dict(base)), (3, x), (9, x), (11, dict(base))], 12, loop=False)
            p["tail"] = wag(t, 12)
            if 3 <= t <= 9:
                p["fx"] = [lambda cv, g, t=t: _whistle_lines(cv, g, t)]
            return p
        self.add("signal_stop", 12, stop, ms=100, loop=False, label="tangan bersilang di atas kepala: berhenti!")

        def winner(t):
            pt = dict(base, rh=(14, -8), rwa=-30, lean=2, mouth="smile", eyes="side")
            p = kf(t, [(0, dict(base)), (3, pt), (11, pt)], 12, loop=False)
            p["wave"] = wag(t, 4)
            p["tail"] = wag(t, 12)
            return p
        self.add("point_winner", 12, winner, ms=100, loop=False, label="bendera menunjuk pemenang")


def _whistle_lines(cv, g, t):
    hx, hy = g.ihead()
    for k in range(3):
        a = -0.8 + k * 0.8
        r = 4 + (t % 3)
        x, y = hx + 2 + math.cos(a) * r, hy + 6 + math.sin(a) * r
        cv.fill({(int(x), int(y)), (int(x + math.cos(a) * 2), int(y + math.sin(a) * 2))}, "K")


# ================================================================== JUDGE
class Judge(DomainChar):
    id = "judge"
    name = "Judge Gobyet"
    category = "role"
    role = "judging"
    silhouette = ["judge_robe_jabot", "desk", "score_sheet", "gavel"]
    sleeve = "L"

    def legs(self, cv, g):
        trousers(cv, g, ("L", "l"), ("L", "K"))

    def torso(self, cv, g):
        m = R.ellipse(g.tcx, g.tcy, g.tw + 1.2, g.th + 0.8)
        R.solid(cv, m, "L", "l", shade_off=(2, 2))
        cx, top = int(round(g.tcx)), int(round(g.tcy - g.th))
        jab = R.poly([(cx - 2, top + 1), (cx + 2, top + 1), (cx + 1, top + 6), (cx - 1, top + 6)])
        R.solid(cv, jab, "W", None, outline="smk")

    def front(self, cv, g):
        P.desk(cv, RX - 15, BASE - 15, w=30, h=12)
        sheet = R.rect(RX + 2, BASE - 18, 10, 4)
        R.solid(cv, sheet, "W", None, outline="smk")
        if g.p.get("score_mark"):
            P.text3(cv, str(g.p["score_mark"])[:1], RX + 4, BASE - 18, "cr1")

    def build(self):
        base = dict(sx=3, rh=(10, 4), rw="gavel", rwa=-40, lh=(-8, 5), lw="papers")
        self.add("idle", 12, idle_loop(base, 12, look=(3, 6)), ms=140, core="idle", label="jubah hakim di balik meja")
        self.add("read", 12, st_read(dict(base, lw=None), "papers"), ms=140, label="membaca argumen")
        self.add("compare", 12, st_compare(base, "papers", "papers"), ms=130, label="membandingkan dua argumen")

        def write(t):
            p = st_write(dict(base, rw=None), "clipboard", "pen")(t)
            p["lh"] = (-3, 2)
            p["score_mark"] = (t // 4) % 9 + 1 if t >= 4 else None
            return p
        self.add("write_score", 12, write, ms=110, label="menulis skor")
        self.add("think", 16, st_think(base), ms=120, label="menimbang")

        def finalize(t):
            up = dict(base, rh=(9, -8), rwa=-140, lw=None, brows="angry", mouth="flat")
            dn = dict(base, rh=(11, 4), rwa=-10, lw=None, mouth="shout")
            p = kf(t, [(0, dict(base)), (3, up), (5, dn), (8, dn), (11, dict(base, mouth="smile"))], 12, loop=False)
            p["tail"] = wag(t, 12)
            if t in (5, 6):
                p["fx"] = [fx_impact(RX + 22, BASE - 18, t - 5, "W")]
            return p
        self.add("finalize", 12, finalize, ms=100, loop=False, label="palu diketuk: putusan final")


# ================================================================== SKEPTIC
class Skeptic(DomainChar):
    id = "skeptic"
    name = "Skeptic Gobyet"
    category = "role"
    role = "falsification"
    silhouette = ["sweater", "monocle", "magnifier", "claim_card", "raised_brow"]
    sleeve = "V"

    def legs(self, cv, g):
        trousers(cv, g, ("e", "x"), ("le2", "K"))

    def torso(self, cv, g):
        m = R.ellipse(g.tcx, g.tcy, g.tw + 0.6, g.th + 0.6)
        R.solid(cv, m, "V", "v", shade_off=(2, 2))
        for (x, y) in R.inner(m):
            if (x + y) % 3 == 0 and y > g.tcy:
                cv.put(x, y, "v")
        cv.fill({(x, int(g.tcy - g.th) + 1) for x in range(int(g.tcx) - 3, int(g.tcx) + 4)}, "W")

    def head(self, cv, g):
        R.head(cv, g)
        hx, hy = g.ihead()
        ring = R.ellipse(hx + 4, hy, 3.3, 3.3) - R.ellipse(hx + 4, hy, 2.3, 2.3)
        cv.fill(ring, "go1")
        cv.fill(R.capsule((hx + 7, hy + 2), (hx + 9, hy + 9), 0.4), "go2")

    def build(self):
        base = dict(sx=3, rh=(10, 2), rw="magnifier", rwa=-60, lh=(-9, 1), lw="papers", eyes="look", brows="raised", mouth="flat")

        def inspect(t):
            # melihat klaim, diam, menyipit, menunjuk premis
            if t < 4:
                p = dict(base, lh=(4, -4), eyes="down")
            elif t < 7:
                p = dict(base, lh=(4, -4), eyes="down", brows="flat")
            elif t < 10:
                p = dict(base, lh=(4, -4), eyes="angry", brows="raised")
            else:
                p = dict(base, lh=(4, -4), rw=None, rh=(8, -6), eyes="angry", brows="raised", mouth="smirk")
            p["tail"] = wag(t, 14)
            return p
        self.add("idle", 12, idle_loop(base, 12, look=(4, 6)), ms=140, core="idle", label="alis terangkat, monokel, kaca pembesar")
        self.add("inspect", 14, inspect, ms=150, loop=False, hold=6, label="melihat klaim, diam, menyipit, menunjuk premis")

        def squint(t):
            p = dict(base, eyes="angry" if t % 8 < 6 else "blink", lean=2, hdx=1, rh=(6, -5), rwa=-20)
            p["tail"] = wag(t, 8)
            return p
        self.add("squint", 8, squint, ms=140, label="menyipit mendekat")
        self.add("point", 10, st_point(base, glyph="?"), ms=110, loop=False, label="menunjuk premis yang lemah")

        def found(t):
            p = kf(t, [(0, dict(base)), (3, dict(base, eyes="wide", brows="up", mouth="o", lh=(4, -6))), (11, dict(base, eyes="look", mouth="smirk", lh=(4, -6)))],
                   12, loop=False)
            p["tail"] = wag(t, 12)
            if t >= 3:
                p["fx"] = [fx_mark("!", dx=8, dy=-16), lambda cv, g: P.text3(cv, "X", int(g.hand[0][0]) - 1, int(g.hand[0][1]) - 7, "R")]
            return p
        self.add("contradiction_found", 12, found, ms=110, loop=False, label="kontradiksi ditemukan: tanda X merah")

        def counter(t):
            pose = dict(base, rh=(15, -6), rw=None, lean=3, eyes="angry", brows="angry", mouth="shout")
            p = kf(t, [(0, dict(base)), (3, pose), (8, pose), (11, dict(base))], 12, loop=False)
            p["tail"] = wag(t, 12)
            if 3 <= t <= 8:
                p["fx"] = [lambda cv, g, t=t: P.text3(cv, "?", RX + 30 + (t - 3) * 4, 22 - (t - 3), "R"), fx_speed(RX + 26, 30, 3, 6, -1)]
            return p
        self.add("counterattack", 12, counter, ms=90, loop=False, core="attack", label="serangan balik: tanda tanya melesat")

        def falsify(t):
            card = lambda cv, g, t=t: (R.solid(cv, R.rect(RX + 14, BASE - 22, 16, 12), "cm1", "cm2", shade_off=(1, 1)),
                                       [cv.fill({(x, BASE - 19 + k * 3) for x in range(RX + 16, RX + 27)}, "s") for k in range(3)],
                                       P.text3(cv, "X", RX + 20, BASE - 20, "R") if t >= 6 else None)
            up = dict(base, rh=(15, -12), rw=None, lean=1, eyes="angry", brows="angry")
            dn = dict(base, rh=(16, -4), rw=None, lean=3, mouth="shout")
            p = kf(t, [(0, dict(base)), (3, up), (5, dn), (8, dn), (11, dict(base, mouth="smirk"))], 12, loop=False)
            p["tail"] = wag(t, 12)
            p["fx_back"] = [card]
            if t in (5, 6):
                p["fx"] = [fx_impact(RX + 24, BASE - 18, t - 5, "W")]
            return p
        self.add("falsification", 12, falsify, ms=100, loop=False, label="stempel X pada kartu klaim")
        self.core_states(base, None, dict(base, rh=(6, -14), lh=(-9, -8), mouth="smirk"), [("magnifier", RX + 10, BASE - 3, 0)])


# ================================================================== CHAMPION
class Champion(Char):
    id = "champion"
    name = "Champion Gobyet"
    category = "role"
    role = "winner"
    label = "TOURNAMENT WINNER"
    silhouette = ["giant_trophy", "red_cape", "medal"]

    def back(self, cv, g):
        G.cape(cv, g, ("cr1", "cr2"), length=14, sway=g.p.get("cape", 0.0), width=1.6)

    def torso(self, cv, g):
        R.torso(cv, g)
        cv.fill(R.capsule((g.tcx - 4, g.tcy - 6), (g.tcx, g.tcy - 1), 0.6) | R.capsule((g.tcx + 4, g.tcy - 6), (g.tcx, g.tcy - 1), 0.6), "cr1")
        R.solid(cv, R.ellipse(g.tcx, g.tcy + 1, 2.4, 2.4), "go1", "go2", shade_off=(1, 1))

    def build(self):
        base = dict(sx=4, rh=(10, 0), rw="trophy", lh=(-9, 4), mouth="smile")

        def tr(t):
            up = dict(base, rh=(2, -16), lh=(-3, -15), eyes="happy", mouth="smile")
            p = kf(t, [(0, dict(base)), (4, up), (8, dict(up, crouch=1)), (12, up), (15, up)], 16)
            p["tail"] = wag(t, 16, 2)
            p["cape"] = wag(t, 16, 2)
            if 4 <= t:
                p["fx"] = [fx_sparkle(RX + 2 + (t % 3), 2, t)]
            return p
        self.add("idle", 12, idle_loop(base, 12, extra=lambda t, p: p.update(cape=wag(t, 12))), ms=140, core="idle",
                 label="memamerkan piala, jubah merah, medali")
        self.add("trophy_raise", 16, tr, ms=110, core="victory", label="piala diangkat tinggi dengan dua tangan")

        def victory(t):
            p = victory_raise(base, dict(base, rh=(6, -14), lh=(-9, -9), eyes="happy"), sparkle_hand=1)(t)
            p["cape"] = wag(t, 16, 2)
            return p
        self.add("victory", 16, victory, ms=110, label="piala terangkat, lompat")

        def celebrate(t):
            p = dict(base, dy=-2 if t % 4 in (1, 2) else 0, lh=(-9, -10 if t % 8 < 4 else 2), rh=(10, -4), eyes="happy", mouth="smile")
            p["tail"] = wag(t, 8, 2)
            p["cape"] = wag(t, 8, 2)
            p["fx"] = [fx_confetti(3, t)]
            return p
        self.add("celebrate", 8, celebrate, ms=100, label="lompat-lompat dengan konfeti")

        def dance(t):
            b = t // 4
            poses = [dict(lean=-3, dx=-1, lh=(-9, -9)), dict(crouch=1), dict(lean=3, dx=1, lh=(-3, 3), rh=(10, -8)), dict(crouch=1)]
            p = dict(base, eyes="happy", **poses[b])
            p["tail"] = wag(t, 16, 2)
            p["cape"] = wag(t, 16, 2)
            return p
        self.add("dance", 16, dance, ms=120, label="tarian juara (16 frame, beat f0/f4/f8/f12)")


# ================================================================== DEFEATED
class Defeated(Char):
    id = "defeated"
    name = "Defeated Gobyet"
    category = "role"
    role = "loser"
    silhouette = ["slumped_sitting", "fallen_sword", "tired_face"]

    def build(self):
        base = dict(sx=4, rh=(10, 3), rw="sword", rwa=-60, lh=(-9, 4), eyes="relief", brows="worried", mouth="frown")
        self.add("hit", 10, hit_fn(dict(base, eyes="look", brows="flat")), ms=100, loop=False, label="terkena")

        def stagger(t):
            p = kf(t, [(0, dict(base, lean=-2, dx=-1)), (3, dict(base, lean=2, dx=1, lift_l=2)), (6, dict(base, lean=-2, dx=-1, lift_r=2))], 9)
            p["tail"] = wag(t, 9)
            p["fx"] = [fx_stars_head(t)]
            return p
        self.add("stagger", 9, stagger, ms=110, label="sempoyongan")
        self.add("fall", 16, defeat_fall(base, drops=[("sword", RX + 8, BASE - 3, 0)], early_drop=3), ms=120, loop=False, hold=10,
                 core="defeat", label="jatuh terduduk lalu rebah")

        def sit(t):
            p = dict(base, mode="sit", rw=None, rh=(9, 4), lh=(-9, 4), hdy=1 if t % 12 < 6 else 0)
            p["tail"] = 0.0
            fx = [fx_item("sword", RX + 8, BASE - 2, 0)]
            if t % 12 >= 6:
                k = t % 6
                fx.append(fx_puff(RX + 12 + k, BASE - 26 - k * 2, 1.3 + k * 0.25))
            p["fx"] = fx
            return p
        self.add("sit", 12, sit, ms=140, core="idle", label="duduk lesu, pedang di lantai, menghela napas")

        def leave(t):
            ph = t * math.tau / 8
            p = dict(base, rw=None, dx=-t * 3, lift_l=max(0, math.sin(ph)) * 2, lift_r=max(0, -math.sin(ph)) * 2, eyes="left", hdy=1,
                     lh=(-8, 6), rh=(8, 6))
            p["tail"] = wag(t, 8)
            p["fx"] = [fx_item("sword", RX + 8, BASE - 2, 0)] if t < 6 else []
            return p
        self.add("leave", 16, leave, ms=110, loop=False, label="berjalan pergi lesu ke kiri")


CHARS = [Hacker, NormalGBLK, Wizard, Referee, Judge, Skeptic, Champion, Defeated]
