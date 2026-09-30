"""State tambahan untuk Normal dan kostum DOMAIN (Fase 2, bertahap per gerbang).

Gerbang C: Greek Philosopher (idle, victory, defeated), Academic (thinking, victory, defeated),
Normal (thinking, victory, defeated).
Gerbang D: Scientist (idle, shocked, victory) dengan tampilan rambut-einstein asli; Mathematician
(idle, thinking, victory), kostum baru: rompi ungu (PAL_EXT p/j), batu tulis genggam, jangka.

Tampilan kostum mengikuti aset asli yang terkunci, tanpa desain ulang: Greek Philosopher memakai
toga, janggut, laurel hijau, gulungan, dan tiang dari filsuf-yunani; Academic memakai kemeja putih,
dasi merah, topi toga, dan ijazah dari wisuda; Normal adalah Gobyet tanpa kostum dengan pisang dari
makan-pisang. Fungsi gambar kostum dipakai ulang dari src/costumes.py. Satu-satunya bentuk baru
adalah pose rebah (lying_body) untuk defeated.
"""
import math

from monkey import (Canvas, head, arm, tail, sitting_body, banana, puff, spark_lines, mini_text, bubble, ellipse,
                    capsule, rect, solid)
from costumes import (CX, CY, TOP, dressed_body, inner, confetti, mortarboard, laurel, beard, scroll, column,
                      chalkboard, wild_hair, einstein_moustache)
from roles import dots_or_mark


# ------------------------------------------------------------------ pose rebah (defeated)
def lying_body(cv, hx, hy, cloth="B", shade="b", pants=None, pants_shade=None, breathe=0, belly=True, folds=False):
    """Badan rebah menyamping ke kanan dari kepala di (hx, hy): kepala tetap menghadap kamera.
    breathe 0/1 = perut sedikit mengembang. folds = lipatan kain toga. Digambar sebelum kepala."""
    body = ellipse(hx + 14, hy + 3.5 - breathe * 0.5, 10.5, 5.2 + breathe * 0.5)
    solid(cv, body, cloth, shade)
    if folds:  # lipatan menyilang seperti toga filsuf-yunani yang duduk
        cv.fill({(x, y) for (x, y) in inner(body) if abs((x - hx - 12) - (y - hy)) <= 1}, "c")
        cv.fill({(x, y) for (x, y) in inner(body) if abs((x - hx - 12) - (y - hy)) == 2 and y % 2 == 0}, "m")
    if belly:
        b = {p for p in ellipse(hx + 14, hy + 5.4, 6.5, 2.4) if p in inner(body)}
        cv.fill(b, "F")
        cv.fill({(x, y) for (x, y) in b if (x, y + 1) not in b}, "f")
    thigh = ellipse(hx + 24, hy + 4.5, 3.8, 3.0)
    solid(cv, thigh, pants or cloth, pants_shade or shade)
    for dy in (0, 3):  # dua telapak kaki di ujung kanan
        solid(cv, ellipse(hx + 28.2, hy + 3.5 + dy, 1.6, 1.4), "F", "f", shade_off=(1, 1))
    return body


def sigh(cv, x, y, k):
    """Hembusan napas panjang: kepulan kecil yang naik dan membesar (k = 0..3)."""
    puff(cv, x + k, y - k, 1.2 + k * 0.35)


# ================================================================== Greek Philosopher
GX = 36  # sama dengan filsuf-yunani asli: tokoh digeser ke kanan, tiang di kiri


def greek_body(cv, t, bob=0):
    column(cv, 3, 8, 45)
    tail(cv, (GX + 5, TOP + 14), phase=t * 0.4, flip=1, length=8)
    torso = dressed_body(cv, GX, TOP + bob, "C", "c", pants="C", pants_shade="c")
    top = TOP + bob
    cv.fill({(x, y) for (x, y) in inner(torso) if abs((x - GX) - (y - top) + 5) <= 1}, "c")
    cv.fill({(x, y) for (x, y) in inner(torso) if abs((x - GX) - (y - top) + 5) == 2 and y % 2 == 0}, "m")


def greek_head(cv, cx, cy, eyes, brows, wag=0):
    head(cv, cx, cy, eyes=eyes, brows=brows, mouth="flat")
    beard(cv, cx, cy, wag=wag)
    laurel(cv, cx, cy)


def greek_idle_frame(i):
    """Mengelus janggut dengan tenang sambil membawa gulungan; sesekali melirik dan berkedip."""
    cv = Canvas()
    t = i % 16
    eyes = ("look", "look", "look", "look", "blink", "look", "look", "side",
            "side", "side", "look", "look", "relief", "relief", "look", "look")[t]
    stroke = (t // 2) % 2
    greek_body(cv, t)
    greek_head(cv, GX, CY, eyes, "flat", wag=stroke)
    arm(cv, (GX + 7, TOP + 3), (GX + 2, CY + 10 + stroke), elbow=(GX + 10, TOP + 5))
    arm(cv, (GX - 7, TOP + 3), (GX - 9, TOP + 9), elbow=(GX - 11, TOP + 5))
    scroll(cv, GX - 10, TOP + 5, vertical=True)
    return cv


def open_scroll(cv, x, y, length, w=7):
    """Gulungan terbuka: rol atas dari (x, y) ke kanan, kertas krem bergaris menjuntai, segel merah.
    Tangan memegang ujung kanan rol di (x + w + 2, y)."""
    if length > 0:
        solid(cv, rect(x + 1, y + 1, w, length), "C", "c", shade_off=(1, 1))
        for k in range(2, length - 1, 2):
            cv.fill(rect(x + 2, y + 1 + k, w - 2 - (k // 2) % 2 * 2, 1), "c")
        if length >= 6:
            cv.fill(rect(x + w // 2, y + length - 1, 2, 2), "R")
    solid(cv, capsule((x, y), (x + w + 1, y), 1.2), "c", None)


# (fase lengan, lompat, panjang gulungan terbuka)
GREEK_VICTORY = [("hold", 0, 0), ("mid", 0, 0), ("up", 1, 2), ("up", 0, 4), ("up", 1, 7), ("up", 0, 9),
                 ("up", 1, 9), ("up", 0, 9), ("up", 1, 9), ("up", 0, 9), ("up", 1, 7), ("up", 0, 4),
                 ("up", 0, 1), ("mid", 0, 0), ("hold", 0, 0), ("hold", 0, 0)]


def greek_victory_frame(i):
    """Gulungan diangkat tinggi lalu terbuka menjuntai, tangan lain mengepal ke atas, melompat kecil."""
    cv = Canvas()
    t = i % 16
    phase, hop, unroll = GREEK_VICTORY[t]
    up = phase == "up"
    greek_body(cv, t, bob=-hop)
    greek_head(cv, GX, CY - hop, "happy" if up else "look", "up" if up else "flat")
    if phase == "hold":
        arm(cv, (GX + 7, TOP + 3), (GX + 9, TOP + 9), elbow=(GX + 11, TOP + 5))
        arm(cv, (GX - 7, TOP + 3), (GX - 9, TOP + 9), elbow=(GX - 11, TOP + 5))
        scroll(cv, GX - 10, TOP + 5, vertical=True)
    elif phase == "mid":
        arm(cv, (GX + 7, TOP + 3), (GX + 11, TOP + 1), elbow=(GX + 12, TOP + 6))
        scroll(cv, GX - 14, TOP - 6, vertical=True)
        arm(cv, (GX - 7, TOP + 3), (GX - 13, TOP - 1), elbow=(GX - 12, TOP + 4))
    else:
        sx, sy = GX - 24, 4 - hop  # ujung kiri rol gulungan
        arm(cv, (GX - 7, TOP + 3 - hop), (sx + 10, sy + 1), elbow=(GX - 14, TOP - 1 - hop))
        open_scroll(cv, sx, sy, unroll)
        arm(cv, (GX + 7, TOP + 3 - hop), (GX + 13, TOP - 9 - hop), elbow=(GX + 13, TOP - 1 - hop))
        if t in (5, 7, 9):  # kilau kecil di atas rol
            kx, ky = sx + 4, sy - 3
            cv.fill({(kx, ky), (kx + 1, ky), (kx - 1, ky), (kx, ky - 1), (kx, ky + 1)}, "O")
    return cv


def rolling_scroll(cv, x, y, turn):
    """Gulungan tergeletak mendatar yang menggelinding: segel merah berpindah mengikuti putaran."""
    solid(cv, capsule((x, y), (x + 7, y), 1.6), "C", "c", shade_off=(1, 1))
    band = x + 1 + (turn % 3) * 2
    cv.fill(rect(int(band), int(y) - 1, 1, 2), "R")


# posisi gulungan (relatif terhadap tangan) per frame: menggelinding menjauh, lalu ditarik kembali dengan lemas
GREEK_SCROLL = [0, 2, 4, 6, 8, 10, 12, 13, 14, 14, 14, 14, 14, 10, 5, 1]


def greek_defeated_frame(i):
    """Rebah di dekat tiang; gulungan terlepas dan menggelinding, ditarik kembali dengan lemas, lalu lepas lagi."""
    cv = Canvas()
    t = i % 16
    hx, hy = 24, 35
    breathe = 1 if t in (9, 10, 11) else 0
    column(cv, 3, 8, 45)
    tail(cv, (hx + 22, hy - 1), phase=t * 0.2, flip=1, length=6, curl=2.2)
    lying_body(cv, hx, hy, "C", "c", breathe=breathe, belly=False, folds=True)
    eyes = "blink" if t == 12 else "relief"
    greek_head(cv, hx, hy, eyes, "worried")
    reach = 13 <= t <= 15 or t == 12
    sx = hx + 9 + GREEK_SCROLL[t]
    rolling_scroll(cv, sx, 45, t if t < 8 else 7)
    if reach:  # lengan terjulur di lantai meraih gulungan
        arm(cv, (hx + 9, hy + 5), (sx, 44), elbow=(hx + 11, hy + 8))
    else:
        arm(cv, (hx + 9, hy + 5), (hx + 8, 44), elbow=(hx + 12, hy + 8))
    if 8 <= t <= 11:
        sigh(cv, hx - 12, hy - 8, t - 8)
    return cv


# ================================================================== Academic
AY, AT = CY + 3, TOP + 3  # sama dengan wisuda asli: kepala dan badan 3 px lebih rendah


def academic_body(cv, t, bob=0):
    tail(cv, (26, AT + 14), phase=t * 0.5, flip=-1, length=8)
    top = AT + bob
    dressed_body(cv, CX, top, "W", "G")
    cv.fill(capsule((CX, top + 2), (CX, top + 9), 0.8), "R")
    cv.fill({(CX - 1, top + 1), (CX, top + 1), (CX + 1, top + 1)}, "R")
    cv.fill({(CX - 3, top), (CX - 2, top + 1), (CX + 3, top), (CX + 2, top + 1)}, "G")


def open_diploma(cv, x, y):
    """Ijazah terbuka di pangkuan: dua rol krem, kertas bergaris, pita merah. (x, y) = pojok kiri atas, 14x7."""
    solid(cv, rect(x + 1, y, 12, 7), "C", "c", shade_off=(1, 1))
    for k in range(3):
        cv.fill(rect(x + 3, y + 2 + k * 2 - 1, 8 - 2 * (k % 2), 1), "c")
    for rx in (x, x + 13):
        solid(cv, capsule((rx, y), (rx, y + 6), 1.0), "c", None)
    cv.fill(rect(x + 10, y + 4, 2, 2), "R")


def crumpled_diploma(cv, x, y):
    """Ijazah kusut: gumpalan kertas krem dengan lipatan, pita merah miring. (x, y) = pusat."""
    blob = ellipse(x, y, 3.6, 2.8) | ellipse(x + 1.5, y - 1.5, 2.2, 1.8)
    solid(cv, blob, "C", "c", shade_off=(1, 1))
    cv.fill({(int(x) - 1, int(y)), (int(x), int(y) - 1), (int(x) + 1, int(y) + 1), (int(x) + 2, int(y) - 1)}, "c")
    cv.fill({(int(x) - 2, int(y) + 1), (int(x) - 1, int(y) + 2)}, "R")


def academic_thinking_frame(i):
    """Membaca ijazah di pangkuan, lalu tangan ke dagu dan muncul gelembung ... dan ?."""
    cv = Canvas()
    t = i % 16
    ponder = 7 <= t <= 13
    eyes = "blink" if t == 6 else ("side" if ponder else "down")
    academic_body(cv, t)
    head(cv, CX, AY, eyes=eyes, brows=("worried" if ponder else "flat"), mouth=("frown" if ponder else "flat"))
    mortarboard(cv, CX, AY, tassel=(t // 2) % 2)
    open_diploma(cv, CX - 7, AT + 7)
    arm(cv, (CX - 7, AT + 3), (CX - 7, AT + 10), elbow=(CX - 11, AT + 6), fur="W")
    if ponder:
        arm(cv, (CX + 7, AT + 3), (CX + 3, AY + 9 + (t % 2)), elbow=(CX + 11, AT + 6), fur="W")
        dots_or_mark(cv, CX + 12, 0, 7, t, "?")
    elif t == 14:
        arm(cv, (CX + 7, AT + 3), (CX + 8, AT + 5), elbow=(CX + 11, AT + 6), fur="W")
    else:
        arm(cv, (CX + 7, AT + 3), (CX + 7, AT + 10), elbow=(CX + 11, AT + 6), fur="W")
    return cv


# (topi: on/fly, geser x, angkat, putar, lengan)
ACADEMIC_VICTORY = [("on", 0, 0, 0, "grip"), ("on", 0, 0, 0, "grip"), ("fly", 4, 3, 1, "throw"),
                    ("fly", 9, 5, 2, "up"), ("fly", 13, 5, 3, "up"), ("fly", 15, 5, 2, "up"),
                    ("fly", 15, 5, 0, "up"), ("fly", 13, 5, -2, "up"), ("fly", 9, 5, -3, "up"),
                    ("fly", 5, 3, -2, "up"), ("fly", 2, 1, -1, "catch"), ("on", 0, 0, 0, "catch"),
                    ("on", 0, 0, 0, "wave"), ("on", 0, 0, 0, "wave"), ("on", 0, 0, 0, "rest"), ("on", 0, 0, 0, "grip")]


def academic_victory_frame(i):
    """Lempar topi penuh: topi melambung tinggi ke kanan sambil berputar, konfeti, lalu kembali ke kepala."""
    cv = Canvas()
    t = i % 16
    cap, dx, lift, spin, pose = ACADEMIC_VICTORY[t]
    crouch = 1 if t == 1 else 0
    cheer = pose in ("throw", "up", "catch", "wave")
    academic_body(cv, t, bob=crouch)
    head(cv, CX, AY + crouch, eyes=("happy" if cheer else "look"), brows=("up" if pose == "up" else "flat"),
         mouth=("o" if pose in ("throw", "up") else "smile"))
    mortarboard(cv, CX + dx, AY + crouch, tassel=(t // 2) % 2, lift=lift, spin=spin)
    if pose == "grip":  # tangan kanan memegang tepi topi
        arm(cv, (CX + 7, AT + 3 + crouch), (CX + 10, AY - 6 + crouch), elbow=(CX + 13, AT - 1), fur="W")
    elif pose == "throw":
        arm(cv, (CX + 7, AT + 3), (CX + 12, AY - 8), elbow=(CX + 13, AT - 2), fur="W")
    elif pose == "up":  # telapak terbuka setelah melempar, di bawah lintasan topi
        arm(cv, (CX + 7, AT + 3), (CX + 11, AY - 6), elbow=(CX + 13, AT - 1), fur="W")
    elif pose == "catch":
        arm(cv, (CX + 7, AT + 3), (CX + 10, AY - 6), elbow=(CX + 13, AT - 1), fur="W")
    else:
        arm(cv, (CX + 7, AT + 3), (CX + 9, AT + 10), elbow=(CX + 10, AT + 6), fur="W")
    if pose in ("up", "catch", "wave"):  # ijazah ikut diangkat
        wy = AY - 6 + (t % 2 if pose == "wave" else 0)
        arm(cv, (CX - 7, AT + 3), (CX - 13, wy), elbow=(CX - 13, AT - 1), fur="W")
        scroll(cv, CX - 14, wy - 7, vertical=True)
    else:
        arm(cv, (CX - 7, AT + 3 + crouch), (CX - 9, AT + 8 + crouch), elbow=(CX - 11, AT + 5), fur="W")
        scroll(cv, CX - 13, AT + 8 + crouch)
    if cap == "fly":
        confetti(cv, t)
    return cv


def academic_defeated_frame(i):
    """Duduk lunglai: bahu turun, topi miring, ijazah kusut di pangkuan, menghela napas panjang."""
    cv = Canvas()
    t = i % 16
    sag = 1 + (1 if t in (7, 8, 9, 10) else 0)
    academic_body(cv, t, bob=1)
    eyes = "blink" if t == 13 else "relief"
    head(cv, CX, AY + sag + 1, eyes=eyes, brows="worried", mouth="frown")
    mortarboard(cv, CX - 2, AY + sag + 1, tassel=0, lift=-1, spin=-1)
    arm(cv, (CX - 7, AT + 4), (CX - 11, AT + 13), elbow=(CX - 11, AT + 8), fur="W")
    crumpled_diploma(cv, CX + 5, AT + 11)
    arm(cv, (CX + 7, AT + 4), (CX + 6, AT + 10), elbow=(CX + 11, AT + 8), fur="W")
    if 7 <= t <= 10:
        sigh(cv, CX + 4, AY + sag + 9, t - 7)
    return cv


# ================================================================== Normal
def normal_body(cv, t, bob=0):
    tail(cv, (CX - 6, TOP + 14), phase=t * 0.5, flip=-1, length=8)
    sitting_body(cv, CX, TOP + bob)


def normal_thinking_frame(i):
    """Menggaruk kepala dan memegang dagu, mata melirik; gelembung ... lalu ?."""
    cv = Canvas()
    t = i % 16
    eyes = ("side", "side", "side", "side", "blink", "side", "left", "left",
            "left", "side", "side", "side", "left", "left", "side", "side")[t]
    normal_body(cv, t)
    head(cv, CX, CY, eyes=eyes, brows="worried", mouth=("frown" if 6 <= t <= 13 else "flat"))
    arm(cv, (CX + 7, TOP + 3), (CX + 7, CY - 8 + (t % 2)), elbow=(CX + 14, CY + 2))
    arm(cv, (CX - 7, TOP + 3), (CX - 2, CY + 9), elbow=(CX - 11, TOP + 7))
    if 6 <= t <= 13:
        dots_or_mark(cv, CX + 15, 0, 6, t, "?")
    return cv


# (fase lengan, lompat)
NORMAL_VICTORY = [("hold", 0), ("mid", 0), ("up", 1), ("up", 0), ("up", 1), ("up", 0), ("up", 1), ("up", 0),
                  ("up", 1), ("up", 0), ("up", 1), ("up", 0), ("mid", 0), ("mid", 0), ("hold", 0), ("hold", 0)]


def normal_victory_frame(i):
    """Pisang diangkat tinggi seperti piala, tangan lain mengepal naik-turun, melompat kecil."""
    cv = Canvas()
    t = i % 16
    phase, hop = NORMAL_VICTORY[t]
    up = phase == "up"
    normal_body(cv, t, bob=-hop)
    head(cv, CX, CY - hop, eyes=("happy" if up else "look"), brows="flat",
         mouth=(("o" if t % 2 else "smile") if up else "smile"))
    if phase == "hold":
        banana(cv, CX + 11, TOP + 6)
        arm(cv, (CX + 7, TOP + 3), (CX + 11, TOP + 7), elbow=(CX + 12, TOP + 9))
        arm(cv, (CX - 7, TOP + 3), (CX - 8, TOP + 10), elbow=(CX - 11, TOP + 6))
    elif phase == "mid":
        banana(cv, CX + 13, TOP - 3)
        arm(cv, (CX + 7, TOP + 3), (CX + 13, TOP - 2), elbow=(CX + 13, TOP + 5))
        arm(cv, (CX - 7, TOP + 3), (CX - 11, TOP + 2), elbow=(CX - 12, TOP + 7))
    else:
        hx, hy = CX + 15, TOP - 9 - hop
        banana(cv, hx, hy)
        arm(cv, (CX + 7, TOP + 3 - hop), (hx, hy + 1), elbow=(CX + 14, TOP - 1 - hop))
        fist_up = t % 4 in (2, 3)
        arm(cv, (CX - 7, TOP + 3 - hop), (CX - 13, (TOP - 10 if fist_up else TOP - 5) - hop), elbow=(CX - 13, TOP - hop))
        if t % 4 == 2:
            sx, sy = hx + 5, hy - 10
            cv.fill({(sx, sy), (sx - 1, sy), (sx + 1, sy), (sx, sy - 1), (sx, sy + 1)}, "W")
    return cv


def normal_defeated_frame(i):
    """Rebah menyamping dengan lemas, ekor terkulai, menghela napas; mata setengah terbuka (bukan pingsan)."""
    cv = Canvas()
    t = i % 16
    hx, hy = 20, 35
    breathe = 1 if t in (6, 7, 8) else 0
    tail(cv, (hx + 22, hy - 1), phase=t * 0.2, flip=1, length=6, curl=2.2 + (0.4 if t in (12, 13) else 0))
    lying_body(cv, hx, hy, breathe=breathe)
    head(cv, hx, hy, eyes=("blink" if t == 11 else "relief"), brows="worried", mouth="frown")
    arm(cv, (hx + 9, hy + 5), (hx + 8, 44), elbow=(hx + 12, hy + 8))
    if 6 <= t <= 9:
        sigh(cv, hx - 12, hy - 8, t - 6)
    return cv


# ================================================================== Gerbang D: Scientist
SX = 21  # sama dengan rambut-einstein asli: tokoh di kiri, papan tulis di kanan


def scientist_base(cv, t, eyes, brows, dx=0, bob=0, bounce=0, tongue=False):
    """Papan tulis asli (E=mc, statis), rambut putih awut-awutan, sweter abu, kumis tebal."""
    chalkboard(cv, 34, 6, 29, 16, "E=mc", 4)
    x, top, cy = SX + dx, TOP + bob, CY + bob
    tail(cv, (x - 5, top + 14), phase=t * 0.5, flip=-1, length=7)
    wild_hair(cv, x, cy, bounce=bounce)
    dressed_body(cv, x, top, "h", "g", pants="g", pants_shade="q")
    head(cv, x, cy, eyes=eyes, brows=brows, mouth="flat")
    wild_hair(cv, x, cy, back=False)
    einstein_moustache(cv, x, cy)
    if tongue:  # lidah menjulur seperti akhir rambut-einstein asli
        cv.fill(rect(x - 1, int(cy + 8), 3, 3), "T")
        cv.fill({(x - 1, int(cy + 10)), (x + 1, int(cy + 10))}, "M")


def chalk(cv, x, y):
    cv.fill(rect(int(x) - 1, int(y) - 1, 2, 2), "W")


def scientist_idle_frame(i):
    """Menggaruk rambut sambil menatap rumus di papan, kapur di tangan kanan; sesekali menoleh dan berkedip."""
    cv = Canvas()
    t = i % 16
    eyes = ("side", "side", "side", "side", "side", "blink", "side", "side",
            "look", "look", "look", "side", "side", "side", "side", "side")[t]
    scratch = (t // 2) % 2
    scientist_base(cv, t, eyes, "flat", bounce=scratch)
    arm(cv, (SX - 7, TOP + 3), (SX - 7, CY - 8 + scratch), elbow=(SX - 13, CY + 2), fur="h")
    arm(cv, (SX + 7, TOP + 3), (SX + 12, TOP + 7), elbow=(SX + 11, TOP + 10), fur="h")
    chalk(cv, SX + 13, TOP + 5)
    return cv


# (fase, dorong mundur, rambut, ukuran kepulan 0 = tidak ada)
SCI_SHOCK = [("write", 0, 0, 0), ("write", 0, 0, 0), ("write", 0, 0, 0), ("write", 0, 0, 0), ("poof", 0, 1, 1),
             ("shock", -2, 3, 2), ("shock", -2, 3, 3), ("shock", -2, 2, 3), ("shock", -2, 3, 4), ("shock", -1, 2, 4),
             ("shock", -1, 2, 3), ("calm", -1, 1, 2), ("calm", 0, 1, 1), ("calm", 0, 0, 0), ("write", 0, 0, 0),
             ("write", 0, 0, 0)]


def scientist_shocked_frame(i):
    """Kapur menyentuh papan, kepulan asap kecil meletup, rambut makin liar, mata lebar, "!", lalu tenang lagi."""
    cv = Canvas()
    t = i % 16
    phase, dx, hair, smoke = SCI_SHOCK[t]
    face = {"write": ("side", "flat"), "poof": ("wide", "up"), "shock": ("wide", "up"), "calm": ("look", "worried")}[phase]
    scientist_base(cv, t, face[0], face[1], dx=dx, bounce=hair)
    px, py = 44, 18  # titik kapur di papan
    if phase in ("write", "poof"):
        arm(cv, (SX + 7, TOP + 3), (px, py + (t % 2)), elbow=(SX + 15, TOP + 2), fur="h")
        chalk(cv, px + 1, py - 1 + (t % 2))
    else:
        arm(cv, (SX + 7 + dx, TOP + 3), (SX + 12 + dx, TOP + 1), elbow=(SX + 13 + dx, TOP + 6), fur="h")
        chalk(cv, SX + 13 + dx, TOP - 1)
    arm(cv, (SX - 7 + dx, TOP + 3), (SX - 9 + dx, TOP + 10), elbow=(SX - 10 + dx, TOP + 6), fur="h")
    if smoke:  # kepulan naik dan membesar dari titik kapur, garis kaget di sampingnya
        rise = max(0, smoke - 1)
        puff(cv, px + 2, py + 3 - rise, 1.0 + smoke * 0.45)
        if smoke >= 3:
            puff(cv, px + 6, py + 1 - rise, 0.8 + smoke * 0.3)
    if phase == "shock":
        spark_lines(cv, SX - 14 + dx, 6)
        spark_lines(cv, SX + 13 + dx, 4)
        bubble(cv, 50, 25, 9, 9, fill="R", tail_dir=-1)
        mini_text(cv, "!", 52, 27, "W")
    return cv


# (fase lengan, lompat)
SCI_VICTORY = [("write", 0), ("write", 0), ("up", 1), ("up", 0), ("up", 1), ("up", 0), ("up", 1), ("up", 0),
               ("up", 1), ("up", 0), ("up", 1), ("up", 0), ("mid", 0), ("mid", 0), ("write", 0), ("write", 0)]


def scientist_victory_frame(i):
    """Menulis "!" di pojok papan, lalu kapur diangkat tinggi, lompat kecil, lidah menjulur seperti aslinya."""
    cv = Canvas()
    t = i % 16
    phase, hop = SCI_VICTORY[t]
    up = phase == "up"
    scientist_base(cv, t, "happy" if up else "side", "up" if up else "flat", bob=-hop, bounce=hop, tongue=up and t % 2 == 1)
    if t >= 1:
        mini_text(cv, "!", 50, 7, "W")
    if phase == "write":
        hx, hy = 58, 13 + (t % 2)
        arm(cv, (SX + 7, TOP + 3), (hx, hy), elbow=(SX + 17, TOP + 1), fur="h")
        chalk(cv, hx + 1, hy - 1)
        arm(cv, (SX - 7, TOP + 3), (SX - 9, TOP + 10), elbow=(SX - 10, TOP + 6), fur="h")
    elif phase == "mid":
        arm(cv, (SX + 7, TOP + 3), (SX + 12, TOP - 2), elbow=(SX + 13, TOP + 4), fur="h")
        chalk(cv, SX + 12, TOP - 5)
        arm(cv, (SX - 7, TOP + 3), (SX - 11, TOP + 2), elbow=(SX - 12, TOP + 7), fur="h")
    else:
        arm(cv, (SX + 7, TOP + 3 - hop), (SX + 12, 7 - hop), elbow=(SX + 13, TOP - 2 - hop), fur="h")
        chalk(cv, SX + 12, 4 - hop)
        arm(cv, (SX - 7, TOP + 3 - hop), (SX - 13, 9 - hop), elbow=(SX - 13, TOP - 1 - hop), fur="h")
        if t % 4 == 2:
            cv.fill({(SX + 16, 2), (SX + 15, 2), (SX + 17, 2), (SX + 16, 1), (SX + 16, 3)}, "W")
    return cv


# ================================================================== Gerbang D: Mathematician
def math_vest(cv, cx, top):
    """Rompi ungu (PAL_EXT p/j) di atas badan berbulu: kerah V, belahan tengah, tiga kancing emas."""
    dressed_body(cv, cx, top, "p", "j", pants="L", pants_shade="q")
    cv.fill({(cx - 2, top), (cx - 1, top + 1), (cx, top + 1), (cx + 1, top), (cx - 1, top), (cx, top),
             (cx - 1, top + 2), (cx, top + 2)}, "B")
    cv.fill({(cx, y) for y in range(top + 3, top + 11)}, "j")
    for y in (top + 4, top + 7, top + 10):
        cv.put(cx - 1, y, "O")


def slate(cv, x, y, mark=None, arc=0):
    """Batu tulis genggam 11x9: bingkai kayu, permukaan abu gelap. mark = glyph yang tertulis (v),
    arc = jumlah titik lingkaran yang sudah digambar jangka (0-12)."""
    solid(cv, rect(x, y, 11, 9), "X", None)
    cv.fill(rect(x + 2, y + 2, 7, 5), "l")
    cx, cy = x + 5, y + 4
    for k in range(min(arc, 12)):
        a = k / 12.0 * 2 * math.pi
        cv.put(int(round(cx + 2.4 * math.cos(a))), int(round(cy + 1.6 * math.sin(a))), "W")
    if mark:
        mini_text(cv, mark, x + 3, y + 2, "W")


def compass(cv, hx, hy, deg, spread=24):
    """Jangka: engsel emas di (hx, hy), dua kaki perak sepanjang 7 yang membuka +-spread derajat dari arah deg."""
    for s in (-1, 1):
        a = math.radians(deg + s * spread)
        ex, ey = hx + 7 * math.cos(a), hy + 7 * math.sin(a)
        cv.fill(capsule((hx, hy), (ex, ey), 0.5), "G")
        cv.put(int(round(ex)), int(round(ey)), "K" if s > 0 else "s")
    cv.fill(rect(int(hx) - 1, int(hy) - 1, 2, 2), "O")
    cv.put(int(hx), int(hy) - 2, "x")


def math_base(cv, t, eyes, brows, mouth, bob=0):
    tail(cv, (CX - 7, TOP + 14), phase=t * 0.45, flip=-1, length=8)
    math_vest(cv, CX, TOP + bob)
    head(cv, CX, CY + bob, eyes=eyes, brows=brows, mouth=mouth)


def math_idle_frame(i):
    """Batu tulis bergambar lingkaran di pangkuan; jangka diangkat di samping bahu dan diputar pelan
    sambil menatap batu tulis; sesekali melirik jangka dan berkedip."""
    cv = Canvas()
    t = i % 16
    eyes = "blink" if t == 9 else ("side" if t in (12, 13) else "down")
    math_base(cv, t, eyes, "flat", "flat")
    sx, sy = CX - 5, TOP + 8
    slate(cv, sx, sy, arc=12)
    arm(cv, (CX - 7, TOP + 3), (sx, sy + 5), elbow=(CX - 11, TOP + 7))
    hx, hy = CX + 15, TOP - 3
    compass(cv, hx, hy, 90 + 22.5 * t, spread=16)  # satu putaran penuh per 16 frame
    arm(cv, (CX + 7, TOP + 3), (hx - 1, hy + 1), elbow=(CX + 13, TOP + 5))
    return cv


def math_thinking_frame(i):
    """Batu tulis diturunkan ke pangkuan, ujung jangka mengetuk dagu; gelembung "..." lalu "?"."""
    cv = Canvas()
    t = i % 16
    eyes = "blink" if t == 4 else "side"
    math_base(cv, t, eyes, "worried", "frown" if t >= 8 else "flat")
    slate(cv, CX - 5, TOP + 9, arc=12)
    arm(cv, (CX - 7, TOP + 3), (CX - 5, TOP + 13), elbow=(CX - 11, TOP + 8))
    tap = t % 2 if 5 <= t <= 13 else 0
    hx, hy = CX + 8, CY + 5 + tap
    compass(cv, hx, hy, 160, spread=10)
    arm(cv, (CX + 7, TOP + 3), (hx + 1, hy + 1), elbow=(CX + 12, TOP + 6))
    if 5 <= t <= 13:
        dots_or_mark(cv, CX + 12, 0, 5, t, "?")
    return cv


# (fase, lompat): menulis centang di batu tulis, lalu mengangkatnya tinggi
MATH_VICTORY = [("write", 0), ("write", 0), ("mid", 0), ("up", 1), ("up", 0), ("up", 1), ("up", 0), ("up", 1),
                ("up", 0), ("up", 1), ("up", 0), ("up", 1), ("mid", 0), ("mid", 0), ("write", 0), ("write", 0)]


def math_victory_frame(i):
    """Jangka menggoreskan centang v di batu tulis, lalu batu tulis diangkat tinggi dengan bangga, lompat kecil."""
    cv = Canvas()
    t = i % 16
    phase, hop = MATH_VICTORY[t]
    up = phase == "up"
    math_base(cv, t, "happy" if up else "down", "up" if up else "flat", ("o" if t % 2 else "smile") if up else "smile", bob=-hop)
    mark = "v" if t >= 1 else None
    if phase == "write":
        sx, sy = CX - 5, TOP + 7
        slate(cv, sx, sy, mark=mark)
        arm(cv, (CX - 7, TOP + 3), (sx, sy + 6), elbow=(CX - 11, TOP + 7))
        compass(cv, sx + 9, sy - 3 + (t % 2), 110, spread=14)
        arm(cv, (CX + 7, TOP + 3), (sx + 10, sy - 4 + (t % 2)), elbow=(CX + 11, TOP + 7))
    elif phase == "mid":
        sx, sy = CX - 22, TOP - 6
        slate(cv, sx, sy, mark=mark)
        arm(cv, (CX - 7, TOP + 3), (sx + 9, sy + 7), elbow=(CX - 13, TOP + 5))
        compass(cv, CX + 12, TOP + 2, 80, spread=16)
        arm(cv, (CX + 7, TOP + 3), (CX + 12, TOP + 3), elbow=(CX + 12, TOP + 7))
    else:
        sx, sy = CX - 24, 2 - hop
        slate(cv, sx, sy, mark=mark)
        arm(cv, (CX - 7, TOP + 3 - hop), (sx + 9, sy + 8), elbow=(CX - 14, TOP - 1 - hop))
        compass(cv, CX + 14, 6 - hop, 70, spread=18)
        arm(cv, (CX + 7, TOP + 3 - hop), (CX + 14, 7 - hop), elbow=(CX + 14, TOP - 1 - hop))
        if t % 4 == 1:
            cv.fill({(sx - 2, sy + 1), (sx - 3, sy + 1), (sx - 1, sy + 1), (sx - 2, sy), (sx - 2, sy + 2)}, "W")
    return cv


PROPS = {
    "scientist: papan tulis (asli)": lambda cv: chalkboard(cv, 20, 10, 29, 16, "E=mc", 4),
    "mathematician: batu tulis": lambda cv: slate(cv, 26, 20, mark="v"),
    "mathematician: jangka": lambda cv: compass(cv, 30, 20, 90, spread=24),
}


SCENES = {
    "greek-philosopher-idle": (greek_idle_frame, 16, lambda i: 190 if i % 16 != 4 else 120),
    "greek-philosopher-victory": (greek_victory_frame, 16, lambda i: 150 if i % 16 in (0, 1, 13, 14, 15) else 120),
    "greek-philosopher-defeated": (greek_defeated_frame, 16, lambda i: 140 if i % 16 < 8 else (260 if i % 16 in (8, 9, 10, 11) else 170)),
    "academic-thinking": (academic_thinking_frame, 16, lambda i: 180 if i % 16 != 6 else 120),
    "academic-victory": (academic_victory_frame, 16, lambda i: 150 if i % 16 in (0, 1, 12, 13, 14, 15) else 100),
    "academic-defeated": (academic_defeated_frame, 16, lambda i: 260 if 7 <= i % 16 <= 10 else 200),
    "normal-thinking": (normal_thinking_frame, 16, lambda i: 170),
    "normal-victory": (normal_victory_frame, 16, lambda i: 110 if 2 <= i % 16 <= 11 else 150),
    "normal-defeated": (normal_defeated_frame, 16, lambda i: 260 if 6 <= i % 16 <= 9 else 200),
    "scientist-idle": (scientist_idle_frame, 16, lambda i: 170 if i % 16 != 5 else 120),
    "scientist-shocked": (scientist_shocked_frame, 16, lambda i: 150 if i % 16 < 4 else (110 if i % 16 == 4 else (220 if i % 16 in (5, 6) else 150))),
    "scientist-victory": (scientist_victory_frame, 16, lambda i: 160 if i % 16 in (0, 1, 12, 13, 14, 15) else 110),
    "mathematician-idle": (math_idle_frame, 16, lambda i: 170 if i % 16 != 9 else 120),
    "mathematician-thinking": (math_thinking_frame, 16, lambda i: 170 if i % 16 != 4 else 120),
    "mathematician-victory": (math_victory_frame, 16, lambda i: 150 if i % 16 in (0, 1, 2, 12, 13, 14, 15) else 110),
}
