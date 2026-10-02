"""Karakter domain v2: Philosopher, Academic, Scientist, Mathematician, Lawyer, Historian, Economist, Psychologist,
Sociologist, Engineer, Detective, Researcher, Pak Haji, Priest.

Setiap karakter domain mengubah siluet lewat pakaian panjang/pendek, topi, dan prop besar (papan berkaki,
gulungan lini masa, piala, kaca pembesar), bukan hanya warna.

Aturan 7.2 (teologi): Pak Haji dan Priest diperlakukan identik: aura yang sama persis, jumlah dan jenis state
paralel, tanpa komedi, tanpa simbol yang meremehkan. Aura adalah efek visual, bukan penanda argumen benar.
"""
import math

import rig2 as R
import gear2 as G
import items2 as I
import props2 as P
from char2 import Char
from rig2 import kf, wag, BASE, RX
from moves import (fx_impact, fx_dust, fx_item, fx_puff, fx_sparkle, fx_hand_sparkle, fx_speed, fx_mark, fx_stars_head,
                   fx_sweat, fx_confetti, idle_loop, hit_fn, defeat_fall, victory_raise)

BOARD_X = RX + 13


def fx_board(kind, t=0, x=BOARD_X, y=24, w=22, h=16):
    return lambda cv, g: P.easel_board(cv, x, y, w, h, kind, t)


def fx_bulb(on=True, dy=-17):
    def f(cv, g):
        hx, hy = g.ihead()
        P.lightbulb(cv, hx + 1, hy + dy, on)
    return f


# ================================================================== pola state domain
def talk(t):
    return "o" if t % 4 in (1, 2) else "smile"


def st_read(base, item="book_open", n=12, flip=(6, 7), extra=None, **kw):
    pose = dict(dict(base, rh=(3, 0), rw=item, lh=(-4, 1), lw=None, eyes="down", mouth="flat"), **kw)

    def fn(t):
        p = kf(t, [(0, dict(pose)), (n // 2, dict(pose, crouch=1))], n)
        p["tail"] = wag(t, n)
        if t in flip:
            p["page"] = 1
        if t == n - 2:
            p["eyes"] = "blink"
        if extra:
            extra(t, p)
        return p
    return fn


def st_write(base, held="clipboard", tool="pen", n=12, extra=None, **kw):
    pose = dict(dict(base, lh=(-3, 0), lw=held, rh=(3, -3), rw=tool, rwa=-120, eyes="down", mouth="flat"), **kw)

    def fn(t):
        dx = [0, 1, 2, 1, 0, 1, 2, 3, 2, 1, 0, -1][t % 12]
        dy = [0, -1, 0, 1, 0, -1, 0, 1, 2, 2, 1, 0][t % 12]
        p = dict(pose, rh=(pose["rh"][0] + dx, pose["rh"][1] + dy))
        p["tail"] = wag(t, n)
        if extra:
            extra(t, p)
        return p
    return fn


def st_think(base, n=16, glyph="?", hand=(3, -6), extra=None, **kw):
    pose = dict(dict(base, rh=hand, rw=None, eyes="side", brows="raised", mouth="flat"), **kw)

    def fn(t):
        p = kf(t, [(0, dict(base)), (3, dict(pose)), (n - 3, dict(pose)), (n - 1, dict(base))], n)
        p["tail"] = wag(t, n)
        if 4 <= t <= n - 4:
            p["fx"] = [fx_mark("..." if t < n // 2 + 1 else glyph)]
        if t == n // 2:
            p["eyes"] = "blink"
        if extra:
            extra(t, p)
        return p
    return fn


def st_present(base, board="formula", n=12, hand=(14, -6), extra=None, **kw):
    pose = dict(dict(base, rh=hand, rw=None, eyes="side"), **kw)

    def fn(t):
        p = kf(t, [(0, dict(pose)), (n // 2, dict(pose, rh=(hand[0], hand[1] - 2), lean=1))], n)
        p["tail"] = wag(t, n)
        p["mouth"] = talk(t)
        fx = [fx_board(board, t)] if board else []
        p["fx_back"] = fx
        if extra:
            extra(t, p)
        return p
    return fn


def st_point(base, n=10, glyph=None, extra=None, **kw):
    pose = dict(dict(base, rh=(16, -5), rw=None, lean=2, eyes="side", brows="angry", mouth="smirk"), **kw)

    def fn(t):
        p = kf(t, [(0, dict(base)), (3, pose), (n - 2, pose), (n - 1, dict(base))], n, loop=False)
        p["tail"] = wag(t, n)
        if glyph and 3 <= t <= n - 2:
            p["fx"] = [fx_mark(glyph, dx=-22, dy=-18)]
        if extra:
            extra(t, p)
        return p
    return fn


def st_shocked(base, n=10, **kw):
    pose = dict(dict(base, dx=-2, dy=-2, eyes="wide", brows="up", mouth="o", lh=(-11, -6), rh=(11, -6)), **kw)

    def fn(t):
        p = kf(t, [(0, dict(base)), (2, pose), (4, dict(pose, dy=0)), (8, dict(pose, dy=0)), (9, dict(base))], n, loop=False)
        p["tail"] = wag(t, n, 2)
        if 2 <= t <= 8:
            p["fx"] = [fx_mark("!", dx=8, dy=-15), fx_sweat()]
        return p
    return fn


def st_eureka(base, n=12, **kw):
    pose = dict(dict(base, rh=(8, -14), rw=None, eyes="happy", mouth="smile"), **kw)

    def fn(t):
        p = kf(t, [(0, dict(base)), (3, pose), (n - 2, pose), (n - 1, dict(base))], n, loop=False)
        p["tail"] = wag(t, n, 2)
        if t in (4, 5):
            p["dy"] = -2
        if 3 <= t <= n - 2:
            p["fx"] = [fx_bulb(on=t % 4 != 3)]
        return p
    return fn


def st_confused(base, n=12, **kw):
    pose = dict(dict(base, rh=(5, -15), rw=None, eyes="side", brows="worried", mouth="frown", tilt=1), **kw)

    def fn(t):
        p = kf(t, [(0, dict(base)), (3, pose), (6, dict(pose, rh=(6, -14))), (9, pose), (11, dict(base))], n)
        p["tail"] = wag(t, n)
        if 3 <= t <= 10:
            p["fx"] = [fx_mark("?")]
        if t == 7:
            p["eyes"] = "blink"
        return p
    return fn


def st_search(base, item="magnifier", n=12, **kw):
    lo = dict(dict(base, crouch=3, rw=item, rwa=10, rh=(4, 6), eyes="down", brows="raised", mouth="flat"), **kw)
    hi = dict(lo, rh=(16, 4), eyes="side", lean=2)

    def fn(t):
        p = kf(t, [(0, lo), (n // 2, hi)], n)
        p["tail"] = wag(t, n)
        return p
    return fn


def st_compare(base, l_item, r_item, n=12, **kw):
    pose = dict(dict(base, lh=(-11, -3), lw=l_item, rh=(11, -3), rw=r_item, rwa=0, mouth="flat"), **kw)

    def fn(t):
        p = dict(pose)
        p["eyes"] = "left" if (t // 4) % 2 == 0 else "side"
        p["brows"] = "raised" if t % 8 >= 6 else "flat"
        p["tail"] = wag(t, n)
        return p
    return fn


def st_defeat_sit(base, drops=(), n=16, **kw):
    """Defeat domain: tersentak, duduk lesu di lantai, prop terjatuh, menghela napas. Lembut, tanpa jatuh keras."""
    stag = dict(base, dx=-1, eyes="wide", brows="up", mouth="o")
    sit = dict(dict(base, mode="sit", rw=None, lw=None, rh=(9, 4), lh=(-9, 4), eyes="relief", brows="worried", mouth="frown", hdy=1), **kw)

    def fn(t):
        p = kf(t, [(0, dict(base)), (2, stag), (5, sit), (15, sit)], n, loop=False, smooth=False)
        p.update(tail=0.0)
        fx = [fx_item(d[0], d[1], d[2], d[3], **(d[4] if len(d) > 4 else {})) for d in drops] if t >= 4 else []
        if t >= 8:
            k = (t - 8) % 6
            fx.append(fx_puff(RX + 12 + k, BASE - 26 - k * 2, 1.3 + k * 0.25))
        p["fx"] = fx
        return p
    return fn


# ================================================================== pakaian
def shirt(cv, g, c=("W", "smk"), tie=None, collar=True, buttons=True):
    m = R.ellipse(g.tcx, g.tcy, g.tw + 0.4, g.th + 0.4)
    R.solid(cv, m, c[0], c[1], shade_off=(2, 2))
    cx, top = int(round(g.tcx)), int(round(g.tcy - g.th))
    if collar:
        cv.fill({(cx - 2, top + 1), (cx - 1, top + 2), (cx + 2, top + 1), (cx + 1, top + 2)}, c[1])
    if tie:
        tm = R.rect(cx, top + 2, 1, 2) | R.rect(cx - 1, top + 4, 3, 6) | {(cx, top + 10)}
        R.solid(cv, tm, tie, None, outline=None)
    elif buttons:
        for k in range(3):
            cv.put(cx, top + 4 + k * 3, c[1])
    return m


def trousers(cv, g, c=("L", "l"), shoes=("L", "K")):
    if g.p.get("mode") == "sit":
        R.sit_legs(cv, g, fur=c[0], boots=shoes)
    else:
        R.legs(cv, g, fur=c[0], boots=shoes)


def glasses(cv, g, c="K", round_=True):
    hx, hy = g.ihead()
    for s in (-1, 1):
        ex = hx + s * 4
        ring = R.rect(ex - 3, hy - 3, 6, 6) - R.rect(ex - 2, hy - 2, 4, 4)
        if round_:
            ring -= {(ex - 3, hy - 3), (ex + 2, hy - 3), (ex - 3, hy + 2), (ex + 2, hy + 2)}
        cv.fill(ring, c)
    cv.fill({(hx - 1, hy - 1), (hx, hy - 1)}, c)


def beard(cv, g, c=("H", "h"), long=False):
    hx, hy = g.ihead()
    m = {(x, y) for (x, y) in R.ellipse(hx, hy + 7.5, 7.0, 4.2 if not long else 6.5) if y >= hy + 6}
    m |= {(x, hy + 5) for x in range(hx - 6, hx - 2)} | {(x, hy + 5) for x in range(hx + 2, hx + 6)}
    R.solid(cv, m, c[0], c[1], outline=c[1], shade_off=(1, 1))


def mortarboard(cv, g, tassel=0):
    hx, hy = g.ihead()
    cap = {p for p in R.ellipse(hx, hy - 4.5, 8.6, 5.4) if p[1] <= hy - 4}
    R.solid(cv, cap, "L", "l", shade_off=(1, 1))
    board = R.poly([(hx - 13, hy - 10), (hx, hy - 14), (hx + 13, hy - 10), (hx, hy - 6)])
    R.solid(cv, board, "L", "l", shade_off=(1, 1))
    tx = hx + 9 + tassel
    cv.fill(R.capsule((hx, hy - 10), (tx, hy - 8), 0.4) | R.capsule((tx, hy - 8), (tx, hy - 2), 0.5), "go1")


def laurel(cv, g, c=("V", "v")):
    hx, hy = g.ihead()
    for s in (-1, 1):
        for k in range(5):
            a = math.pi / 2 + s * (0.55 + k * 0.32)
            x, y = hx + math.cos(a) * 9.6, hy - 3 + -abs(math.sin(a)) * 6.0 - k * 0.3
            R.solid(cv, R.ellipse(x, y - 1, 1.6, 1.1), c[0], c[1], outline=c[1], shade_off=(1, 1))


def hard_hat(cv, g):
    hx, hy = g.ihead()
    dome = {p for p in R.ellipse(hx, hy - 4.5, 9.6, 7.4) if p[1] <= hy - 4}
    brim = R.rect(hx - 12, hy - 5, 25, 2)
    R.solid(cv, dome | brim, "hz1", "y", shade_off=(1, 1))
    cv.fill({(hx, y) for y in range(hy - 11, hy - 5)}, "y")
    cv.fill({(hx - 4, hy - 9), (hx - 3, hy - 10)}, "W")


def deerstalker(cv, g):
    hx, hy = g.ihead()
    m = {p for p in R.ellipse(hx, hy - 4.0, 9.8, 7.0) if p[1] <= hy - 3} | R.poly([(hx + 7, hy - 5), (hx + 14, hy - 4), (hx + 8, hy - 2)]) | \
        R.poly([(hx - 7, hy - 5), (hx - 14, hy - 4), (hx - 8, hy - 2)])
    R.solid(cv, m, "X", "x", shade_off=(1, 1))
    for (x, y) in R.inner(m):
        if (x // 2 + y // 2) % 2 == 0:
            cv.put(x, y, "x")
    R.solid(cv, R.rect(hx - 1, hy - 12, 3, 2), "x", None)


def accountant_visor(cv, g):
    hx, hy = g.ihead()
    band = R.rect(hx - 9, hy - 6, 19, 2)
    visor = R.poly([(hx - 9, hy - 5), (hx + 9, hy - 5), (hx + 13, hy - 2), (hx - 7, hy - 2)])
    R.solid(cv, band, "Z", "v", shade_off=(1, 1))
    R.solid(cv, visor, "glw", "Z", shade_off=(1, 1))


def kopiah(cv, g, c=("W", "smk")):
    """Kopiah haji putih polos (sama dengan v1 yang sudah disetujui)."""
    hx, hy = g.ihead()
    m = R.rect(hx - 9, hy - 11, 19, 6) - {(hx - 9, hy - 11), (hx + 9, hy - 11)}
    R.solid(cv, m, c[0], c[1], shade_off=(1, 1))


def peci_black(cv, g):
    hx, hy = g.ihead()
    m = R.rect(hx - 9, hy - 11, 19, 6) - {(hx - 9, hy - 11), (hx + 9, hy - 11)}
    R.solid(cv, m, "L", "l", shade_off=(1, 1))


def flat_cap(cv, g, c=("x", "e")):
    hx, hy = g.ihead()
    m = {p for p in R.ellipse(hx, hy - 4.5, 9.6, 5.6) if p[1] <= hy - 4} | R.poly([(hx + 2, hy - 6), (hx + 13, hy - 4), (hx + 3, hy - 3)])
    R.solid(cv, m, c[0], c[1], shade_off=(1, 1))


# ================================================================== base kelas domain
class DomainChar(Char):
    category = "domain"
    faction = None
    sleeve = "B"
    legwear = None  # (warna, sepatu) atau None = kaki bulu

    def legs(self, cv, g):
        if self.legwear:
            trousers(cv, g, self.legwear[0], self.legwear[1])
        else:
            Char.legs(self, cv, g)

    def arm(self, cv, g, i):
        R.arm(cv, g, i, sleeve=self.sleeve, r=1.9)

    def core_states(self, base, attack_state, victory_up, drops, hit_kw=None):
        victory_up = dict(victory_up)
        if "rh" in victory_up:
            victory_up["rh"] = (max(victory_up["rh"][0], 12), min(victory_up["rh"][1], -15))
        self.add("hit", 10, hit_fn(base, recoil=hit_kw), ms=100, loop=False, core="hit", label="tersentak mundur")
        self.add("victory", 16, victory_raise(base, victory_up, sparkle_hand=1), ms=110, core="victory",
                 label="prop diangkat, lompat kecil")
        self.add("defeat", 16, st_defeat_sit(base, drops), ms=120, loop=False, hold=10, core="defeat",
                 label="duduk lesu, prop terjatuh, menghela napas")
        if attack_state:
            self.states[attack_state].core = "attack"


# ------------------------------------------------------------------ PHILOSOPHER
class Philosopher(DomainChar):
    id = "philosopher"
    name = "Philosopher Gobyet"
    role = "philosophy"
    silhouette = ["toga_drape", "laurel", "scroll", "white_beard"]

    def legs(self, cv, g):
        Char.legs(self, cv, g)

    def torso(self, cv, g):
        if g.p.get("mode") == "sit":
            R.solid(cv, R.ellipse(g.tcx, g.tcy, g.tw + 0.6, g.th + 0.6), "cm1", "cm2", shade_off=(2, 2))
            return
        m = G.robe(cv, g, ("cm1", "cm2"), flare=3.0, length=-4)
        cv.fill(R.capsule((g.tcx - 7, g.tcy - 6), (g.tcx + 6, g.hip_y + 2), 1.4) & m, "cm2")
        cv.fill(R.capsule((g.tcx - 7, g.tcy - 6), (g.tcx + 6, g.hip_y + 2), 0.6) & m, "go1")

    def head(self, cv, g):
        R.head(cv, g)
        beard(cv, g)

    def headgear(self, cv, g):
        laurel(cv, g)

    def arm(self, cv, g, i):
        R.arm(cv, g, i, sleeve="B" if i == 1 else "cm1", r=1.9)

    def build(self):
        base = dict(sx=3, rh=(10, 3), rw="scroll_rolled", rwa=-70, lh=(-9, 4))
        self.add("idle", 12, idle_loop(base, 12, look=(4, 6)), ms=140, core="idle", label="gulungan di tangan, toga")
        self.add("thinking", 16, st_think(base, hand=(2, -4)), ms=120, label="mengelus janggut, ... lalu ?")
        self.add("reading", 12, st_read(base, "scroll_open"), ms=140, label="membaca gulungan terbuka")
        self.add("contemplating", 16, st_think(base, glyph="...", hand=(-2, -3), eyes="side"), ms=140,
                 label="merenung menatap jauh")

        def arguing(t):
            up = dict(base, rh=(12, -8), rw=None, lh=(-11, -2), lw="scroll_rolled", lwa=-60, eyes="look", brows="angry", lean=1)
            p = kf(t, [(0, dict(up)), (3, dict(up, rh=(14, -5))), (6, dict(up)), (9, dict(up, rh=(14, -5)))], 12)
            p["mouth"] = "shout" if t % 6 in (1, 2) else "o"
            p["tail"] = wag(t, 12)
            return p
        self.add("arguing", 12, arguing, ms=110, label="berargumen dengan tangan bergerak")
        self.add("pointing", 10, st_point(base, glyph="!"), ms=110, loop=False, label="menunjuk premis")
        self.core_states(base, "arguing", dict(base, rw="scroll_open", rh=(6, -14), lh=(-9, -6), mouth="smile"),
                         [("scroll_rolled", RX + 10, BASE - 2, 0)])


# ------------------------------------------------------------------ ACADEMIC
class Academic(DomainChar):
    id = "academic"
    name = "Academic Gobyet"
    role = "academia"
    silhouette = ["mortarboard", "long_gown", "book"]
    sleeve = "L"

    def legs(self, cv, g):
        trousers(cv, g, ("L", "l"), ("L", "K"))

    def torso(self, cv, g):
        if g.p.get("mode") == "sit":
            R.solid(cv, R.ellipse(g.tcx, g.tcy, g.tw + 0.6, g.th + 0.6), "L", "l", shade_off=(2, 2))
            return
        m = G.robe(cv, g, ("L", "l"), flare=4.0, length=-3)
        cv.fill(R.capsule((g.tcx - 4, g.tcy - 6), (g.tcx - 3, g.hip_y + 1), 1.2) & m, "cr1")
        cv.fill(R.capsule((g.tcx + 4, g.tcy - 6), (g.tcx + 3, g.hip_y + 1), 1.2) & m, "cr1")
        cv.fill({(x, y) for (x, y) in R.ellipse(g.tcx, g.tcy - 5, 3, 2)}, "W")

    def headgear(self, cv, g):
        mortarboard(cv, g, tassel=int(round(math.sin(g.p.get("tail", 0)))))

    def build(self):
        base = dict(sx=3, rh=(9, 2), rw="book_closed", lh=(-9, 4))
        self.add("idle", 12, idle_loop(base, 12, look=(4, 6)), ms=140, core="idle", label="toga hitam, buku tebal")
        self.add("read", 12, st_read(base, "book_open"), ms=140, label="membaca buku terbuka")
        self.add("write", 12, st_write(base, "notebook", "pen"), ms=110, label="mencatat")

        def lecture(t):
            p = st_present(base, board="formula", hand=(14, -7))(t)
            p["rw"] = None
            return p
        self.add("lecture", 12, lecture, ms=120, label="mengajar di depan papan")
        self.add("think", 16, st_think(base), ms=120, label="berpikir")

        def present(t):
            pose = dict(base, rh=(10, -6), rw="diploma", rwa=0, lh=(-9, 4), eyes="look", mouth="smile")
            p = kf(t, [(0, dict(base)), (3, pose), (9, pose), (11, dict(base))], 12)
            p["tail"] = wag(t, 12)
            return p
        self.add("present", 12, present, ms=120, label="memamerkan ijazah")
        self.core_states(base, "lecture", dict(base, rh=(6, -14), rw="book_closed", lh=(-9, -8), mouth="smile"),
                         [("book_closed", RX + 12, BASE + 2, 0)])


# ------------------------------------------------------------------ SCIENTIST
class Scientist(DomainChar):
    id = "scientist"
    name = "Scientist Gobyet"
    role = "science"
    silhouette = ["long_lab_coat", "goggles_on_forehead", "flask", "clipboard"]
    sleeve = "W"

    def legs(self, cv, g):
        trousers(cv, g, ("nv1", "nv2"), ("L", "K"))

    def torso(self, cv, g):
        if g.p.get("mode") == "sit":
            R.solid(cv, R.ellipse(g.tcx, g.tcy, g.tw + 0.6, g.th + 0.6), "W", "smk", shade_off=(2, 2))
            return
        G.long_coat(cv, g, ("W", "smk"), trim=None, flare=3.0, length=-2, lapel="tl1")
        cx = int(round(g.tcx))
        cv.fill({(cx + 4, int(g.tcy) - 2), (cx + 5, int(g.tcy) - 2)}, "3")

    def headgear(self, cv, g):
        hx, hy = g.ihead()
        cv.fill({(x, hy - 7) for x in range(hx - 10, hx + 11)}, "L")
        for s in (-1, 1):
            ring = R.ellipse(hx + s * 4, hy - 7.5, 3.2, 2.6)
            R.solid(cv, ring, "I", None, outline="l")
            cv.put(hx + s * 4 - 1, hy - 8, "W")

    def build(self):
        base = dict(sx=3, rh=(10, 1), rw="flask", lh=(-9, 3), lw="clipboard")
        self.add("idle", 12, idle_loop(base, 12, look=(4, 6), extra=lambda t, p: p.update(bubble=t)), ms=130, core="idle",
                 label="jas lab panjang, labu bergelembung, papan klip")

        def observe(t):
            pose = dict(base, rh=(6, -9), eyes="side", brows="raised", mouth="flat")
            p = kf(t, [(0, dict(pose)), (6, dict(pose, rh=(7, -10)))], 12)
            p.update(tail=wag(t, 12), bubble=t)
            return p
        self.add("observe", 12, observe, ms=120, label="mengamati labu di depan mata")

        def experiment(t):
            pose = dict(base, rh=(9, -4), lh=(1, -6), lw="flask", lwa=0, eyes="down", mouth="o")
            p = kf(t, [(0, dict(pose)), (4, dict(pose, lh=(3, -9))), (8, dict(pose))], 12)
            p.update(tail=wag(t, 12), bubble=t * 2, liquid="glw" if t >= 6 else "Z")
            if 6 <= t <= 9:
                p["fx"] = [fx_puff(RX + 14, 22 - (t - 6) * 2, 1.5 + (t - 6) * 0.5)]
            return p
        self.add("experiment", 12, experiment, ms=110, label="menuang dari labu ke labu, kepulan kecil")
        self.add("write", 12, st_write(dict(base, rw=None), "clipboard", "pen"), ms=110, label="mencatat hasil")
        self.add("compare", 12, st_compare(base, "flask", "flask"), ms=130, label="membandingkan dua sampel")
        self.add("shocked", 10, st_shocked(base), ms=100, loop=False, label="terkejut hasil eksperimen")
        self.add("success", 12, st_eureka(dict(base, rw=None)), ms=110, loop=False, label="berhasil: lampu ide menyala")
        self.core_states(base, "experiment", dict(base, rh=(6, -14), lh=(-9, -8), mouth="smile"),
                         [("flask", RX + 12, BASE, 0), ("clipboard", RX - 14, BASE + 1, 0)])


# ------------------------------------------------------------------ MATHEMATICIAN
class Mathematician(DomainChar):
    id = "mathematician"
    name = "Mathematician Gobyet"
    role = "math"
    silhouette = ["chalkboard_with_formula", "compass", "purple_vest"]

    def legs(self, cv, g):
        trousers(cv, g, ("l", "L"), ("L", "K"))

    def torso(self, cv, g):
        shirt(cv, g, ("W", "smk"), collar=True, buttons=False)
        m = R.ellipse(g.tcx, g.tcy, g.tw + 0.4, g.th + 0.4)
        for s in (-1, 1):
            v = {(x, y) for (x, y) in m if s * (x - g.tcx) > 1.5}
            R.solid(cv, v, "p", "j", shade_off=(1, 1))

    def arm(self, cv, g, i):
        R.arm(cv, g, i, sleeve="W", r=1.9)

    def head(self, cv, g):
        R.head(cv, g)
        glasses(cv, g)

    def build(self):
        base = dict(sx=3, rh=(10, 2), rw="chalk", lh=(-9, 4))

        def with_board(kind="formula"):
            return lambda t, p: p.update(fx_back=[fx_board(kind, t)])

        self.add("idle", 12, idle_loop(base, 12, look=(4, 6), extra=with_board()), ms=140, core="idle",
                 label="papan tulis berkaki dengan rumus di samping")

        def calculate(t):
            p = st_think(base, glyph="?", hand=(3, -6))(t)
            p["fx_back"] = [fx_board("formula", t)]
            if 4 <= t <= 11:
                p["fx"] = [lambda cv, g, t=t: P.text3(cv, ("1+1", "2x3", "p=3")[(t // 3) % 3], g.ihead()[0] + 6, g.ihead()[1] - 16, "K")]
            return p
        self.add("calculate", 16, calculate, ms=110, label="menghitung di kepala")

        def write(t):
            pose = dict(base, rh=(13, -9 + (t % 3)), rw="chalk", eyes="side", mouth="flat", lean=1)
            p = dict(pose)
            p["tail"] = wag(t, 12)
            p["fx_back"] = [fx_board("formula", t)]
            return p
        self.add("write", 12, write, ms=110, label="menulis rumus dengan kapur")

        def erase(t):
            pose = dict(base, rh=(14 + (2 if t % 4 < 2 else -2), -8), rw=None, eyes="side", mouth="flat")
            p = dict(pose)
            p["tail"] = wag(t, 12)
            p["fx_back"] = [fx_board("formula" if t < 6 else "blank", t)]
            if t >= 4:
                p["fx"] = [fx_puff(RX + 24 + (t % 3), 26, 1.4)]
            return p
        self.add("erase", 12, erase, ms=110, label="menghapus papan, debu kapur")
        self.add("think", 16, st_think(base, extra=with_board()), ms=120, label="berpikir di depan rumus")
        self.add("eureka", 12, st_eureka(base, extra=None), ms=110, loop=False, label="eureka: lampu menyala")
        self.add("confused", 12, st_confused(base), ms=120, label="bingung, garuk kepala")
        self.core_states(base, "write", dict(base, rh=(6, -14), rw="chalk", lh=(-9, -8), mouth="smile"),
                         [("chalk", RX + 10, BASE - 1, 0)])
        self.states["victory"].fn = _with_back(self.states["victory"].fn, fx_board("formula", 0))


def _with_back(fn, fx):
    def f(t):
        p = fn(t)
        p["fx_back"] = p.get("fx_back", []) + [fx]
        return p
    return f


# ------------------------------------------------------------------ LAWYER
class Lawyer(DomainChar):
    id = "lawyer"
    name = "Lawyer Gobyet"
    role = "law"
    silhouette = ["dark_suit_red_tie", "thick_law_book", "briefcase", "documents"]
    sleeve = "J"

    def legs(self, cv, g):
        trousers(cv, g, ("J", "w"), ("L", "K"))

    def torso(self, cv, g):
        m = R.ellipse(g.tcx, g.tcy, g.tw + 0.8, g.th + 0.5)
        R.solid(cv, m, "J", "w", shade_off=(2, 2))
        cx, top = int(round(g.tcx)), int(round(g.tcy - g.th))
        shirtv = R.poly([(cx - 3, top + 1), (cx + 3, top + 1), (cx, top + 8)])
        cv.fill(shirtv & m, "W")
        cv.fill(R.rect(cx, top + 2, 1, 2) | R.rect(cx - 1, top + 4, 2, 4), "cr1")
        cv.fill({(cx + 4, top + 4), (cx + 5, top + 4)}, "W")

    def build(self):
        base = dict(sx=3, rh=(9, 2), rw="book_closed", sym="law", cover=("le1", "le2"), lh=(-10, 3), lw="briefcase")
        self.add("idle", 12, idle_loop(base, 12, look=(4, 6)), ms=140, core="idle", label="jas gelap, kitab hukum, berkas")
        self.add("read", 12, st_read(dict(base, lw=None), "papers"), ms=140, label="membaca berkas")

        def present(t):
            pose = dict(base, rh=(13, -4), rw="papers", lh=(-9, 4), eyes="look", mouth=talk(t))
            p = dict(pose)
            p["tail"] = wag(t, 12)
            return p
        self.add("present", 12, present, ms=120, label="menyerahkan bukti")

        def objection(t):
            pose = dict(base, rh=(16, -7), rw=None, lean=3, eyes="angry", brows="angry", mouth="shout")
            p = kf(t, [(0, dict(base)), (2, pose), (8, pose), (9, dict(base))], 10, loop=False)
            p["tail"] = wag(t, 10)
            if 2 <= t <= 8:
                p["fx"] = [fx_mark("!", dx=-22, dy=-18, fill="Y"), fx_speed(RX + 50, 28, 3, 5, 1)]
            return p
        self.add("object", 10, objection, ms=100, loop=False, label="keberatan! menunjuk keras")
        self.add("point", 10, st_point(base), ms=110, loop=False, label="menunjuk saksi")

        def judge(t):
            up = dict(base, rh=(8, -10), rw="gavel", rwa=-150, lw=None, mouth="flat", brows="angry")
            dn = dict(base, rh=(12, 2), rw="gavel", rwa=-20, lw=None, mouth="shout")
            p = kf(t, [(0, up), (3, dn), (5, dn), (8, up)], 10)
            p["tail"] = wag(t, 10)
            if t in (3, 4):
                p["fx"] = [fx_impact(RX + 26, 40, t - 3, "W")]
            return p
        self.add("judge", 10, judge, ms=100, label="mengetuk palu")
        self.core_states(base, "object", dict(base, rh=(6, -14), lh=(-9, -8), mouth="smile"),
                         [("papers", RX + 12, BASE + 1, 0), ("book_closed", RX - 14, BASE + 1, 0, {"sym": "law", "cover": ("le1", "le2")})])


# ------------------------------------------------------------------ HISTORIAN
class Historian(DomainChar):
    id = "historian"
    name = "Historian Gobyet"
    role = "history"
    silhouette = ["flat_cap", "tweed_jacket", "long_timeline_scroll", "archive_box"]
    sleeve = "X"

    def legs(self, cv, g):
        trousers(cv, g, ("e", "x"), ("le2", "K"))

    def torso(self, cv, g):
        m = R.ellipse(g.tcx, g.tcy, g.tw + 0.7, g.th + 0.5)
        R.solid(cv, m, "X", "x", shade_off=(2, 2))
        for (x, y) in R.inner(m):
            if (x + 2 * y) % 5 == 0:
                cv.put(x, y, "x")
        cx, top = int(round(g.tcx)), int(round(g.tcy - g.th))
        cv.fill(R.rect(cx - 1, top + 1, 3, 2), "cr1")
        cv.fill({(cx - 2, top + 1), (cx + 2, top + 1)}, "cr2")

    def head(self, cv, g):
        R.head(cv, g)
        glasses(cv, g, round_=True)

    def headgear(self, cv, g):
        flat_cap(cv, g)

    def build(self):
        base = dict(sx=3, rh=(10, 2), rw="scroll_rolled", rwa=-70, lh=(-9, 4))

        def box(t, p):
            p["fx_back"] = p.get("fx_back", []) + [lambda cv, g: P.archive_box(cv, RX + 18, BASE - 10)]
        self.add("idle", 12, idle_loop(base, 12, look=(4, 6), extra=box), ms=140, core="idle",
                 label="jaket wol, kacamata bundar, kotak arsip")
        self.add("read_archive", 12, st_read(base, "papers", extra=box), ms=140, label="membaca naskah tua")

        def compare(t):
            p = st_compare(base, "papers", "scroll_rolled")(t)
            return p
        self.add("compare", 12, compare, ms=130, label="membandingkan dua sumber")
        self.add("search", 12, st_search(base), ms=120, label="mencari dengan kaca pembesar")
        self.add("write", 12, st_write(base, "notebook", "quill"), ms=110, label="menulis dengan pena bulu")

        def discover(t):
            pose = dict(base, rh=(3, -1), rw="timeline", lh=(-9, -1), eyes="wide", brows="up", mouth="o")
            p = kf(t, [(0, dict(base)), (3, pose), (10, dict(pose, eyes="happy", mouth="smile")), (11, dict(base))], 12)
            p["tail"] = wag(t, 12)
            if 4 <= t <= 10:
                p["fx"] = [fx_mark("!", dx=-20, dy=-16)]
            return p
        self.add("discover", 12, discover, ms=120, label="membentangkan lini masa: menemukan!")
        self.core_states(base, "discover", dict(base, rh=(3, -14), rw="timeline", lh=(-9, -8), mouth="smile"),
                         [("scroll_rolled", RX + 10, BASE - 2, 0)])


# ------------------------------------------------------------------ ECONOMIST
class Economist(DomainChar):
    id = "economist"
    name = "Economist Gobyet"
    role = "economics"
    silhouette = ["green_visor", "vest_tie", "chart_board", "calculator"]
    sleeve = "W"

    def legs(self, cv, g):
        trousers(cv, g, ("l", "L"), ("L", "K"))

    def torso(self, cv, g):
        shirt(cv, g, ("W", "smk"), tie="nv1")
        m = R.ellipse(g.tcx, g.tcy, g.tw + 0.4, g.th + 0.4)
        for s in (-1, 1):
            v = {(x, y) for (x, y) in m if s * (x - g.tcx) > 1.5 and y > g.tcy - 4}
            R.solid(cv, v, "h", "g", shade_off=(1, 1))

    def headgear(self, cv, g):
        accountant_visor(cv, g)

    def build(self):
        base = dict(sx=3, rh=(10, 2), rw="calculator", lh=(-9, 4), lw="ledger")

        def chart(kind="chart_up"):
            return lambda t, p: p.update(fx_back=[fx_board(kind, t % 4 if t < 4 else 0)])
        self.add("idle", 12, idle_loop(base, 12, look=(4, 6), extra=chart()), ms=140, core="idle",
                 label="pelindung mata hijau, kalkulator, buku besar, grafik")

        def calc(t):
            pose = dict(base, rh=(4, -2), lh=(-4, 0), lw=None, eyes="down", mouth="flat", key=t % 9)
            p = dict(pose)
            p["tail"] = wag(t, 12)
            p["fx_back"] = [fx_board("chart_up", 0)]
            return p
        self.add("calculate", 12, calc, ms=100, label="menekan tombol kalkulator")

        def graph(t):
            p = st_present(dict(base, rw=None), board="chart_up", hand=(14, -7))(t)
            p["fx_back"] = [fx_board("chart_up", min(t // 2, 3) + 1)]
            return p
        self.add("graph", 12, graph, ms=120, label="menunjuk grafik yang naik")
        self.add("check", 12, st_read(base, "ledger", extra=chart()), ms=130, label="memeriksa buku besar")

        def shocked(t):
            p = st_shocked(base)(t)
            p["fx_back"] = [fx_board("chart_down", 0)]
            return p
        self.add("shocked", 10, shocked, ms=100, loop=False, label="grafik anjlok, terkejut")
        self.add("analyze", 16, st_think(base, glyph="%", extra=chart()), ms=120, label="menganalisis")
        self.core_states(base, "graph", dict(base, rh=(6, -14), lh=(-9, -8), mouth="smile"),
                         [("calculator", RX + 12, BASE + 1, 0), ("ledger", RX - 14, BASE + 1, 0)])


# ------------------------------------------------------------------ PSYCHOLOGIST
class Psychologist(DomainChar):
    id = "psychologist"
    name = "Psychologist Gobyet"
    role = "psychology"
    silhouette = ["wingback_armchair_seated", "cardigan", "big_glasses", "notebook", "inkblot_card"]
    sleeve = "tl1"
    SEAT_DY = -7

    def back(self, cv, g):
        P.armchair(cv, R.RX, int(R.BASE - 2 + self.SEAT_DY + 1))

    def legs(self, cv, g):
        trousers(cv, g, ("e", "x"), ("le2", "K"))

    def torso(self, cv, g):
        m = R.ellipse(g.tcx, g.tcy, g.tw + 0.6, g.th + 0.6)
        R.solid(cv, m, "tl1", "tl2", shade_off=(2, 2))
        cx, top = int(round(g.tcx)), int(round(g.tcy - g.th))
        cv.fill(R.poly([(cx - 2, top + 1), (cx + 2, top + 1), (cx, top + 7)]) & m, "cm1")
        for k in range(3):
            cv.put(cx + 1, top + 8 + k * 2, "go1")

    def head(self, cv, g):
        R.head(cv, g)
        glasses(cv, g, c="le2")

    def build(self):
        base = dict(sx=3, rh=(10, 2), rw="pen", rwa=-60, lh=(-8, 2), lw="notebook", mode="sit", dy=self.SEAT_DY)
        self.add("idle", 12, idle_loop(base, 12, look=(4, 6)), ms=140, core="idle",
                 label="duduk di kursi berlengan, kardigan, kacamata besar, buku catatan")

        def observe(t):
            pose = dict(base, eyes="side", brows="raised", mouth="flat", lean=1)
            p = kf(t, [(0, pose), (6, dict(pose, lean=2, crouch=1))], 12)
            p["tail"] = wag(t, 12)
            if t in (5, 6):
                p["eyes"] = "blink"
            return p
        self.add("observe", 12, observe, ms=130, label="mengamati dengan alis terangkat")
        self.add("write", 12, st_write(dict(base, rw=None), "notebook", "pen"), ms=110, label="mencatat")
        self.add("think", 16, st_think(base), ms=120, label="berpikir")

        def analyze(t):
            pose = dict(base, rh=(11, -4), rw="inkblot", lw="notebook", eyes="side", mouth="flat")
            p = dict(pose)
            p["mouth"] = talk(t) if t > 5 else "flat"
            p["tail"] = wag(t, 12)
            if 6 <= t <= 11:
                p["fx"] = [fx_mark("?", dx=-22, dy=-16)]
            return p
        self.add("analyze", 12, analyze, ms=120, label="menunjukkan kartu bercak tinta: apa yang kamu lihat?")

        def suspicious(t):
            pose = dict(base, eyes="side", brows="raised", mouth="smirk", lean=2, hdx=1)
            p = dict(pose)
            p["tail"] = wag(t, 12)
            if t % 6 in (3, 4):
                p["eyes"] = "angry"
            return p
        self.add("suspicious", 12, suspicious, ms=130, label="curiga, mata menyipit")
        self.core_states(base, "analyze", dict(base, rh=(6, -14), lh=(-9, -8), mouth="smile"),
                         [("notebook", RX + 12, BASE + 1, 0)])

        def slump(t):
            pose = dict(base, rw=None, lw=None, rh=(9, 4), lh=(-9, 4), eyes="relief", brows="worried", mouth="frown", hdy=1)
            p = kf(t, [(0, dict(base)), (2, dict(base, eyes="wide", brows="up", mouth="o")), (5, pose), (15, pose)], 16, loop=False,
                   smooth=False)
            p["tail"] = 0.0
            fx = [fx_item("notebook", RX + 12, BASE + 1, 0)] if t >= 4 else []
            if t >= 8:
                k = (t - 8) % 6
                fx.append(fx_puff(RX + 12 + k, BASE - 33 - k * 2, 1.3 + k * 0.25))
            p["fx"] = fx
            return p
        self.add("defeat", 16, slump, ms=120, loop=False, hold=10, core="defeat", label="lesu di kursi, buku catatan jatuh")


# ------------------------------------------------------------------ SOCIOLOGIST
class Sociologist(DomainChar):
    id = "sociologist"
    name = "Sociologist Gobyet"
    role = "sociology"
    silhouette = ["field_jacket_scarf", "network_diagram_board", "clipboard"]
    sleeve = "ol1"

    def legs(self, cv, g):
        trousers(cv, g, ("nv1", "nv2"), ("le1", "le2"))

    def torso(self, cv, g):
        m = R.ellipse(g.tcx, g.tcy, g.tw + 0.6, g.th + 0.6)
        R.solid(cv, m, "ol1", "ol2", shade_off=(2, 2))
        for s in (-1, 1):
            cv.fill(R.rect(int(g.tcx) + s * 4 - 1, int(g.tcy) + 1, 3, 3), "ol2")
        scarf = R.ellipse(g.tcx, g.tcy - g.th + 1, 6.5, 2.2) | R.capsule((g.tcx + 3, g.tcy - 4), (g.tcx + 4, g.tcy + 3), 1.2)
        R.solid(cv, scarf, "o", "t", shade_off=(1, 1))

    def build(self):
        base = dict(sx=3, rh=(10, 2), rw="pen", rwa=-60, lh=(-8, 2), lw="clipboard")

        def net(t, p):
            p["fx_back"] = [fx_board("network", t)]
        self.add("idle", 12, idle_loop(base, 12, look=(4, 6), extra=net), ms=140, core="idle",
                 label="papan diagram jaringan, papan klip, syal")

        def crowd(t):
            pose = dict(base, eyes="side", brows="raised", mouth="flat", rh=(9, -7), rw=None)
            p = dict(pose)
            p["eyes"] = "side" if (t // 4) % 2 == 0 else "left"
            p["tail"] = wag(t, 12)
            p["fx_back"] = [fx_board("crowd", t)]
            return p
        self.add("observe_crowd", 12, crowd, ms=130, label="mengamati kerumunan")

        def draw_net(t):
            pose = dict(base, rh=(13, -9 + (t % 3)), rw="pen", rwa=-120, eyes="side", lean=1, mouth="flat")
            p = dict(pose)
            p["tail"] = wag(t, 12)
            p["fx_back"] = [fx_board("network", t)]
            return p
        self.add("draw_network", 12, draw_net, ms=110, label="menggambar jaringan")
        self.add("compare", 12, st_compare(base, "clipboard", "papers"), ms=130, label="membandingkan data")

        def analyze(t):
            p = st_present(dict(base, rw=None), board="network")(t)
            return p
        self.add("analyze", 12, analyze, ms=120, label="menjelaskan jaringan sosial")
        self.core_states(base, "analyze", dict(base, rh=(6, -14), lh=(-9, -8), mouth="smile"),
                         [("clipboard", RX + 12, BASE + 1, 0)])


# ------------------------------------------------------------------ ENGINEER
class Engineer(DomainChar):
    id = "engineer"
    name = "Engineer Gobyet"
    role = "engineering"
    silhouette = ["hard_hat", "hi_vis_vest", "wrench", "blueprint"]
    sleeve = "nv1"

    def legs(self, cv, g):
        trousers(cv, g, ("nv1", "nv2"), ("le2", "K"))

    def torso(self, cv, g):
        m = R.ellipse(g.tcx, g.tcy, g.tw + 0.6, g.th + 0.6)
        R.solid(cv, m, "nv1", "nv2", shade_off=(2, 2))
        vest = {(x, y) for (x, y) in m if abs(x - g.tcx) > 1.5}
        R.solid(cv, vest, "o", "t", shade_off=(1, 1))
        cv.fill({(x, int(g.tcy) + 1) for (x, y) in vest if y == int(g.tcy) + 1} | {(x, int(g.tcy) + 2) for (x, y) in vest
                                                                                    if y == int(g.tcy) + 2}, "hz1")

    def headgear(self, cv, g):
        hard_hat(cv, g)

    def build(self):
        base = dict(sx=4, rh=(11, 2), rw="wrench", rwa=-70, lh=(-9, 3), lw="blueprint_roll")
        self.add("idle", 12, idle_loop(base, 12, look=(4, 6)), ms=130, core="idle", label="helm proyek, rompi oranye, kunci pas")

        def measure(t):
            pose = dict(base, rw=None, rh=(5, 2), lh=(-10, 2), lw="tape_measure", eyes="down", mouth="flat", crouch=1)
            p = dict(pose, tape=[0, 4, 8, 12, 16, 20, 22, 20, 16, 12, 8, 4][t % 12])
            p["lh"] = (-10, 2)
            p["tail"] = wag(t, 12)
            return p
        self.add("measure", 12, measure, ms=110, label="menarik meteran")

        def design(t):
            pose = dict(base, rh=(13, -9 + (t % 3)), rw="pen", rwa=-120, lw=None, eyes="side", lean=1, mouth="flat")
            p = dict(pose)
            p["tail"] = wag(t, 12)
            p["fx_back"] = [fx_board("blueprint", t)]
            return p
        self.add("design", 12, design, ms=110, label="menggambar cetak biru")

        def build(t):
            up = dict(base, rh=(10, -9), rwa=-140, lw=None, lh=(-6, 6), eyes="angry", mouth="flat")
            dn = dict(base, rh=(12, 4), rwa=10, lw=None, lh=(-6, 6), mouth="shout")
            p = kf(t, [(0, up), (2, dn), (4, up)], 6)
            p["tail"] = wag(t, 6)
            p["fx_back"] = [lambda cv, g: R.solid(cv, R.rect(RX + 16, BASE - 6, 14, 5), "wo1", "wo2", shade_off=(1, 1))]
            if t in (2, 3):
                p["fx"] = [fx_impact(RX + 26, BASE - 8, t - 2, "W")]
            return p
        self.add("build", 6, build, ms=100, label="membangun: mengetuk balok")
        self.add("inspect", 12, st_search(base, "magnifier"), ms=120, label="memeriksa sambungan")

        def fix(t):
            pose = dict(base, rh=(13, 4), rwa=-30 + (40 if t % 4 < 2 else 0), lw=None, lh=(-6, 6), eyes="down", mouth="flat",
                        crouch=2)
            p = dict(pose)
            p["tail"] = wag(t, 8)
            p["fx_back"] = [lambda cv, g: (R.solid(cv, R.rect(RX + 18, BASE - 12, 4, 11), "st2", "st3", shade_off=(1, 1)),
                                           R.solid(cv, R.rect(RX + 16, BASE - 13, 8, 3), "st1", None))]
            if t % 4 == 2:
                p["fx"] = [lambda cv, g: R.star(cv, RX + 24, BASE - 15, "Y")]
            return p
        self.add("fix", 8, fix, ms=100, label="memutar baut dengan kunci pas")
        self.core_states(base, "build", dict(base, rh=(6, -14), lh=(-9, -8), mouth="smile"),
                         [("wrench", RX + 12, BASE - 2, 0)])


# ------------------------------------------------------------------ DETECTIVE
class Detective(DomainChar):
    id = "detective"
    name = "Detective Gobyet"
    role = "investigation"
    silhouette = ["deerstalker", "trench_coat_cape", "big_magnifier", "notebook"]
    sleeve = "d"

    def legs(self, cv, g):
        trousers(cv, g, ("e", "x"), ("L", "K"))

    def torso(self, cv, g):
        if g.p.get("mode") == "sit":
            R.solid(cv, R.ellipse(g.tcx, g.tcy, g.tw + 0.6, g.th + 0.6), "d", "e", shade_off=(2, 2))
            return
        G.long_coat(cv, g, ("d", "e"), trim=None, flare=4.0, length=-1, lapel="cm1")
        cape = R.ellipse(g.tcx, g.tcy - 3, g.tw + 3.2, 4.0)
        R.solid(cv, {(x, y) for (x, y) in cape if y >= g.tcy - 5}, "d", "e", shade_off=(1, 1))
        for (x, y) in R.inner(cape):
            if (x // 2 + y // 2) % 2 == 0 and y >= g.tcy - 5:
                cv.put(x, y, "e")

    def headgear(self, cv, g):
        deerstalker(cv, g)

    def build(self):
        base = dict(sx=3, rh=(10, 1), rw="magnifier", rwa=-60, lh=(-9, 3), lw="notebook", nb="cr1")
        self.add("idle", 12, idle_loop(base, 12, look=(4, 6)), ms=140, core="idle", label="topi deerstalker, mantel berjubah, kaca pembesar")
        self.add("search", 12, st_search(base), ms=120, label="menyisir lantai dengan kaca pembesar")

        def inspect(t):
            pose = dict(base, rh=(8, -6), rwa=-10, eyes="side", brows="raised", mouth="flat", lean=1)
            p = kf(t, [(0, pose), (6, dict(pose, rh=(10, -5)))], 12)
            p["tail"] = wag(t, 12)
            p["fx_back"] = [fx_board("evidence", t)]
            return p
        self.add("inspect", 12, inspect, ms=120, label="memeriksa papan bukti")

        def magnify(t):
            pose = dict(base, rh=(-2, -2), rwa=-10, eyes="wide", brows="raised", mouth="o")
            p = kf(t, [(0, dict(base)), (3, pose), (9, pose), (11, dict(base))], 12)
            p["tail"] = wag(t, 12)
            return p
        self.add("magnify", 12, magnify, ms=120, label="lensa di depan mata, mata membesar")

        def discover(t):
            p = st_eureka(dict(base, rw="magnifier"))(t)
            if 3 <= t <= 10:
                p["fx"] = [fx_mark("!", dx=8, dy=-16)]
            return p
        self.add("discover", 12, discover, ms=110, loop=False, label="menemukan petunjuk!")

        def suspicious(t):
            pose = dict(base, eyes="angry", brows="raised", mouth="smirk", lean=2, rh=(8, -4), rwa=-20)
            p = dict(pose)
            p["tail"] = wag(t, 12)
            p["eyes"] = "angry" if t % 6 < 4 else "side"
            return p
        self.add("suspicious", 12, suspicious, ms=130, label="curiga, menyipit")
        self.add("point", 10, st_point(base, glyph="!"), ms=110, loop=False, label="menunjuk pelaku")
        self.core_states(base, "point", dict(base, rh=(6, -14), lh=(-9, -8), mouth="smile"),
                         [("magnifier", RX + 10, BASE - 3, 0)])


# ------------------------------------------------------------------ RESEARCHER
class Researcher(DomainChar):
    id = "researcher"
    name = "Researcher Gobyet"
    role = "evidence"
    silhouette = ["book_stack", "laptop", "papers", "glasses", "sweater"]
    sleeve = "h"

    def legs(self, cv, g):
        trousers(cv, g, ("nv1", "nv2"), ("le1", "le2"))

    def torso(self, cv, g):
        m = R.ellipse(g.tcx, g.tcy, g.tw + 0.6, g.th + 0.6)
        R.solid(cv, m, "h", "g", shade_off=(2, 2))
        cx, top = int(round(g.tcx)), int(round(g.tcy - g.th))
        cv.fill({(cx - 1, top + 1), (cx, top + 1), (cx + 1, top + 1), (cx, top + 2)}, "W")
        cv.fill({(x, top + 5) for x in range(cx - 5, cx + 6)} & m, "3")

    def head(self, cv, g):
        R.head(cv, g)
        glasses(cv, g, round_=False)

    def build(self):
        base = dict(sx=3, rh=(12, 6), rw="book_stack", books=7, lh=(-9, 4))
        self.add("idle", 12, idle_loop(base, 12, look=(4, 6)), ms=140, core="idle", label="memeluk tumpukan buku")
        self.add("search", 12, st_search(dict(base, lw=None), "magnifier"), ms=120, label="mencari di tumpukan sumber")
        self.add("read", 12, st_read(base, "book_open", cover=("3", "4")), ms=140, label="membaca")
        self.add("compare", 12, st_compare(base, "papers", "book_open"), ms=130, label="membandingkan sumber")

        def write(t):
            pose = dict(base, rw="laptop_side", rh=(2, 6), lh=(-2, 6), eyes="down", mouth="flat", glow="Z")
            p = dict(pose)
            p["tail"] = wag(t, 12)
            p["lh"] = (-2, 6 - (t % 2))
            p["rh"] = (2, 6 - ((t + 1) % 2))
            p["fx"] = [lambda cv, g, t=t: P.terminal_window(cv, RX + 16, 10, t)]
            return p
        self.add("write", 12, write, ms=100, label="mengetik catatan di laptop")

        def archive(t):
            pose = dict(base, rw="papers", rh=(13, 2 + (t % 6) // 2), lh=(-8, 3), eyes="down")
            p = dict(pose)
            p["tail"] = wag(t, 12)
            p["fx_back"] = [lambda cv, g, t=t: P.archive_box(cv, RX + 15, BASE - 10, open_=t % 6 >= 3)]
            return p
        self.add("archive", 12, archive, ms=110, label="menyimpan bukti ke kotak arsip")
        self.core_states(base, "compare", dict(base, rh=(6, -14), rw="book_open", lh=(-9, -8), mouth="smile"),
                         [("book_stack", RX + 12, BASE + 4, 0)])


# ------------------------------------------------------------------ PAK HAJI dan PRIEST (aturan 7.2: paralel)
class _Theology(DomainChar):
    role = "theology"

    def front(self, cv, g):
        P.aura(cv, g, g.p.get("aura_k", 0))

    def theology_states(self, base, book, item_extra):
        """State paralel untuk kedua tokoh: idle, read, think, present, calm, + satu khas, + inti arena."""
        def calm_extra(t, p):
            p["aura_k"] = t // 4
        self.add("idle", 12, idle_loop(base, 12, extra=calm_extra), ms=150, core="idle", label="tenang, aura halus")
        self.add("read", 12, st_read(base, book, extra=calm_extra, cover=self.book_cover), ms=150, label="membaca kitab")
        self.add("think", 16, st_think(base, glyph="...", extra=calm_extra), ms=130, label="merenung")

        def present(t):
            pose = dict(base, rh=(12, -4), rw=book, rwa=0, cover=self.book_cover, eyes="look", mouth=talk(t) if t % 8 < 6 else "smile")
            p = dict(pose)
            p["tail"] = wag(t, 12)
            p["aura_k"] = t // 4
            return p
        self.add("present", 12, present, ms=130, core="attack", label="menyampaikan pandangan dengan kitab terbuka")

        def calm(t):
            pose = dict(base, eyes="relief", brows="flat", mouth="smile")
            p = kf(t, [(0, pose), (8, dict(pose, crouch=1))], 16)
            p["tail"] = wag(t, 16)
            p["aura_k"] = t // 4
            if t in (6, 7):
                p["eyes"] = "blink"
            return p
        self.add("calm", 16, calm, ms=150, label="menenangkan diri, napas panjang")
        self.add("hit", 10, hit_fn(base), ms=110, loop=False, core="hit", label="tersentak")
        up = dict(base, rh=(8, -12), lh=(-8, -12), rw=None, mouth="smile", eyes="happy")
        self.add("victory", 16, victory_raise(base, up, sparkle_hand=None, hop=False), ms=130, core="victory",
                 label="kedua tangan terangkat bersyukur, tanpa lompat")
        self.add("defeat", 16, st_defeat_sit(base, [(book, RX + 12, BASE + 1, 0, {"cover": self.book_cover})]), ms=130,
                 loop=False, hold=10, core="defeat", label="duduk tenang, kitab diletakkan")


class PakHaji(_Theology):
    id = "pak-haji"
    name = "Pak Haji Gobyet"
    silhouette = ["kopiah_putih", "baju_koko", "sarung", "tasbih"]
    sleeve = "S"
    book_cover = ("V", "v")

    def legs(self, cv, g):
        if g.p.get("mode") == "sit":
            R.sit_legs(cv, g, fur="V")
            return
        R.legs(cv, g, fur="B")
        top = int(round(g.hip_y - 3))
        m = set()
        for k in range(int(R.BASE - 3 - top)):
            half = 7.5 + k * 0.25
            m |= {(x, top + k) for x in range(int(g.cx - half), int(g.cx + half) + 1)}
        R.solid(cv, m, "V", "v", shade_off=(1, 1))
        for (x, y) in R.inner(m):
            if (x - int(g.cx)) % 4 == 0 or (y - top) % 4 == 0:
                cv.put(x, y, "v")

    def torso(self, cv, g):
        shirt(cv, g, ("S", "smk"), collar=False, buttons=True)

    def headgear(self, cv, g):
        kopiah(cv, g)

    def build(self):
        base = dict(sx=3, rh=(9, 3), rw="tasbih", lh=(-9, 4))
        self.theology_states(base, "book_open", None)

        def consult(t):
            pose = dict(base, rh=(13, -2), rw=None, lh=(-8, 2), lw="tasbih", eyes="look", mouth=talk(t) if t % 8 < 6 else "smile")
            p = dict(pose, bead=t)
            p["tail"] = wag(t, 12)
            p["aura_k"] = t // 4
            return p
        self.add("consult", 12, consult, ms=140, label="berdiskusi dengan sopan")


class Priest(_Theology):
    id = "priest"
    name = "Priest Gobyet"
    silhouette = ["cassock", "white_collar", "plain_book"]
    sleeve = "L"
    book_cover = ("D", "le2")

    def legs(self, cv, g):
        if g.p.get("mode") == "sit":
            R.sit_legs(cv, g, fur="L", boots=("L", "K"))
            return
        R.legs(cv, g, fur="L", boots=("L", "K"))

    def torso(self, cv, g):
        if g.p.get("mode") == "sit":
            R.solid(cv, R.ellipse(g.tcx, g.tcy, g.tw + 0.6, g.th + 0.6), "L", "l", shade_off=(2, 2))
        else:
            G.robe(cv, g, ("L", "l"), flare=2.5, length=-2)
        cx, top = int(round(g.tcx)), int(round(g.tcy - g.th))
        cv.fill(R.rect(cx - 3, top + 1, 6, 2), "W")
        for k in range(4):
            cv.put(cx, top + 4 + k * 3, "l")

    def build(self):
        base = dict(sx=3, rh=(9, 3), rw="book_closed", cover=self.book_cover, lh=(-9, 4))
        self.theology_states(base, "book_open", None)

        def judge(t):
            pose = dict(base, rh=(4, 0), rw="book_open", lh=(-4, 1), eyes="down", mouth="flat")
            p = kf(t, [(0, pose), (6, dict(pose, eyes="look", mouth="flat")), (11, pose)], 12)
            p["tail"] = wag(t, 12)
            p["aura_k"] = t // 4
            if 6 <= t <= 9:
                p["fx"] = [fx_mark("...")]
            return p
        self.add("judge", 12, judge, ms=140, label="menimbang dengan saksama")


CHARS = [Philosopher, Academic, Scientist, Mathematician, Lawyer, Historian, Economist, Psychologist, Sociologist, Engineer,
         Detective, Researcher, PakHaji, Priest]
