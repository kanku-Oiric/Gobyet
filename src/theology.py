"""Kostum teologi Gobyet (Fase 2, Gerbang I): Pak Haji dan Priest. Aturan brief 7.2 berlaku penuh.

- Wajah Gobyet terlihat penuh. Tanpa janggut putih panjang dan tanpa mahkota daun (K8).
- Pak Haji: kopiah putih polos, baju koko putih, sarung motif kotak dua hijau PAL (V/v), tasbih kayu.
  Tanpa peci hitam dan tanpa batik (K7: itu milik kondangan).
- Priest: jubah panjang abu (g, bayangan 5; bukan hitam Judge), kerah putih, buku polos tanpa tulisan
  atau tanda apa pun, kalung salib polos kecil 3x4 berwarna emas tua (y) dengan tali cokelat.
  Warna y hanya dipakai salib ini di kedua kostum (dipakai pemeriksaan otomatis iv).
- Tidak ada gestur ritual atau ibadah: tangan tidak ditengadahkan, tidak dilipat di depan dada, kepala
  tidak menunduk. Tasbih hanya digeser, buku hanya dipegang (tidak dibuka, tidak dibaca).
- Tidak menari, tidak melompat, tidak slapstick.
- Perlakuan identik (7.2e): kedua kostum memakai tabel state, jumlah frame, durasi, ritme angguk,
  ekspresi, dan aura yang sama. Yang berbeda hanya pakaian dan prop.
- Aura (7.2f): glow lembut berlapis (dithering) di belakang badan, warna C, n, O, digambar paling awal
  sehingga selalu di belakang. Pusatnya di badan dan tepi atasnya di bawah puncak kepala: bukan halo,
  tanpa sinar, tanpa nyala.
- Menang atau kalah tidak berarti benar atau salah secara teologis (7.2h; lihat pack/README.md).
"""
import math

from monkey import Canvas, head, arm, tail, rect, ellipse, capsule, solid
from costumes import CX, CY, TOP, dressed_body, inner
from domains import thought_dots

COSTUMES = ("pak-haji", "priest")

# ================================================================== tabel bersama (7.2e)
# state: (jumlah frame, durasi ms per frame). Dipakai kedua kostum tanpa pengecualian.
STATES = {
    "idle": (16, 180),
    "thinking": (12, 170),
    "happy": (12, 150),
    "victory": (16, 160),
    "defeated": (16, 200),
}
NOD = (0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0)  # angguk pelan 1 px, sama untuk keduanya


def wag(t, n):
    return t * math.tau / n


# ================================================================== aura (identik untuk keduanya)
AURA_CENTER = (CX, TOP + 7)
AURA_R = (19.0, 13.0)
AURA_COLORS = ("C", "n", "O")


def aura_mask(level=1, pulse=0, shimmer=0):
    """{(x, y): warna} aura. level -1 = paling redup (hanya lapisan dalam, hampir seluruhnya tertutup badan),
    0 = redup, 1 = biasa, 2 = sedikit lebih terang (happy), 3 = terang (victory).
    pulse -1..1 menggeser tepi 1 px (berdenyut). shimmer menggeser pola titik O di lapisan tengah (victory).
    Hanya fungsi dari (level, pulse, shimmer), jadi kedua kostum dengan argumen yang sama mendapat mask sama."""
    cx, cy = AURA_CENTER
    rx, ry = AURA_R[0] + pulse, AURA_R[1] + pulse
    out = {}
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            d = math.hypot((x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry)
            if d > 1.0:
                continue
            quarter = x % 2 == 0 and y % 2 == 0
            half = (x + y) % 2 == 0
            spark = (x + 2 * y + shimmer) % 6 == 0 and half
            if level < 0 and d > 0.6:
                continue
            if d > 0.8:  # lapisan luar: paling tipis
                if level == 3 and half or level in (1, 2) and quarter:
                    out[(x, y)] = "C"
            elif d > 0.6:  # lapisan tengah
                if level == 0:
                    if quarter:
                        out[(x, y)] = "C"
                elif half:
                    out[(x, y)] = "O" if (level >= 2 and spark) else "n"
            else:  # lapisan dalam (sebagian besar tertutup badan)
                if level <= 0:
                    if quarter:
                        out[(x, y)] = "C"
                elif half or level == 3:
                    out[(x, y)] = "O" if (level >= 2 and spark) else "n"
    return out


def aura(cv, level=1, pulse=0, shimmer=0):
    """Gambar aura di kanvas yang masih kosong (paling belakang). Mengembalikan mask yang digambar."""
    m = aura_mask(level, pulse, shimmer)
    for p, c in m.items():
        cv.put(p[0], p[1], c)
    return m


def aura_params(state, t):
    """(level, pulse, shimmer) per state dan frame. Satu fungsi untuk kedua kostum."""
    breathe = (0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, -1, -1, -1, 0, 0)[t % 16]
    if state == "idle":
        return 1, breathe, 0
    if state == "thinking":
        return 1, 0, 0
    if state == "happy":
        return 2, (0, 0, 1, 1, 1, 0, 0, 0, -1, -1, -1, 0)[t % 12], t // 3
    if state == "victory":
        return 3, breathe, t // 2
    if state == "defeated":  # meredup sesaat lalu kembali (7.2g): 1 -> 0 -> paling redup -> 0 -> 1
        return (-1 if 6 <= t <= 9 else (0 if 4 <= t <= 11 else 1)), 0, 0
    raise KeyError(state)


# ================================================================== pakaian dan prop
def kopiah(cv, cx, cy):
    """Kopiah putih haji: topi bundar polos yang pas di puncak kepala. Tanpa motif, tanpa tulisan."""
    cap = {p for p in ellipse(cx, cy - 3.0, 9.6, 6.6) if p[1] <= cy - 5}
    solid(cv, cap, "W", "h", shade_off=(1, 1))


def koko_sarung(cv, cx, top, bob=0):
    """Baju koko putih (S) dengan kerah pendek dan kancing, sarung kotak dua hijau (V/v) dari pinggang ke kaki.
    Sarung dibuat lebih luas daripada koko supaya hijau menjadi warna dominan (alokasi global)."""
    t = top + bob
    torso = dressed_body(cv, cx, t, "S", "h", pants="V", pants_shade="v")
    body = inner(torso)
    cv.fill({(cx - 1, t), (cx, t), (cx - 2, t + 1), (cx + 1, t + 1)}, "h")  # kerah pendek
    cv.fill({(cx - 1, y) for y in range(t + 2, t + 4)}, "h")  # belahan kancing
    cv.fill({(cx - 1, t + 2)}, "c")
    wrap = {(x, y) for (x, y) in body if y >= t + 4}
    legs = {(x, y) for (x, y), c in cv.px.items() if c in ("V", "v") and y >= t + 8}
    sarung = wrap | legs
    # motif kotak: dasar hijau V dengan garis hijau tua v tiap 5 piksel (kotak-kotak dua warna PAL)
    cv.fill(sarung, "V")
    cv.fill({(x, y) for (x, y) in sarung if (x - cx) % 5 == 2 or (y - t) % 5 == 1}, "v")
    return torso


BEADS = 9


def tasbih(cv, hx, hy, slide=0.0):
    """Tasbih kayu: untaian butir cokelat yang menjuntai dari jari di (hx, hy). slide 0..1 = butir sedang digeser."""
    cx, cy, rx, ry = hx, hy + 4, 2.6, 3.4
    for k in range(BEADS):
        a = -math.pi / 2 + (k + 0.5 + slide) * math.tau / BEADS
        bx, by = int(round(cx + rx * math.cos(a))), int(round(cy + ry * math.sin(a)))
        if by <= hy:  # butir yang berada di balik jari tidak terlihat
            continue
        cv.fill({(bx, by), (bx + 1, by), (bx, by + 1), (bx + 1, by + 1)}, "N")
        cv.put(bx, by, "X")


def cassock(cv, cx, top, bob=0):
    """Jubah panjang abu (g, bayangan 5) sampai menutupi kaki; kerah putih di leher."""
    t = top + bob
    robe = set()
    for y in range(t - 1, t + 16):
        half = 7.5 + max(0.0, (y - t) / 15.0) * 3.5
        robe |= {(x, y) for x in range(int(round(cx - half)), int(round(cx + half)) + 1)}
    shoulders = ellipse(cx, t + 5, 10.0, 6.5)
    robe = {p for p in robe if p[1] >= t + 4 or p in shoulders}
    solid(cv, robe, "g", "5")
    for s in (-1, 1):
        solid(cv, ellipse(cx + s * 3.0, t + 15.6, 2.6, 1.4), "F", "f", shade_off=(1, 1))
    cv.fill({(x, y) for x in range(cx - 3, cx + 3) for y in (t, t + 1) if (x, y) in inner(robe)}, "W")  # kerah putih
    return robe


def cross_necklace(cv, cx, top, bob=0):
    """Kalung salib polos kecil 3x4 (warna y) bertali cokelat, tergantung di dada di bawah kerah."""
    t = top + bob
    cv.fill({(cx - 3, t + 2), (cx - 2, t + 2), (cx + 1, t + 2), (cx + 2, t + 2)}, "N")  # tali
    y0 = t + 3
    cv.fill({(cx - 1, y0), (cx - 2, y0 + 1), (cx - 1, y0 + 1), (cx, y0 + 1), (cx - 1, y0 + 2), (cx - 1, y0 + 3)}, "y")


def plain_book(cv, x, y):
    """Buku polos tertutup 9x7: sampul cokelat tua tanpa tulisan atau tanda, tepi halaman krem."""
    solid(cv, rect(x, y, 9, 7), "D", None)
    cv.fill({(x + 7, yy) for yy in range(y + 1, y + 6)}, "C")


# ================================================================== kerangka frame bersama
def dressed(cv, costume, t, bob):
    tail(cv, (CX - 7, TOP + 14 + bob), phase=wag(t, 16), flip=-1, length=8)
    if costume == "pak-haji":
        koko_sarung(cv, CX, TOP, bob=bob)
    else:
        cassock(cv, CX, TOP, bob=bob)
        cross_necklace(cv, CX, TOP, bob=bob)


def face(cv, costume, bob, eyes, brows, mouth):
    head(cv, CX, CY + bob, eyes=eyes, brows=brows, mouth=mouth)
    if costume == "pak-haji":
        kopiah(cv, CX, CY + bob)


SLEEVE = {"pak-haji": "S", "priest": "g"}


def hold_prop(cv, costume, t, bob, slide=0.0):
    """Pose tangan baku: Pak Haji memegang tasbih di tangan kanan (tangan kiri di pangkuan);
    Priest memegang buku tertutup di pangkuan dengan dua tangan."""
    s = SLEEVE[costume]
    if costume == "pak-haji":
        arm(cv, (CX - 7, TOP + 3 + bob), (CX - 6, TOP + 10 + bob), elbow=(CX - 11, TOP + 7 + bob), fur=s)
        hand = (CX + 5, TOP + 3 + bob)  # di depan dada, untaian menjuntai di atas koko putih supaya terbaca
        tasbih(cv, hand[0], hand[1], slide)
        arm(cv, (CX + 7, TOP + 3 + bob), hand, elbow=(CX + 12, TOP + 7 + bob), fur=s)
    else:
        plain_book(cv, CX - 4, TOP + 7 + bob)
        arm(cv, (CX - 7, TOP + 3 + bob), (CX - 5, TOP + 10 + bob), elbow=(CX - 11, TOP + 7 + bob), fur=s)
        arm(cv, (CX + 7, TOP + 3 + bob), (CX + 5, TOP + 10 + bob), elbow=(CX + 11, TOP + 7 + bob), fur=s)


def slide_at(t):
    """Butir tasbih bergeser satu per beat (tiap 4 frame): setengah jalan di frame kedua beat."""
    return 0.5 if t % 4 == 1 else 0.0


def idle_frame(costume, i):
    """Pak Haji menggeser butir tasbih pelan dan mengangguk; Priest memegang buku dan mengangguk pelan;
    aura berdenyut lembut. Kedip di f10."""
    cv = Canvas()
    t = i % 16
    aura(cv, *aura_params("idle", t))
    dressed(cv, costume, t, 0)
    hold_prop(cv, costume, t, 0, slide_at(t))
    face(cv, costume, NOD[t], "blink" if t == 10 else "look", "flat", "smile")  # hanya kepala yang mengangguk
    return cv


def thinking_frame(costume, i):
    """Tangan kiri di dagu, prop tetap di tangan kanan (Pak Haji) atau di pangkuan (Priest); gelembung "..."."""
    cv = Canvas()
    t = i % 12
    aura(cv, *aura_params("thinking", t))
    dressed(cv, costume, t, 0)
    face(cv, costume, 0, "blink" if t == 7 else "side", "flat", "flat")
    s = SLEEVE[costume]
    if costume == "pak-haji":
        hand = (CX + 5, TOP + 3)
        tasbih(cv, hand[0], hand[1], 0.0)
        arm(cv, (CX + 7, TOP + 3), hand, elbow=(CX + 12, TOP + 7), fur=s)
    else:
        plain_book(cv, CX - 1, TOP + 7)
        arm(cv, (CX + 7, TOP + 3), (CX + 7, TOP + 10), elbow=(CX + 11, TOP + 7), fur=s)
    arm(cv, (CX - 7, TOP + 3), (CX - 3, CY + 9), elbow=(CX - 11, TOP + 7), fur=s)  # tangan di dagu
    if 2 <= t <= 10:
        thought_dots(cv, CX + 12, 1, 1 + min(2, (t - 2) // 2))
    return cv


def happy_frame(costume, i):
    """Senyum kecil dengan mata tersenyum, aura sedikit lebih terang; angguk kecil."""
    cv = Canvas()
    t = i % 12
    aura(cv, *aura_params("happy", t))
    dressed(cv, costume, t, 0)
    hold_prop(cv, costume, t, 0, slide_at(t))
    face(cv, costume, 1 if t in (5, 6) else 0, "happy" if 2 <= t <= 9 else "look", "flat", "smile")
    return cv


def victory_frame(costume, i):
    """Senyum tenang, aura paling terang dengan kilau emas yang bergeser pelan. Tanpa konfeti, tanpa lompat.
    Elemen khas: aura menguat (sama untuk keduanya karena 7.2e)."""
    cv = Canvas()
    t = i % 16
    aura(cv, *aura_params("victory", t))
    dressed(cv, costume, t, 0)
    face(cv, costume, 0, "happy" if 3 <= t <= 12 else "look", "flat", "smile")
    hold_prop(cv, costume, t, 0, slide_at(t))
    return cv


def defeated_frame(costume, i):
    """Tenang menerima (7.2g): badan tetap tegak, senyum tipis, mata setengah terpejam, tangan diam di
    pangkuan dengan siku rapat ke badan; aura meredup di f4-f11 (paling redup f6-f9) lalu kembali."""
    cv = Canvas()
    t = i % 16
    aura(cv, *aura_params("defeated", t))
    dressed(cv, costume, t, 0)
    face(cv, costume, 0, "blink" if t == 14 else "relief", "flat", "smile")
    s = SLEEVE[costume]
    if costume == "pak-haji":  # tasbih diam (tidak digeser) di tangan kanan, tangan kiri di pangkuan
        arm(cv, (CX - 7, TOP + 3), (CX - 4, TOP + 11), elbow=(CX - 9, TOP + 8), fur=s)
        tasbih(cv, CX + 4, TOP + 5, 0.0)
        arm(cv, (CX + 7, TOP + 3), (CX + 4, TOP + 5), elbow=(CX + 9, TOP + 8), fur=s)
    else:  # buku tertutup diam di pangkuan
        plain_book(cv, CX - 4, TOP + 8)
        arm(cv, (CX - 7, TOP + 3), (CX - 4, TOP + 11), elbow=(CX - 9, TOP + 8), fur=s)
        arm(cv, (CX + 7, TOP + 3), (CX + 4, TOP + 11), elbow=(CX + 9, TOP + 8), fur=s)
    return cv


FRAMES = {"idle": idle_frame, "thinking": thinking_frame, "happy": happy_frame, "victory": victory_frame,
          "defeated": defeated_frame}


def _scene(costume, state):
    n, ms = STATES[state]
    fn = FRAMES[state]
    return (lambda i: fn(costume, i)), n, (lambda i: ms)


# Urutan kerja Gerbang I (keputusan pemilik 11): idle kedua kostum dulu, pemeriksaan otomatis (i)-(vi),
# baru state lain. BUILD_STATES semula ("idle",); diperluas ke semua state setelah pemeriksaan idle lulus
# (bukti di pack/reports/gate-I.md).
BUILD_STATES = ("idle", "thinking", "happy", "victory", "defeated")

PROPS = {
    "pak-haji: kopiah putih": lambda cv: kopiah(cv, 32, 24),
    "pak-haji: tasbih": lambda cv: tasbih(cv, 30, 16),
    "priest: buku polos": lambda cv: plain_book(cv, 28, 20),
    "priest: kalung salib": lambda cv: cross_necklace(cv, 32, 20),
}

SCENES = {"%s-%s" % (c, s): _scene(c, s) for c in ("pak-haji", "priest") for s in BUILD_STATES}
