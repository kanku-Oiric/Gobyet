"""Faksi Knight v2: Heavy Knight, Archer, Man-at-Arms, Assassin.

Bahasa visual faksi: baja kebiruan (st0-st3), putih, aksen merah tua. Zirah mengambil porsi besar tubuh,
wajah Gobyet tetap terlihat lewat jendela helm, telinga menyembul di sisi helm.
"""
import math

import rig2 as R
import gear2 as G
import items2 as I
from char2 import Char
from rig2 import kf, wag, BASE, RX


from moves import (fx_impact, fx_dust, fx_stars, fx_item, fx_puff, fx_sparkle, fx_hand_sparkle, fx_speed, fx_mark,
                   fx_smoke_cloud, fx_stars_head, idle_loop, hit_fn, defeat_fall, victory_raise)

fx_item_ground = fx_item


# ================================================================== HEAVY KNIGHT
class HeavyKnight(Char):
    id = "knight-heavy"
    name = "Heavy Knight Gobyet"
    faction = "knights"
    role = "heavy"
    silhouette = ["large_helmet", "plume", "broad_pauldrons", "tower_shield", "greatsword"]
    body = {"torso_w": 8.6, "torso_h": 7.0, "shoulder": 7.6}

    def back(self, cv, g):
        G.cape(cv, g, ("z", "1"), length=12, sway=g.p.get("cape", 0.0))

    def legs(self, cv, g):
        if g.p.get("mode") == "sit":
            R.sit_legs(cv, g, fur="st2", boots=("st1", "st3"))
        else:
            G.plate_legs(cv, g)
        G.faulds(cv, g, w=9.0)

    def torso(self, cv, g):
        G.breastplate(cv, g, w=0.9, h=0.6)
        G.tabard(cv, g, ("z", "1"), length=6)

    def headgear(self, cv, g):
        G.great_helm(cv, g, plume=g.p.get("plume", 0.0))

    def arm(self, cv, g, i):
        G.plate_arm(cv, g, i, r=2.4)

    def over_arm(self, cv, g, i):
        d = g.p.get("rattle", 0) * (1 if i else -1)
        G.pauldron(cv, g.sh[i][0], g.sh[i][1] + d, -1 if i == 0 else 1, big=1.1)

    def hand(self, cv, g, i):
        G.gauntlet(cv, g, i, r=2.6)

    def build(self):
        base = dict(sx=5, rh=(12, 3), lh=(-12, 4), rw="greatsword", rwa=-62, lw="tower_shield")

        def idle(t):
            p = kf(t, [(0, dict(base)), (6, dict(base, crouch=1, rh=(12, 4), rwa=-58))], 12)
            p.update(plume=wag(t, 12), tail=wag(t, 12), cape=wag(t, 12))
            if t == 8:
                p["eyes"] = "blink"
            return p
        self.add("idle", 12, idle, ms=130, core="idle", label="berdiri berat, zirah naik-turun pelan")

        def walk(t):
            keys = [(0, dict(base, crouch=1, fx_l=-1, fx_r=1)),
                    (3, dict(base, lift_l=3, fx_l=1, fx_r=0, lean=1, rwa=-56)),
                    (6, dict(base, crouch=1, fx_l=1, fx_r=-1)),
                    (9, dict(base, lift_r=3, fx_l=0, fx_r=1, lean=1, rwa=-66))]
            p = kf(t, keys, 12)
            p.update(plume=wag(t, 12, 2), tail=wag(t, 12), cape=wag(t, 12, 2), rattle=1 if t in (0, 6) else 0)
            if t in (0, 6):
                fx = g_feet_dust(p, 0 if t == 6 else 1)
                p["fx"] = [fx]
            return p
        self.add("walk", 12, walk, ms=130, label="langkah berat, debu tiap kaki menapak")

        guard = dict(base, sx=6, crouch=2, lh=(1, 1), rh=(9, -5), rwa=-105, eyes="side", brows="angry", mouth="flat")

        def guard_f(t):
            p = kf(t, [(0, dict(guard)), (4, dict(guard, crouch=3, lh=(1, 2)))], 8)
            p.update(plume=wag(t, 8), tail=wag(t, 8))
            return p
        self.add("guard", 8, guard_f, ms=140, label="perisai menara ke depan, pedang siaga")

        def attack(t):
            keys = [(0, dict(base)),
                    (3, dict(base, rh=(3, -11), rwa=-160, lean=-2, eyes="angry", brows="angry", mouth="shout", rw_back=True)),
                    (5, dict(base, rh=(13, -7), rwa=-70, lean=1, eyes="angry", brows="angry", mouth="shout", rw_back=False)),
                    (6, dict(base, rh=(14, 4), rwa=25, lean=3, crouch=2, eyes="angry", brows="angry", mouth="shout")),
                    (9, dict(base, rh=(14, 4), rwa=25, lean=3, crouch=2, eyes="look", brows="angry", mouth="flat")),
                    (13, dict(base))]
            p = kf(t, keys, 14, loop=False)
            p.update(plume=wag(t, 14), tail=wag(t, 14))
            if t in (6, 7, 8):
                p["fx"] = [fx_impact(RX + 33, BASE - 6, k=t - 6), fx_dust(RX + 30, BASE - 1, t - 6)]
            if t == 5:
                p["fx"] = [lambda cv, g: R.speed_lines(cv, RX + 22, 22, 3, 6, -1)]
            return p
        self.add("attack", 14, attack, ms=90, loop=False, core="attack", label="ancang-ancang, ayunan pedang besar, hantaman")

        def block(t):
            keys = [(0, dict(guard)), (3, dict(guard, dx=-1, lh=(0, 1), eyes="blink", brows="angry", mouth="shout", crouch=3)),
                    (5, dict(guard, crouch=2)), (9, dict(guard))]
            p = kf(t, keys, 10, loop=False)
            p.update(plume=wag(t, 10), tail=wag(t, 10))
            if t in (3, 4, 5):
                p["fx"] = [fx_impact(RX + 11, BASE - 22, k=min(t - 3, 1), c="W")]
            return p
        self.add("block", 10, block, ms=100, loop=False, label="perisai menahan hantaman")

        def hit(t):
            keys = [(0, dict(base)), (2, dict(base, lean=-3, dx=-2, hdx=-1, eyes="wide", brows="up", mouth="o", rwa=-80, lh=(-12, 6))),
                    (6, dict(base, lean=-2, dx=-1, eyes="relief", brows="worried", mouth="frown", rwa=-70)), (9, dict(base))]
            p = kf(t, keys, 10, loop=False)
            p.update(plume=wag(t, 10, 2), tail=wag(t, 10), rattle=(1 if t % 2 else -1) if 2 <= t <= 6 else 0)
            if 2 <= t <= 7:
                p["fx"] = [fx_stars(R.RX - 2, 14, t)]
            return p
        self.add("hit", 10, hit, ms=100, loop=False, core="hit", label="zirah bergetar, helm berdenting")

        vic = dict(base, rh=(9, -15), rwa=-90, lh=(-12, 1), mouth="smile")

        def victory(t):
            keys = [(0, dict(base)), (4, dict(vic)), (8, dict(vic, crouch=1, eyes="happy")), (12, dict(vic)), (15, dict(vic))]
            p = kf(t, keys, 16)
            p.update(plume=wag(t, 16, 2), tail=wag(t, 16, 2), glint=(t % 4) / 4.0 if 4 <= t <= 13 else None)
            if 4 <= t <= 13:
                p["fx"] = [fx_sparkle(RX + 9, 3, t)]
            return p
        self.add("victory", 16, victory, ms=110, core="victory", label="pedang besar terangkat lurus, perisai naik")

        def defeat(t):
            keys = [(0, dict(base)),
                    (2, dict(base, lean=-2, dx=-2, eyes="wide", brows="up", mouth="o", rwa=-30)),
                    (4, dict(base, crouch=4, dx=-2, eyes="relief", brows="worried", mouth="o", rw=None, lh=(-12, 6))),
                    (6, dict(base, mode="sit", dx=-2, rw=None, lh=(-12, 6), rh=(10, 5), eyes="relief", brows="worried")),
                    (8, dict(base, mode="sit", dx=-2, rw=None, lh=(-12, 6), rh=(10, 5), eyes="relief", brows="worried"))]
            p = kf(t, keys, 16, loop=False, smooth=False) if t < 9 else dict(base, mode="sit", dx=-2, rw=None, lw=None,
                                                                             rh=(10, 2), lh=(-10, 2), eyes="relief",
                                                                             brows="worried", rot=-90, rot_ground=True)
            p.update(plume=0.0, tail=0.0)
            fx = []
            if t >= 4:
                fx.append(fx_item_ground("greatsword", RX + 6, BASE - 3, 0))
            if t >= 9:
                fx.append(fx_item_ground("tower_shield", RX + 6, BASE - 11, 0))
            if 9 <= t <= 11:
                fx.append(fx_dust(RX - 8, BASE - 1, t - 9))
                fx.append(fx_puff(RX - 14, BASE - 4, 2.5 + (t - 9)))
            if t >= 13:
                fx.append(fx_puff(RX - 12, BASE - 16 - (t - 13) * 2, 1.5))
            if t >= 9:
                p["fx_after"] = fx
            else:
                p["fx"] = fx
            return p
        self.add("defeat", 16, defeat, ms=120, loop=False, hold=10, core="defeat",
                 label="limbung, lutut tertekuk, duduk, lalu rebah berat dengan debu")


def g_feet_dust(p, which):
    sx = p.get("sx", 4)
    x = RX - sx + p.get("fx_l", 0) if which == 0 else RX + sx + p.get("fx_r", 0)
    return fx_dust(x, BASE - 1, 0)




# ================================================================== ARCHER
class Archer(Char):
    id = "knight-archer"
    name = "Archer Gobyet"
    faction = "knights"
    role = "ranged"
    silhouette = ["kettle_hat_wide_brim", "longbow", "quiver_on_back"]
    body = {"torso_w": 7.2, "shoulder": 6.4}

    def back(self, cv, g):
        I.quiver(cv, g.tcx - 6, g.tcy - 7, ang=-115)

    def legs(self, cv, g):
        if g.p.get("mode") == "sit":
            R.sit_legs(cv, g, fur="le1", boots=("le2", "K"))
        else:
            R.legs(cv, g, fur="le1", boots=("le2", "K"))

    def torso(self, cv, g):
        m = R.ellipse(g.tcx, g.tcy, g.tw + 0.6, g.th + 0.5)
        R.solid(cv, m, "V", "v", shade_off=(2, 2))
        for (x, y) in R.inner(m):
            if (y - int(g.tcy)) % 3 == 0 and (x + y) % 2 == 0:
                cv.put(x, y, "v")
        cv.fill(R.capsule((g.tcx - 6, g.tcy - 5), (g.tcx + 5, g.tcy + 4), 0.8), "le2")
        by = int(round(g.tcy + g.th - 1.5))
        cv.fill({(x, y) for (x, y) in m if y in (by, by + 1)}, "le2")
        cv.fill(R.rect(int(g.tcx) - 1, by, 3, 2), "st1")

    def headgear(self, cv, g):
        G.kettle_hat(cv, g, tilt=g.p.get("hat_tilt", 0))

    def arm(self, cv, g, i):
        R.arm(cv, g, i, sleeve="V", r=1.9)
        if i == 1:
            hx, hy = g.hand[1]
            ex = g.elbow[1] or g.sh[1]
            bx, by = hx + (ex[0] - hx) * 0.35, hy + (ex[1] - hy) * 0.35
            R.solid(cv, R.ellipse(bx, by, 2.0, 2.0), "le1", "le2", shade_off=(1, 1))

    def over_arm(self, cv, g, i):
        G.pauldron(cv, g.sh[i][0], g.sh[i][1], -1 if i == 0 else 1, big=0.62)

    def build(self):
        base = dict(sx=4, rh=(10, 2), rw="bow", rwa=-8, nock=False, lh=(-9, 4))
        aim = dict(base, rh=(14, -3), rwa=0, nock=True, draw=1.0, lh=(5, -3), eyes="side", brows="angry", mouth="flat",
                   sx=5, lean=1)
        full = dict(aim, draw=8.0, lh=(-2, -3))
        self.add("idle", 12, idle_loop(base, 12, alt=dict(rwa=-4), look=(3, 5)), ms=130, core="idle",
                 label="busur panjang di sisi, tabung panah di punggung")

        def aim_f(t):
            p = kf(t, [(0, dict(aim)), (4, dict(aim, rh=(14, -4), crouch=1))], 8)
            p["tail"] = wag(t, 8)
            return p
        self.add("aim", 8, aim_f, ms=130, label="busur terangkat, panah terpasang, membidik")

        def draw_f(t):
            p = kf(t, [(0, dict(aim)), (7, dict(full)), (9, dict(full))], 10, loop=False)
            p["tail"] = wag(t, 10)
            if t >= 7:
                p["rh"] = (14, -3 + (t % 2) * 0)
                p["mouth"] = "shout" if t == 9 else "flat"
            return p
        self.add("draw", 10, draw_f, ms=110, loop=False, label="menarik tali sampai penuh")

        def fire_f(t):
            p = dict(full) if t == 0 else dict(aim, draw=(-1.0 if t % 2 else 1.0) if t < 4 else 0.0, nock=False,
                                                 lh=(-4, -7), eyes="side", mouth="smirk")
            if t >= 1:
                ax = R.RX + 36 + (t - 1) * 9
                p["fx"] = [lambda cv, g, ax=ax: I.arrow_flying(cv, ax, int(g.tcy - 3))]
            p["tail"] = wag(t, 8)
            return p
        self.add("fire", 8, fire_f, ms=80, loop=False, label="melepas panah, tali bergetar")

        def recoil_f(t):
            p = kf(t, [(0, dict(aim, nock=False, draw=0.0, lh=(-4, -7))), (2, dict(aim, nock=False, draw=0.0, rh=(13, -7), rwa=-20,
                                                                                    lean=-1, lh=(-5, -6))),
                       (7, dict(aim, nock=False, draw=0.0))], 8, loop=False)
            p["tail"] = wag(t, 8)
            return p
        self.add("recoil", 8, recoil_f, ms=100, loop=False, label="busur terhentak naik lalu kembali membidik")

        def attack(t):
            if t < 6:
                p = kf(t, [(0, dict(base)), (2, dict(aim)), (5, dict(full))], 16, loop=False)
            elif t < 10:
                p = fire_f(t - 5)
            else:
                p = kf(t, [(10, dict(aim, nock=False, draw=0.0, rh=(13, -7), rwa=-20, lean=-1, lh=(-5, -6))), (15, dict(base))],
                       16, loop=False)
                if t <= 11:
                    ax = R.RX + 36 + (t - 5) * 9
                    p["fx"] = [lambda cv, g, ax=ax: I.arrow_flying(cv, ax, int(g.tcy - 3))]
            p["tail"] = wag(t, 16)
            return p
        self.add("attack", 16, attack, ms=90, loop=False, core="attack", label="bidik, tarik, lepas, hentakan busur")
        self.add("hit", 10, hit_fn(base, recoil=dict(rwa=-30, hat_tilt=-2)), ms=100, loop=False, core="hit",
                 label="terdorong, topi baja miring")
        up = dict(base, rh=(4, -16), rwa=-90, lh=(-10, -6), mouth="smile")
        self.add("victory", 16, victory_raise(base, up, sparkle_hand=1), ms=110, core="victory",
                 label="busur diangkat melintang di atas kepala")
        self.add("defeat", 16, defeat_fall(dict(base, rw=None), drops=[("bow", R.RX + 10, BASE - 5, -90, {"nock": False})],
                                           early_drop=2), ms=120, loop=False, hold=10, core="defeat",
                 label="busur jatuh lebih dulu, lalu ikut rebah")


# ================================================================== MAN-AT-ARMS
class ManAtArms(Char):
    id = "knight-man-at-arms"
    name = "Man-at-Arms Gobyet"
    faction = "knights"
    role = "versatile"
    silhouette = ["pointed_bascinet", "halberd_long", "brigandine", "wide_stance"]
    body = {"torso_w": 7.8, "shoulder": 6.8}

    def legs(self, cv, g):
        if g.p.get("mode") == "sit":
            R.sit_legs(cv, g, fur="nv2", boots=("le2", "K"))
            return
        R.legs(cv, g, fur="nv2", boots=("le2", "K"))
        for i, s in enumerate((-1, 1)):
            hx, hy = g.hips[i]
            fx, fy = g.feet[i]
            R.solid(cv, R.ellipse((hx + fx) / 2 + s * 0.6, (hy + fy) / 2, 2.2, 1.9), "st1", "st2", shade_off=(1, 1))
        G.tunic_skirt(cv, g, ("nv1", "nv2"), w=8.0, rows=3)

    def torso(self, cv, g):
        m = R.ellipse(g.tcx, g.tcy, g.tw + 0.7, g.th + 0.6)
        R.solid(cv, m, "nv1", "nv2", shade_off=(2, 2))
        for (x, y) in R.inner(m):
            if (x - int(g.tcx)) % 3 == 0 and (y - int(g.tcy)) % 3 == 1:
                cv.put(x, y, "st1")
        by = int(round(g.tcy + g.th - 1.5))
        cv.fill({(x, y) for (x, y) in m if y in (by, by + 1)}, "le2")
        cv.fill(R.rect(int(g.tcx) - 1, by, 3, 2), "go1")
        G.mail_coif(cv, g)

    def headgear(self, cv, g):
        G.nasal_bascinet(cv, g)

    def arm(self, cv, g, i):
        R.arm(cv, g, i, sleeve="st2", r=2.0)

    def over_arm(self, cv, g, i):
        G.pauldron(cv, g.sh[i][0], g.sh[i][1], -1 if i == 0 else 1, big=0.8)

    def hand(self, cv, g, i):
        G.gauntlet(cv, g, i, r=2.3)

    def build(self):
        base = dict(sx=5, rh=(10, 3), rw="halberd", rwa=-78, lh=(-8, 4))
        ready = dict(sx=6, crouch=2, lean=2, rh=(9, 1), rw="halberd", rwa=-28, lh=(1, 5), grip2=True, eyes="side",
                     brows="angry", mouth="flat")
        self.add("idle", 12, idle_loop(base, 12, alt=dict(rwa=-74, lean=1), look=(2, 4)), ms=130, core="idle",
                 label="halberd tegak, berat badan berpindah")

        def ready_f(t):
            p = kf(t, [(0, dict(ready)), (4, dict(ready, crouch=3, rh=(10, 1)))], 8)
            p["tail"] = wag(t, 8)
            return p
        self.add("ready", 8, ready_f, ms=120, label="kuda-kuda lebar, halberd mengarah ke depan")

        def thrust(t):
            keys = [(0, dict(ready)), (3, dict(ready, rh=(5, 2), lh=(-3, 5), lean=0)),
                    (5, dict(ready, rh=(15, 0), lh=(7, 3), rwa=-22, lean=5, dx=2, mouth="shout")),
                    (8, dict(ready, rh=(15, 0), lh=(7, 3), rwa=-22, lean=5, dx=2)), (11, dict(ready))]
            p = kf(t, keys, 12, loop=False)
            p["tail"] = wag(t, 12)
            if t in (5, 6, 7):
                p["fx"] = [fx_impact(R.RX + 58, 26, t - 5), fx_speed(R.RX + 4, 38, 3, 6, -1)]
            return p
        self.add("attack", 12, thrust, ms=90, loop=False, core="attack", label="tusukan halberd ke depan")

        def swing(t):
            keys = [(0, dict(ready)), (3, dict(ready, rh=(4, -10), lh=(-4, -6), rwa=-160, lean=-2, rw_back=True, mouth="shout")),
                    (5, dict(ready, rh=(12, -6), lh=(4, -4), rwa=-60, lean=2, rw_back=False)),
                    (6, dict(ready, rh=(12, 3), lh=(4, 4), rwa=15, lean=4, crouch=3, mouth="shout")),
                    (9, dict(ready, rh=(12, 3), lh=(4, 4), rwa=15, lean=4, crouch=3)), (13, dict(ready))]
            p = kf(t, keys, 14, loop=False)
            p["tail"] = wag(t, 14)
            if t in (6, 7, 8):
                p["fx"] = [fx_impact(R.RX + 44, BASE - 6, t - 6), fx_dust(R.RX + 40, BASE - 1, t - 6)]
            return p
        self.add("swing", 14, swing, ms=90, loop=False, label="ayunan lebar dari atas kepala")

        blk = dict(ready, rh=(10, -9), lh=(-5, -9), rwa=-180, lean=0, crouch=2, eyes="look", brows="angry", mouth="flat")

        def block(t):
            keys = [(0, dict(ready)), (3, dict(blk)), (5, dict(blk, dx=-1, crouch=3, eyes="blink", mouth="shout")),
                    (7, dict(blk)), (11, dict(ready))]
            p = kf(t, keys, 12, loop=False)
            p["tail"] = wag(t, 12)
            if t in (5, 6):
                p["fx"] = [fx_impact(R.RX + 4, 21, t - 5, "W")]
            return p
        self.add("block", 12, block, ms=100, loop=False, label="gagang halberd menahan di atas kepala")

        def recover(t):
            tired = dict(ready, crouch=3, lean=0, rwa=10, rh=(10, 4), lh=(2, 6), eyes="relief", brows="worried", mouth="o")
            p = kf(t, [(0, tired), (4, dict(tired, crouch=4)), (9, dict(ready))], 10, loop=False)
            p["tail"] = wag(t, 10)
            if t < 6:
                p["fx"] = [lambda cv, g: R.sweat(cv, g.ihead()[0] + 11, g.ihead()[1] - 6)]
            return p
        self.add("recover", 10, recover, ms=110, loop=False, label="terengah, kembali ke kuda-kuda")
        self.add("hit", 10, hit_fn(base, recoil=dict(rwa=-60), rattle=False), ms=100, loop=False, core="hit",
                 label="terdorong, halberd goyah")
        up = dict(base, rh=(8, -13), rwa=-90, lh=(-9, -9), mouth="smile")
        self.add("victory", 16, victory_raise(base, up, sparkle_hand=0), ms=110, core="victory",
                 label="halberd diacungkan, tinju naik")
        self.add("defeat", 16, defeat_fall(base, drops=[("halberd", R.RX - 6, BASE - 3, 0)], early_drop=4), ms=120,
                 loop=False, hold=10, core="defeat", label="halberd terlepas, rebah")


# ================================================================== ASSASSIN
class Assassin(Char):
    id = "knight-assassin"
    name = "Assassin Gobyet"
    faction = "knights"
    role = "stealth"
    silhouette = ["hood_peak", "asymmetric_cloak", "dual_daggers", "low_stance", "narrow"]
    body = {"torso_w": 6.4, "torso_h": 6.3, "shoulder": 5.6}

    def back(self, cv, g):
        G.cape(cv, g, ("l", "L"), length=14, sway=g.p.get("cape", 0.0), side=-1, width=1.3)

    def legs(self, cv, g):
        if g.p.get("mode") == "sit":
            R.sit_legs(cv, g, fur="l", boots=("L", "K"))
        else:
            R.legs(cv, g, fur="l", boots=("L", "K"))

    def torso(self, cv, g):
        m = R.ellipse(g.tcx, g.tcy, g.tw + 0.5, g.th + 0.4)
        R.solid(cv, m, "L", "q", shade_off=(2, 2))
        cv.fill(R.capsule((g.tcx - 5, g.tcy - 4), (g.tcx + 5, g.tcy + 4), 1.0) & m, "cr1")
        by = int(round(g.tcy + g.th - 1.5))
        cv.fill({(x, y) for (x, y) in m if y in (by, by + 1)}, "le2")
        R.solid(cv, R.ellipse(g.tcx - 3, by + 1, 1.8, 1.8), "l", None)

    def headgear(self, cv, g):
        G.hood(cv, g, ("l", "L"), mask=True)
        G.cloak_front(cv, g, ("l", "L"))

    def arm(self, cv, g, i):
        R.arm(cv, g, i, sleeve="L", r=1.7)

    def hand(self, cv, g, i):
        R.hand(cv, g, i, color="l", shade="L", r=1.9)

    def build(self):
        base = dict(sx=5, crouch=3, lean=2, rh=(11, 3), rw="dagger", rwa=40, lh=(-10, 4), lw="dagger", lwa=140, eyes="side",
                    brows="angry", mouth="flat")
        self.add("idle", 12, idle_loop(base, 12, alt=dict(lean=3)), ms=130, core="idle",
                 label="kuda-kuda rendah, dua belati terbalik")

        def stealth(t):
            keys = [(0, dict(base, crouch=5, lift_l=0, dx=-1)), (3, dict(base, crouch=5, lift_l=2, dx=0)),
                    (6, dict(base, crouch=5, dx=1)), (9, dict(base, crouch=5, lift_r=2, dx=0))]
            p = kf(t, keys, 12)
            p.update(tail=wag(t, 12), cape=wag(t, 12), eyes="side")
            return p
        self.add("stealth", 12, stealth, ms=120, label="berjingkat sambil merunduk")

        def dash(t):
            keys = [(0, dict(base)), (2, dict(base, crouch=5, lean=-1)), (4, dict(base, dx=14, lean=6, crouch=2, rh=(14, 0), rwa=0,
                                                                                  mouth="shout")),
                    (6, dict(base, dx=14, lean=6, crouch=2, rh=(14, 0), rwa=0)), (9, dict(base, dx=4)), (11, dict(base))]
            p = kf(t, keys, 12, loop=False)
            p.update(tail=wag(t, 12), cape=wag(t, 12, 2))
            if t in (3, 4, 5):
                p["fx"] = [fx_speed(R.RX - 2 + (t - 3) * 6, 40, 4, 8, -1)]
            if t in (4, 5, 6):
                p["fx"] = p.get("fx", []) + [fx_impact(R.RX + 38 + 14, 40, t - 4, "W")]
            return p
        self.add("attack", 12, dash, ms=70, loop=False, core="attack", label="melesat cepat, tusukan belati")

        def backstab(t):
            keys = [(0, dict(base)), (2, dict(base, crouch=1, rh=(6, -10), rwa=90, lean=1)),
                    (4, dict(base, crouch=4, rh=(12, 3), rwa=80, lean=4, mouth="shout")),
                    (6, dict(base, crouch=4, rh=(12, 3), rwa=80, lean=4)), (9, dict(base))]
            p = kf(t, keys, 10, loop=False)
            p.update(tail=wag(t, 10), cape=wag(t, 10))
            if t in (4, 5):
                p["fx"] = [fx_impact(R.RX + 26, 50, t - 4, "W")]
            return p
        self.add("backstab", 10, backstab, ms=80, loop=False, label="tikaman cepat dari atas")

        def smoke(t):
            keys = [(0, dict(base)), (2, dict(base, crouch=1, lh=(-4, -8), lw="smoke_bomb", lean=0)),
                    (4, dict(base, crouch=5, lh=(2, 8), lw=None)), (11, dict(base, crouch=5, lw=None))]
            p = kf(t, keys, 12, loop=False, smooth=False)
            p.update(tail=wag(t, 12), cape=wag(t, 12))
            if t >= 4:
                p["fx"] = [fx_smoke_cloud(R.RX, BASE - 6, min(t - 4, 4))]
            return p
        self.add("smoke", 12, smoke, ms=100, loop=False, label="bom asap dibanting ke lantai")

        def disappear(t):
            p = dict(base, crouch=5) if t < 3 else dict(base, crouch=5, visible=t < 5)
            p.update(tail=wag(t, 12), cape=wag(t, 12))
            if t >= 2:
                k = min(t - 2, 4) if t < 8 else max(0, 4 - (t - 8))
                p["fx"] = [fx_smoke_cloud(R.RX, BASE - 8 - max(0, t - 7), k)] if t < 11 else []
            return p
        self.add("disappear", 12, disappear, ms=100, loop=False, hold=6, label="hilang di balik asap")
        self.add("hit", 10, hit_fn(base, recoil=dict(crouch=2)), ms=100, loop=False, core="hit", label="terpental ringan")
        cross = dict(base, crouch=0, lean=0, rh=(5, -2), rwa=-50, lh=(-5, -2), lwa=-130, eyes="look", mouth="smirk")

        def victory(t):
            p = kf(t, [(0, dict(base)), (4, dict(cross)), (12, dict(cross, crouch=1)), (15, dict(cross))], 16)
            p.update(tail=wag(t, 16), cape=wag(t, 16, 2))
            if 5 <= t <= 13:
                p["fx"] = [fx_sparkle(R.RX + 2, 34, t)]
            if t in (9, 10):
                p["eyes"] = "blink" if t == 9 else "look"
            return p
        self.add("victory", 16, victory, ms=110, core="victory", label="belati bersilang, jubah berkibar")

        def defeat(t):
            if t < 3:
                p = kf(t, [(0, dict(base)), (2, dict(base, lean=-2, dx=-2, eyes="wide", mouth="o", brows="up"))], 16, loop=False)
            elif t < 5:
                p = dict(base, dx=-2, crouch=5, lw="smoke_bomb", lh=(-2, 8), eyes="relief", brows="worried")
            else:
                p = dict(base, visible=False)
            p.update(tail=wag(t, 16), cape=0.0)
            if t >= 4:
                k = min(t - 4, 4) if t < 10 else max(0, 4 - (t - 10))
                p["fx"] = ([fx_smoke_cloud(R.RX - 2 - (t - 4), BASE - 8 - max(0, t - 9), k)] if t < 14 else []) + \
                    ([fx_item("dagger", R.RX + 6, BASE - 2, 0)] if t >= 7 else [])
            return p
        self.add("defeat", 16, defeat, ms=110, loop=False, hold=8, core="defeat",
                 label="mundur di balik asap, satu belati tertinggal")


# ================================================================== FANTASY KNIGHT
class FantasyKnight(Char):
    id = "fantasy-knight"
    name = "Fantasy Knight Gobyet"
    category = "fantasy"
    faction = "fantasy"
    role = "archetype"
    silhouette = ["visor_helm_white_plume", "blue_cape", "kite_shield", "longsword"]
    body = {"torso_w": 7.8, "shoulder": 6.8}

    def back(self, cv, g):
        G.cape(cv, g, ("3", "4"), length=15, sway=g.p.get("cape", 0.0), width=1.4)

    def legs(self, cv, g):
        if g.p.get("mode") == "sit":
            R.sit_legs(cv, g, fur="st2", boots=("st1", "st3"))
        else:
            G.plate_legs(cv, g)

    def torso(self, cv, g):
        G.breastplate(cv, g, w=0.5, h=0.4, accent=("3", "4"))

    def headgear(self, cv, g):
        G.visor_helm(cv, g, plume=g.p.get("plume", 0.0))

    def arm(self, cv, g, i):
        G.plate_arm(cv, g, i, r=2.1)

    def over_arm(self, cv, g, i):
        G.pauldron(cv, g.sh[i][0], g.sh[i][1], -1 if i == 0 else 1, big=0.8)

    def hand(self, cv, g, i):
        G.gauntlet(cv, g, i, r=2.3)

    def build(self):
        base = dict(sx=5, rh=(11, 3), rw="sword", rwa=-55, lh=(-11, 3), lw="kite_shield", lwp=None)
        self.add("idle", 12, idle_loop(base, 12, alt=dict(rwa=-52)), ms=130, core="idle",
                 label="pedang panjang, perisai layang-layang biru, jubah biru")

        def attack(t):
            wind = dict(base, rh=(4, -11), rwa=-150, lean=-2, rw_back=True, mouth="shout", brows="angry")
            hit = dict(base, rh=(14, 2), rwa=15, lean=3, crouch=2, mouth="shout", brows="angry")
            p = kf(t, [(0, dict(base)), (3, wind), (5, hit), (8, dict(hit, mouth="flat")), (11, dict(base))], 12, loop=False)
            p.update(tail=wag(t, 12), plume=wag(t, 12), cape=wag(t, 12, 2))
            if t in (5, 6, 7):
                p["fx"] = [fx_impact(R.RX + 36, 40, t - 5, "W"), fx_speed(R.RX + 18, 28, 3, 7, -1)]
            return p
        self.add("attack", 12, attack, ms=85, loop=False, core="attack", label="tebasan pedang panjang")
        self.add("hit", 10, hit_fn(base, rattle=False), ms=100, loop=False, core="hit", label="tertahan perisai, mundur")
        up = dict(base, rh=(8, -15), rwa=-90, lh=(-11, 0), mouth="smile")
        self.add("victory", 16, victory_raise(base, up, sparkle_hand=None,
                                              extra=lambda t, p: p.update(glint=(t % 4) / 4.0, fx=[fx_sparkle(R.RX + 8, 5, t)])
                                              if 4 <= t <= 13 else None), ms=110, core="victory",
                 label="pedang diangkat, jubah berkibar")
        self.add("defeat", 16, defeat_fall(base, drops=[("sword", R.RX + 6, BASE - 3, 0)], early_drop=4), ms=120, loop=False,
                 hold=10, core="defeat", label="pedang terlepas, rebah")


CHARS = [HeavyKnight, Archer, ManAtArms, Assassin, FantasyKnight]
