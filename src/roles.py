"""Kostum ROLE Gobyet untuk Battle Royale Argumen (Fase 2, bertahap per gerbang).

Gerbang A: Referee (idle, thinking).
Gerbang B: Judge (idle, thinking, judging), Skeptic (idle, suspicious, attack),
Champion (idle, victory).

Semua memakai rig yang sama dengan aset asli: kanvas 64x48, palet PAL, garis tepi K,
kepala dan badan duduk yang sama. Kostum hanya lapisan di atasnya. Setiap prop dimiliki
satu kostum saja; frame 0 setiap loop adalah pose tetap yang jelas.
"""
import math

from monkey import Canvas, head, arm, tail, sitting_body, mini_text, bubble, ellipse, capsule, chain, rect, edge, solid
from costumes import CX, CY, TOP, dressed_body, inner, confetti


# ------------------------------------------------------------------ perlengkapan wasit
def referee_shirt(cv, cx, top):
    """Kaus wasit putih bergaris hitam tipis, kerah hitam, celana hitam."""
    torso = dressed_body(cv, cx, top, "W", "G", pants="L", pants_shade="q")
    body = {p for p in inner(torso) if p[1] < top + 10}
    cv.fill({(x, y) for (x, y) in body if (x - cx) % 3 == 0}, "P")
    cv.fill({(cx - 3, top), (cx - 2, top + 1), (cx + 3, top), (cx + 2, top + 1)}, "P")
    return torso


def referee_arm(cv, shoulder, hand, elbow):
    """Lengan berbulu Gobyet dengan lengan kaus pendek putih di bahu."""
    arm(cv, shoulder, hand, elbow=elbow)
    solid(cv, ellipse(shoulder[0], shoulder[1] + 0.5, 2.3, 2.0), "W", None)


def whistle(cv, cx, top):
    """Peluit perak di dada kanan, tergantung tali merah yang melingkar dari sisi kiri leher."""
    wx, wy = cx + 3, top + 6
    cv.fill(chain([(cx - 3, top + 0.5), (cx - 1, top + 3), (wx - 2, wy)], 0.45), "R")
    solid(cv, rect(wx - 2, wy - 1, 5, 3), "G", None, outline="l")
    cv.put(wx + 2, wy, "P")


def clipboard(cv, x, y):
    """Papan klip: papan cokelat, kertas putih bergaris, penjepit perak."""
    solid(cv, rect(x, y, 8, 10), "N", None)
    cv.fill(rect(x + 1, y + 2, 6, 7), "W")
    for k in range(3):
        cv.fill(rect(x + 2, y + 4 + k * 2, 4 - (k % 2), 1), "h")
    cv.fill(rect(x + 2, y, 4, 2), "G")


def pencil(cv, x0, y0, x1, y1):
    cv.fill(capsule((x0, y0), (x1, y1), 0.6), "Y")
    cv.put(int(x1), int(y1), "K")


# ------------------------------------------------------------------ Referee / idle
def referee_idle_frame(i):
    """Tangan di pinggang, menoleh kiri dan kanan mengawasi arena, sesekali berkedip."""
    cv = Canvas()
    t = i % 16
    eyes = ("look", "look", "left", "left", "left", "look", "blink", "look",
            "side", "side", "side", "look", "look", "look", "blink", "look")[t]
    bob = 1 if t in (5, 13) else 0
    tail(cv, (26, TOP + 14), phase=t * 0.45, flip=-1, length=8)
    referee_shirt(cv, CX, TOP)
    head(cv, CX, CY + bob, eyes=eyes, brows="flat", mouth="flat")
    whistle(cv, CX, TOP)
    for s in (-1, 1):  # akimbo: siku keluar, telapak di pinggang
        referee_arm(cv, (CX + s * 7, TOP + 3), (CX + s * 7, TOP + 9), (CX + s * 12, TOP + 6))
    return cv


# ------------------------------------------------------------------ Referee / thinking
def referee_thinking_frame(i):
    """Membaca papan klip, mengetuk dagu dengan pensil, lalu muncul tanda tanya."""
    cv = Canvas()
    t = i % 18
    tap = t % 2
    eyes = "blink" if t == 9 else ("down" if t < 6 else "side")
    tail(cv, (26, TOP + 14), phase=t * 0.45, flip=-1, length=8)
    referee_shirt(cv, CX, TOP)
    head(cv, CX, CY, eyes=eyes, brows=("flat" if t < 6 else "worried"), mouth=("flat" if t < 6 else "frown"))
    whistle(cv, CX, TOP)
    # tangan kiri memegang papan klip di depan badan
    clipboard(cv, CX - 15, TOP + 1)
    referee_arm(cv, (CX - 7, TOP + 3), (CX - 8, TOP + 7), (CX - 11, TOP + 7))
    # tangan kanan: pensil mengetuk dagu
    hx, hy = CX + 6, CY + 9 + tap
    referee_arm(cv, (CX + 7, TOP + 3), (hx, hy), (CX + 12, TOP + 4))
    pencil(cv, hx + 1, hy - 1, hx - 2, hy - 4)
    if t >= 6:
        bx, by = CX + 9, 1
        cv.fill({(bx - 3, by + 10), (bx - 2, by + 9)}, "W")
        bubble(cv, bx, by, 11, 9, fill="W", tail_dir=-1)
        if t >= 10:
            mini_text(cv, "?", bx + 3, by + 2, "K")
        else:
            for k in range(1 + (t - 6) % 3):
                cv.put(bx + 2 + k * 3, by + 6, "K")
    return cv


def dots_or_mark(cv, bx, by, t0, t, mark):
    """Gelembung pikiran: titik bertambah (…), lalu satu tanda (?) dari glyph yang ada."""
    cv.fill({(bx - 3, by + 10), (bx - 2, by + 9)}, "W")
    bubble(cv, bx, by, 11, 9, fill="W", tail_dir=-1)
    if t - t0 >= 3:
        mini_text(cv, mark, bx + 3, by + 2, "K")
    else:
        for k in range(1 + (t - t0)):
            cv.put(bx + 2 + k * 3, by + 6, "K")


# ================================================================== Gerbang B: Judge
def judge_robe(cv, cx, top):
    """Jubah hakim hitam lebar berbentuk lonceng menutupi paha, kerah putih dua lidah, kaki mengintip."""
    robe = set()
    for y in range(top - 1, top + 16):
        half = 7.5 + max(0.0, (y - top) / 15.0) * 6.0
        robe |= {(x, y) for x in range(int(round(cx - half)), int(round(cx + half)) + 1)}
    shoulders = ellipse(cx, top + 5, 10.5, 6.5)
    robe = {p for p in robe if p[1] >= top + 4 or p in shoulders}
    solid(cv, robe, "L", "q")
    body = inner(robe)
    for dx in (-8, -3, 3, 8):  # lipatan kain
        cv.fill({(cx + dx, y) for y in range(top + 8, top + 15) if (cx + dx, y) in body}, "l")
    cv.fill(rect(cx - 2, top, 2, 4) | rect(cx + 1, top, 2, 4), "W")
    cv.fill({(cx - 2, top + 3), (cx + 2, top + 3)}, "G")
    for s in (-1, 1):
        solid(cv, ellipse(cx + s * 3.0, top + 15.6, 2.6, 1.4), "F", "f", shade_off=(1, 1))
    return robe


def judge_arm(cv, shoulder, hand, elbow):
    """Lengan jubah hitam yang lebar."""
    arm(cv, shoulder, hand, elbow=elbow, fur="L", r=2.2)


def gavel(cv, hx, hy, deg):
    """Palu hakim: gagang cokelat dari tangan, kepala kayu tegak lurus gagang."""
    a = math.radians(deg)
    ex, ey = hx + 7 * math.cos(a), hy - 7 * math.sin(a)
    cv.fill(capsule((hx, hy), (ex, ey), 0.7), "N")
    px, py = math.sin(a), math.cos(a)
    solid(cv, capsule((ex - px * 3, ey - py * 3), (ex + px * 3, ey + py * 3), 1.9), "X", "x", shade_off=(1, 1))


def sound_block(cv, x, y):
    """Landasan palu dari kayu."""
    solid(cv, rect(x, y, 7, 3), "N", None)
    cv.fill(rect(x + 1, y, 5, 1), "X")


def score_paddle(cv, x, y):
    """Papan skor kecil bertangkai dengan tanda seru merah."""
    cv.fill(capsule((x + 4, y + 8), (x + 4, y + 12), 0.6), "N")
    solid(cv, rect(x, y, 9, 8), "W", "G", shade_off=(1, 1))
    mini_text(cv, "!", x + 2, y + 2, "R")


JX_BLOCK = CX + 13  # landasan di lantai kanan depan


def judge_base(cv, t, eyes, brows, mouth, bob=0):
    tail(cv, (CX - 9, TOP + 14), phase=t * 0.45, flip=-1, length=7)
    judge_robe(cv, CX, TOP)
    head(cv, CX, CY + bob, eyes=eyes, brows=brows, mouth=mouth)
    sound_block(cv, JX_BLOCK, TOP + 12)


def judge_idle_frame(i):
    """Palu diam di tangan kanan, tangan kiri di pangkuan, sesekali melirik kiri-kanan."""
    cv = Canvas()
    t = i % 16
    eyes = ("look", "look", "look", "left", "left", "look", "look", "blink",
            "look", "look", "side", "side", "look", "look", "look", "look")[t]
    judge_base(cv, t, eyes, "flat", "flat", bob=(1 if t in (13, 14) else 0))
    judge_arm(cv, (CX - 7, TOP + 3), (CX - 6, TOP + 10), (CX - 11, TOP + 7))
    gavel(cv, CX + 11, TOP + 10, 45)  # palu siap di atas landasan, di luar siluet jubah
    judge_arm(cv, (CX + 7, TOP + 3), (CX + 11, TOP + 10), (CX + 11, TOP + 6))
    return cv


def judge_thinking_frame(i):
    """Tangan di dagu, palu diturunkan ke landasan, lalu gelembung ... dan ?."""
    cv = Canvas()
    t = i % 16
    eyes = "blink" if t == 4 else "side"
    judge_base(cv, t, eyes, "worried", "frown" if t >= 8 else "flat")
    gavel(cv, CX + 9, TOP + 11, -8)
    judge_arm(cv, (CX + 7, TOP + 3), (CX + 9, TOP + 11), (CX + 11, TOP + 7))
    judge_arm(cv, (CX - 7, TOP + 3), (CX - 2, CY + 9 + (t % 2 if t >= 5 else 0)), (CX - 11, TOP + 7))
    if 5 <= t <= 13:
        dots_or_mark(cv, CX + 9, 1, 5, t, "?")
    return cv


# (posisi tangan palu, sudut palu, percikan) per frame
JUDGING = [("up", 0), ("down", 1), ("up", 0), ("down", 1), ("up", 0), ("down", 1), ("down", 0), ("down", 0),
           ("down", 0), ("down", 0), ("down", 0), ("down", 0), ("down", 0), ("down", 0), ("mid", 0), ("mid", 0),
           ("up", 0), ("up", 0)]


def judge_judging_frame(i):
    """Mengangkat palu, mengetuk landasan tiga kali dengan percikan kecil, lalu mengangkat papan skor '!'."""
    cv = Canvas()
    t = i % 18
    pose, spark = JUDGING[t]
    verdict = 8 <= t <= 14
    judge_base(cv, t, "look" if not verdict else "wide", "up" if verdict else "flat", "o" if verdict and t < 11 else "flat")
    if pose == "up":  # palu terangkat di kanan telinga, tidak menumpuk di kepala
        gavel(cv, CX + 15, TOP - 3, 80)
        judge_arm(cv, (CX + 7, TOP + 3), (CX + 15, TOP - 3), (CX + 14, TOP + 3))
    elif pose == "mid":
        gavel(cv, CX + 12, TOP + 3, 60)
        judge_arm(cv, (CX + 7, TOP + 3), (CX + 12, TOP + 3), (CX + 12, TOP + 6))
    else:
        gavel(cv, CX + 10, TOP + 9, -15)
        judge_arm(cv, (CX + 7, TOP + 3), (CX + 10, TOP + 9), (CX + 12, TOP + 6))
    if spark:
        cv.fill({(JX_BLOCK - 1, TOP + 10), (JX_BLOCK + 7, TOP + 10), (JX_BLOCK - 2, TOP + 12), (JX_BLOCK + 8, TOP + 12)}, "O")
        cv.fill({(JX_BLOCK + 3, TOP + 7), (JX_BLOCK - 2, TOP + 9), (JX_BLOCK + 8, TOP + 9)}, "W")
    if verdict:  # papan skor diangkat tangan kiri
        up = 0 if t >= 9 else 3
        score_paddle(cv, CX - 20, TOP - 16 + up)
        judge_arm(cv, (CX - 7, TOP + 3), (CX - 16, TOP - 4 + up), (CX - 13, TOP + 3))
    else:
        judge_arm(cv, (CX - 7, TOP + 3), (CX - 6, TOP + 10), (CX - 11, TOP + 7))
    return cv


# ================================================================== Gerbang B: Skeptic
def skeptic_sweater(cv, cx, top):
    """Sweter hijau berkerah V (bulu terlihat di leher), celana cokelat."""
    torso = dressed_body(cv, cx, top, "v", "k", pants="e", pants_shade="x")
    cv.fill({(cx - 2, top), (cx - 1, top + 1), (cx, top + 1), (cx + 1, top), (cx - 1, top), (cx, top)}, "B")
    return torso


def monocle(cv, cx, cy, glint=False, big=False):
    """Monokel emas di mata kanan dengan rantai menjuntai ke dada; big = mata membesar di balik lensa."""
    x0, ey = cx + 4, cy + 0.4
    if big:  # referensi beat kaget detektif-bug: mata membesar di balik lensa
        cv.fill(ellipse(x0, ey, 2.7, 2.5), "W")
        cv.fill(rect(int(x0) - 1, int(ey) - 1, 3, 3), "P")
        cv.put(int(x0), int(ey) - 1, "W")
    cv.fill(edge(ellipse(x0, ey, 3.5, 3.5)), "O")
    cv.fill(chain([(x0 + 3, ey + 2), (x0 + 5, ey + 6), (x0 + 3, TOP + 2)], 0.4), "O")
    if glint:
        cv.fill({(int(x0) - 2, int(ey) - 2), (int(x0) - 1, int(ey) - 3)}, "W")


def crossed_arms(cv, cx, top):
    arm(cv, (cx + 7, top + 3), (cx - 5, top + 7), elbow=(cx + 10, top + 8), fur="v")
    arm(cv, (cx - 7, top + 3), (cx + 5, top + 6), elbow=(cx - 10, top + 8), fur="v")


def stamp(cv, x, y):
    """Stempel karet: kenop cokelat, leher, bantalan merah. (x, y) = pojok kiri atas bantalan 7x4."""
    solid(cv, ellipse(x + 3.5, y - 3.5, 2.2, 1.8), "N", None)
    cv.fill(rect(x + 3, y - 2, 1, 2), "N")
    solid(cv, rect(x, y, 7, 4), "R", "u", shade_off=(1, 1))


def paper(cv, x, y, mark=False):
    """Kertas argumen di lantai; mark = cap tanda tanya merah."""
    solid(cv, rect(x, y, 10, 7), "W", "G", shade_off=(1, 1))
    if mark:
        mini_text(cv, "?", x + 2, y + 1, "R")


def skeptic_base(cv, t, eyes, brows, mouth, bob=0, tilt=0, lean=0):
    tail(cv, (CX - 7, TOP + 14), phase=t * 0.45, flip=-1, length=8)
    skeptic_sweater(cv, CX, TOP)
    head(cv, CX + lean, CY + bob, eyes=eyes, brows=brows, mouth=mouth, tilt=tilt)


def skeptic_idle_frame(i):
    """Bersedekap, satu alis naik, senyum miring; monokel sesekali berkilau, stempel berdiri di lantai."""
    cv = Canvas()
    t = i % 16
    bob = 1 if t in (12, 13) else 0
    skeptic_base(cv, t, "blink" if t == 9 else "look", "raised", "smirk", bob=bob, tilt=bob)
    monocle(cv, CX, CY + bob, glint=t in (4, 5))
    crossed_arms(cv, CX, TOP)
    stamp(cv, CX + 12, TOP + 11)
    return cv


# (condong ke depan dalam px, kilau, mata membesar)
SUSPICIOUS = [(1, 0, 0), (2, 0, 0), (2, 0, 0), (3, 0, 0), (3, 1, 0), (3, 0, 1), (3, 0, 1), (3, 0, 1),
              (3, 0, 1), (3, 0, 1), (3, 1, 0), (3, 0, 0), (2, 0, 0), (2, 0, 0), (1, 0, 0), (1, 0, 0)]


def skeptic_suspicious_frame(i):
    """Condong ke depan, mata menyipit; monokel berkilau lalu mata membesar di baliknya, ditahan sejenak."""
    cv = Canvas()
    t = i % 16
    lean, glint, big = SUSPICIOUS[t]
    skeptic_base(cv, t, "relief", "raised", "flat" if not big else "o", bob=lean, lean=lean // 2)
    monocle(cv, CX + lean // 2, CY + lean, glint=bool(glint), big=bool(big))
    crossed_arms(cv, CX, TOP)
    stamp(cv, CX + 12, TOP + 11)
    return cv


# (posisi stempel, cap terlihat, benturan)
ATTACK = [("up", 0, 0), ("high", 0, 0), ("high", 0, 0), ("down", 0, 1), ("down", 0, 1), ("down", 0, 0),
          ("down", 0, 0), ("lift", 1, 0), ("lift", 1, 0), ("up", 1, 0), ("up", 1, 0), ("up", 1, 0),
          ("up", 1, 0), ("up", 0, 0), ("up", 0, 0), ("up", 0, 0)]


def skeptic_attack_frame(i):
    """Metafora intelektual: menghentak stempel '?' ke kertas argumen, lalu memperlihatkan capnya."""
    cv = Canvas()
    t = i % 16
    where, mark, hit = ATTACK[t]
    face = ("look", "raised", "smirk") if where in ("up", "high") else ("look", "up", "o")
    if mark and where == "up":
        face = ("happy", "raised", "smirk")
    skeptic_base(cv, t, *face)
    monocle(cv, CX, CY, glint=hit == 1)
    paper(cv, CX + 9, TOP + 9, mark=bool(mark))
    arm(cv, (CX - 7, TOP + 3), (CX - 7, TOP + 9), elbow=(CX - 12, TOP + 6), fur="v")  # tangan kiri di pinggang
    hand = {"up": (CX + 13, TOP - 3), "high": (CX + 14, TOP - 6), "down": (CX + 14, TOP + 5), "lift": (CX + 14, TOP + 1)}[where]
    stamp(cv, hand[0] - 3, hand[1] + 3)
    arm(cv, (CX + 7, TOP + 3), hand, elbow=(CX + 11, TOP + 1 if where != "down" else TOP + 5), fur="v")
    if hit:
        for (x, y) in ((CX + 7, TOP + 13), (CX + 21, TOP + 13), (CX + 8, TOP + 9), (CX + 20, TOP + 9)):
            cv.put(x, y, "K")
        cv.fill({(CX + 6, TOP + 11), (CX + 22, TOP + 11)}, "O")
    return cv


# ================================================================== Gerbang B: Champion
def champion_body(cv, cx, top):
    """Badan berbulu Gobyet (seperti Normal) dengan selempang merah menyilang."""
    sitting_body(cv, cx, top)
    torso = ellipse(cx, top + 6.5, 8.2, 7.2)
    body = inner(torso)
    band = {(x, y) for (x, y) in body if abs((x - cx) + (y - top) - 4) <= 1 and y < top + 11}
    cv.fill(band, "R")
    cv.fill({(x, y) for (x, y) in band if (x - 1, y - 1) not in band}, "r")


def gold_laurel(cv, cx, cy):
    """Mahkota laurel EMAS (laurel hijau milik filsuf-yunani asli; emas membedakan Champion)."""
    for k in range(15):
        a = math.pi + k / 14 * math.pi
        x, y = cx + 9.8 * math.cos(a), cy - 0.5 + 8.4 * math.sin(a)
        cv.put(x, y, "O")
        cv.put(x + (1 if k < 7 else -1), y - 1, "y" if k % 2 else "O")
        cv.put(x, y - 1, "O")


def trophy(cv, x, y, sparkle=None):
    """Piala emas: mangkuk, dua pegangan, tangkai, alas cokelat. (x, y) = pojok kiri atas mangkuk (lebar 9)."""
    cup = rect(x, y, 9, 5) | rect(x + 1, y + 5, 7, 1) | rect(x + 2, y + 6, 5, 1)
    for hx in (x - 2, x + 9):  # pegangan
        cv.fill({(hx, y + 1), (hx, y + 2), (hx + (1 if hx < x else 0), y + 3), (hx + (1 if hx < x else 0), y)}, "O")
    solid(cv, cup, "O", "y", shade_off=(1, 1))
    solid(cv, rect(x + 3, y + 7, 3, 2), "y", None)
    solid(cv, rect(x + 1, y + 9, 7, 2), "N", None)
    cv.fill({(x + 2, y + 1), (x + 2, y + 2)}, "W")
    if sparkle:
        sx, sy = sparkle
        cv.fill({(sx, sy), (sx - 1, sy), (sx + 1, sy), (sx, sy - 1), (sx, sy + 1)}, "W")


def champion_base(cv, t, eyes, mouth, bob=0):
    tail(cv, (CX - 6, TOP + 14), phase=t * 0.5, flip=-1, length=8)
    champion_body(cv, CX, TOP)
    head(cv, CX, CY + bob, eyes=eyes, brows="flat", mouth=mouth)
    gold_laurel(cv, CX, CY + bob)


TX, TY = CX + 10, TOP - 4  # piala dipamerkan setinggi bahu kanan (siluet beda dari kostum lain)
SPARKLES = [None, None, (TX + 3, TY + 1), None, None, (TX + 6, TY + 3), None, None,
            None, (TX + 4, TY + 2), None, None, None, (TX + 2, TY + 4), None, None]


def hold_trophy_at_shoulder(cv, sparkle=None):
    trophy(cv, TX, TY, sparkle=sparkle)
    arm(cv, (CX + 7, TOP + 3), (CX + 14, TOP + 7), elbow=(CX + 12, TOP + 10))
    arm(cv, (CX - 7, TOP + 3), (CX - 7, TOP + 9), elbow=(CX - 12, TOP + 6))  # tangan kiri di pinggang


def champion_idle_frame(i):
    """Memamerkan piala setinggi bahu dengan bangga, tangan lain di pinggang, kilau berpindah di piala."""
    cv = Canvas()
    t = i % 16
    bob = 1 if t in (6, 7) else 0
    champion_base(cv, t, "blink" if t == 11 else ("happy" if t in (6, 7) else "look"), "smile", bob=bob)
    hold_trophy_at_shoulder(cv, SPARKLES[t])
    return cv


# (fase piala, lompat)
VICTORY = [("shoulder", 0), ("mid", 0), ("up", 1), ("up", 0), ("up", 1), ("up", 0), ("up", 1), ("up", 0),
           ("up", 1), ("up", 0), ("up", 1), ("up", 0), ("mid", 0), ("mid", 0), ("shoulder", 0), ("shoulder", 0)]


def champion_victory_frame(i):
    """Piala diangkat tinggi ke samping kepala, tangan lain mengepal ke atas, konfeti piksel."""
    cv = Canvas()
    t = i % 16
    phase, hop = VICTORY[t]
    up = phase == "up"
    champion_base(cv, t, "happy" if up else "look", ("o" if t % 2 else "smile") if up else "smile", bob=-hop)
    if phase == "shoulder":
        hold_trophy_at_shoulder(cv)
    elif phase == "mid":
        trophy(cv, CX + 9, TOP - 5)
        arm(cv, (CX + 7, TOP + 3), (CX + 13, TOP + 6), elbow=(CX + 12, TOP + 8))
        arm(cv, (CX - 7, TOP + 3), (CX - 7, TOP + 9), elbow=(CX - 11, TOP + 7))
    else:
        trophy(cv, CX + 14, 2 - hop, sparkle=(CX + 17, 3 - hop) if t % 4 == 2 else None)
        arm(cv, (CX + 7, TOP + 3), (CX + 18, 13 - hop), elbow=(CX + 14, TOP + 1))
        arm(cv, (CX - 7, TOP + 3), (CX - 14, TOP - 8 - hop), elbow=(CX - 13, TOP))
        confetti(cv, t)
    return cv


SCENES = {
    "referee-idle": (referee_idle_frame, 16, lambda i: 170 if i % 16 not in (6, 14) else 120),
    "referee-thinking": (referee_thinking_frame, 18, lambda i: 150 if i % 18 < 10 else 190),
    "judge-idle": (judge_idle_frame, 16, lambda i: 170 if i % 16 != 7 else 120),
    "judge-thinking": (judge_thinking_frame, 16, lambda i: 170),
    "judge-judging": (judge_judging_frame, 18, lambda i: 110 if i % 18 < 8 else (260 if i % 18 == 9 else 160)),
    "skeptic-idle": (skeptic_idle_frame, 16, lambda i: 170 if i % 16 != 9 else 120),
    "skeptic-suspicious": (skeptic_suspicious_frame, 16, lambda i: 300 if i % 16 == 5 else 150),
    "skeptic-attack": (skeptic_attack_frame, 16, lambda i: 90 if i % 16 in (3, 4) else (260 if i % 16 == 7 else 140)),
    "champion-idle": (champion_idle_frame, 16, lambda i: 170),
    "champion-victory": (champion_victory_frame, 16, lambda i: 110 if 2 <= i % 16 <= 11 else 150),
}
