"""Animasi Berserker Hero v3 (kostum `berserker-hero`, kanvas 128x96; zirah bukan Gobyet, wajah Gobyet di balik topeng): sembilan state.

    idle 12, run 12, rage 12 (tidak loop), attack-leap 14, attack-smash 12, miss 10, exhaustion 12, defeated 14, victory 20 (tidak loop).

Tiap state dibangun dari tabel pose per frame yang diinterpolasi (smoothstep) lalu dibulatkan ke piksel utuh, jadi tidak ada gerak sub-piksel yang
berkedip. Durasi per frame tidak seragam: pose kunci ditahan lebih lama, ayunan cepat. Pola durasi dan urutan beat tiap state mengikuti yang sudah
dilihat pemilik pada hero v1 (gaya v1 ditolak, timing dan emote dipertahankan); isinya digambar ulang dengan rig `hero3`.

State baru `victory` (permintaan pemilik): topeng membuka (wajah Gobyet tersenyum) dan menutup, pedang ditusukkan ke tanah, satu kaki naik ke batu sambil tangan mengusap
darah monster dari bilah. Darah monster berwarna merah darah gelap (dibedakan dari merah zirah) dan hanya ada di state ini.

SCENES mengikuti konvensi modul adegan lain: {nama: (fungsi_frame, jumlah_frame, fungsi_durasi_ms)}.
"""
import math

import hero as H3base  # noqa: F401  (FLOOR, SwordFrame)
import hero3 as R
import hero3_fx as FX
from hero import FLOOR, SwordFrame

COSTUME = "berserker-hero"
CANVAS = {"w": R.H.W, "h": R.H.H}
GIF_SCALE = 4

# ------------------------------------------------------------------ interpolasi pose
INT_FIELDS = ("cx", "lean", "crouch", "dy", "hdx", "hdy", "twist", "lh_u", "heat")
TUP_FIELDS = ("fl", "fr", "grip", "rh", "lh")
NO_LERP = ("fx", "props")


def smooth(x):
    return x * x * (3 - 2 * x)


def lerp(a, b, f):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return a + (b - a) * f
    if isinstance(a, tuple) and isinstance(b, tuple) and len(a) == len(b):
        return tuple(lerp(x, y, f) for x, y in zip(a, b))
    return a if f < 0.5 else b


def at(keys, t, n, loop=False):
    """Pose pada frame t dari keyframe [(frame, dict)] berurutan naik. Bila loop, segmen terakhir menuju keyframe pertama pada frame n.
    Nilai bukan angka (ekspresi, None) mengikuti keyframe sebelumnya."""
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
                out[k] = lerp(va, vb, x) if k not in NO_LERP else va
            return out
    return dict(keys[-1][1])


def quant(p):
    """Bulatkan ke piksel utuh: posisi, kaki, genggaman; sudut pedang ke kelipatan 2 derajat; sway dan flare ke 0,5."""
    p = dict(p)
    for k in INT_FIELDS:
        p[k] = int(round(p[k]))
    for k in TUP_FIELDS:
        if p.get(k) is not None:
            p[k] = tuple(int(round(v)) for v in p[k])
    p["ang"] = 2 * int(round(p["ang"] / 2.0))
    p["sway"] = round(p["sway"] * 2) / 2.0
    p["flare"] = round(p["flare"] * 2) / 2.0
    p["mask"] = round(p["mask"] * 8) / 8.0
    if p.get("stain_u") is not None:
        p["stain_u"] = int(round(p["stain_u"]))
    return p


def pose_of(spec):
    d = R.pose()
    d.update(spec)
    return d


# per state: pengali jari-jari ekor dan putaran tambahan kipas (derajat), dicari agar tepi kiri tetap >= 1 px (perisai naga menahan cx >= 52)
TAIL_SCALE = {"rage": 0.6, "attack-leap": 0.8, "attack-smash": 1.0, "miss": 0.9, "exhaustion": 0.95, "defeated": 0.75, "victory": 1.0}
TAIL_ROT = {"rage": 10.0, "attack-leap": 55.0, "attack-smash": 55.0, "miss": 25.0, "exhaustion": 10.0, "defeated": 10.0, "victory": 25.0}


# State serangan (keputusan pemilik "ekor sedang"): di frame tumbukan kipas ekor dipindah ke atas-belakang dan dibesarkan supaya tidak tertutup perisai
# naga; di frame lain ekor kembali bertahap ke bentuk dasar state itu supaya tidak terpotong tepi kanvas. (skala, putaran, dx, dy) dasar dan puncak,
# dan bobot puncak per frame (0 = dasar, 1 = puncak). Nilai dicari otomatis terhadap tepi kanvas dan ukuran ekor idle; lihat laporan.
TAIL_PEAK = {
    "attack-leap": ((1.2, 90.0, 8.0, -24.0), [0.5, 0.75, 0.5, 0.5, 0.5, 0.5, 0.75, 0.75, 1.0, 1.0, 1.0, 1.0, 0.5, 0.5]),
    "attack-smash": ((0.8, 30.0, 4.0, -24.0), [1.0] * 12),
    "miss": ((0.8, 15.0, 8.0, -24.0), [1.0] * 10),
}


def tail_params(name, i):
    base = (TAIL_SCALE.get(name, 1.0), TAIL_ROT.get(name, 0.0), 0.0, 0.0)
    if name not in TAIL_PEAK:
        return base
    peak, weights = TAIL_PEAK[name]
    w = weights[i % len(weights)]
    return tuple(a + (b - a) * w for a, b in zip(base, peak))


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
        sc, rot, dx, dy = tail_params(self.name, i)                          # ekor per state (dan per frame di state serangan)
        p["tail_k"] = p["tail_k"] * sc
        p["tail_rot"] = p["tail_rot"] + rot
        p["tail_dx"], p["tail_dy"] = dx, dy
        p = quant(p)
        if self.fx:
            p["fx"] = list(self.fx(i, p))
        return p

    def frame(self, i):
        return R.render_pose(self.pose(i % self.n))

    def duration(self, i):
        return self.ms[i % self.n]


def key(frame, **kw):
    return (frame, kw)


def rest(cx, **kw):
    """Pose istirahat: pedang tertancap di sisi kanan, satu tangan di gagang setinggi bahu, tangan lain di pinggul (di balik pelindung bahu)."""
    d = dict(cx=cx, lean=1, grip=(cx + 28, 47), ang=82, lh=(cx - 14, 74), tail_k=0.82, tail_phase=0.4)
    d.update(kw)
    return d


# ================================================================== idle
_BREATH = [0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0]          # tarik napas: dada turun satu piksel lalu kembali
_HEAD = [0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0]            # kepala mengikuti dengan jeda satu frame
_IC = 66


def _idle_keys():
    keys = []
    for i in range(12):
        sway = 0.5 + 1.5 * math.sin(2 * math.pi * i / 12.0)              # jambul mencapai ayunan maksimum satu frame setelah dada turun
        d = rest(_IC, crouch=_BREATH[i], hdy=_HEAD[i], sway=round(sway * 2) / 2.0, tail_phase=0.4 + 2 * math.pi * i / 12.0, eyes="look")
        if i == 8:
            d.update(eyes="shut")
        if i == 9:
            d.update(eyes="dim")
        keys.append((i, d))
    return keys


IDLE_TRACK = Track("idle", 12, _idle_keys(), [240, 140, 140, 160, 160, 200, 180, 160, 90, 140, 160, 180], keyframe=0,
                   label="berdiri tegak, pedang tertancap, napas, jambul bergoyang, visor berkedip")

# ================================================================== run
_RC = 60
# (fl, fr, crouch, dy) per frame; fl = kaki kiri layar, fr = kanan layar
_RUN = [
    dict(fr=(13, 0), fl=(-12, 4), crouch=4, dy=0, hdy=1),         # f0 kontak: kaki kanan depan
    dict(fr=(11, 0), fl=(-10, 7), crouch=6, dy=0, hdy=1),         # f1 serap
    dict(fr=(4, 0), fl=(1, 9), crouch=4, dy=0, hdy=0),            # f2 lintas
    dict(fr=(-6, 2), fl=(8, 8), crouch=1, dy=-3, hdy=0),          # f3 dorong naik
    dict(fr=(-12, 4), fl=(13, 11), crouch=2, dy=-7, hdy=1),       # f4 melayang
    dict(fr=(-10, 6), fl=(13, 4), crouch=3, dy=-3, hdy=1),        # f5 turun
    dict(fl=(13, 0), fr=(-12, 4), crouch=4, dy=0, hdy=1),         # f6 kontak: kaki kiri depan
    dict(fl=(11, 0), fr=(-10, 7), crouch=6, dy=0, hdy=1),         # f7
    dict(fl=(4, 0), fr=(1, 9), crouch=4, dy=0, hdy=0),            # f8
    dict(fl=(-6, 2), fr=(8, 8), crouch=1, dy=-3, hdy=0),          # f9
    dict(fl=(-12, 4), fr=(13, 11), crouch=2, dy=-7, hdy=1),       # f10 kunci: melayang, kaki kiri belakang
    dict(fl=(-10, 6), fr=(13, 4), crouch=3, dy=-3, hdy=1),        # f11
]


def _run_keys():
    keys = []
    for i, r in enumerate(_RUN):
        prev = _RUN[(i - 1) % 12]
        bob = int(round(r["dy"] * 0.4))
        sway = -4 - round(3 * (-prev["dy"]) / 7.0)                          # jambul menyusul badan dengan jeda satu frame
        d = dict(r, cx=_RC, lean=12, grip=(_RC + 31, 60 + bob), ang=-50 + (4 if r["dy"] < -5 else 0) - (2 if r["dy"] > -1 else 0),
                 lh=(_RC + 2, 70), eyes="angry", mouth="closed", hdx=2, sway=sway, tail_k=0.82, tail_rot=8 - 2 * (i % 2),
                 tail_phase=2 * math.pi * 2 * i / 12.0 + 1.0)
        if i in (3, 4, 9, 10):
            d.update(mouth="shout")
        keys.append((i, d))
    return keys


def _run_fx(i, p):
    cx = _RC
    out = []
    step = i % 6
    if step == 0:
        out.append(lambda cv, g: FX.fx_dust(cv, cx + 6, FLOOR - 1, 0, 0.8))                          # kontak: debu sama di dua injakan supaya seam tidak lebih besar dari langkah
    elif step == 1:
        out.append(lambda cv, g: FX.fx_dust(cv, cx + 3, FLOOR - 1, 1, 0.8))
    elif step == 2:
        out.append(lambda cv, g: FX.fx_dust(cv, cx - 1, FLOOR - 1, 2, 0.7))
    if step == 3:
        out.append(lambda cv, g: FX.fx_dust(cv, cx - 12, FLOOR - 1, 0, 0.6))
    n_lines = 2 + (i % 2)
    out.append(lambda cv, g: FX.fx_speed(cv, cx - 30 - (i % 3) * 2, 60 + (i % 3) * 3, n_lines, 8 + (i % 3) * 2))
    return out


RUN_TRACK = Track("run", 12, _run_keys(), [70, 80, 70, 60, 100, 60, 70, 80, 70, 60, 100, 60], keyframe=10, fx=_run_fx,
                  label="lari condong ke depan dengan pedang diacungkan: kontak, serap, lintas, dorong, melayang; debu tiap injakan, garis kecepatan")

# ================================================================== rage (tidak loop): kumpul amarah, meledak, pedang diacungkan, tahan
_GC = 56
_RAISED = dict(grip=(_GC + 24, 48), ang=-66, lh=(_GC - 14, 72))


def _rg(**kw):
    d = rest(_GC)
    d.update(kw)
    return d


RAGE_KEYS = [
    key(0, **_rg(eyes="look")),
    key(1, **_rg(crouch=2, lean=0, hdy=1, eyes="glare", sway=0.0)),
    key(2, **_rg(crouch=4, lean=-1, hdy=2, eyes="glare", sway=-0.5, grip=(_GC + 27, 50), ang=76)),
    key(3, **_rg(crouch=5, lean=-1, hdy=3, eyes="dim", sway=-1.0, grip=(_GC + 26, 49), ang=70)),
    key(4, **_rg(crouch=-1, lean=-3, hdy=-2, eyes="rage", mouth="shout", heat=2, flare=3, sway=2.0, glow=2, tail_rot=16, tail_k=0.9, **_RAISED)),
    key(5, **_rg(crouch=-2, lean=-4, hdy=-3, eyes="rage", mouth="shout", heat=2, flare=4, sway=3.0, glow=2, tail_rot=22, tail_k=0.95, **_RAISED)),
    key(6, **_rg(crouch=-2, lean=-4, hdy=-3, eyes="rage", mouth="shout", heat=2, flare=5, sway=3.0, glow=2, tail_rot=24, tail_k=1.0, **_RAISED)),
    key(7, **_rg(cx=_GC + 1, crouch=-1, lean=-3, hdy=-2, eyes="rage", mouth="shout", heat=2, flare=5, sway=3.0, glow=2, tail_rot=22, tail_k=1.0,
                 grip=(_GC + 25, 48), ang=-66, lh=(_GC - 13, 72))),
    key(8, **_rg(cx=_GC - 1, crouch=-1, lean=-3, hdy=-2, eyes="rage", mouth="shout", heat=2, flare=4, sway=2.0, glow=2, tail_rot=18, tail_k=0.95,
                 grip=(_GC + 23, 48), ang=-66, lh=(_GC - 15, 72))),
    key(9, **_rg(cx=_GC + 1, crouch=0, lean=-2, hdy=-1, eyes="rage", mouth="shout", heat=2, flare=4, sway=2.0, glow=2, tail_rot=18, tail_k=0.95, **_RAISED)),
    key(10, **_rg(crouch=1, lean=0, hdy=0, eyes="angry", mouth="closed", heat=1, flare=3, sway=1.0, glow=2, tail_rot=12, tail_k=0.9, **_RAISED)),
    key(11, **_rg(crouch=3, lean=3, hdy=1, eyes="angry", mouth="closed", heat=1, flare=3, sway=1.0, glow=2, tail_rot=10, tail_k=0.88, **_RAISED)),
]


def _rage_keys():
    keys = []
    for f, d in RAGE_KEYS:
        d = dict(d)
        d["tail_phase"] = 0.4 + 2 * math.pi * f * 1.5 / 12.0
        keys.append((f, d))
    return keys


def _rage_fx(i, p):
    out = []
    if 4 <= i <= 10:
        k = (i - 4) % 3
        out.append(lambda cv, g: FX.fx_roar(cv, int(g["head"][0]) + 14, int(g["head"][1]) + 8, k))
        out.append(lambda cv, g: FX.fx_embers(cv, int(g["head"][0]) - 4, int(g["head"][1]) - 22, i, seed=i, n=7, spread=22))
        out.append(lambda cv, g: FX.fx_dust(cv, p["cx"] + (-2 if i % 2 else 2), FLOOR - 1, 0 if i < 8 else 1, 0.7))
    if i == 11:
        out.append(lambda cv, g: FX.fx_dust(cv, p["cx"], FLOOR - 1, 2, 0.6))
        out.append(lambda cv, g: FX.fx_embers(cv, int(g["head"][0]) - 4, int(g["head"][1]) - 22, 11, seed=11, n=3, spread=18))
    return out


RAGE_TRACK = Track("rage", 12, _rage_keys(), [200, 140, 140, 180, 70, 90, 110, 70, 70, 70, 120, 1500], keyframe=6, loop=False, fx=_rage_fx,
                   label="mengumpulkan amarah, meledak: visor putih-merah, jambul dan ekor mengembang, pedang diacungkan, bara dan garis kejut")

# ================================================================== attack-smash (target: balok kayu)
_SC = 53
_HIT = dict(cx=_SC, lean=10, crouch=6, fl=(-14, 0), fr=(15, 0), eyes="rage", mouth="shout", glow=2, tail_phase=2.6, tail_rot=10, tail_k=0.64, twist=5,
            grip=(_SC + 30, 58), ang=44, lh=(_SC + 1, 72))


def _smash_target(gx=83.0, gy=58.0, ang=44.0):
    sf = SwordFrame(gx, gy, ang)
    ux = (FLOOR - 11 - gy) / math.sin(math.radians(ang))
    return sf.w(ux, 0)


SMASH_HIT = _smash_target()


def _sm(**kw):
    d = rest(_SC, tail_k=0.64)
    d.update(kw)
    return d


SMASH_KEYS = [
    key(0, **_sm()),
    key(1, **_sm(lean=-1, crouch=2, grip=(_SC + 30, 50), ang=50, sway=-0.5, tail_phase=1.0, eyes="angry")),
    key(2, **_sm(lean=-1, crouch=3, grip=(_SC + 26, 54), ang=22, sway=-1.0, tail_phase=1.6, eyes="angry")),
    key(3, **_sm(lean=-2, crouch=4, grip=(_SC + 30, 56), ang=-40, sway=-1.5, tail_phase=2.0, eyes="angry", hdy=1, hdx=1)),
    key(4, **_sm(lean=-2, crouch=4, grip=(_SC + 30, 55), ang=-80, sway=-1.0, tail_phase=2.2, eyes="angry", mouth="shout", hdy=1)),
    key(5, **_sm(lean=3, crouch=5, grip=(_SC + 31, 56), ang=-52, sway=3.0, tail_phase=2.4, eyes="angry", mouth="shout", twist=3)),
    key(6, **_sm(lean=8, crouch=6, grip=(_SC + 26, 57), ang=14, sway=4.0, tail_phase=2.5, eyes="angry", mouth="shout", twist=4)),
    key(7, **_sm(**_HIT)),
    key(8, **_sm(**dict(_HIT, ang=42, mouth="closed", eyes="rage"))),
    key(9, **_sm(**dict(_HIT, ang=38, crouch=5, lean=9, mouth="closed", glow=1, eyes="angry", grip=(_SC + 29, 59)))),
    key(10, **_sm(**dict(_HIT, ang=50, crouch=3, lean=5, mouth="closed", glow=1, eyes="look", grip=(_SC + 28, 54), twist=3))),
    key(11, **_sm()),
]


def _smash_fx(i, p):
    hx, hy = SMASH_HIT
    gx, gy = p["grip"]
    crack = 0 if i < 7 else (1 if i == 7 else 2)
    out = [lambda cv, g: FX.wood_block(cv, hx + 3, FLOOR, 16, 11, crack=crack)]
    if 5 <= i <= 6:                                             # dua frame smear sebelum tumbukan (tumbukan sendiri memuat ekor smear)
        k = 6 - i
        out.append(lambda cv, g: FX.fx_smear(cv, gx, gy, 38, p["ang"] - 62, p["ang"] - 2, 2 if k < 2 else 1))
        out.append(lambda cv, g: FX.fx_smear(cv, gx, gy, 29, p["ang"] - 50, p["ang"] - 6, 1))
    if i >= 7:
        k = i - 7
        if k <= 3:
            out.insert(0, lambda cv, g: FX.fx_dust(cv, hx + 3, FLOOR - 1, min(k + 1, 2), 0.9))
        if k == 0:
            out.append(lambda cv, g: FX.fx_smear(cv, gx, gy, 34, -34, 40, 2))
            out.append(lambda cv, g: FX.fx_smear(cv, gx, gy, 26, -26, 34, 1))
            out.append(lambda cv, g: FX.fx_burst(cv, hx - 1, hy - 2, 7))
        elif k == 1:
            out.append(lambda cv, g: FX.fx_burst(cv, hx - 1, hy - 2, 4))
        if k <= 4:
            out.append(lambda cv, g: FX.fx_chips(cv, hx + 1, FLOOR - 10, k + 1, seed=3, n=9, power=1.0))
    return out


SMASH_TRACK = Track("attack-smash", 12, SMASH_KEYS, [120, 100, 120, 180, 50, 40, 40, 240, 120, 100, 100, 140], keyframe=7, fx=_smash_fx,
                    label="antisipasi, pedang diangkat tinggi, ayunan turun dengan smear, tumbukan ditahan ke balok kayu, serpihan dan debu, pulih")


# ================================================================== attack-leap (lompat lalu tebas turun ke balok kayu)
_L0, _L1 = 52, 57                                # kiri-awal dan titik mendarat (pelindung bahu raksasa menahan cx >= 46 agar tidak terpotong)
LEAP_HIT = SMASH_HIT


def _lp(cx, **kw):
    d = rest(cx, tail_k=0.82)
    d.update(kw)
    return d


_LIMP = {k: v for k, v in _HIT.items() if k != "cx"}
LEAP_KEYS = [
    key(0, **_lp(_L0)),
    key(1, **_lp(_L0, lean=-1, crouch=6, hdy=2, grip=(_L0 + 30, 53), ang=55, sway=-1.0, tail_phase=1.0, eyes="angry", fl=(-9, 0), fr=(10, 0))),
    key(2, **_lp(_L0 + 2, lean=2, crouch=1, dy=-1, grip=(_L0 + 27, 52), ang=24, sway=-2.0, tail_phase=1.4, eyes="angry", fl=(-9, 3), fr=(9, 2),
                 mouth="shout")),
    key(3, **_lp(_L0 + 4, lean=0, crouch=0, dy=-3, grip=(_L0 + 35, 52), ang=-45, sway=-3.0, tail_phase=1.8, eyes="angry", fl=(-8, 9), fr=(7, 11),
                 mouth="shout")),
    key(4, **_lp(_L0 + 6, lean=-1, crouch=-1, dy=-3, grip=(_L0 + 36, 52), ang=-78, sway=-3.0, tail_phase=2.0, eyes="angry", fl=(-6, 10), fr=(8, 12),
                 mouth="shout")),
    key(5, **_lp(_L0 + 7, lean=4, crouch=0, dy=-2, grip=(_L0 + 38, 54), ang=-45, sway=2.0, tail_phase=2.2, eyes="angry", fl=(-8, 7), fr=(11, 8),
                 mouth="shout", twist=3)),
    key(6, **_lp(_L1 - 1, lean=8, crouch=2, dy=-1, grip=(_L1 + 21, 57), ang=-10, sway=4.0, tail_phase=2.4, eyes="angry", fl=(-11, 3), fr=(13, 3),
                 mouth="shout", twist=4)),
    key(7, **_lp(_L1, lean=10, crouch=5, grip=(_L1 + 26, 58), ang=26, sway=4.0, tail_phase=2.5, eyes="angry", fl=(-13, 0), fr=(14, 0), mouth="shout",
                 twist=5, glow=2)),
    key(8, **_lp(_L1, **dict(_LIMP, tail_k=0.64))),
    key(9, **_lp(_L1, **dict(_LIMP, ang=38, mouth="closed", tail_k=0.64))),
    key(10, **_lp(_L1, **dict(_LIMP, ang=38, crouch=5, lean=8, mouth="closed", glow=1, eyes="angry", grip=(_L1 + 20, 59), tail_k=0.64))),
    key(11, **_lp(_L1 - 1, **dict(_LIMP, ang=46, crouch=3, lean=5, mouth="closed", glow=1, eyes="look", grip=(_L1 + 19, 54), twist=2, tail_k=0.62))),
    key(12, **_lp(_L1 - 5, lean=3, crouch=1, hdy=0, sway=0.5, tail_phase=3.4)),
    key(13, **_lp(_L0 + 2, lean=1, crouch=0, sway=0.5, tail_phase=3.7)),
]


def _leap_fx(i, p):
    hx, hy = LEAP_HIT
    gx, gy = p["grip"]
    crack = 0 if i < 8 else (1 if i == 8 else 2)
    out = [lambda cv, g: FX.wood_block(cv, hx + 3, FLOOR, 16, 11, crack=crack)]
    if i == 2:
        out.append(lambda cv, g: FX.fx_dust(cv, p["cx"] - 3, FLOOR - 1, 1, 0.8))              # debu tolakan
    if 6 <= i <= 7:                                             # dua frame smear sebelum tumbukan
        k = 7 - i
        out.append(lambda cv, g: FX.fx_smear(cv, gx, gy, 38, p["ang"] - 66, p["ang"] - 2, 2 if k < 2 else 1))
        out.append(lambda cv, g: FX.fx_smear(cv, gx, gy, 29, p["ang"] - 54, p["ang"] - 6, 1))
    if i == 7:
        out.append(lambda cv, g: FX.fx_dust(cv, p["cx"] + 2, FLOOR - 1, 0, 0.9))              # tiba di lantai
    if i >= 8:
        k = i - 8
        if k <= 4:
            out.insert(0, lambda cv, g: FX.fx_dust(cv, hx + 3, FLOOR - 1, min(k + 1, 2), 0.9))
        if k <= 2:
            out.insert(0, lambda cv, g: FX.fx_dust(cv, p["cx"] + 2, FLOOR - 1, min(k + 1, 3), 0.9))
        if k == 0:
            out.append(lambda cv, g: FX.fx_smear(cv, gx, gy, 34, -34, 40, 2))
            out.append(lambda cv, g: FX.fx_smear(cv, gx, gy, 26, -26, 34, 1))
            out.append(lambda cv, g: FX.fx_burst(cv, hx - 1, hy - 2, 8))
        elif k == 1:
            out.append(lambda cv, g: FX.fx_burst(cv, hx - 1, hy - 2, 4))
        if k <= 5:
            out.append(lambda cv, g: FX.fx_chips(cv, hx + 1, FLOOR - 10, k + 1, seed=5, n=10, power=1.1))
    return out


LEAP_TRACK = Track("attack-leap", 14, LEAP_KEYS, [140, 130, 60, 60, 120, 50, 40, 40, 260, 130, 110, 100, 100, 130], keyframe=8, fx=_leap_fx,
                   label="berjongkok, melompat dengan pedang terangkat, tebas turun dengan smear, mendarat dan menghantam balok kayu, pulih")

# ================================================================== miss (tebasan meleset: pedang menancap lantai di depan balok)
_MC = 53
MISS_TIP_X = 86.0


def _ms(**kw):
    d = rest(_MC, tail_k=0.64)
    d.update(kw)
    return d


MISS_KEYS = [
    key(0, **_ms()),
    key(1, **_ms(lean=-1, crouch=2, grip=(_MC + 30, 50), ang=50, sway=-0.5, tail_phase=1.0, eyes="angry")),
    key(2, **_ms(lean=-1, crouch=3, grip=(_MC + 31, 56), ang=-50, sway=-1.0, tail_phase=1.6, eyes="angry", hdy=1)),
    key(3, **_ms(lean=3, crouch=4, grip=(_MC + 24, 57), ang=-8, sway=2.0, tail_phase=2.0, eyes="angry", mouth="shout", twist=3)),
    key(4, **_ms(lean=9, crouch=5, grip=(_MC + 28, 58), ang=34, sway=4.0, tail_phase=2.3, eyes="angry", mouth="shout", twist=4)),
    key(5, **_ms(lean=14, crouch=7, fl=(-14, 0), fr=(15, 0), grip=(_MC + 21, 60), ang=62, sway=5.0, tail_phase=2.6, eyes="wide", mouth="closed", twist=5)),
    key(6, **_ms(cx=_MC + 2, lean=17, crouch=6, fl=(-14, 3), fr=(15, 0), grip=(_MC + 22, 60), ang=62, sway=6.0, tail_phase=2.8, eyes="wide", twist=6)),
    key(7, **_ms(cx=_MC + 1, lean=12, crouch=5, fl=(-12, 0), fr=(13, 0), grip=(_MC + 22, 60), ang=62, sway=3.0, tail_phase=3.0, eyes="dim", twist=3, hdx=1)),
    key(8, **_ms(lean=6, crouch=3, grip=(_MC + 26, 54), ang=70, sway=1.5, tail_phase=3.2, eyes="dim")),
    key(9, **_ms(lean=2, crouch=1, sway=0.5, tail_phase=3.5)),
]


def _miss_hit():
    sf = SwordFrame(_MC + 22, 60.0, 62.0)
    ux = (FLOOR - 60.0) / math.sin(math.radians(62.0))
    return sf.w(ux, 0)


MISS_HIT = _miss_hit()


def _miss_fx(i, p):
    hx, hy = MISS_HIT
    gx, gy = p["grip"]
    out = [lambda cv, g: FX.wood_block(cv, SMASH_HIT[0] + 3, FLOOR, 16, 11, crack=0)]
    if 3 <= i <= 4:
        out.append(lambda cv, g: FX.fx_smear(cv, gx, gy, 38, p["ang"] - 62, p["ang"] - 2, 2 if i == 4 else 1))
        out.append(lambda cv, g: FX.fx_smear(cv, gx, gy, 29, p["ang"] - 50, p["ang"] - 6, 1))
    if 5 <= i <= 7:
        k = i - 5
        out.insert(0, lambda cv, g: FX.fx_dust(cv, hx + 2, FLOOR - 1, min(k + 1, 3), 0.9))
        if i == 5:
            out.append(lambda cv, g: FX.fx_burst(cv, hx - 1, FLOOR - 4, 5))
            out.append(lambda cv, g: FX.fx_chips(cv, hx + 1, FLOOR - 8, 1, seed=11, n=6, power=0.8))
    if i in (6, 7):
        out.append(lambda cv, g: FX.fx_sweat(cv, int(g["head"][0]) + 22 + (i - 6) * 2, int(g["head"][1]) - 8 + (i - 6) * 4))
    if i == 8:
        out.append(lambda cv, g: FX.fx_dust(cv, hx + 2, FLOOR - 1, 3, 0.7))
    return out


MISS_TRACK = Track("miss", 10, MISS_KEYS, [140, 100, 130, 50, 40, 200, 220, 240, 140, 140], keyframe=6, fx=_miss_fx,
                   label="ayunan penuh tenaga, pedang menancap lantai di depan balok, kehilangan keseimbangan, malu lalu kembali siaga")

# ================================================================== exhaustion (kelelahan: bungkuk bertumpu pada pedang, napas berat)
_EC = 58
_E_CROUCH = [8, 7, 6, 6, 7, 8, 8, 7, 6, 6, 7, 8]            # dada naik-turun dua kali per putaran; frame 11 = frame 0
_E_HEAD = [5, 4, 3, 3, 4, 5, 5, 4, 3, 3, 4, 5]


def _exh_keys():
    keys = []
    for i in range(12):
        c, h = _E_CROUCH[i], _E_HEAD[i]
        d = dict(cx=_EC, lean=8, crouch=c, hdy=h, grip=(_EC + 29, 60 + (c - 6)), ang=84, lh=(_EC - 12, 76), eyes="tired", mouth="closed",
                 sway=-1.0 - (c - 6) * 0.5, tail_phase=0.5 + 2 * math.pi * i * 2 / 12.0, fl=(-8, 0), fr=(8, 0), tail_k=0.8, hdx=1)
        if i == 8:
            d.update(eyes="shut")
        keys.append((i, d))
    return keys


def _exh_fx(i, p):
    out = []
    g = R.geometry(p)
    hx, hy = int(g["head"][0]), int(g["head"][1])
    if i in (4, 5, 6):                                          # uap keluar saat hembus, dari grill di bawah visor
        out.append(lambda cv, g: FX.fx_breath(cv, hx + 14 + (i - 4) * 2, hy + 14 + (i - 4), i - 4))
    if i in (10, 11, 0):
        kk = 2 if i == 0 else i - 10
        out.append(lambda cv, g: FX.fx_breath(cv, hx + 14 + kk * 2, hy + 14 + kk, kk))
    k = i % 6                                                   # keringat pendingin menetes dari sisi helm
    if k < 5:
        out.append(lambda cv, g: FX.fx_sweat(cv, hx + 21, hy + 2 + k * 5))
    return out


EXH_TRACK = Track("exhaustion", 12, _exh_keys(), [200, 150, 150, 170, 220, 260, 220, 150, 90, 150, 170, 200], keyframe=5, fx=_exh_fx,
                  label="bungkuk bertumpu pada pedang, dada naik turun, visor redup, uap mengepul, keringat menetes")

# ================================================================== defeated (berlutut bertumpu pada pedang, tertunduk, bermartabat)
_DC = 52
_D_CROUCH = [10, 10, 9, 9, 9, 10, 10, 10, 9, 9, 9, 10, 10, 10]
_D_HEAD = [5, 5, 4, 4, 4, 5, 5, 5, 4, 4, 4, 5, 5, 5]
_D_EYES = ["tired", "tired", "tired", "tired", "dim", "dim", "dim", "dim", "dim", "dim", "shut", "dim", "shut", "shut"]


def _def_keys():
    keys = []
    for i in range(14):
        d = dict(cx=_DC, lean=8, crouch=_D_CROUCH[i], hdy=_D_HEAD[i], fl=(-17, 1), fr=(13, 0), toe_l=-1, legs_front=True,
                 grip=(_DC + 31, 70), ang=84, lh=(_DC - 12, 78), eyes=_D_EYES[i], mouth="closed", glow=0, hdx=1,
                 sway=-2.0 + 0.5 * (_D_CROUCH[i] - 9), tail_phase=0.3 + 2 * math.pi * i / 14.0, tail_k=0.8)
        keys.append((i, d))
    return keys


def _def_fx(i, p):
    out = []
    g = R.geometry(p)
    hx, hy = int(g["head"][0]), int(g["head"][1])
    if i in (4, 5, 6):
        out.append(lambda cv, g: FX.fx_breath(cv, hx + 14 + (i - 4) * 2, hy + 14 + (i - 4), i - 4))
    k = (i - 9) % 14
    if k < 5:
        out.append(lambda cv, g: FX.fx_sweat(cv, hx + 21, hy + 2 + k * 5))
    return out


DEF_TRACK = Track("defeated", 14, _def_keys(), [200, 180, 180, 200, 200, 220, 200, 160, 120, 180, 200, 200, 200, 200], keyframe=3, fx=_def_fx,
                  label="berlutut bertumpu pada pedang yang menancap, kepala tertunduk, visor meredup, napas pelan; bermartabat")


# ================================================================== victory (tidak loop): topeng buka-tutup memperlihatkan wajah Gobyet, pedang ditusuk ke tanah, kaki naik batu, usap darah monster
_VC = 56
ROCK_X, ROCK_W, ROCK_H = _VC + 19, 20, 10          # batu berpuncak rata (FX.ROCK_TOP) di depan kaki kanan
_ROCK = (lambda cv: FX.rock(cv, ROCK_X, FLOOR, ROCK_W, ROCK_H),)
_XS = _VC + 36                                    # sumbu mendatar pedang yang tertancap (di kanan batu)
_PLANT = dict(grip=(_XS, 48), ang=88)
_ON_ROCK = (15, ROCK_H)                           # kaki kanan di puncak rata batu (sol tepat di atas batu)
_WIPE = (7, 11, 15, 20, 26)                       # depan usapan (u bilah) di lima frame usap; tangan sedikit di depannya


def _vk(**kw):
    d = rest(_VC, tail_k=0.55, props=_ROCK, stain_u=0, grip=(_XS, 47), ang=86, lh=(_VC - 12, 74), lean=3)
    d.update(kw)
    return d


def _wipe(u, **kw):
    """Frame usap: kaki di batu, badan condong di atas lutut, kepalan kanan di sisi kiri bilah tepat di depan batas noda."""
    d = dict(legs_front=True, eyes="look", crouch=2, lean=8, grip=_PLANT["grip"], ang=_PLANT["ang"], rh=(_XS - 7, 48 + u + 2), fr=_ON_ROCK, hdy=2,
             stain_u=u, sway=-0.5)
    d.update(kw)
    return _vk(**d)


_SMIRK, _SMILE = ("look", "flat", "smirk"), ("look", "flat", "smile")
VICT_KEYS = [
    key(0, **_vk()),
    key(1, **_vk(mask=0.25, face=_SMIRK)),
    key(2, **_vk(mask=0.625, hdy=-1, face=_SMIRK)),
    key(3, **_vk(mask=1.0, hdy=-1, hdx=1, sway=0.5, face=_SMIRK)),
    key(4, **_vk(mask=1.0, hdy=-1, hdx=1, sway=0.5, face=_SMILE)),
    key(5, **_vk(mask=0.625, hdx=1, face=_SMIRK)),
    key(6, **_vk(mask=0.25, hdx=1, face=_SMIRK)),
    key(7, **_vk(mask=0.0, eyes="wide", tail_phase=1.7)),
    key(8, **_vk(eyes="angry", crouch=1, lean=1, grip=(_XS - 3, 42), ang=60, sway=-1.0, tail_phase=1.9)),
    key(9, **_vk(eyes="angry", crouch=3, lean=0, grip=(_XS - 6, 40), ang=-44, sway=-2.0, tail_phase=2.1, hdy=1)),
    key(10, **_vk(eyes="angry", mouth="shout", crouch=4, lean=5, grip=(_XS - 3, 46), ang=70, sway=3.0, tail_phase=2.3, twist=3)),
    key(11, **_vk(eyes="rage", crouch=4, lean=6, grip=_PLANT["grip"], ang=_PLANT["ang"], sway=3.0, tail_phase=2.5, twist=4, glow=2, hdy=1)),
    key(12, **_vk(legs_front=True, eyes="look", crouch=4, lean=6, grip=_PLANT["grip"], ang=_PLANT["ang"], rh=(_XS - 4, 49), fr=(10, 5), sway=0.5,
                  tail_phase=2.8, hdy=1)),
    key(13, **_vk(legs_front=True, eyes="look", crouch=2, lean=8, grip=_PLANT["grip"], ang=_PLANT["ang"], rh=(_XS - 6, 53), fr=_ON_ROCK, hdy=2, sway=-0.5,
                  tail_phase=3.1)),
    key(14, **_wipe(_WIPE[0], tail_phase=3.1)),
    key(15, **_wipe(_WIPE[1], tail_phase=3.1)),
    key(16, **_wipe(_WIPE[2], tail_phase=3.1)),
    key(17, **_wipe(_WIPE[3], tail_phase=3.1)),
    key(18, **_wipe(_WIPE[4], tail_phase=3.1, eyes="wide", glow=2)),
    key(19, **_vk(legs_front=True, eyes="look", crouch=2, lean=6, grip=_PLANT["grip"], ang=_PLANT["ang"], rh=(_XS - 3, 47), fr=_ON_ROCK, hdy=1, hdx=1,
                  stain_u=60, sway=1.0, tail_phase=3.1, glow=1)),
]


def _vict_fx(i, p):
    out = []
    g = R.geometry(p)
    hx, hy = int(g["head"][0]), int(g["head"][1])
    gx, gy = p["grip"]
    sf = SwordFrame(gx, gy, p["ang"])
    if 2 <= i <= 6:                                             # uap keluar dari celah pintu topeng saat membuka dan menutup
        k = (0, 0, 1, 2, 3, 3, 2)[i]
        out.append(lambda cv, g: FX.fx_steam(cv, hx - 15, hy + 6, k))
        out.append(lambda cv, g: FX.fx_steam(cv, hx + 15, hy + 6, k))
    if i == 7:                                                  # klik: percikan di tengah pelat saat topeng tertutup
        out.append(lambda cv, g: FX.fx_burst(cv, hx, hy + 3, 4))
    if i == 10:                                                 # sapuan menukik
        out.append(lambda cv, g: FX.fx_smear(cv, gx - 6, gy + 2, 38, p["ang"] - 62, p["ang"] - 2, 2))
    if i >= 11:                                                 # ujung bilah masuk tanah: debu dan retakan di titik tusuk
        k = min(i - 11, 3)
        tx = sf.w(40.0, 0)[0]
        if i <= 13:
            out.append(lambda cv, g: FX.fx_dust(cv, int(tx), FLOOR - 1, k, 0.9))
        if i == 11:
            out.append(lambda cv, g: FX.fx_chips(cv, int(tx), FLOOR - 4, 1, seed=7, n=7, power=0.8))
            out.append(lambda cv, g: FX.fx_burst(cv, int(tx), FLOOR - 6, 4))
            out.append(lambda cv, g: FX.fx_ichor_drip(cv, int(tx) - 13, gy + 20, 0))
            out.append(lambda cv, g: FX.fx_ichor_drip(cv, int(tx) + 13, gy + 14, 1))
    if i in (15, 16):                                           # tetesan darah jatuh dari sisi bilah ke lantai saat diusap
        out.append(lambda cv, g: FX.fx_ichor_drip(cv, int(sf.w(30.0, 0)[0]) + 12, int(gy) + 26 + (i - 15) * 8, 1 + (i - 15) * 2))
    if i == 18:
        out.append(lambda cv, g: FX.fx_glint(cv, int(sf.w(14.0, 0)[0]) - 4, int(gy) + 14, 0))
    if i == 19:
        out.append(lambda cv, g: FX.fx_glint(cv, int(sf.w(14.0, 0)[0]) - 4, int(gy) + 14, 1))
        out.append(lambda cv, g: FX.fx_glint(cv, int(sf.w(28.0, 0)[0]) + 4, int(gy) + 29, 2))
    return out


VICT_TRACK = Track("victory", 20, VICT_KEYS, [160, 100, 100, 150, 350, 100, 80, 140, 100, 70, 60, 200, 140, 160, 110, 110, 110, 110, 130, 1500],
                   keyframe=16, loop=False, fx=_vict_fx,
                   label="topeng membuka memperlihatkan wajah Gobyet yang tersenyum lalu menutup, pedang dicabut lalu ditusukkan ke tanah, satu kaki naik ke batu sambil tangan mengusap darah monster sepanjang bilah, bilah bersih berkilau")

TRACKS = {t.name: t for t in (IDLE_TRACK, RUN_TRACK, RAGE_TRACK, LEAP_TRACK, SMASH_TRACK, MISS_TRACK, EXH_TRACK, DEF_TRACK, VICT_TRACK)}


# ================================================================== daftar adegan dan metadata
def _scene(t):
    return (lambda i, t=t: t.frame(i), t.n, lambda i, t=t: t.duration(i))


SCENES = {"%s-%s" % (COSTUME, name): _scene(t) for name, t in TRACKS.items()}
META = {name: {"frames": t.n, "keyframe": t.keyframe, "loop": t.loop, "label": t.label} for name, t in TRACKS.items()}
