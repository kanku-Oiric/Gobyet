"""Animasi Berserker Hero (kostum `berserker-hero`, kanvas 128x96): delapan state.

    idle 12, run 12, rage 12 (tidak loop), attack-leap 14, attack-smash 12, miss 10, exhaustion 12, defeated 14.

Tiap state dibangun dari tabel pose per frame yang diinterpolasi (smoothstep) lalu dibulatkan ke piksel utuh, jadi
tidak ada gerak sub-piksel yang berkedip. Durasi per frame tidak seragam: pose kunci ditahan lebih lama, ayunan cepat.
Frame kunci idle, run, dan attack-smash dibuat dari pose Fase B yang disetujui pemilik untuk dilihat (run: kaki depan
ditukar supaya ayunan lengan lawan kaki, lihat catatan di run); frame kunci state lain ditandai di META.

SCENES mengikuti konvensi modul adegan lain: {nama: (fungsi_frame, jumlah_frame, fungsi_durasi_ms)}.
"""
import math

import hero as H
from hero import FLOOR, SwordFrame

COSTUME = "berserker-hero"
CANVAS = {"w": H.W, "h": H.H}
GIF_SCALE = 4

# ------------------------------------------------------------------ interpolasi pose
INT_FIELDS = ("cx", "lean", "crouch", "dy", "hdx", "hdy", "tilt", "twist", "lh_u")
TUP_FIELDS = ("fl", "fr", "grip", "rh", "lh")


def smooth(x):
    return x * x * (3 - 2 * x)


def lerp(a, b, f):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return a + (b - a) * f
    if isinstance(a, tuple) and isinstance(b, tuple) and len(a) == len(b):
        return tuple(lerp(x, y, f) for x, y in zip(a, b))
    return a if f < 0.5 else b


def at(keys, t, n, loop=False):
    """Pose pada frame t dari keyframe [(frame, dict)] berurutan naik. Bila loop, segmen terakhir menuju keyframe pertama
    pada frame n. Nilai bukan angka (ekspresi, None) mengikuti keyframe sebelumnya."""
    keys = [(f, dict(d)) for f, d in keys]
    if loop:
        keys = keys + [(n, keys[0][1])]
    if t <= keys[0][0]:
        return dict(keys[0][1])
    for (f0, a), (f1, b) in zip(keys, keys[1:]):
        if f0 <= t < f1:
            x = smooth((t - f0) / float(f1 - f0))
            out = dict(a)
            for k in set(a) | set(b):
                va, vb = a.get(k, b.get(k)), b.get(k, a.get(k))
                out[k] = lerp(va, vb, x) if k not in ("fx",) else va
            return out
    return dict(keys[-1][1])


def quant(p):
    """Bulatkan ke piksel utuh: posisi, kaki, genggaman; sudut pedang ke kelipatan 2 derajat."""
    p = dict(p)
    for k in INT_FIELDS:
        p[k] = int(round(p[k]))
    for k in TUP_FIELDS:
        if p.get(k) is not None:
            p[k] = tuple(int(round(v)) for v in p[k])
    p["ang"] = 2 * int(round(p["ang"] / 2.0))
    return p


def pose_of(spec):
    d = H.pose()
    d.update(spec)
    return d


class Track:
    """Satu state: keyframe, jumlah frame, durasi, dan fungsi efek."""

    def __init__(self, name, n, keys, ms, keyframe, loop=True, fx=None, post=None, label=""):
        self.name, self.n, self.keys, self.ms, self.keyframe, self.loop = name, n, keys, ms, keyframe, loop
        self.fx, self.post, self.label = fx, post, label
        assert len(ms) == n, (name, len(ms), n)
        self.keys = [(f, pose_of(d)) for f, d in keys]

    def pose(self, i):
        p = at(self.keys, i, self.n, self.loop)
        if self.post:
            self.post(i, p)
        p = quant(p)
        if self.fx:
            p["fx"] = list(self.fx(i, p))
        return p

    def frame(self, i):
        return H.render_pose(self.pose(i % self.n))

    def duration(self, i):
        return self.ms[i % self.n]


def key(frame, **kw):
    return (frame, kw)


# ================================================================== idle
IDLE = dict(cx=44, lean=1, grip=(63, 73), ang=20, lh_u=-10, sway=0.5, tail_phase=0.4)
_BREATH = [0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0]          # tarik napas: dada turun satu piksel (jongkok 1) lalu kembali
_HEAD = [0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0]            # kepala mengikuti dengan jeda satu frame


def _idle_keys():
    keys = []
    for i in range(12):
        sway = 0.5 + 1.5 * math.sin(2 * math.pi * i / 12.0)             # tabard mencapai ayunan maksimum satu frame setelah dada turun
        d = dict(IDLE, crouch=_BREATH[i], hdy=_HEAD[i], sway=round(sway * 2) / 2.0, tail_phase=0.4 + 2 * math.pi * i / 12.0)
        if i in (5, 6):
            d.update(eyes="side")
        if i == 8:
            d.update(eyes="blink")
        keys.append((i, d))
    return keys


IDLE_TRACK = Track("idle", 12, _idle_keys(), [240, 140, 140, 160, 160, 200, 180, 160, 90, 140, 160, 180], keyframe=0,
                   label="berdiri tegak, ujung pedang di lantai, napas, tabard bergoyang, berkedip")

# ================================================================== run
_RUN_CX = 80
# (fl, fr, crouch, dy, free fist) per frame; fl = kaki kiri layar, fr = kanan layar
_RUN = [
    # f0 kontak kiri depan
    dict(fl=(13, 0), fr=(-13, 5), crouch=4, dy=0, rh=(17, 64), hdy=1, mouth="frown"),
    dict(fl=(12, 0), fr=(-10, 8), crouch=6, dy=0, rh=(16, 66), hdy=1, mouth="frown"),      # f1 turun menyerap
    dict(fl=(4, 0), fr=(2, 9), crouch=4, dy=0, rh=(10, 68), hdy=0, mouth="frown"),         # f2 lintas
    dict(fl=(-6, 2), fr=(9, 8), crouch=1, dy=-3, rh=(2, 70), hdy=0, mouth="shout"),        # f3 dorong naik
    dict(fl=(-16, 3), fr=(15, 11), crouch=2, dy=-8, rh=(-6, 72), hdy=1, mouth="shout"),   # f4 melayang, kaki kanan depan
    dict(fl=(-14, 5), fr=(15, 4), crouch=2, dy=-4, rh=(-4, 72), hdy=0, mouth="shout"),     # f5 turun
    dict(fr=(13, 0), fl=(-13, 5), crouch=4, dy=0, rh=(-6, 72), hdy=1, mouth="frown"),      # f6 kontak kanan depan
    dict(fr=(12, 0), fl=(-10, 8), crouch=6, dy=0, rh=(-2, 71), hdy=1, mouth="frown"),      # f7
    dict(fr=(4, 0), fl=(2, 9), crouch=4, dy=0, rh=(6, 69), hdy=0, mouth="frown"),          # f8
    dict(fr=(-6, 2), fl=(9, 8), crouch=1, dy=-3, rh=(12, 66), hdy=0, mouth="shout"),       # f9
    dict(fr=(-17, 3), fl=(15, 11), crouch=2, dy=-8, rh=(20, 61), hdy=1, mouth="shout"),   # f10 kunci: melayang, kaki kiri depan
    dict(fr=(-14, 5), fl=(15, 4), crouch=3, dy=-4, rh=(18, 63), hdy=0, mouth="shout"),     # f11
]


def _run_keys():
    keys = []
    for i, r in enumerate(_RUN):
        prev = _RUN[(i - 1) % 12]
        sword_y = 80 + int(round(r["dy"] * 0.4))
        # tabard dan ekor menyusul badan dengan jeda satu frame: terangkat dan terseret setelah badan naik
        sway = -5 - round(3 * (-prev["dy"]) / 8.0)
        d = dict(r, cx=_RUN_CX, lean=9, grip=(_RUN_CX - 22, sword_y), ang=186 + (1 if r["dy"] < -5 else 0), lh_u=0,
                 sword_layer="back", head_front=True, eyes="look", brows="angry", sway=sway, lift=1 if prev["dy"] < -3 else 0,
                 tail_phase=2 * math.pi * 2 * i / 12.0 + 1.0)
        keys.append((i, d))
    return keys


def _run_fx(i, p):
    cx = _RUN_CX
    out = []
    step = i % 6
    planted = p["fl"] if i < 6 else p["fr"]
    if step == 0:
        out.append(lambda cv, g: H.fx_dust(cv, cx + 4, FLOOR - 1, 0, 0.7 if i < 6 else 0.85))      # dua injakan tidak identik
    elif step == 1:
        out.append(lambda cv, g: H.fx_dust(cv, cx + 1, FLOOR - 1, 1, 0.8))
    elif step == 2:
        out.append(lambda cv, g: H.fx_dust(cv, cx - 3, FLOOR - 1, 2, 0.7))
    if step == 3:
        out.append(lambda cv, g: H.fx_dust(cv, cx - 14, FLOOR - 1, 0, 0.6))
    n_lines = 2 + (i % 2)
    out.append(lambda cv, g: H.fx_speed(cv, cx - 16 - (i % 3) * 2, 48 + (i % 4) * 2, n_lines, 8 + (i % 3) * 2))
    return out


RUN_TRACK = Track("run", 12, _run_keys(), [70, 80, 70, 60, 100, 60, 70, 80, 70, 60, 100, 60], keyframe=10, fx=_run_fx,
                  label="lari condong ke depan: kontak, serap, lintas, dorong, melayang; debu tiap injakan, garis kecepatan")

# ================================================================== rage (tidak loop)
_RC = 44
RAGE_KEYS = [
    key(0, **IDLE, eyes="look", mouth="frown"),
    key(1, **dict(IDLE, crouch=2, lean=0, hdy=1, eyes="angry", mouth="flat", sway=0.0)),
    key(2, **dict(IDLE, crouch=4, lean=-1, hdy=2, eyes="angry", mouth="flat", sway=-0.5, tilt=0)),
    key(3, **dict(IDLE, crouch=5, lean=-1, hdy=3, eyes="blink", mouth="flat", sway=-1.0)),
    key(4, **dict(IDLE, crouch=-1, lean=-3, hdy=-2, eyes="angry", mouth="shout", face="A", rage=True, sway=2.0, lift=1, flare=2)),
    key(5, **dict(IDLE, crouch=-2, lean=-4, hdy=-3, eyes="angry", mouth="shout", face="A", rage=True, sway=3.0, lift=1, flare=4)),
    key(6, **dict(IDLE, crouch=-2, lean=-4, hdy=-3, eyes="angry", mouth="shout", face="A", rage=True, sway=3.0, lift=1, flare=5)),
    key(7, **dict(IDLE, cx=45, crouch=-1, lean=-3, hdy=-2, eyes="angry", mouth="shout", face="A", rage=True, sway=3.0, lift=1, flare=5)),
    key(8, **dict(IDLE, cx=43, crouch=-1, lean=-3, hdy=-2, eyes="angry", mouth="shout", face="A", rage=True, sway=2.0, lift=1, flare=4)),
    key(9, **dict(IDLE, cx=45, crouch=0, lean=-2, hdy=-1, eyes="angry", mouth="shout", face="A", rage=True, sway=2.0, lift=1, flare=4)),
    key(10, **dict(IDLE, crouch=1, lean=0, hdy=0, eyes="angry", mouth="flat", face="A", rage=True, sway=1.0, lift=0, flare=3)),
    key(11, **dict(IDLE, crouch=3, lean=3, hdy=1, eyes="angry", mouth="frown", face="A", rage=True, sway=1.0, lift=0, flare=3)),
]


def _rage_keys():
    keys = []
    for f, d in RAGE_KEYS:
        d = dict(d, head_front=True)
        d["tail_phase"] = 0.4 + 2 * math.pi * f * 1.5 / 12.0
        keys.append((f, d))
    return keys


def _rage_fx(i, p):
    out = []
    hx = p["cx"] + 4 + 6                               # kira-kira di depan mulut
    if 4 <= i <= 10:
        k = (i - 4) % 3
        out.append(lambda cv, g: H.fx_roar(cv, int(g["head"][0]) + 16, int(g["head"][1]) + 10, k))
        out.append(lambda cv, g: H.fx_teal_sparks(cv, int(g["head"][0]), int(g["head"][1]) - 13, i, seed=i))
        # debu bergetar di kaki: gumpalan kecil kiri dan kanan yang bergeser tiap frame
        out.append(lambda cv, g: H.fx_dust(cv, p["cx"] + (-2 if i % 2 else 2), FLOOR - 1, 0 if i < 8 else 1, 0.7))
    if i == 11:
        out.append(lambda cv, g: H.fx_dust(cv, p["cx"], FLOOR - 1, 2, 0.6))
    return out


RAGE_TRACK = Track("rage", 12, _rage_keys(), [200, 140, 140, 180, 70, 90, 110, 70, 70, 70, 120, 400], keyframe=6, loop=False,
                   fx=_rage_fx, label="mengumpulkan amarah, meledak: wajah merah, mata teal, teriak, tabard mengembang, debu bergetar")

# ================================================================== attack-smash (target: balok kayu)
_SC = 34
_SG = lambda cx: (cx + 19, 73)                  # genggaman istirahat (sama dengan idle yang digeser ke cx)
_IMP = dict(cx=_SC, lean=13, crouch=8, fl=(-13, 0), fr=(14, 0), eyes="angry", brows="angry", mouth="shout", sway=4.0, tail_phase=2.6,
            hdy=0, twist=6, head_front=True, grip=(_SC + 25, 67), ang=42, lh_u=-7)


def _smash_target():
    sf = SwordFrame(_SC + 25, 67.0, 42.0)
    ux = (FLOOR - 67.0) / math.sin(math.radians(42.0))
    return sf.w(ux, 0)


SMASH_HIT = _smash_target()
SMASH_KEYS = [
    key(0, cx=_SC, lean=1, grip=_SG(_SC), ang=20, lh_u=-10, sway=0.5, tail_phase=0.4),
    key(1, cx=_SC, lean=-1, crouch=2, grip=(_SC + 17, 66), ang=-20, lh_u=-9, sway=-0.5, tail_phase=1.0, eyes="angry"),
    key(2, cx=_SC, lean=-1, crouch=3, grip=(_SC + 14, 58), ang=-62, lh_u=-8, sway=-1.0, tail_phase=1.6, eyes="angry", head_front=True),
    key(3, cx=_SC, lean=-2, crouch=4, grip=(_SC + 12, 55), ang=-78, lh_u=-8, sway=-1.5, tail_phase=2.0, eyes="angry", head_front=True, hdy=1, hdx=1),
    key(4, cx=_SC, lean=1, crouch=4, grip=(_SC + 14, 56), ang=-66, lh_u=-8, sway=0.0, tail_phase=2.2, eyes="angry", mouth="shout", head_front=True),
    key(5, cx=_SC, lean=8, crouch=6, grip=(_SC + 21, 58), ang=-44, lh_u=-8, sway=3.0, tail_phase=2.4, eyes="angry", mouth="shout", twist=4, head_front=True),
    key(6, cx=_SC, lean=11, crouch=7, fl=(-13, 0), fr=(14, 0), grip=(_SC + 24, 63), ang=6, lh_u=-7, sway=4.0, tail_phase=2.5, eyes="angry", mouth="shout", twist=5, head_front=True),
    key(7, **_IMP),
    key(8, **dict(_IMP, ang=40, crouch=7, mouth="flat", sway=3.0, tail_phase=2.7)),
    key(9, **dict(_IMP, ang=34, crouch=6, lean=10, mouth="flat", sway=2.0, tail_phase=2.8, grip=(_SC + 24, 66))),
    key(10, **dict(_IMP, ang=26, crouch=4, lean=6, mouth="frown", sway=1.0, tail_phase=3.0, grip=(_SC + 22, 69), twist=3, eyes="look")),
    key(11, cx=_SC, lean=2, crouch=1, grip=_SG(_SC), ang=21, lh_u=-10, sway=0.5, tail_phase=3.2),
]


def _smash_fx(i, p):
    hx, hy = SMASH_HIT
    gx, gy = p["grip"]
    crack = 0 if i < 7 else (1 if i == 7 else 2)
    out = [lambda cv, g: H.wood_block(cv, hx + 5, FLOOR, 18, 11, crack=crack)]
    if 5 <= i <= 6:                                             # dua frame smear sebelum tumbukan (tumbukan sendiri memuat ekor smear)
        k = 6 - i
        out.append(lambda cv, g: H.fx_smear(cv, gx, gy, 44, p["ang"] - 62, p["ang"] - 2, 2 if k < 2 else 1))
        out.append(lambda cv, g: H.fx_smear(cv, gx, gy, 33, p["ang"] - 50, p["ang"] - 6, 1))
    if i >= 7:
        k = i - 7
        if k <= 3:
            out.insert(0, lambda cv, g: H.fx_dust(cv, hx + 5, FLOOR - 1, min(k + 1, 3), 1.0))
        if k == 0:
            out.append(lambda cv, g: H.fx_smear(cv, gx, gy, 44, -38, 34, 2))
            out.append(lambda cv, g: H.fx_smear(cv, gx, gy, 33, -26, 30, 1))
            out.append(lambda cv, g: H.fx_burst(cv, hx - 1, hy - 12, 7))
        elif k == 1:
            out.append(lambda cv, g: H.fx_burst(cv, hx - 1, hy - 12, 4))
        if k <= 4:
            out.append(lambda cv, g: H.fx_chips(cv, hx + 1, FLOOR - 10, k + 1, seed=3, n=9, power=1.0))
    return out


SMASH_TRACK = Track("attack-smash", 12, SMASH_KEYS, [120, 100, 120, 180, 50, 40, 40, 240, 120, 100, 100, 140], keyframe=7,
                    fx=_smash_fx, label="antisipasi, ayunan turun dengan smear, tumbukan ditahan ke balok kayu, serpihan dan debu, pulih")


# ================================================================== attack-leap (lompat lalu tebas turun ke balok kayu)
_LC0, _LC1 = 35, 44                               # kiri-awal dan titik mendarat
_LIMP = dict(_IMP, cx=_LC1, grip=(_LC1 + 25, 67), tail_phase=2.6)


def _leap_target():
    sf = SwordFrame(_LC1 + 25, 67.0, 42.0)
    ux = (FLOOR - 67.0) / math.sin(math.radians(42.0))
    return sf.w(ux, 0)


LEAP_HIT = _leap_target()
_LG = lambda cx: (cx + 19, 73)
LEAP_KEYS = [
    key(0, cx=_LC0, lean=1, grip=_LG(_LC0), ang=20, lh_u=-10, sway=0.5, tail_phase=0.4),
    key(1, cx=_LC0, lean=-1, crouch=6, hdy=2, grip=(_LC0 + 17, 70), ang=-6, lh_u=-9, sway=-1.0, tail_phase=1.0, eyes="angry",
        fl=(-9, 0), fr=(10, 0), head_front=True),
    key(2, cx=_LC0 + 3, lean=2, crouch=2, dy=-2, grip=(_LC0 + 17, 60), ang=-46, lh_u=-8, sway=-2.0, tail_phase=1.4, eyes="angry",
        fl=(-9, 3), fr=(9, 1), mouth="shout", head_front=True),
    key(3, cx=_LC0 + 7, lean=0, crouch=0, dy=-4, grip=(_LC0 + 19, 55), ang=-70, lh_u=-8, sway=-3.0, lift=1, tail_phase=1.8, eyes="angry",
        fl=(-8, 9), fr=(7, 11), mouth="shout", head_front=True),
    key(4, cx=_LC0 + 11, lean=-1, crouch=0, dy=-5, grip=(_LC0 + 22, 55), ang=-74, lh_u=-8, sway=-3.0, lift=1, tail_phase=2.0, eyes="angry",
        fl=(-6, 10), fr=(8, 12), mouth="shout", head_front=True),
    key(5, cx=_LC0 + 13, lean=5, crouch=0, dy=-4, grip=(_LC0 + 24, 56), ang=-38, lh_u=-8, sway=2.0, tail_phase=2.2, eyes="angry",
        fl=(-8, 7), fr=(11, 8), mouth="shout", twist=3, head_front=True),
    key(6, cx=_LC0 + 14, lean=9, crouch=2, dy=-3, grip=(_LC0 + 27, 62), ang=6, lh_u=-8, sway=4.0, tail_phase=2.4, eyes="angry",
        fl=(-11, 3), fr=(13, 3), mouth="shout", twist=4, head_front=True),
    key(7, cx=_LC1, lean=11, crouch=6, grip=(_LC1 + 24, 64), ang=28, lh_u=-7, sway=4.0, tail_phase=2.5, eyes="angry", fl=(-13, 0), fr=(14, 0),
        mouth="shout", twist=5, head_front=True),
    key(8, **_LIMP),
    key(9, **dict(_LIMP, ang=40, crouch=7, mouth="flat", sway=3.0, tail_phase=2.7)),
    key(10, **dict(_LIMP, ang=34, crouch=5, lean=8, mouth="flat", sway=2.0, tail_phase=2.8, grip=(_LC1 + 23, 66), twist=3)),
    key(11, **dict(_LIMP, ang=28, crouch=3, lean=5, mouth="frown", sway=1.0, tail_phase=3.0, grip=(_LC1 + 21, 69), twist=1, cx=_LC1 - 2,
                   eyes="look")),
    key(12, cx=_LC1 - 8, lean=3, crouch=1, grip=_LG(_LC1 - 8), ang=24, lh_u=-10, sway=0.5, tail_phase=3.4, hdy=0),
    key(13, cx=_LC0 + 4, lean=1, crouch=0, grip=_LG(_LC0 + 4), ang=21, lh_u=-10, sway=0.5, tail_phase=3.7),
]


def _leap_fx(i, p):
    hx, hy = LEAP_HIT
    gx, gy = p["grip"]
    crack = 0 if i < 8 else (1 if i == 8 else 2)
    out = [lambda cv, g: H.wood_block(cv, hx + 5, FLOOR, 18, 11, crack=crack)]
    if i == 2:
        out.append(lambda cv, g: H.fx_dust(cv, p["cx"] - 3, FLOOR - 1, 1, 0.8))              # debu tolakan
    if 6 <= i <= 7:                                             # dua frame smear sebelum tumbukan
        k = 7 - i
        out.append(lambda cv, g: H.fx_smear(cv, gx, gy, 44, p["ang"] - 66, p["ang"] - 2, 2 if k < 2 else 1))
        out.append(lambda cv, g: H.fx_smear(cv, gx, gy, 33, p["ang"] - 54, p["ang"] - 6, 1))
    if i == 7:
        out.append(lambda cv, g: H.fx_dust(cv, p["cx"] + 2, FLOOR - 1, 0, 0.9))              # tiba di lantai
    if i >= 8:
        k = i - 8
        if k <= 4:
            out.insert(0, lambda cv, g: H.fx_dust(cv, hx + 5, FLOOR - 1, min(k + 1, 3), 1.0))
        if k <= 2:
            out.insert(0, lambda cv, g: H.fx_dust(cv, p["cx"] + 2, FLOOR - 1, min(k + 1, 3), 0.9))
        if k == 0:
            out.append(lambda cv, g: H.fx_smear(cv, gx, gy, 44, -38, 34, 2))
            out.append(lambda cv, g: H.fx_smear(cv, gx, gy, 33, -26, 30, 1))
            out.append(lambda cv, g: H.fx_burst(cv, hx - 1, hy - 12, 8))
        elif k == 1:
            out.append(lambda cv, g: H.fx_burst(cv, hx - 1, hy - 12, 4))
        if k <= 5:
            out.append(lambda cv, g: H.fx_chips(cv, hx + 1, FLOOR - 10, k + 1, seed=5, n=10, power=1.1))
    return out


LEAP_TRACK = Track("attack-leap", 14, LEAP_KEYS, [140, 130, 60, 60, 120, 50, 40, 40, 260, 130, 110, 100, 100, 130], keyframe=8, fx=_leap_fx,
                   label="berjongkok, melompat dengan pedang terangkat, tebas turun dengan smear, mendarat dan menghantam balok kayu, pulih")

# ================================================================== miss (tebasan meleset: pedang menancap lantai di depan balok)
_MC = 34
MISS_FLOOR = 70.0                                  # x tempat bilah masuk lantai (di depan balok kayu di ~ 89)
MISS_KEYS = [
    key(0, cx=_MC, lean=1, grip=_SG(_MC), ang=20, lh_u=-10, sway=0.5, tail_phase=0.4),
    key(1, cx=_MC, lean=-1, crouch=2, grip=(_MC + 17, 66), ang=-20, lh_u=-9, sway=-0.5, tail_phase=1.0, eyes="angry"),
    key(2, cx=_MC, lean=-1, crouch=3, grip=(_MC + 14, 58), ang=-62, lh_u=-8, sway=-1.0, tail_phase=1.6, eyes="angry", head_front=True),
    key(3, cx=_MC, lean=3, crouch=4, grip=(_MC + 18, 56), ang=-30, lh_u=-8, sway=2.0, tail_phase=2.0, eyes="angry", mouth="shout",
        head_front=True, twist=3),
    key(4, cx=_MC, lean=9, crouch=5, grip=(_MC + 21, 62), ang=20, lh_u=-7, sway=4.0, tail_phase=2.3, eyes="angry", mouth="shout",
        head_front=True, twist=4),
    key(5, cx=_MC, lean=14, crouch=7, fl=(-14, 0), fr=(15, 0), grip=(_MC + 22, 67), ang=56, lh_u=-7, sway=5.0, tail_phase=2.6, eyes="wide",
        brows="worried", mouth="o", head_front=True, twist=5),
    key(6, cx=_MC + 2, lean=17, crouch=6, fl=(-14, 3), fr=(15, 0), grip=(_MC + 25, 67), ang=56, lh_u=-7, sway=6.0, tail_phase=2.8,
        eyes="wide", brows="worried", mouth="o", head_front=True, twist=6),
    key(7, cx=_MC + 1, lean=12, crouch=5, fl=(-12, 0), fr=(13, 0), grip=(_MC + 24, 67), ang=56, lh_u=-7, sway=3.0, tail_phase=3.0,
        eyes="side", brows="worried", mouth="flat", head_front=True, twist=3, hdx=1),
    key(8, cx=_MC, lean=6, crouch=3, grip=(_MC + 22, 69), ang=42, lh_u=-8, sway=1.5, tail_phase=3.2, eyes="down", brows="worried", mouth="flat"),
    key(9, cx=_MC, lean=2, crouch=1, grip=_SG(_MC), ang=21, lh_u=-10, sway=0.5, tail_phase=3.5),
]


def _miss_hit():
    sf = SwordFrame(_MC + 22, 67.0, 56.0)
    ux = (FLOOR - 67.0) / math.sin(math.radians(56.0))
    return sf.w(ux, 0)


MISS_HIT = _miss_hit()


def _miss_fx(i, p):
    hx, hy = MISS_HIT
    gx, gy = p["grip"]
    out = [lambda cv, g: H.wood_block(cv, SMASH_HIT[0] + 5, FLOOR, 18, 11, crack=0)]
    if 3 <= i <= 4:
        out.append(lambda cv, g: H.fx_smear(cv, gx, gy, 44, p["ang"] - 62, p["ang"] - 2, 2 if i == 4 else 1))
        out.append(lambda cv, g: H.fx_smear(cv, gx, gy, 33, p["ang"] - 50, p["ang"] - 6, 1))
    if 5 <= i <= 7:
        k = i - 5
        out.insert(0, lambda cv, g: H.fx_dust(cv, hx + 2, FLOOR - 1, min(k + 1, 3), 0.9))
        if i == 5:
            out.append(lambda cv, g: H.fx_burst(cv, hx - 1, hy - 8, 5))
            out.append(lambda cv, g: H.fx_chips(cv, hx + 1, FLOOR - 8, 1, seed=11, n=6, power=0.8))
    if i in (6, 7):
        hx_, hy_ = g_head(p)
        out.append(lambda cv, g: H.fx_sweat(cv, int(g["head"][0]) - 20 + (i - 6) * 2, int(g["head"][1]) - 12 + (i - 6) * 4))
    if i == 8:
        out.append(lambda cv, g: H.fx_dust(cv, hx + 2, FLOOR - 1, 3, 0.7))
    return out


def g_head(p):
    g = H.geometry(p)
    return g["head"]


MISS_TRACK = Track("miss", 10, MISS_KEYS, [140, 100, 130, 50, 40, 200, 220, 240, 140, 140], keyframe=6, fx=_miss_fx,
                   label="ayunan penuh tenaga, pedang menancap lantai di depan balok, kehilangan keseimbangan, malu lalu kembali siaga")

# ================================================================== exhaustion (kelelahan: bungkuk, napas berat)
_EC = 44
_E_CROUCH = [8, 7, 6, 6, 7, 8, 8, 7, 6, 6, 7, 8]            # dada naik-turun dua kali per putaran; frame 11 = frame 0
_E_HEAD = [5, 4, 3, 3, 4, 5, 5, 4, 3, 3, 4, 5]


def _exh_keys():
    keys = []
    for i in range(12):
        c, h = _E_CROUCH[i], _E_HEAD[i]
        d = dict(cx=_EC, lean=8, crouch=c, hdy=h, grip=(_EC + 19, 79), ang=12, lh_u=-9, eyes="relief", brows="worried", mouth="o", head_front=True,
                 sway=-1.0 - (c - 6) * 0.5, lift=0, tail_phase=0.5 + 2 * math.pi * i * 2 / 12.0, fl=(-8, 0), fr=(8, 0))
        if i in (2, 3):
            d.update(mouth="flat")
        if i in (8,):
            d.update(eyes="blink")
        keys.append((i, d))
    return keys


def _exh_fx(i, p):
    out = []
    g = H.geometry(p)
    hx, hy = int(g["head"][0]), int(g["head"][1])
    if i in (4, 5, 6):                                          # napas keluar saat hembus, di bawah dagu (tidak menutup wajah/telinga)
        out.append(lambda cv, g: H.fx_breath(cv, hx + 6 + (i - 4) * 2, hy + 16 + (i - 4), i - 4))
    if i in (10, 11, 0):
        kk = 2 if i == 0 else i - 10
        out.append(lambda cv, g: H.fx_breath(cv, hx + 6 + kk * 2, hy + 16 + kk, kk))
    # keringat jatuh dari pelipis sepanjang putaran, di luar telinga kiri
    k = i % 6
    sx = hx - 25
    if k < 5:
        out.append(lambda cv, g: H.fx_sweat(cv, sx, hy - 4 + k * 5))
    return out


EXH_TRACK = Track("exhaustion", 12, _exh_keys(), [200, 150, 150, 170, 220, 260, 220, 150, 90, 150, 170, 200], keyframe=5, fx=_exh_fx,
                  label="bungkuk bertumpu pada pedang, dada naik turun, mata sayu, napas mengepul, keringat menetes")

# ================================================================== defeated (berlutut bertumpu pada pedang, tertunduk, bermartabat)
_DC = 40
_D_CROUCH = [11, 11, 10, 10, 10, 11, 11, 11, 10, 10, 10, 11, 11, 11]
_D_HEAD = [5, 5, 4, 4, 4, 5, 5, 5, 4, 4, 4, 5, 5, 5]


def _def_keys():
    keys = []
    for i in range(14):
        d = dict(cx=_DC, lean=9, crouch=_D_CROUCH[i], hdy=_D_HEAD[i], fl=(-19, 1), fr=(14, 0), toe_l=-1, legs_front=True,
                 grip=(_DC + 33, 74), ang=84, lh=(_DC + 11, 76), head_front=True,
                 eyes="down", brows="worried", mouth="flat", sway=-2.0 + 0.5 * (_D_CROUCH[i] - 10), tail_phase=0.3 + 2 * math.pi * i / 14.0)
        if i in (7, 8):
            d.update(eyes="blink")
        keys.append((i, d))
    return keys


def _def_fx(i, p):
    out = []
    g = H.geometry(p)
    hx, hy = int(g["head"][0]), int(g["head"][1])
    if i in (4, 5, 6):
        out.append(lambda cv, g: H.fx_breath(cv, hx + 6 + (i - 4) * 2, hy + 16 + (i - 4), i - 4))
    k = (i - 9) % 14
    if k < 5:
        out.append(lambda cv, g: H.fx_sweat(cv, hx - 25, hy - 4 + k * 5))
    return out


DEF_TRACK = Track("defeated", 14, _def_keys(), [200, 180, 180, 200, 200, 220, 200, 160, 120, 180, 200, 200, 200, 200], keyframe=3, fx=_def_fx,
                  label="berlutut bertumpu pada pedang yang menancap, kepala tertunduk, napas pelan; bermartabat")


# ================================================================== daftar adegan dan metadata
TRACKS = {t.name: t for t in (IDLE_TRACK, RUN_TRACK, RAGE_TRACK, LEAP_TRACK, SMASH_TRACK, MISS_TRACK, EXH_TRACK, DEF_TRACK)}


def _scene(t):
    return (lambda i, t=t: t.frame(i), t.n, lambda i, t=t: t.duration(i))


SCENES = {"%s-%s" % (COSTUME, name): _scene(t) for name, t in TRACKS.items()}
META = {name: {"frames": t.n, "keyframe": t.keyframe, "loop": t.loop, "label": t.label} for name, t in TRACKS.items()}
