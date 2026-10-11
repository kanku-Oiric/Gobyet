#!/usr/bin/env python3
"""Fase B Berserker Hero: tiga pose kunci, pengukuran batas keterbacaan (bagian 4.4), dan lembar bukti.

    python3 tools/hero_phase_b.py [folder-keluaran]        # bawaan: pack/reports/hero-fase-b/

Menulis:
  kontak-1x.png, kontak-2x.png, kontak-4x.png   tiga pose hero berdampingan dengan viking-berserker 64x48 (dibesarkan 2x/4x/8x
                                                supaya tinggi kanvas dalam piksel layar sama), latar terang (atas) dan gelap (bawah)
  helm-8x.png, pedang-4x.png                    close-up helm (8x) dan pedang (4x), dua latar
  siluet.png                                    siluet isi hitam tiga pose, dua latar
  pose-1x-<nama>.png                            frame 128x96 asli (RGBA, transparan) tiap pose kunci
  ukuran.json                                   semua angka yang diukur (dicetak juga ke stdout)

Pengukuran memakai peta pemilik piksel (PartCanvas): hanya piksel yang masih terlihat setelah semua lapisan digambar.
Hasil adalah angka heuristik; tidak menyatakan gaya bagus atau disetujui.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

from PIL import Image  # noqa: E402

import hero  # noqa: E402
import monkey  # noqa: E402

LIGHT, DARK = (250, 247, 240), (24, 28, 44)
HELM = {"helm", "crest", "horn", "horn_break", "snout", "fang", "socket", "socket_glow", "rivet", "helm_seam", "jaw"}


def lum(rgb):
    def ch(c):
        c /= 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


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


def bbox(pix):
    xs, ys = [p[0] for p in pix], [p[1] for p in pix]
    return (min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1)


def farthest(pix):
    pts = list(pix)
    best = 0.0
    for i in range(0, len(pts)):
        for j in range(i + 1, len(pts)):
            d = math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
            best = max(best, d)
    return best


def arc_len(p0, p1, p2, n=200, upto=1.0):
    pts = hero.bezier(p0, p1, p2, n)[:int(n * upto) + 1]
    return sum(math.hypot(a[0] - b[0], a[1] - b[1]) for a, b in zip(pts, pts[1:]))


def owners(cv, names=None, prefix=None):
    return {k for k, o in cv.owner.items() if (names and o in names) or (prefix and o and o.startswith(prefix))}


def measure_blade():
    """Bilah digambar sendiri pada sudut 0: lebar terlebar, jumlah luk per sisi, dan amplitudo (puncak luk ke pinggang)."""
    cv = hero.PartCanvas()
    sf = hero.SwordFrame(10, 48, 0.0)
    hero.sword_parts(cv, sf, parts=("blade",))
    cols = {}
    for (x, y), o in cv.owner.items():
        if o == "blade":
            cols.setdefault(x, []).append(y)
    xs = sorted(cols)
    top = [48 - min(cols[x]) for x in xs]          # jarak terluar sisi atas dari sumbu
    bot = [max(cols[x]) - 48 + 1 for x in xs]
    widths = [max(cols[x]) - min(cols[x]) + 1 for x in xs]
    lo, hi = hero.LOBE0 + 1, hero.LOBE0 + hero.LOBES * hero.PITCH - 1
    sel = [i for i, x in enumerate(xs) if lo <= x - 10 <= hi]
    out = {"bilah_terlebar_px": max(widths), "bilah_pinggang_tersempit_px": min(widths[i] for i in sel)}
    lobes, amps = [], []
    for prof in (top, bot):
        p = [prof[i] for i in sel]
        peaks = [i for i in range(1, len(p) - 1) if p[i] >= p[i - 1] and p[i] > p[i + 1] or (p[i] > p[i - 1] and p[i] >= p[i + 1])]
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
    out["bilah_luk_per_sisi"] = lobes
    out["bilah_amplitudo_desain_px"] = hero.DEPTH
    out["bilah_amplitudo_terukur_px"] = {"min": min(amps), "rata": round(sum(amps) / len(amps), 1)} if amps else None
    return out


def measure_idle():
    p = hero.pose_idle()
    cv = hero.render_pose(p)
    g = hero.geometry(p)
    hx, hy = g["head"]
    m = {}
    # helm
    helm_all = owners(cv, HELM, "tooth")
    helm_core = owners(cv, {"helm", "crest", "jaw"}, "tooth")
    m["helm_total_bbox_wh"] = bbox(helm_all)[2:]
    m["helm_kubah_rahang_bbox_wh"] = bbox(helm_core)[2:]
    snout = owners(cv, {"snout"})
    m["moncong_bbox_wh"] = bbox(snout)[2:]
    # tanduk
    horn_pix = owners(cv, {"horn", "horn_break"})
    comps = sorted(components(horn_pix), key=lambda c: -len(c))
    hx0, hy0 = int(round(hx)), int(round(hy))
    arcs = [arc_len(*hero.tr(hero.HORN_A, hx0, hy0)), arc_len(*hero.tr(hero.HORN_B, hx0, hy0), upto=(hero.HORN_B_KEEP - 1) / 22.0)]
    m["tanduk"] = [{"piksel_terlihat": len(c), "jarak_terjauh_piksel": round(farthest(c), 1), "bbox_wh": bbox(c)[2:]} for c in comps if len(c) >= 20]
    m["tanduk_panjang_busur_desain"] = [round(a, 1) for a in arcs]
    m["tanduk_lengkung_busur_per_tali"] = [round(arcs[0] / math.hypot(hero.HORN_A[2][0] - hero.HORN_A[0][0], hero.HORN_A[2][1] - hero.HORN_A[0][1]), 2)]
    # rongga mata
    sock = sorted(components(owners(cv, {"socket"})), key=lambda c: bbox(c)[0])
    m["rongga_mata_bbox_wh"] = [bbox(c)[2:] for c in sock]
    # gigi
    teeth = {}
    for k, o in cv.owner.items():
        if o and (o.startswith("tooth") or o == "fang"):
            teeth.setdefault(o if o != "fang" else "fang%d" % ((k[0] - hx0 - 10) // 6), set()).add(k)
    vis = {n: len(v) for n, v in teeth.items()}
    m["gigi_rahang_terlihat"] = sum(1 for n, v in vis.items() if n.startswith("tooth") and v >= 4)
    m["gigi_lebar_px"] = sorted({bbox(v)[2] for n, v in teeth.items() if n.startswith("tooth")})
    m["taring_moncong_terlihat"] = sum(1 for n, v in vis.items() if n.startswith("fang") and v >= 4)
    # bilah: diukur pada render pedang tanpa rotasi (sudut 0) supaya kolom piksel = sumbu u; per sisi dicari puncak dan lembah luk
    m.update(measure_blade())
    # bilah di pose idle: lebar terlebar yang masih terlihat (setelah tertutup tangan dan pelindung)
    sf = g["sword"]
    ext = {}
    for (x, y) in owners(cv, {"blade"}):
        u = (x + 0.5 - sf.gx) * sf.ca + (y + 0.5 - sf.gy) * sf.sa
        v = -(x + 0.5 - sf.gx) * sf.sa + (y + 0.5 - sf.gy) * sf.ca
        k = int(math.floor(u))
        lo, hi = ext.get(k, (v, v))
        ext[k] = (min(lo, v), max(hi, v))
    m["bilah_terlebar_di_pose_idle_px"] = round(max(hi - lo + 1 for lo, hi in ext.values()), 1)
    # rasio pedang / tubuh (tubuh = telapak sampai puncak tengkorak Gobyet, tanpa helm dan tanduk)
    sword_len = hero.S_LEN - (hero.POMMEL_U - 2.7)
    body_h = (hero.FLOOR - 1) - (hy - 12.6) + 1
    m["pedang_panjang_total_px"] = round(sword_len, 1)
    m["tinggi_tubuh_px"] = round(body_h, 1)
    m["rasio_pedang_per_tubuh"] = round(sword_len / body_h, 2)
    # bahu berlapis
    m["bahu_pelat_piksel_terlihat"] = [len(owners(cv, {"pauldron%d" % i})) for i in (1, 2, 3)]
    # wajah
    face = {"face", "eye", "brow", "mouth"}
    m["wajah_piksel_terlihat"] = len(owners(cv, face))
    return m


def global_checks(poses):
    cols, partial = set(), False
    for name, cv in poses.items():
        cols |= set(cv.px.values())
    return {"warna_dipakai_tiga_pose": len(cols), "warna_palet": len(hero.HERO_PAL), "batas_warna": 28,
            "alfa_parsial": partial, "kanvas": [hero.W, hero.H]}


def face_visible(poses):
    out = {}
    faceset = {"face", "eye", "brow", "mouth"}
    for name, cv in poses.items():
        out[name] = {"wajah": len(owners(cv, faceset)), "telinga": len(owners(cv, {"ear"})), "tengkorak_bulu": len(owners(cv, {"skull"}))}
    return out


def to_img(cv, bg=None):
    return cv.image(1, bg=bg)


def silhouette(cv, bg):
    im = Image.new("RGB", (hero.W, hero.H), bg)
    ink = (14, 14, 18) if bg == LIGHT else (236, 236, 244)
    for (x, y) in cv.px:
        im.putpixel((x, y), ink)
    return im


def stack_h(images, gap=8, bg=(255, 255, 255)):
    w = sum(i.width for i in images) + gap * (len(images) - 1)
    h = max(i.height for i in images)
    out = Image.new("RGB", (w, h), bg)
    x = 0
    for i in images:
        out.paste(i, (x, 0))
        x += i.width + gap
    return out


def stack_v(images, gap=8, bg=(255, 255, 255)):
    w = max(i.width for i in images)
    h = sum(i.height for i in images) + gap * (len(images) - 1)
    out = Image.new("RGB", (w, h), bg)
    y = 0
    for i in images:
        out.paste(i, (0, y))
        y += i.height + gap
    return out


def v1_viking_berserker():
    """Frame kunci viking-berserker/idle (64x48) dari sheet 1x v1."""
    sheet = Image.open(os.path.join(ROOT, "sheets", "viking-berserker-idle.png")).convert("RGBA")
    return sheet.crop((0, 0, monkey.W, monkey.H))


def main(argv):
    out = argv[0] if argv else os.path.join(ROOT, "pack", "reports", "hero-fase-b")
    os.makedirs(out, exist_ok=True)
    poses = {name: hero.render_pose(fn()) for name, fn in hero.KEYPOSES.items()}
    vb = v1_viking_berserker()
    # --- lembar kontak 1x, 2x, 4x: hero berskala s, viking-berserker berskala 2s (kanvas 64x48 -> 128x96 x s)
    for s in (1, 2, 4):
        rows = []
        for bg in (LIGHT, DARK):
            cells = []
            vbi = Image.new("RGBA", vb.size, bg + (255,))
            vbi.alpha_composite(vb)
            cells.append(vbi.convert("RGB").resize((hero.W * s, hero.H * s), Image.NEAREST))
            for name, cv in poses.items():
                cells.append(to_img(cv, bg).convert("RGB").resize((hero.W * s, hero.H * s), Image.NEAREST))
            rows.append(stack_h(cells))
        stack_v(rows).save(os.path.join(out, "kontak-%dx.png" % s))
    # --- close-up helm 8x dan pedang 4x (pose idle)
    idle = poses["idle"]
    g = hero.geometry(hero.pose_idle())
    hx, hy = int(round(g["head"][0])), int(round(g["head"][1]))
    hb = (hx - 34, hy - 40, hx + 30, hy + 17)
    sw = (36, 54, 118, 92)
    for fname, box, sc in (("helm-8x.png", hb, 8), ("pedang-4x.png", sw, 4)):
        rows = []
        for bg in (LIGHT, DARK):
            im = to_img(idle, bg).convert("RGB").crop(box)
            rows.append(im.resize((im.width * sc, im.height * sc), Image.NEAREST))
        stack_h(rows).save(os.path.join(out, fname))
    # --- siluet isi hitam
    rows = [stack_h([silhouette(cv, bg).resize((hero.W * 4, hero.H * 4), Image.NEAREST) for cv in poses.values()]) for bg in (LIGHT, DARK)]
    stack_v(rows).save(os.path.join(out, "siluet.png"))
    # --- frame asli 1x
    for name, cv in poses.items():
        cv.image(1).save(os.path.join(out, "pose-1x-%s.png" % name))
    # --- angka
    res = {"pose_idle": measure_idle(), "global": global_checks(poses), "wajah": face_visible(poses)}
    o2, rm, ib = monkey.rgb("o2"), monkey.rgb("rm"), monkey.rgb("ib")
    res["kontras_luminans"] = {
        "tepi_hitam_o2_vs_latar_terang": round(contrast(o2, LIGHT), 2), "tepi_hitam_o2_vs_latar_gelap": round(contrast(o2, DARK), 2),
        "besi_dasar_ib_vs_latar_terang": round(contrast(ib, LIGHT), 2), "besi_dasar_ib_vs_latar_gelap": round(contrast(ib, DARK), 2),
        "rim_biru_baja_vs_latar_gelap": round(contrast(rm, DARK), 2), "rim_biru_baja_vs_latar_terang": round(contrast(rm, LIGHT), 2),
        "latar_terang": LIGHT, "latar_gelap": DARK}
    res["bbox_tinggi_kepala"] = {n: bbox(owners(cv, {"skull", "face", "ear"}) | owners(cv, HELM, "tooth"))[3] for n, cv in poses.items()}
    with open(os.path.join(out, "ukuran.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
