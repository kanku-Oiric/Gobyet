#!/usr/bin/env python3
"""Fase Body Berserker Hero v2: tiga pose kunci, peta bagian, ukuran, dan lembar bukti (hanya membaca kode; tidak menulis aset).

    python3 tools/hero2_body.py [folder-keluaran]        # bawaan: pack/reports/hero2-body/

Menulis:
  kunci-3-pose.png        idle, run, attack-smash pada latar terang, gelap, dan abu tengah, 4x
  detail-<pose>-8x.png    tiap pose 8x
  helm-12x.png            kepala dan helm idle 12x, latar terang dan gelap
  siluet.png              siluet isi hitam tiga pose (latar terang dan abu tengah)
  bandingan-v1-v2.png     hero lama (v1, ditolak) dan v2 (body) berdampingan, 5x
  peta-bagian.png         idle 6x dengan nomor bagian; daftar nomor ada di ukuran.json dan laporan
  ukuran.json             proporsi, kotak pembatas, keterlihatan wajah, palet, kontras (angka heuristik)
Bukan pernyataan bahwa gaya bagus atau disetujui.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import hero  # noqa: E402  (v1, untuk perbandingan)
import hero2  # noqa: E402
import hero_check as hc  # noqa: E402

OUT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ROOT, "pack", "reports", "hero2-body")
LIGHT, DARK, GRAY = (250, 247, 240), (24, 28, 44), (128, 128, 128)
POSES = ["idle", "run", "attack-smash"]
FX_PARTS = {"dust", "chip", "burst", "smear", "block", "speed", "sweat", "breath", "spark", "roar"}
HEAD_PARTS = {"crest", "helm_cap", "brow_band", "brow_glow", "sensor", "rivet", "fin", "cheek", "chin", "chin_glow", "neck", "skull", "face", "eye", "brow",
              "mouth", "ear"}
TORSO_PARTS = {"collar", "chest", "vent", "belly", "belt", "buckle", "hip_plate", "pauldron_big", "horn_fin", "hatch", "ring", "pauldron_small", "upper_arm",
               "vambrace", "elbow", "gauntlet"}
LEG_PARTS = {"thigh", "shin", "knee", "boot", "spike"}
FACE_PARTS = ("face", "eye", "mouth", "ear")
PART_LABELS = [  # (nomor, nama bagian, bagian pemilik piksel, keterangan)
    (1, "jambul bilah merah", {"crest"}, "lima bilah menyebar ke belakang-atas dan ke atas"),
    (2, "tutup dahi + pita alis V", {"helm_cap", "brow_band", "brow_glow"}, "strip cahaya merah menyala"),
    (3, "wajah Gobyet", {"face", "eye", "mouth", "brow"}, "mata, hidung, mulut selalu terlihat"),
    (4, "telinga", {"ear"}, "selalu terlihat"),
    (5, "sirip helm", {"fin"}, "sirip samping belakang dan depan"),
    (6, "pelindung bahu raksasa", {"pauldron_big"}, "cangkang bersudut"),
    (7, "sirip tanduk bahu", {"horn_fin"}, "dua sirip tinggi bertulang merah"),
    (8, "palka + cincin inti merah", {"hatch", "ring"}, "ventilasi tiga celah, cincin berinti merah"),
    (9, "pelindung bahu bundar", {"pauldron_small"}, "cakram berlapis cincin"),
    (10, "dada berventilasi", {"chest", "vent"}, "dua celah bercahaya merah"),
    (11, "perut sisik heksagonal", {"belly"}, "pola sisik merah darah"),
    (12, "sabuk + gesper", {"belt", "buckle"}, "gesper bercahaya"),
    (13, "pelat pinggul", {"hip_plate"}, ""),
    (14, "sepatu besar + paku merah", {"boot", "spike"}, "paku di belakang pergelangan dan di bawah bahu"),
    (15, "ekor kipas panah", {"tail_arrow", "tail_stem"}, "dua busur panah merah"),
    (16, "sarung tangan", {"gauntlet"}, ""),
    (17, "pedang PENGGANTI", {"weapon"}, "balok polos, bukan desain akhir"),
]


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def pose_cv(name, fx=True):
    p = hero2.KEYPOSES[name]()
    if not fx:
        p = dict(p, fx=())
    return p, hero2.render_pose(p)


def paste(bg, cv, scale):
    return cv.image(1, bg=bg).convert("RGB").resize((hero2.W * scale, hero2.HGT * scale), Image.NEAREST)


def label(im, text, ink):
    ImageDraw.Draw(im).text((6, 4), text, fill=ink, font=font(14))


def owners(cv, names):
    return [k for k, o in cv.owner.items() if o in names]


def yrange(cv, names):
    pts = owners(cv, names)
    return (min(y for _, y in pts), max(y for _, y in pts)) if pts else None


def xrange(cv, names):
    pts = owners(cv, names)
    return (min(x for x, _ in pts), max(x for x, _ in pts)) if pts else None


def main():
    os.makedirs(OUT, exist_ok=True)
    info = {"poses": {}}
    # --- tiga pose, tiga latar, 4x
    sc = 4
    w, h = hero2.W * sc, hero2.HGT * sc
    sheet = Image.new("RGB", (3 * (w + 6) + 6, 3 * (h + 6) + 6), (128, 0, 128))
    for c, name in enumerate(POSES):
        p, cv = pose_cv(name)
        for r, (bg, ink) in enumerate(((LIGHT, (200, 0, 0)), (DARK, (255, 200, 120)), (GRAY, (255, 255, 0)))):
            im = paste(bg, cv, sc)
            label(im, name, ink)
            sheet.paste(im, (6 + c * (w + 6), 6 + r * (h + 6)))
        big = paste(LIGHT, cv, 8)
        big.save(os.path.join(OUT, "detail-%s-8x.png" % name))
    sheet.save(os.path.join(OUT, "kunci-3-pose.png"))

    # --- helm 12x
    p, cv = pose_cv("idle", fx=False)
    box = (28, 0, 104, 64)
    ims = [cv.image(1, bg=bg).convert("RGB").crop(box) for bg in (LIGHT, DARK)]
    ims = [i.resize((i.width * 12, i.height * 12), Image.NEAREST) for i in ims]
    o = Image.new("RGB", (ims[0].width * 2 + 6, ims[0].height), (128, 0, 128))
    o.paste(ims[0], (0, 0))
    o.paste(ims[1], (ims[0].width + 6, 0))
    o.save(os.path.join(OUT, "helm-12x.png"))

    # --- siluet isi hitam
    sil = Image.new("RGB", (3 * (w + 6) + 6, 2 * (h + 6) + 6), (128, 0, 128))
    for c, name in enumerate(POSES):
        p, cv = pose_cv(name)
        for r, bg in enumerate((LIGHT, GRAY)):
            im = Image.new("RGB", (hero2.W, hero2.HGT), bg)
            px = im.load()
            for (x, y) in cv.px:
                px[x, y] = (0, 0, 0)
            sil.paste(im.resize((w, h), Image.NEAREST), (6 + c * (w + 6), 6 + r * (h + 6)))
    sil.save(os.path.join(OUT, "siluet.png"))

    # --- bandingan v1 (lama) dan v2
    s5 = 5
    v1 = hero.render_pose(hero.pose_idle())
    v2 = hero2.render_pose(hero2.pose_idle())
    cmp_ = Image.new("RGB", (2 * (hero2.W * s5 + 6) + 6, 2 * (hero2.HGT * s5 + 6) + 6), (128, 0, 128))
    for r, (bg, ink) in enumerate(((LIGHT, (200, 0, 0)), (DARK, (255, 200, 120)))):
        for c, (cv, name) in enumerate(((v1, "v1 (ditolak)"), (v2, "v2 body"))):
            im = paste(bg, cv, s5)
            label(im, name, ink)
            cmp_.paste(im, (6 + c * (hero2.W * s5 + 6), 6 + r * (hero2.HGT * s5 + 6)))
    cmp_.save(os.path.join(OUT, "bandingan-v1-v2.png"))

    # --- peta bagian (idle 6x) dengan nomor
    p, cv = pose_cv("idle", fx=False)
    s6 = 6
    base = paste(LIGHT, cv, s6)
    d = ImageDraw.Draw(base)
    f = font(15)
    used = []
    legend = []
    for num, name, parts, note in PART_LABELS:
        pts = owners(cv, parts)
        if not pts:
            continue
        # titik jangkar: piksel milik bagian yang paling dekat dengan pusat massanya
        cx_ = sum(x for x, _ in pts) / float(len(pts))
        cy_ = sum(y for _, y in pts) / float(len(pts))
        ax, ay = min(pts, key=lambda q: (q[0] - cx_) ** 2 + (q[1] - cy_) ** 2)
        X, Y = ax * s6 + s6 // 2, ay * s6 + s6 // 2
        for ux, uy in used:
            if abs(ux - X) < 20 and abs(uy - Y) < 20:
                Y += 20
        used.append((X, Y))
        d.ellipse((X - 10, Y - 10, X + 10, Y + 10), fill=(120, 10, 30), outline=(255, 255, 255), width=2)
        d.text((X - (5 if num < 10 else 9), Y - 8), str(num), fill=(255, 255, 255), font=f)
        legend.append({"nomor": num, "bagian": name, "keterangan": note, "piksel": len(pts)})
    base.save(os.path.join(OUT, "peta-bagian.png"))
    info["legenda_bagian"] = legend

    # --- ukuran dan proporsi per pose
    keys_union = set()
    for name in POSES:
        p, cv = pose_cv(name, fx=False)
        allp = [k for k, o in cv.owner.items() if o not in FX_PARTS and o not in ("tail_arrow", "tail_stem", "weapon")]
        xs = [x for x, _ in allp]
        ys = [y for _, y in allp]
        full = [k for k in cv.px]
        entry = {"kotak_badan_tanpa_ekor_pedang": [min(xs), min(ys), max(xs), max(ys)], "tinggi_badan": max(ys) - min(ys) + 1, "lebar_badan": max(xs) - min(xs) + 1,
                 "kotak_semua_piksel": [min(x for x, _ in full), min(y for _, y in full), max(x for x, _ in full), max(y for _, y in full)]}
        hy, ty, ly = yrange(cv, HEAD_PARTS), yrange(cv, TORSO_PARTS), yrange(cv, LEG_PARTS)
        entry["rentang_y"] = {"kepala_jambul": hy, "badan_bahu_perut": ty, "kaki_sepatu": ly}
        total = max(ys) - min(ys) + 1
        # proporsi vertikal: jambul sampai dagu, dagu sampai sabuk, sabuk sampai lantai (potongan berurutan, jumlah = 100%)
        chin_y = yrange(cv, {"skull"})[1]                      # dasar tengkorak = dasar kepala yang terlihat (dagu/kerah menimpa dada)
        belt_y = yrange(cv, {"belt"})[1]
        top = min(ys)
        bottom = max(ys)
        entry["proporsi_vertikal_persen"] = {"kepala_dan_jambul": round(100.0 * (chin_y - top + 1) / total, 1),
                                              "badan_kepala_ke_sabuk": round(100.0 * (belt_y - chin_y) / total, 1),
                                              "kaki_sabuk_ke_lantai": round(100.0 * (bottom - belt_y) / total, 1)}
        ear_x = xrange(cv, {"ear"})
        entry["lebar_kepala_dengan_telinga"] = ear_x[1] - ear_x[0] + 1
        entry["lebar_pelindung_bahu_raksasa"] = (lambda r: r[1] - r[0] + 1)(xrange(cv, {"pauldron_big"}))
        # keterlihatan wajah dibanding kepala sendirian
        ref = hero2.head_only(p)
        from collections import Counter
        full_c, ref_c = Counter(cv.owner.values()), Counter(ref.owner.values())
        entry["wajah_terlihat_vs_kepala_sendirian"] = {k: [full_c.get(k, 0), ref_c.get(k, 0)] for k in FACE_PARTS}
        entry["warna_dipakai"] = sorted(set(cv.px.values()))
        keys_union |= set(cv.px.values())
        entry["piksel_per_bagian"] = dict(sorted(Counter(o for o in cv.owner.values() if o).items(), key=lambda kv: -kv[1]))
        info["poses"][name] = entry
    info["warna_seluruh_tiga_pose"] = {"jumlah": len(keys_union), "kunci": sorted(keys_union)}
    # --- kontras tepi besi (k0) dan merah menyala (hr), k4 rim
    pal = hero2.monkey.PAL_HERO
    halo = tuple(hero.HERO_PAL["bb"])
    info["kontras_wcag"] = {k: {"terang": round(hc.contrast(pal[k], LIGHT), 2), "gelap": round(hc.contrast(pal[k], DARK), 2),
                                 "abu_tengah": round(hc.contrast(pal[k], GRAY), 2), "halo_krem": round(hc.contrast(pal[k], halo), 2)}
                           for k in ("k0", "k1", "k2", "k3", "k4", "br", "hr")}
    json.dump(info, open(os.path.join(OUT, "ukuran.json"), "w"), indent=2)
    print(json.dumps({k: v for k, v in info.items() if k != "legenda_bagian"}, indent=1)[:3500])


if __name__ == "__main__":
    main()
