"""Faksi Pirate v2: Captain, Skirmisher, Sharpshooter, Buccaneer, dan Fantasy Pirate.

Bahasa visual faksi: navy, cokelat, merah, emas. Topi + mantel + senjata + kuda-kuda menjadi satu siluet.
Senjata api adalah prop kartun: kepulan asap di ujung laras, tanpa peluru yang mengenai siapa pun.
Ledakan tong mesiu juga kartun (bintang 'pow' dan asap), tanpa luka.
"""
import math

import rig2 as R
import gear2 as G
import items2 as I
from char2 import Char
from rig2 import kf, wag, BASE, RX
from moves import (fx_impact, fx_dust, fx_item, fx_puff, fx_sparkle, fx_hand_sparkle, fx_speed, fx_mark, fx_stars_head,
                   fx_smoke_cloud, idle_loop, hit_fn, defeat_fall, victory_raise)


class _HatGeo:
    """Geo palsu untuk menggambar topi di lantai (topi jatuh)."""

    def __init__(self, x, y, p=None):
        self.hx, self.hy, self.p = x, y, p or {}

    def ihead(self):
        return int(self.hx), int(self.hy)


def fx_hat(fn, x, y, **kw):
    return lambda cv, g: fn(cv, _HatGeo(x, y), **kw)


def slash_fn(base, n=12, reach=(14, 1), ang_hit=20, impact_at=None):
    wind = dict(base, rh=(4, -10), rwa=-140, lean=-2, rw_back=True, mouth="shout", eyes="angry", brows="angry")
    hit = dict(base, rh=reach, rwa=ang_hit, lean=3, crouch=2, mouth="shout", eyes="angry", brows="angry")

    def fn(t):
        p = kf(t, [(0, dict(base)), (3, wind), (5, hit), (8, dict(hit, mouth="smirk", eyes="look")), (n - 1, dict(base))], n, loop=False)
        p.update(tail=wag(t, n), coat_sway=-1.5 if 4 <= t <= 7 else 0.0)
        if t in (5, 6, 7):
            ix, iy = impact_at or (RX + 36, 40)
            p["fx"] = [fx_impact(ix, iy, t - 5, "W"), fx_speed(RX + 18, 30, 3, 7, -1)]
        return p
    return fn


def gun_fn(base, aim, n=12, muzzle=(RX + 40, 30), recoil=(-3, -4), reload=None):
    """Bidik, tembak (kepulan kartun), hentakan, kembali."""
    def fn(t):
        keys = [(0, dict(base)), (3, dict(aim)), (5, dict(aim)), (6, dict(aim, rh=(aim["rh"][0] + recoil[0], aim["rh"][1] + recoil[1]),
                                                                       rwa=aim["rwa"] - 15, lean=-2, eyes="blink")),
                (8, dict(aim)), (n - 1, dict(base))]
        p = kf(t, keys, n, loop=False)
        p["tail"] = wag(t, n)
        if 6 <= t <= 9:
            p["fx"] = [lambda cv, g, k=t - 6: I.muzzle_puff(cv, muzzle[0], muzzle[1], k)]
        return p
    return fn


def hat_fall_fn(base, hat_fn, drops=(), n=16, hat_kw=None):
    """Defeat Pirate: terdorong, topi terlepas melayang lalu jatuh di lantai, Gobyet terduduk lalu rebah."""
    inner = defeat_fall(dict(base, hat_off=True), drops=drops, n=n, early_drop=4)

    def fn(t):
        p = inner(t)
        if t < 2:
            p["hat_off"] = False
        fx_key = "fx_after" if t >= 9 else "fx"
        if t >= 2:
            if t < 6:
                hx, hy = RX - 2 + (t - 2) * 3, 16 - (t - 2) * 2 + (t - 3) ** 2
            else:
                hx, hy = RX + 14, BASE + 2
            p[fx_key] = p.get(fx_key, []) + [fx_hat(hat_fn, hx, hy, **(hat_kw or {}))]
        return p
    return fn


# ================================================================== CAPTAIN
class Captain(Char):
    id = "pirate-captain"
    name = "Pirate Captain Gobyet"
    faction = "pirates"
    role = "leader"
    silhouette = ["big_tricorn_feather", "long_flared_coat", "epaulettes", "cutlass", "pistol"]
    body = {"torso_w": 8.0, "shoulder": 7.2}

    def legs(self, cv, g):
        if g.p.get("mode") == "sit":
            R.sit_legs(cv, g, fur="W", boots=("L", "l"))
        else:
            R.legs(cv, g, fur="W", boots=("L", "l"))

    def torso(self, cv, g):
        if g.p.get("mode") == "sit":
            m = R.ellipse(g.tcx, g.tcy, g.tw + 0.8, g.th + 0.6)
            R.solid(cv, m, "nv1", "nv2", shade_off=(2, 2))
        else:
            G.long_coat(cv, g, ("nv1", "nv2"), trim="go1", flare=6.0, lapel="W")
        G.sash(cv, g, ("cr1", "cr2"))

    def headgear(self, cv, g):
        if not g.p.get("hat_off"):
            G.tricorn_big(cv, g, ("L", "l"), "go1", feather=("cr1", "cr2"))

    def arm(self, cv, g, i):
        R.arm(cv, g, i, sleeve="nv1", r=2.0)
        hx, hy = g.hand[i]
        ex = g.elbow[i] or g.sh[i]
        R.solid(cv, R.ellipse(hx + (ex[0] - hx) * 0.25, hy + (ex[1] - hy) * 0.25, 2.2, 2.0), "go1", "go2", shade_off=(1, 1))

    def over_arm(self, cv, g, i):
        sx, sy = g.sh[i]
        s = -1 if i == 0 else 1
        m = R.ellipse(sx + s * 1.5, sy - 1, 4.2, 2.2)
        R.solid(cv, m, "go1", "go2", shade_off=(1, 1))
        for k in range(4):
            cv.put(int(sx + s * 1.5) - 3 + k * 2, int(sy) + 1, "go2")

    def build(self):
        base = dict(sx=5, lean=-1, rh=(11, 3), rw="cutlass", rwa=-60, lh=(-11, 4), lw="pistol", lwa=100, mouth="smirk")
        self.add("idle", 12, idle_loop(base, 12, alt=dict(rwa=-56), look=(3, 5)), ms=130, core="idle",
                 label="dada membusung, cutlass dan pistol")
        cmd = dict(base, rh=(14, -6), rwa=-20, lean=1, mouth="shout", eyes="look", brows="angry")

        def command(t):
            p = kf(t, [(0, dict(base)), (3, cmd), (9, cmd), (11, dict(base))], 12, loop=False)
            p["tail"] = wag(t, 12)
            if 3 <= t <= 9:
                p["fx"] = [fx_mark("!", dx=-22, dy=-18)]
            return p
        self.add("command", 12, command, ms=110, loop=False, label="memberi perintah, cutlass menunjuk ke depan")
        self.add("sword", 12, slash_fn(base), ms=90, loop=False, core="attack", label="tebasan cutlass")
        aim = dict(base, lh=(12, -4), lwa=0, rh=(6, 4), rwa=-80, eyes="side", brows="angry", mouth="flat", lean=0)
        self.add("pistol", 12, gun_fn(base, aim, muzzle=(RX + 31, 33)), ms=100, loop=False,
                 label="membidik pistol, kepulan asap kartun")
        pnt = dict(base, rh=(9, 2), rw="cutlass", rwa=60, lh=(13, -5), lw=None, eyes="side", mouth="smirk")

        def point(t):
            p = kf(t, [(0, dict(base)), (3, pnt), (9, pnt), (11, dict(base))], 12, loop=False)
            p["tail"] = wag(t, 12)
            return p
        self.add("point", 12, point, ms=110, loop=False, label="menunjuk sasaran")
        up = dict(base, rh=(8, -14), rwa=-80, lh=(-11, -2), mouth="smile")
        self.add("victory", 16, victory_raise(base, up, sparkle_hand=1), ms=110, core="victory", label="cutlass diangkat")
        self.add("hit", 10, hit_fn(base, recoil=dict(rwa=-90)), ms=100, loop=False, core="hit", label="terhuyung, topi miring")
        self.add("defeat", 16, hat_fall_fn(dict(base, rw=None, lw=None), lambda cv, g: G.tricorn_big(cv, g, ("L", "l"), "go1", feather=("cr1", "cr2")),
                                           drops=[("cutlass", RX + 4, BASE - 3, 0)]),
                 ms=120, loop=False, hold=10, core="defeat", label="topi kapten jatuh, cutlass terlepas, terduduk lalu rebah")


# ================================================================== SKIRMISHER
class Skirmisher(Char):
    id = "pirate-skirmisher"
    name = "Pirate Skirmisher Gobyet"
    faction = "pirates"
    role = "mobility"
    silhouette = ["bandana_tails", "striped_shirt_open_vest", "powder_keg", "short_blade", "bare_feet_agile"]
    body = {"torso_w": 7.0, "torso_h": 6.4, "shoulder": 6.2}

    def legs(self, cv, g):
        if g.p.get("mode") == "sit":
            R.sit_legs(cv, g, fur="nv1")
            return
        R.legs(cv, g, fur="B")
        for i, s in enumerate((-1, 1)):
            hx, hy = g.hips[i]
            fx, fy = g.feet[i]
            R.solid(cv, R.capsule((hx, hy), ((hx + fx) / 2, (hy + fy) / 2 - 1), 2.5), "nv1", "nv2", shade_off=(1, 1))

    def torso(self, cv, g):
        G.short_vest(cv, g, ("cr1", "cr2"))

    def headgear(self, cv, g):
        if not g.p.get("hat_off"):
            G.bandana_v2(cv, g, ("R", "T"), knot_flap=g.p.get("tail", 0.0) * 2)

    def arm(self, cv, g, i):
        R.arm(cv, g, i, sleeve="B", r=1.8)

    def build(self):
        base = dict(sx=5, crouch=2, lean=2, rh=(11, 2), rw="dagger", rwa=-30, lh=(-10, 2), lw="powder_keg", eyes="side",
                    mouth="smirk")

        def idle(t):
            p = kf(t, [(0, dict(base)), (3, dict(base, crouch=3)), (6, dict(base)), (9, dict(base, crouch=3))], 12)
            p["tail"] = wag(t, 12, 2)
            if t == 7:
                p["eyes"] = "blink"
            return p
        self.add("idle", 12, idle, ms=110, core="idle", label="memantul ringan, tong mesiu di tangan")

        def run(t):
            ph = t * math.tau / 8
            p = dict(base, lean=4, crouch=2 + (1 if t % 4 == 0 else 0), lift_l=max(0, math.sin(ph)) * 4, lift_r=max(0, -math.sin(ph)) * 4,
                     fx_l=math.cos(ph) * 3, fx_r=-math.cos(ph) * 3, rh=(10 + math.cos(ph) * 3, 1), lh=(-9 - math.cos(ph) * 3, 2))
            p["tail"] = wag(t, 8, 2)
            p["fx"] = [fx_speed(RX - 12, 42, 3, 6, -1)]
            return p
        self.add("run", 8, run, ms=80, label="berlari lincah")

        def dash(t):
            p = kf(t, [(0, dict(base)), (2, dict(base, crouch=4, lean=-1)), (4, dict(base, dx=12, lean=6)), (7, dict(base, dx=12, lean=3)),
                       (9, dict(base))], 10, loop=False)
            p["tail"] = wag(t, 10)
            if 3 <= t <= 6:
                p["fx"] = [fx_speed(RX - 4 + (t - 3) * 4, 40, 4, 9, -1), fx_dust(RX - 2 + (t - 3) * 3, BASE - 1, t - 3)]
            return p
        self.add("dash", 10, dash, ms=70, loop=False, label="melesat ke depan")
        self.add("attack", 10, slash_fn(base, n=10, reach=(13, 0), ang_hit=0, impact_at=(RX + 38, 40)), ms=80, loop=False,
                 core="attack", label="sayatan cepat")

        def throw(t):
            up = dict(base, lh=(-6, -12), lean=-2, crouch=1)
            rel = dict(base, lh=(10, -6), lw=None, lean=4, mouth="shout")
            p = kf(t, [(0, dict(base)), (3, up), (5, rel), (11, dict(rel, mouth="smirk"))], 12, loop=False, smooth=False)
            p["tail"] = wag(t, 12)
            if t >= 5:
                k = t - 5
                x, y = RX + 16 + k * 5, 24 - k * 4 + k * k * 0.9
                p["fx"] = [fx_item("powder_keg", x, y, 0, lit=True)]
            return p
        self.add("throw", 12, throw, ms=80, loop=False, label="melempar tong mesiu melengkung")

        def explosion(t):
            cover = dict(base, lw=None, lh=(-7, -9), rh=(7, -9), rw=None, eyes="blink" if t % 2 else "relief", brows="worried",
                         mouth="o", crouch=4, lean=-1)
            p = dict(cover)
            p["tail"] = wag(t, 12)
            k = min(t, 4) if t < 8 else max(0, 4 - (t - 8))
            fx = [fx_impact(RX + 46, BASE - 14, min(t, 3), "Y")] if t < 6 else []
            if t >= 2:
                fx.append(fx_smoke_cloud(RX + 46, BASE - 10, k))
            p["fx"] = fx
            return p
        self.add("explosion", 12, explosion, ms=90, loop=False, label="tong meledak kartun, menutup telinga")

        def recover(t):
            p = kf(t, [(0, dict(base, lw=None, crouch=4, eyes="relief", mouth="o")), (5, dict(base))], 6, loop=False)
            p["tail"] = wag(t, 6)
            if t < 4:
                p["fx"] = [lambda cv, g: R.sweat(cv, g.ihead()[0] + 11, g.ihead()[1] - 6)]
            return p
        self.add("recover", 6, recover, ms=110, loop=False, label="mengibas debu, siap lagi")
        self.add("hit", 10, hit_fn(base), ms=90, loop=False, core="hit", label="terpental ringan")
        up = dict(base, crouch=0, lean=0, rh=(8, -13), rwa=-80, lh=(-9, -12), lw="powder_keg", mouth="smile")
        self.add("victory", 16, victory_raise(base, up, sparkle_hand=None), ms=100, core="victory",
                 label="melompat, tong mesiu dan belati terangkat")
        self.add("defeat", 16, hat_fall_fn(dict(base, rw=None, lw=None), lambda cv, g: G.bandana_v2(cv, g, ("R", "T")),
                                           drops=[("powder_keg", RX + 16, BASE + 1, 0)]),
                 ms=120, loop=False, hold=10, core="defeat", label="bandana terlepas, tong menggelinding")


# ================================================================== SHARPSHOOTER
class Sharpshooter(Char):
    id = "pirate-sharpshooter"
    name = "Pirate Sharpshooter Gobyet"
    faction = "pirates"
    role = "long-range"
    silhouette = ["wide_flat_hat", "long_rifle", "light_long_coat"]
    body = {"torso_w": 7.0, "shoulder": 6.2}

    def legs(self, cv, g):
        if g.p.get("mode") == "sit":
            R.sit_legs(cv, g, fur="le1", boots=("D", "K"))
        else:
            R.legs(cv, g, fur="le1", boots=("D", "K"))

    def torso(self, cv, g):
        if g.p.get("mode") == "sit":
            R.solid(cv, R.ellipse(g.tcx, g.tcy, g.tw + 0.6, g.th + 0.6), "d", "e", shade_off=(2, 2))
        else:
            G.long_coat(cv, g, ("d", "e"), trim=None, flare=3.0, length=2, lapel="cm1")
        cv.fill(R.capsule((g.tcx - 6, g.tcy - 5), (g.tcx + 6, g.tcy + 4), 0.9), "le2")

    def headgear(self, cv, g):
        if not g.p.get("hat_off"):
            G.wide_hat(cv, g, ("D", "N"), band="cr1")

    def arm(self, cv, g, i):
        R.arm(cv, g, i, sleeve="d", r=1.9)

    def build(self):
        base = dict(sx=4, rh=(9, -3), rw="rifle", rwa=-62, lh=(-6, 4), eyes="look", mouth="flat")
        aim = dict(base, rh=(4, -3), rwa=0, lh=(12, -2), grip2=False, eyes="angry", brows="flat", mouth="flat", lean=1, crouch=1, sx=5)
        self.add("idle", 12, idle_loop(base, 12, alt=dict(rwa=-60), look=(6, 8)), ms=140, core="idle",
                 label="senapan panjang di bahu, topi lebar")

        def aim_f(t):
            p = kf(t, [(0, dict(aim)), (4, dict(aim, crouch=2))], 8)
            p["tail"] = wag(t, 8)
            if t in (2, 3):
                p["eyes"] = "angry"
            return p
        self.add("aim", 8, aim_f, ms=150, label="membidik dengan mata menyipit")
        self.add("shoot", 12, gun_fn(base, aim, muzzle=(RX + 54, 34), recoil=(-3, -2)), ms=100, loop=False, core="attack",
                 label="menembak: kepulan kartun di ujung laras")

        def recoil(t):
            kick = dict(aim, rh=(1, -6), rwa=-20, lean=-3, dx=-1, eyes="blink")
            p = kf(t, [(0, dict(aim)), (1, kick), (6, dict(aim))], 8, loop=False)
            p["tail"] = wag(t, 8)
            return p
        self.add("recoil", 8, recoil, ms=90, loop=False, label="hentakan popor ke bahu")

        def reload(t):
            hold = dict(base, rh=(5, 4), rwa=-80, lh=(4, -10), eyes="down", mouth="flat")
            p = kf(t, [(0, dict(base)), (3, hold), (5, dict(hold, lh=(4, -14))), (7, dict(hold, lh=(4, -9))), (9, dict(hold, lh=(4, -14))),
                       (13, dict(base))], 14, loop=False)
            p["tail"] = wag(t, 14)
            if 3 <= t <= 10:
                p["fx"] = [lambda cv, g: cv.fill(R.capsule(g.hand[0], (g.hand[0][0], g.hand[0][1] + 9), 0.5), "st3")]
            return p
        self.add("reload", 14, reload, ms=100, loop=False, label="mengisi ulang dengan tongkat pemadat")
        up = dict(base, rh=(8, -14), rwa=-90, lh=(-9, -6), mouth="smile")
        self.add("victory", 16, victory_raise(base, up, sparkle_hand=None), ms=110, core="victory", label="senapan diangkat tegak")
        self.add("hit", 10, hit_fn(base, recoil=dict(rwa=-80)), ms=100, loop=False, core="hit", label="terdorong")
        self.add("defeat", 16, hat_fall_fn(dict(base, rw=None), lambda cv, g: G.wide_hat(cv, g, ("D", "N"), band="cr1"),
                                           drops=[("rifle", RX - 6, BASE - 3, 0)]),
                 ms=120, loop=False, hold=10, core="defeat", label="topi lebar jatuh, senapan terlepas")


# ================================================================== BUCCANEER
class Buccaneer(Char):
    id = "pirate-buccaneer"
    name = "Pirate Buccaneer Gobyet"
    faction = "pirates"
    role = "heavy"
    silhouette = ["big_body", "heavy_coat", "giant_hammer", "anchor_on_back", "crossbelts"]
    body = {"torso_w": 10.4, "torso_h": 7.8, "shoulder": 8.8}

    def back(self, cv, g):
        if g.p.get("rw") != "anchor":
            I.anchor(cv, (g.tcx - 4, g.tcy - 8), -120, {})

    def legs(self, cv, g):
        if g.p.get("mode") == "sit":
            R.sit_legs(cv, g, fur="le2", boots=("L", "l"))
        else:
            R.legs(cv, g, fur="le2", boots=("L", "l"))

    def torso(self, cv, g):
        if g.p.get("mode") == "sit":
            R.solid(cv, R.ellipse(g.tcx, g.tcy, g.tw + 1, g.th + 0.6), "i", "2", shade_off=(2, 2))
        else:
            G.long_coat(cv, g, ("i", "2"), trim=None, flare=4.0, length=-2, lapel="F")
        G.crossbelts(cv, g, "le2", "go1")

    def headgear(self, cv, g):
        if not g.p.get("hat_off"):
            G.skull_cap(cv, g, ("nv1", "nv2"))
            hx, hy = g.ihead()
            cv.fill({(hx + 9, hy - 2), (hx + 9, hy - 1)}, "go1")

    def arm(self, cv, g, i):
        R.arm(cv, g, i, sleeve="i", r=2.5)

    def hand(self, cv, g, i):
        R.hand(cv, g, i, r=2.4)

    def build(self):
        base = dict(sx=6, rh=(13, -1), rw="hammer", rwa=80, lh=(-12, 4), mouth="frown")
        self.add("idle", 12, idle_loop(base, 12, alt=dict(rh=(13, 0))), ms=150, core="idle",
                 label="bertumpu pada palu raksasa, jangkar di punggung")
        ready = dict(base, rh=(11, 2), rwa=-60, rw_back=False, lh=(4, 4), grip2=True, crouch=2, sx=7, brows="angry")
        heavy = lambda: None  # noqa: E731

        def heavy_attack(t):
            hit = dict(ready, rh=(14, 6), rwa=10, lh=(7, 6), lean=4, crouch=3, mouth="shout")
            p = kf(t, [(0, dict(base)), (3, dict(ready, rh=(4, 0), rwa=-140, lean=-2, lh=(-4, 0))), (6, hit), (9, dict(hit, mouth="flat")),
                       (13, dict(base))], 14, loop=False)
            p["tail"] = wag(t, 14)
            if t in (6, 7, 8):
                p["fx"] = [fx_impact(RX + 40, 44, t - 6)]
            return p
        self.add("heavy_attack", 14, heavy_attack, ms=100, loop=False, label="ayunan palu menyamping")

        def smash(t):
            up = dict(ready, rh=(4, -14), rwa=-100, lh=(-2, -12), lean=-2, dy=0, mouth="shout", rw_back=True)
            down = dict(ready, rh=(13, 6), rwa=40, lh=(6, 6), lean=4, crouch=4, mouth="shout", rw_back=False)
            p = kf(t, [(0, dict(base)), (4, up), (6, down), (10, dict(down, mouth="smirk")), (15, dict(base))], 16, loop=False)
            p["tail"] = wag(t, 16)
            if t in (6, 7, 8, 9):
                p["fx"] = [fx_impact(RX + 30, BASE - 4, min(t - 6, 2)), fx_dust(RX + 28, BASE - 1, t - 6), fx_dust(RX + 10, BASE - 1, t - 6)]
                p["dy"] = -1 if t == 7 else 0
            return p
        self.add("hammer_smash", 16, smash, ms=90, loop=False, core="attack", label="palu dihantamkan ke lantai, lantai bergetar")

        def anchor_attack(t):
            b2 = dict(base, rw="anchor", rwa=-120, rh=(10, -6), rw_back=True)
            hit = dict(b2, rh=(14, 4), rwa=15, lh=(6, 5), grip2=True, lean=4, crouch=3, rw_back=False, mouth="shout")
            p = kf(t, [(0, b2), (3, dict(b2, rh=(2, -10), rwa=-170, lean=-3)), (6, hit), (9, dict(hit, mouth="flat")), (13, b2)], 14,
                   loop=False)
            p["tail"] = wag(t, 14)
            if t in (6, 7, 8):
                p["fx"] = [fx_impact(RX + 44, 46, t - 6)]
            return p
        self.add("anchor_attack", 14, anchor_attack, ms=100, loop=False, label="jangkar diayunkan seperti gada")
        self.add("hit", 10, hit_fn(base, recoil=dict(rwa=70)), ms=110, loop=False, core="hit", label="nyaris tak bergeming")
        up = dict(base, rh=(9, -14), rwa=-95, rw_back=False, lh=(-12, -6), mouth="smile")
        self.add("victory", 16, victory_raise(base, up, sparkle_hand=None, hop=False), ms=120, core="victory",
                 label="palu diangkat tinggi")
        self.add("defeat", 16, defeat_fall(dict(base, rw=None, rw_back=False), drops=[("hammer", RX + 2, BASE - 7, 0)], early_drop=4),
                 ms=130, loop=False, hold=10, core="defeat", label="palu jatuh berdebam, rebah berat")


# ================================================================== FANTASY PIRATE
class FantasyPirate(Char):
    id = "fantasy-pirate"
    name = "Fantasy Pirate Gobyet"
    category = "fantasy"
    faction = "fantasy"
    role = "archetype"
    silhouette = ["tricorn", "eyepatch", "red_coat", "cutlass", "telescope", "treasure_map"]
    body = {"torso_w": 7.8, "shoulder": 7.0}

    def legs(self, cv, g):
        if g.p.get("mode") == "sit":
            R.sit_legs(cv, g, fur="nv1", boots=("L", "l"))
        else:
            R.legs(cv, g, fur="nv1", boots=("L", "l"))

    def torso(self, cv, g):
        if g.p.get("mode") == "sit":
            R.solid(cv, R.ellipse(g.tcx, g.tcy, g.tw + 0.7, g.th + 0.6), "cr1", "cr2", shade_off=(2, 2))
        else:
            G.long_coat(cv, g, ("cr1", "cr2"), trim="go1", flare=3.5, length=-1, lapel="W")

    def head(self, cv, g):
        R.head(cv, g)
        G.eyepatch(cv, g)

    def headgear(self, cv, g):
        if not g.p.get("hat_off"):
            G.tricorn_big(cv, g, ("L", "l"), "go1")

    def arm(self, cv, g, i):
        R.arm(cv, g, i, sleeve="cr1", r=1.9)

    def build(self):
        base = dict(sx=5, rh=(11, 3), rw="cutlass", rwa=-60, lh=(-10, 3), lw="treasure_map")

        def idle(t):
            p = idle_loop(base, 12, alt=dict(rwa=-56))(t)
            if 4 <= t <= 7:
                p.update(lw="telescope", lh=(-2, -7), lwa=-10)
            return p
        self.add("idle", 12, idle, ms=130, core="idle", label="peta harta, sesekali meneropong")
        self.add("attack", 12, slash_fn(base), ms=90, loop=False, core="attack", label="tebasan cutlass")
        self.add("hit", 10, hit_fn(base), ms=100, loop=False, core="hit", label="terhuyung")
        up = dict(base, rh=(8, -14), rwa=-80, lh=(-10, -8), mouth="smile")
        self.add("victory", 16, victory_raise(base, up, sparkle_hand=0), ms=110, core="victory", label="peta harta diangkat")
        self.add("defeat", 16, hat_fall_fn(dict(base, rw=None, lw=None), lambda cv, g: G.tricorn_big(cv, g, ("L", "l"), "go1"),
                                           drops=[("treasure_map", RX - 12, BASE, 0)]),
                 ms=120, loop=False, hold=10, core="defeat", label="topi jatuh, peta terlepas")


CHARS = [Captain, Skirmisher, Sharpshooter, Buccaneer, FantasyPirate]
