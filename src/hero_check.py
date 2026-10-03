"""Pengukuran Berserker Hero untuk validator V11 dan uji (hanya membaca; tidak menulis aset).

Semua ukuran memakai peta pemilik piksel (hero.PartCanvas): hanya piksel yang masih terlihat setelah semua lapisan digambar
yang dihitung. Angka bersifat heuristik; modul ini tidak menyatakan gaya bagus atau disetujui.
"""
import math
from collections import Counter

import hero

HELM = {"helm", "crest", "horn", "horn_break", "snout", "fang", "socket", "socket_glow", "rivet", "helm_seam", "jaw"}
HEAD_PARTS = HELM | {"skull", "ear", "face", "eye", "brow", "mouth"}
FACE_PARTS = ("face", "eye", "mouth", "ear")        # kulit wajah, mata, hidung + mulut, telinga

# Batas keterbacaan bagian 4.4 spesifikasi
MIN_HELM = (34, 26)
MIN_SNOUT = (10, 8)
MIN_HORN_PX = 14
MIN_SOCKET = (4, 3)
MIN_TEETH = 6
MIN_BLADE_WIDTH = 10
MIN_LOBES, MIN_LOBE_AMP = 5, 3
MIN_PLATES = 3


def owners(cv, names=None, prefix=None):
    return {k for k, o in cv.owner.items() if (names and o in names) or (prefix and o and o.startswith(prefix))}


def bbox(pix):
    """(x0, y0, lebar, tinggi) kotak pembatas; None bila kosong."""
    if not pix:
        return None
    xs, ys = [p[0] for p in pix], [p[1] for p in pix]
    return (min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1)


def components(pix):
    pix, out = set(pix), []
    while pix:
        stack, comp = [pix.pop()], set()
        comp.add(stack[0])
        while stack:
            x, y = stack.pop()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    q = (x + dx, y + dy)
                    if q in pix:
                        pix.discard(q)
                        comp.add(q)
                        stack.append(q)
        out.append(comp)
    return out


def farthest(pix):
    pts = list(pix)
    best = 0.0
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            best = max(best, math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1]))
    return best


def head_alone(p):
    """Kepala dan helm digambar sendirian di posisi dan ekspresi pose p: acuan 'tidak tertutup apa pun'."""
    g = hero.geometry(p)
    hx, hy = int(round(g["head"][0])), int(round(g["head"][1]))
    cv = hero.PartCanvas()
    hero.head_hd(cv, hx, hy, eyes=p["eyes"], brows=p["brows"], mouth=p["mouth"], face=p["face"], tilt=p["tilt"])
    hero.helm(cv, hx, hy, rage=p["rage"])
    return cv


def visibility(cv, p):
    """{bagian: (terlihat, acuan)}: piksel bagian wajah yang terlihat di frame penuh dibanding kepala sendirian."""
    ref = head_alone(p)
    full, alone = Counter(cv.owner.values()), Counter(ref.owner.values())
    return {name: (full.get(name, 0), alone.get(name, 0)) for name in FACE_PARTS}


def head_height(cv):
    b = bbox(owners(cv, HEAD_PARTS, "tooth"))
    return b[3] if b else 0


def readability(cv):
    """Ukuran bagian helm yang masih terlihat di satu frame (bagian 4.4)."""
    out = {}
    helm = owners(cv, HELM, "tooth")
    out["helm"] = bbox(helm)[2:] if helm else (0, 0)
    snout = owners(cv, {"snout"})
    out["snout"] = bbox(snout)[2:] if snout else (0, 0)
    horns = sorted(components(owners(cv, {"horn", "horn_break"})), key=lambda c: -len(c))
    out["horn_px"] = [round(farthest(c), 1) for c in horns[:2]]
    sockets = sorted(components(owners(cv, {"socket"})), key=lambda c: bbox(c)[0])
    out["socket"] = [bbox(c)[2:] for c in sockets]
    teeth = {}
    for k, o in cv.owner.items():
        if o and o.startswith("tooth"):
            teeth.setdefault(o, set()).add(k)
    seen = {n: v for n, v in teeth.items() if len(v) >= 4}
    out["teeth"] = len(seen)
    out["teeth_width"] = sorted({bbox(v)[2] for v in seen.values()})
    out["plates"] = [len(owners(cv, {"pauldron%d" % i})) for i in (1, 2, 3)]
    return out


def readability_failures(r):
    """Daftar kegagalan terhadap batas 4.4 untuk hasil readability()."""
    bad = []
    if r["helm"][0] < MIN_HELM[0] or r["helm"][1] < MIN_HELM[1]:
        bad.append("helm %dx%d < %dx%d" % (r["helm"] + MIN_HELM))
    if r["snout"][0] < MIN_SNOUT[0] or r["snout"][1] < MIN_SNOUT[1]:
        bad.append("moncong %dx%d < %dx%d" % (r["snout"] + MIN_SNOUT))
    if len(r["horn_px"]) < 2 or min(r["horn_px"]) < MIN_HORN_PX:
        bad.append("tanduk terlihat %s < %d px" % (r["horn_px"], MIN_HORN_PX))
    if len(r["socket"]) < 2 or any(w < MIN_SOCKET[0] or h < MIN_SOCKET[1] for w, h in r["socket"]):
        bad.append("rongga mata %s < %dx%d" % (r["socket"], MIN_SOCKET[0], MIN_SOCKET[1]))
    if r["teeth"] < MIN_TEETH or 2 not in r["teeth_width"]:
        bad.append("gigi terlihat %d (lebar %s), butuh >= %d lebar 2" % (r["teeth"], r["teeth_width"], MIN_TEETH))
    if sum(1 for n in r["plates"] if n >= 8) < MIN_PLATES:
        bad.append("pelat bahu terlihat %s, butuh %d pelat terpisah (>= 8 piksel)" % (r["plates"], MIN_PLATES))
    return bad


def blade_static():
    """Bilah digambar sendiri pada sudut 0 (kolom piksel = sumbu bilah): lebar terlebar, jumlah luk per sisi, amplitudo."""
    cv = hero.PartCanvas()
    sf = hero.SwordFrame(10, 48, 0.0)
    hero.sword_parts(cv, sf, parts=("blade",))
    cols = {}
    for (x, y), o in cv.owner.items():
        if o == "blade":
            cols.setdefault(x, []).append(y)
    xs = sorted(cols)
    top = [48 - min(cols[x]) for x in xs]
    bot = [max(cols[x]) - 48 + 1 for x in xs]
    widths = [max(cols[x]) - min(cols[x]) + 1 for x in xs]
    lo, hi = hero.LOBE0 + 1, hero.LOBE0 + hero.LOBES * hero.PITCH - 1
    sel = [i for i, x in enumerate(xs) if lo <= x - 10 <= hi]
    lobes, amps = [], []
    for prof in (top, bot):
        p = [prof[i] for i in sel]
        peaks = [i for i in range(1, len(p) - 1) if (p[i] >= p[i - 1] and p[i] > p[i + 1]) or (p[i] > p[i - 1] and p[i] >= p[i + 1])]
        keep = []
        for i in peaks:
            if keep and i - keep[-1] < 4:
                if p[i] > p[keep[-1]]:
                    keep[-1] = i
                continue
            keep.append(i)
        lobes.append(len(keep))
        for a, b in zip(keep, keep[1:]):
            amps.append(min(p[a], p[b]) - min(p[a:b + 1]))
    return {"lebar": max(widths), "luk": lobes, "amplitudo_min": min(amps) if amps else 0}


def blade_failures(b):
    bad = []
    if b["lebar"] < MIN_BLADE_WIDTH:
        bad.append("bilah terlebar %d < %d px" % (b["lebar"], MIN_BLADE_WIDTH))
    if max(b["luk"]) < MIN_LOBES:
        bad.append("luk bilah %s < %d" % (b["luk"], MIN_LOBES))
    if b["amplitudo_min"] < MIN_LOBE_AMP:
        bad.append("amplitudo luk %d < %d px" % (b["amplitudo_min"], MIN_LOBE_AMP))
    return bad


def lum(rgb):
    def ch(c):
        c /= 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def iou(a, b):
    u = len(a | b)
    return len(a & b) / float(u) if u else 1.0
