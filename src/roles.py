"""Kostum ROLE Gobyet untuk Battle Royale Argumen (Fase 2, bertahap per gerbang).

Gerbang A: Referee (idle, thinking). Semua memakai rig yang sama dengan aset asli:
kanvas 64x48, palet PAL, garis tepi K, badan duduk berbaju dari costumes.dressed_body.
"""
from monkey import Canvas, head, arm, tail, mini_text, bubble, ellipse, capsule, chain, rect, solid
from costumes import CX, CY, TOP, dressed_body, inner


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


SCENES = {
    "referee-idle": (referee_idle_frame, 16, lambda i: 170 if i % 16 not in (6, 14) else 120),
    "referee-thinking": (referee_thinking_frame, 18, lambda i: 150 if i % 18 < 10 else 190),
}
