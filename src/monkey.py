"""Rig pixel art Gobyet: bentuk dasar (elips, kapsul) -> sprite berlapis dengan garis tepi -> frame animasi."""
import math
from PIL import Image

W, H = 64, 48
PAL = {
    "K": (52, 30, 18), "B": (139, 90, 55), "b": (108, 66, 38), "F": (226, 172, 128), "f": (198, 142, 100),
    "A": (236, 140, 108), "a": (206, 110, 84),  # wajah memerah (marah)
    "E": (201, 132, 96), "W": (250, 247, 240), "P": (26, 18, 14), "M": (86, 42, 28), "T": (196, 72, 64),
    "Y": (247, 208, 72), "y": (216, 160, 38), "N": (96, 70, 30), "n": (236, 226, 150),
    "L": (30, 30, 36), "l": (64, 64, 74), "G": (214, 214, 220),
    "C": (246, 234, 208), "c": (214, 194, 160), "D": (74, 42, 26),
    "S": (240, 238, 234), "s": (168, 162, 156), "R": (226, 58, 48), "r": (255, 130, 96), "O": (255, 214, 90),
    # kostum
    "H": (242, 242, 240), "h": (196, 196, 202), "g": (150, 150, 160),  # rambut/janggut putih, sweter abu
    "V": (96, 176, 72), "v": (58, 122, 48),  # daun zaitun
    "Q": (62, 66, 78), "q": (42, 44, 54), "Z": (80, 226, 120),  # hoodie, layar hijau
    "U": (150, 62, 40), "u": (112, 44, 28),  # batik
    "X": (176, 136, 84), "x": (128, 94, 56), "d": (156, 118, 72), "e": (122, 90, 52),  # topi & mantel detektif
    "I": (196, 228, 246), "k": (44, 76, 60), "m": (232, 228, 218),  # lensa, papan tulis, marmer
}


class Canvas:
    def __init__(self):
        self.px = {}

    def put(self, x, y, c):
        if 0 <= x < W and 0 <= y < H and c:
            self.px[(int(x), int(y))] = c

    def fill(self, pts, c):
        for p in pts:
            self.put(p[0], p[1], c)

    def image(self, scale=1, bg=None):
        im = Image.new("RGBA", (W, H), bg + (255,) if bg else (0, 0, 0, 0))
        for (x, y), c in self.px.items():
            im.putpixel((x, y), PAL[c] + (255,))
        return im.resize((W * scale, H * scale), Image.NEAREST) if scale != 1 else im


def ellipse(cx, cy, rx, ry):
    out = set()
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0:
                out.add((x, y))
    return out


def capsule(p0, p1, r):
    (x0, y0), (x1, y1) = p0, p1
    out = set()
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy or 1e-9
    for y in range(int(min(y0, y1) - r) - 1, int(max(y0, y1) + r) + 2):
        for x in range(int(min(x0, x1) - r) - 1, int(max(x0, x1) + r) + 2):
            px, py = x + 0.5, y + 0.5
            t = max(0, min(1, ((px - x0) * dx + (py - y0) * dy) / L2))
            if (px - x0 - t * dx) ** 2 + (py - y0 - t * dy) ** 2 <= r * r:
                out.add((x, y))
    return out


def chain(points, r):
    out = set()
    for a, b in zip(points, points[1:]):
        out |= capsule(a, b, r)
    return out


def rect(x, y, w, h):
    return {(i, j) for i in range(x, x + w) for j in range(y, y + h)}


def edge(mask):
    return {(x, y) for (x, y) in mask if any((x + dx, y + dy) not in mask for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}


def solid(cv, mask, fill, shade=None, outline="K", shade_off=(2, 2)):
    """Isi bentuk, beri bayangan di sisi kanan-bawah, lalu garis tepi gelap."""
    cv.fill(mask, fill)
    if shade:
        sx, sy = shade_off
        cv.fill({(x, y) for (x, y) in mask if (x - sx, y - sy) not in mask}, shade)
    if outline:
        cv.fill(edge(mask), outline)


# ------------------------------------------------------------------ kepala
def head(cv, cx, cy, eyes="look", brows="flat", mouth="frown", face="F", tilt=0):
    """Kepala tampak depan: telinga, bulu, wajah bentuk hati, mata besar, alis, mulut."""
    fs = "f" if face == "F" else "a"
    for s in (-1, 1):  # telinga di belakang kepala
        ear = ellipse(cx + s * 10.5, cy + 1.5 + (tilt * s * 0.5), 3.6, 3.8)
        solid(cv, ear, "B", "b")
        cv.fill(ellipse(cx + s * 10.3, cy + 1.7 + (tilt * s * 0.5), 1.9, 2.1), "E")
    skull = ellipse(cx, cy, 9.6, 8.4)
    solid(cv, skull, "B", "b")
    facep = ellipse(cx - 3.8, cy + 1.2, 4.4, 4.0) | ellipse(cx + 3.8, cy + 1.2, 4.4, 4.0) | ellipse(cx, cy + 4.6, 6.2, 3.4)
    facep = {p for p in facep if p in skull and p not in edge(skull)}
    cv.fill(facep, face)
    cv.fill({(x, y) for (x, y) in facep if (x, y + 1) not in facep or (x, y + 2) not in facep}, fs)
    ex = (cx - 4, cx + 4)
    ey = int(cy + 0.4)
    for i, x0 in enumerate(ex):
        x0 = int(x0)
        if eyes in ("look", "wide", "down", "side", "left"):
            h = 4 if eyes != "wide" else 5
            white = rect(x0 - 2, ey - 2, 4, h) - {(x0 - 2, ey - 2), (x0 + 1, ey - 2), (x0 - 2, ey - 3 + h), (x0 + 1, ey - 3 + h)}
            cv.fill(white, "W")
            if eyes == "wide":
                cv.fill(rect(x0 - 1 + i * 0, ey - 1, 2, 2), "P")
            elif eyes == "down":
                cv.fill(rect(x0 - 1 + i, ey, 2, 2), "P")
            elif eyes == "side":
                cv.fill(rect(x0, ey - 1, 2, 2), "P")
            elif eyes == "left":
                cv.fill(rect(x0 - 2, ey - 1, 2, 2), "P")
            else:
                cv.fill(rect(x0 - 1 + i, ey - 1, 2, 2), "P")
        elif eyes == "blink":
            cv.fill(rect(x0 - 2, ey, 4, 1), "K")
        elif eyes == "happy":  # ^ ^
            cv.fill({(x0 - 2, ey), (x0 - 1, ey - 1), (x0, ey - 1), (x0 + 1, ey)}, "K")
        elif eyes == "angry":
            white = rect(x0 - 2, ey - 1, 4, 3) - {(x0 - 2, ey + 1), (x0 + 1, ey + 1)}
            cv.fill(white, "W")
            cv.fill(rect(x0 - 1 + (1 if i == 0 else 0), ey, 2, 1), "P")
            cv.fill(rect(x0 - 1 + (1 if i == 0 else 0), ey - 1, 2, 1), "P")
        elif eyes == "relief":  # setengah tertutup, lega
            cv.fill(rect(x0 - 2, ey, 4, 2), "W")
            cv.fill(rect(x0 - 2, ey - 1, 4, 1), "K")
            cv.fill(rect(x0 - 1 + i, ey + 1, 2, 1), "P")
    # alis
    for i, x0 in enumerate(ex):
        x0 = int(x0)
        by = ey - 3 - (1 if eyes == "wide" else 0)
        if brows == "flat":
            cv.fill(rect(x0 - 2, by, 4, 1), "K")
        elif brows == "worried":  # ujung dalam naik
            inner = x0 + 1 if i == 0 else x0 - 2
            cv.fill(rect(x0 - 2, by, 4, 1), "K")
            cv.put(inner, by - 1, "K")
        elif brows == "angry":  # ujung dalam turun tajam
            pts = [(x0 - 2, by - 1), (x0 - 1, by - 1), (x0, by), (x0 + 1, by + 1)] if i == 0 else [(x0 + 1, by - 1), (x0, by - 1), (x0 - 1, by), (x0 - 2, by + 1)]
            cv.fill(pts, "K")
            cv.fill([(p[0], p[1] - 1) for p in pts[1:]], "K")
        elif brows == "up":
            cv.fill(rect(x0 - 2, by - 1, 4, 1), "K")
        elif brows == "raised":  # skeptis: alis kiri turun, alis kanan melengkung naik
            if i == 0:
                cv.fill({(x0 - 2, by), (x0 - 1, by), (x0, by + 1), (x0 + 1, by + 1)}, "K")
            else:
                cv.fill({(x0 - 2, by - 1), (x0 - 1, by - 2), (x0, by - 2), (x0 + 1, by - 1)}, "K")
    # hidung dan mulut
    my = int(cy + 4)
    cv.put(cx - 1, my - 1, "M"); cv.put(cx, my - 1, "M")
    if mouth == "frown":
        cv.fill({(cx - 2, my + 2), (cx - 1, my + 1), (cx, my + 1), (cx + 1, my + 2)}, "M")
    elif mouth == "flat":
        cv.fill(rect(cx - 2, my + 1, 4, 1), "M")
    elif mouth == "smile":
        cv.fill({(cx - 2, my + 1), (cx - 1, my + 2), (cx, my + 2), (cx + 1, my + 1)}, "M")
    elif mouth == "smirk":  # datar dengan sudut kanan naik
        cv.fill({(cx - 2, my + 2), (cx - 1, my + 2), (cx, my + 2), (cx + 1, my + 1)}, "M")
    elif mouth == "shout":
        cv.fill(rect(cx - 2, my + 1, 4, 3), "M")
        cv.fill(rect(cx - 1, my + 3, 2, 1), "T")
        cv.fill({(cx - 2, my + 1), (cx + 1, my + 1)}, "W")
    elif mouth == "chew":
        cv.fill(rect(cx - 2, my + 1, 4, 2), "M")
        cv.fill(rect(cx - 1, my + 2, 2, 1), "T")
    elif mouth == "chomp":
        cv.fill({(cx - 2, my + 1), (cx + 1, my + 1), (cx - 1, my + 2), (cx, my + 2)}, "M")
        cv.fill({(cx - 3, my), (cx + 2, my)}, fs)  # pipi mengembung
    elif mouth == "o":
        cv.fill(rect(cx - 1, my + 1, 2, 2), "M")


# ------------------------------------------------------------------ badan
def arm(cv, shoulder, hand, elbow=None, fur="B", hand_r=2.0, r=1.8):
    """Lengan gemuk dengan siku opsional, telapak krem."""
    pts = [shoulder] + ([elbow] if elbow else []) + [hand]
    solid(cv, chain(pts, r), fur, None)
    solid(cv, ellipse(hand[0], hand[1], hand_r, hand_r), "F", "f", shade_off=(1, 1))


def tail(cv, base, phase=0.0, flip=1, length=9, curl=3.0):
    """Ekor: lengkung S dari pangkal lalu spiral besar di ujung (seperti gambar asli)."""
    bx, by = base
    pts = []
    for i in range(12):
        t = i / 11
        x = bx + flip * t * length
        y = by + 2.5 * math.sin(t * math.pi) + math.sin(t * 4 + phase) * 0.8
        pts.append((x, y))
    ex, ey = pts[-1]
    cx, cy = ex, ey - curl
    for i in range(1, 17):
        a = math.pi / 2 - flip * (i / 16) * math.pi * 1.75
        rr = curl * (1 - i / 16 * 0.45)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    solid(cv, chain(pts, 1.25), "B", None)


def sitting_body(cv, cx, top, scratch=0, leg_twitch=0):
    """Badan duduk tampak depan: perut krem, paha, telapak kaki."""
    torso = ellipse(cx, top + 6.5, 8.2, 7.2)
    solid(cv, torso, "B", "b")
    cv.fill({p for p in ellipse(cx, top + 7.5, 5.0, 5.2) if p not in edge(torso)}, "F")
    cv.fill({(x, y) for (x, y) in ellipse(cx, top + 7.5, 5.0, 5.2) if (x, y + 1) not in ellipse(cx, top + 7.5, 5.0, 5.2)}, "f")
    for s in (-1, 1):
        lift = leg_twitch if s == 1 else 0
        thigh = ellipse(cx + s * 5.2, top + 12.2 - lift, 4.2, 2.8)
        solid(cv, thigh, "B", "b")
        foot = ellipse(cx + s * 3.0, top + 14.2 - lift, 2.6, 1.5)
        solid(cv, foot, "F", "f", shade_off=(1, 1))


# ------------------------------------------------------------------ properti
def banana(cv, hx, hy, bites=0, peel=0):
    """Pisang melengkung dipegang di (hx, hy), ujung atas dekat mulut. bites: 0..3."""
    length = [12, 9, 7, 4][min(bites, 3)]
    pts = [(hx + 2.2 * math.sin(i / 12 * math.pi * 0.8), hy - i) for i in range(length + 1)]
    top_y = hy - length
    if bites:
        solid(cv, chain(pts, 1.9), "Y", "y", shade_off=(1, 1))
        cv.fill({p for p in chain(pts[-3:], 1.2)}, "n")  # daging buah di bekas gigitan
        for s in (-1, 1):  # kulit terkulai ke bawah
            flap = chain([(pts[-3][0] + s * 1.5, top_y + 2), (pts[-3][0] + s * 3.6, top_y + 4 + peel), (pts[-3][0] + s * 4.2, top_y + 7 + peel)], 0.9)
            solid(cv, flap, "Y", None)
    else:
        solid(cv, chain(pts, 1.9), "Y", "y", shade_off=(1, 1))
        tx, ty = pts[-1]
        cv.fill(rect(int(tx) - 1, int(ty) - 2, 2, 2), "N")
    cv.fill(rect(int(hx) - 1, int(hy) + 2, 2, 1), "N")


def laptop(cv, x, y, shake=0, glow=None):
    """Laptop dilihat dari belakang layar (seperti gambar asli)."""
    x += shake
    lid = rect(x, y, 20, 13)
    lid -= {(x, y), (x + 19, y)}
    solid(cv, lid, "L", None, outline="K")
    cv.fill(rect(x + 1, y + 1, 18, 1), "l")
    for (dx, dy) in ((10, 5), (11, 5), (9, 6), (12, 6), (10, 7), (11, 7)):
        cv.put(x + dx, y + dy, "G")
    base = rect(x - 4, y + 13, 24, 2)
    solid(cv, base, "l", None, outline="K")
    if glow:  # cahaya layar merah memantul di tepi atas tutup
        cv.fill(rect(x + 1, y + 1, 18, 1), glow)


def mug(cv, x, y, lift=0, steam=0):
    y -= lift
    body = rect(x, y, 7, 7)
    solid(cv, body, "C", "c", shade_off=(1, 1))
    cv.fill(rect(x + 1, y + 1, 5, 1), "D")
    handle = {(x - 2, y + 2), (x - 2, y + 3), (x - 2, y + 4), (x - 1, y + 2), (x - 1, y + 4)}
    cv.fill(handle, "K")
    for i, (dx, dy) in enumerate(((2, -3), (4, -5), (2, -7), (4, -9))):
        if (i + steam) % 2 == 0:
            cv.put(x + dx, y + dy, "S")
            cv.put(x + dx + 1, y + dy, "S")


# font simbol 5x5 untuk umpatan dan tanda
MINI = {
    "#": ["01010", "11111", "01010", "11111", "01010"], "@": ["01110", "10001", "10111", "10110", "01111"],
    "!": ["00100", "00100", "00100", "00000", "00100"], "%": ["11001", "11010", "00100", "01011", "10011"],
    "$": ["01111", "10100", "01110", "00101", "11110"], "*": ["10101", "01110", "11111", "01110", "10101"],
    "?": ["01110", "10001", "00110", "00000", "00100"], "&": ["01100", "10010", "01101", "10010", "01101"],
    "E": ["11111", "10000", "11110", "10000", "11111"], "=": ["00000", "11111", "00000", "11111", "00000"],
    "m": ["00000", "11010", "10101", "10101", "10101"], "c": ["00000", "01111", "10000", "10000", "01111"],
    ".": ["00000", "00000", "00000", "00000", "00100"], "v": ["00001", "00010", "10100", "01000", "00000"],
    "n": ["00110", "00101", "00100", "11100", "11100"],  # not musik
    "O": ["01110", "10001", "10001", "10001", "01110"], "K": ["10010", "10100", "11000", "10100", "10010"],
}


def mini_text(cv, s, x, y, c):
    for i, ch in enumerate(s):
        for ry, row in enumerate(MINI[ch]):
            for rx, v in enumerate(row):
                if v == "1":
                    cv.put(x + i * 6 + rx, y + ry, c)


def bubble(cv, x, y, w, h, fill="W", tail_dir=1):
    box = rect(x, y, w, h) - {(x, y), (x + w - 1, y), (x, y + h - 1), (x + w - 1, y + h - 1)}
    solid(cv, box, fill, None)
    tx = x + (3 if tail_dir < 0 else w - 4)
    cv.fill({(tx, y + h), (tx + 1, y + h), (tx + (1 if tail_dir > 0 else 0), y + h + 1)}, fill)
    cv.fill({(tx - 1, y + h), (tx + 2, y + h), (tx + (0 if tail_dir > 0 else 1) + (1 if tail_dir > 0 else -1) * 0, y + h + 2)}, "K")


def puff(cv, x, y, size):
    solid(cv, ellipse(x, y, size, size * 0.85), "S", None, outline="s")


def spark_lines(cv, x, y, c="K"):
    cv.fill({(x, y), (x + 1, y + 1), (x, y + 3), (x + 1, y + 4)}, c)
