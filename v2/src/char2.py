"""Kerangka karakter v2: kelas Char (lapisan kostum sebagai hook) dan render(char, state, i) -> Canvas.

Urutan lapisan (belakang ke depan):
  efek belakang, back() (jubah, tabung panah), ekor, item di punggung, kaki, badan, kepala + headgear,
  lengan kiri layar (lengan, over_arm, item, tangan), lengan kanan layar, tangan kiri lagi bila memegang
  senjata dua tangan, front(), efek depan.

Semua karakter menghadap ke kanan layar (senjata utama di tangan kanan layar). Arena mencerminkan sprite
untuk petarung di sisi kanan.
"""
import math

import rig2 as R
from rig2 import Canvas, Geo, W, H, BASE
from items2 import ITEMS


class State:
    def __init__(self, n, fn, ms=110, loop=True, hold=0, label="", core=None, durs=None, events=None, variant_of=None):
        self.n, self.fn, self.ms, self.loop, self.hold, self.label = n, fn, ms, loop, hold, label
        self.core = core  # state inti arena yang diwakili (idle/attack/hit/victory/defeat)
        # durasi per frame (ms, kelipatan 10) bila tempo tidak rata: ancang-ancang lambat, ayunan cepat, frame hantam
        # ditahan. Tanpa durs semua frame memakai ms.
        if durs is not None:
            assert len(durs) == n and all(d % 10 == 0 for d in durs), (label, durs)
        self.durs = list(durs) if durs is not None else None
        self.events = list(events or [])  # [{"frame": i, "type": "hit" | "hitstop" | "screen_shake" | "vfx", ...}]
        self.variant_of = variant_of  # varian dari state lain (mis. idle_look -> idle)

    def durations(self):
        return list(self.durs) if self.durs else [self.ms] * self.n


class Char:
    id = ""
    name = ""
    category = "fantasy"  # fantasy | domain | role | special
    faction = None
    role = ""
    silhouette = []
    fallback = "normal-gblk"
    body = {}
    fur = "B"
    tail_side = -1
    aliases = {}
    canvas = None  # (x0, y0, w, h) di koordinat rig; None = 64x64 standar

    def __init__(self):
        self.states = {}
        self.build()

    def new_canvas(self):
        return Canvas(self.canvas)

    def post_pose(self, p):
        """Dipanggil setelah pose dibulatkan (mis. tangan kiri dikunci ke gagang senjata dua tangan)."""
        pass

    def build(self):
        pass

    def add(self, name, n, fn, **kw):
        self.states[name] = State(n, fn, **kw)

    # ---- hook kostum
    def back(self, cv, g):
        pass

    def draw_tail(self, cv, g):
        R.tail(cv, g, g.p["tail"], self.tail_side)

    def legs(self, cv, g):
        if g.p.get("mode") == "sit":
            R.sit_legs(cv, g)
        else:
            R.legs(cv, g)

    def torso(self, cv, g):
        R.torso(cv, g)

    def head(self, cv, g):
        R.head(cv, g)

    def headgear(self, cv, g):
        pass

    def arm(self, cv, g, i):
        R.arm(cv, g, i)

    def over_arm(self, cv, g, i):
        pass

    def hand(self, cv, g, i):
        R.hand(cv, g, i)

    def front(self, cv, g):
        pass


def _item(cv, g, i, p):
    key, ang = ("lw", "lwa") if i == 0 else ("rw", "rwa")
    name = p.get(key)
    if not name or p.get("_no_weapon"):
        return None
    return ITEMS[name] + (g.hand[i], p.get(ang, 0.0))


def draw_figure(ch, p, with_head=True, with_fx=True):
    cv = ch.new_canvas()
    g = Geo(p, ch.body)
    if not p.get("_no_fx"):
        for f in p.get("fx_back", ()):
            f(cv, g)
    ch.back(cv, g)
    for i in (0, 1):
        it = _item(cv, g, i, p)
        if it and p.get(("lw" if i == 0 else "rw") + "_back"):
            it[0](cv, it[2], it[3], p)
    if p.get("tail") is not None:
        ch.draw_tail(cv, g)
    ch.legs(cv, g)
    ch.torso(cv, g)
    if p.get("arms_behind_head"):
        _arms(ch, cv, g, p)
        if with_head:
            ch.head(cv, g)
            ch.headgear(cv, g)
    else:
        if with_head:
            ch.head(cv, g)
            ch.headgear(cv, g)
        _arms(ch, cv, g, p)
    ch.front(cv, g)
    if with_fx and not p.get("_no_fx"):
        for f in p.get("fx", ()):
            f(cv, g)
    return cv, g


def _arms(ch, cv, g, p):
    for i in (0, 1):
        if p.get("hide_arm_%d" % i):
            continue
        ch.arm(cv, g, i)
        ch.over_arm(cv, g, i)
        it = _item(cv, g, i, p)
        back = p.get(("lw" if i == 0 else "rw") + "_back")
        if it and not back and not it[1]:
            it[0](cv, it[2], it[3], p)
        if not p.get("hide_hand_%d" % i):
            ch.hand(cv, g, i)
        if it and not back and it[1]:
            it[0](cv, it[2], it[3], p)
    if p.get("grip2"):
        ch.hand(cv, g, 0)


def rotate(cv, deg, pivot):
    """Putar seluruh figur (hanya kelipatan 90 derajat, supaya piksel tetap utuh)."""
    k = int(round(deg / 90.0)) % 4
    px, py = pivot
    out = cv.blank()
    for (x, y), c in cv.px.items():
        dx, dy = x - px, y - py
        for _ in range(k):
            dx, dy = -dy, dx
        out.put(px + dx, py + dy, c)
    return out


def shift(cv, dx, dy):
    out = cv.blank()
    for (x, y), c in cv.px.items():
        out.put(x + dx, y + dy, c)
    return out


QINT = ("dx", "dy", "crouch", "lean", "sx", "lift_l", "lift_r", "fx_l", "fx_r", "hdx", "hdy")
QPT = ("rh", "lh", "re", "le")


def quantize(p):
    """Posisi dibulatkan ke piksel utuh dan sudut ke kelipatan 5 derajat, supaya bentuk tidak berkedip
    antar-frame karena pusat elips pecahan."""
    for k in QINT:
        p[k] = int(round(p[k]))
    for k in QPT:
        if p.get(k) is not None:
            p[k] = tuple(int(round(v)) for v in p[k])
    for k in ("rwa", "lwa"):
        p[k] = 5 * int(round(p[k] / 5.0))
    return p


def ground(cv):
    """Geser figur supaya piksel terbawah tepat di baseline (dipakai setelah rebah)."""
    if not cv.px:
        return cv
    low = max(y for (_, y) in cv.px)
    return shift(cv, 0, (BASE - 1) - low)


def floor_clip(cv):
    """Garis tanah: piksel di bawah baseline (y >= BASE) tidak digambar, jadi prop tidak menembus lantai."""
    cv.px = {k: v for k, v in cv.px.items() if k[1] < BASE}
    return cv


LAYERS = ("body", "weapon", "vfx")


def render(ch, state, i, layer=None):
    """Frame komposit, atau satu lapisan: body (karakter tanpa senjata dan efek), weapon (piksel senjata yang
    terlihat di komposit tanpa efek), vfx (piksel efek yang terlihat di komposit). Ditumpuk body -> weapon -> vfx,
    ketiganya sama persis dengan komposit."""
    if layer is None:
        return floor_clip(_render(ch, state, i))
    full = floor_clip(_render(ch, state, i))
    no_fx = floor_clip(_render(ch, state, i, _no_fx=True))
    if layer == "vfx":
        out = full.blank()
        out.px = {k: v for k, v in full.px.items() if no_fx.px.get(k) != v}
        return out
    body = floor_clip(_render(ch, state, i, _no_fx=True, _no_weapon=True))
    if layer == "body":
        return body
    out = full.blank()
    out.px = {k: v for k, v in no_fx.px.items() if body.px.get(k) != v}
    return out


def render_all(ch, state, i):
    """Komposit + ketiga lapisan dengan tiga render saja (dipakai ekspor)."""
    full = floor_clip(_render(ch, state, i))
    no_fx = floor_clip(_render(ch, state, i, _no_fx=True))
    body = floor_clip(_render(ch, state, i, _no_fx=True, _no_weapon=True))
    vfx, weapon = full.blank(), full.blank()
    vfx.px = {k: v for k, v in full.px.items() if no_fx.px.get(k) != v}
    weapon.px = {k: v for k, v in no_fx.px.items() if body.px.get(k) != v}
    return {"composite": full, "body": body, "weapon": weapon, "vfx": vfx}


def _render(ch, state, i, **flags):
    st = ch.states[state]
    p = R.pose()
    p.update(st.fn(i % st.n))
    quantize(p)
    ch.post_pose(p)
    p.update(flags)
    if not p.get("visible", True):
        cv = ch.new_canvas()
        if not p.get("_no_fx"):
            for f in p.get("fx", ()):
                f(cv, Geo(p, ch.body))
        return cv
    if p.get("spin"):
        # Putaran salto: seluruh figur (kepala, armor, senjata) diputar kelipatan 90 derajat di sekitar pusat badan,
        # piksel tetap utuh. Efek (jejak tebasan) digambar setelahnya di koordinat dunia.
        cv, g = draw_figure(ch, p, with_fx=False)
        cv = rotate(cv, p["spin"], p.get("pivot", (int(round(g.tcx)), int(round(g.tcy)))))
        if not p.get("_no_fx"):
            for f in p.get("fx", ()):
                f(cv, g)
        return cv
    if not p.get("rot"):
        cv, g = draw_figure(ch, p)
        if p.get("mirror"):
            # cermin horizontal (putaran gasing: badan sesaat menghadap kiri), sumbu = tengah badan
            ax = p.get("mirror_x", int(round(g.tcx)))
            out = cv.blank()
            for (x, y), c in cv.px.items():
                out.put(2 * ax - x, y, c)
            cv = out
        return cv
    # Rebah: badan diputar 90 derajat, kepala digambar ulang tegak menghadap kamera (wajah tidak ikut terbalik).
    cv, g = draw_figure(ch, p, with_head=False)
    pivot = p.get("pivot", (R.RX, BASE - 1))
    cv = rotate(cv, p["rot"], pivot)
    hx, hy = _rot_point(g.hx, g.hy, p["rot"], pivot)
    dy = 0
    if p.get("rot_ground") and cv.px:
        dy = (BASE - 1) - max(y for (_, y) in cv.px)
        cv = shift(cv, 0, dy)
    sx, sy = p.get("rot_shift", (0, 0))
    if cv.px:
        minx = min(min(x for (x, _) in cv.px), int(hx) + p.get("lie_hdx", 0) - 15)
        if minx + sx < 1:
            sx = 1 - minx
    if sx or sy:
        cv = shift(cv, sx, sy)
    g.hx, g.hy = hx + sx + p.get("lie_hdx", 0), min(hy + dy + sy, BASE - 9) + p.get("lie_hdy", 0)
    ch.head(cv, g)
    ch.headgear(cv, g)
    if not p.get("_no_fx"):
        for f in p.get("fx_after", ()):
            f(cv, g)
    return cv


def _rot_point(x, y, deg, pivot):
    k = int(round(deg / 90.0)) % 4
    dx, dy = x - pivot[0], y - pivot[1]
    for _ in range(k):
        dx, dy = -dy, dx
    return pivot[0] + dx, pivot[1] + dy


def frames(ch, state, layer=None):
    st = ch.states[state]
    return [render(ch, state, i, layer) for i in range(st.n)]
