"""Varian kelas fantasi Gobyet (Fase 2, Gerbang J): 4 varian per faksi Knight, Viking, Pirate.

Tiap varian punya idle, attack, dan victory. Tampilan mengikuti kostum dasar faksi (src/fantasy.py):
badan duduk yang sama, helm atau topi faksi, dan prop faksi yang dipakai bersama. Yang berubah hanya prop,
aksesori, dan warna aksen. Warna aksen (warna dominan varian) berjarak ΔE >= 10 dari saudara sefaksi.

Pedoman senjata (7.1): gaya kartun; tanpa darah, luka, proyektil melayang, kilatan tembakan, atau asap laras.
attack adalah metafora: prop dihentak atau ditancapkan ke lantai atau ke balok/papan kayu, atau pose membidik
ke papan sasaran bulat (tanpa melepas anak panah) dan ke atas (senapan). Tidak ada yang diarahkan ke karakter.
Senjata api (blunderbuss, senapan panjang) hanya prop yang dipegang.

Setiap victory punya satu elemen khas yang belum dipakai kostum lain (tabel di pack/STYLE.md).
"""
import math

from monkey import (Canvas, head, arm, tail, sitting_body, mini_text, bubble, puff, spark_lines, ellipse, capsule,
                    chain, rect, edge, solid)
from costumes import CX, CY, TOP, dressed_body, inner
from fantasy import (wag, dust, sword, kite_shield, open_helmet, horned_helmet, round_shield, axe, log_block,
                     tricorn, cutlass, plank, star, coin, MAIL)

IDLE_N, ATTACK_N, VICTORY_N = 12, 12, 16
# fase attack bersama: (pose, dampak). dampak 1..3 = debu/serpihan menyebar di frame hentakan
ATTACK = [("rest", 0), ("rise", 0), ("up", 0), ("up", 0), ("hit", 1), ("hit", 2), ("hit", 3), ("hit", 0),
          ("hit", 0), ("rest", 0), ("rest", 0), ("rest", 0)]
AIM = [("rest", 0), ("rise", 0), ("draw", 0), ("draw", 0), ("aim", 1), ("aim", 2), ("aim", 3), ("aim", 2),
       ("aim", 1), ("rest", 0), ("rest", 0), ("rest", 0)]
VICTORY = [("rest", 0), ("rise", 0), ("up", 1), ("up", 0), ("up", 1), ("up", 0), ("up", 1), ("up", 0),
           ("up", 1), ("up", 0), ("up", 1), ("up", 0), ("rise", 0), ("rise", 0), ("rest", 0), ("rest", 0)]
FACE = {"rest": ("look", "flat", "smile"), "rise": ("look", "angry", "flat"), "up": ("look", "angry", "o"),
        "hit": ("happy", "flat", "smile"), "draw": ("look", "angry", "flat"), "aim": ("look", "angry", "flat")}


def idle_ms(i):
    return 180 if i % IDLE_N != 7 else 120


def attack_ms(i):
    return 90 if i % ATTACK_N == 4 else (220 if i % ATTACK_N == 6 else 140)


def aim_ms(i):
    return 200 if 4 <= i % ATTACK_N <= 8 else 140


def victory_ms(i):
    return 150 if i % VICTORY_N in (0, 1, 14, 15) else 110


# ================================================================== prop varian
def pauldron(cv, x, y):
    """Pelindung bahu baja tebal."""
    solid(cv, ellipse(x, y, 3.6, 2.8), "G", "s", shade_off=(1, 1))


def greatsword(cv, hx, hy, deg, length=17, glint=None):
    """Pedang besar dua tangan: bilah panjang, pelindung tangan lebar."""
    sword(cv, hx, hy, deg, length=length, glint=glint)
    a = math.radians(deg)
    ux, uy = math.cos(a), -math.sin(a)
    px, py = -uy, ux
    cv.fill(capsule((hx + ux * 2 - px * 3, hy + uy * 2 - py * 3), (hx + ux * 2 + px * 3, hy + uy * 2 + py * 3), 0.6), "y")


def longbow(cv, x, y0, y1, draw=0, bend=3, horizontal=False):
    """Busur panjang tegak dari y0 ke y1 di x (melengkung ke kiri), tali lurus; draw = tali ditarik ke kanan (px).
    horizontal=True: busur mendatar dari x0=y0 ke x1=y1 di baris x... (tidak dipakai)."""
    mid = (y0 + y1) / 2.0
    half = (y1 - y0) / 2.0
    pts = [(x - bend * (1 - ((y - mid) / half) ** 2), y) for y in [y0 + k * (y1 - y0) / 10.0 for k in range(11)]]
    cv.fill(chain(pts, 0.8), "N")
    cv.fill({(x, y0), (x, y1)}, "N")
    if draw:
        cv.fill(chain([(x, y0), (x + draw, mid), (x, y1)], 0.4), "h")
    else:
        cv.fill({(x, y) for y in range(int(y0) + 1, int(y1))}, "h")


def arrow_nocked(cv, x0, x1, y):
    """Anak panah terpasang di busur (tidak dilepas): batang dari x0 ke x1, mata panah di x1."""
    cv.fill({(x, y) for x in range(min(x0, x1), max(x0, x1) + 1)}, "X")
    cv.fill({(x1, y), (x1 + 1, y), (x1, y - 1), (x1, y + 1)}, "s")
    cv.fill({(min(x0, x1) - 1, y - 1), (min(x0, x1) - 1, y + 1)}, "R")


def quiver(cv, x, y):
    """Tabung anak panah di punggung (terlihat di atas bahu kiri) dengan tiga bulu anak panah."""
    solid(cv, capsule((x, y), (x + 3, y + 9), 1.6), "x", "e", shade_off=(1, 1))
    for k, c in enumerate("WRW"):
        cv.fill({(x - 1 + k, y - 2 - (k % 2)), (x - 1 + k, y - 1 - (k % 2))}, c)


def target_board(cv, x, y, star_on=False):
    """Papan sasaran bulat di atas tiang kayu (untuk pose membidik; tidak ada anak panah yang menancap)."""
    cv.fill(capsule((x, y + 5), (x, y + 17), 0.7), "N")
    solid(cv, ellipse(x, y, 5.0, 5.0), "W", None)
    ring = ellipse(x, y, 3.4, 3.4)
    cv.fill(ring - ellipse(x, y, 2.2, 2.2), "R")
    cv.fill(ellipse(x, y, 1.2, 1.2), "R")
    if star_on:
        star(cv, int(x), int(y), "Y")


def halberd(cv, x, y_bot, length=26):
    """Halberd tegak: tongkat kayu, kapak baja kecil dan tombak di puncak."""
    top = y_bot - length
    cv.fill(capsule((x, y_bot), (x, top), 0.7), "N")
    solid(cv, {(x + 1 + dx, top + 3 + dy) for dx in range(4) for dy in range(4 - dx // 2)}, "G", "s", shade_off=(1, 1))
    cv.fill({(x, top - 1), (x, top - 2), (x, top - 3)}, "G")


def mace(cv, hx, hy, deg, length=8):
    """Gada: gagang kayu dan kepala bulat bertonjolan."""
    a = math.radians(deg)
    ux, uy = math.cos(a), -math.sin(a)
    tip = (hx + ux * length, hy + uy * length)
    cv.fill(capsule((hx - ux, hy - uy), tip, 0.7), "N")
    solid(cv, ellipse(tip[0], tip[1], 2.4, 2.4), "s", "g", shade_off=(1, 1))
    for dx, dy in ((0, -3), (3, 0), (0, 3), (-3, 0)):
        cv.put(int(round(tip[0])) + dx, int(round(tip[1])) + dy, "s")


def hood(cv, cx, cy, back=True):
    """Tudung gelap: back=True menggambar kain di belakang kepala (dipanggil sebelum head);
    back=False menggambar kubah tudung di atas kepala sampai alis (dipanggil sesudah head). Wajah tetap terbuka."""
    if back:
        solid(cv, ellipse(cx, cy + 1, 12.5, 10.0), "l", "L")
    else:
        dome = {p for p in ellipse(cx, cy - 2.0, 10.4, 8.2) if p[1] <= cy - 3}
        solid(cv, dome, "l", "L", shade_off=(1, 1))
        cv.fill({(cx - 1, int(cy) - 9), (cx, int(cy) - 9)}, "L")


def dagger(cv, hx, hy, deg, length=6):
    sword(cv, hx, hy, deg, length=length)


def smoke_bomb(cv, x, y):
    """Bom asap kecil di sabuk: bola gelap 4x4 dengan sumbu cokelat pendek (tidak menyala)."""
    solid(cv, ellipse(x, y, 2.2, 2.2), "g", "s", shade_off=(1, 1))
    cv.put(int(x), int(y) - 3, "N")
    cv.put(int(x) + 1, int(y) - 4, "N")


def smoke_ring(cv, x, y, r):
    """Cincin asap berongga yang membesar."""
    ring = ellipse(x, y, r, r * 0.6) - ellipse(x, y, max(0.1, r - 1.2), max(0.1, r * 0.6 - 1.0))
    cv.fill(ring, "s")


def fur_headband(cv, cx, cy):
    """Ikat kepala bulu krem di dahi (di atas alis), tanpa helm."""
    band = {(x, y) for x in range(cx - 9, cx + 10) for y in (int(cy) - 6, int(cy) - 5)}
    band = {p for p in band if p in ellipse(cx, cy, 10.2, 9.0)}
    solid(cv, band, "c", "X", shade_off=(1, 1))
    for x in range(cx - 8, cx + 9, 3):
        cv.put(x, int(cy) - 7, "c")


def fur_mantle(cv, cx, top):
    """Mantel bulu krem di bahu dan dada (Berserker), di atas badan berbulu."""
    m = {p for p in ellipse(cx, top + 3.5, 10.5, 5.0) if p[1] >= top}
    solid(cv, m, "c", "X", shade_off=(1, 1))
    for x in range(cx - 8, cx + 9, 3):
        cv.put(x, top + 7, "X")


def javelin(cv, x, y_bot, length=24, deg=90):
    """Tombak lempar: gagang kayu tipis panjang, mata tombak baja kecil. Dipegang, tidak dilempar."""
    a = math.radians(deg)
    ux, uy = math.cos(a), -math.sin(a)
    tip = (x + ux * length, y_bot + uy * length)
    cv.fill(capsule((x, y_bot), tip, 0.6), "N")
    tx, ty = int(round(tip[0])), int(round(tip[1]))
    px, py = -uy, ux
    head_ = {(int(round(tip[0] + ux * k + px * s)), int(round(tip[1] + uy * k + py * s))) for k in range(0, 4)
             for s in ((-1, 0, 1) if k < 2 else (0,))}
    solid(cv, head_, "G", None)


def seax(cv, x, y):
    """Pisau seax dalam sarung kulit di sabuk (tidak dicabut)."""
    solid(cv, capsule((x, y), (x + 5, y + 2), 1.0), "e", None)
    cv.put(x - 1, y, "N")


def captain_hat(cv, cx, cy, dy=0):
    """Topi kapten: tricorn bertepi emas lebar dengan bulu merah besar melengkung ke kiri."""
    tricorn(cv, cx, cy, dy=dy)
    y = int(cy - 8 + dy)
    solid(cv, chain([(cx - 3, y - 1), (cx - 7, y - 4), (cx - 12, y - 4), (cx - 14, y - 2)], 1.4), "R", "T", shade_off=(1, 1))
    cv.fill({(x, y + 2 - abs(x - cx) // 5) for x in range(cx - 11, cx + 12)}, "O")


def blunderbuss(cv, hx, hy, deg=-90, length=12):
    """Blunderbuss sebagai prop yang dipegang: popor kayu dan laras kuningan melebar. Tidak pernah ditembakkan."""
    a = math.radians(deg)
    ux, uy = math.cos(a), -math.sin(a)
    px, py = -uy, ux
    solid(cv, capsule((hx - ux * 4, hy - uy * 4), (hx + ux * 2, hy + uy * 2), 1.4), "X", "x", shade_off=(1, 1))
    cv.fill(capsule((hx + ux * 2, hy + uy * 2), (hx + ux * length, hy + uy * length), 0.9), "y")
    mx, my = hx + ux * length, hy + uy * length
    cv.fill(capsule((mx - px * 1.8, my - py * 1.8), (mx + px * 1.8, my + py * 1.8), 0.7), "y")


def parrot(cv, x, y, flap=0):
    """Burung beo kecil 6x7 (merah, sayap biru), hinggap di bahu; flap 0/1 = sayap terbuka."""
    solid(cv, ellipse(x, y, 2.4, 3.0), "R", "T", shade_off=(1, 1))
    solid(cv, ellipse(x + 0.5, y - 3.2, 1.8, 1.7), "R", None)
    cv.put(x - 1, y - 4, "P")
    cv.fill({(x - 2, y - 3), (x - 3, y - 3)}, "Y")  # paruh
    wing = {(x + 1, y), (x + 2, y), (x + 2, y + 1)} if not flap else {(x + 2, y - 1), (x + 3, y - 2), (x + 4, y - 3), (x + 3, y - 1)}
    cv.fill(wing, "3")
    cv.fill({(x, y + 3), (x + 1, y + 4)}, "3")  # ekor


def bandana(cv, cx, cy, flap=0):
    """Bandana merah menutupi puncak kepala sampai alis, simpul dengan dua ujung kain di kanan."""
    dome = {p for p in ellipse(cx, cy - 2.0, 10.0, 7.8) if p[1] <= cy - 3}
    solid(cv, dome, "R", "T", shade_off=(1, 1))
    for k in range(0, 13, 4):
        cv.put(cx - 6 + k, int(cy) - 6, "W")  # bintik putih
    kx, ky = cx + 9, int(cy) - 4
    solid(cv, chain([(kx, ky), (kx + 3, ky + 2 + flap), (kx + 5, ky + 1 + 2 * flap)], 0.9), "R", None)


def powder_keg(cv, x, y):
    """Tong mesiu kecil 5x6 di sabuk (tertutup, tanpa sumbu menyala)."""
    solid(cv, rect(x, y, 5, 6), "X", "x", shade_off=(1, 1))
    cv.fill({(x + dx, y + 1) for dx in range(1, 4)} | {(x + dx, y + 4) for dx in range(1, 4)}, "N")


def rope(cv, x, y1):
    """Tali dari tepi atas kanvas sampai y1."""
    cv.fill({(x, y) for y in range(0, y1 + 1)} | {(x + 1, y) for y in range(0, y1 + 1) if y % 3 == 0}, "c")


def rifle(cv, hx, hy, deg, length=20):
    """Senapan panjang sebagai prop: popor kayu dan laras panjang. Tanpa kilatan atau asap laras."""
    a = math.radians(deg)
    ux, uy = math.cos(a), -math.sin(a)
    solid(cv, capsule((hx - ux * 4, hy - uy * 4), (hx + ux * 3, hy + uy * 3), 1.3), "X", "x", shade_off=(1, 1))
    cv.fill(capsule((hx + ux * 3, hy + uy * 3), (hx + ux * length, hy + uy * length), 0.6), "l")


def hammer(cv, hx, hy, deg, length=11):
    """Palu besar: gagang kayu panjang dan kepala baja balok."""
    a = math.radians(deg)
    ux, uy = math.cos(a), -math.sin(a)
    tip = (hx + ux * length, hy + uy * length)
    cv.fill(capsule((hx - ux * 2, hy - uy * 2), tip, 0.8), "N")
    px, py = -uy, ux
    headm = capsule((tip[0] - px * 3.5, tip[1] - py * 3.5), (tip[0] + px * 3.5, tip[1] + py * 3.5), 2.0)
    solid(cv, headm, "s", "g", shade_off=(1, 1))


def anchor(cv, x, y, big=1.0):
    """Jangkar baja: cincin, batang, palang, dan dua lengan melengkung. (x, y) = cincin di atas."""
    s = big
    shank = capsule((x, y + 2 * s), (x, y + 12 * s), 1.0)
    bar = capsule((x - 3 * s, y + 4 * s), (x + 3 * s, y + 4 * s), 0.8)
    arms = chain([(x - 6 * s, y + 8 * s), (x - 5 * s, y + 11 * s), (x, y + 12.5 * s), (x + 5 * s, y + 11 * s), (x + 6 * s, y + 8 * s)], 1.0)
    ring = ellipse(x, y, 2.0, 2.0) - ellipse(x, y, 0.7, 0.7)
    solid(cv, shank | bar | arms | ring, "G", "s", shade_off=(1, 1))


# ================================================================== badan varian
def knight_look(tabard, shade, pauldrons=False, arms=MAIL, helmet="open"):
    def look(cv, t, n, eyes, brows, mouth, dx=0, bob=0):
        tail(cv, (CX - 7 + dx, TOP + 14 + bob), phase=wag(t, n), flip=-1, length=8)
        if helmet == "hood":
            hood(cv, CX + dx, CY + bob, back=True)
        torso = dressed_body(cv, CX + dx, TOP + bob, "G" if helmet != "hood" else "l", "s" if helmet != "hood" else "L",
                             pants="s" if helmet != "hood" else "L", pants_shade="g" if helmet != "hood" else "q")
        tab = {(x, y) for (x, y) in inner(torso) if y >= TOP + bob + 2} | rect(CX + dx - 4, TOP + bob + 10, 9, 4)
        solid(cv, tab, tabard, shade, shade_off=(1, 1))
        cv.fill({(CX + dx - 1, TOP + bob + 4), (CX + dx, TOP + bob + 4), (CX + dx - 1, TOP + bob + 5), (CX + dx, TOP + bob + 5)}, "O")
        head(cv, CX + dx, CY + bob, eyes=eyes, brows=brows, mouth=mouth)
        if helmet == "open":
            open_helmet(cv, CX + dx, CY + bob)
        elif helmet == "hood":
            hood(cv, CX + dx, CY + bob, back=False)
        if pauldrons:
            for s in (-1, 1):
                pauldron(cv, CX + dx + s * 8, TOP + bob + 2)
    look.arms = arms
    return look


def viking_look(vest, shade, helmet=True, mantle=False, chest="B"):
    def look(cv, t, n, eyes, brows, mouth, dx=0, bob=0):
        tail(cv, (CX - 7 + dx, TOP + 14 + bob), phase=wag(t, n), flip=-1, length=8)
        if mantle:
            sitting_body(cv, CX + dx, TOP + bob)
            fur_mantle(cv, CX + dx, TOP + bob)
        else:
            torso = dressed_body(cv, CX + dx, TOP + bob, vest, shade, pants="x", pants_shade="e")
            cv.fill({(x, y) for (x, y) in inner(torso) if y <= TOP + bob + 3 and abs(x - CX - dx + 0.5) <= 3.5 - (y - TOP - bob)}, chest)
            cv.fill({(x, TOP + bob + 9) for x in range(CX + dx - 7, CX + dx + 8) if (x, TOP + bob + 9) in inner(torso)}, "N")
            cv.fill(rect(CX + dx - 1, TOP + bob + 9, 2, 1), "O")
        head(cv, CX + dx, CY + bob, eyes=eyes, brows=brows, mouth=mouth)
        if helmet:
            horned_helmet(cv, CX + dx, CY + bob)
        else:
            fur_headband(cv, CX + dx, CY + bob)
    look.arms = "B"
    return look


def pirate_look(coat, shade, hat="tricorn", stripes=None, straps=False):
    def look(cv, t, n, eyes, brows, mouth, dx=0, bob=0, hat_on=True):
        tail(cv, (CX - 7 + dx, TOP + 14 + bob), phase=wag(t, n), flip=-1, length=8)
        torso = dressed_body(cv, CX + dx, TOP + bob, coat, shade, pants="L", pants_shade="q")
        body = inner(torso)
        if stripes:
            cv.fill({(x, y) for (x, y) in body if (y - TOP - bob) % 3 == 1}, stripes)
        else:
            cv.fill({(CX + dx - 1, TOP + bob), (CX + dx, TOP + bob), (CX + dx - 1, TOP + bob + 1), (CX + dx, TOP + bob + 1)}, "C")
        cv.fill({(x, TOP + bob + 8) for x in range(CX + dx - 8, CX + dx + 9) if (x, TOP + bob + 8) in body}, "L")
        cv.fill(rect(CX + dx - 1, TOP + bob + 8, 2, 1), "O")
        if straps:  # dua sabuk kulit lebar menyilang di dada (aksesori besar, proporsi Gobyet tetap)
            for s in (-1, 1):
                cv.fill({(x, y) for (x, y) in body for w in (0, 1, 2) if x - CX - dx == s * (y - TOP - bob - 4) + w - 1 and y <= TOP + bob + 8}, "e")
            cv.fill(rect(CX + dx - 2, TOP + bob + 3, 4, 3), "O")
        head(cv, CX + dx, CY + bob, eyes=eyes, brows=brows, mouth=mouth)
        if not hat_on:
            return
        if hat == "tricorn":
            tricorn(cv, CX + dx, CY + bob)
        elif hat == "captain":
            captain_hat(cv, CX + dx, CY + bob)
        elif hat == "bandana":
            bandana(cv, CX + dx, CY + bob, flap=(t // 2) % 2)
    look.arms = coat
    return look


# ================================================================== pola frame bersama
def frame_idle(look, props, blink_at=7):
    """idle: pose baku dengan prop kelas, angguk kecil di f4-f5 dan f10-f11, kedip di blink_at."""
    def fn(i):
        cv = Canvas()
        t = i % IDLE_N
        bob = 1 if t in (4, 5, 10, 11) else 0
        look(cv, t, IDLE_N, "blink" if t == blink_at else "look", "flat", "smile", bob=bob)
        props(cv, t, bob)
        return cv
    return fn


def frame_attack(look, strike, seq=ATTACK):
    def fn(i):
        cv = Canvas()
        t = i % ATTACK_N
        pos, k = seq[t]
        look(cv, t, ATTACK_N, *FACE[pos], bob=1 if pos == "hit" and k in (1, 2) else 0)
        strike(cv, t, pos, k)
        return cv
    return fn


def frame_victory(look, cheer, low=0):
    def fn(i):
        cv = Canvas()
        t = i % VICTORY_N
        phase, hop = VICTORY[t]
        up = phase == "up"
        look(cv, t, VICTORY_N, "happy" if up else "look", "flat", ("o" if t % 2 else "smile") if up else "smile", bob=low - hop)
        cheer(cv, t, phase, hop)
        return cv
    return fn


def rest_arm_left(cv, fur, bob=0):
    arm(cv, (CX - 7, TOP + 3 + bob), (CX - 7, TOP + 9 + bob), elbow=(CX - 12, TOP + 6 + bob), fur=fur)


# ================================================================== Knights
HEAVY = knight_look("z", "1", pauldrons=True, arms="G")


def heavy_idle(cv, t, bob):
    """Pedang besar berdiri di sisi kanan (ujung di lantai), tangan kanan di gagang. Tidak dipegang di depan
    badan: bilah tegak dengan pelindung tangan di depan dada bisa terbaca seperti salib."""
    greatsword(cv, CX + 14, TOP - 1, -90, length=17)
    rest_arm_left(cv, "G", bob)
    arm(cv, (CX + 7, TOP + 3 + bob), (CX + 14, TOP - 1), elbow=(CX + 12, TOP + 5 + bob), fur="G")
    for s in (-1, 1):
        pauldron(cv, CX + s * 8, TOP + 2 + bob)


def heavy_strike(cv, t, pos, k):
    """Pedang besar diangkat dua tangan lalu ditancapkan ke lantai, debu tebal."""
    if pos == "rest":
        heavy_idle(cv, t, 0)
        return
    if pos in ("rise", "up"):
        hy = TOP - 2 if pos == "rise" else TOP - 6
        greatsword(cv, CX + 14, hy, 90, length=14)
        arm(cv, (CX - 7, TOP + 3), (CX + 13, hy + 2), elbow=(CX + 2, TOP + 6), fur="G")
        arm(cv, (CX + 7, TOP + 3), (CX + 14, hy), elbow=(CX + 14, TOP + 3), fur="G")
    else:
        greatsword(cv, CX + 12, TOP + 2, -90, length=15)
        arm(cv, (CX - 7, TOP + 3), (CX + 11, TOP + 2), elbow=(CX - 2, TOP + 9), fur="G")
        arm(cv, (CX + 7, TOP + 3), (CX + 12, TOP + 3), elbow=(CX + 11, TOP + 7), fur="G")
        if k:
            dust(cv, CX + 12, TOP + 16, k - 1)
            dust(cv, CX + 12, TOP + 15, k)
            spark_lines(cv, CX + 17, TOP + 9)
    for s in (-1, 1):
        pauldron(cv, CX + s * 8, TOP + 2)


def heavy_cheer(cv, t, phase, hop):
    """Pedang besar terangkat dua tangan; tiap mendarat, debu hentakan besar menyembur di kedua sisi (khas)."""
    b = -hop
    if phase == "rest":
        heavy_idle(cv, t, 0)
        return
    hy = TOP - 3 + b if phase == "rise" else TOP - 6 + b
    greatsword(cv, CX + 14, hy, 90, length=15 if phase == "up" else 12)
    arm(cv, (CX - 7, TOP + 3 + b), (CX + 13, hy + 2), elbow=(CX + 2, TOP + 6 + b), fur="G")
    arm(cv, (CX + 7, TOP + 3 + b), (CX + 14, hy), elbow=(CX + 14, TOP + 3 + b), fur="G")
    for s in (-1, 1):
        pauldron(cv, CX + s * 8, TOP + 2 + b)
    if phase == "up" and hop == 0:
        for s in (-1, 1):
            puff(cv, CX + s * 15, TOP + 15, 2.2)
            puff(cv, CX + s * 19, TOP + 13, 1.6)


ARCHER = knight_look("v", "k")


def archer_idle(cv, t, bob):
    quiver(cv, CX - 12, TOP - 4 + bob)
    longbow(cv, CX - 14, TOP - 8 + bob, TOP + 15 + bob)
    arm(cv, (CX - 7, TOP + 3 + bob), (CX - 14, TOP + 3 + bob), elbow=(CX - 12, TOP + 7 + bob), fur=MAIL)
    arm(cv, (CX + 7, TOP + 3 + bob), (CX + 7, TOP + 9 + bob), elbow=(CX + 12, TOP + 6 + bob), fur=MAIL)


def archer_strike(cv, t, pos, k):
    """Membidik papan sasaran bulat di kanan (tidak melepas anak panah): busur mendatar tidak dipakai; busur tegak
    di tangan kanan terentang ke arah sasaran, tangan kiri menarik tali ke dekat dagu."""
    quiver(cv, CX - 12, TOP - 4)
    target_board(cv, 57, TOP - 6)
    if pos == "rest":
        longbow(cv, CX - 14, TOP - 8, TOP + 15)
        arm(cv, (CX - 7, TOP + 3), (CX - 14, TOP + 3), elbow=(CX - 12, TOP + 7), fur=MAIL)
        arm(cv, (CX + 7, TOP + 3), (CX + 7, TOP + 9), elbow=(CX + 12, TOP + 6), fur=MAIL)
        return
    draw = {"rise": 0, "draw": 3, "aim": 5}[pos]
    bx = CX + 18
    longbow(cv, bx, TOP - 14, TOP + 6, draw=draw, bend=-3)
    arm(cv, (CX + 7, TOP + 3), (bx, TOP - 4), elbow=(CX + 13, TOP), fur=MAIL)
    if draw:
        arrow_nocked(cv, bx + draw - 9, bx + 1, TOP - 4)
        arm(cv, (CX - 7, TOP + 3), (bx + draw - 9, TOP - 4), elbow=(CX - 8, TOP - 1), fur=MAIL)
    else:
        rest_arm_left(cv, MAIL)
    if pos == "aim" and k in (2, 3):
        cv.fill({(46, TOP - 11), (47, TOP - 12)}, "K")  # garis fokus kecil di atas busur


def archer_cheer(cv, t, phase, hop):
    """Busur terangkat; bintang emas berkedip di tengah papan sasaran di samping (khas)."""
    b = -hop
    quiver(cv, CX - 12, TOP - 4 + b)
    target_board(cv, 57, TOP - 4, star_on=phase == "up" and (t // 2) % 2 == 0)
    if phase == "rest":
        longbow(cv, CX - 14, TOP - 8, TOP + 15)
        arm(cv, (CX - 7, TOP + 3), (CX - 14, TOP + 3), elbow=(CX - 12, TOP + 7), fur=MAIL)
        arm(cv, (CX + 7, TOP + 3), (CX + 7, TOP + 9), elbow=(CX + 12, TOP + 6), fur=MAIL)
        return
    hy = TOP - 4 + b if phase == "rise" else TOP - 9 + b
    longbow(cv, CX - 15, hy - 11, hy + 9, bend=3)
    arm(cv, (CX - 7, TOP + 3 + b), (CX - 15, hy), elbow=(CX - 14, TOP + 1 + b), fur=MAIL)
    arm(cv, (CX + 7, TOP + 3 + b), (CX + 13, TOP - 4 + b), elbow=(CX + 13, TOP + 1 + b), fur=MAIL)


MANATARMS = knight_look("J", "w")


def manatarms_idle(cv, t, bob):
    halberd(cv, CX - 14, TOP + 15, length=27)
    arm(cv, (CX - 7, TOP + 3 + bob), (CX - 14, TOP + 4 + bob), elbow=(CX - 12, TOP + 8 + bob), fur=MAIL)
    mace(cv, CX + 11, TOP + 8 + bob, -60, length=7)
    arm(cv, (CX + 7, TOP + 3 + bob), (CX + 11, TOP + 8 + bob), elbow=(CX + 12, TOP + 5 + bob), fur=MAIL)


def manatarms_strike(cv, t, pos, k):
    """Gada dihantamkan ke papan kayu di lantai kanan: serpihan kayu dan garis hentakan."""
    plank(cv, CX + 12, TOP + 13)
    halberd(cv, CX - 14, TOP + 15, length=27)
    arm(cv, (CX - 7, TOP + 3), (CX - 14, TOP + 4), elbow=(CX - 12, TOP + 8), fur=MAIL)
    if pos == "rest":
        mace(cv, CX + 11, TOP + 8, -60, length=7)
        arm(cv, (CX + 7, TOP + 3), (CX + 11, TOP + 8), elbow=(CX + 12, TOP + 5), fur=MAIL)
    elif pos in ("rise", "up"):
        hy = TOP - 2 if pos == "rise" else TOP - 7
        mace(cv, CX + 13, hy, 95, length=8)
        arm(cv, (CX + 7, TOP + 3), (CX + 13, hy), elbow=(CX + 14, TOP + 3), fur=MAIL)
    else:
        mace(cv, CX + 12, TOP + 5, -55, length=8)
        arm(cv, (CX + 7, TOP + 3), (CX + 12, TOP + 5), elbow=(CX + 12, TOP + 8), fur=MAIL)
        if k:
            for j, (ox, oy) in enumerate(((1, -2), (8, -3), (12, -1))):
                cv.put(CX + 12 + ox + (k - 1) * (1 if j else -1), TOP + 12 + oy - k, "X")
            spark_lines(cv, CX + 22, TOP + 6)


def manatarms_cheer(cv, t, phase, hop):
    """Halberd diputar di atas kepala dengan garis busur putaran melingkar (khas); gada terangkat."""
    b = -hop
    if phase == "rest":
        manatarms_idle(cv, t, 0)
        return
    hy = TOP - 3 + b if phase == "rise" else TOP - 8 + b
    mace(cv, CX + 13, hy, 95, length=8)
    arm(cv, (CX + 7, TOP + 3 + b), (CX + 13, hy), elbow=(CX + 14, TOP + 1 + b), fur=MAIL)
    ang = [120, 75, 30, 165][t % 4] if phase == "up" else 100
    a = math.radians(ang)
    hx, hy2 = CX - 14, TOP - 6 + b
    length = 13
    x0, y0 = hx - math.cos(a) * length, hy2 + math.sin(a) * length
    x1, y1 = hx + math.cos(a) * length, hy2 - math.sin(a) * length
    cv.fill(capsule((x0, y0), (x1, y1), 0.7), "N")
    solid(cv, ellipse(x1, y1, 1.8, 1.8), "G", None)
    arm(cv, (CX - 7, TOP + 3 + b), (int(hx), int(hy2)), elbow=(CX - 13, TOP + 1 + b), fur=MAIL)
    if phase == "up":  # jejak busur putaran di belakang kedua ujung halberd
        for end in (0, 180):
            for k in (18, 32, 46):
                r = math.radians(ang + end - k)
                cv.put(int(round(hx + math.cos(r) * 14)), int(round(hy2 - math.sin(r) * 14)), "s" if k > 18 else "K")


ASSASSIN = knight_look("l", "L", helmet="hood", arms="l")


def assassin_idle(cv, t, bob):
    smoke_bomb(cv, CX + 5, TOP + 10 + bob)
    arm(cv, (CX - 7, TOP + 3 + bob), (CX - 7, TOP + 9 + bob), elbow=(CX - 12, TOP + 6 + bob), fur="l")
    dagger(cv, CX + 12, TOP + 7 + bob, -60)
    arm(cv, (CX + 7, TOP + 3 + bob), (CX + 12, TOP + 7 + bob), elbow=(CX + 12, TOP + 4 + bob), fur="l")


def assassin_strike(cv, t, pos, k):
    """Belati terangkat ke atas dengan kepulan asap kecil di kaki (tidak diarahkan ke siapa pun)."""
    smoke_bomb(cv, CX + 5, TOP + 10)
    arm(cv, (CX - 7, TOP + 3), (CX - 7, TOP + 9), elbow=(CX - 12, TOP + 6), fur="l")
    if pos == "rest":
        dagger(cv, CX + 12, TOP + 7, -60)
        arm(cv, (CX + 7, TOP + 3), (CX + 12, TOP + 7), elbow=(CX + 12, TOP + 4), fur="l")
        return
    hy = TOP - 1 if pos == "rise" else TOP - 7
    dagger(cv, CX + 13, hy, 90, length=7)
    arm(cv, (CX + 7, TOP + 3), (CX + 13, hy), elbow=(CX + 14, TOP + 2), fur="l")
    if pos == "hit" and k:
        for s in (-1, 1):
            puff(cv, CX + s * (8 + k), TOP + 15 - k // 2, 1.4 + k * 0.4)


def assassin_cheer(cv, t, phase, hop):
    """Belati terangkat; cincin asap berongga naik dan membesar dari bom asap di sabuk (khas)."""
    b = -hop
    smoke_bomb(cv, CX + 5, TOP + 10 + b)
    if phase == "rest":
        arm(cv, (CX - 7, TOP + 3), (CX - 7, TOP + 9), elbow=(CX - 12, TOP + 6), fur="l")
        dagger(cv, CX + 12, TOP + 7, -60)
        arm(cv, (CX + 7, TOP + 3), (CX + 12, TOP + 7), elbow=(CX + 12, TOP + 4), fur="l")
        return
    hy = TOP - 3 + b if phase == "rise" else TOP - 8 + b
    dagger(cv, CX + 13, hy, 90, length=7)
    arm(cv, (CX + 7, TOP + 3 + b), (CX + 13, hy), elbow=(CX + 14, TOP + 1 + b), fur="l")
    arm(cv, (CX - 7, TOP + 3 + b), (CX - 13, TOP - 4 + b), elbow=(CX - 13, TOP + 1 + b), fur="l")
    if phase == "up":
        k = (t - 2) % 5
        smoke_ring(cv, CX - 17, TOP + 6 - k * 3, 1.8 + k * 0.7)


# ================================================================== Vikings
BERSERKER = viking_look("D", "K", helmet=False, mantle=True)


def two_axes(cv, lx, ly, ldeg, rx, ry, rdeg, bob=0):
    axe(cv, lx, ly + bob, ldeg, length=10)
    axe(cv, rx, ry + bob, rdeg, length=10)


def berserker_idle(cv, t, bob):
    two_axes(cv, CX - 11, TOP + 7, 110, CX + 11, TOP + 7, 70, bob)
    arm(cv, (CX - 7, TOP + 3 + bob), (CX - 11, TOP + 7 + bob), elbow=(CX - 12, TOP + 4 + bob))
    arm(cv, (CX + 7, TOP + 3 + bob), (CX + 11, TOP + 7 + bob), elbow=(CX + 12, TOP + 4 + bob))


def berserker_look(cv, t, n, eyes, brows, mouth, dx=0, bob=0):
    """Mata melebar (amuk kartun) di semua pose kecuali kedip dan senang."""
    BERSERKER(cv, t, n, "wide" if eyes == "look" else eyes, brows, mouth, dx=dx, bob=bob)


def berserker_strike(cv, t, pos, k):
    """Dua kapak dihentak bersamaan ke balok kayu di lantai, serpihan kayu, "!"."""
    log_block(cv, CX - 6, TOP + 13)
    if pos == "rest":
        berserker_idle(cv, t, 0)
        return
    if pos in ("rise", "up"):
        hy = TOP - 2 if pos == "rise" else TOP - 7
        two_axes(cv, CX - 12, hy, 95, CX + 12, hy, 85)
        arm(cv, (CX - 7, TOP + 3), (CX - 12, hy), elbow=(CX - 13, TOP + 3))
        arm(cv, (CX + 7, TOP + 3), (CX + 12, hy), elbow=(CX + 13, TOP + 3))
    else:
        two_axes(cv, CX - 9, TOP + 6, -60, CX + 9, TOP + 6, -120)
        arm(cv, (CX - 7, TOP + 3), (CX - 9, TOP + 6), elbow=(CX - 12, TOP + 7))
        arm(cv, (CX + 7, TOP + 3), (CX + 9, TOP + 6), elbow=(CX + 12, TOP + 7))
        if k:
            for j, ox in enumerate((-8, -2, 5, 11)):
                cv.put(CX + ox + (k - 1) * (1 if j % 2 else -1), TOP + 11 - k, "X")
            bubble(cv, 50, 2, 9, 9, fill="R", tail_dir=-1)
            mini_text(cv, "!", 52, 4, "W")


def berserker_cheer(cv, t, phase, hop):
    """Dua kapak diadu di atas kepala dengan percikan kilau di titik temu (khas)."""
    b = -hop
    if phase == "rest":
        berserker_idle(cv, t, 0)
        return
    hy = TOP - 3 + b if phase == "rise" else TOP - 8 + b
    two_axes(cv, CX - 10, hy, 60, CX + 10, hy, 120)
    arm(cv, (CX - 7, TOP + 3 + b), (CX - 10, hy), elbow=(CX - 13, TOP + 1 + b))
    arm(cv, (CX + 7, TOP + 3 + b), (CX + 10, hy), elbow=(CX + 13, TOP + 1 + b))
    if phase == "up" and t % 2 == 0:
        cx_, cy_ = CX, hy - 10
        for dx, dy in ((-3, 0), (3, 0), (0, -3), (-2, -2), (2, -2)):
            cv.put(cx_ + dx, cy_ + dy, "Y")
        cv.put(cx_, cy_, "W")


HUSCARL = viking_look("s", "g")


def huscarl_idle(cv, t, bob):
    round_shield(cv, CX - 15, TOP + 6)
    arm(cv, (CX - 7, TOP + 3 + bob), (CX - 12, TOP + 8 + bob), elbow=(CX - 12, TOP + 4 + bob))
    axe(cv, CX + 12, TOP + 14, 90, length=16, big=True)
    arm(cv, (CX + 7, TOP + 3 + bob), (CX + 12, TOP + 5 + bob), elbow=(CX + 12, TOP + 8 + bob))


def huscarl_strike(cv, t, pos, k):
    """Kapak besar dua tangan dihantamkan ke balok kayu di kanan."""
    log_block(cv, CX + 11, TOP + 13)
    round_shield(cv, CX - 17, TOP + 7)
    if pos == "rest":
        huscarl_idle(cv, t, 0)
        return
    if pos in ("rise", "up"):  # dua tangan di sisi kanan, lengan kiri melintang di dada (bukan di depan wajah)
        hy = TOP + 1 if pos == "rise" else TOP - 3
        axe(cv, CX + 11, hy, 95, length=14, big=True)
        arm(cv, (CX - 7, TOP + 3), (CX + 9, hy + 4), elbow=(CX - 1, TOP + 8))
        arm(cv, (CX + 7, TOP + 3), (CX + 11, hy), elbow=(CX + 13, TOP + 5))
    else:
        axe(cv, CX + 7, TOP + 3, -30, length=13, big=True)
        arm(cv, (CX - 7, TOP + 3), (CX + 5, TOP + 4), elbow=(CX - 2, TOP + 9))
        arm(cv, (CX + 7, TOP + 3), (CX + 7, TOP + 3), elbow=(CX + 10, TOP + 7))
        if k:
            for j, (ox, oy) in enumerate(((2, -2), (7, -3), (11, -1))):
                cv.put(CX + 11 + ox + (k - 1) * (1 if j else -1), TOP + 12 + oy - k, "X")


def huscarl_cheer(cv, t, phase, hop):
    """Perisai diangkat dan dipukul pelan dengan gagang kapak: garis bunyi melengkung di sekitar perisai (khas)."""
    b = -hop
    if phase == "rest":
        huscarl_idle(cv, t, 0)
        return
    sy = TOP - 2 + b if phase == "rise" else TOP - 5 + b
    round_shield(cv, CX - 15, sy)
    arm(cv, (CX - 7, TOP + 3 + b), (CX - 13, sy + 3), elbow=(CX - 13, TOP + 3 + b))
    beat = phase == "up" and t % 2 == 0
    axe(cv, CX + 13, TOP + 1 + b, 80 if beat else 95, length=13, big=True)
    arm(cv, (CX + 7, TOP + 3 + b), (CX + 13, TOP + 1 + b), elbow=(CX + 13, TOP + 6 + b))
    if beat:
        for r in (8.5, 11.0):
            for k in range(-3, 4):
                a = math.radians(180 + k * 14)
                cv.put(int(round(CX - 15 + math.cos(a) * r)), int(round(sy + math.sin(a) * r)), "K")


GESTIR = viking_look("k", "K")


def gestir_idle(cv, t, bob):
    javelin(cv, CX + 12, TOP + 15, length=26)
    arm(cv, (CX + 7, TOP + 3 + bob), (CX + 12, TOP + 4 + bob), elbow=(CX + 12, TOP + 8 + bob))
    rest_arm_left(cv, "B", bob)


def gestir_strike(cv, t, pos, k):
    """Tombak lempar diangkat lalu ditancapkan tegak ke lantai (dipegang, tidak dilempar), debu piksel."""
    if pos == "rest":
        gestir_idle(cv, t, 0)
        return
    rest_arm_left(cv, "B")
    if pos in ("rise", "up"):
        lift = 5 if pos == "rise" else 10
        javelin(cv, CX + 13, TOP + 15 - lift, length=26)
        arm(cv, (CX + 7, TOP + 3), (CX + 13, TOP + 4 - lift), elbow=(CX + 14, TOP + 2))
    else:
        javelin(cv, CX + 14, TOP + 17, length=26)
        arm(cv, (CX + 7, TOP + 3), (CX + 14, TOP + 3), elbow=(CX + 12, TOP + 7))
        if k:
            dust(cv, CX + 14, TOP + 16, k - 1)
            spark_lines(cv, CX + 18, TOP + 9)


def gestir_cheer(cv, t, phase, hop):
    """Tombak lempar diseimbangkan tegak di ujung jari kanan, bergoyang kiri-kanan; tangan kiri terentang
    menjaga keseimbangan (khas)."""
    b = -hop
    if phase == "rest":
        gestir_idle(cv, t, 0)
        return
    hx, hy = CX + 13, TOP - 2 + b
    if phase == "rise":
        javelin(cv, CX + 13, TOP + 13, length=26)
        arm(cv, (CX + 7, TOP + 3 + b), (CX + 13, TOP + 2 + b), elbow=(CX + 13, TOP + 7 + b))
        rest_arm_left(cv, "B", b)
        return
    wob = (-8, 0, 8, 0)[t % 4]
    javelin(cv, hx, hy - 1, length=15, deg=90 + wob)
    arm(cv, (CX + 7, TOP + 3 + b), (hx, hy + 1), elbow=(CX + 13, TOP + 3 + b))
    arm(cv, (CX - 7, TOP + 3 + b), (CX - 17, TOP + 1 + b), elbow=(CX - 12, TOP + 5 + b))
    for s in (-1, 1):  # garis goyang di kedua sisi ujung tombak
        if (wob > 0) == (s > 0) and wob:
            cv.fill({(hx + s * 5, hy - 12), (hx + s * 5, hy - 11)}, "K")


BONDI = viking_look("d", "e")


def short_bow_rest(cv, bob):
    longbow(cv, CX - 13, TOP - 1 + bob, TOP + 13 + bob, bend=2)


def bondi_idle(cv, t, bob):
    seax(cv, CX + 2, TOP + 9 + bob)
    short_bow_rest(cv, bob)
    arm(cv, (CX - 7, TOP + 3 + bob), (CX - 13, TOP + 6 + bob), elbow=(CX - 12, TOP + 8 + bob))
    arm(cv, (CX + 7, TOP + 3 + bob), (CX + 7, TOP + 9 + bob), elbow=(CX + 12, TOP + 6 + bob))


def bondi_strike(cv, t, pos, k):
    """Membidik papan sasaran bulat di kanan dengan busur pendek (tidak melepas anak panah)."""
    seax(cv, CX + 2, TOP + 9)
    target_board(cv, 57, TOP - 3)
    if pos == "rest":
        short_bow_rest(cv, 0)
        arm(cv, (CX - 7, TOP + 3), (CX - 13, TOP + 6), elbow=(CX - 12, TOP + 8))
        arm(cv, (CX + 7, TOP + 3), (CX + 7, TOP + 9), elbow=(CX + 12, TOP + 6))
        return
    draw = {"rise": 0, "draw": 2, "aim": 4}[pos]
    bx = CX + 17
    longbow(cv, bx, TOP - 8, TOP + 6, draw=draw, bend=-2)
    arm(cv, (CX + 7, TOP + 3), (bx, TOP - 1), elbow=(CX + 13, TOP + 2))
    if draw:
        arrow_nocked(cv, bx + draw - 8, bx + 1, TOP - 1)
        arm(cv, (CX - 7, TOP + 3), (bx + draw - 8, TOP - 1), elbow=(CX - 8, TOP + 1))
    else:
        rest_arm_left(cv, "B")


def bondi_cheer(cv, t, phase, hop):
    """Busur pendek terangkat dan talinya dipetik: garis getar tali berganti sisi (khas)."""
    b = -hop
    seax(cv, CX + 2, TOP + 9 + b)
    if phase == "rest":
        bondi_idle(cv, t, 0)
        return
    hy = TOP - 3 + b if phase == "rise" else TOP - 8 + b
    bx = CX - 14
    longbow(cv, bx, hy - 7, hy + 7, bend=2, draw=(1 if t % 2 else -1) if phase == "up" else 0)
    arm(cv, (CX - 7, TOP + 3 + b), (bx, hy), elbow=(CX - 14, TOP + 2 + b))
    arm(cv, (CX + 7, TOP + 3 + b), (CX + 13, TOP - 4 + b), elbow=(CX + 13, TOP + 1 + b))
    if phase == "up":
        for s in (-1, 1):
            cv.fill({(bx + s * 3, hy - 2), (bx + s * 4, hy), (bx + s * 3, hy + 2)} if (t // 2) % 2 == (s > 0) else set(), "K")


# ================================================================== Pirates
CAPTAIN = pirate_look("w", "L", hat="captain")


def captain_idle(cv, t, bob):
    blunderbuss(cv, CX - 12, TOP + 6 + bob, -80)
    arm(cv, (CX - 7, TOP + 3 + bob), (CX - 12, TOP + 6 + bob), elbow=(CX - 12, TOP + 3 + bob), fur="w")
    cutlass(cv, CX + 13, TOP + 4 + bob, -100, length=11)
    arm(cv, (CX + 7, TOP + 3 + bob), (CX + 13, TOP + 4 + bob), elbow=(CX + 12, TOP + 8 + bob), fur="w")


def captain_strike(cv, t, pos, k):
    """Cutlass ditancapkan ke papan kayu, blunderbuss tetap dipegang menunduk ke lantai. TANPA tembakan."""
    plank(cv, CX + 11, TOP + 13)
    blunderbuss(cv, CX - 12, TOP + 6, -80)
    arm(cv, (CX - 7, TOP + 3), (CX - 12, TOP + 6), elbow=(CX - 12, TOP + 3), fur="w")
    if pos == "rest":
        cutlass(cv, CX + 13, TOP + 4, -100, length=11)
        arm(cv, (CX + 7, TOP + 3), (CX + 13, TOP + 4), elbow=(CX + 12, TOP + 8), fur="w")
    elif pos in ("rise", "up"):
        hy = TOP - 2 if pos == "rise" else TOP - 7
        cutlass(cv, CX + 13, hy, 85, length=11)
        arm(cv, (CX + 7, TOP + 3), (CX + 13, hy), elbow=(CX + 14, TOP + 3), fur="w")
    else:
        cutlass(cv, CX + 16, TOP + 3, -80, length=10)
        arm(cv, (CX + 7, TOP + 3), (CX + 16, TOP + 3), elbow=(CX + 12, TOP + 7), fur="w")
        if k:
            for j, (ox, oy) in enumerate(((1, -2), (8, -3), (12, -1))):
                cv.put(CX + 11 + ox + (k - 1) * (1 if j else -1), TOP + 12 + oy - k, "X")
    if pos == "hit" and k:
        bubble(cv, 50, 2, 9, 9, fill="R", tail_dir=-1)
        mini_text(cv, "!", 52, 4, "W")


def captain_cheer(cv, t, phase, hop):
    """Cutlass terangkat; burung beo terbang hinggap di bahu kiri dan mengepakkan sayap (khas)."""
    b = -hop
    blunderbuss(cv, CX - 12, TOP + 6 + b, -80)
    arm(cv, (CX - 7, TOP + 3 + b), (CX - 12, TOP + 6 + b), elbow=(CX - 12, TOP + 3 + b), fur="w")
    if phase == "rest":
        cutlass(cv, CX + 13, TOP + 4, -100, length=11)
        arm(cv, (CX + 7, TOP + 3), (CX + 13, TOP + 4), elbow=(CX + 12, TOP + 8), fur="w")
    else:
        hy = TOP - 3 + b if phase == "rise" else TOP - 8 + b
        cutlass(cv, CX + 14, hy, 80, length=11)
        arm(cv, (CX + 7, TOP + 3 + b), (CX + 14, hy), elbow=(CX + 14, TOP + 1 + b), fur="w")
    land = {1: (4, 4), 2: (3, 2), 3: (2, 1)}
    if phase == "up" or t in land:
        ox, oy = land.get(t, (0, 0))
        parrot(cv, CX - 13 - ox, TOP - 3 + b - oy, flap=1 if t in land or t % 2 == 0 else 0)


SKIRMISHER = pirate_look("W", "h", hat="bandana", stripes="R")


def skirmisher_idle(cv, t, bob):
    powder_keg(cv, CX + 2, TOP + 9 + bob)
    rest_arm_left(cv, "W", bob)
    sword(cv, CX + 12, TOP + 6 + bob, -80, length=11)
    arm(cv, (CX + 7, TOP + 3 + bob), (CX + 12, TOP + 6 + bob), elbow=(CX + 12, TOP + 3 + bob), fur="W")


def skirmisher_strike(cv, t, pos, k):
    """Pedang dihantamkan ke papan kayu di lantai dengan lompatan kecil (badan naik 2 px saat mengangkat)."""
    plank(cv, CX + 11, TOP + 13)
    powder_keg(cv, CX + 2, TOP + 9)
    rest_arm_left(cv, "W")
    if pos == "rest":
        sword(cv, CX + 12, TOP + 6, -80, length=11)
        arm(cv, (CX + 7, TOP + 3), (CX + 12, TOP + 6), elbow=(CX + 12, TOP + 3), fur="W")
    elif pos in ("rise", "up"):
        hy = TOP - 2 if pos == "rise" else TOP - 7
        sword(cv, CX + 13, hy, 90, length=11)
        arm(cv, (CX + 7, TOP + 3), (CX + 13, hy), elbow=(CX + 14, TOP + 3), fur="W")
    else:
        sword(cv, CX + 13, TOP + 4, -40, length=11)
        arm(cv, (CX + 7, TOP + 3), (CX + 13, TOP + 4), elbow=(CX + 12, TOP + 7), fur="W")
        if k:
            spark_lines(cv, CX + 24, TOP + 6)
            for j, (ox, oy) in enumerate(((2, -2), (9, -3))):
                cv.put(CX + 11 + ox + (k - 1) * (1 if j else -1), TOP + 12 + oy - k, "X")


def skirmisher_hop_look(cv, t, n, eyes, brows, mouth, dx=0, bob=0):
    pos = ATTACK[t % ATTACK_N][0]
    SKIRMISHER(cv, t, n, eyes, brows, mouth, dx=dx, bob=bob - (2 if pos == "up" else 0))


def skirmisher_cheer(cv, t, phase, hop):
    """Bergelantung di tali dari atas dan berayun ke kiri-kanan dengan pedang terangkat (khas)."""
    if phase == "rest":
        powder_keg(cv, CX + 2, TOP + 9)
        skirmisher_idle(cv, t, 0)
        return
    swing = (0, -1, -2, -3, -2, -1, 0, 1, 2, 3, 2, 1, 0, 0, 0, 0)[t] if phase == "up" else 0
    hx = CX - 12 + swing
    rope(cv, hx, TOP - 7)
    arm(cv, (CX - 7, TOP + 3), (hx, TOP - 6), elbow=(CX - 13 + swing // 2, TOP), fur="W")
    powder_keg(cv, CX + 2, TOP + 9)
    hy = TOP - 3 if phase == "rise" else TOP - 7
    sword(cv, CX + 14, hy, 80, length=10)
    arm(cv, (CX + 7, TOP + 3), (CX + 14, hy), elbow=(CX + 14, TOP + 1), fur="W")


def skirmisher_victory_look(cv, t, n, eyes, brows, mouth, dx=0, bob=0):
    phase = VICTORY[t % VICTORY_N][0]
    swing = (0, -1, -2, -3, -2, -1, 0, 1, 2, 3, 2, 1, 0, 0, 0, 0)[t % VICTORY_N] if phase == "up" else 0
    SKIRMISHER(cv, t, n, eyes, brows, mouth, dx=swing, bob=0)


SHARPSHOOTER = pirate_look("k", "L")


def sharpshooter_idle(cv, t, bob):
    rifle(cv, CX + 12, TOP + 14, 95, length=22)
    arm(cv, (CX + 7, TOP + 3 + bob), (CX + 12, TOP + 5 + bob), elbow=(CX + 12, TOP + 8 + bob), fur="k")
    rest_arm_left(cv, "k", bob)


def sharpshooter_strike(cv, t, pos, k):
    """Pose membidik ke atas: senapan panjang miring ke langit, satu mata menyipit. TANPA kilatan atau asap laras."""
    if pos == "rest":
        sharpshooter_idle(cv, t, 0)
        return
    deg = {"rise": 60, "draw": 50, "aim": 45}[pos]
    rifle(cv, CX + 3, TOP + 4, deg, length=22)
    arm(cv, (CX + 7, TOP + 3), (CX + 3, TOP + 4), elbow=(CX + 11, TOP + 7), fur="k")
    a = math.radians(deg)
    arm(cv, (CX - 7, TOP + 3), (int(CX + 3 + math.cos(a) * 9), int(TOP + 4 - math.sin(a) * 9)), elbow=(CX - 6, TOP + 8), fur="k")


def sharpshooter_look(cv, t, n, eyes, brows, mouth, dx=0, bob=0, hat_on=True):
    pos = AIM[t % ATTACK_N][0]
    SHARPSHOOTER(cv, t, n, "side" if pos == "aim" else eyes, brows, mouth, dx=dx, bob=bob, hat_on=hat_on)


def sharpshooter_victory_look(cv, t, n, eyes, brows, mouth, dx=0, bob=0):
    phase = VICTORY[t % VICTORY_N][0]
    SHARPSHOOTER(cv, t, n, eyes, brows, mouth, dx=dx, bob=bob, hat_on=phase not in ("up",) and t not in (12, 13))


def sharpshooter_cheer(cv, t, phase, hop):
    """Senapan diangkat tegak dengan tricorn berputar di ujung laras (khas)."""
    b = -hop
    if phase == "rest":
        sharpshooter_idle(cv, t, 0)
        return
    hy = TOP - 3 + b if phase == "rise" else TOP - 8 + b
    rifle(cv, CX + 13, hy + 8, 90, length=18)
    arm(cv, (CX + 7, TOP + 3 + b), (CX + 13, hy + 8), elbow=(CX + 13, TOP + 7 + b), fur="k")
    arm(cv, (CX - 7, TOP + 3 + b), (CX - 13, TOP - 4 + b), elbow=(CX - 13, TOP + 1 + b), fur="k")
    if phase == "up" or t in (12, 13):
        spin = t % 3
        tx, ty = CX + 13, hy - 10
        if spin == 1:  # tampak samping (sedang berputar)
            solid(cv, rect(tx - 2, ty - 3, 5, 4), "L", None)
            cv.fill({(tx - 3, ty + 1), (tx + 3, ty + 1)}, "O")
        else:
            tricorn(cv, tx, ty + 8)


BUCCANEER = pirate_look("x", "e", straps=True)


def buccaneer_idle(cv, t, bob):
    """Jangkar berdiri di lantai kanan dengan tangan kanan di cincinnya; palu besar bersandar di bahu kiri."""
    arm(cv, (CX + 7, TOP + 3 + bob), (CX + 19, TOP + 1), elbow=(CX + 13, TOP + 7 + bob), fur="x")
    anchor(cv, CX + 19, TOP - 1, big=1.2)
    solid(cv, ellipse(CX + 19, TOP + 2, 2.0, 2.0), "F", "f", shade_off=(1, 1))
    hammer(cv, CX - 9, TOP + 7 + bob, 115, length=12)
    arm(cv, (CX - 7, TOP + 3 + bob), (CX - 9, TOP + 7 + bob), elbow=(CX - 12, TOP + 6 + bob), fur="x")


def buccaneer_strike(cv, t, pos, k):
    """Palu besar di tangan kiri dihantamkan ke lantai kiri, debu piksel menyebar; jangkar tetap berdiri di kanan."""
    arm(cv, (CX + 7, TOP + 3), (CX + 19, TOP + 1), elbow=(CX + 13, TOP + 7), fur="x")
    anchor(cv, CX + 19, TOP - 1, big=1.2)
    solid(cv, ellipse(CX + 19, TOP + 2, 2.0, 2.0), "F", "f", shade_off=(1, 1))
    if pos == "rest":
        hammer(cv, CX - 9, TOP + 7, 115, length=12)
        arm(cv, (CX - 7, TOP + 3), (CX - 9, TOP + 7), elbow=(CX - 12, TOP + 6), fur="x")
    elif pos in ("rise", "up"):
        hy = TOP - 2 if pos == "rise" else TOP - 6
        hammer(cv, CX - 13, hy, 90, length=9)
        arm(cv, (CX - 7, TOP + 3), (CX - 13, hy), elbow=(CX - 14, TOP + 3), fur="x")
    else:
        hammer(cv, CX - 13, TOP + 4, -100, length=10)
        arm(cv, (CX - 7, TOP + 3), (CX - 13, TOP + 4), elbow=(CX - 12, TOP + 8), fur="x")
        if k:
            dust(cv, CX - 15, TOP + 16, k - 1)
            dust(cv, CX - 15, TOP + 15, k)
            spark_lines(cv, CX - 23, TOP + 9)


def buccaneer_cheer(cv, t, phase, hop):
    """Jangkar diangkat tinggi dengan tangan kanan (di sisi, tidak menutupi wajah), palu terangkat di kiri,
    garis tenaga di samping jangkar (khas)."""
    b = -hop
    if phase == "rest":
        buccaneer_idle(cv, t, 0)
        return
    ay = TOP - 21 + b if phase == "up" else TOP - 12 + b
    arm(cv, (CX + 7, TOP + 3 + b), (CX + 20, ay + 4), elbow=(CX + 15, TOP + 1 + b), fur="x")
    anchor(cv, CX + 20, ay, big=1.0)
    solid(cv, ellipse(CX + 20, ay + 4, 2.0, 2.0), "F", "f", shade_off=(1, 1))
    hammer(cv, CX - 13, TOP - 3 + b, 95, length=9)
    arm(cv, (CX - 7, TOP + 3 + b), (CX - 13, TOP - 3 + b), elbow=(CX - 14, TOP + 3 + b), fur="x")
    if phase == "up":
        for dy in (1, 6):
            sgn = 1 if t % 2 else 0
            cv.fill({(CX + 28, ay + dy + sgn), (CX + 29, ay + dy + 1 - sgn)}, "K")
            cv.fill({(CX + 12, ay + dy + sgn), (CX + 11, ay + dy + 1 - sgn)}, "K")


# ================================================================== registrasi
VARIANTS = {
    "knight-heavy": (HEAVY, heavy_idle, frame_attack(HEAVY, heavy_strike), heavy_cheer, None),
    "knight-archer": (ARCHER, archer_idle, frame_attack(ARCHER, archer_strike, AIM), archer_cheer, None),
    "knight-manatarms": (MANATARMS, manatarms_idle, frame_attack(MANATARMS, manatarms_strike), manatarms_cheer, None),
    "knight-assassin": (ASSASSIN, assassin_idle, frame_attack(ASSASSIN, assassin_strike), assassin_cheer, None),
    "viking-berserker": (berserker_look, berserker_idle, frame_attack(berserker_look, berserker_strike), berserker_cheer, None),
    "viking-huscarl": (HUSCARL, huscarl_idle, frame_attack(HUSCARL, huscarl_strike), huscarl_cheer, None),
    "viking-gestir": (GESTIR, gestir_idle, frame_attack(GESTIR, gestir_strike), gestir_cheer, None),
    "viking-bondi": (BONDI, bondi_idle, frame_attack(BONDI, bondi_strike, AIM), bondi_cheer, None),
    "pirate-captain": (CAPTAIN, captain_idle, frame_attack(CAPTAIN, captain_strike), captain_cheer, None),
    "pirate-skirmisher": (SKIRMISHER, skirmisher_idle, frame_attack(skirmisher_hop_look, skirmisher_strike),
                          skirmisher_cheer, skirmisher_victory_look),
    "pirate-sharpshooter": (SHARPSHOOTER, sharpshooter_idle, frame_attack(sharpshooter_look, sharpshooter_strike, AIM),
                            sharpshooter_cheer, sharpshooter_victory_look),
    "pirate-buccaneer": (BUCCANEER, buccaneer_idle, frame_attack(BUCCANEER, buccaneer_strike), buccaneer_cheer, None),
}
AIMING = {"knight-archer", "viking-bondi", "pirate-sharpshooter"}

SCENES = {}
for _name, (_look, _idle, _attack, _cheer, _vlook) in VARIANTS.items():
    SCENES[_name + "-idle"] = (frame_idle(_look, _idle), IDLE_N, idle_ms)
    SCENES[_name + "-attack"] = (_attack, ATTACK_N, aim_ms if _name in AIMING else attack_ms)
    SCENES[_name + "-victory"] = (frame_victory(_vlook or _look, _cheer), VICTORY_N, victory_ms)

PROPS = {
    "knight-heavy: pedang besar": lambda cv: greatsword(cv, 20, 36, 90, length=17),
    "knight-heavy: pelindung bahu": lambda cv: pauldron(cv, 30, 24),
    "knight-archer: busur panjang": lambda cv: longbow(cv, 30, 10, 33),
    "knight-archer: tabung panah": lambda cv: quiver(cv, 28, 16),
    "knight-archer: papan sasaran": lambda cv: target_board(cv, 30, 16),
    "knight-manatarms: halberd": lambda cv: halberd(cv, 30, 40, length=27),
    "knight-manatarms: gada": lambda cv: mace(cv, 26, 30, 70, length=8),
    "knight-assassin: belati": lambda cv: dagger(cv, 28, 30, 90, length=7),
    "knight-assassin: bom asap": lambda cv: smoke_bomb(cv, 30, 24),
    "viking-berserker: ikat kepala bulu": lambda cv: fur_headband(cv, 32, 24),
    "viking-huscarl: kapak besar": lambda cv: axe(cv, 30, 38, 90, length=16, big=True),
    "viking-gestir: tombak lempar": lambda cv: javelin(cv, 30, 40, length=26),
    "viking-bondi: busur pendek": lambda cv: longbow(cv, 30, 16, 30, bend=2),
    "viking-bondi: seax": lambda cv: seax(cv, 28, 24),
    "pirate-captain: topi kapten": lambda cv: captain_hat(cv, 32, 24),
    "pirate-captain: blunderbuss": lambda cv: blunderbuss(cv, 26, 30, 80),
    "pirate-captain: burung beo": lambda cv: parrot(cv, 30, 24, flap=1),
    "pirate-skirmisher: bandana": lambda cv: bandana(cv, 32, 24),
    "pirate-skirmisher: tong mesiu": lambda cv: powder_keg(cv, 30, 24),
    "pirate-sharpshooter: senapan panjang": lambda cv: rifle(cv, 24, 36, 70, length=22),
    "pirate-buccaneer: palu besar": lambda cv: hammer(cv, 28, 36, 90, length=11),
    "pirate-buccaneer: jangkar": lambda cv: anchor(cv, 30, 16),
}
