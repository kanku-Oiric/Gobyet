"""Sel sisa kostum lama (Fase 2, Gerbang F): 14 sel wajib dan 22 sel opsional.

Tampilan tiap kostum dipakai ulang dari modul aslinya (roles.py, domains.py), tanpa desain ulang.
Bahasa state mengikuti brief bagian 10:
- happy: senyum kecil dan gerakan positif, bukan perayaan besar;
- victory: perayaan dengan satu elemen khas yang belum dipakai kostum lain;
- defeated: lunglai atau rebah, prop terjatuh, tidak brutal;
- shocked: mata melebar, mundur sedikit, efek kecil, "!";
- thinking: pose beda dari idle, "..." lalu "?".

Role netral (Referee, Judge, Skeptic) tidak menari dan tidak dibuat konyol (7.3): victory mereka tanpa
lompat dan tanpa konfeti. Hanya Normal dan Champion yang punya dance-a (16 frame x 120 ms).
"""
import math

from monkey import (Canvas, head, arm, tail, sitting_body, banana, puff, spark_lines, mini_text, bubble, ellipse,
                    capsule, chain, rect, solid)
from costumes import CX, CY, TOP, confetti, mortarboard, scroll, column, chalkboard, wild_hair, einstein_moustache, magnifier
from roles import (referee_shirt, referee_arm, whistle, clipboard, pencil, dots_or_mark, judge_robe, judge_arm, gavel,
                   sound_block, JX_BLOCK, skeptic_sweater, monocle, stamp, paper, champion_body, trophy)
from domains import (sigh, lying_body, GX, greek_body, greek_head, AY, AT, academic_body, open_diploma, SX, chalk,
                     math_vest, slate, compass, HX, HY, terminal, hacker_base, typing, thought_dots, detective_base,
                     lawyer_suit, folder, CODE)

# ================================================================== pola bersama
VIC = [("rest", 0), ("mid", 0), ("up", 1), ("up", 0), ("up", 1), ("up", 0), ("up", 1), ("up", 0), ("up", 1),
       ("up", 0), ("up", 1), ("up", 0), ("mid", 0), ("mid", 0), ("rest", 0), ("rest", 0)]
SHOCK = [("calm", 0), ("calm", 0), ("jolt", -2), ("shock", -2), ("shock", -3), ("shock", -2), ("shock", -3),
         ("shock", -2), ("shock", -2), ("calm", -1), ("calm", 0), ("calm", 0)]
DANCE = [(-2, 0, "left"), (0, 1, "low"), (2, 0, "right"), (0, 1, "low")]


def wag(t, n):
    return t * math.tau / n


def shock_face(phase):
    return ("look", "flat", "flat") if phase == "calm" else ("wide", "up", "o")


def bang(cv, x=46, y=3):
    """Gelembung merah "!" di kanan atas (sama dengan shocked kostum lain)."""
    bubble(cv, x, y, 9, 9, fill="R", tail_dir=-1)
    mini_text(cv, "!", x + 2, y + 2, "W")


def ms_const(v):
    return lambda i: v


def shock_ms(i):
    return 150 if i % 12 in (0, 1, 9, 10, 11) else 110


def happy_eyes(t):
    return "happy" if 3 <= t <= 8 else ("blink" if t == 10 else "look")


def nod12(t):
    return 1 if t in (5, 6) else 0


def defeated_ms(i):
    return 230 if 6 <= i % 16 <= 9 else 190


# ================================================================== Normal (tampilan Gerbang C: badan duduk berbulu)
def normal_look(cv, t, n, eyes, brows, mouth, dx=0, bob=0):
    tail(cv, (CX - 6 + dx, TOP + 14 + bob), phase=wag(t, n), flip=-1, length=8)
    sitting_body(cv, CX + dx, TOP + bob)
    head(cv, CX + dx, CY + bob, eyes=eyes, brows=brows, mouth=mouth)


def normal_shocked_frame(i):
    """Pisang di tangan terlonjak ke atas, badan tersentak mundur, mata lebar, "!"."""
    cv = Canvas()
    t = i % 12
    phase, dx = SHOCK[t]
    normal_look(cv, t, 12, *shock_face(phase), dx=dx)
    if phase == "calm":
        banana(cv, CX + 11 + dx, TOP + 6)
        arm(cv, (CX + 7 + dx, TOP + 3), (CX + 11 + dx, TOP + 7), elbow=(CX + 12 + dx, TOP + 9))
        arm(cv, (CX - 7 + dx, TOP + 3), (CX - 8 + dx, TOP + 10), elbow=(CX - 11 + dx, TOP + 6))
    else:
        jump = 5 if phase == "jolt" else 3 + (t % 2)
        banana(cv, CX + 15 + dx, TOP - jump)
        arm(cv, (CX + 7 + dx, TOP + 3), (CX + 13 + dx, TOP + 2), elbow=(CX + 13 + dx, TOP + 7))
        arm(cv, (CX - 7 + dx, TOP + 3), (CX - 13 + dx, TOP + 1), elbow=(CX - 12 + dx, TOP + 7))
        bang(cv)
        spark_lines(cv, CX - 15 + dx, 6)
    return cv


def normal_dance_a_frame(i):
    """Joget pisang: pisang diangkat bergantian dengan kepalan tangan, badan bergeser per beat (16 x 120 ms)."""
    cv = Canvas()
    t = i % 16
    beat = t // 4
    dx, bob, move = DANCE[beat]
    tail(cv, (CX - 6 + dx, TOP + 14 + bob), phase=beat * 1.6 + (t % 4) * 0.25, flip=-1, length=8)
    sitting_body(cv, CX + dx, TOP + bob)
    head(cv, CX + dx, CY + bob, eyes="happy", brows="flat", mouth="smile" if beat % 2 == 0 else "o")
    sh = TOP + 3 + bob
    if move == "left":  # pisang tinggi di kanan, kepalan kiri di pinggang
        banana(cv, CX + 15 + dx, TOP - 8)
        arm(cv, (CX + 7 + dx, sh), (CX + 15 + dx, TOP - 7), elbow=(CX + 14 + dx, TOP))
        arm(cv, (CX - 7 + dx, sh), (CX - 7 + dx, TOP + 9 + bob), elbow=(CX - 12 + dx, TOP + 6 + bob))
    elif move == "right":  # kepalan kiri tinggi, pisang turun di pinggang kanan
        banana(cv, CX + 11 + dx, TOP + 6)
        arm(cv, (CX + 7 + dx, sh), (CX + 11 + dx, TOP + 7), elbow=(CX + 12 + dx, TOP + 9))
        arm(cv, (CX - 7 + dx, sh), (CX - 17 + dx, TOP - 11), elbow=(CX - 15 + dx, TOP - 1))
    else:  # dua tangan di depan dada, pisang di tengah
        banana(cv, CX + 3 + dx, TOP + 5 + bob)
        arm(cv, (CX + 7 + dx, sh), (CX + 3 + dx, TOP + 6 + bob), elbow=(CX + 12 + dx, TOP + 7 + bob))
        arm(cv, (CX - 7 + dx, sh), (CX - 2 + dx, TOP + 7 + bob), elbow=(CX - 12 + dx, TOP + 7 + bob))
    return cv


# ================================================================== Referee
def referee_look(cv, t, n, eyes, brows, mouth, dx=0, bob=0, whistle_on_chest=True):
    tail(cv, (26 + dx, TOP + 14 + bob), phase=wag(t, n), flip=-1, length=8)
    referee_shirt(cv, CX + dx, TOP + bob)
    head(cv, CX + dx, CY + bob, eyes=eyes, brows=brows, mouth=mouth)
    if whistle_on_chest:
        whistle(cv, CX + dx, TOP + bob)


def whistle_at_mouth(cv, x, y):
    """Peluit dipegang di mulut: badan perak menutupi mulut, tali merah ke leher."""
    solid(cv, rect(x - 2, y - 1, 5, 3), "G", None, outline="l")
    cv.put(x + 2, y, "P")


def referee_victory_frame(i):
    """Akhir pertandingan: lengan kanan diangkat lurus sebagai isyarat, peluit ditiup dengan nada "n" yang naik (khas).
    Tanpa lompat dan tanpa konfeti (role netral, 7.3)."""
    cv = Canvas()
    t = i % 16
    phase = VIC[t][0]
    up = phase == "up"
    referee_look(cv, t, 16, "happy" if up else "look", "flat", "o" if up else "smile", whistle_on_chest=not up)
    if phase == "rest":
        for s in (-1, 1):
            referee_arm(cv, (CX + s * 7, TOP + 3), (CX + s * 7, TOP + 9), (CX + s * 12, TOP + 6))
        return cv
    if phase == "mid":
        referee_arm(cv, (CX + 7, TOP + 3), (CX + 12, TOP - 4), (CX + 13, TOP + 2))
        referee_arm(cv, (CX - 7, TOP + 3), (CX - 7, TOP + 9), (CX - 12, TOP + 6))
        return cv
    referee_arm(cv, (CX + 7, TOP + 3), (CX + 11, 2), (CX + 12, TOP - 4))  # isyarat: lengan lurus ke atas
    whistle_at_mouth(cv, CX + 1, CY + 6)
    referee_arm(cv, (CX - 7, TOP + 3), (CX - 2, CY + 8), (CX - 11, TOP + 5))
    k = (t - 2) % 4
    mini_text(cv, "n", CX - 20 - k, 12 - k * 2, "K")
    return cv


def referee_defeated_frame(i):
    """Duduk lunglai, bahu turun, papan klip terjatuh telentang di lantai, tangan terkulai; menghela napas."""
    cv = Canvas()
    t = i % 16
    sag = 2 + (1 if 6 <= t <= 9 else 0)
    tail(cv, (26, TOP + 14), phase=wag(t, 16) * 0.5, flip=-1, length=8)
    referee_shirt(cv, CX, TOP + 1)
    head(cv, CX, CY + sag, eyes="blink" if t == 12 else "relief", brows="worried", mouth="frown")
    whistle(cv, CX, TOP + 1)
    solid(cv, rect(CX + 12, TOP + 14, 11, 3), "N", None)  # papan klip rebah di lantai kanan
    cv.fill(rect(CX + 13, TOP + 14, 8, 1), "W")
    referee_arm(cv, (CX - 7, TOP + 4), (CX - 10, TOP + 13), (CX - 11, TOP + 8))
    referee_arm(cv, (CX + 7, TOP + 4), (CX + 10, TOP + 13), (CX + 11, TOP + 8))
    if 6 <= t <= 9:
        sigh(cv, CX - 16, CY - 2, t - 6)
    return cv


def referee_shocked_frame(i):
    """Tersentak mundur, papan klip diangkat ke depan dada dengan dua tangan, mata lebar, "!"."""
    cv = Canvas()
    t = i % 12
    phase, dx = SHOCK[t]
    referee_look(cv, t, 12, *shock_face(phase), dx=dx)
    if phase == "calm":
        for s in (-1, 1):
            referee_arm(cv, (CX + dx + s * 7, TOP + 3), (CX + dx + s * 7, TOP + 9), (CX + dx + s * 12, TOP + 6))
    else:
        clipboard(cv, CX - 4 + dx, TOP + 1)
        referee_arm(cv, (CX - 7 + dx, TOP + 3), (CX - 4 + dx, TOP + 6), (CX - 11 + dx, TOP + 7))
        referee_arm(cv, (CX + 7 + dx, TOP + 3), (CX + 4 + dx, TOP + 6), (CX + 11 + dx, TOP + 7))
        bang(cv)
        spark_lines(cv, CX - 15 + dx, 6)
    return cv


def referee_happy_frame(i):
    """Menggoreskan centang kecil di papan klip, lalu mengangguk dengan senyum kecil."""
    cv = Canvas()
    t = i % 12
    referee_look(cv, t, 12, happy_eyes(t) if t >= 4 else "down", "flat", "smile", bob=0)
    if nod12(t):
        head(cv, CX, CY + 1, eyes=happy_eyes(t), brows="flat", mouth="smile")
    clipboard(cv, CX - 15, TOP + 1)
    if t >= 2:
        cv.fill({(CX - 12, TOP + 6), (CX - 11, TOP + 7), (CX - 10, TOP + 6), (CX - 9, TOP + 5)}, "V")  # centang
    referee_arm(cv, (CX - 7, TOP + 3), (CX - 8, TOP + 7), (CX - 11, TOP + 7))
    if t < 3:
        hx, hy = CX - 9, TOP + 5 + (t % 2)
        referee_arm(cv, (CX + 7, TOP + 3), (hx + 3, hy + 2), (CX + 8, TOP + 9))
        pencil(cv, hx + 3, hy + 1, hx, hy)
    else:
        referee_arm(cv, (CX + 7, TOP + 3), (CX + 7, TOP + 9), (CX + 12, TOP + 6))
    return cv


# ================================================================== Judge
def judge_look(cv, t, n, eyes, brows, mouth, dx=0, bob=0):
    tail(cv, (CX - 9 + dx, TOP + 14), phase=wag(t, n), flip=-1, length=7)
    judge_robe(cv, CX + dx, TOP + bob)
    head(cv, CX + dx, CY + bob, eyes=eyes, brows=brows, mouth=mouth)
    sound_block(cv, JX_BLOCK, TOP + 12)


def balance_scale(cv, x, y, tilt=0, glint=False):
    """Timbangan emas kecil (prop victory Judge): tiang, balok, dua piring bertali. (x, y) = puncak tiang;
    tilt -1..1 = balok miring, 0 = seimbang."""
    cv.fill(capsule((x, y), (x, y + 9), 0.6), "y")
    solid(cv, rect(x - 2, y + 9, 5, 2), "y", None)
    lx, rx = x - 6, x + 6
    ly, ry = y + 1 + tilt, y + 1 - tilt
    cv.fill(chain([(lx, ly), (x, y + 1), (rx, ry)], 0.5), "O")
    for px, py in ((lx, ly), (rx, ry)):
        cv.fill({(px, py + 1), (px, py + 2)}, "y")
        solid(cv, rect(px - 2, py + 3, 5, 2), "O", "y", shade_off=(1, 1))
    if glint:
        cv.fill({(x, y - 2), (x - 1, y - 2), (x + 1, y - 2), (x, y - 3), (x, y - 1)}, "W")


def judge_victory_frame(i):
    """Palu diangkat, tangan kiri mengangkat timbangan emas kecil yang berayun lalu seimbang dan berkilau (khas).
    Tanpa lompat dan tanpa konfeti (role netral, 7.3)."""
    cv = Canvas()
    t = i % 16
    phase = VIC[t][0]
    up = phase == "up"
    judge_look(cv, t, 16, "happy" if up else "look", "flat", "smile")
    if phase == "rest":
        judge_arm(cv, (CX - 7, TOP + 3), (CX - 6, TOP + 10), (CX - 11, TOP + 7))
        gavel(cv, CX + 11, TOP + 10, 45)
        judge_arm(cv, (CX + 7, TOP + 3), (CX + 11, TOP + 10), (CX + 11, TOP + 6))
        return cv
    gy = TOP - 3 if up else TOP + 3
    gavel(cv, CX + 15, gy, 80)
    judge_arm(cv, (CX + 7, TOP + 3), (CX + 15, gy), (CX + 14, TOP + 3))
    sy = 3 if up else 10
    tilt = (1, -1, 1, 0, -1, 0, 0, 0, 0, 0)[t - 2] if up else 1
    balance_scale(cv, CX - 20, sy, tilt=tilt, glint=up and t >= 8 and t % 2 == 0)
    judge_arm(cv, (CX - 7, TOP + 3), (CX - 20, sy + 11), (CX - 13, TOP + 4))
    return cv


def judge_defeated_frame(i):
    """Lunglai: badan merosot ke kiri, kepala tertunduk sedikit, palu tergeletak mendatar di lantai, tangan terkulai;
    menghela napas."""
    cv = Canvas()
    t = i % 16
    lean = -3
    sag = 3 + (1 if 6 <= t <= 9 else 0)
    tail(cv, (CX - 9 + lean, TOP + 14), phase=wag(t, 16) * 0.5, flip=-1, length=7)
    judge_robe(cv, CX + lean, TOP + 1)
    head(cv, CX + lean, CY + sag, eyes="blink" if t == 12 else "relief", brows="worried", mouth="frown", tilt=-1)
    sound_block(cv, JX_BLOCK, TOP + 12)
    gavel(cv, JX_BLOCK - 2, TOP + 16, 0)  # palu tergeletak di lantai
    judge_arm(cv, (CX - 7 + lean, TOP + 4), (CX - 12 + lean, TOP + 13), (CX - 12 + lean, TOP + 8))
    judge_arm(cv, (CX + 7 + lean, TOP + 4), (CX + 8 + lean, TOP + 13), (CX + 11 + lean, TOP + 8))
    if 6 <= t <= 9:
        sigh(cv, CX + lean - 17, CY, t - 6)
    return cv


def judge_shocked_frame(i):
    """Tersentak mundur, palu terlonjak ke atas di tangan, mata lebar, "!"."""
    cv = Canvas()
    t = i % 12
    phase, dx = SHOCK[t]
    judge_look(cv, t, 12, *shock_face(phase), dx=dx)
    judge_arm(cv, (CX - 7 + dx, TOP + 3), (CX - 12 + dx, TOP + 4) if phase != "calm" else (CX - 6 + dx, TOP + 10),
              (CX - 12 + dx, TOP + 8) if phase != "calm" else (CX - 11 + dx, TOP + 7))
    if phase == "calm":
        gavel(cv, CX + 11 + dx, TOP + 10, 45)
        judge_arm(cv, (CX + 7 + dx, TOP + 3), (CX + 11 + dx, TOP + 10), (CX + 11 + dx, TOP + 6))
    else:
        gavel(cv, CX + 14 + dx, TOP - 1, 100)
        judge_arm(cv, (CX + 7 + dx, TOP + 3), (CX + 14 + dx, TOP - 1), (CX + 14 + dx, TOP + 4))
        bang(cv)
        spark_lines(cv, CX - 16 + dx, 6)
    return cv


def judge_happy_frame(i):
    """Senyum kecil, mengangguk, palu mengetuk landasan pelan sekali (tanpa percikan)."""
    cv = Canvas()
    t = i % 12
    judge_look(cv, t, 12, happy_eyes(t), "flat", "smile", bob=nod12(t))
    judge_arm(cv, (CX - 7, TOP + 3), (CX - 6, TOP + 10), (CX - 11, TOP + 7))
    tap = t in (7, 8)
    gavel(cv, CX + 10 if tap else CX + 11, TOP + 9 if tap else TOP + 10, -15 if tap else 45)
    judge_arm(cv, (CX + 7, TOP + 3), (CX + 10, TOP + 9) if tap else (CX + 11, TOP + 10), (CX + 12, TOP + 6))
    return cv


# ================================================================== Skeptic
def skeptic_look(cv, t, n, eyes, brows, mouth, dx=0, bob=0, tilt=0):
    tail(cv, (CX - 7 + dx, TOP + 14), phase=wag(t, n), flip=-1, length=8)
    skeptic_sweater(cv, CX + dx, TOP + bob)
    head(cv, CX + dx, CY + bob, eyes=eyes, brows=brows, mouth=mouth, tilt=tilt)


def dangling_monocle(cv, cx, top, swing=0):
    """Monokel terlepas dari mata, tergantung pada rantainya di dada."""
    x, y = cx + 5 + swing, top + 6
    cv.fill(chain([(cx + 6, top - 4), (cx + 7, top), (x, y - 3)], 0.4), "O")
    cv.fill({p for p in ellipse(x, y, 3.0, 3.0)} - {p for p in ellipse(x, y, 1.9, 1.9)}, "O")


def skeptic_thinking_frame(i):
    """Telunjuk di dagu, kepala sedikit miring, monokel berkilau, stempel diam di pangkuan; "..." lalu "?"."""
    cv = Canvas()
    t = i % 16
    skeptic_look(cv, t, 16, "blink" if t == 4 else "side", "raised", "flat" if t < 8 else "smirk", tilt=1)
    monocle(cv, CX, CY, glint=t in (9, 10))
    stamp(cv, CX - 12, TOP + 10)
    arm(cv, (CX - 7, TOP + 3), (CX - 9, TOP + 9), elbow=(CX - 12, TOP + 6), fur="v")
    arm(cv, (CX + 7, TOP + 3), (CX + 3, CY + 9 + (t % 2 if t >= 5 else 0)), elbow=(CX + 11, TOP + 7), fur="v")
    if 5 <= t <= 13:
        dots_or_mark(cv, CX + 12, 0, 5, t, "?")
    return cv


def skeptic_victory_frame(i):
    """Stempel diangkat; tangan lain menggosok monokel dengan sapu tangan putih, senyum puas (khas).
    Tanpa lompat dan tanpa konfeti (role netral, 7.3)."""
    cv = Canvas()
    t = i % 16
    phase = VIC[t][0]
    up = phase == "up"
    skeptic_look(cv, t, 16, "happy" if up else "look", "raised", "smirk" if up else "smile")
    if not up:
        monocle(cv, CX, CY)
    if phase == "rest":
        arm(cv, (CX + 7, TOP + 3), (CX - 5, TOP + 7), elbow=(CX + 10, TOP + 8), fur="v")
        arm(cv, (CX - 7, TOP + 3), (CX + 5, TOP + 6), elbow=(CX - 10, TOP + 8), fur="v")
        stamp(cv, CX + 12, TOP + 11)
        return cv
    hy = TOP - 1 if phase == "mid" else TOP - 7
    stamp(cv, CX + 12, hy)
    arm(cv, (CX + 7, TOP + 3), (CX + 15, hy + 5), elbow=(CX + 14, TOP + 3), fur="v")
    if up:  # monokel dilepas dan digosok sapu tangan putih di depan dada; sapu tangan bergeser kiri-kanan
        mx, my = CX - 4, TOP + 3
        cv.fill(chain([(CX + 6, TOP - 2), (CX + 2, TOP + 2), (mx + 2, my + 2)], 0.4), "O")
        cv.fill({p for p in ellipse(mx, my, 3.2, 3.2)} - {p for p in ellipse(mx, my, 2.0, 2.0)}, "O")
        if t % 4 == 0:
            cv.fill({(mx - 1, my - 1), (mx, my - 2)}, "W")
        rub = (t % 2) * 3
        cv.fill(rect(mx - 3 + rub, my + 1, 4, 4), "W")
        cv.fill({(mx - 3 + rub, my + 5), (mx - 2 + rub, my + 5)}, "G")
        arm(cv, (CX - 7, TOP + 3), (mx - 2 + rub, my + 4), elbow=(CX - 12, TOP + 6), fur="v")
    else:
        arm(cv, (CX - 7, TOP + 3), (CX - 7, TOP + 9), elbow=(CX - 12, TOP + 6), fur="v")
    return cv


def skeptic_defeated_frame(i):
    """Lunglai: monokel lepas dan tergantung di rantai, stempel terjatuh miring di lantai, tangan terkulai;
    menghela napas."""
    cv = Canvas()
    t = i % 16
    sag = 2 + (1 if 6 <= t <= 9 else 0)
    tail(cv, (CX - 7, TOP + 14), phase=wag(t, 16) * 0.5, flip=-1, length=8)
    skeptic_sweater(cv, CX, TOP + 1)
    head(cv, CX, CY + sag, eyes="blink" if t == 12 else "relief", brows="worried", mouth="frown")
    dangling_monocle(cv, CX, TOP + 1, swing=(0, 1, 0, -1)[(t // 2) % 4])
    solid(cv, rect(CX + 13, TOP + 15, 4, 7 - 5), "R", None)  # bantalan stempel rebah
    solid(cv, capsule((CX + 17, TOP + 15), (CX + 21, TOP + 15), 1.2), "N", None)
    arm(cv, (CX - 7, TOP + 4), (CX - 10, TOP + 13), elbow=(CX - 11, TOP + 8), fur="v")
    arm(cv, (CX + 7, TOP + 4), (CX + 10, TOP + 13), elbow=(CX + 11, TOP + 8), fur="v")
    if 6 <= t <= 9:
        sigh(cv, CX - 16, CY - 1, t - 6)
    return cv


def skeptic_shocked_frame(i):
    """Monokel terlepas dari mata dan terayun di rantai, badan tersentak mundur, mata lebar, "!"."""
    cv = Canvas()
    t = i % 12
    phase, dx = SHOCK[t]
    skeptic_look(cv, t, 12, *shock_face(phase), dx=dx)
    if phase == "calm":
        monocle(cv, CX + dx, CY)
    else:
        dangling_monocle(cv, CX + dx, TOP, swing=(1, -1)[t % 2])
        bang(cv)
        spark_lines(cv, CX - 15 + dx, 6)
    arm(cv, (CX + 7 + dx, TOP + 3), (CX - 5 + dx, TOP + 7), elbow=(CX + 10 + dx, TOP + 8), fur="v")
    arm(cv, (CX - 7 + dx, TOP + 3), (CX + 5 + dx, TOP + 6), elbow=(CX - 10 + dx, TOP + 8), fur="v")
    stamp(cv, CX + 12, TOP + 11)
    return cv


def skeptic_happy_frame(i):
    """Senyum kecil puas, monokel berkilau, stempel ditepuk-tepukkan pelan ke telapak tangan; mengangguk."""
    cv = Canvas()
    t = i % 12
    skeptic_look(cv, t, 12, happy_eyes(t), "raised", "smile", bob=nod12(t))
    monocle(cv, CX, CY + nod12(t), glint=t in (3, 4))
    tap = t % 3 == 1
    arm(cv, (CX - 7, TOP + 3), (CX - 4, TOP + 9), elbow=(CX - 11, TOP + 7), fur="v")
    stamp(cv, CX - 1, TOP + 3 + (1 if tap else 0))
    arm(cv, (CX + 7, TOP + 3), (CX + 2, TOP + 1 + (1 if tap else 0)), elbow=(CX + 11, TOP + 6), fur="v")
    return cv


# ================================================================== Champion
def champion_look(cv, t, n, eyes, mouth, dx=0, bob=0):
    tail(cv, (CX - 6 + dx, TOP + 14 + bob), phase=wag(t, n), flip=-1, length=8)
    champion_body(cv, CX + dx, TOP + bob)
    head(cv, CX + dx, CY + bob, eyes=eyes, brows="flat", mouth=mouth)


def champion_thinking_frame(i):
    """Piala di pangkuan dipandangi, tangan kanan di dagu; "..." lalu "?"."""
    cv = Canvas()
    t = i % 16
    champion_look(cv, t, 16, "blink" if t == 4 else ("down" if t < 6 else "side"), "flat" if t < 8 else "frown")
    trophy(cv, CX - 13, TOP + 6)
    arm(cv, (CX - 7, TOP + 3), (CX - 9, TOP + 11), elbow=(CX - 12, TOP + 7))
    arm(cv, (CX + 7, TOP + 3), (CX + 3, CY + 9 + (t % 2 if t >= 5 else 0)), elbow=(CX + 11, TOP + 7))
    if 5 <= t <= 13:
        dots_or_mark(cv, CX + 12, 0, 5, t, "?")
    return cv


def champion_defeated_frame(i):
    """Lunglai: piala diletakkan di lantai kanan, medali tetap di selempang, tangan terkulai; menghela napas."""
    cv = Canvas()
    t = i % 16
    sag = 2 + (1 if 6 <= t <= 9 else 0)
    tail(cv, (CX - 6, TOP + 14), phase=wag(t, 16) * 0.5, flip=-1, length=8)
    champion_body(cv, CX, TOP + 1)
    head(cv, CX, CY + sag, eyes="blink" if t == 12 else "relief", brows="worried", mouth="frown")
    trophy(cv, CX + 13, TOP + 7)
    arm(cv, (CX - 7, TOP + 4), (CX - 10, TOP + 13), elbow=(CX - 11, TOP + 8))
    arm(cv, (CX + 7, TOP + 4), (CX + 9, TOP + 13), elbow=(CX + 11, TOP + 8))
    if 6 <= t <= 9:
        sigh(cv, CX - 16, CY - 1, t - 6)
    return cv


def champion_shocked_frame(i):
    """Piala hampir tergelincir dari tangan (merosot), badan tersentak mundur, mata lebar, "!"."""
    cv = Canvas()
    t = i % 12
    phase, dx = SHOCK[t]
    champion_look(cv, t, 12, *(("look", "smile") if phase == "calm" else ("wide", "o")), dx=dx)
    if phase == "calm":
        trophy(cv, CX + 10 + dx, TOP - 4)
        arm(cv, (CX + 7 + dx, TOP + 3), (CX + 14 + dx, TOP + 7), elbow=(CX + 12 + dx, TOP + 10))
        arm(cv, (CX - 7 + dx, TOP + 3), (CX - 7 + dx, TOP + 9), elbow=(CX - 12 + dx, TOP + 6))
    else:
        slip = 3 + (t % 2)
        trophy(cv, CX + 11 + dx, TOP - 4 + slip)
        arm(cv, (CX + 7 + dx, TOP + 3), (CX + 14 + dx, TOP + 8 + slip), elbow=(CX + 12 + dx, TOP + 10))
        arm(cv, (CX - 7 + dx, TOP + 3), (CX - 13 + dx, TOP + 1), elbow=(CX - 12 + dx, TOP + 7))
        bang(cv, 46, 2)
        spark_lines(cv, CX - 15 + dx, 6)
    return cv


def heart(cv, x, y):
    cv.fill({(x, y), (x + 1, y), (x + 3, y), (x + 4, y), (x - 0, y + 1), (x + 1, y + 1), (x + 2, y + 1), (x + 3, y + 1),
             (x + 4, y + 1), (x + 1, y + 2), (x + 2, y + 2), (x + 3, y + 2), (x + 2, y + 3)}, "R")


def champion_happy_frame(i):
    """Memeluk piala di dada dengan senyum kecil, hati kecil muncul sebentar; mengangguk."""
    cv = Canvas()
    t = i % 12
    champion_look(cv, t, 12, happy_eyes(t), "smile", bob=nod12(t))
    trophy(cv, CX - 4, TOP + 3)
    arm(cv, (CX - 7, TOP + 3), (CX - 3, TOP + 9), elbow=(CX - 12, TOP + 7))
    arm(cv, (CX + 7, TOP + 3), (CX + 3, TOP + 9), elbow=(CX + 12, TOP + 7))
    if 4 <= t <= 8:
        heart(cv, CX + 12, 6 - (t - 4) // 2)
    return cv


def champion_dance_a_frame(i):
    """Joget juara: piala diangkat satu tangan bergantian di sisi kiri dan kanan, di antaranya dipeluk di dada;
    badan bergeser per beat (16 x 120 ms). Piala tidak pernah di depan wajah."""
    cv = Canvas()
    t = i % 16
    beat = t // 4
    dx, bob, move = DANCE[beat]
    tail(cv, (CX - 6 + dx, TOP + 14 + bob), phase=beat * 1.6 + (t % 4) * 0.25, flip=-1, length=8)
    champion_body(cv, CX + dx, TOP + bob)
    head(cv, CX + dx, CY + bob, eyes="happy", brows="flat", mouth="smile" if beat % 2 == 0 else "o")
    sh = TOP + 3 + bob
    if move == "low":
        trophy(cv, CX - 4 + dx, TOP + 3 + bob)
        arm(cv, (CX - 7 + dx, sh), (CX - 3 + dx, TOP + 9 + bob), elbow=(CX - 12 + dx, TOP + 7 + bob))
        arm(cv, (CX + 7 + dx, sh), (CX + 3 + dx, TOP + 9 + bob), elbow=(CX + 12 + dx, TOP + 7 + bob))
        return cv
    s = -1 if move == "left" else 1
    tx = CX + dx + s * 17 - 4
    trophy(cv, tx, 1)
    arm(cv, (CX + dx + s * 7, sh), (tx + 4, 11), elbow=(CX + dx + s * 15, TOP + 1))
    arm(cv, (CX + dx - s * 7, sh), (CX + dx - s * 7, TOP + 9), elbow=(CX + dx - s * 12, TOP + 6))
    return cv


# ================================================================== Greek Philosopher
def greek_look(cv, t, eyes, brows, dx=0, bob=0, wag_=0):
    column(cv, 3, 8, 45)
    tail(cv, (GX + 5 + dx, TOP + 14), phase=wag(t, 12), flip=1, length=8)
    from costumes import dressed_body, inner
    torso = dressed_body(cv, GX + dx, TOP + bob, "C", "c", pants="C", pants_shade="c")
    top = TOP + bob
    cv.fill({(x, y) for (x, y) in inner(torso) if abs((x - GX - dx) - (y - top) + 5) <= 1}, "c")
    cv.fill({(x, y) for (x, y) in inner(torso) if abs((x - GX - dx) - (y - top) + 5) == 2 and y % 2 == 0}, "m")
    greek_head(cv, GX + dx, CY + bob, eyes, brows, wag=wag_)


def greek_shocked_frame(i):
    """Gulungan terlepas dan jatuh ke lantai, badan tersentak ke kanan, mata lebar, "!"."""
    cv = Canvas()
    t = i % 12
    phase, dx = SHOCK[t]
    dx = -dx  # menjauh dari tiang
    greek_look(cv, t, "look" if phase == "calm" else "wide", "flat" if phase == "calm" else "up", dx=dx)
    if phase == "calm":
        arm(cv, (GX + 7 + dx, TOP + 3), (GX + 9 + dx, TOP + 9), elbow=(GX + 11 + dx, TOP + 5))
        arm(cv, (GX - 7 + dx, TOP + 3), (GX - 9 + dx, TOP + 9), elbow=(GX - 11 + dx, TOP + 5))
        scroll(cv, GX - 10 + dx, TOP + 5, vertical=True)
    else:
        fall = min(8, (t - 2) * 3)
        scroll(cv, GX - 16, TOP + 5 + fall if fall < 8 else TOP + 16)
        arm(cv, (GX + 7 + dx, TOP + 3), (GX + 13 + dx, TOP + 1), elbow=(GX + 12 + dx, TOP + 7))
        arm(cv, (GX - 7 + dx, TOP + 3), (GX - 13 + dx, TOP + 1), elbow=(GX - 12 + dx, TOP + 7))
        bang(cv, 52, 2)
    return cv


def greek_happy_frame(i):
    """Mengelus janggut dengan senyum puas (mata tersenyum), gulungan dipegang di sisi; mengangguk."""
    cv = Canvas()
    t = i % 12
    stroke = (t // 2) % 2
    greek_look(cv, t, happy_eyes(t), "flat", bob=nod12(t), wag_=stroke)
    arm(cv, (GX + 7, TOP + 3), (GX + 2, CY + 10 + stroke + nod12(t)), elbow=(GX + 10, TOP + 5))
    arm(cv, (GX - 7, TOP + 3), (GX - 11, TOP + 2), elbow=(GX - 12, TOP + 7))
    scroll(cv, GX - 13, TOP - 5, vertical=True)
    return cv


# ================================================================== Academic
def academic_look(cv, t, eyes, brows, mouth, bob=0, lift=0, tassel=None):
    tail(cv, (26, AT + 14), phase=wag(t, 12), flip=-1, length=8)
    from costumes import dressed_body
    top = AT + bob
    dressed_body(cv, CX, top, "W", "G")
    cv.fill(capsule((CX, top + 2), (CX, top + 9), 0.8), "R")
    cv.fill({(CX - 1, top + 1), (CX, top + 1), (CX + 1, top + 1)}, "R")
    cv.fill({(CX - 3, top), (CX - 2, top + 1), (CX + 3, top), (CX + 2, top + 1)}, "G")
    head(cv, CX, AY + bob, eyes=eyes, brows=brows, mouth=mouth)
    mortarboard(cv, CX, AY + bob, tassel=(t // 2) % 2 if tassel is None else tassel, lift=lift)


def academic_shocked_frame(i):
    """Topi toga terlonjak dari kepala, ijazah didekap ke dada, mata lebar, "!"."""
    cv = Canvas()
    t = i % 12
    phase = SHOCK[t][0]
    calm = phase == "calm"
    academic_look(cv, t, "look" if calm else "wide", "flat" if calm else "up", "flat" if calm else "o",
                  lift=0 if calm else (4 if phase == "jolt" else 2 + (t % 2)), tassel=None if calm else 1)
    if calm:
        arm(cv, (CX - 7, AT + 3), (CX - 9, AT + 8), elbow=(CX - 11, AT + 5), fur="W")
        scroll(cv, CX - 13, AT + 8)
        arm(cv, (CX + 7, AT + 3), (CX + 9, AT + 10), elbow=(CX + 10, AT + 6), fur="W")
    else:
        scroll(cv, CX - 4, AT + 4)
        arm(cv, (CX - 7, AT + 3), (CX - 3, AT + 6), elbow=(CX - 11, AT + 7), fur="W")
        arm(cv, (CX + 7, AT + 3), (CX + 3, AT + 6), elbow=(CX + 11, AT + 7), fur="W")
        bang(cv, 48, 1)
        spark_lines(cv, CX - 15, 6)
    return cv


def academic_happy_frame(i):
    """Senyum kecil, rumbai topi berayun, ijazah terbuka diangkat sedikit di depan dada; mengangguk."""
    cv = Canvas()
    t = i % 12
    academic_look(cv, t, happy_eyes(t), "flat", "smile", bob=nod12(t))
    open_diploma(cv, CX - 7, AT + 5 + nod12(t))
    arm(cv, (CX - 7, AT + 3), (CX - 7, AT + 9), elbow=(CX - 11, AT + 6), fur="W")
    arm(cv, (CX + 7, AT + 3), (CX + 7, AT + 9), elbow=(CX + 11, AT + 6), fur="W")
    return cv


# ================================================================== Scientist
def scientist_defeated_frame(i):
    """Rebah menyamping di lantai depan papan tulis (E=mc tetap di tempatnya), kapur terlepas; menghela napas."""
    cv = Canvas()
    t = i % 16
    chalkboard(cv, 34, 6, 29, 16, "E=mc", 4)
    hx, hy = 12, 36
    breathe = 1 if t in (6, 7, 8) else 0
    tail(cv, (hx + 22, hy - 1), phase=wag(t, 16) * 0.5, flip=1, length=6, curl=2.2)
    wild_hair(cv, hx, hy, bounce=0)
    lying_body(cv, hx, hy, "h", "g", pants="g", pants_shade="q", breathe=breathe, belly=False)
    head(cv, hx, hy, eyes="blink" if t == 12 else "relief", brows="worried", mouth="flat")
    wild_hair(cv, hx, hy, back=False)
    einstein_moustache(cv, hx, hy)
    arm(cv, (hx + 9, hy + 5), (hx + 8, 44), elbow=(hx + 12, hy + 8), fur="h")
    chalk(cv, hx + 22, 45)
    if 6 <= t <= 9:
        sigh(cv, hx + 2, hy - 13, t - 6)
    return cv


def scientist_happy_frame(i):
    """Senyum kecil sambil menggaruk rambut dengan riang, kapur mengetuk papan pelan."""
    cv = Canvas()
    t = i % 12
    from domains import scientist_base
    scratch = (t // 2) % 2
    scientist_base(cv, t, happy_eyes(t), "flat", bounce=scratch)
    head(cv, SX, CY, eyes=happy_eyes(t), brows="flat", mouth="smile")
    wild_hair(cv, SX, CY, back=False)
    einstein_moustache(cv, SX, CY)
    arm(cv, (SX - 7, TOP + 3), (SX - 7, CY - 8 + scratch), elbow=(SX - 13, CY + 2), fur="h")
    tap = t % 4 == 1
    arm(cv, (SX + 7, TOP + 3), (SX + 13 + (1 if tap else 0), TOP + 2), elbow=(SX + 12, TOP + 8), fur="h")
    chalk(cv, SX + 14 + (1 if tap else 0), TOP)
    return cv


# ================================================================== Mathematician
def math_look(cv, t, n, eyes, brows, mouth, dx=0, bob=0):
    tail(cv, (CX - 7 + dx, TOP + 14), phase=wag(t, n), flip=-1, length=8)
    math_vest(cv, CX + dx, TOP + bob)
    head(cv, CX + dx, CY + bob, eyes=eyes, brows=brows, mouth=mouth)


def math_defeated_frame(i):
    """Lunglai: batu tulis terjatuh di lantai, jangka tergeletak terbuka, tangan terkulai; menghela napas."""
    cv = Canvas()
    t = i % 16
    sag = 2 + (1 if 6 <= t <= 9 else 0)
    tail(cv, (CX - 7, TOP + 14), phase=wag(t, 16) * 0.5, flip=-1, length=8)
    math_vest(cv, CX, TOP + 1)
    head(cv, CX, CY + sag, eyes="blink" if t == 12 else "relief", brows="worried", mouth="frown")
    slate(cv, CX + 12, TOP + 12, arc=5)
    compass(cv, CX - 19, TOP + 15, 0, spread=30)
    arm(cv, (CX - 7, TOP + 4), (CX - 10, TOP + 13), elbow=(CX - 11, TOP + 8))
    arm(cv, (CX + 7, TOP + 4), (CX + 9, TOP + 13), elbow=(CX + 11, TOP + 8))
    if 6 <= t <= 9:
        sigh(cv, CX - 16, CY - 1, t - 6)
    return cv


def math_shocked_frame(i):
    """Jangka terlonjak dari tangan, batu tulis diangkat ke depan dada, mundur, mata lebar, "!"."""
    cv = Canvas()
    t = i % 12
    phase, dx = SHOCK[t]
    math_look(cv, t, 12, *shock_face(phase), dx=dx)
    if phase == "calm":
        slate(cv, CX - 5 + dx, TOP + 8, arc=12)
        arm(cv, (CX - 7 + dx, TOP + 3), (CX - 5 + dx, TOP + 13), elbow=(CX - 11 + dx, TOP + 8))
        compass(cv, CX + 15 + dx, TOP - 3, 90, spread=16)
        arm(cv, (CX + 7 + dx, TOP + 3), (CX + 14 + dx, TOP - 2), elbow=(CX + 13 + dx, TOP + 5))
    else:
        slate(cv, CX - 6 + dx, TOP + 1, arc=12)
        arm(cv, (CX - 7 + dx, TOP + 3), (CX - 5 + dx, TOP + 6), elbow=(CX - 11 + dx, TOP + 8))
        compass(cv, CX + 16 + dx, TOP - 9 - (t % 2), 90 + t * 40, spread=20)
        arm(cv, (CX + 7 + dx, TOP + 3), (CX + 5 + dx, TOP + 6), elbow=(CX + 11 + dx, TOP + 8))
        bang(cv, 48, 1)
        spark_lines(cv, CX - 15 + dx, 6)
    return cv


def math_happy_frame(i):
    """Senyum kecil, jangka memutar satu lingkaran cepat di batu tulis di pangkuan; mengangguk."""
    cv = Canvas()
    t = i % 12
    math_look(cv, t, 12, happy_eyes(t), "flat", "smile", bob=nod12(t))
    sx, sy = CX - 5, TOP + 8
    slate(cv, sx, sy, arc=t + 1)
    arm(cv, (CX - 7, TOP + 3), (sx, sy + 5), elbow=(CX - 11, TOP + 7))
    a = t / 12.0 * math.tau
    px, py = sx + 5 + 2.4 * math.cos(a), sy + 4 + 1.6 * math.sin(a)
    compass(cv, px + 1, py - 7, -90, spread=8)
    arm(cv, (CX + 7, TOP + 3), (int(px) + 2, int(py) - 7), elbow=(CX + 11, TOP + 7))
    return cv


# ================================================================== Lawyer
def lawyer_look(cv, t, n, eyes, brows, mouth, dx=0, bob=0, tilt=0):
    tail(cv, (CX - 7 + dx, TOP + 14), phase=wag(t, n), flip=-1, length=8)
    lawyer_suit(cv, CX + dx, TOP + bob)
    head(cv, CX + dx, CY + bob, eyes=eyes, brows=brows, mouth=mouth, tilt=tilt)


def loose_papers(cv, x, y):
    """Kertas berkas yang meluncur keluar dari map di lantai."""
    for k, (dx, dy) in enumerate(((0, 0), (5, -1), (10, 1))):
        solid(cv, rect(x + dx, y + dy, 6, 3), "W", "G", shade_off=(1, 1))
        cv.fill(rect(x + dx + 1, y + dy + 1, 3, 1), "c")


def lawyer_defeated_frame(i):
    """Lunglai: map terjatuh terbuka di lantai dengan kertas meluncur keluar, dasi miring; menghela napas."""
    cv = Canvas()
    t = i % 16
    sag = 2 + (1 if 6 <= t <= 9 else 0)
    tail(cv, (CX - 7, TOP + 14), phase=wag(t, 16) * 0.5, flip=-1, length=8)
    lawyer_suit(cv, CX, TOP + 1)
    cv.fill({(CX, TOP + 4), (CX + 1, TOP + 5), (CX + 1, TOP + 6)}, "P")  # dasi miring
    head(cv, CX, CY + sag, eyes="blink" if t == 12 else "relief", brows="worried", mouth="frown")
    solid(cv, rect(CX + 11, TOP + 14, 10, 3), "U", "u", shade_off=(1, 1))
    loose_papers(cv, CX - 25, TOP + 15)
    arm(cv, (CX - 7, TOP + 4), (CX - 10, TOP + 13), elbow=(CX - 11, TOP + 8), fur="J")
    arm(cv, (CX + 7, TOP + 4), (CX + 10, TOP + 13), elbow=(CX + 11, TOP + 8), fur="J")
    if 6 <= t <= 9:
        sigh(cv, CX - 17, CY - 3, t - 6)
    return cv


def lawyer_shocked_frame(i):
    """Map didekap ke dada, badan tersentak mundur, mata lebar, "!"."""
    cv = Canvas()
    t = i % 12
    phase, dx = SHOCK[t]
    lawyer_look(cv, t, 12, *shock_face(phase), dx=dx)
    if phase == "calm":
        folder(cv, CX - 20 + dx, TOP + 3)
        arm(cv, (CX - 7 + dx, TOP + 3), (CX - 11 + dx, TOP + 8), elbow=(CX - 12 + dx, TOP + 5), fur="J")
        arm(cv, (CX + 7 + dx, TOP + 3), (CX + 9 + dx, TOP + 10), elbow=(CX + 10 + dx, TOP + 6), fur="J")
    else:
        folder(cv, CX - 5 + dx, TOP + 3)
        arm(cv, (CX - 7 + dx, TOP + 3), (CX - 4 + dx, TOP + 8), elbow=(CX - 11 + dx, TOP + 7), fur="J")
        arm(cv, (CX + 7 + dx, TOP + 3), (CX + 4 + dx, TOP + 8), elbow=(CX + 11 + dx, TOP + 7), fur="J")
        bang(cv, 48, 1)
        spark_lines(cv, CX - 15 + dx, 6)
    return cv


def lawyer_happy_frame(i):
    """Senyum kecil, menepuk map yang dikepit dengan puas; mengangguk."""
    cv = Canvas()
    t = i % 12
    lawyer_look(cv, t, 12, happy_eyes(t), "flat", "smile", bob=nod12(t))
    folder(cv, CX - 20, TOP + 3)
    arm(cv, (CX - 7, TOP + 3), (CX - 11, TOP + 8), elbow=(CX - 12, TOP + 5), fur="J")
    pat = t % 4 in (1, 2)
    arm(cv, (CX + 7, TOP + 3), (CX - 12, TOP + 3 + (1 if pat else 0)), elbow=(CX + 2, TOP + 9), fur="J")
    return cv


# ================================================================== Hacker
def hacker_defeated_frame(i):
    """Jendela terminal meredup lalu tertutup (f3 ke atas tidak ada jendela), badan merosot di balik laptop,
    kacamata melorot, tangan terkulai dari keyboard; "..." lemas."""
    cv = Canvas()
    t = i % 16
    if t < 3:
        terminal(cv, t, scroll=False, color="l")
    sag = 3
    hacker_base(cv, t, "relief", "worried", "frown", glasses_dy=3, bob=sag,
                hands=((HX - 11, 38), (HX + 11, 38)))
    if 6 <= t <= 12:
        thought_dots(cv, 4, 2, 1 + min(2, (t - 6) // 2))
    return cv


def hacker_happy_frame(i):
    """Senyum kecil sambil mengetik cepat, baris kode hijau bergulir lebih cepat, kilau kecil di layar."""
    cv = Canvas()
    t = i % 12
    terminal(cv, t * 2, scroll=True, color="Z")
    hacker_base(cv, t, "happy" if 3 <= t <= 8 else "down", "flat", "smile", hands=typing(t))
    if t % 4 == 1:
        cv.fill({(58, 26), (57, 26), (59, 26), (58, 25), (58, 27)}, "W")
    return cv


# ================================================================== Detective
def detective_defeated_frame(i):
    """Lunglai: topi merosot ke depan, kaca pembesar terjatuh di lantai, tangan terkulai; menghela napas."""
    cv = Canvas()
    t = i % 16
    sag = 2 + (1 if 6 <= t <= 9 else 0)
    detective_base(cv, t, "blink" if t == 12 else "relief", "worried", "frown", bob=1, hat_lift=-1)
    head_cover = sag - 1
    if head_cover:
        from costumes import deerstalker
        from monkey import head as _h
        _h(cv, CX, CY + sag, eyes="blink" if t == 12 else "relief", brows="worried", mouth="frown")
        deerstalker(cv, CX, CY + sag - 1)
    magnifier(cv, CX + 17, TOP + 12)
    arm(cv, (CX - 7, TOP + 4), (CX - 10, TOP + 13), elbow=(CX - 11, TOP + 8), fur="d")
    arm(cv, (CX + 7, TOP + 4), (CX + 9, TOP + 13), elbow=(CX + 11, TOP + 8), fur="d")
    if 6 <= t <= 9:
        sigh(cv, CX - 16, CY - 1, t - 6)
    return cv


def detective_happy_frame(i):
    """Senyum kecil, mengangguk, kaca pembesar diketuk-ketukkan pelan ke telapak tangan."""
    cv = Canvas()
    t = i % 12
    detective_base(cv, t, happy_eyes(t), "flat", "smile", bob=nod12(t))
    tap = t % 3 == 1
    lx, ly = CX + 4, TOP + 1 + (1 if tap else 0)
    magnifier(cv, lx, ly)
    arm(cv, (CX + 7, TOP + 3), (lx + 4, ly + 5), elbow=(CX + 11, TOP + 8), fur="d")
    arm(cv, (CX - 7, TOP + 3), (CX - 1, TOP + 8), elbow=(CX - 11, TOP + 7), fur="d")
    return cv


# ================================================================== registrasi
SCENES = {
    "normal-shocked": (normal_shocked_frame, 12, shock_ms),
    "normal-dance-a": (normal_dance_a_frame, 16, ms_const(120)),
    "referee-victory": (referee_victory_frame, 16, lambda i: 150 if i % 16 in (0, 1, 14, 15) else 120),
    "referee-defeated": (referee_defeated_frame, 16, defeated_ms),
    "referee-shocked": (referee_shocked_frame, 12, shock_ms),
    "referee-happy": (referee_happy_frame, 12, ms_const(150)),
    "judge-victory": (judge_victory_frame, 16, lambda i: 150 if i % 16 in (0, 1, 14, 15) else 130),
    "judge-defeated": (judge_defeated_frame, 16, defeated_ms),
    "judge-shocked": (judge_shocked_frame, 12, shock_ms),
    "judge-happy": (judge_happy_frame, 12, ms_const(150)),
    "skeptic-thinking": (skeptic_thinking_frame, 16, ms_const(170)),
    "skeptic-victory": (skeptic_victory_frame, 16, lambda i: 150 if i % 16 in (0, 1, 14, 15) else 130),
    "skeptic-defeated": (skeptic_defeated_frame, 16, defeated_ms),
    "skeptic-shocked": (skeptic_shocked_frame, 12, shock_ms),
    "skeptic-happy": (skeptic_happy_frame, 12, ms_const(150)),
    "champion-thinking": (champion_thinking_frame, 16, ms_const(170)),
    "champion-defeated": (champion_defeated_frame, 16, defeated_ms),
    "champion-shocked": (champion_shocked_frame, 12, shock_ms),
    "champion-happy": (champion_happy_frame, 12, ms_const(150)),
    "champion-dance-a": (champion_dance_a_frame, 16, ms_const(120)),
    "greek-philosopher-shocked": (greek_shocked_frame, 12, shock_ms),
    "greek-philosopher-happy": (greek_happy_frame, 12, ms_const(150)),
    "academic-shocked": (academic_shocked_frame, 12, shock_ms),
    "academic-happy": (academic_happy_frame, 12, ms_const(150)),
    "scientist-defeated": (scientist_defeated_frame, 16, defeated_ms),
    "scientist-happy": (scientist_happy_frame, 12, ms_const(150)),
    "mathematician-defeated": (math_defeated_frame, 16, defeated_ms),
    "mathematician-shocked": (math_shocked_frame, 12, shock_ms),
    "mathematician-happy": (math_happy_frame, 12, ms_const(150)),
    "lawyer-defeated": (lawyer_defeated_frame, 16, defeated_ms),
    "lawyer-shocked": (lawyer_shocked_frame, 12, shock_ms),
    "lawyer-happy": (lawyer_happy_frame, 12, ms_const(150)),
    "hacker-defeated": (hacker_defeated_frame, 16, defeated_ms),
    "hacker-happy": (hacker_happy_frame, 12, ms_const(150)),
    "detective-defeated": (detective_defeated_frame, 16, defeated_ms),
    "detective-happy": (detective_happy_frame, 12, ms_const(150)),
}

PROPS = {
    "judge: timbangan (victory)": lambda cv: balance_scale(cv, 30, 16),
    "skeptic: monokel tergantung": lambda cv: dangling_monocle(cv, 30, 20),
    "lawyer: kertas berkas": lambda cv: loose_papers(cv, 20, 24),
    "champion: hati kecil": lambda cv: heart(cv, 30, 20),
}
