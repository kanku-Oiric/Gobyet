"""State tambahan untuk Normal dan kostum DOMAIN (Fase 2, bertahap per gerbang).

Gerbang C: Greek Philosopher (idle, victory, defeated), Academic (thinking, victory, defeated),
Normal (thinking, victory, defeated).

Tampilan kostum mengikuti aset asli yang terkunci, tanpa desain ulang: Greek Philosopher memakai
toga, janggut, laurel hijau, gulungan, dan tiang dari filsuf-yunani; Academic memakai kemeja putih,
dasi merah, topi toga, dan ijazah dari wisuda; Normal adalah Gobyet tanpa kostum dengan pisang dari
makan-pisang. Fungsi gambar kostum dipakai ulang dari src/costumes.py. Satu-satunya bentuk baru
adalah pose rebah (lying_body) untuk defeated.
"""
from monkey import Canvas, head, arm, tail, sitting_body, banana, puff, ellipse, capsule, rect, solid
from costumes import CX, CY, TOP, dressed_body, inner, confetti, mortarboard, laurel, beard, scroll, column
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
}
