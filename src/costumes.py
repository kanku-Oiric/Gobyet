"""Kostum Gobyet: wisuda, filsuf Yunani, rambut Einstein, hacker, detektif bug, kondangan.

Setiap kostum memakai rig yang sama (monkey.py): badan duduk berbaju, lengan berlengan
baju, aksesori kepala digambar sesudah kepala, properti di sekitarnya.
"""
import math

from monkey import (Canvas, head, arm, tail, laptop, mini_text, bubble, ellipse, capsule, chain, rect,
                    edge, solid)

CX, CY, TOP = 32, 14, 23  # posisi baku: pusat kepala dan puncak badan


# ------------------------------------------------------------------ badan berbaju
def dressed_body(cv, cx, top, cloth, cloth_shade, pants="L", pants_shade="q", leg_twitch=0, sway=0):
    torso = ellipse(cx + sway, top + 6.5, 8.2, 7.2)
    solid(cv, torso, cloth, cloth_shade)
    for s in (-1, 1):
        lift = leg_twitch if s == 1 else 0
        solid(cv, ellipse(cx + s * 5.2, top + 12.2 - lift, 4.2, 2.8), pants, pants_shade)
        solid(cv, ellipse(cx + s * 3.0, top + 14.2 - lift, 2.6, 1.5), "F", "f", shade_off=(1, 1))
    return torso


def inner(mask):
    return {p for p in mask if p not in edge(mask)}


# ------------------------------------------------------------------ aksesori kepala
def mortarboard(cv, cx, cy, tassel=0, lift=0, spin=0):
    """Topi toga: papan persegi (tampak belah ketupat), topi dasar, rumbai emas."""
    y = int(cy - 10 - lift)
    solid(cv, rect(cx - 6, y + 1, 12, 3), "L", None)
    board = set()
    for dy, half in ((-2, 3 + spin), (-1, 7), (0, 10), (1, 7), (2, 3 - spin)):
        board |= {(x, y + dy - 1) for x in range(cx - half, cx + half + 1)}
    solid(cv, board, "L", None)
    cv.fill({(x, y - 3) for x in range(cx - 2, cx + 3)}, "l")
    cv.put(cx, y - 1, "O")
    end = (cx + 9 + tassel, y + 4)
    cv.fill(chain([(cx + 0.5, y - 0.5), (cx + 8.5, y - 0.5), end], 0.5), "O")
    cv.fill(rect(int(end[0]) - 1, int(end[1]), 2, 3), "O")


def laurel(cv, cx, cy):
    """Mahkota daun zaitun melingkar di atas kepala."""
    for k in range(13):
        a = math.pi + k / 12 * math.pi
        x, y = cx + 9.6 * math.cos(a), cy - 0.5 + 8.2 * math.sin(a)
        cv.put(x, y, "V")
        cv.put(x + (1 if k < 6 else -1), y - 1, "v" if k % 2 else "V")


def beard(cv, cx, cy, wag=0):
    b = ellipse(cx, cy + 9.4 + wag * 0.3, 5.6, 4.6)
    solid(cv, b, "H", "h", outline="h", shade_off=(1, 1))
    cv.fill(rect(cx - 4, int(cy + 5), 8, 1), "H")  # kumis
    cv.fill({(cx - 1, int(cy + 7)), (cx, int(cy + 7))}, "h")


def wild_hair(cv, cx, cy, bounce=0, back=True):
    """Rambut putih awut-awutan: helai runcing mencuat ke samping dan atas."""
    if back:
        m = set()
        for k in range(15):
            a = math.pi * 0.8 + k / 14 * math.pi * 1.4
            reach = 12.5 + (2.2 if k % 2 else 0) + (1.4 if k % 3 == 0 else 0) + (bounce if k % 2 else 0)
            x0, y0 = cx + 7.5 * math.cos(a), cy - 1 + 6.5 * math.sin(a)
            x1, y1 = cx + reach * math.cos(a), cy - 1 + reach * 0.78 * math.sin(a)
            m |= capsule((x0, y0), (x1, y1), 1.25)
        for s in (-1, 1):  # gumpalan besar di atas telinga
            m |= ellipse(cx + s * 11.5, cy - 4.5, 3.4, 2.8)
        solid(cv, m, "H", "h", outline="g", shade_off=(1, 1))
    else:  # beberapa helai di atas dahi
        for dx, dy in ((-5, -7), (-2, -8), (1, -8), (4, -7)):
            cv.fill(capsule((cx + dx, cy + dy), (cx + dx + (1 if dx > 0 else -1), cy + dy - 2), 0.8), "H")
            cv.put(cx + dx, cy + dy + 1, "h")


def einstein_moustache(cv, cx, cy):
    """Kumis tebal yang menutupi bibir atas."""
    m = rect(cx - 5, int(cy + 5), 10, 3) - {(cx - 5, int(cy + 7)), (cx + 4, int(cy + 7)), (cx - 5, int(cy + 5)), (cx + 4, int(cy + 5))}
    solid(cv, m, "H", "h", outline="g", shade_off=(1, 1))


def hood(cv, cx, cy):
    ring = ellipse(cx, cy - 0.3, 12.2, 10.6) - ellipse(cx, cy + 1.6, 8.6, 8.2)
    ring = {p for p in ring if p[1] < cy + 9}
    solid(cv, ring, "Q", "q")


def sunglasses(cv, cx, cy, glint=0):
    ey = int(cy + 0.4)
    for x0 in (cx - 7, cx + 1):
        cv.fill(rect(x0, ey - 2, 6, 3), "P")
        cv.put(x0 + 1 + glint, ey - 2, "Z")
    cv.fill(rect(cx - 1, ey - 2, 2, 1), "P")


def deerstalker(cv, cx, cy):
    cap = {p for p in ellipse(cx, cy - 5.2, 10.2, 5.0) if p[1] <= cy - 3}
    solid(cv, cap, "X", None)
    cv.fill({(x, y) for (x, y) in inner(cap) if (x // 2 + y // 2) % 2 == 0}, "x")
    cv.fill({(x, int(cy - 3)) for x in range(cx - 9, cx + 10)}, "x")
    cv.fill({(cx - 1, int(cy - 11)), (cx, int(cy - 11)), (cx - 2, int(cy - 12)), (cx + 1, int(cy - 12))}, "x")


def peci(cv, cx, cy):
    cap = rect(cx - 6, int(cy - 11), 12, 5) - {(cx - 6, int(cy - 11)), (cx + 5, int(cy - 11))}
    solid(cv, cap, "L", None)
    cv.fill(rect(cx - 5, int(cy - 10), 10, 1), "l")


# ------------------------------------------------------------------ properti
def scroll(cv, x, y, vertical=False):
    m = capsule((x, y), (x, y + 6) if vertical else (x + 7, y), 1.6)
    solid(cv, m, "C", "c", shade_off=(1, 1))
    cv.fill(rect(int(x) + (0 if vertical else 3), int(y) + (3 if vertical else -1), 1 if not vertical else 2, 2 if not vertical else 1), "R")


def column(cv, x, top, bottom):
    solid(cv, rect(x - 1, top, 11, 3), "m", "c", shade_off=(1, 1))
    shaft = rect(x + 1, top + 3, 7, bottom - top - 6)
    solid(cv, shaft, "m", None)
    for k in (2, 4, 6):
        cv.fill({(x + 1 + k, y) for y in range(top + 4, bottom - 3)}, "c")
    solid(cv, rect(x - 1, bottom - 3, 11, 3), "m", "c", shade_off=(1, 1))


def chalkboard(cv, x, y, w, h, text, shown):
    solid(cv, rect(x, y, w, h), "N", None)
    cv.fill(rect(x + 1, y + 1, w - 2, h - 2), "k")
    mini_text(cv, text[:shown], x + 2, y + 6, "W")
    if shown >= len(text):  # pangkat 2 kecil
        sx = x + 2 + len(text) * 6
        cv.fill({(sx, y + 3), (sx + 1, y + 3), (sx + 1, y + 4), (sx, y + 5), (sx, y + 6), (sx + 1, y + 6)}, "W")
    cv.fill(rect(x + 2, y + h - 3, 4, 1), "W")  # kapur di tatakan


def magnifier(cv, x, y, big_eye=False, look=(0, 0)):
    lens = ellipse(x, y, 4.2, 4.2)
    cv.fill(capsule((x + 3, y + 3), (x + 7, y + 8), 1.1), "N")
    solid(cv, lens, "I", None, outline="g")
    if big_eye:
        cv.fill(ellipse(x, y, 3.0, 2.7), "W")
        cv.fill(rect(int(x) - 1 + look[0], int(y) - 1 + look[1], 3, 3), "P")
        cv.put(int(x) + look[0], int(y) - 1 + look[1], "W")
    else:
        cv.put(int(x) - 2, int(y) - 2, "W")


def bug(cv, x, y, step=0):
    body = ellipse(x, y, 2.2, 1.5)
    solid(cv, body, "R", None)
    cv.fill({(int(x) - 1, int(y) - 1), (int(x) + 1, int(y))}, "P")
    for k, dx in enumerate((-1, 0, 1)):
        cv.put(int(x) + dx, int(y) + 2 - ((k + step) % 2), "K")
    cv.fill({(int(x) - 3, int(y) - 2), (int(x) - 4, int(y) - 3)}, "K")


def confetti(cv, t, n=10):
    colors = "ORVZIr"
    for k in range(n):
        x = (k * 17 + t * 3) % 60 + 2
        y = (k * 11 + t * 4) % 30 + 1
        cv.put(x, y, colors[k % len(colors)])


# ------------------------------------------------------------------ 1. wisuda
def wisuda_frame(i):
    cv = Canvas()
    t = i % 18
    toss = t in (10, 11, 12, 13)
    lift = {10: 2, 11: 4, 12: 4, 13: 1}.get(t, 0)
    CY, TOP = globals()["CY"] + 3, globals()["TOP"] + 3
    eyes = "blink" if t == 4 else ("happy" if toss or t == 14 else "look")
    tail(cv, (26, TOP + 14), phase=t * 0.5, flip=-1, length=8)
    dressed_body(cv, CX, TOP, "W", "G")
    # dasi merah dan kerah
    cv.fill(capsule((CX, TOP + 2), (CX, TOP + 9), 0.8), "R")
    cv.fill({(CX - 1, TOP + 1), (CX, TOP + 1), (CX + 1, TOP + 1)}, "R")
    cv.fill({(CX - 3, TOP), (CX - 2, TOP + 1), (CX + 3, TOP), (CX + 2, TOP + 1)}, "G")
    head(cv, CX, CY, eyes=eyes, brows=("up" if toss else "flat"), mouth=("smile" if not toss else "o"))
    mortarboard(cv, CX, CY, tassel=(t // 2) % 2, lift=lift, spin=(1 if toss and t % 2 else 0))
    # tangan kanan memegang ijazah, tangan kiri melempar/menangkap topi
    arm(cv, (CX - 7, TOP + 3), (CX - 9, TOP + 8), elbow=(CX - 11, TOP + 5), fur="W")
    scroll(cv, CX - 13, TOP + 8)
    if toss:
        arm(cv, (CX + 7, TOP + 3), (CX + 9, TOP - 6), elbow=(CX + 11, TOP - 1), fur="W")
        confetti(cv, t)
    else:
        arm(cv, (CX + 7, TOP + 3), (CX + 9, TOP + 10), elbow=(CX + 10, TOP + 6), fur="W")
    return cv


# ------------------------------------------------------------------ 2. filsuf Yunani
def filsuf_frame(i):
    cv = Canvas()
    t = i % 20
    cx = 36
    column(cv, 3, 8, 45)
    tail(cv, (cx + 5, TOP + 14), phase=t * 0.4, flip=1, length=8)
    torso = dressed_body(cv, cx, TOP, "C", "c", pants="C", pants_shade="c")
    # kain toga menyilang dari bahu kiri ke pinggang kanan
    cv.fill({(x, y) for (x, y) in inner(torso) if abs((x - cx) - (y - TOP) + 5) <= 1}, "c")
    cv.fill({(x, y) for (x, y) in inner(torso) if abs((x - cx) - (y - TOP) + 5) == 2 and y % 2 == 0}, "m")
    eureka = t >= 14
    head(cv, cx, CY, eyes=("look" if eureka else ("blink" if t == 3 else "side")),
         brows=("up" if eureka else "worried"), mouth="flat")
    beard(cv, cx, CY, wag=(t % 2 if not eureka else 0))
    laurel(cv, cx, CY)
    # tangan mengelus janggut, tangan lain memegang gulungan
    stroke = (t % 4) // 2
    if eureka:
        arm(cv, (cx + 7, TOP + 3), (cx + 11, TOP - 5), elbow=(cx + 12, TOP + 1))
        cv.fill(rect(cx + 11, TOP - 9, 1, 3), "K")  # telunjuk ke atas
    else:
        arm(cv, (cx + 7, TOP + 3), (cx + 2, CY + 10 + stroke), elbow=(cx + 10, TOP + 5))
    arm(cv, (cx - 7, TOP + 3), (cx - 9, TOP + 9), elbow=(cx - 11, TOP + 5))
    scroll(cv, cx - 10, TOP + 5, vertical=True)
    # gelembung pikiran: ... lalu ? lalu !
    bx, by = cx + 10, 1
    if t >= 4:
        for k, (dx, dy) in enumerate(((-4, 11), (-2, 9))):
            cv.fill(rect(bx + dx, by + dy, 1 + k, 1 + k), "W")
        bubble(cv, bx, by, 13, 9, fill=("O" if eureka else "W"), tail_dir=-1)
        text = "!" if eureka else ("?" if t >= 9 else "." * min(3, (t - 3) // 2 + 1))
        if text.startswith("."):
            for k in range(len(text)):
                cv.put(bx + 3 + k * 3, by + 6, "K")
        else:
            mini_text(cv, text, bx + 4, by + 2, "K")
    return cv


# ------------------------------------------------------------------ 3. rambut Einstein
def einstein_frame(i):
    cv = Canvas()
    t = i % 22
    cx = 21
    text = "E=mc"
    shown = min(len(text), max(0, (t - 2) // 2))
    tongue = t >= 14
    chalkboard(cv, 34, 6, 29, 16, text, shown)
    tail(cv, (cx - 5, TOP + 14), phase=t * 0.5, flip=-1, length=7)
    wild_hair(cv, cx, CY, bounce=(1 if tongue and t % 2 else 0))
    dressed_body(cv, cx, TOP, "h", "g", pants="g", pants_shade="q")
    head(cv, cx, CY, eyes=("happy" if tongue else "side"), brows=("up" if tongue else "flat"), mouth="flat")
    wild_hair(cv, cx, CY, back=False)
    einstein_moustache(cv, cx, CY)
    if tongue:
        cv.fill(rect(cx - 1, int(CY + 8), 3, 3), "T")
        cv.fill({(cx - 1, int(CY + 10)), (cx + 1, int(CY + 10))}, "M")
    # tangan menulis dengan kapur
    writing = t < 12
    if writing:
        hx = min(37 + shown * 6, 55)
        arm(cv, (cx + 7, TOP + 3), (hx, 16 + (t % 2)), elbow=(cx + 15, TOP + 2), fur="h")
        cv.fill(rect(hx - 1, 14 + (t % 2), 2, 2), "W")
    else:
        arm(cv, (cx + 7, TOP + 3), (cx + 10, TOP + 9), elbow=(cx + 11, TOP + 5), fur="h")
    arm(cv, (cx - 7, TOP + 3), (cx - 9, TOP + 10), elbow=(cx - 10, TOP + 6), fur="h")
    return cv


# ------------------------------------------------------------------ 4. hacker
CODE = ["sudo rm -rf /bug", "git push --force", "while(1) ngopi()", "npm i pisang", "ssh gobyet@mars"]


def hacker_frame(i):
    cv = Canvas()
    t = i % 16
    cx, cy = 22, 16
    # jendela terminal di belakang: baris kode hijau bergulir
    solid(cv, rect(36, 2, 27, 26), "q", None)
    cv.fill(rect(37, 3, 25, 2), "Q")
    for k, c in enumerate("RYZ"):
        cv.put(38 + k * 2, 3, c)
    for row in range(6):
        line = CODE[(row + t // 2) % len(CODE)]
        w = (len(line) * 7) % 20 + 4
        cv.fill(rect(38, 7 + row * 3, min(w, 22), 1), "Z" if row % 2 == 0 else "V")
    done = t >= 12
    if done:
        bubble(cv, 41, 30, 22, 9, fill="Z", tail_dir=-1)
        mini_text(cv, "OK", 44, 32, "q")
        mini_text(cv, "v", 56, 32, "q")
    tail(cv, (cx - 7, 37), phase=t * 0.5, flip=-1, length=6)
    torso = ellipse(cx, 32, 9.5, 7.5)
    solid(cv, torso, "Q", "q")
    head(cv, cx, cy, eyes="down", brows="flat", mouth=("smile" if done else "flat"))
    hood(cv, cx, cy)
    sunglasses(cv, cx, cy, glint=t % 4)
    laptop(cv, cx - 10, 29, glow="Z")
    hand_y = (28 - (t % 2), 27 + (t % 2)) if not done else (28, 28)
    arm(cv, (cx - 7, 27), (cx - 5, hand_y[0]), elbow=(cx - 11, 31), fur="Q")
    arm(cv, (cx + 7, 27), (cx + 5, hand_y[1]), elbow=(cx + 11, 31), fur="Q")
    cv.fill({(cx - 1, 25), (cx - 1, 26), (cx + 1, 25), (cx + 1, 26)}, "W")  # tali hoodie
    return cv


# ------------------------------------------------------------------ 5. detektif bug
def detektif_frame(i):
    cv = Canvas()
    t = i % 20
    bug_x = 60 - t * 1.6
    found = t >= 12
    tail(cv, (26, TOP + 14), phase=t * 0.5, flip=-1, length=8)
    dressed_body(cv, CX, TOP, "d", "e", pants="e", pants_shade="x")
    for y in (TOP + 3, TOP + 6, TOP + 9):
        cv.put(CX, y, "K")
    cv.fill({(CX - 3, TOP), (CX - 2, TOP + 1), (CX - 1, TOP + 2), (CX + 3, TOP), (CX + 2, TOP + 1), (CX + 1, TOP + 2)}, "e")
    head(cv, CX, CY, eyes=("wide" if found else "look"), brows=("up" if found else "flat"), mouth=("o" if found else "flat"))
    deerstalker(cv, CX, CY)
    # kaca pembesar menyapu, lalu berhenti di depan mata saat bug ketemu
    if found:
        lx, ly = CX + 4, CY + 0.5
        magnifier(cv, lx, ly, big_eye=True, look=(1, 1))
        arm(cv, (CX + 7, TOP + 3), (lx + 5, ly + 7), elbow=(CX + 12, TOP + 4), fur="d")
        bubble(cv, 46, 12, 9, 9, fill="R", tail_dir=1)
        mini_text(cv, "!", 48, 14, "W")
    else:
        sweep = math.sin(t / 3.0) * 6
        lx, ly = CX + 13 + sweep, TOP + 14
        magnifier(cv, lx, ly)
        arm(cv, (CX + 7, TOP + 3), (lx - 3, ly - 3), elbow=(CX + 10, TOP + 8), fur="d")
    arm(cv, (CX - 7, TOP + 3), (CX - 9, TOP + 10), elbow=(CX - 10, TOP + 6), fur="d")
    bug(cv, max(bug_x, 44), 44, step=t)
    return cv


# ------------------------------------------------------------------ 6. kondangan (peci + batik, joget)
def kondangan_frame(i):
    cv = Canvas()
    t = i % 12
    sway = (-1, 0, 1, 0)[t % 4]
    cx = CX + sway
    tail(cv, (cx - 6, TOP + 14), phase=t * 0.8, flip=-1, length=8)
    torso = dressed_body(cv, cx, TOP, "U", "u", sway=0)
    # motif batik kawung sederhana
    body = {p for p in inner(torso) if p[1] < TOP + 10}
    for (x, y) in body:
        if (x - cx) % 4 == 0 and (y - TOP) % 4 == 1:
            cv.fill({(x, y), (x + 1, y + 1), (x - 1, y + 1), (x, y + 2)} & body, "O")
    head(cv, cx, CY + (1 if t % 4 == 1 else 0), eyes="happy", brows="flat", mouth=("smile" if t % 2 else "o"))
    peci(cv, cx, CY + (1 if t % 4 == 1 else 0))
    up = (t // 2) % 2
    arm(cv, (cx - 7, TOP + 3), (cx - 15, TOP - 7) if up else (cx - 13, TOP + 4), elbow=(cx - 14, TOP), fur="U")
    arm(cv, (cx + 7, TOP + 3), (cx + 13, TOP + 4) if up else (cx + 15, TOP - 7), elbow=(cx + 14, TOP), fur="U")
    for k, x0 in enumerate((3, 52, 8, 56)):  # not musik melayang di kiri dan kanan
        mini_text(cv, "n", x0 + (t + k) % 3, 16 - ((t + k * 3) % 10) + (k // 2) * 14, "R")
    return cv


def ms(default):
    return lambda i: default


SCENES = {
    "wisuda": (wisuda_frame, 18, lambda i: 110 if i % 18 in (10, 11, 12, 13) else 160),
    "filsuf-yunani": (filsuf_frame, 20, lambda i: 320 if i % 20 == 14 else 170),
    "rambut-einstein": (einstein_frame, 22, lambda i: 200 if i % 22 < 12 else 150),
    "hacker": (hacker_frame, 16, ms(130)),
    "detektif-bug": (detektif_frame, 20, lambda i: 300 if i % 20 == 12 else 140),
    "kondangan": (kondangan_frame, 12, ms(140)),
}
