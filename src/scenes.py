"""Animasi Gobyet: ngopi santai, makan pisang sambil garuk pantat, ngamuk ke laptop gara-gara debug."""
from monkey import (Canvas, head, arm, tail, sitting_body, banana, laptop, mug, mini_text, bubble, puff,
                    spark_lines, ellipse, solid, edge)


def belly(cv, cx, cy, rx, ry, torso):
    b = {p for p in ellipse(cx, cy, rx, ry) if p in torso and p not in edge(torso)}
    cv.fill(b, "F")
    cv.fill({(x, y) for (x, y) in b if (x, y + 1) not in b}, "f")


# ------------------------------------------------------------------ 1. marah karena debug
RAGE_TEXT = ["#@!", "%&!", "#!*", "@!?"]


def rage_frame(i):
    cv = Canvas()
    cx, cy = 33, 16
    t = i % 28
    face, eyes, brows, mouth = "F", "down", "flat", "flat"
    lh, rh = (28, 28), (38, 28)
    le, re = (22, 31), (44, 31)
    shake = lift = bob = steam = 0
    symbols, alert = None, False
    if t < 7:  # mengetik tenang
        lh, rh = (28, 28 - (t % 2)), (38, 27 + (t % 2))
        if t == 4:
            eyes = "blink"
    elif t < 10:  # error muncul
        eyes, brows, mouth, alert = "wide", "up", "o", True
        face = "A" if t >= 8 else "F"
    elif t < 22:  # ngamuk: tinju naik, lalu banting
        face, eyes, brows, mouth = "A", "angry", "angry", "shout"
        up = t % 2 == 0
        if up:
            lh, rh, le, re = (20, 17), (46, 17), (19, 24), (47, 24)
        else:
            lh, rh = (28, 28), (38, 28)
            shake, lift, bob = (1 if t % 4 == 1 else -1), 2, 1
        symbols = RAGE_TEXT[(t // 2) % 4]
        steam = 1 + t % 3
    else:  # capek, menghela napas
        eyes, brows, mouth = ("blink" if t in (23, 24) else "relief"), "worried", "frown"
    tail(cv, (26, 37), phase=t * 0.5, flip=-1, length=8)
    torso = ellipse(cx, 32 + bob, 9.5, 7.5)
    solid(cv, torso, "B", "b")
    belly(cv, cx, 34 + bob, 5.5, 5, torso)
    head(cv, cx, cy + bob, eyes=eyes, brows=brows, mouth=mouth, face=face,
         tilt=(1 if shake > 0 else -1 if shake < 0 else 0))
    if t >= 22 and t <= 25:
        puff(cv, cx + 3, cy + 7 + (t - 22), 1.3 + (t - 22) * 0.35)
    if steam:  # uap keluar dari telinga, naik dan membesar
        for s in (-1, 1):
            k = (steam + (s > 0)) % 3
            puff(cv, cx + s * (12 + k), cy - 1 - k * 2, 1.7 + k * 0.6)
    laptop(cv, 23, 29, shake=shake, glow=("R" if face == "A" else None))
    arm(cv, (26, 27 + bob), lh, elbow=le)
    arm(cv, (40, 27 + bob), rh, elbow=re)
    if lift:
        spark_lines(cv, 21, 25)
        spark_lines(cv, 44, 25)
    mug(cv, 4, 36, lift=lift, steam=t)
    if alert:
        bubble(cv, 46, 4, 9, 9, fill="R", tail_dir=-1)
        mini_text(cv, "!", 48, 6, "W")
    if symbols:
        bubble(cv, 43, 0, 21, 9, fill="W", tail_dir=-1)
        mini_text(cv, symbols, 45, 2, "R")
    return cv


# ------------------------------------------------------------------ 2. makan pisang + garuk pantat
# (gigitan, angkat ke mulut, mulut, mata, garuk)
BANANA_SCRIPT = [
    (0, 0, "smile", "look", 0), (0, 0, "smile", "look", 0), (0, 1, "o", "look", 0), (1, 1, "chomp", "happy", 0),
    (1, 0, "chew", "happy", 0), (1, 0, "chomp", "happy", 0), (1, 0, "chew", "happy", 0), (1, 1, "o", "look", 0),
    (2, 1, "chomp", "happy", 0), (2, 0, "chew", "happy", 0), (2, 0, "chomp", "happy", 0),
    (2, 0, "flat", "relief", 1), (2, 0, "flat", "relief", 2), (2, 0, "smile", "relief", 1), (2, 0, "smile", "relief", 2),
    (2, 0, "smile", "relief", 1), (2, 0, "o", "relief", 2), (2, 0, "smile", "relief", 1), (2, 0, "smile", "look", 0),
    (2, 1, "o", "look", 0), (3, 1, "chomp", "happy", 0), (3, 0, "chew", "happy", 0), (3, 0, "chomp", "happy", 0),
    (3, 0, "smile", "happy", 0), (3, 0, "smile", "look", 0),
]


def banana_frame(i):
    cv = Canvas()
    bites, raised, mouth, eyes, scratch = BANANA_SCRIPT[i % len(BANANA_SCRIPT)]
    cx, cy, top = 30, 14, 23
    lean = 1 if scratch else 0
    if scratch:  # tangan menyelinap ke belakang pantat (digambar di belakang badan)
        dy = 0 if scratch == 1 else 2
        arm(cv, (36 - lean, top + 3), (38, top + 13 + dy), elbow=(42, top + 7 + dy // 2))
    tail(cv, (25, top + 14), phase=i * 0.7 + (2 if scratch else 0), flip=-1, length=8)
    sitting_body(cv, cx - lean, top, leg_twitch=(1 if scratch == 2 else 0))
    head(cv, cx - lean, cy, eyes=eyes, brows=("worried" if eyes == "relief" else "flat"), mouth=mouth)
    if scratch:  # garis gerakan menggaruk
        off = scratch - 1
        for k, (x, y) in enumerate(((45, 32), (46, 35), (45, 38))):
            cv.fill({(x + off, y), (x + 1 + off, y + (1 if k != 1 else 0)), (x + 2 + off, y)}, "s")
    else:
        arm(cv, (36, top + 3), (38, top + 11), elbow=(39, top + 7))  # tangan istirahat di paha
    hy = top + 7 - (3 if raised else 0)
    banana(cv, 26.5, hy, bites=bites, peel=(1 if mouth == "chew" else 0))
    arm(cv, (24 - lean, top + 3), (26.5, hy + 1), elbow=(20, top + 8))
    if mouth in ("chomp", "chew") and i % 2 == 0:
        cv.put(cx + 4, cy + 8, "n")
        cv.put(cx + 6, cy + 10, "n")
    return cv


# ------------------------------------------------------------------ 3. santai ngopi (pose gambar asli)
def idle_frame(i):
    cv = Canvas()
    cx, cy = 30, 16
    t = i % 16
    sip = t in (10, 11, 12)
    eyes = "blink" if t == 6 else ("happy" if sip else "side")
    tail(cv, (23, 38), phase=t * 0.45, flip=-1, length=8)
    torso = ellipse(cx, 32, 9.5, 7.5)
    solid(cv, torso, "B", "b")
    belly(cv, cx, 34, 5.5, 5, torso)
    head(cv, cx, cy, eyes=eyes, brows=("flat" if sip else "worried"), mouth=("o" if sip else "frown"))
    # tangan kanan melingkar ke atas menggaruk kepala
    arm(cv, (37, 27), (38, 7 + (t % 2)), elbow=(44, 17))
    laptop(cv, 36, 30)
    if sip:
        mug(cv, 18, 17, steam=t)
        arm(cv, (23, 27), (19, 22), elbow=(17, 29))
    else:
        mug(cv, 7, 29, steam=t)
        arm(cv, (23, 27), (14, 32), elbow=(18, 34))
    return cv


def rage_ms(i):
    t = i % 28
    return 150 if t < 7 else 260 if t < 10 else 95 if t < 22 else 200


def banana_ms(i):
    bites, raised, mouth, eyes, scratch = BANANA_SCRIPT[i % len(BANANA_SCRIPT)]
    return 110 if scratch else 200 if raised else 150


def idle_ms(i):
    return 240 if i % 16 in (10, 11, 12) else 160


# nama: (fungsi frame, jumlah frame, fungsi durasi per frame dalam ms)
SCENES = {"marah-debug": (rage_frame, 28, rage_ms), "makan-pisang": (banana_frame, len(BANANA_SCRIPT), banana_ms),
          "ngopi-santai": (idle_frame, 16, idle_ms)}
