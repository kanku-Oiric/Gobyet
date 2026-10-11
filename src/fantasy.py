"""Kostum fantasi Gobyet (Fase 2): Knight, Viking, Pirate, Wizard (Gerbang H) dan 12 varian kelas (Gerbang J).

Semua memakai rig yang sama (kepala, badan duduk, lengan) dengan wajah Gobyet terlihat penuh: helm terbuka,
topi tidak menutupi wajah, kecuali beat defeated yang diminta brief (topi merosot menutupi mata).

Pedoman senjata (brief 7.1): gaya kartun, tanpa darah, luka, proyektil melayang, kilatan tembakan, atau asap
laras. attack adalah metafora: prop dihentak atau ditancapkan ke lantai, balok kayu, papan kayu, atau papan
sasaran. Tidak ada senjata yang diarahkan ke karakter lain.

Warna dominan (alokasi global, pack/STYLE.md): Knight tabard merah tua z/1, Viking rompi kulit D,
Pirate mantel marun i/2, Wizard jubah biru kerajaan 3/4.
"""
import math

from monkey import (Canvas, head, arm, tail, sitting_body, mini_text, bubble, puff, spark_lines, ellipse, capsule,
                    chain, rect, edge, solid)
from costumes import CX, CY, TOP, dressed_body, inner, confetti
from roles import dots_or_mark
from domains import thought_dots, sigh


# ================================================================== prop bersama
def wag(t, n):
    """Fase ekor periodik: satu putaran penuh per n frame, jadi frame terakhir menyambung mulus ke frame 0."""
    return t * math.tau / n


def dust(cv, x, y, k=0):
    """Debu piksel kecil di lantai saat benda dihentak (k = 0..2 menyebar)."""
    for dx, dy in ((-3 - k, 0), (-2 - k, -1), (3 + k, 0), (2 + k, -1), (-1, -2 - k // 2), (1, -2 - k // 2)):
        cv.put(x + dx, y + dy, "s")


def sword(cv, hx, hy, deg, length=11, blade="G", glint=None):
    """Pedang: gagang di (hx, hy), bilah sepanjang `length` ke arah deg (0 = kanan, 90 = atas).
    glint = 0..1 posisi kilau di sepanjang bilah."""
    a = math.radians(deg)
    ux, uy = math.cos(a), -math.sin(a)
    tip = (hx + ux * length, hy + uy * length)
    cv.fill(capsule((hx + ux * 2, hy + uy * 2), tip, 1.0), "s")  # tepi bilah abu supaya kontras dengan latar krem
    cv.fill(capsule((hx + ux * 2, hy + uy * 2), tip, 0.5), blade)
    cv.put(int(round(tip[0])), int(round(tip[1])), "W")
    px, py = -uy, ux  # pelindung tangan tegak lurus bilah
    cv.fill(capsule((hx + ux * 2 - px * 2, hy + uy * 2 - py * 2), (hx + ux * 2 + px * 2, hy + uy * 2 + py * 2), 0.6), "y")
    cv.fill(capsule((hx - ux * 1, hy - uy * 1), (hx + ux * 1, hy + uy * 1), 0.6), "N")
    if glint is not None:
        gx, gy = hx + ux * (3 + glint * (length - 4)), hy + uy * (3 + glint * (length - 4))
        cv.fill({(int(gx), int(gy)), (int(gx) + 1, int(gy)), (int(gx) - 1, int(gy)), (int(gx), int(gy) - 1), (int(gx), int(gy) + 1)}, "W")


def pennant(cv, x, y, flap=0):
    """Panji emas kecil 8x5 yang menempel di bilah pada (x, y), ujungnya berkibar naik-turun (flap -1..1)."""
    tip = y + 2 + flap
    m = set()
    for k in range(8):
        f = k / 7.0
        top, bot = y + f * (tip - y), y + 4 + f * (tip - y - 4)
        m |= {(x + k, yy) for yy in range(int(round(top)), int(round(bot)) + 1)}
    solid(cv, m, "O", "y", shade_off=(1, 1))


def kite_shield(cv, x, y, color="z", shade="1", emblem="O"):
    """Perisai kecil 9x11 (bentuk layang-layang) berwarna tabard dengan pita emas mendatar (bukan simbol agama).
    Pita dipilih karena tetap terbaca walau separuh perisai tertutup lengan (chevron terbaca seperti petir)."""
    m = set()
    for dy in range(11):
        half = 4 if dy < 6 else max(0, 4 - (dy - 5))
        m |= {(x + 4 + dx, y + dy) for dx in range(-half, half + 1)}
    solid(cv, m, color, shade, shade_off=(1, 1))
    cv.fill({(xx, yy) for (xx, yy) in inner(m) if yy in (y + 4, y + 5)}, emblem)


def open_helmet(cv, cx, cy, tilt=0):
    """Helm baja terbuka: kubah di atas kepala sampai alis, pelindung pipi pendek; wajah tetap terlihat."""
    dome = {p for p in ellipse(cx + tilt, cy - 2.5, 10.2, 7.6) if p[1] <= cy - 3}
    solid(cv, dome, "G", "s", shade_off=(1, 1))
    cv.fill({(x, int(cy) - 3) for x in range(int(cx + tilt) - 9, int(cx + tilt) + 10)}, "s")
    cv.fill(rect(int(cx + tilt) - 1, int(cy) - 9, 2, 3), "W")  # kilau di kubah


def tabard_body(cv, cx, top, bob=0):
    """Zirah baja di bahu dan kaki, tabard merah tua (z) menutupi seluruh dada sampai pangkuan.
    Tabard dibuat selebar badan supaya merah tua menjadi warna dominan (alokasi global), bukan baja."""
    torso = dressed_body(cv, cx, top + bob, "G", "s", pants="s", pants_shade="g")
    tab = {(x, y) for (x, y) in inner(torso) if y >= top + bob + 2} | rect(cx - 4, top + bob + 10, 9, 4)
    solid(cv, tab, "z", "1", shade_off=(1, 1))
    cv.fill({(cx - 1, top + bob + 4), (cx, top + bob + 4), (cx - 1, top + bob + 5), (cx, top + bob + 5)}, "O")  # gesper emas
    return torso


def horned_helmet(cv, cx, cy, dx=0):
    """Helm Viking: kubah abu, pinggiran cokelat, tanduk kecil krem melengkung ke atas (gaya kartun)."""
    x = cx + dx
    dome = {p for p in ellipse(x, cy - 2.5, 10.0, 7.4) if p[1] <= cy - 3}
    solid(cv, dome, "s", "g", shade_off=(1, 1))
    band = {(xx, yy) for (xx, yy) in dome if yy in (int(cy) - 4, int(cy) - 5) and (xx, yy) in inner(dome)}
    cv.fill({(xx, int(cy) - 3) for xx in range(int(x) - 9, int(x) + 10)}, "N")
    cv.fill(band, "D")  # pita kulit di pangkal helm, bahan yang sama dengan rompi
    for s in (-1, 1):
        horn = capsule((x + s * 8, cy - 5), (x + s * 11, cy - 8), 1.7) | capsule((x + s * 11, cy - 8), (x + s * 12, cy - 12), 1.1)
        solid(cv, horn, "C", "c", shade_off=(1, 1))


def round_shield(cv, x, y, r=6.0):
    """Perisai bundar kayu bercat: papan cokelat, dua lajur cat merah, bos logam di tengah."""
    disc = ellipse(x, y, r, r)
    solid(cv, disc, "X", "x", shade_off=(1, 1))
    body = inner(disc)
    cv.fill({(xx, yy) for (xx, yy) in body if abs((xx - x) - (yy - y)) <= 1}, "R")
    cv.fill(ellipse(x, y, 1.6, 1.6), "s")


def axe(cv, hx, hy, deg, length=10, big=False):
    """Kapak: gagang kayu dari tangan (hx, hy) ke arah deg, mata kapak abu di ujung."""
    a = math.radians(deg)
    ux, uy = math.cos(a), -math.sin(a)
    tip = (hx + ux * length, hy + uy * length)
    cv.fill(capsule((hx - ux, hy - uy), tip, 0.8), "N")
    px, py = -uy, ux
    r = 3.0 if big else 2.4
    blade = ellipse(tip[0] + px * 2.2, tip[1] + py * 2.2, r, r + 0.6)
    solid(cv, blade, "G", "s", shade_off=(1, 1))


def vest_body(cv, cx, top, bob=0):
    """Rompi kulit cokelat tua (D) tertutup, belahan leher V kecil berbulu, sabuk dengan gesper."""
    torso = dressed_body(cv, cx, top + bob, "D", "K", pants="x", pants_shade="e")
    cv.fill({(x, y) for (x, y) in inner(torso) if y <= top + bob + 3 and abs(x - cx + 0.5) <= 3.5 - (y - top - bob)}, "B")
    cv.fill({(x, top + bob + 9) for x in range(cx - 7, cx + 8) if (x, top + bob + 9) in inner(torso)}, "N")
    cv.fill(rect(cx - 1, top + bob + 9, 2, 1), "O")
    return torso


def log_block(cv, x, y):
    """Balok kayu di lantai (sasaran hentakan)."""
    solid(cv, rect(x, y, 12, 5), "X", "x", shade_off=(1, 1))
    cv.fill(ellipse(x + 1.5, y + 2.5, 1.2, 1.8), "C")
    cv.put(x + 1, y + 2, "c")


def tricorn(cv, cx, cy, dy=0, tip=0):
    """Topi tricorn hitam bertepi emas. tip = merosot ke depan (0..3) sampai menutupi mata saat defeated."""
    y = int(cy - 8 + dy + tip)
    crown = {p for p in ellipse(cx, y, 6.5, 4.0) if p[1] <= y + 1}
    brim = set()
    for x in range(cx - 12, cx + 13):
        rise = abs(x - cx) // 5
        brim |= {(x, y + 2 - rise), (x, y + 3 - rise)}
    solid(cv, crown | brim, "L", "q", shade_off=(1, 1))
    cv.fill({(x, y + 3 - abs(x - cx) // 5) for x in range(cx - 11, cx + 12)}, "O")


def coat_body(cv, cx, top, bob=0):
    """Mantel marun (PAL_EXT i/2) berkerah lebar, kemeja krem di leher, sabuk hitam."""
    torso = dressed_body(cv, cx, top + bob, "i", "2", pants="L", pants_shade="q")
    cv.fill({(cx - 1, top + bob), (cx, top + bob), (cx - 1, top + bob + 1), (cx, top + bob + 1), (cx - 2, top + bob),
             (cx + 1, top + bob)}, "C")
    cv.fill({(x, top + bob + 8) for x in range(cx - 8, cx + 9) if (x, top + bob + 8) in inner(torso)}, "L")
    cv.fill(rect(cx - 1, top + bob + 8, 2, 1), "O")
    for y in (top + bob + 3, top + bob + 6):
        cv.put(cx + 3, y, "O")
    return torso


def cutlass(cv, hx, hy, deg, length=10):
    """Pedang lengkung (cutlass): bilah melengkung, pelindung tangan bulat emas."""
    a = math.radians(deg)
    pts = []
    for k in range(length + 1):
        t = k / float(length)
        bend = math.radians(deg - 25 * t)
        pts.append((hx + math.cos(a) * 2 + math.cos(bend) * k * 0.95, hy - math.sin(a) * 2 - math.sin(bend) * k * 0.95))
    cv.fill(chain(pts, 1.0), "s")
    cv.fill(chain(pts, 0.5), "G")
    cv.put(int(round(pts[-1][0])), int(round(pts[-1][1])), "W")
    solid(cv, ellipse(hx + math.cos(a) * 1.5, hy - math.sin(a) * 1.5, 1.8, 1.8), "y", None)
    cv.fill(capsule((hx - math.cos(a), hy + math.sin(a)), (hx, hy), 0.6), "N")


def telescope(cv, x, y, deg=0, length=9):
    """Teropong kuningan: tiga ruas makin kecil ke ujung."""
    a = math.radians(deg)
    ux, uy = math.cos(a), -math.sin(a)
    for k, (r, c) in enumerate(((1.6, "y"), (1.3, "O"), (1.0, "y"))):
        s0, s1 = k * length / 3.0, (k + 1) * length / 3.0
        solid(cv, capsule((x + ux * s0, y + uy * s0), (x + ux * s1, y + uy * s1), r), c, None)


def plank(cv, x, y):
    """Papan kayu di lantai (sasaran cutlass)."""
    solid(cv, rect(x, y, 13, 4), "X", "x", shade_off=(1, 1))
    for k in (4, 8):
        cv.put(x + k, y + 1, "x")


def treasure_chest(cv, x, y):
    """Peti kayu berbingkai emas (tempat duduk Pirate saat defeated)."""
    solid(cv, rect(x, y, 20, 8), "X", "x", shade_off=(1, 1))
    cv.fill({(x + 1, yy) for yy in range(y + 1, y + 7)} | {(x + 18, yy) for yy in range(y + 1, y + 7)}, "O")
    cv.fill(rect(x + 9, y + 2, 2, 3), "O")


def coin(cv, x, y):
    """Koin emas 4x4 bergaris tepi K (cukup besar untuk terbaca di skala 1x)."""
    solid(cv, {(x + dx, y + dy) for dx in range(4) for dy in range(4)} - {(x, y), (x + 3, y), (x, y + 3), (x + 3, y + 3)},
          "O", "y", shade_off=(1, 1))


def robe_body(cv, cx, top, bob=0):
    """Jubah biru kerajaan (PAL_EXT 3/4) panjang menutupi kaki, lengan lebar, sabuk tali emas."""
    robe = set()
    for y in range(top + bob - 1, top + bob + 16):
        half = 7.5 + max(0.0, (y - top - bob) / 15.0) * 5.0
        robe |= {(x, y) for x in range(int(round(cx - half)), int(round(cx + half)) + 1)}
    shoulders = ellipse(cx, top + bob + 5, 10.0, 6.5)
    robe = {p for p in robe if p[1] >= top + bob + 4 or p in shoulders}
    solid(cv, robe, "3", "4")
    cv.fill({(x, top + bob + 8) for x in range(cx - 7, cx + 8) if (x, top + bob + 8) in inner(robe)}, "O")
    for s in (-1, 1):
        solid(cv, ellipse(cx + s * 3.0, top + bob + 15.6, 2.6, 1.4), "F", "f", shade_off=(1, 1))
    return robe


def star(cv, x, y, c="Y"):
    cv.fill({(x, y), (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)}, c)


def wizard_hat(cv, cx, cy, lift=0, twinkle=0, droop=0):
    """Topi runcing biru kerajaan dengan pinggiran lebar dan bintang; ujungnya melengkung ke kanan supaya
    muat di kanvas. droop = topi merosot ke bawah (menutupi mata saat defeated)."""
    y = int(cy - 8 - lift + droop)
    brim = {(x, yy) for x in range(cx - 12, cx + 13) for yy in (y + 1, y + 2)} - {(cx - 12, y + 1), (cx + 12, y + 1)}
    cone = set()
    for k in range(0, 10):
        half = 6.5 - k * 0.62
        bend = (k / 9.0) ** 2 * 5
        cone |= {(int(round(cx + bend + dx)), y - k) for dx in [d * 0.5 for d in range(int(-half * 2), int(half * 2) + 1)]}
    solid(cv, cone | brim, "3", "4", shade_off=(1, 1))
    cv.fill({(x, y) for x in range(cx - 6, cx + 7)}, "O")  # pita emas
    star(cv, cx - 2, y - 3, "Y" if twinkle % 2 == 0 else "O")
    cv.put(cx + 3, y - 6, "Y" if twinkle % 2 else "W")


def staff(cv, x, y, glow=0, length=22):
    """Tongkat kayu tegak dari (x, y) ke atas, kristal di ujung yang bersinar redup (glow 0..2)."""
    cv.fill(capsule((x, y), (x, y - length), 0.7), "N")
    top = (x, y - length - 2)
    solid(cv, ellipse(top[0], top[1], 1.8, 2.3), "I" if glow < 2 else "W", None, outline="4")
    if glow:
        for dx, dy in ((-3, 0), (3, 0), (0, -4)):
            cv.put(top[0] + dx, top[1] + dy, "I")


def spellbook(cv, x, y, page=0):
    """Buku mantra terbuka 13x7: sampul merah tua, halaman krem, garis tulisan; page 0-2 = halaman dibalik."""
    solid(cv, rect(x, y, 13, 7), "z", "1", shade_off=(1, 1))
    for hx in (x + 1, x + 7):
        cv.fill(rect(hx, y + 1, 5, 5), "C")
        for k in range(2):
            cv.fill(rect(hx + 1, y + 2 + k * 2, 3, 1), "c")
    if page:
        px = x + 7 - 2 * page
        cv.fill(rect(px, y - 2, 2, 6), "C")


# ================================================================== Knight
MAIL = "s"  # lengan zirah rantai abu sedang: baja terang hanya di helm dan bahu, supaya tabard merah tua dominan
KT = TOP  # posisi baku


def knight_base(cv, t, eyes, brows, mouth, n=12, dx=0, bob=0, tilt=0):
    tail(cv, (CX - 7 + dx, KT + 14 + bob), phase=wag(t, n), flip=-1, length=8)
    tabard_body(cv, CX + dx, KT, bob=bob)
    head(cv, CX + dx, CY + bob, eyes=eyes, brows=brows, mouth=mouth)
    open_helmet(cv, CX + dx, CY + bob, tilt=tilt)


def knight_idle_frame(i):
    """Tegak, pedang bertumpu ujung di lantai dengan tangan di pangkal, perisai di lengan kiri; berkedip."""
    cv = Canvas()
    t = i % 12
    knight_base(cv, t, "blink" if t == 7 else "look", "flat", "flat", bob=1 if t in (4, 5) else 0)
    kite_shield(cv, CX - 19, KT + 2)
    arm(cv, (CX - 7, KT + 3), (CX - 13, KT + 7), elbow=(CX - 12, KT + 4), fur=MAIL)
    sword(cv, CX + 13, KT + 3, -90, length=13)
    arm(cv, (CX + 7, KT + 3), (CX + 13, KT + 3), elbow=(CX + 11, KT + 7), fur=MAIL)
    return cv


def knight_thinking_frame(i):
    """Tangan di dagu, pedang bersandar di bahu, perisai di lengan; gelembung "..." lalu "?"."""
    cv = Canvas()
    t = i % 12
    knight_base(cv, t, "blink" if t == 3 else "side", "worried", "frown" if t >= 6 else "flat")
    kite_shield(cv, CX - 19, KT + 2)
    arm(cv, (CX - 7, KT + 3), (CX - 13, KT + 7), elbow=(CX - 12, KT + 4), fur=MAIL)
    sword(cv, CX + 12, KT + 10, 70, length=13)
    arm(cv, (CX + 7, KT + 3), (CX + 3, CY + 9 + (t % 2 if t >= 4 else 0)), elbow=(CX + 11, KT + 7), fur=MAIL)
    if 2 <= t <= 10:
        dots_or_mark(cv, CX + 15, 0, 2, t, "?")
    return cv


def knight_shocked_frame(i):
    """Perisai terangkat ke depan bahu, mata lebar, mundur sedikit, "!"."""
    cv = Canvas()
    t = i % 12
    scare = 2 <= t <= 8
    dx = -2 if scare else 0
    knight_base(cv, t, "wide" if scare else "look", "up" if scare else "flat", "o" if scare else "flat", dx=dx)
    if scare:
        kite_shield(cv, CX - 21 + dx, KT - 6)
        arm(cv, (CX - 7 + dx, KT + 3), (CX - 14 + dx, KT), elbow=(CX - 13 + dx, KT + 5), fur=MAIL)
        bubble(cv, 48, 2, 9, 9, fill="R", tail_dir=-1)
        mini_text(cv, "!", 50, 4, "W")
        spark_lines(cv, CX + 12 + dx, CY - 6)
    else:
        kite_shield(cv, CX - 19, KT + 2)
        arm(cv, (CX - 7, KT + 3), (CX - 13, KT + 7), elbow=(CX - 12, KT + 4), fur=MAIL)
    sword(cv, CX + 13 + dx, KT + 3, -90, length=13)
    arm(cv, (CX + 7 + dx, KT + 3), (CX + 13 + dx, KT + 3), elbow=(CX + 11 + dx, KT + 7), fur=MAIL)
    return cv


# (posisi pedang, debu)
KNIGHT_ATTACK = [("rest", 0), ("rise", 0), ("up", 0), ("up", 0), ("plant", 1), ("plant", 2), ("plant", 3), ("plant", 0),
                 ("plant", 0), ("rest", 0), ("rest", 0), ("rest", 0)]


def knight_attack_frame(i):
    """Metafora: pedang diangkat lalu ditancapkan ke lantai dengan hentakan kecil dan debu piksel."""
    cv = Canvas()
    t = i % 12
    pos, dusty = KNIGHT_ATTACK[t]
    face = {"rest": ("look", "flat", "flat"), "rise": ("look", "angry", "flat"), "up": ("look", "angry", "o"),
            "plant": ("happy", "flat", "smile")}[pos]
    knight_base(cv, t, *face, bob=1 if pos == "plant" and dusty in (1, 2) else 0)
    kite_shield(cv, CX - 19, KT + 2)
    arm(cv, (CX - 7, KT + 3), (CX - 13, KT + 7), elbow=(CX - 12, KT + 4), fur=MAIL)
    if pos == "rest":
        sword(cv, CX + 13, KT + 3, -90, length=13)
        arm(cv, (CX + 7, KT + 3), (CX + 13, KT + 3), elbow=(CX + 11, KT + 7), fur=MAIL)
    elif pos == "rise":
        sword(cv, CX + 14, KT - 2, 90, length=12)
        arm(cv, (CX + 7, KT + 3), (CX + 14, KT - 2), elbow=(CX + 13, KT + 4), fur=MAIL)
    elif pos == "up":
        sword(cv, CX + 14, KT - 8, 90, length=12)
        arm(cv, (CX + 7, KT + 3), (CX + 14, KT - 8), elbow=(CX + 14, KT - 1), fur=MAIL)
    else:
        sword(cv, CX + 15, KT + 1, -90, length=15)
        arm(cv, (CX + 7, KT + 3), (CX + 15, KT + 1), elbow=(CX + 12, KT + 6), fur=MAIL)
        if dusty:
            dust(cv, CX + 15, KT + 16, dusty - 1)
            spark_lines(cv, CX + 19, KT + 10)
    return cv


KNIGHT_VICTORY = [("rest", 0), ("rise", 0), ("up", 1), ("up", 0), ("up", 1), ("up", 0), ("up", 1), ("up", 0),
                  ("up", 1), ("up", 0), ("up", 1), ("up", 0), ("rise", 0), ("rise", 0), ("rest", 0), ("rest", 0)]


def knight_victory_frame(i):
    """Pedang terangkat tinggi dengan kilau menyapu bilah (diminta brief) dan panji emas kecil yang berkibar di
    ujung pedang (elemen khas Knight; kilau berpindah sudah dipakai Detective); lompat kecil."""
    cv = Canvas()
    t = i % 16
    phase, hop = KNIGHT_VICTORY[t]
    up = phase == "up"
    knight_base(cv, t, "happy" if up else "look", "flat", ("o" if t % 2 else "smile") if up else "smile", bob=-hop, n=16)
    kite_shield(cv, CX - 19, KT + 2 - hop)
    arm(cv, (CX - 7, KT + 3 - hop), (CX - 13, KT + 7 - hop), elbow=(CX - 12, KT + 4 - hop), fur=MAIL)
    if phase == "rest":
        sword(cv, CX + 13, KT + 3, -90, length=13)
        arm(cv, (CX + 7, KT + 3), (CX + 13, KT + 3), elbow=(CX + 11, KT + 7), fur=MAIL)
    elif phase == "rise":
        sword(cv, CX + 14, KT - 2, 90, length=12)
        arm(cv, (CX + 7, KT + 3), (CX + 14, KT - 2), elbow=(CX + 13, KT + 4), fur=MAIL)
    else:
        sweep = ((t - 2) % 5) / 4.0
        sword(cv, CX + 14, KT - 9 - hop, 90, length=13, glint=sweep)
        pennant(cv, CX + 16, KT - 19 - hop, flap=(-1, 0, 1, 0)[t % 4])
        arm(cv, (CX + 7, KT + 3 - hop), (CX + 14, KT - 9 - hop), elbow=(CX + 14, KT - 2 - hop), fur=MAIL)
    return cv


def knight_defeated_frame(i):
    """Duduk bersandar pada perisai yang berdiri di lantai kiri, helm miring, pedang menancap di kanan; menghela napas."""
    cv = Canvas()
    t = i % 16
    lean = -3
    kite_shield(cv, CX - 24, KT + 4)
    tail(cv, (CX - 7 + lean, KT + 14), phase=wag(t, 16), flip=-1, length=8)
    tabard_body(cv, CX + lean, KT, bob=1)
    head(cv, CX + lean, CY + 2, eyes="blink" if t == 12 else "relief", brows="worried", mouth="frown")
    open_helmet(cv, CX + lean, CY + 2, tilt=-2)
    arm(cv, (CX - 7 + lean, KT + 4), (CX - 17, KT + 8), elbow=(CX - 13 + lean, KT + 9), fur=MAIL)
    sword(cv, CX + 17, KT + 5, -90, length=11)
    arm(cv, (CX + 7 + lean, KT + 4), (CX + 8, KT + 13), elbow=(CX + 9 + lean, KT + 9), fur=MAIL)
    if 6 <= t <= 9:
        sigh(cv, CX + lean - 16, CY - 4, t - 6)
    return cv


# ================================================================== Viking
def viking_base(cv, t, eyes, brows, mouth, n=12, dx=0, bob=0, helm_dx=0):
    tail(cv, (CX - 7 + dx, TOP + 14 + bob), phase=wag(t, n), flip=-1, length=8)
    vest_body(cv, CX + dx, TOP, bob=bob)
    head(cv, CX + dx, CY + bob, eyes=eyes, brows=brows, mouth=mouth)
    horned_helmet(cv, CX + dx, CY + bob, dx=helm_dx)


def viking_idle_frame(i):
    """Kapak di bahu kanan, perisai bundar di lengan kiri, mengangguk pelan."""
    cv = Canvas()
    t = i % 12
    nod = 1 if t in (4, 5, 10, 11) else 0
    viking_base(cv, t, "blink" if t == 8 else "look", "flat", "smile", bob=nod)
    round_shield(cv, CX - 15, TOP + 6)
    arm(cv, (CX - 7, TOP + 3), (CX - 12, TOP + 8), elbow=(CX - 12, TOP + 4))
    axe(cv, CX + 9, TOP + 6, 70, length=12)
    arm(cv, (CX + 7, TOP + 3), (CX + 10, TOP + 5), elbow=(CX + 12, TOP + 7))
    return cv


def viking_thinking_frame(i):
    """Mengelus dagu, kapak disandarkan ke bahu, perisai di lengan; gelembung "..."."""
    cv = Canvas()
    t = i % 12
    viking_base(cv, t, "blink" if t == 5 else "side", "worried", "flat")
    round_shield(cv, CX - 15, TOP + 6)
    arm(cv, (CX - 7, TOP + 3), (CX - 12, TOP + 8), elbow=(CX - 12, TOP + 4))
    axe(cv, CX + 12, TOP + 12, 80, length=13)
    arm(cv, (CX + 7, TOP + 3), (CX + 2, CY + 9 + (t // 2) % 2), elbow=(CX + 11, TOP + 7))
    if 2 <= t <= 10:
        thought_dots(cv, CX + 12, 1, 1 + min(2, (t - 2) // 2))
    return cv


VIKING_ATTACK = [("rest", 0), ("rise", 0), ("up", 0), ("up", 0), ("chop", 1), ("chop", 2), ("chop", 3), ("chop", 0),
                 ("chop", 0), ("rest", 0), ("rest", 0), ("rest", 0)]


def viking_attack_frame(i):
    """Metafora: kapak diangkat lalu dihentak ke balok kayu di lantai, serpihan kayu, "!"."""
    cv = Canvas()
    t = i % 12
    pos, chips = VIKING_ATTACK[t]
    face = {"rest": ("look", "flat", "smile"), "rise": ("look", "angry", "flat"), "up": ("look", "angry", "shout"),
            "chop": ("happy", "flat", "smile")}[pos]
    viking_base(cv, t, *face)
    log_block(cv, CX + 12, TOP + 12)
    round_shield(cv, CX - 15, TOP + 6)
    arm(cv, (CX - 7, TOP + 3), (CX - 12, TOP + 8), elbow=(CX - 12, TOP + 4))
    if pos == "rest":
        axe(cv, CX + 9, TOP + 6, 70, length=12)
        arm(cv, (CX + 7, TOP + 3), (CX + 10, TOP + 5), elbow=(CX + 12, TOP + 7))
    elif pos in ("rise", "up"):
        hy = TOP - 2 if pos == "rise" else TOP - 7
        axe(cv, CX + 12, hy, 100, length=11)
        arm(cv, (CX + 7, TOP + 3), (CX + 12, hy), elbow=(CX + 13, TOP + 3))
    else:
        axe(cv, CX + 12, TOP + 4, -40, length=11)
        arm(cv, (CX + 7, TOP + 3), (CX + 12, TOP + 4), elbow=(CX + 12, TOP + 7))
        if chips:
            for k, (ox, oy) in enumerate(((2, -2), (7, -3), (11, -1))):
                cv.put(CX + 12 + ox + (chips - 1) * (1 if k else -1), TOP + 11 + oy - chips, "X")
    if pos == "chop" and chips:
        bubble(cv, 48, 2, 9, 9, fill="R", tail_dir=-1)
        mini_text(cv, "!", 50, 4, "W")
    return cv


VIKING_VICTORY = [("rest", 0), ("rise", 0), ("up", 1), ("up", 0), ("up", 1), ("up", 0), ("up", 1), ("up", 0),
                  ("up", 1), ("up", 0), ("up", 1), ("up", 0), ("rise", 0), ("rise", 0), ("rest", 0), ("rest", 0)]


def viking_victory_frame(i):
    """Kapak dan perisai terangkat, berteriak dengan garis teriakan dari mulut (khas Viking), "!"."""
    cv = Canvas()
    t = i % 16
    phase, hop = VIKING_VICTORY[t]
    up = phase == "up"
    viking_base(cv, t, "happy" if up else "look", "up" if up else "flat", "shout" if up else "smile", bob=-hop, n=16)
    if phase == "rest":
        round_shield(cv, CX - 15, TOP + 6)
        arm(cv, (CX - 7, TOP + 3), (CX - 12, TOP + 8), elbow=(CX - 12, TOP + 4))
        axe(cv, CX + 9, TOP + 6, 70, length=12)
        arm(cv, (CX + 7, TOP + 3), (CX + 10, TOP + 5), elbow=(CX + 12, TOP + 7))
    else:
        hy = TOP - 3 if phase == "rise" else TOP - 9 - hop
        round_shield(cv, CX - 17, hy + 2)
        arm(cv, (CX - 7, TOP + 3 - hop), (CX - 14, hy + 4), elbow=(CX - 14, TOP + 1 - hop))
        axe(cv, CX + 14, hy, 95, length=11)
        arm(cv, (CX + 7, TOP + 3 - hop), (CX + 14, hy), elbow=(CX + 14, TOP + 1 - hop))
        if up:
            for s in (-1, 1):  # garis teriakan
                cv.fill({(CX + s * 5, CY + 8 - hop), (CX + s * 6, CY + 9 - hop), (CX + s * 7, CY + 10 - hop)}, "K")
            if t >= 4:
                bubble(cv, 50, 12, 9, 9, fill="R", tail_dir=-1)
                mini_text(cv, "!", 52, 14, "W")
    return cv


def viking_defeated_frame(i):
    """Duduk di atas perisai yang tergeletak, helm tergeser miring, kapak di lantai; menghela napas."""
    cv = Canvas()
    t = i % 16
    solid(cv, ellipse(CX, TOP + 16, 11.0, 2.2), "X", "x", shade_off=(1, 1))  # perisai rebah di bawah badan
    tail(cv, (CX - 7, TOP + 13), phase=wag(t, 16), flip=-1, length=8)
    vest_body(cv, CX, TOP - 1, bob=1)
    head(cv, CX, CY + 2, eyes="blink" if t == 12 else "relief", brows="worried", mouth="frown")
    horned_helmet(cv, CX, CY + 2, dx=3)
    arm(cv, (CX - 7, TOP + 3), (CX - 12, TOP + 13), elbow=(CX - 12, TOP + 8))
    arm(cv, (CX + 7, TOP + 3), (CX + 11, TOP + 13), elbow=(CX + 12, TOP + 8))
    axe(cv, CX + 14, TOP + 16, 10, length=10)
    if 6 <= t <= 9:
        sigh(cv, CX - 18, CY - 2, t - 6)
    return cv


VIKING_DANCE = [("stomp_r", 0), ("swing", 1), ("stomp_l", 0), ("swing", 1)]


def viking_dance_a_frame(i):
    """Jig Viking: hentakan kaki dan ayunan lengan bergantian per beat (16 x 120 ms)."""
    cv = Canvas()
    t = i % 16
    beat = t // 4
    move, bob = VIKING_DANCE[beat]
    tail(cv, (CX - 7, TOP + 14 + bob), phase=beat * 1.6 + (t % 4) * 0.25, flip=-1, length=8)
    torso = dressed_body(cv, CX, TOP + bob, "D", "K", pants="x", pants_shade="e",
                         leg_twitch=2 if move == "stomp_r" else 0)
    cv.fill({(x, y) for (x, y) in inner(torso) if y <= TOP + bob + 3 and abs(x - CX + 0.5) <= 3.5 - (y - TOP - bob)}, "B")
    if move == "stomp_l":  # kaki kiri terangkat
        solid(cv, ellipse(CX - 5.2, TOP + 10.2 + bob, 4.2, 2.8), "x", "e")
        solid(cv, ellipse(CX - 3.0, TOP + 12.2 + bob, 2.6, 1.5), "F", "f", shade_off=(1, 1))
    head(cv, CX, CY + bob, eyes="happy", brows="flat", mouth="smile" if beat % 2 == 0 else "o")
    horned_helmet(cv, CX, CY + bob)
    if move == "swing":
        arm(cv, (CX - 7, TOP + 3 + bob), (CX - 18, TOP - 9 + bob), elbow=(CX - 15, TOP + 1 + bob))
        arm(cv, (CX + 7, TOP + 3 + bob), (CX + 18, TOP - 9 + bob), elbow=(CX + 15, TOP + 1 + bob))
    else:
        s = 1 if move == "stomp_r" else -1
        arm(cv, (CX + 7 * s, TOP + 3), (CX + 13 * s, TOP + 9), elbow=(CX + 12 * s, TOP + 5))
        arm(cv, (CX - 7 * s, TOP + 3), (CX - 14 * s, TOP - 3), elbow=(CX - 13 * s, TOP + 2))
        dust(cv, CX + 5 * s, TOP + 16, 0)
    return cv


# ================================================================== Pirate
def pirate_base(cv, t, eyes, brows, mouth, n=12, dx=0, bob=0, hat_dy=0, hat_tip=0, hat=True):
    tail(cv, (CX - 7 + dx, TOP + 14 + bob), phase=wag(t, n), flip=-1, length=8)
    coat_body(cv, CX + dx, TOP, bob=bob)
    head(cv, CX + dx, CY + bob, eyes=eyes, brows=brows, mouth=mouth)
    if hat:
        tricorn(cv, CX + dx, CY + bob, dy=hat_dy, tip=hat_tip)


def pirate_idle_frame(i):
    """Bersandar pada cutlass yang ujungnya di lantai, tangan lain di pinggang; berkedip."""
    cv = Canvas()
    t = i % 12
    pirate_base(cv, t, "blink" if t == 6 else ("side" if t in (9, 10) else "look"), "flat", "smirk")
    cutlass(cv, CX + 13, TOP + 4, -100, length=11)
    arm(cv, (CX + 7, TOP + 3), (CX + 13, TOP + 4), elbow=(CX + 12, TOP + 8), fur="i")
    arm(cv, (CX - 7, TOP + 3), (CX - 7, TOP + 9), elbow=(CX - 12, TOP + 6), fur="i")
    return cv


def pirate_thinking_frame(i):
    """Teropong ke mata kanan, mengamati kejauhan; gelembung "..." lalu "?"."""
    cv = Canvas()
    t = i % 12
    look = 2 <= t <= 10
    pirate_base(cv, t, "blink" if t == 11 else ("left" if look else "look"), "raised" if look else "flat", "flat")
    if look:
        telescope(cv, CX + 5, CY + 1, deg=10, length=12)
        arm(cv, (CX + 7, TOP + 3), (CX + 9, CY + 3), elbow=(CX + 12, TOP + 5), fur="i")
        dots_or_mark(cv, CX + 17, 10, 2, t, "?")
    else:
        telescope(cv, CX + 9, TOP + 8, deg=-20, length=9)
        arm(cv, (CX + 7, TOP + 3), (CX + 10, TOP + 8), elbow=(CX + 11, TOP + 6), fur="i")
    arm(cv, (CX - 7, TOP + 3), (CX - 7, TOP + 9), elbow=(CX - 12, TOP + 6), fur="i")
    return cv


PIRATE_ATTACK = [("rest", 0), ("rise", 0), ("up", 0), ("up", 0), ("stab", 1), ("stab", 2), ("stab", 0), ("stab", 0),
                 ("stab", 0), ("rest", 0), ("rest", 0), ("rest", 0)]


def pirate_attack_frame(i):
    """Metafora: cutlass ditancapkan ke papan kayu di lantai, "!"."""
    cv = Canvas()
    t = i % 12
    pos, hit = PIRATE_ATTACK[t]
    face = {"rest": ("look", "flat", "smirk"), "rise": ("look", "angry", "flat"), "up": ("look", "angry", "o"),
            "stab": ("happy", "flat", "smile")}[pos]
    pirate_base(cv, t, *face)
    plank(cv, CX + 9, TOP + 13)
    if pos == "rest":
        cutlass(cv, CX + 13, TOP + 4, -100, length=11)
        arm(cv, (CX + 7, TOP + 3), (CX + 13, TOP + 4), elbow=(CX + 12, TOP + 8), fur="i")
    elif pos in ("rise", "up"):
        hy = TOP - 3 if pos == "rise" else TOP - 8
        cutlass(cv, CX + 13, hy, 80, length=11)
        arm(cv, (CX + 7, TOP + 3), (CX + 13, hy), elbow=(CX + 13, TOP + 3), fur="i")
    else:
        cutlass(cv, CX + 15, TOP + 3, -85, length=11)
        arm(cv, (CX + 7, TOP + 3), (CX + 15, TOP + 3), elbow=(CX + 12, TOP + 7), fur="i")
        if hit:
            spark_lines(cv, CX + 20, TOP + 8)
            bubble(cv, 48, 2, 9, 9, fill="R", tail_dir=-1)
            mini_text(cv, "!", 50, 4, "W")
    arm(cv, (CX - 7, TOP + 3), (CX - 7, TOP + 9), elbow=(CX - 12, TOP + 6), fur="i")
    return cv


PIRATE_VICTORY = [("rest", 0), ("toss", 0), ("up", 1), ("up", 0), ("up", 1), ("up", 0), ("up", 1), ("up", 0),
                  ("up", 1), ("up", 0), ("up", 1), ("catch", 0), ("rest", 0), ("rest", 0), ("rest", 0), ("rest", 0)]
# (geser x, geser y) topi terhadap posisi di kepala: melambung ke kiri atas lalu kembali, tetap di dalam kanvas
HAT_FLY = {1: (0, -2), 2: (-2, -4), 3: (-4, -5), 4: (-6, -5), 5: (-7, -5), 6: (-8, -5), 7: (-8, -4), 8: (-7, -3),
           9: (-5, -2), 10: (-3, -1), 11: (-1, 0)}
PLOW = 3  # victory: tokoh diturunkan 3 px supaya topi yang dilempar tetap di dalam kanvas


def pirate_victory_frame(i):
    """Topi dilempar ke atas, cutlass terangkat, konfeti, dan koin emas memercik lalu jatuh (khas Pirate)."""
    cv = Canvas()
    t = i % 16
    phase, hop = PIRATE_VICTORY[t]
    up = phase == "up"
    fly = HAT_FLY.get(t)
    b = PLOW - hop
    pirate_base(cv, t, "happy" if phase != "rest" else "look", "flat", ("o" if t % 2 else "smile") if up else "smile",
                bob=b, hat=fly is None, n=16)
    if fly is not None:
        tricorn(cv, CX + fly[0], CY + b, dy=fly[1])
    if phase == "rest":
        cutlass(cv, CX + 13, TOP + 4 + b, -100, length=11)
        arm(cv, (CX + 7, TOP + 3 + b), (CX + 13, TOP + 4 + b), elbow=(CX + 12, TOP + 8 + b), fur="i")
        arm(cv, (CX - 7, TOP + 3 + b), (CX - 7, TOP + 9 + b), elbow=(CX - 12, TOP + 6 + b), fur="i")
    else:
        cutlass(cv, CX + 14, TOP - 8 + b, 80, length=11)
        arm(cv, (CX + 7, TOP + 3 + b), (CX + 14, TOP - 8 + b), elbow=(CX + 14, TOP - 1 + b), fur="i")
        arm(cv, (CX - 7, TOP + 3 + b), (CX - 17, TOP - 8 + b), elbow=(CX - 14, TOP + b), fur="i")
        if up:
            confetti(cv, t, n=6)
            for k in range(4):  # koin memercik ke atas lalu jatuh
                ph = (t - 2 + k * 2) % 8
                cx_, cy_ = CX - 18 + k * 12, 34 - (6 - abs(ph - 4)) * 2
                coin(cv, cx_, cy_)
    return cv


def pirate_defeated_frame(i):
    """Duduk di atas peti dengan tenang, topi merosot menutupi mata, tangan terlipat; menghela napas."""
    cv = Canvas()
    t = i % 16
    treasure_chest(cv, CX - 10, TOP + 12)
    tail(cv, (CX - 7, TOP + 10), phase=wag(t, 16), flip=-1, length=8)
    coat_body(cv, CX, TOP - 3)
    head(cv, CX, CY - 1, eyes="blink", brows="flat", mouth="flat" if t < 8 else "smile")
    tricorn(cv, CX, CY - 1, tip=4)
    arm(cv, (CX + 7, TOP), (CX - 5, TOP + 4), elbow=(CX + 10, TOP + 5), fur="i")
    arm(cv, (CX - 7, TOP), (CX + 5, TOP + 3), elbow=(CX - 10, TOP + 5), fur="i")
    cutlass(cv, CX + 16, TOP + 17, -170, length=9)
    if 6 <= t <= 9:
        sigh(cv, CX + 12, CY + 2, t - 6)
    return cv


PIRATE_DANCE = [("kick_r", 0), ("clap", 1), ("kick_l", 0), ("clap", 1)]


def pirate_dance_a_frame(i):
    """Jig bajak laut: tendangan kaki bergantian dan tepuk tangan di depan dada per beat (16 x 120 ms).
    Tepukan sengaja di depan dada, bukan di atas kepala: tangan di atas kepala menutupi wajah di kanvas 64x48."""
    cv = Canvas()
    t = i % 16
    beat = t // 4
    move, bob = PIRATE_DANCE[beat]
    tail(cv, (CX - 7, TOP + 14 + bob), phase=beat * 1.6 + (t % 4) * 0.25, flip=-1, length=8)
    torso = dressed_body(cv, CX, TOP + bob, "i", "2", pants="L", pants_shade="q", leg_twitch=3 if move == "kick_r" else 0)
    cv.fill({(x, TOP + bob + 8) for x in range(CX - 8, CX + 9) if (x, TOP + bob + 8) in inner(torso)}, "L")
    if move == "kick_r":
        solid(cv, ellipse(CX + 9, TOP + 11, 2.4, 1.6), "F", "f", shade_off=(1, 1))
    if move == "kick_l":
        solid(cv, ellipse(CX - 5.2, TOP + 9.2, 4.2, 2.8), "L", "q")
        solid(cv, ellipse(CX - 9, TOP + 11, 2.4, 1.6), "F", "f", shade_off=(1, 1))
    head(cv, CX, CY + bob, eyes="happy", brows="flat", mouth="smile" if beat % 2 == 0 else "o")
    tricorn(cv, CX, CY + bob)
    if move == "clap":
        arm(cv, (CX - 7, TOP + 3 + bob), (CX - 2, TOP + 2 + bob), elbow=(CX - 13, TOP + 5 + bob), fur="i")
        arm(cv, (CX + 7, TOP + 3 + bob), (CX + 2, TOP + 2 + bob), elbow=(CX + 13, TOP + 5 + bob), fur="i")
    else:
        s = 1 if move == "kick_r" else -1
        arm(cv, (CX + 7 * s, TOP + 3), (CX + 7 * s, TOP + 9), elbow=(CX + 12 * s, TOP + 6), fur="i")
        arm(cv, (CX - 7 * s, TOP + 3), (CX - 14 * s, TOP - 2), elbow=(CX - 13 * s, TOP + 3), fur="i")
    return cv


# ================================================================== Wizard
WY, WT = CY + 4, TOP + 4  # diturunkan 4 px supaya topi runcing muat di kanvas


def wizard_base(cv, t, eyes, brows, mouth, n=12, dx=0, bob=0, hat_lift=0, droop=0, twinkle=0, hat=True):
    tail(cv, (CX - 9 + dx, WT + 14 + bob), phase=wag(t, n), flip=-1, length=7)
    robe_body(cv, CX + dx, WT, bob=bob)
    head(cv, CX + dx, WY + bob, eyes=eyes, brows=brows, mouth=mouth)
    if hat:
        wizard_hat(cv, CX + dx, WY + bob, lift=hat_lift, twinkle=twinkle, droop=droop)


def wizard_arm(cv, shoulder, hand, elbow):
    arm(cv, shoulder, hand, elbow=elbow, fur="3", r=2.2)


def wizard_idle_frame(i):
    """Tongkat bersinar redup di tangan kanan, bintang di topi berkedip; tangan kiri memegang buku tertutup."""
    cv = Canvas()
    t = i % 12
    wizard_base(cv, t, "blink" if t == 7 else "look", "flat", "smile", twinkle=t // 3)
    staff(cv, CX + 14, WT + 14, glow=(t // 2) % 3 if t % 6 < 4 else 0, length=21)
    wizard_arm(cv, (CX + 7, WT + 3), (CX + 14, WT + 5), (CX + 12, WT + 8))
    solid(cv, rect(CX - 18, WT + 4, 7, 9), "z", "1", shade_off=(1, 1))  # buku mantra tertutup
    cv.fill(rect(CX - 17, WT + 5, 1, 7), "C")
    wizard_arm(cv, (CX - 7, WT + 3), (CX - 12, WT + 8), (CX - 12, WT + 5))
    return cv


def wizard_thinking_frame(i):
    """Membolak-balik buku mantra di pangkuan; gelembung "..." lalu "?"."""
    cv = Canvas()
    t = i % 12
    page = {3: 1, 4: 2, 8: 1, 9: 2}.get(t, 0)
    wizard_base(cv, t, "down" if t < 6 else "side", "flat" if t < 6 else "worried", "flat" if t < 6 else "frown")
    spellbook(cv, CX - 6, WT + 8, page=page)
    wizard_arm(cv, (CX - 7, WT + 3), (CX - 6, WT + 11), (CX - 11, WT + 7))
    wizard_arm(cv, (CX + 7, WT + 3), (CX + 6, WT + 11), (CX + 11, WT + 7))
    staff(cv, CX + 17, WT + 16, glow=0, length=20)
    if 5 <= t <= 11:
        dots_or_mark(cv, CX + 14, 0, 5, t, "?")
    return cv


def wizard_shocked_frame(i):
    """"Poof": kepulan asap kecil dari tongkat, topi terangkat dari kepala, mata lebar, "!"."""
    cv = Canvas()
    t = i % 12
    poof = 2 <= t <= 8
    lift = {2: 2, 3: 4, 4: 4, 5: 3, 6: 2, 7: 1}.get(t, 0)
    wizard_base(cv, t, "wide" if poof else "look", "up" if poof else "flat", "o" if poof else "flat", dx=-1 if poof else 0,
                hat_lift=lift)
    staff(cv, CX + 14, WT + 14, glow=2 if t == 2 else 0, length=21)
    wizard_arm(cv, (CX + 7, WT + 3), (CX + 14, WT + 5), (CX + 12, WT + 8))
    wizard_arm(cv, (CX - 7, WT + 3), (CX - 13, WT + 1) if poof else (CX - 12, WT + 8), (CX - 12, WT + 5))
    if poof:
        k = min(3, t - 2)
        puff(cv, CX + 14, 4 - (k // 2), 1.4 + k * 0.5)
        puff(cv, CX + 18, 7, 1.0 + k * 0.3)
        bubble(cv, 2, 2, 9, 9, fill="R", tail_dir=1)
        mini_text(cv, "!", 4, 4, "W")
    return cv


WIZ_ATTACK = [("rest", 0), ("rise", 0), ("rise", 0), ("stomp", 1), ("stomp", 2), ("stomp", 3), ("stomp", 3), ("stomp", 2),
              ("stomp", 1), ("rest", 0), ("rest", 0), ("rest", 0)]


def wizard_attack_frame(i):
    """Metafora: tongkat dihentak ke lantai, percikan bintang menyebar di sekitar kristal, "!"."""
    cv = Canvas()
    t = i % 12
    pos, spark = WIZ_ATTACK[t]
    face = {"rest": ("look", "flat", "smile"), "rise": ("look", "angry", "flat"), "stomp": ("happy", "up", "o")}[pos]
    wizard_base(cv, t, *face)
    sy = WT + 14 - (3 if pos == "rise" else 0)
    staff(cv, CX + 14, sy, glow=2 if pos == "stomp" else 0, length=21)
    wizard_arm(cv, (CX + 7, WT + 3), (CX + 14, sy - 9), (CX + 12, WT + 6))
    wizard_arm(cv, (CX - 7, WT + 3), (CX - 12, WT + 8), (CX - 12, WT + 5))
    if spark:
        top = (CX + 14, sy - 23)
        for k in range(5):
            a = math.radians(k * 72 + spark * 12)
            r = 3 + spark * 2
            star(cv, int(top[0] + r * math.cos(a)), int(top[1] + r * math.sin(a)), "Y" if k % 2 else "O")
        dust(cv, CX + 14, WT + 17, spark - 1)
        if spark >= 2:
            bubble(cv, 2, 2, 9, 9, fill="R", tail_dir=1)
            mini_text(cv, "!", 4, 4, "W")
    return cv


WIZ_VICTORY = [("rest", 0), ("rise", 0), ("up", 1), ("up", 0), ("up", 1), ("up", 0), ("up", 1), ("up", 0),
               ("up", 1), ("up", 0), ("up", 1), ("up", 0), ("rise", 0), ("rise", 0), ("rest", 0), ("rest", 0)]


def wizard_victory_frame(i):
    """Tongkat terangkat tinggi, bintang meledak dari kristal menjadi hujan bintang kecil (khas Wizard)."""
    cv = Canvas()
    t = i % 16
    phase, hop = WIZ_VICTORY[t]
    up = phase == "up"
    wizard_base(cv, t, "happy" if up else "look", "flat", ("o" if t % 2 else "smile") if up else "smile", bob=-hop,
                twinkle=t, n=16)
    if phase == "rest":
        staff(cv, CX + 14, WT + 14, glow=0, length=21)
        wizard_arm(cv, (CX + 7, WT + 3), (CX + 14, WT + 5), (CX + 12, WT + 8))
    else:
        sy = WT + 6 - (6 if up else 0) - hop
        staff(cv, CX + 15, sy, glow=2 if up else 1, length=18)
        wizard_arm(cv, (CX + 7, WT + 3 - hop), (CX + 15, sy - 6), (CX + 14, WT - 1 - hop))
        if up:
            for k in range(7):  # hujan bintang dari kristal
                ph = (t - 2 + k) % 6
                x = (k * 9 + 3) % 58 + 3
                y = 2 + ph * 5 + (k % 3)
                star(cv, x, y, "Y" if (k + t) % 2 else "O")
    wizard_arm(cv, (CX - 7, WT + 3 - hop), (CX - 13, WT - 3 - hop) if up else (CX - 12, WT + 8), (CX - 13, WT + 2 - hop))
    return cv


def wizard_defeated_frame(i):
    """Mantra gagal: asap kecil dari tongkat yang tergeletak, topi merosot menutupi mata, duduk lunglai."""
    cv = Canvas()
    t = i % 16
    wizard_base(cv, t, "blink", "worried", "frown", bob=1, droop=5, n=16)
    staff(cv, CX + 16, WT + 17, glow=0, length=0)  # kristal di lantai
    cv.fill(capsule((CX - 20, WT + 17), (CX + 15, WT + 17), 0.7), "N")  # tongkat tergeletak di lantai
    wizard_arm(cv, (CX - 7, WT + 4), (CX - 12, WT + 13), (CX - 12, WT + 8))
    wizard_arm(cv, (CX + 7, WT + 4), (CX + 11, WT + 13), (CX + 12, WT + 8))
    k = (t // 2) % 4
    puff(cv, CX + 17 + k, WT + 10 - k * 2, 1.0 + k * 0.35)
    if 8 <= t <= 13:
        thought_dots(cv, CX + 10, 1, 1 + min(2, (t - 8) // 2))
    return cv


PROPS = {
    "knight: pedang": lambda cv: sword(cv, 20, 30, 90, length=13),
    "knight: perisai": lambda cv: kite_shield(cv, 28, 20),
    "knight: helm terbuka": lambda cv: open_helmet(cv, 32, 24),
    "knight: panji": lambda cv: pennant(cv, 28, 20),
    "viking: kapak": lambda cv: axe(cv, 26, 30, 70, length=12),
    "viking: perisai bundar": lambda cv: round_shield(cv, 32, 24),
    "viking: helm bertanduk": lambda cv: horned_helmet(cv, 32, 24),
    "pirate: cutlass": lambda cv: cutlass(cv, 26, 30, 80, length=11),
    "pirate: teropong": lambda cv: telescope(cv, 24, 24, 0, 12),
    "pirate: tricorn": lambda cv: tricorn(cv, 32, 24),
    "wizard: tongkat": lambda cv: staff(cv, 32, 40, glow=1, length=21),
    "wizard: topi runcing": lambda cv: wizard_hat(cv, 32, 30),
    "wizard: buku mantra": lambda cv: spellbook(cv, 26, 20),
}

SCENES = {
    "knight-idle": (knight_idle_frame, 12, lambda i: 180 if i % 12 != 7 else 120),
    "knight-thinking": (knight_thinking_frame, 12, lambda i: 170),
    "knight-shocked": (knight_shocked_frame, 12, lambda i: 150 if i % 12 in (0, 1, 9, 10, 11) else 120),
    "knight-attack": (knight_attack_frame, 12, lambda i: 90 if i % 12 == 4 else (220 if i % 12 == 6 else 140)),
    "knight-victory": (knight_victory_frame, 16, lambda i: 150 if i % 16 in (0, 1, 14, 15) else 110),
    "knight-defeated": (knight_defeated_frame, 16, lambda i: 230 if 6 <= i % 16 <= 9 else 190),
    "viking-idle": (viking_idle_frame, 12, lambda i: 180 if i % 12 != 8 else 120),
    "viking-thinking": (viking_thinking_frame, 12, lambda i: 170),
    "viking-attack": (viking_attack_frame, 12, lambda i: 90 if i % 12 == 4 else (220 if i % 12 == 6 else 140)),
    "viking-victory": (viking_victory_frame, 16, lambda i: 150 if i % 16 in (0, 1, 14, 15) else 110),
    "viking-defeated": (viking_defeated_frame, 16, lambda i: 230 if 6 <= i % 16 <= 9 else 190),
    "viking-dance-a": (viking_dance_a_frame, 16, lambda i: 120),
    "pirate-idle": (pirate_idle_frame, 12, lambda i: 180 if i % 12 != 6 else 120),
    "pirate-thinking": (pirate_thinking_frame, 12, lambda i: 170),
    "pirate-attack": (pirate_attack_frame, 12, lambda i: 90 if i % 12 == 4 else (220 if i % 12 == 5 else 140)),
    "pirate-victory": (pirate_victory_frame, 16, lambda i: 150 if i % 16 in (0, 12, 13, 14, 15) else 110),
    "pirate-defeated": (pirate_defeated_frame, 16, lambda i: 230 if 6 <= i % 16 <= 9 else 200),
    "pirate-dance-a": (pirate_dance_a_frame, 16, lambda i: 120),
    "wizard-idle": (wizard_idle_frame, 12, lambda i: 180 if i % 12 != 7 else 120),
    "wizard-thinking": (wizard_thinking_frame, 12, lambda i: 170),
    "wizard-shocked": (wizard_shocked_frame, 12, lambda i: 150 if i % 12 in (0, 1, 9, 10, 11) else 110),
    "wizard-attack": (wizard_attack_frame, 12, lambda i: 90 if i % 12 == 3 else 140),
    "wizard-victory": (wizard_victory_frame, 16, lambda i: 150 if i % 16 in (0, 1, 14, 15) else 110),
    "wizard-defeated": (wizard_defeated_frame, 16, lambda i: 200),
}
