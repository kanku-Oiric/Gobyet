"""Efek dan pola gerak bersama v2 (hit, defeat, victory), supaya tiap kelas cukup memberi pose dasar
dan bumbu khasnya sendiri."""
import math

import rig2 as R
import items2 as I
from rig2 import kf, wag, BASE, RX


# ------------------------------------------------------------------ efek sebagai closure (cv, g)
def fx_impact(x, y, k=0, c="Y"):
    return lambda cv, g: R.impact(cv, int(x), int(y), k, c)


def fx_dust(x, y, k=0):
    return lambda cv, g: R.dust(cv, int(x), int(y), k)


def fx_stars(cx, cy, t):
    def f(cv, g):
        for k in range(3):
            a = t * 0.9 + k * math.tau / 3
            R.star(cv, int(cx + math.cos(a) * 8), int(cy + math.sin(a) * 2.5), "Y")
    return f


def fx_stars_head(t):
    def f(cv, g):
        hx, hy = g.ihead()
        for k in range(3):
            a = t * 0.9 + k * math.tau / 3
            R.star(cv, int(hx + math.cos(a) * 9), int(hy - 12 + math.sin(a) * 2.5), "Y")
    return f


def fx_item(name, x, y, ang=0, **kw):
    def f(cv, g):
        I.ITEMS[name][0](cv, (x, y), ang, dict(kw))
    return f


def fx_puff(x, y, r):
    return lambda cv, g: R.puff(cv, x, y, r)


def fx_sparkle(x, y, t):
    def f(cv, g):
        if t % 2 == 0:
            R.star(cv, int(x), int(y), "W", big=True)
        else:
            R.star(cv, int(x) + 2, int(y) - 2, "Y")
    return f


def fx_hand_sparkle(i, t, dx=0, dy=-4):
    def f(cv, g):
        x, y = g.hand[i]
        if t % 2 == 0:
            R.star(cv, int(x + dx), int(y + dy), "W", big=True)
        else:
            R.star(cv, int(x + dx) + 2, int(y + dy) - 2, "Y")
    return f


def fx_speed(x, y, n=3, length=7, direction=-1):
    return lambda cv, g: R.speed_lines(cv, x, y, n, length, direction)


def fx_mark(glyph, dx=8, dy=-14, fill="W"):
    def f(cv, g):
        hx, hy = g.ihead()
        R.mark_bubble(cv, hx + dx, hy + dy, glyph, fill)
    return f


def fx_sweat():
    def f(cv, g):
        hx, hy = g.ihead()
        R.sweat(cv, hx + 11, hy - 6)
    return f


def fx_confetti(seed, t):
    return lambda cv, g: R.confetti(cv, seed, t)


def fx_smoke_cloud(x, y, k):
    """Awan asap besar (Assassin, Wizard): 4 kepulan yang membesar lalu menipis."""
    def f(cv, g):
        r = 3 + k * 1.5
        for (dx, dy, s) in ((0, 0, 1.0), (-6, 3, 0.8), (6, 2, 0.85), (0, -6, 0.75), (-4, -4, 0.6), (5, -5, 0.6)):
            R.puff(cv, x + dx * (1 + k * 0.25), y + dy * (1 + k * 0.2), max(1.5, r * s))
    return f


def fx_text(s, x, y, c="R"):
    return lambda cv, g: R.mini_text(cv, s, x, y, c)


# ------------------------------------------------------------------ pola state
def idle_loop(base, n=12, alt=None, blink=8, extra=None, look=None):
    """Napas pelan (jongkok 0/1 px), kedip satu frame, opsional pose alternatif kecil di tengah."""
    alt = dict(base, crouch=base.get("crouch", 0) + 1, **(alt or {}))

    def fn(t):
        p = kf(t, [(0, dict(base)), (n // 2, alt)], n)
        p.update(tail=wag(t, n), plume=wag(t, n), cape=wag(t, n), coat_sway=math.sin(wag(t, n)) * 0.8)
        if look and look[0] <= t <= look[1]:
            p["eyes"] = "side"
        if t == blink:
            p["eyes"] = "blink"
        if extra:
            extra(t, p)
        return p
    return fn


def hit_fn(base, n=10, recoil=None, rattle=False):
    rec = dict(base, lean=-3, dx=-2, hdx=-1, eyes="wide", brows="up", mouth="o", **(recoil or {}))
    mid = dict(base, lean=-1, dx=-1, eyes="relief", brows="worried", mouth="frown")

    def fn(t):
        p = kf(t, [(0, dict(base)), (2, rec), (6, mid), (n - 1, dict(base))], n, loop=False)
        p.update(tail=wag(t, n), plume=wag(t, n, 2))
        if rattle and 2 <= t <= 6:
            p["rattle"] = 1 if t % 2 else -1
        if 2 <= t <= 7:
            p["fx"] = [fx_stars_head(t)]
        return p
    return fn


def defeat_fall(base, drops=(), n=16, lie_extra=None, sit_pose=None, early_drop=4, after=None):
    """Limbung, lutut tertekuk, duduk, lalu rebah ke belakang. drops = [(item, x, y, ang, kw), ...]
    yang muncul di lantai setelah frame early_drop."""
    stag = dict(base, lean=-2, dx=-2, eyes="wide", brows="up", mouth="o")
    buck = dict(base, crouch=4, dx=-2, eyes="relief", brows="worried", mouth="o", rw=None, lw=None)
    sit = dict(base, mode="sit", dx=-2, rw=None, lw=None, rh=(9, 5), lh=(-9, 5), eyes="relief", brows="worried", **(sit_pose or {}))

    def fn(t):
        if t < 9:
            p = kf(t, [(0, dict(base)), (2, stag), (4, buck), (6, sit), (8, sit)], n, loop=False, smooth=False)
        else:
            p = dict(sit, rot=-90, rot_ground=True, rh=(9, 2), lh=(-9, 2), eyes="relief", brows="worried",
                     mouth="frown", **(lie_extra or {}))
        p.update(tail=0.0, plume=0.0)
        fx = [fx_item(it[0], it[1], it[2], it[3], **(it[4] if len(it) > 4 else {})) for it in drops] if t >= early_drop else []
        if 9 <= t <= 11:
            fx += [fx_dust(RX - 10, BASE - 1, t - 9), fx_puff(RX - 16, BASE - 4, 2.0 + (t - 9))]
        if t >= 13:
            fx.append(fx_puff(RX - 8 + (t - 13), BASE - 20 - (t - 13) * 2, 1.2 + (t - 13) * 0.3))
        if after:
            after(t, p, fx)
        p["fx_after" if t >= 9 else "fx"] = fx
        return p
    return fn


def victory_raise(base, up, n=16, hop=True, sparkle_hand=1, extra=None):
    def fn(t):
        keys = [(0, dict(base)), (4, dict(up)), (8, dict(up, crouch=up.get("crouch", 0) + 1, eyes="happy")), (12, dict(up)),
                (15, dict(up))]
        p = kf(t, keys, n)
        p.update(tail=wag(t, n, 2), plume=wag(t, n, 2), cape=wag(t, n, 2))
        if hop and t in (9, 10, 11):
            p["dy"] = -1
        if 4 <= t <= 13 and sparkle_hand is not None:
            p["fx"] = [fx_hand_sparkle(sparkle_hand, t)]
        if extra:
            extra(t, p)
        return p
    return fn
