"""Faksi Viking v2: Viking dasar, Berserker, Huscarl, Gestir, Bondi, dan Fantasy Viking.

Bahasa visual faksi: bulu bergerigi (fu0-fu2), kulit (le1/le2), kayu (wo1/wo2), besi gelap (st2/st3),
aksen cat merah pada perisai bundar. Tidak ada pelat baja halus seperti Knight.
"""
import math

import rig2 as R
import gear2 as G
import items2 as I
from char2 import Char
from rig2 import kf, wag, BASE, RX
from moves import (fx_impact, fx_dust, fx_item, fx_puff, fx_sparkle, fx_hand_sparkle, fx_speed, fx_stars_head,
                   idle_loop, hit_fn, defeat_fall, victory_raise)


def chop_fn(base, n=14, big=False, impact_x=None, two=False):
    """Kapak: ancang-ancang di atas kepala (di belakang kepala), ayunan berat, hantaman ke lantai, kembali."""
    wind = dict(base, rh=(2, -12), rwa=-165, lean=-2, rw_back=True, eyes="angry", brows="angry", mouth="shout")
    if two:
        wind.update(lh=(-2, -11), grip2=True)
    mid = dict(base, rh=(12, -7), rwa=-60, lean=1, rw_back=False, eyes="angry", brows="angry", mouth="shout")
    hit = dict(base, rh=(13, 4), rwa=40 if not big else 35, lean=3, crouch=2, eyes="angry", brows="angry", mouth="shout")
    if two:
        mid.update(lh=(6, -5), grip2=True)
        hit.update(lh=(7, 4), grip2=True)
    ix = impact_x or (RX + 34 if big else RX + 30)

    def fn(t):
        keys = [(0, dict(base)), (3, wind), (5, mid), (6, hit), (9, dict(hit, mouth="flat", eyes="look")), (n - 1, dict(base))]
        p = kf(t, keys, n, loop=False)
        p.update(tail=wag(t, n), cape=wag(t, n))
        if t in (6, 7, 8):
            p["fx"] = [fx_impact(ix, BASE - 4, t - 6), fx_dust(ix - 2, BASE - 1, t - 6)]
        if t == 5:
            p["fx"] = [fx_speed(RX + 18, 20, 3, 6, -1)]
        return p
    return fn


def shield_down_fn(base, drops=(), n=16):
    """Defeat Viking: perisai diturunkan ke lantai, berlutut, kepala tertunduk, menghela napas."""
    sag = dict(base, crouch=3, lean=-1, eyes="relief", brows="worried", mouth="frown", lh=(-10, 8))
    kneel = dict(base, crouch=7, lean=0, sx=6, eyes="relief", brows="worried", mouth="frown", lh=(-9, 9), rh=(10, 8), rwa=70,
                 hdy=2)

    def fn(t):
        p = kf(t, [(0, dict(base)), (3, dict(base, eyes="wide", brows="up", mouth="o", dx=-1)), (6, sag), (10, kneel),
                   (15, kneel)], n, loop=False)
        p.update(tail=0.0, cape=0.0)
        fx = [fx_item(d[0], d[1], d[2], d[3], **(d[4] if len(d) > 4 else {})) for d in drops] if t >= 8 else []
        if t >= 11:
            fx.append(fx_puff(RX + 10 + (t - 11), BASE - 30 - (t - 11) * 2, 1.4 + (t - 11) * 0.25))
        p["fx"] = fx
        return p
    return fn


class VikingBase(Char):
    id = "viking"
    name = "Viking Gobyet"
    faction = "vikings"
    role = "base"
    silhouette = ["horned_helmet", "fur_mantle", "round_shield", "axe"]
    body = {"torso_w": 7.8, "shoulder": 6.8}
    mantle = ("fu1", "fu2")
    mantle_big = 1.0
    vest = ("le1", "le2")
    skirt = ("le1", "le2")
    horns = 1.0

    def legs(self, cv, g):
        if g.p.get("mode") == "sit":
            R.sit_legs(cv, g, fur="le1", boots=("le2", "K"))
        else:
            G.wraps_legs(cv, g, ("le1", "le2"))
        G.tunic_skirt(cv, g, self.skirt, w=8.5, rows=4)

    def torso(self, cv, g):
        G.leather_vest(cv, g, self.vest)
        if self.mantle:
            G.fur_mantle(cv, g, self.mantle, big=self.mantle_big)

    def headgear(self, cv, g):
        G.horned_helm(cv, g, horns=self.horns)

    def arm(self, cv, g, i):
        R.arm(cv, g, i, sleeve="le1", r=2.0)
        hx, hy = g.hand[i]
        ex = g.elbow[i] or g.sh[i]
        R.solid(cv, R.ellipse(hx + (ex[0] - hx) * 0.3, hy + (ex[1] - hy) * 0.3, 2.1, 2.1), "fu1", "fu2", shade_off=(1, 1))

    def build(self):
        base = dict(sx=5, rh=(11, 3), rw="axe", rwa=-70, lh=(-12, 3), lw="round_shield")
        self.add("idle", 12, idle_loop(base, 12, alt=dict(rwa=-66)), ms=130, core="idle", label="kapak dan perisai bundar")
        self.add("attack", 14, chop_fn(base), ms=90, loop=False, core="attack", label="ayunan kapak dari atas kepala")
        self.add("hit", 10, hit_fn(base, recoil=dict(rwa=-90, lh=(-12, 6))), ms=100, loop=False, core="hit",
                 label="terdorong, perisai goyah")
        up = dict(base, rh=(8, -14), rwa=-80, lh=(-12, -2), mouth="shout", eyes="happy")
        self.add("victory", 16, victory_raise(base, dict(up, eyes="look", mouth="smile"), sparkle_hand=1), ms=110,
                 core="victory", label="kapak terangkat, perisai naik")
        self.add("defeat", 16, shield_down_fn(dict(base, lw=None), drops=[("round_shield", RX - 9, BASE - 7, 0)]), ms=120,
                 loop=False, hold=10, core="defeat", label="perisai turun ke lantai, berlutut")


class Berserker(VikingBase):
    id = "viking-berserker"
    name = "Berserker Gobyet"
    role = "rage"
    silhouette = ["wolf_pelt_hood", "dual_axes", "bare_arms", "low_aggressive_stance"]
    body = {"torso_w": 7.6, "shoulder": 6.8}

    def torso(self, cv, g):
        R.torso(cv, g)
        G.crossbelts(cv, g, "le2", "st1")
        G.fur_mantle(cv, g, ("fu1", "fu2"), big=0.85)

    def legs(self, cv, g):
        if g.p.get("mode") == "sit":
            R.sit_legs(cv, g)
        else:
            G.wraps_legs(cv, g, ("le1", "le2"))
        G.tunic_skirt(cv, g, ("fu1", "fu2"), w=8.0, rows=4)

    def head(self, cv, g):
        R.head(cv, g)
        hx, hy = g.ihead()
        for s in (-1, 1):  # cat perang biru di pipi
            cv.fill({(hx + s * 6, hy + 2), (hx + s * 6, hy + 3), (hx + s * 7, hy + 3)}, "3")

    def headgear(self, cv, g):
        G.pelt_hood(cv, g)

    def arm(self, cv, g, i):
        R.arm(cv, g, i, sleeve="B", r=2.1)
        hx, hy = g.hand[i]
        ex = g.elbow[i] or g.sh[i]
        R.solid(cv, R.ellipse(hx + (ex[0] - hx) * 0.3, hy + (ex[1] - hy) * 0.3, 2.0, 1.8), "le2", None)

    def build(self):
        base = dict(sx=6, crouch=2, lean=1, rh=(12, 2), rw="axe", rwa=-55, lh=(-12, 2), lw="axe", lwa=-125, eyes="angry",
                    brows="angry", mouth="flat")

        def idle(t):
            p = kf(t, [(0, dict(base)), (3, dict(base, crouch=3, rwa=-50, lwa=-130)), (6, dict(base)),
                       (9, dict(base, crouch=3, rwa=-50, lwa=-130))], 12)
            p.update(tail=wag(t, 12, 2))
            if t == 8:
                p["eyes"] = "blink"
            return p
        self.add("idle", 12, idle, ms=110, core="idle", label="memantul tak sabar, dua kapak siap")
        rage = dict(base, crouch=5, lean=2, sx=7, rh=(11, -9), rwa=-80, lh=(-11, -9), lwa=-100, face="A", eyes="angry",
                    brows="angry", mouth="shout")

        def rage_f(t):
            p = kf(t, [(0, dict(rage)), (2, dict(rage, crouch=6, rh=(12, -8), lh=(-12, -8))), (4, dict(rage))], 6)
            p["tail"] = wag(t, 6)
            p["fx"] = [lambda cv, g, t=t: _steam(cv, g, t)]
            return p
        self.add("rage", 6, rage_f, ms=70, label="mode amuk: lebih rendah, wajah memerah, kapak terangkat, lebih cepat")

        def roar(t):
            p = kf(t, [(0, dict(base)), (3, dict(rage, crouch=1, lean=-2, hdy=-1)), (8, dict(rage, crouch=1, lean=-2, hdy=-1)),
                       (11, dict(base))], 12, loop=False)
            p["tail"] = wag(t, 12)
            if 3 <= t <= 9:
                p["fx"] = [lambda cv, g, t=t: _roar_lines(cv, g, t)]
            return p
        self.add("roar", 12, roar, ms=100, loop=False, label="mengaum, garis suara")
        self.add("axe_attack", 14, chop_fn(base), ms=80, loop=False, label="satu kapak menghantam")

        def double(t):
            wind = dict(base, rh=(4, -12), rwa=-160, lh=(-4, -12), lwa=-20, rw_back=True, lw_back=True, mouth="shout",
                        lean=-2)
            hit = dict(base, rh=(13, 4), rwa=40, lh=(6, 5), lwa=60, crouch=4, lean=3, mouth="shout", rw_back=False,
                       lw_back=False)
            p = kf(t, [(0, dict(base)), (3, wind), (5, hit), (8, dict(hit, mouth="flat")), (11, dict(base))], 12, loop=False)
            p["tail"] = wag(t, 12)
            if t in (5, 6, 7):
                p["fx"] = [fx_impact(RX + 30, BASE - 4, t - 5), fx_impact(RX + 18, BASE - 3, max(0, t - 6)),
                           fx_dust(RX + 26, BASE - 1, t - 5)]
            return p
        self.add("double_attack", 12, double, ms=80, loop=False, core="attack", label="dua kapak menghantam bersamaan")
        self.add("hit", 10, hit_fn(base, recoil=dict(rwa=-90, lwa=-150)), ms=90, loop=False, core="hit",
                 label="terpental, makin marah")
        up = dict(base, crouch=0, lean=0, rh=(9, -14), rwa=-75, lh=(-9, -14), lwa=-105, mouth="shout", eyes="happy")
        self.add("victory", 16, victory_raise(base, up, sparkle_hand=None,
                                              extra=lambda t, p: p.update(fx=[lambda cv, g, t=t: _roar_lines(cv, g, t)])
                                              if 5 <= t <= 12 else None), ms=100, core="victory",
                 label="dua kapak diangkat, mengaum")
        self.add("defeat", 16, defeat_fall(dict(base, rw=None, lw=None), drops=[("axe", RX + 8, BASE - 3, 0), ("axe", RX - 14, BASE - 3, 180)],
                                           early_drop=4), ms=120, loop=False, hold=10, core="defeat",
                 label="kehabisan tenaga, dua kapak jatuh, rebah")


def _steam(cv, g, t):
    hx, hy = g.ihead()
    for k, s in enumerate((-1, 1)):
        y = hy - 12 - ((t + k * 2) % 4)
        R.puff(cv, hx + s * 12, y, 1.6 + ((t + k) % 2) * 0.6)


def _roar_lines(cv, g, t):
    hx, hy = g.ihead()
    for k in range(3):
        r = 13 + ((t + k * 2) % 6)
        for a in (-0.5, 0.0, 0.5):
            x, y = hx + 4 + math.cos(a) * r, hy + 4 + math.sin(a) * r
            cv.fill({(int(x), int(y)), (int(x) + 1, int(y))}, "K")


class Huscarl(VikingBase):
    id = "viking-huscarl"
    name = "Huscarl Gobyet"
    role = "heavy"
    silhouette = ["big_horned_helmet", "huge_fur_mantle", "large_round_shield", "dane_axe"]
    body = {"torso_w": 8.6, "torso_h": 7.0, "shoulder": 7.4}
    horns = 1.35
    mantle_big = 1.3

    def torso(self, cv, g):
        m = R.ellipse(g.tcx, g.tcy, g.tw + 0.6, g.th + 0.6)
        R.solid(cv, m, "st2", "st3", shade_off=(2, 2))
        for (x, y) in R.inner(m):
            if (x + y) % 2 == 0:
                cv.put(x, y, "st1")
        by = int(round(g.tcy + g.th - 1.5))
        cv.fill({(x, y) for (x, y) in m if y in (by, by + 1)}, "le2")
        cv.fill(R.rect(int(g.tcx) - 1, by, 3, 2), "go1")
        G.fur_mantle(cv, g, ("fu2", "le2"), big=self.mantle_big)

    def legs(self, cv, g):
        if g.p.get("mode") == "sit":
            R.sit_legs(cv, g, fur="le1", boots=("le2", "K"))
        else:
            G.wraps_legs(cv, g, ("le2", "K"))
        G.tunic_skirt(cv, g, ("st2", "st3"), w=9.5, rows=5)

    def build(self):
        base = dict(sx=6, rh=(12, 2), rw="greataxe", rwa=-72, lh=(-13, 3), lw="round_shield_big")
        self.add("idle", 12, idle_loop(base, 12, alt=dict(rwa=-70)), ms=140, core="idle",
                 label="kapak Dane besar dan perisai bundar besar")
        guard = dict(base, crouch=2, sx=7, lh=(2, 0), rh=(9, -6), rwa=-120, eyes="side", brows="angry", mouth="flat")

        def guard_f(t):
            p = kf(t, [(0, dict(guard)), (4, dict(guard, crouch=3))], 8)
            p["tail"] = wag(t, 8)
            return p
        self.add("guard", 8, guard_f, ms=140, label="dinding perisai")
        self.add("attack", 16, chop_fn(base, n=16, big=True, impact_x=RX + 40), ms=95, loop=False, core="attack",
                 label="hantaman kapak Dane yang berat")
        self.add("hit", 10, hit_fn(base, recoil=dict(rwa=-85, lh=(-13, 6))), ms=110, loop=False, core="hit",
                 label="tertahan, mundur setapak")
        up = dict(base, rh=(9, -15), rwa=-85, lh=(-13, -1), mouth="smile")
        self.add("victory", 16, victory_raise(base, up, sparkle_hand=None, hop=False), ms=120, core="victory",
                 label="kapak besar terangkat, tanpa lompat (berat)")
        self.add("defeat", 16, shield_down_fn(dict(base, lw=None), drops=[("round_shield", RX - 10, BASE - 9, 0, {"r": 9.5})]),
                 ms=130, loop=False, hold=10, core="defeat", label="perisai besar turun, berlutut")



class Gestir(VikingBase):
    id = "viking-gestir"
    name = "Gestir Gobyet"
    role = "spear"
    silhouette = ["conical_helmet", "long_spear", "javelins_on_back", "small_shield"]
    mantle = None

    def back(self, cv, g):
        for k, a in enumerate((-112, -100)):
            I.javelin(cv, (g.tcx - 5 + k * 2, g.tcy + 4), a, {})

    def torso(self, cv, g):
        G.leather_vest(cv, g, ("tl1", "tl2"), buckle="st1")
        cv.fill(R.capsule((g.tcx - 6, g.tcy - 5), (g.tcx + 5, g.tcy + 4), 0.8), "le2")

    def headgear(self, cv, g):
        G.conical_helm(cv, g)

    def build(self):
        base = dict(sx=5, rh=(11, 3), rw="spear", rwa=-82, lh=(-11, 4), lw="buckler")
        aim = dict(base, rh=(6, -8), rwa=-5, lh=(-11, 1), eyes="side", brows="angry", mouth="flat", lean=-1, crouch=1,
                   rw="javelin")
        self.add("idle", 12, idle_loop(base, 12, alt=dict(rwa=-80)), ms=130, core="idle",
                 label="tombak panjang tegak, lembing di punggung")

        def aim_f(t):
            p = kf(t, [(0, dict(aim)), (4, dict(aim, rh=(5, -8), crouch=2))], 8)
            p["tail"] = wag(t, 8)
            return p
        self.add("aim", 8, aim_f, ms=130, label="lembing di atas bahu, membidik")

        def throw(t):
            back = dict(aim, rh=(0, -8), lean=-3)
            rel = dict(aim, rh=(14, -6), lean=4, rw=None, mouth="shout", dx=1)
            p = kf(t, [(0, dict(aim)), (2, back), (4, rel), (9, dict(rel, mouth="smirk"))], 10, loop=False, smooth=False)
            p["tail"] = wag(t, 10)
            if 3 <= t:
                x = RX + 20 + (t - 3) * 10
                p["fx"] = [fx_item("javelin", x, 18 - (t - 3), -3), fx_speed(x - 12, 18, 2, 6, -1)]
            return p
        self.add("throw", 10, throw, ms=80, loop=False, core="attack", label="melempar lembing")

        def recover(t):
            p = kf(t, [(0, dict(aim, rh=(14, -6), lean=4, rw=None)), (5, dict(base))], 6, loop=False)
            p["tail"] = wag(t, 6)
            return p
        self.add("recover", 6, recover, ms=110, loop=False, label="mengambil tombak lagi")
        melee = dict(base, sx=6, crouch=2, rh=(8, 1), rwa=-8, lh=(-9, 2), eyes="side", brows="angry", mouth="flat")

        def melee_f(t):
            p = kf(t, [(0, dict(melee)), (2, dict(melee, rh=(3, 1), lean=-1)), (4, dict(melee, rh=(16, 0), lean=5, dx=2, mouth="shout")),
                       (7, dict(melee, rh=(16, 0), lean=5, dx=2)), (9, dict(melee))], 10, loop=False)
            p["tail"] = wag(t, 10)
            if t in (4, 5, 6):
                p["fx"] = [fx_impact(RX + 55, 37, t - 4)]
            return p
        self.add("melee", 10, melee_f, ms=85, loop=False, label="tusukan tombak jarak dekat")
        self.add("hit", 10, hit_fn(base, recoil=dict(rwa=-95)), ms=100, loop=False, core="hit", label="terdorong")
        up = dict(base, rh=(8, -12), rwa=-90, lh=(-11, -3), mouth="smile")
        self.add("victory", 16, victory_raise(base, up, sparkle_hand=None), ms=110, core="victory", label="tombak diacungkan")
        self.add("defeat", 16, shield_down_fn(dict(base, lw=None, rw=None), drops=[("spear", RX - 12, BASE - 2, 0), ("buckler", RX - 10, BASE - 5, 0)]),
                 ms=120, loop=False, hold=10, core="defeat", label="tombak rebah, perisai kecil turun, berlutut")


class Bondi(VikingBase):
    id = "viking-bondi"
    name = "Bondi Gobyet"
    role = "ranged"
    silhouette = ["cloth_cap", "simple_tunic", "flatbow", "seax"]
    mantle = None

    def torso(self, cv, g):
        m = R.ellipse(g.tcx, g.tcy, g.tw + 0.4, g.th + 0.4)
        R.solid(cv, m, "ol1", "ol2", shade_off=(2, 2))
        by = int(round(g.tcy + g.th - 1.5))
        cv.fill({(x, y) for (x, y) in m if y in (by, by + 1)}, "le2")
        I.seax(cv, (g.tcx + 2, by + 1), 15, {})

    def legs(self, cv, g):
        if g.p.get("mode") == "sit":
            R.sit_legs(cv, g, fur="fu1")
        else:
            R.legs(cv, g, fur="fu1", boots=("le1", "le2"))
        G.tunic_skirt(cv, g, ("ol1", "ol2"), w=8.0, rows=3)

    def headgear(self, cv, g):
        G.cloth_cap(cv, g)

    def arm(self, cv, g, i):
        R.arm(cv, g, i, sleeve="ol1", r=1.9)

    def build(self):
        base = dict(sx=4, rh=(10, 2), rw="flatbow", rwa=-8, nock=False, lh=(-9, 4))
        aim = dict(base, rh=(13, -3), rwa=0, nock=True, draw=1.0, lh=(5, -3), eyes="side", brows="angry", mouth="flat")
        full = dict(aim, draw=7.0, lh=(-1, -3))
        self.add("idle", 12, idle_loop(base, 12, alt=dict(rwa=-4), look=(4, 6)), ms=130, core="idle",
                 label="busur pendek, seax di sabuk, pakaian sederhana")

        def attack(t):
            if t < 6:
                p = kf(t, [(0, dict(base)), (2, dict(aim)), (5, dict(full))], 14, loop=False)
            else:
                p = kf(t, [(6, dict(aim, nock=False, draw=0.0, lh=(-4, -7))), (8, dict(aim, nock=False, draw=0.0, rh=(12, -6), rwa=-15)),
                           (13, dict(base))], 14, loop=False)
                if t <= 9:
                    p["fx"] = [lambda cv, g, t=t: I.arrow_flying(cv, RX + 34 + (t - 6) * 9, int(g.tcy - 3), 10)]
            p["tail"] = wag(t, 14)
            return p
        self.add("attack", 14, attack, ms=90, loop=False, core="attack", label="menarik busur pendek dan melepas")
        self.add("hit", 10, hit_fn(base), ms=100, loop=False, core="hit", label="terkejut")
        up = dict(base, rh=(5, -14), rwa=-90, lh=(-10, -6), mouth="smile")
        self.add("victory", 16, victory_raise(base, up, sparkle_hand=None), ms=110, core="victory", label="busur diangkat")
        self.add("defeat", 16, defeat_fall(dict(base, rw=None), drops=[("flatbow", RX + 10, BASE - 5, -90, {"nock": False})], early_drop=2),
                 ms=120, loop=False, hold=10, core="defeat", label="busur jatuh, rebah")


class FantasyViking(VikingBase):
    id = "fantasy-viking"
    name = "Fantasy Viking Gobyet"
    category = "fantasy"
    faction = "fantasy"
    role = "archetype"
    silhouette = ["giant_horns", "braided_beard", "red_cape", "round_shield", "axe"]
    horns = 1.8

    def back(self, cv, g):
        G.cape(cv, g, ("cr1", "cr2"), length=13, sway=g.p.get("cape", 0.0))

    def headgear(self, cv, g):
        G.horned_helm(cv, g, horns=self.horns, c=("go1", "go2"), band="cr2")
        G.braid_beard(cv, g, ("O", "y"))


I.register("round_shield_big", lambda cv, grip, ang, p: I.round_shield(cv, grip, ang, p, r=9.5), over_hand=True)
_orig_round = I.ITEMS["round_shield"][0]
I.register("round_shield", lambda cv, grip, ang, p: _orig_round(cv, grip, ang, p, r=p.get("r", 7.5)), over_hand=True)

CHARS = [VikingBase, Berserker, Huscarl, Gestir, Bondi, FantasyViking]
