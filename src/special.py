"""Kostum spesial Gobyet (Fase 2, Gerbang G): normal-gblk.

Tampilan Gobyet Normal persis (badan berbulu, tanpa kostum) dengan satu prop: papan tanda bertongkat
kayu bertuliskan GBLK. Papan krem-kuning (n) bergaris tepi K, tulisan K kontras tinggi, 27x11 piksel.
Kepanjangan akronim hanya ada di caption manifest dan dokumentasi, tidak pernah di papan.

Tarian (dance-a/b/c): tepat 16 frame x 120 ms, pose besar berganti di f0, f4, f8, f12. Di dalam satu
beat hanya ekor yang bergerak halus. Papan tidak pernah keluar dari kanvas di frame mana pun.
"""
from monkey import Canvas, head, arm, tail, sitting_body, mini_text, puff, spark_lines, rect, solid
from costumes import CX, CY, TOP, confetti

SIGN_W, SIGN_H = 27, 11
TEXT = "GBLK"


def sign(cv, x, y, front=True, text_color="K", stick=None):
    """Papan GBLK 27x11 dengan pojok kiri atas (x, y). front=False = sisi belakang polos.
    stick = (x_bawah, y_bawah): tongkat kayu dari tepi bawah papan ke titik itu (digambar lebih dulu)."""
    if stick:
        sx = x + SIGN_W // 2
        cv.fill({(sx, yy) for yy in range(y + SIGN_H, stick[1] + 1)} | {(sx + 1, yy) for yy in range(y + SIGN_H, stick[1] + 1)}, "N")
    board = rect(x, y, SIGN_W, SIGN_H)
    if front:
        solid(cv, board, "n", "y", shade_off=(1, 1))
        mini_text(cv, TEXT, x + 2, y + 3, text_color)
    else:
        solid(cv, board, "c", "x", shade_off=(1, 1))
        cv.fill({(x + 3 + k * 4, y + 5) for k in range(6)}, "x")  # serat karton di sisi belakang


def edge_on(cv, x, y, stick=None):
    """Papan sedang dibalik: terlihat dari samping, hanya tebalnya."""
    sx = x + SIGN_W // 2
    if stick:
        cv.fill({(sx, yy) for yy in range(y + SIGN_H, stick[1] + 1)} | {(sx + 1, yy) for yy in range(y + SIGN_H, stick[1] + 1)}, "N")
    solid(cv, rect(sx - 1, y - 1, 4, SIGN_H + 2), "y", None)


def gblk_body(cv, t, dx=0, bob=0, tail_phase=None):
    tail(cv, (CX - 6 + dx, TOP + 14 + bob), phase=(t * 0.5 if tail_phase is None else tail_phase), flip=-1, length=8)
    sitting_body(cv, CX + dx, TOP + bob)


SX, SY = 36, 1  # posisi papan saat dipegang tegak di kanan atas


def hold_sign_right(cv, sx=SX, sy=SY, dx=0, bob=0, front=True, text_color="K"):
    hand = (sx + SIGN_W // 2 - 1, TOP + 5 + bob)
    sign(cv, sx, sy, front=front, text_color=text_color, stick=hand)
    arm(cv, (CX + 7 + dx, TOP + 3 + bob), hand, elbow=(CX + 11 + dx, TOP + 8 + bob))


def gblk_idle_frame(i):
    """Memegang papan GBLK dengan bangga; papan sedikit berayun, sesekali berkedip."""
    cv = Canvas()
    t = i % 16
    sway = (0, 0, 1, 1, 0, 0, -1, -1)[t % 8]
    gblk_body(cv, t)
    head(cv, CX, CY, eyes="blink" if t == 10 else "look", brows="flat", mouth="smile")
    hold_sign_right(cv, SX + sway, SY)
    arm(cv, (CX - 7, TOP + 3), (CX - 7, TOP + 9), elbow=(CX - 12, TOP + 6))  # tangan kiri di pinggang
    return cv


# (fase papan): belakang polos -> dibalik dengan sentakan -> GBLK
REVEAL = ["back", "back", "back", "back", "back", "lift", "edge", "front", "front", "front", "front", "front",
          "front", "front", "front", "front"]


def gblk_reveal_frame(i):
    """Papan awalnya polos (sisi belakang), lalu dibalik dengan sentakan dan GBLK muncul."""
    cv = Canvas()
    t = i % 16
    phase = REVEAL[t]
    lift = {"lift": -1, "edge": -2, "front": 0}.get(phase, 0)
    gblk_body(cv, t)
    eyes = "side" if phase == "back" else ("wide" if phase in ("lift", "edge") else ("happy" if t in (8, 9, 10) else "look"))
    head(cv, CX, CY, eyes=eyes, brows="up" if phase in ("edge", "front") else "flat",
         mouth="o" if phase in ("edge",) or t == 7 else ("smile" if phase == "front" else "flat"))
    hand = (SX + SIGN_W // 2 - 1, TOP + 5 + lift)
    if phase == "edge":
        edge_on(cv, SX, SY, stick=hand)
    else:
        sign(cv, SX, SY, front=phase == "front", stick=hand)
    arm(cv, (CX + 7, TOP + 3), hand, elbow=(CX + 11, TOP + 8))
    arm(cv, (CX - 7, TOP + 3), (CX - 7, TOP + 9), elbow=(CX - 12, TOP + 6))
    if t in (7, 8):  # sentakan
        spark_lines(cv, SX - 3, SY + 2)
        spark_lines(cv, SX + SIGN_W + 1, SY + 2)
    return cv


def gblk_happy_frame(i):
    """Melambaikan papan kiri-kanan dengan senyum lebar."""
    cv = Canvas()
    t = i % 12
    wave = (0, 2, 4, 4, 2, 0, -2, -4, -4, -2, 0, 0)[t]
    gblk_body(cv, t)
    head(cv, CX, CY, eyes="happy", brows="flat", mouth="smile" if t % 4 < 2 else "o")
    hold_sign_right(cv, 33 + wave, SY)
    arm(cv, (CX - 7, TOP + 3), (CX - 12, TOP + 1), elbow=(CX - 12, TOP + 6))
    return cv


LOW = 3  # untuk pose papan di atas kepala: tokoh diturunkan supaya papan tetap di dalam kanvas


def gblk_victory_frame(i):
    """Papan GBLK diangkat di atas kepala dengan dua tangan, tulisannya berkedip merah-gelap, konfeti."""
    cv = Canvas()
    t = i % 16
    up = 2 <= t <= 13
    hop = 1 if up and t % 2 == 0 else 0
    tail(cv, (CX - 6, TOP + 14 + LOW - hop), phase=t * 0.5, flip=-1, length=8)
    sitting_body(cv, CX, TOP + LOW - hop)
    head(cv, CX, CY + LOW - hop, eyes="happy" if up else "look", brows="flat", mouth=("o" if t % 2 else "smile") if up else "smile")
    if up:
        confetti(cv, t, n=8)  # digambar lebih dulu supaya tidak menimpa tulisan papan
        bx, by = CX - SIGN_W // 2, 0
        sign(cv, bx, by, text_color="R" if (t // 2) % 2 else "K")
        arm(cv, (CX - 7, TOP + 3 + LOW - hop), (bx + 3, by + SIGN_H), elbow=(CX - 13, TOP + LOW - hop))
        arm(cv, (CX + 7, TOP + 3 + LOW - hop), (bx + SIGN_W - 4, by + SIGN_H), elbow=(CX + 13, TOP + LOW - hop))
    else:
        hand = (SX + SIGN_W // 2 - 1, TOP + 5 + LOW)
        sign(cv, SX, SY + 1, stick=hand)
        arm(cv, (CX + 7, TOP + 3 + LOW), hand, elbow=(CX + 11, TOP + 8 + LOW))
        arm(cv, (CX - 7, TOP + 3 + LOW), (CX - 7, TOP + 9 + LOW), elbow=(CX - 12, TOP + 6 + LOW))
    return cv


def gblk_defeated_frame(i):
    """Papan diturunkan ke depan badan; Gobyet mengintip dari baliknya dengan lesu. GBLK tetap terbaca."""
    cv = Canvas()
    t = i % 16
    sink = 1 if t in (6, 7, 8, 9) else 0
    gblk_body(cv, t, bob=1)
    head(cv, CX, CY + 2 + sink, eyes="blink" if t == 12 else "relief", brows="worried", mouth="frown")
    bx, by = CX - SIGN_W // 2, TOP - 1 + sink
    sign(cv, bx, by)
    for s in (-1, 1):  # jari memegang tepi atas papan
        cv.fill(rect(CX + s * 9 - 1, by - 1, 2, 2), "F")
    if 6 <= t <= 9:
        puff(cv, CX + 14 + (t - 6), CY + 3 - (t - 6), 1.2 + (t - 6) * 0.35)
    return cv


# ---- tarian: papan di atas kepala dengan dua tangan. Per beat: (geser badan, lompat, geser papan, naik-turun papan).
# Di dalam satu beat hanya ekor yang bergerak halus; pose besar berganti di f0, f4, f8, f12.
def dance_frame(t, beats):
    beat = t // 4
    dx, bob, sdx, sdy = beats[beat]
    cv = Canvas()
    y0 = TOP + LOW + bob
    tail(cv, (CX - 6 + dx, y0 + 14), phase=beat * 1.6 + (t % 4) * 0.25, flip=-1, length=8)
    sitting_body(cv, CX + dx, y0)
    head(cv, CX + dx, CY + LOW + bob, eyes="happy", brows="flat", mouth="smile" if beat % 2 == 0 else "o")
    bx, by = CX - SIGN_W // 2 + dx + sdx, 2 + bob + sdy
    sign(cv, bx, by)
    arm(cv, (CX - 7 + dx, y0 + 3), (bx + 3, by + SIGN_H), elbow=(CX - 13 + dx, y0))
    arm(cv, (CX + 7 + dx, y0 + 3), (bx + SIGN_W - 4, by + SIGN_H), elbow=(CX + 13 + dx, y0))
    return cv


# dance-a: goyang pinggul, papan berayun kiri-kanan
DANCE_A = [(-2, 0, -6, 0), (0, 1, 0, 1), (2, 0, 6, 0), (0, 1, 0, 1)]
# dance-b: lompat-lompat di tempat, papan ikut naik-turun
DANCE_B = [(0, -2, 0, 0), (0, 1, 0, 1), (0, -2, 0, 0), (0, 1, 0, 1)]
# dance-c: langkah geser ke samping, papan mengangguk (turun 3 px di beat ganjil)
DANCE_C = [(-5, 0, 0, 0), (0, 0, 0, 3), (5, 0, 0, 0), (0, 0, 0, 3)]


def gblk_dance_a_frame(i):
    return dance_frame(i % 16, DANCE_A)


def gblk_dance_b_frame(i):
    return dance_frame(i % 16, DANCE_B)


def gblk_dance_c_frame(i):
    return dance_frame(i % 16, DANCE_C)


PROPS = {
    "normal-gblk: papan GBLK": lambda cv: sign(cv, 18, 10, stick=(31, 30)),
}

DANCE_MS = lambda i: 120  # noqa: E731

SCENES = {
    "normal-gblk-idle": (gblk_idle_frame, 16, lambda i: 170 if i % 16 != 10 else 120),
    "normal-gblk-reveal": (gblk_reveal_frame, 16, lambda i: 160 if i % 16 < 5 else (90 if i % 16 in (5, 6) else (220 if i % 16 == 7 else 150))),
    "normal-gblk-happy": (gblk_happy_frame, 12, lambda i: 120),
    "normal-gblk-victory": (gblk_victory_frame, 16, lambda i: 150 if i % 16 in (0, 1, 14, 15) else 110),
    "normal-gblk-defeated": (gblk_defeated_frame, 16, lambda i: 240 if 6 <= i % 16 <= 9 else 190),
    "normal-gblk-dance-a": (gblk_dance_a_frame, 16, DANCE_MS),
    "normal-gblk-dance-b": (gblk_dance_b_frame, 16, DANCE_MS),
    "normal-gblk-dance-c": (gblk_dance_c_frame, 16, DANCE_MS),
}
