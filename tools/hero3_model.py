#!/usr/bin/env python3
"""Berserker Hero v3 (tanpa basis Gobyet): tiga pose kunci, peta bagian, emosi visor, siluet, ukuran, dan lembar bukti (hanya membaca kode; tidak menulis aset).

    python3 tools/hero3_model.py [folder-keluaran]        # bawaan: pack/reports/hero3-model/

Menulis:
  kunci-3-pose.png        idle, run, attack-smash pada latar terang, gelap, dan abu tengah, 4x
  detail-<pose>-8x.png    tiap pose 8x
  kepala-12x.png          kepala dan helm idle 12x, latar terang dan gelap
  emosi-visor.png         sembilan ekspresi visor (look, angry, rage + mulut terbuka, wide, glare, dim, tired, shut, x), 6x
  siluet.png              siluet isi hitam tiga pose (latar terang dan abu tengah)
  bandingan-v2-v3.png     v2 (ditolak) dan v3 berdampingan, 5x
  peta-bagian.png         idle 6x dengan nomor bagian; daftar nomor ada di ukuran.json dan laporan
  ukuran.json             proporsi, kotak pembatas, palet, kontras (angka heuristik)
Bukan pernyataan bahwa gaya bagus atau disetujui.
"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import hero  # noqa: E402
import hero2  # noqa: E402  (v2 yang ditolak, hanya untuk perbandingan)
import hero3  # noqa: E402
import hero_check as hc  # noqa: E402

OUT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ROOT, "pack", "reports", "hero3-model")
LIGHT, DARK, GRAY = (250, 247, 240), (24, 28, 44), (128, 128, 128)
POSES = ["idle", "run", "attack-smash"]
W, HGT = hero3.H.W, hero3.H.H
FX_PARTS = {"dust", "chip", "burst", "smear", "block", "speed", "sweat", "breath", "spark", "roar"}
HEAD_PARTS = {"crest", "helm", "brow_band", "visor", "visor_plate", "sensor", "fin", "ear_disc", "cheek", "grill", "chin"}
TORSO_PARTS = {"collar", "chest", "belly", "belt", "buckle", "hip_plate", "pauldron_big", "horn_fin", "face_panel", "ring", "claw", "pauldron_small", "upper_arm",
               "vambrace", "elbow", "gauntlet"}
LEG_PARTS = {"thigh", "shin", "knee", "boot"}
PART_LABELS = [  # (nomor, nama bagian, bagian pemilik piksel, keterangan)
    (1, "jambul merah darah", {"crest"}, "lima bilah menyapu ke belakang-atas, tiga nada merah gelap"),
    (2, "kubah helm + plat sensor", {"helm", "sensor"}, "besi hitam, jahitan miring, baut"),
    (3, "alis V merah menyala", {"brow_band"}, "garis V di atas wajah"),
    (4, "visor salib", {"visor", "visor_plate"}, "salib merah menyala; lengan datar = mata"),
    (5, "grill mulut", {"grill"}, "tiga celah; terbuka bercahaya saat berteriak"),
    (6, "sayap helm", {"fin"}, "sirip runcing di sisi depan"),
    (7, "cakram telinga mekanis", {"ear_disc", "cheek"}, "cakram baja dan ventilasi pipi"),
    (8, "pelindung bahu raksasa", {"pauldron_big"}, "cangkang bersudut bergaris merah"),
    (9, "sirip tanduk bahu", {"horn_fin"}, "dua sirip tinggi bertulang merah"),
    (10, "panel wajah mesin", {"face_panel"}, "dua jendela mata merah"),
    (11, "cincin inti merah + cakar", {"ring", "claw"}, "cincin baja berinti merah; tiga cakar merah"),
    (12, "pelindung bahu bundar", {"pauldron_small"}, "cakram berlapis cincin"),
    (13, "dada bergaris merah", {"chest", "collar"}, "bingkai merah tipis, garis V, inti cahaya"),
    (14, "perut sisik heksagonal", {"belly"}, "pola sisik merah darah"),
    (15, "sabuk + gesper", {"belt", "buckle"}, "gesper bercahaya"),
    (16, "pelat pinggul", {"hip_plate"}, "ujung bergaris merah"),
    (17, "sepatu besar", {"boot", "knee", "thigh", "shin"}, "penutup ujung, bibir merah"),
    (18, "ekor kipas panah", {"tail_arrow"}, "dua busur panah merah menyala"),
    (19, "kepalan baja", {"gauntlet"}, "manset merah, buku jari"),
    (20, "pedang agung hitam inti api", {"weapon"}, "bilah lebar 19 px, tepi api merah, pelindung, gagang bergaris merah"),
]
EMOTES = [("look", "closed"), ("angry", "closed"), ("rage", "shout"), ("wide", "closed"), ("glare", "closed"), ("dim", "closed"), ("tired", "closed"),
          ("shut", "closed"), ("x", "closed")]


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def pose_cv(name, fx=True):
    p = hero3.KEYPOSES[name]()
    if not fx:
        p = dict(p, fx=())
    return p, hero3.render_pose(p)


def paste(bg, cv, scale):
    return cv.image(1, bg=bg).convert("RGB").resize((W * scale, HGT * scale), Image.NEAREST)


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
    w, h = W * sc, HGT * sc
    sheet = Image.new("RGB", (3 * (w + 6) + 6, 3 * (h + 6) + 6), (128, 0, 128))
    for c, name in enumerate(POSES):
        p, cv = pose_cv(name)
        for r, (bg, ink) in enumerate(((LIGHT, (200, 0, 0)), (DARK, (255, 200, 120)), (GRAY, (255, 255, 0)))):
            im = paste(bg, cv, sc)
            label(im, name, ink)
            sheet.paste(im, (6 + c * (w + 6), 6 + r * (h + 6)))
        paste(LIGHT, cv, 8).save(os.path.join(OUT, "detail-%s-8x.png" % name))
    sheet.save(os.path.join(OUT, "kunci-3-pose.png"))

    # --- kepala 12x
    p, cv = pose_cv("idle", fx=False)
    box = (30, 0, 100, 62)
    ims = [cv.image(1, bg=bg).convert("RGB").crop(box) for bg in (LIGHT, DARK)]
    ims = [i.resize((i.width * 12, i.height * 12), Image.NEAREST) for i in ims]
    o = Image.new("RGB", (ims[0].width * 2 + 6, ims[0].height), (128, 0, 128))
    o.paste(ims[0], (0, 0))
    o.paste(ims[1], (ims[0].width + 6, 0))
    o.save(os.path.join(OUT, "kepala-12x.png"))

    # --- emosi visor 6x
    tw, th = 52, 46
    s6 = 6
    emo = Image.new("RGB", (3 * (tw * s6 + 6) + 6, 3 * (th * s6 + 6) + 6), (128, 0, 128))
    for i, (style, mouth) in enumerate(EMOTES):
        cv = hero3.PartCanvas()
        hero3.helm3(cv, 24, 22, style, mouth)
        im = cv.image(1, bg=LIGHT).convert("RGB").crop((0, 0, tw, th)).resize((tw * s6, th * s6), Image.NEAREST)
        label(im, style + (" + mulut terbuka" if mouth == "shout" else ""), (200, 0, 0))
        emo.paste(im, (6 + (i % 3) * (tw * s6 + 6), 6 + (i // 3) * (th * s6 + 6)))
    emo.save(os.path.join(OUT, "emosi-visor.png"))

    # --- siluet isi hitam
    sil = Image.new("RGB", (3 * (w + 6) + 6, 2 * (h + 6) + 6), (128, 0, 128))
    for c, name in enumerate(POSES):
        p, cv = pose_cv(name)
        for r, bg in enumerate((LIGHT, GRAY)):
            im = Image.new("RGB", (W, HGT), bg)
            px = im.load()
            for (x, y) in cv.px:
                px[x, y] = (0, 0, 0)
            sil.paste(im.resize((w, h), Image.NEAREST), (6 + c * (w + 6), 6 + r * (h + 6)))
    sil.save(os.path.join(OUT, "siluet.png"))

    # --- bandingan v2 (ditolak) dan v3
    s5 = 5
    v2 = hero2.render_pose(hero2.pose_idle())
    v3 = hero3.render_pose(hero3.pose_idle())
    cmp_ = Image.new("RGB", (2 * (W * s5 + 6) + 6, 2 * (HGT * s5 + 6) + 6), (128, 0, 128))
    for r, (bg, ink) in enumerate(((LIGHT, (200, 0, 0)), (DARK, (255, 200, 120)))):
        for c, (cv, name) in enumerate(((v2, "v2 (ditolak)"), (v3, "v3 tanpa basis Gobyet"))):
            im = paste(bg, cv, s5)
            label(im, name, ink)
            cmp_.paste(im, (6 + c * (W * s5 + 6), 6 + r * (HGT * s5 + 6)))
    cmp_.save(os.path.join(OUT, "bandingan-v2-v3.png"))

    # --- peta bagian (idle 6x) dengan nomor
    p, cv = pose_cv("idle", fx=False)
    base = paste(LIGHT, cv, s5 + 1)
    s6 = s5 + 1
    d = ImageDraw.Draw(base)
    f = font(15)
    used = []
    legend = []
    for num, name, parts, note in PART_LABELS:
        pts = owners(cv, parts)
        if not pts:
            continue
        cx_ = sum(x for x, _ in pts) / float(len(pts))
        cy_ = sum(y for _, y in pts) / float(len(pts))
        ax, ay = min(pts, key=lambda q: (q[0] - cx_) ** 2 + (q[1] - cy_) ** 2)
        X, Y = ax * s6 + s6 // 2, ay * s6 + s6 // 2
        for ux, uy in used:
            if abs(ux - X) < 22 and abs(uy - Y) < 22:
                Y += 22
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
        allp = [k for k, o in cv.owner.items() if o not in FX_PARTS and o not in ("tail_arrow", "weapon")]
        xs = [x for x, _ in allp]
        ys = [y for _, y in allp]
        full = [k for k in cv.px]
        entry = {"kotak_badan_tanpa_ekor_pedang": [min(xs), min(ys), max(xs), max(ys)], "tinggi_badan": max(ys) - min(ys) + 1, "lebar_badan": max(xs) - min(xs) + 1,
                 "kotak_semua_piksel": [min(x for x, _ in full), min(y for _, y in full), max(x for x, _ in full), max(y for _, y in full)]}
        entry["rentang_y"] = {"kepala_jambul": yrange(cv, HEAD_PARTS), "badan_bahu_perut": yrange(cv, TORSO_PARTS), "kaki_sepatu": yrange(cv, LEG_PARTS)}
        total = max(ys) - min(ys) + 1
        chin_y = yrange(cv, {"helm"})[1]                       # dasar helm = dagu
        belt_y = yrange(cv, {"belt"})[1]
        top = min(ys)
        bottom = max(ys)
        entry["proporsi_vertikal_persen"] = {"kepala_dan_jambul": round(100.0 * (chin_y - top + 1) / total, 1),
                                              "dagu_ke_sabuk": round(100.0 * (belt_y - chin_y) / total, 1),
                                              "sabuk_ke_lantai": round(100.0 * (bottom - belt_y) / total, 1)}
        hxr = xrange(cv, {"helm"})
        entry["lebar_helm"] = hxr[1] - hxr[0] + 1
        entry["lebar_pelindung_bahu_raksasa"] = (lambda r: r[1] - r[0] + 1)(xrange(cv, {"pauldron_big"}))
        entry["lebar_bilah_px"] = 2 * hero3.BLADE_HW
        entry["warna_dipakai"] = sorted(set(cv.px.values()))
        keys_union |= set(cv.px.values())
        cnt = Counter(cv.px.values())
        tot = float(sum(cnt.values()))
        red = sum(v for k, v in cnt.items() if k in ("q0", "q1", "q2", "q3", "q4"))
        blk = sum(v for k, v in cnt.items() if k in ("n0", "n1", "n2", "n3", "n4"))
        entry["rasio_warna_persen"] = {"merah_q0_q4": round(100.0 * red / tot, 1), "besi_hitam_n0_n4": round(100.0 * blk / tot, 1),
                                       "lain": round(100.0 * (tot - red - blk) / tot, 1)}
        entry["piksel_per_bagian"] = dict(sorted(Counter(o for o in cv.owner.values() if o).items(), key=lambda kv: -kv[1]))
        info["poses"][name] = entry
    info["warna_seluruh_tiga_pose_tanpa_efek"] = {"jumlah": len(keys_union), "kunci": sorted(keys_union)}
    # --- kontras warna kunci terhadap latar
    pal = hero3.monkey.PAL_HERO
    halo = tuple(hero.HERO_PAL["bb"])
    info["kontras_wcag"] = {k: {"terang": round(hc.contrast(pal[k], LIGHT), 2), "gelap": round(hc.contrast(pal[k], DARK), 2),
                                 "abu_tengah": round(hc.contrast(pal[k], GRAY), 2), "halo_krem": round(hc.contrast(pal[k], halo), 2)}
                           for k in ("n0", "n1", "n2", "n3", "n4", "q1", "q2", "q3", "q4")}
    json.dump(info, open(os.path.join(OUT, "ukuran.json"), "w"), indent=2)
    print(json.dumps({k: v for k, v in info.items() if k != "legenda_bagian"}, indent=1)[:3000])


if __name__ == "__main__":
    main()
