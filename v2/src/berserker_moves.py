"""State animasi Berserker (lihat berserker.py).

Tempo tidak rata (durs per frame, kelipatan 10 ms): ancang-ancang lambat, lepas cepat, putaran sangat cepat,
frame hantam ditahan, pemulihan berat. Event per frame (hit, hitstop, screen_shake, vfx) dibaca mesin; VFX
non-darah sudah ikut di lapisan VFX sheet (baked), darah dimunculkan mesin hanya saat kena.

Konvensi pose: rh/lh relatif ke pusat badan, rwa = arah pedang (0 kanan, 90 bawah, -90 atas).
two=True mengunci tangan kiri ke gagang (berserker.post_pose).
"""
import math

import rig2 as R
import vfx2 as V
import char2
from rig2 import wag, BASE, RX
from berserker import TIP, sword_point

FL = BASE  # efek tidak menembus lantai
FLOOR_Y = BASE - 1

# ------------------------------------------------------------------ pose dasar
SWORD = dict(rw="slab_sword", two=True)
IDLE = dict(SWORD, sx=6, crouch=3, lean=4, hdy=1, rh=(10, -3), rwa=20, arm0_behind=True,
            eyes="look", brows="angry", mouth="frown")
READY = dict(SWORD, sx=7, crouch=4, lean=3, hdy=0, rh=(7, -3), re=(12, 1), rwa=-150, rw_back=True,
             eyes="angry", brows="angry", mouth="flat")
WIND = dict(READY, rh=(4, -5), re=(11, -1), rwa=-170, lean=-1, crouch=5, sx=8)
OVER = dict(SWORD, sx=7, crouch=3, lean=0, rh=(3, -13), rwa=-95, rw_back=True, arms_behind_head=True,
            eyes="angry", brows="angry", mouth="shout")
SLAM = dict(SWORD, sx=8, crouch=6, lean=5, hdy=1, rh=(13, 2), rwa=30, arm0_behind=True,
            eyes="angry", brows="angry", mouth="shout")
TUCK = dict(SWORD, crouch=3, lean=2, sx=4, lift_l=5, lift_r=5, rh=(10, -8), rwa=-45, cloak_lift=3,
            eyes="angry", brows="angry", mouth="shout")

# Nama state dari brief (berserker_*) -> nama state di registry
BRIEF_NAMES = {
    "berserker_idle": "idle", "berserker_ready": "ready", "berserker_rage": "rage", "berserker_run": "run",
    "berserker_jump": "jump", "berserker_attack": "attack", "berserker_heavy_attack": "heavy_attack",
    "berserker_leap_spin_slash": "leap_spin_slash", "berserker_overhead_smash": "overhead_smash",
    "berserker_air_slash": "air_slash", "berserker_rage_attack": "rage_attack", "berserker_combo": "combo",
    "berserker_hit": "hit", "berserker_miss": "miss", "berserker_exhausted": "exhausted",
    "berserker_victory": "victory", "berserker_defeat": "defeat",
}


# ------------------------------------------------------------------ alat bantu
def P(base, **kw):
    d = dict(base)
    d.update(kw)
    return d


def seq(poses, extra=None):
    """State dari daftar pose per frame (kontrol penuh), extra(t, p) menambah efek."""
    def fn(t):
        p = dict(poses[t])
        p.setdefault("tail", wag(t, len(poses)))
        p.setdefault("cape", wag(t, len(poses)))
        if extra:
            extra(t, p)
        return p
    return fn


def geo_of(ch, p):
    q = R.pose()
    q.update(p)
    char2.quantize(q)
    ch.post_pose(q)
    return R.Geo(q, ch.body), q


def rel(x, y):
    """Titik dunia -> relatif jangkar (x kanan, y ke bawah, 0 = lantai)."""
    return int(round(x - RX)), int(round(y - BASE))


def floor_hit_x(g, ang):
    """Titik bilah menyentuh lantai (x dunia), atau ujung pedang bila tidak menyentuh."""
    hx, hy = g.hand[1]
    a = math.radians(ang)
    if math.sin(a) > 0.05:
        u = min(TIP, (FLOOR_Y - hy) / math.sin(a))
        return hx + u * math.cos(a)
    return sword_point(g.hand[1], ang, TIP)[0]


# ------------------------------------------------------------------ efek (closure cv, g)
def fx_trail(a0, a1, k=0, r_in=22, r_out=None, pivot=None):
    def f(cv, g):
        c = pivot(g) if pivot else g.hand[1]
        V.sword_trail(cv, c, a0, a1, r_in, r_out or TIP + 1, k=k, floor=FL)
    return f


def fx_cres(a0, a1, r, thick, k=0, flat=1.0, pivot=None, dx=0, dy=0):
    def f(cv, g):
        c = pivot(g) if pivot else (g.tcx + dx, g.tcy + dy)
        V.crescent(cv, c[0], c[1], r, a0, a1, thick, k=k, flat=flat, floor=FL)
    return f


def at_floor(fn):
    """fn(cv, x) menggambar di titik bilah menyentuh lantai."""
    def f(cv, g):
        fn(cv, floor_hit_x(g, g.p["rwa"]))
    return f


def fx_ground(k, size=1.0, seed=9):
    return at_floor(lambda cv, x: V.ground_impact(cv, int(round(x)), FLOOR_Y, k, size=size, floor=FL, seed=seed))


def fx_debris(k, seed=11, n=8, power=1.0):
    return at_floor(lambda cv, x: V.debris(cv, int(round(x)), FLOOR_Y, k, seed=seed, n=n, power=power, floor=FL))


def fx_dust_feet(k, size=1.0):
    return lambda cv, g: V.dust(cv, int(round(g.cx)), FLOOR_Y, k, size=size, floor=FL)


def fx_dust_x(x, k, size=1.0, seed=0):
    return lambda cv, g: V.dust(cv, int(x), FLOOR_Y, k, size=size, seed=seed, floor=FL)


def fx_dust_at(k, size=0.8, seed=0):
    return at_floor(lambda cv, x: V.dust(cv, int(round(x)), FLOOR_Y, k, size=size, seed=seed, floor=FL))


def fx_tip_sparks(k, seed=0, direction=-150):
    def f(cv, g):
        x, y = sword_point(g.hand[1], g.p["rwa"], TIP - 1)
        V.sparks(cv, int(round(x)), min(int(round(y)), FLOOR_Y - 1), k, seed=seed, n=5, direction=direction, floor=FL)
    return f


def fx_impact_tip(k, size=1.0, u=None):
    def f(cv, g):
        x, y = sword_point(g.hand[1], g.p["rwa"], u if u is not None else TIP - 4)
        V.impact(cv, int(round(x)), min(int(round(y)), FLOOR_Y - 3), k, size=size, floor=FL)
    return f


def fx_lines(k, r0=12, r1=24):
    def f(cv, g):
        x = floor_hit_x(g, g.p["rwa"])
        V.impact_lines(cv, int(round(x)), FLOOR_Y - 6, k, r0=r0, r1=r1, floor=FL)
    return f


def fx_embers(k, seed=0):
    return lambda cv, g: V.embers(cv, int(round(g.tcx)), int(round(g.tcy + 6)), k, seed=seed, n=9, spread=13,
                                  height=30, floor=FL)


def fx_roar(k):
    def f(cv, g):
        hx, hy = g.ihead()
        V.roar_lines(cv, hx + 9, hy + 5, k, floor=FL)
    return f


def fx_sweat(dx=11, dy=-6):
    def f(cv, g):
        hx, hy = g.ihead()
        V.sweat_drop(cv, hx + dx, hy + dy)
    return f


def fx_breath(k):
    def f(cv, g):
        hx, hy = g.ihead()
        V.breath_puff(cv, hx + 8, hy + 6, k)
    return f


def fx_speed(dx=-16, dy=0, n=4, length=12):
    return lambda cv, g: V.speed_lines(cv, int(round(g.tcx + dx)), int(round(g.tcy + dy)), n=n, length=length,
                                       direction=-1, floor=FL)


def fx_mark(glyph, dx=8, dy=-15):
    def f(cv, g):
        hx, hy = g.ihead()
        R.mark_bubble(cv, hx + dx, hy + dy, glyph)
    return f


def fx_rim(k):
    """Aura amuk tipis: titik merah redup di sekeliling kepala dan bahu, terputus-putus."""
    def f(cv, g):
        hx, hy = g.ihead()
        pts = set()
        for j in range(30):
            a = j * math.tau / 30
            pts.add((int(round(hx + math.cos(a) * 16.5)), int(round(hy + 3 + math.sin(a) * 13))))
        V.rage_rim(cv, pts, k)
    return f


def add_fx(p, *fs, back=False):
    key = "fx_back" if back else "fx"
    p[key] = list(p.get(key, [])) + list(fs)


# ------------------------------------------------------------------ pembuat state
def add(ch, name, poses, durs, extra=None, loop=False, hold=0, label="", core=None, events=None, variant_of=None):
    assert len(durs) == len(poses), (name, len(durs), len(poses))
    ch.add(name, len(poses), seq(poses, extra), ms=durs[0], loop=loop, hold=hold, label=label, core=core, durs=durs,
           events=events or [], variant_of=variant_of)


def hit_events(ch, poses, frame, hitstop=70, shake=None, u=TIP * 0.7, direction=20, ground=None, extra=None,
               blood=("blood_small", "blood_medium", "blood_burst")):
    """Event serangan kena di frame: titik kena di bilah (relatif jangkar), arah ayunan untuk darah."""
    g, q = geo_of(ch, poses[frame])
    x, y = sword_point(g.hand[1], q["rwa"], u)
    y = min(y, FLOOR_Y - 14)  # titik kena setinggi badan target (Gobyet standar), bukan di kaki
    hx, hy = rel(x, y)
    ev = [{"frame": frame, "type": "hit", "x": hx, "y": hy, "direction": direction,
           "blood": {"1": blood[0], "2": blood[1], "3": blood[2]}},
          {"frame": frame, "type": "hitstop", "ms": hitstop}]
    if shake:
        ev.append({"frame": frame, "type": "screen_shake", "px": shake[0], "ms": shake[1]})
    if ground:
        gx = floor_hit_x(g, q["rwa"])
        ev.append({"frame": frame, "type": "vfx", "name": ground, "x": rel(gx, FLOOR_Y)[0], "y": 0, "baked": True})
    return ev + (extra or [])


def spin_ref(ch, pose):
    """Sudut dan jari-jari ujung pedang relatif pusat badan (untuk jejak salto)."""
    g, q = geo_of(ch, pose)
    tx, ty = sword_point(g.hand[1], q["rwa"], TIP)
    return math.degrees(math.atan2(ty - g.tcy, tx - g.tcx)), math.hypot(tx - g.tcx, ty - g.tcy)


def piv(g):
    return (int(round(g.tcx)), int(round(g.tcy)))


# ------------------------------------------------------------------ state
def build_states(ch):
    _idle_family(ch)
    _locomotion(ch)
    _attacks(ch)
    _signature(ch)
    _specials(ch)
    _reactions(ch)


def _idle_family(ch):
    # idle F0-F4: napas halus, pedang tetap bertumpu di lantai (tangan dikompensasi saat badan naik turun)
    poses = [P(IDLE), P(IDLE, crouch=2, rh=(10, -2)), P(IDLE, crouch=2, rh=(10, -2), hdy=0), P(IDLE, crouch=3),
             P(IDLE, crouch=4, rh=(10, -4), hdy=2)]
    add(ch, "idle", poses, [220, 170, 200, 160, 190], loop=True, core="idle",
        label="jongkok condong ke depan, ujung pedang raksasa bertumpu di lantai, kepala sedikit menunduk")

    poses = [P(IDLE), P(IDLE, crouch=2, rh=(10, -2)), P(IDLE, crouch=1, rh=(10, -1), hdy=0),
             P(IDLE, crouch=1, rh=(10, -1), hdy=0, mouth="o"), P(IDLE, crouch=3, mouth="o"),
             P(IDLE, crouch=4, rh=(10, -4), hdy=2), P(IDLE, crouch=4, rh=(10, -4), hdy=2), P(IDLE)]

    def breath(t, p):
        if 3 <= t <= 5:
            add_fx(p, fx_breath(t - 3))
    add(ch, "idle_breath", poses, [200, 160, 160, 220, 120, 140, 160, 180], extra=breath, loop=True,
        label="napas dalam, uap napas keluar", variant_of="idle")

    loose = P(IDLE, two=False, lh=(1, 0), arm0_behind=True)
    poses = [P(IDLE), P(IDLE, two=False, lh=(3, -2)), loose, P(loose, lh=(0, -1), eyes="down"),
             P(loose, lh=(1, -1), eyes="down"), P(IDLE, two=False, lh=(3, -3)), P(IDLE, rwa=25), P(IDLE)]
    add(ch, "idle_grip", poses, [200, 90, 140, 160, 120, 90, 120, 180], loop=True,
        label="melepas tangan kiri, meregangkan jari, menggenggam ulang", variant_of="idle")

    poses = [P(IDLE), P(IDLE, rh=(8, -3), lean=3), P(IDLE, rh=(6, -3), lean=2, dx=-1),
             P(IDLE, rh=(5, -3), lean=2, dx=-1), P(IDLE, rh=(5, -3), lean=2, dx=-1, eyes="down"),
             P(IDLE, rh=(7, -3), lean=3), P(IDLE, rh=(9, -3), lean=4), P(IDLE, rh=(10, -3)), P(IDLE), P(IDLE)]

    def drag(t, p):
        if t in (2, 3, 6):
            add_fx(p, fx_tip_sparks(t % 3, seed=t, direction=-160 if t < 5 else -30))
        if t in (2, 3, 4):
            add_fx(p, fx_dust_at(t - 2, 0.6, seed=t))
        if t in (6, 7):
            add_fx(p, fx_dust_at(t - 6, 0.6, seed=t))
    add(ch, "idle_drag", poses, [200, 140, 120, 120, 200, 120, 120, 140, 160, 200], extra=drag, loop=True,
        label="menyeret ujung pedang di lantai lalu mendorongnya kembali", variant_of="idle")

    poses = [P(IDLE), P(IDLE, eyes="left"), P(IDLE, eyes="left", hdx=-1), P(IDLE, eyes="left", hdx=-1),
             P(IDLE, eyes="look", hdx=0), P(IDLE, eyes="side", hdx=1), P(IDLE, eyes="side", hdx=1, brows="flat"),
             P(IDLE, eyes="side", hdx=1), P(IDLE, eyes="look"), P(IDLE, eyes="blink")]
    add(ch, "idle_look", poses, [220, 140, 200, 260, 100, 140, 240, 180, 160, 80], loop=True,
        label="menoleh ke belakang, lalu menatap ke depan", variant_of="idle")

    poses = [P(IDLE), P(IDLE, crouch=2, hdy=-1, rh=(10, -2), eyes="wide", brows="up"), P(IDLE, crouch=4, hdy=2, rh=(10, -4)),
             P(IDLE, eyes="angry"), P(IDLE, crouch=2, hdy=0, rh=(10, -2), eyes="angry"), P(IDLE)]
    add(ch, "idle_twitch", poses, [260, 50, 70, 200, 60, 220], loop=True,
        label="bahu berkedut, mata melotot sesaat", variant_of="idle")


def _locomotion(ch):
    poses = [P(READY), P(READY, crouch=5, rh=(7, -2)), P(READY, crouch=5, rh=(7, -2), hdy=1), P(READY),
             P(READY, crouch=3, rh=(7, -4), hdy=-1), P(READY, crouch=3, rh=(7, -4))]
    add(ch, "ready", poses, [120, 110, 120, 110, 120, 110], loop=True, label="pedang terkokang di bahu, kuda-kuda lebar")

    # run: rendah, pedang diseret di tangan kiri (belakang), ujung menggores lantai
    base = dict(sx=5, crouch=4, lean=6, hdy=1, eyes="angry", brows="angry", mouth="flat", cloak_lift=3,
                rw=None, two=False, lw="slab_sword", lwa=175, lw_back=True, lh=(-9, 3), arm0_behind=True)
    poses = []
    for k in range(8):
        a = k * math.tau / 8
        poses.append(P(base, fx_r=round(math.cos(a) * 4), fx_l=round(-math.cos(a) * 4),
                       lift_r=round(max(0.0, math.sin(a)) * 4), lift_l=round(max(0.0, -math.sin(a)) * 4),
                       dy=-1 if k % 4 in (1, 2) else 0, rh=(9 + round(math.cos(a) * 3), -round(math.cos(a) * 2)),
                       lh=(-9, 3 + (k % 2))))

    def run_fx(t, p):
        add_fx(p, lambda cv, g, t=t: V.sparks(cv, int(round(sword_point(g.hand[0], g.p["lwa"], TIP)[0])), FLOOR_Y - 1,
                                              t % 3, seed=t, n=4, direction=-30, floor=FL))
        if t % 4 == 0:
            add_fx(p, lambda cv, g: V.dust(cv, int(round(g.feet[0][0])), FLOOR_Y, 1, size=0.6, floor=FL))
        add_fx(p, fx_speed(dx=-21, dy=-12, n=3, length=7), back=True)
    add(ch, "run", poses, [80] * 8, extra=run_fx, loop=True, label="lari rendah, pedang raksasa diseret menggores lantai")

    j = P(READY, crouch=1, lift_l=4, lift_r=4, cloak_lift=4)
    poses = [P(READY), P(READY, crouch=7, sx=8, hdy=1), P(READY, crouch=0, dy=-10, sx=5, lift_l=2, lift_r=1),
             P(j, dy=-20), P(j, dy=-25, rh=(8, -6), rwa=-135), P(j, dy=-26, rh=(8, -6), rwa=-135), P(j, dy=-19),
             P(j, dy=-8, lift_l=1, lift_r=1), P(READY, crouch=8, sx=8, hdy=2), P(READY, crouch=5)]

    def jump_fx(t, p):
        if t in (2, 3):
            add_fx(p, fx_dust_x(RX, t - 2, 1.0))
        if t in (8, 9):
            add_fx(p, fx_dust_feet(t - 8, 1.2))
    add(ch, "jump", poses, [120, 160, 50, 60, 80, 110, 70, 50, 140, 140], extra=jump_fx,
        label="ancang-ancang berat, melompat dengan pedang di bahu, mendarat berdebu",
        events=[{"frame": 8, "type": "screen_shake", "px": 1, "ms": 80}])


def _attacks(ch):
    # attack: tebasan diagonal dari bahu, berakhir di pose istirahat (ujung di lantai)
    poses = [P(IDLE), P(READY, rwa=-70, rh=(9, -6), re=None), P(READY), P(WIND),
             P(READY, rh=(11, -10), re=None, rwa=-85, lean=2, mouth="shout", rw_back=False),
             P(SLAM, rh=(14, -3), rwa=-15, crouch=4), P(SLAM), P(SLAM, crouch=7, mouth="flat"),
             P(SLAM, crouch=6, mouth="flat", eyes="look"), P(IDLE, crouch=5), P(IDLE, crouch=4), P(IDLE)]

    def atk(t, p):
        if t == 4:
            add_fx(p, fx_trail(-170, -85), back=True)
        if t == 5:
            add_fx(p, fx_trail(-140, -15), back=True)
        if t in (6, 7, 8):
            add_fx(p, fx_trail(-110, 30, k=t - 6), back=True)
        if t in (6, 7):
            add_fx(p, fx_impact_tip(t - 6, 0.8))
        if t in (6, 7, 8, 9):
            add_fx(p, fx_dust_at(t - 6, 0.8))
    add(ch, "attack", poses, [80, 80, 110, 160, 40, 40, 130, 90, 90, 90, 100, 120], extra=atk, core="attack",
        label="tebasan diagonal dari bahu: ancang-ancang lambat, ayunan cepat, hantam ke depan",
        events=hit_events(ch, poses, 6, hitstop=60, shake=(1, 80)))

    low_back = P(SWORD, sx=8, crouch=5, lean=-2, rh=(-3, 2), rwa=175, rw_back=True, arm0_behind=True,
                 eyes="angry", brows="angry", mouth="flat")
    poses = [P(IDLE), P(IDLE, rh=(6, 0), rwa=60, crouch=4), P(low_back, rwa=165, rh=(1, 0)), low_back,
             P(low_back, rh=(4, 1), rwa=-170, lean=1, mouth="shout"),
             P(SLAM, rh=(14, -4), rwa=-5, crouch=4, mouth="shout"),
             P(SLAM, rh=(13, -7), rwa=-35, crouch=4), P(SLAM, rh=(11, -8), rwa=-55, crouch=4, mouth="flat"),
             P(READY, crouch=5), P(READY, rwa=-90, rh=(9, -6), re=None), P(IDLE, crouch=4), P(IDLE)]

    def atk_b(t, p):
        if t == 4:
            add_fx(p, fx_cres(160, 200, 30, 9, flat=0.4, dy=2), back=True)
        if t in (5, 6, 7):
            add_fx(p, fx_cres(150, 345 if t == 5 else 330, 46, 12, k=t - 5, flat=0.42, dy=-2), back=True)
    add(ch, "attack_b", poses, [80, 90, 120, 160, 50, 40, 120, 90, 100, 90, 100, 120], extra=atk_b,
        label="sapuan mendatar dari belakang ke depan", variant_of="attack",
        events=hit_events(ch, poses, 5, hitstop=60, u=TIP * 0.8, direction=0))

    poses = [P(IDLE), P(READY, rwa=-80, rh=(8, -8), re=None, crouch=4), P(OVER, rwa=-120), P(OVER, rwa=-150, lean=-2),
             P(OVER, rwa=-160, lean=-3, crouch=4, rh=(2, -12)), P(OVER, rwa=-160, lean=-3, crouch=5, rh=(2, -12), dx=1),
             P(READY, rh=(10, -12), re=None, rwa=-80, rw_back=False, lean=3, dx=3, sx=9, mouth="shout"),
             P(SLAM, rwa=35, dx=4, sx=9, crouch=7), P(SLAM, rwa=35, dx=4, sx=9, crouch=8, mouth="flat"),
             P(SLAM, rwa=35, dx=4, sx=9, crouch=7, mouth="flat"),
             P(SLAM, rwa=30, dx=4, sx=9, crouch=6, mouth="flat", eyes="look"),
             P(SLAM, rwa=25, dx=3, crouch=6, mouth="frown", eyes="look"), P(IDLE, dx=2, crouch=5), P(IDLE, dx=1, crouch=4),
             P(IDLE, crouch=3), P(IDLE)]

    def heavy(t, p):
        if t == 6:
            add_fx(p, fx_trail(-165, -80), back=True)
        if 7 <= t <= 11:
            k = t - 7
            if k <= 2:
                add_fx(p, fx_trail(-120, 35, k=k), back=True)
            add_fx(p, fx_ground(k, 1.1), back=True)
            add_fx(p, fx_debris(k, seed=21))
        if t == 7:
            add_fx(p, fx_lines(0))
    add(ch, "heavy_attack", poses, [80, 100, 130, 150, 180, 160, 40, 150, 90, 90, 100, 100, 100, 100, 100, 120],
        extra=heavy, label="pedang di atas kepala, langkah maju, menghantam tanah (retak, puing)",
        events=hit_events(ch, poses, 7, hitstop=90, shake=(3, 200), ground="ground_impact",
                          extra=[{"frame": 7, "type": "vfx", "name": "debris", "baked": True}]))

    up = P(OVER, rwa=-95, rh=(4, -14), mouth="flat")
    stuck = P(SLAM, rh=(13, -5), rwa=65, crouch=6, lean=4, sx=9)
    poses = [P(IDLE), P(READY, rwa=-100, rh=(8, -8), re=None), P(up, rwa=-100, crouch=2), P(up, crouch=1, lean=-1),
             P(up, crouch=2, lean=-2, mouth="shout"), P(up, crouch=3, lean=-2, mouth="shout", dx=-1),
             P(READY, rh=(12, -10), re=None, rwa=-40, rw_back=False, mouth="shout", crouch=5),
             stuck, P(stuck, crouch=7, rh=(13, -6), mouth="flat"), P(stuck, mouth="flat"), P(stuck, mouth="flat", eyes="look"),
             P(stuck, lean=2, rh=(13, -6), mouth="shout"), P(SLAM, rh=(13, -2), rwa=40, crouch=6, lean=1),
             P(IDLE, crouch=5, rwa=30), P(IDLE, crouch=4), P(IDLE), P(IDLE), P(IDLE)]

    def smash(t, p):
        if t == 6:
            add_fx(p, fx_trail(-100, -40), back=True)
        if 7 <= t <= 13:
            k = t - 7
            if k <= 2:
                add_fx(p, fx_trail(-95, 55, k=k), back=True)
            add_fx(p, fx_ground(k, 1.3, seed=31), back=True)
            add_fx(p, fx_debris(k, seed=33, n=10, power=1.2))
        if t == 7:
            add_fx(p, fx_lines(0, 14, 28))
        if t == 8:
            add_fx(p, fx_lines(1, 14, 28))
    add(ch, "overhead_smash", poses,
        [80, 100, 140, 160, 200, 180, 40, 170, 100, 100, 110, 110, 100, 100, 100, 110, 120, 140], extra=smash,
        label="pedang tegak di atas kepala, ditahan, dibanting lurus ke bawah",
        events=hit_events(ch, poses, 7, hitstop=100, shake=(4, 240), u=TIP * 0.35, direction=90, ground="ground_impact"))

    a = P(READY, crouch=1, lift_l=4, lift_r=4, cloak_lift=4)
    poses = [P(IDLE), P(READY, crouch=7, sx=8), P(a, dy=-12, crouch=0, lift_l=1, lift_r=1), P(a, dy=-22, rwa=-165, rh=(4, -5)),
             P(a, dy=-26, rwa=-170, rh=(3, -6), lean=-2),
             P(a, dy=-27, rh=(13, -6), re=None, rwa=-20, rw_back=False, lean=4, mouth="shout"),
             P(a, dy=-25, rh=(13, 0), re=None, rwa=35, rw_back=False, lean=5, arm0_behind=True, mouth="shout"),
             P(a, dy=-17, rh=(12, 1), re=None, rwa=45, rw_back=False, lean=4, arm0_behind=True),
             P(a, dy=-7, rh=(12, 0), re=None, rwa=40, rw_back=False, lean=3, arm0_behind=True, lift_l=1, lift_r=1),
             P(SLAM, crouch=8, rwa=25), P(SLAM, crouch=7, rwa=25, mouth="flat"), P(IDLE, crouch=5), P(IDLE, crouch=4), P(IDLE)]

    def air(t, p):
        if t == 2:
            add_fx(p, fx_dust_x(RX, 0, 1.0))
        if t == 5:
            add_fx(p, fx_trail(-170, -20), back=True)
        if t in (6, 7, 8):
            add_fx(p, fx_cres(-160, 50, 44, 13, k=t - 6, dx=4, dy=-6), back=True)
        if t in (9, 10):
            add_fx(p, fx_dust_feet(t - 9, 1.2))
    add(ch, "air_slash", poses, [80, 150, 50, 60, 90, 40, 70, 60, 50, 130, 100, 100, 100, 120], extra=air,
        label="melompat, tebasan bulan sabit di udara, mendarat berat",
        events=hit_events(ch, poses, 6, hitstop=70, direction=40))


def _signature(ch):
    """leap_spin_slash: jongkok -> isi tenaga -> melompat -> salto -> tebasan 360 -> hantaman -> pulih.
    Frame 0-3 ancang-ancang (lambat), 4-6 isi tenaga, 7-10 lompat (cepat), 11-14 salto (sangat cepat, figur
    diputar 90 derajat per frame, piksel utuh), 15 hantaman (ditahan), 16-18 debu dan puing, 19-22 pulih."""
    c0 = P(READY, crouch=5)
    charge = P(WIND, crouch=8, sx=9, lean=-2, mouth="shout", eyes="angry")
    poses = [P(IDLE), c0, P(c0, crouch=7, sx=8, hdy=1), P(c0, crouch=8, sx=9, hdy=2, dx=-1),
             P(charge), P(charge, crouch=9, dx=-1), P(charge, crouch=9, dx=-2, lean=-3),
             P(TUCK, dy=-12, dx=4, crouch=0, lift_l=1, lift_r=2, rh=(8, -6), rwa=-120, rw_back=True),
             P(TUCK, dy=-22, dx=7, rh=(9, -7), rwa=-80), P(TUCK, dy=-28, dx=9), P(TUCK, dy=-31, dx=10),
             P(TUCK, dy=-32, dx=11, spin=90), P(TUCK, dy=-31, dx=12, spin=180), P(TUCK, dy=-28, dx=13, spin=270),
             P(TUCK, dy=-21, dx=14, spin=0),
             P(SLAM, dx=14, crouch=8, sx=9, rwa=35, rh=(13, 2)),
             P(SLAM, dx=14, crouch=9, sx=9, rwa=35, rh=(13, 3), mouth="flat"),
             P(SLAM, dx=14, crouch=8, sx=9, rwa=35, rh=(13, 2), mouth="flat"),
             P(SLAM, dx=14, crouch=7, sx=9, rwa=30, rh=(13, 1), mouth="flat", eyes="look"),
             P(SLAM, dx=13, crouch=6, rwa=25, rh=(12, 0), mouth="frown", eyes="look"),
             P(IDLE, dx=9, dy=-4, crouch=2, lift_l=2, lift_r=2), P(IDLE, dx=3, crouch=6), P(IDLE)]
    base_ang, r_tip = spin_ref(ch, poses[10])

    def sig(t, p):
        if t in (2, 3):
            add_fx(p, fx_dust_feet(t - 2, 0.7))
        if 4 <= t <= 6:
            add_fx(p, fx_embers(t, seed=4), fx_dust_feet(min(t - 4, 2), 0.9))
        if t == 7:
            add_fx(p, fx_dust_x(RX - 2, 0, 1.4))
            add_fx(p, lambda cv, g: V.ground_impact(cv, RX - 2, FLOOR_Y, 1, size=0.6, floor=FL, seed=2))
        if t == 8:
            add_fx(p, fx_dust_x(RX - 2, 1, 1.4))
        if 11 <= t <= 14:
            s = p["spin"] if p["spin"] else 360
            a1 = base_ang + s
            add_fx(p, fx_cres(a1 - 100, a1, r_tip + 1, 24, pivot=piv))
            if t >= 12:
                add_fx(p, fx_cres(a1 - 190, a1 - 90, r_tip, 16, k=1, pivot=piv))
        if t == 15:
            add_fx(p, fx_trail(-80, 35, k=0), back=True)
        if t in (16, 17):
            add_fx(p, fx_trail(-60, 35, k=t - 15), back=True)
        if 15 <= t <= 22:
            k = t - 15
            add_fx(p, fx_ground(min(k, 7), 1.5, seed=41), back=True)
            if k <= 6:
                add_fx(p, fx_debris(k, seed=43, n=12, power=1.3))
        if t == 15:
            add_fx(p, fx_lines(0, 16, 32), fx_impact_tip(0, 1.4, u=TIP * 0.45))
        if t == 16:
            add_fx(p, fx_lines(1, 16, 32))
        if t in (20, 21):
            add_fx(p, fx_dust_feet(t - 20, 0.9))
    durs = [120, 140, 160, 180, 90, 90, 110, 50, 50, 60, 70, 40, 40, 40, 40, 160, 90, 90, 100, 110, 80, 110, 140]
    ev = hit_events(ch, poses, 15, hitstop=110, shake=(5, 260), u=TIP * 0.45, direction=60, ground="ground_impact",
                    extra=[{"frame": 15, "type": "vfx", "name": "debris", "baked": True},
                           {"frame": 7, "type": "vfx", "name": "dust", "baked": True},
                           {"frame": 7, "type": "screen_shake", "px": 1, "ms": 60}])
    ev.append({"frame": 0, "type": "phase", "phases": {"anticipation": [0, 3], "charge": [4, 6], "jump": [7, 10],
                                                        "spin": [11, 14], "impact": [15, 15], "aftermath": [16, 18],
                                                        "recovery": [19, 22]}})
    add(ch, "leap_spin_slash", poses, durs, extra=sig,
        label="jurus khas: jongkok, isi tenaga, melompat, salto 360 dengan tebasan, hantaman tanah besar, pulih",
        events=ev)


def _specials(ch):
    # rage: 10 langkah, aksen merah halus (wajah memerah sesaat, bara, garis aura tipis), bukan cahaya merah penuh
    r0 = P(READY, crouch=6, sx=8)
    roar = P(READY, crouch=4, sx=8, lean=-2, hdy=-1, rh=(8, -8), re=None, rwa=-115, face="A", mouth="shout", eyes="angry")
    poses = [P(READY), P(r0, dx=-1), P(r0, dx=1, crouch=7), P(r0, crouch=7, hdy=3, eyes="blink", mouth="flat"),
             P(roar), P(roar, dx=1), P(roar, dx=-1, face="F"), P(roar, dx=1, face="F"), P(roar, face="F", mouth="flat"),
             P(READY, crouch=6, sx=8, eyes="angry", mouth="flat")]

    def rage(t, p):
        if 4 <= t <= 8:
            add_fx(p, fx_roar(t), fx_embers(t, seed=7), fx_rim(t))
            add_fx(p, fx_dust_feet(min(t - 4, 3), 1.2))
        if t in (1, 2, 9):
            add_fx(p, fx_embers(t, seed=7))
    add(ch, "rage", poses, [120, 90, 90, 200, 60, 90, 90, 90, 110, 160], extra=rage,
        label="mode amuk: gemetar, menunduk, mengaum (bara merah redup, aura tipis), kuda-kuda lebih rendah",
        events=[{"frame": 4, "type": "screen_shake", "px": 3, "ms": 260},
                {"frame": 4, "type": "rage_on"}])

    # rage_attack: jongkok -> meledak maju -> sabetan rendah -> sabetan naik -> putaran gasing -> tebasan berat
    low = P(SWORD, sx=9, crouch=7, lean=6, hdy=1, rh=(-2, 4), rwa=170, rw_back=True, arm0_behind=True,
            eyes="angry", brows="angry", mouth="shout", face="A", cloak_lift=3)
    spin_a = P(SWORD, sx=6, crouch=4, lean=2, rh=(13, -2), rwa=-5, arm0_behind=True, eyes="angry", brows="angry",
               mouth="shout", cloak_lift=4)
    poses = [P(IDLE), P(READY, crouch=7, sx=8, face="A"), P(low, dx=-1, crouch=8),
             P(low, dx=7, rh=(1, 4)),
             P(SLAM, dx=10, rh=(14, 1), rwa=5, crouch=6, lean=6),
             P(SLAM, dx=11, rh=(13, -4), rwa=-30, crouch=5, lean=5),
             P(SLAM, dx=11, rh=(12, -9), re=None, rwa=-75, crouch=4, lean=2),
             P(READY, dx=12, rh=(6, -6), re=None, rwa=-160, crouch=4, lean=-1),
             P(spin_a, dx=13), P(spin_a, dx=14, rh=(1, 0), rwa=-170, rw_back=True, mouth="flat"),
             P(spin_a, dx=14, mirror=True), P(spin_a, dx=15, rh=(2, 3), rwa=95),
             P(OVER, dx=15, rwa=-140, rh=(3, -13), crouch=5, dy=-4, lift_l=2, lift_r=2),
             P(READY, dx=16, rh=(12, -11), re=None, rwa=-70, rw_back=False, dy=-3, mouth="shout"),
             P(SLAM, dx=16, crouch=8, sx=9, rwa=35),
             P(SLAM, dx=16, crouch=9, sx=9, rwa=35, mouth="flat"), P(SLAM, dx=16, crouch=7, sx=9, rwa=30, mouth="flat"),
             P(SLAM, dx=15, crouch=6, rwa=25, mouth="flat", eyes="look"),
             P(IDLE, dx=11, dy=-4, crouch=2, lift_l=2, lift_r=2), P(IDLE, dx=5, crouch=6), P(IDLE, dx=1, crouch=4), P(IDLE)]

    def ra(t, p):
        if t in (1, 2):
            add_fx(p, fx_embers(t, seed=9), fx_rim(t))
        if t == 3:
            add_fx(p, fx_speed(dx=-14, dy=2, n=5, length=14), back=True)
            add_fx(p, fx_dust_x(RX + 2, 0, 1.3))
        if t in (4, 5):
            add_fx(p, fx_cres(170, 375, 40, 11, k=t - 4, flat=0.5, dx=2, dy=6), back=True)
        if t == 6:
            add_fx(p, fx_trail(30, -75), back=True)
        if t == 7:
            add_fx(p, fx_trail(-30, -160, k=1), back=True)
        if 8 <= t <= 11:
            add_fx(p, fx_cres(-200 + (t - 8) * 90, -20 + (t - 8) * 90, 46, 10, flat=0.32, dy=-1, k=0 if t < 11 else 1),
                   back=True)
        if t == 13:
            add_fx(p, fx_trail(-150, -70), back=True)
        if 14 <= t <= 17:
            k = t - 14
            if k <= 2:
                add_fx(p, fx_trail(-110, 35, k=k), back=True)
            add_fx(p, fx_ground(k, 1.2, seed=51), back=True)
            add_fx(p, fx_debris(k, seed=53))
        if t == 14:
            add_fx(p, fx_lines(0))
        if t in (18, 19):
            add_fx(p, fx_dust_feet(t - 18, 0.9))
    durs = [100, 140, 120, 60, 50, 70, 50, 70, 40, 40, 40, 40, 90, 40, 150, 90, 100, 100, 80, 100, 110, 130]
    small = ("blood_small", "blood_small", "blood_medium")
    ev = (hit_events(ch, poses, 4, hitstop=40, u=TIP * 0.7, direction=0, blood=small) +
          hit_events(ch, poses, 6, hitstop=40, u=TIP * 0.6, direction=-60, blood=small) +
          hit_events(ch, poses, 8, hitstop=30, u=TIP * 0.8, direction=0, blood=small) +
          hit_events(ch, poses, 14, hitstop=100, shake=(4, 240), u=TIP * 0.45, direction=60, ground="ground_impact"))
    add(ch, "rage_attack", poses, durs, extra=ra,
        label="amuk: jongkok, meledak maju, sabetan rendah, sabetan naik, putaran gasing, tebasan berat",
        events=ev + [{"frame": 1, "type": "rage_on"}])

    # combo: mendatar -> balik -> atas -> lompat salto -> hantaman tanah
    poses = [P(IDLE), P(IDLE, rh=(3, -1), rwa=165, rw_back=True, crouch=5, lean=0, mouth="flat"),
             P(SWORD, sx=8, crouch=5, lean=-2, rh=(-3, 2), rwa=175, rw_back=True, arm0_behind=True, eyes="angry",
               brows="angry", mouth="shout"),
             P(SLAM, rh=(14, -4), rwa=-5, crouch=4), P(SLAM, rh=(13, -6), rwa=-30, crouch=4),
             P(SLAM, rh=(14, 2), rwa=30, crouch=5),
             P(READY, rh=(9, -8), re=None, rwa=-120, rw_back=True, crouch=4, lean=1, mouth="shout"),
             P(OVER, rwa=-140, rh=(3, -13)),
             P(SLAM, rwa=30, crouch=7), P(SLAM, rwa=30, crouch=6, mouth="flat"),
             P(READY, crouch=8, sx=9), P(TUCK, dy=-16, dx=4, crouch=0, lift_l=1, lift_r=2, rh=(8, -6), rwa=-100),
             P(TUCK, dy=-28, dx=7), P(TUCK, dy=-31, dx=8, spin=90), P(TUCK, dy=-30, dx=9, spin=180),
             P(TUCK, dy=-26, dx=10, spin=270), P(TUCK, dy=-18, dx=11, spin=0),
             P(SLAM, dx=11, crouch=8, sx=9, rwa=35), P(SLAM, dx=11, crouch=9, sx=9, rwa=35, mouth="flat"),
             P(SLAM, dx=11, crouch=7, rwa=30, mouth="flat"), P(SLAM, dx=10, crouch=6, rwa=25, mouth="frown", eyes="look"),
             P(IDLE, dx=7, dy=-4, crouch=2, lift_l=2, lift_r=2), P(IDLE, dx=2, crouch=6), P(IDLE)]
    base_ang, r_tip = spin_ref(ch, poses[12])

    def combo(t, p):
        if t in (3, 4):
            add_fx(p, fx_cres(160, 355, 44, 12, k=t - 3, flat=0.42, dy=-2), back=True)
        if t == 6:
            add_fx(p, fx_trail(30, -120), back=True)
        if t == 8:
            add_fx(p, fx_trail(-140, 30), back=True)
            add_fx(p, fx_impact_tip(0, 0.8), fx_dust_at(0))
        if t == 9:
            add_fx(p, fx_trail(-100, 30, k=1), back=True)
            add_fx(p, fx_dust_at(1))
        if t == 11:
            add_fx(p, fx_dust_x(RX + 2, 0, 1.3))
        if 13 <= t <= 16:
            s = p["spin"] if p["spin"] else 360
            a1 = base_ang + s
            add_fx(p, fx_cres(a1 - 100, a1, r_tip + 1, 24, pivot=piv))
        if 17 <= t <= 22:
            k = t - 17
            if k <= 2:
                add_fx(p, fx_trail(-80, 35, k=k), back=True)
            add_fx(p, fx_ground(k, 1.4, seed=61), back=True)
            add_fx(p, fx_debris(k, seed=63, n=11, power=1.2))
        if t == 17:
            add_fx(p, fx_lines(0, 16, 30))
    durs = [80, 100, 130, 40, 90, 90, 50, 120, 50, 90, 140, 50, 60, 40, 40, 40, 40, 160, 90, 100, 110, 80, 110, 140]
    ev = (hit_events(ch, poses, 3, hitstop=40, u=TIP * 0.8, direction=0) +
          hit_events(ch, poses, 6, hitstop=40, u=TIP * 0.6, direction=-70) +
          hit_events(ch, poses, 8, hitstop=60, shake=(2, 100), direction=40) +
          hit_events(ch, poses, 17, hitstop=110, shake=(5, 260), u=TIP * 0.45, direction=60, ground="ground_impact"))
    add(ch, "combo", poses, durs, extra=combo,
        label="kombo: sapuan mendatar, sabetan balik, bacokan atas, lompat salto, hantaman tanah", events=ev)


def _reactions(ch):
    poses = [P(IDLE, dx=-3, lean=-2, hdy=-1, rwa=10, rh=(9, -5), eyes="wide", brows="worried", mouth="shout"),
             P(IDLE, dx=-4, lean=-3, hdy=-1, rwa=5, rh=(8, -6), eyes="wide", brows="worried", mouth="shout"),
             P(IDLE, dx=-3, crouch=5, lean=1, rwa=15, rh=(9, -4), eyes="angry", brows="angry", mouth="flat"),
             P(IDLE, dx=-2, crouch=5, eyes="angry", mouth="flat"), P(IDLE, dx=-1, crouch=4, eyes="angry"),
             P(IDLE, crouch=4), P(IDLE), P(IDLE)]

    def hit(t, p):
        if t <= 1:
            add_fx(p, lambda cv, g, t=t: V.impact(cv, int(round(g.tcx + 6)), int(round(g.tcy - 2)), t, size=0.7, floor=FL))
        if t in (1, 2, 3):
            add_fx(p, fx_dust_feet(t - 1, 0.8))
    add(ch, "hit", poses, [60, 90, 100, 100, 90, 90, 100, 120], extra=hit, core="hit",
        label="tersentak mundur, pedang goyah, menggertakkan gigi, kembali ke kuda-kuda")

    up = P(OVER, rwa=-100, rh=(4, -14), mouth="flat")
    stuck = P(SLAM, rh=(13, -5), rwa=65, crouch=6, lean=4, sx=9)

    def pull(dx, lean, **kw):
        # tangan tetap di gagang yang tertancap: posisi tangan dunia dikompensasi geser badan dan condong
        return P(stuck, dx=dx, lean=lean, rh=(int(round(13 + 0.45 * 4 - dx - 0.45 * lean)), -5), **kw)
    poses = [P(IDLE), P(READY, rwa=-100, rh=(8, -8), re=None), P(up, crouch=2), P(up, crouch=3, lean=-2, mouth="shout"),
             P(READY, rh=(12, -10), re=None, rwa=-40, rw_back=False, mouth="shout", crouch=5), stuck,
             P(stuck, crouch=7, rh=(13, -6), mouth="flat"), P(stuck, mouth="flat", eyes="look"),
             pull(-1, 1, mouth="shout", eyes="angry"), pull(-2, -2, mouth="shout", eyes="angry"),
             pull(-1, 0, mouth="shout", eyes="angry"), pull(-2, -3, mouth="shout", eyes="blink"),
             pull(-3, -4, mouth="shout", eyes="angry"), pull(-1, 0, mouth="flat", eyes="angry"),
             pull(-1, 1, mouth="flat", eyes="down", brows="worried"), pull(-1, 1, mouth="flat", eyes="down", brows="worried"),
             pull(-1, 1, mouth="frown", eyes="down", brows="worried"),
             pull(-1, 1, mouth="flat", eyes="look", brows="flat", hdx=-1),
             pull(-1, 1, mouth="flat", eyes="look", brows="flat", hdx=-1),
             pull(-1, 1, mouth="flat", eyes="blink", brows="flat", hdx=-1),
             pull(-1, 1, mouth="flat", eyes="look", brows="flat", hdx=-1)]

    def miss(t, p):
        if 5 <= t <= 9:
            add_fx(p, fx_dust_at(t - 5, 1.0, seed=2), fx_debris(t - 5, seed=71, n=5, power=0.7))
        if 8 <= t <= 12:
            add_fx(p, fx_sweat())
            add_fx(p, lambda cv, g, t=t: V.dust(cv, int(round(g.feet[0][0])) - 2, FLOOR_Y, t % 2, size=0.5, floor=FL))
        if t >= 17:
            add_fx(p, fx_mark("..."))
    add(ch, "miss", poses,
        [80, 100, 150, 170, 40, 160, 100, 140, 110, 90, 110, 90, 130, 200, 240, 200, 200, 120, 260, 80, 300],
        extra=miss, hold=8, label="meleset: pedang tertancap, ditarik-tarik, menatap pedang, lalu menatap penonton",
        events=[{"frame": 5, "type": "screen_shake", "px": 2, "ms": 120},
                {"frame": 5, "type": "vfx", "name": "dust", "baked": True}])

    tired = P(IDLE, crouch=6, lean=5, hdy=3, rh=(10, -1), rwa=15, eyes="relief", brows="worried", mouth="o")
    poses = [P(tired), P(tired, crouch=5, rh=(10, -2), hdy=2), P(tired, crouch=5, rh=(10, -2), hdy=2, mouth="shout"),
             P(tired, crouch=6), P(tired, crouch=7, rh=(10, 0), hdy=4), P(tired, crouch=6),
             P(tired, crouch=5, rh=(10, -2), hdy=2), P(tired, crouch=6, eyes="blink")]

    def ex(t, p):
        add_fx(p, fx_sweat(11, -6 + (t % 4)))
        if t in (2, 3):
            add_fx(p, fx_breath(t - 2))
        if t in (6, 7):
            add_fx(p, fx_breath(t - 6))
    add(ch, "exhausted", poses, [140, 110, 110, 140, 160, 120, 110, 140], extra=ex, loop=True,
        label="kehabisan tenaga: bersandar ke pedang, terengah-engah, berkeringat")

    strain = P(IDLE, crouch=5, lean=1, mouth="shout", eyes="angry", brows="worried")
    raised = P(SWORD, sx=7, crouch=1, lean=0, rh=(9, -14), rwa=-85, eyes="angry", brows="angry", mouth="shout", hdy=0)
    poses = [P(IDLE), P(strain, rh=(9, -4)), P(strain, rh=(8, -5), dx=-1), P(strain, rh=(8, -5), dx=1, rwa=15),
             P(strain, rh=(8, -7), rwa=10, dx=-1), P(strain, rh=(8, -8), rwa=-10, crouch=4),
             P(READY, rh=(7, -7), re=None, rwa=-100, crouch=4, mouth="shout"),
             P(raised, rh=(8, -12), crouch=3), P(raised), P(raised, crouch=0, hdy=-1),
             P(raised, crouch=0, hdy=-1, lean=-1), P(raised, crouch=0, hdy=-1, lean=-1, dx=1),
             P(raised, crouch=0, hdy=-1, lean=-1), P(raised, crouch=0, hdy=-1, lean=-1, dx=-1),
             P(raised, crouch=1, mouth="smirk", eyes="look"), P(raised, crouch=1, mouth="smirk", eyes="happy", brows="flat")]

    def vic(t, p):
        if 1 <= t <= 5:
            add_fx(p, fx_sweat(11 if t % 2 else 12, -6))
        if t in (2, 3, 4):
            add_fx(p, fx_dust_at(t - 2, 0.5, seed=t))
        if 9 <= t <= 13:
            add_fx(p, fx_roar(t))
        if t in (9, 10):
            add_fx(p, fx_dust_feet(t - 9, 1.2))
    add(ch, "victory", poses, [200, 160, 120, 120, 160, 140, 90, 90, 90, 120, 90, 90, 90, 120, 200, 240], extra=vic,
        hold=10, core="victory", label="susah payah mengangkat pedang, mengacungkannya tinggi, mengaum",
        events=[{"frame": 9, "type": "screen_shake", "px": 2, "ms": 160}])

    wob = P(SWORD, sx=6, crouch=3, lean=0, rh=(8, -12), rwa=-95, eyes="wide", brows="worried", mouth="shout")
    gsw = (RX - 22, FLOOR_Y - 5, 180)
    sit = dict(mode="sit", rw=None, two=False, lean=0, crouch=0, ground_sword=gsw, eyes="side", brows="angry",
               mouth="frown", rh=(7, 2), lh=(-7, 2), hdy=0, dx=-3, re=None, le=None, arm0_behind=False)
    poses = [P(IDLE, eyes="relief", brows="worried"), P(IDLE, crouch=5, rh=(9, -6), rwa=0, mouth="shout", eyes="angry"),
             P(wob, rh=(8, -10), rwa=-80), P(wob), P(wob, rwa=-110, lean=-2, dx=-1),
             P(wob, rwa=-135, lean=-3, dx=-2, rw_back=True), P(wob, rwa=-160, lean=-4, dx=-3, rw_back=True, rh=(5, -9)),
             P(IDLE, rw=None, two=False, ground_sword=gsw, dx=-3, crouch=5, lean=-2, rh=(8, -12), lh=(-8, -12),
               arm0_behind=False, eyes="wide", brows="worried", mouth="o"),
             P(sit, eyes="wide", brows="worried", mouth="o"), P(sit, eyes="relief", brows="worried"),
             P(sit, eyes="left"), P(sit, eyes="left", brows="angry"),
             P(sit, eyes="left", lh=(-12, -2), mouth="shout"), P(sit, eyes="left", lh=(-13, -1), mouth="shout"),
             P(sit, eyes="left", lh=(-12, -2), mouth="flat"),
             P(sit, eyes="look", rh=(3, 1), lh=(-3, 1)), P(sit, eyes="look", rh=(3, 1), lh=(-3, 1), brows="flat"),
             P(sit, eyes="blink", rh=(3, 1), lh=(-3, 1), brows="flat"), P(sit, eyes="look", rh=(3, 1), lh=(-3, 1), brows="flat")]

    def de(t, p):
        if 2 <= t <= 6:
            add_fx(p, fx_sweat())
        if t == 7:
            add_fx(p, lambda cv, g: V.ground_impact(cv, RX - 22, FLOOR_Y, 1, size=0.8, floor=FL, seed=5))
        if t in (8, 9):
            add_fx(p, fx_dust_x(RX - 22, t - 7, 1.0), fx_dust_feet(t - 8, 1.0))
        if 12 <= t <= 14:
            add_fx(p, fx_mark("!", dx=-24, dy=-12))
        if t >= 15:
            add_fx(p, fx_mark("..."))
    add(ch, "defeat", poses, [200, 120, 140, 160, 120, 110, 90, 120, 140, 160, 200, 140, 120, 160, 200, 200, 200, 90, 300],
        extra=de, hold=10, core="defeat",
        label="pedang terlalu berat, terjungkal ke belakang dan jatuh, duduk, menyalahkan pedang",
        events=[{"frame": 7, "type": "screen_shake", "px": 2, "ms": 100}])
