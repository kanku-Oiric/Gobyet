#!/usr/bin/env python3
"""Bukti revisi Berserker Hero v3 setelah fase animasi (keputusan pemilik): perisai naga, wajah Gobyet di balik topeng, darah monster merah,
tepi terang, ekor sedang di state serangan, dan anggaran 2 MB. Hanya membaca kode dan aset; tidak menulis aset pack.

    python3 tools/hero3_revisi.py [folder-keluaran]        # bawaan: pack/reports/hero3-revisi/

Menulis (selain keluaran tools/hero3_animasi.py di folder yang sama: lembar per state, kunci-9-state, victory-topeng, victory-usapan, ukuran.json):
  perisai-naga.png        perisai naga pose idle 8x di latar terang dan gelap, dan pose run serta attack-smash 4x
  wajah-gobyet.png        helm dengan topeng 0, 25, 50, 75, 100% terbuka (visor look dan angry) dan frame victory f1-f5, 8x
  tepi-terang.png         idle dan attack-smash di latar terang, gelap, abu tengah: tanpa tepi terang (kiri) dan dengan (kanan), 3x
  ekor-serangan.png       frame tumbukan attack-leap, attack-smash, miss dengan ekor ditandai, dan idle sebagai pembanding, 3x
  darah-monster.png       bilah di frame victory f11, f14, f16, f18, f19, 6x
  revisi.json             ukuran perisai, wajah, tepi terang, ekor, warna darah, ukuran berkas dan anggaran
Bukan pernyataan bahwa gaya bagus atau disetujui.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import hero3 as R  # noqa: E402
import hero3_check as hc  # noqa: E402
import hero3_scenes as hs  # noqa: E402
import monkey  # noqa: E402

OUT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ROOT, "pack", "reports", "hero3-revisi")
LIGHT, DARK, GRAY = (250, 247, 240), (24, 28, 44), (128, 128, 128)
SHIELD = hc.SHIELD_PARTS


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def tile(cv, scale, bg, text=None, crop=None, ink=(200, 0, 0)):
    im = cv.image(1, bg=bg).convert("RGB")
    if crop:
        im = im.crop(crop)
    im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    if text:
        ImageDraw.Draw(im).text((4, 2), text, fill=ink, font=font(13))
    return im


def grid(tiles, cols, gap=4, bg=(128, 0, 128)):
    w = max(t.width for t in tiles)
    h = max(t.height for t in tiles)
    rows = (len(tiles) + cols - 1) // cols
    out = Image.new("RGB", (cols * (w + gap) + gap, rows * (h + gap) + gap), bg)
    for k, im in enumerate(tiles):
        out.paste(im, (gap + (k % cols) * (w + gap), gap + (k // cols) * (h + gap)))
    return out


def no_rim(cv):
    """Salinan kanvas tanpa piksel tepi terang (untuk bandingan sebelum-sesudah)."""
    out = R.PartCanvas()
    for k, c in cv.px.items():
        if cv.owner.get(k) != "rim":
            out.px[k] = c
            out.owner[k] = cv.owner.get(k)
    return out


def bbox_of(cv, parts):
    pts = [k for k, o in cv.owner.items() if o in parts and k in cv.px]
    xs, ys = [x for x, _ in pts], [y for _, y in pts]
    return (min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1) if pts else None


def main():
    os.makedirs(OUT, exist_ok=True)
    subprocess.run([sys.executable, os.path.join(HERE, "hero3_animasi.py"), OUT], check=True, stdout=subprocess.DEVNULL)
    info = {}
    # perisai naga
    idle = R.render_pose(R.pose_idle())
    b = bbox_of(idle, SHIELD)
    crop = (max(0, b[0] - 3), max(0, b[1] - 3), b[0] + b[2] + 3, b[1] + b[3] + 3)
    tiles = [tile(idle, 8, LIGHT, "idle 8x", crop), tile(idle, 8, DARK, "latar gelap", crop, (255, 200, 120))]
    row2 = [tile(R.render_pose(R.KEYPOSES[n]()), 4, LIGHT, n) for n in ("run", "attack-smash")]
    a = grid(tiles, 2)
    c = grid(row2, 2)
    o = Image.new("RGB", (max(a.width, c.width), a.height + c.height), (128, 0, 128))
    o.paste(a, (0, 0))
    o.paste(c, (0, a.height))
    o.save(os.path.join(OUT, "perisai-naga.png"))
    counts = {p: hc.count(idle, (p,)) for p in SHIELD}
    info["perisai_naga"] = {"kotak_idle": {"x": b[0], "y": b[1], "lebar": b[2], "tinggi": b[3]}, "piksel_idle": counts, "total_idle": sum(counts.values()),
                            "per_state_kunci": {st: hc.readability(t.frame(t.keyframe))["perisai"] for st, t in hs.TRACKS.items()}}
    # wajah Gobyet di balik topeng
    tiles = []
    for eyes in ("look", "angry"):
        for m in (0.0, 0.25, 0.5, 0.75, 1.0):
            cv = R.PartCanvas()
            R.helm3(cv, 30, 30, eyes, "closed", 0.0, m)
            tiles.append(tile(cv, 8, LIGHT, "%s %d%%" % (eyes, int(m * 100)), (8, 8, 54, 50)))
    t = hs.TRACKS["victory"]
    for i in range(1, 6):
        p = t.pose(i)
        g = R.geometry(p)
        hx, hy = int(round(g["head"][0])), int(round(g["head"][1]))
        tiles.append(tile(t.frame(i), 8, LIGHT, "victory f%d" % i, (hx - 22, hy - 21, hx + 24, hy + 21)))
    grid(tiles, 5).save(os.path.join(OUT, "wajah-gobyet.png"))
    series = hc.victory_series([t.frame(i) for i in range(t.n)], [t.pose(i) for i in range(t.n)])
    info["wajah_gobyet"] = {"per_frame_victory": [{"f": i, "isi_topeng": x["rongga"], "wajah": x["wajah"], "mata": x["mata_gobyet"]} for i, x in enumerate(series)],
                            "kunci_warna": sorted(R.GOBYET_FACE_KEYS), "ekspresi_puncak": list(t.pose(3)["face"] or [])}
    # tepi terang
    tiles = []
    for n in ("idle", "attack-smash"):
        cv = R.render_pose(R.KEYPOSES[n]())
        for bg, ink in ((LIGHT, (200, 0, 0)), (DARK, (255, 200, 120)), (GRAY, (255, 255, 0))):
            tiles.append(tile(no_rim(cv), 3, bg, "%s tanpa tepi" % n, None, ink))
            tiles.append(tile(cv, 3, bg, "%s dengan tepi" % n, None, ink))
    grid(tiles, 2).save(os.path.join(OUT, "tepi-terang.png"))
    pal = monkey.PAL_HERO
    info["tepi_terang"] = {"warna": R.RIM_COLOR, "rgb": list(pal[R.RIM_COLOR]), "kontras": {"terang": hc.contrast(pal["n4"], LIGHT), "gelap": hc.contrast(pal["n4"], DARK),
                                                                                        "abu_tengah": hc.contrast(pal["n4"], GRAY)},
                           "garis_hitam_n0_tanpa_tepi": {"terang": hc.contrast(pal["n0"], LIGHT), "gelap": hc.contrast(pal["n0"], DARK), "abu_tengah": hc.contrast(pal["n0"], GRAY)},
                           "piksel_tepi_idle": hc.count(idle, ("rim",)),
                           "tepi_gelap_tanpa_tepi_terang_semua_frame": sum(hc.dark_edge_unlit(tr.frame(i)) for tr in hs.TRACKS.values() for i in range(tr.n))}
    # ekor
    ref = hc.count(hs.TRACKS["idle"].frame(0), ("tail_arrow",))
    tiles = [tile(hs.TRACKS["idle"].frame(0), 3, LIGHT, "idle f0 ekor %d px" % ref)]
    tail = {"idle_f0": ref}
    for st in ("attack-leap", "attack-smash", "miss"):
        tr = hs.TRACKS[st]
        cv = tr.frame(tr.keyframe)
        k = hc.count(cv, ("tail_arrow",))
        tail[st] = {"frame_kunci": tr.keyframe, "piksel": k, "persen_idle": round(100.0 * k / ref, 1), "puncak": list(hs.TAIL_PEAK[st][0]), "bobot_per_frame": hs.TAIL_PEAK[st][1]}
        mark = R.PartCanvas()
        for kk, c in cv.px.items():
            mark.px[kk] = "q4" if cv.owner.get(kk) == "tail_arrow" else c
            mark.owner[kk] = cv.owner.get(kk)
        tiles.append(tile(mark, 3, LIGHT, "%s f%d ekor %d px (%d%%)" % (st, tr.keyframe, k, round(100.0 * k / ref))))
    grid(tiles, 2).save(os.path.join(OUT, "ekor-serangan.png"))
    info["ekor"] = tail
    # darah monster
    tiles = []
    for i in (11, 14, 16, 18, 19):
        tiles.append(tile(t.frame(i), 6, LIGHT, "f%d noda %d px" % (i, series[i]["noda"]), (60, 34, 116, 92)))
    grid(tiles, 5).save(os.path.join(OUT, "darah-monster.png"))
    info["darah_monster"] = {k: list(pal[k]) for k in ("m1", "m2", "m3")}
    # ukuran
    man = json.load(open(os.path.join(ROOT, "pack", "manifest.json"), encoding="utf-8"))
    row = man["cells"]["berserker-hero"]
    sizes = {}
    for st, cell in row.items():
        sizes[st] = {"gif": os.path.getsize(os.path.join(ROOT, cell["gif"].replace("../", ""))), "sheet": os.path.getsize(os.path.join(ROOT, cell["sheet"].replace("../", "")))}
    total = sum(v["gif"] + v["sheet"] for v in sizes.values())
    info["ukuran"] = {"per_state": sizes, "total_gif_dan_sheet": total, "batas_total": 2000000, "gif_terbesar": max(v["gif"] for v in sizes.values()), "batas_per_gif": 307200}
    json.dump(info, open(os.path.join(OUT, "revisi.json"), "w"), indent=2)
    print(json.dumps({"perisai_idle": info["perisai_naga"]["total_idle"], "kotak": info["perisai_naga"]["kotak_idle"], "ekor": {k: (v if isinstance(v, int) else v["persen_idle"]) for k, v in tail.items()},
                      "tepi_gelap_tanpa_tepi": info["tepi_terang"]["tepi_gelap_tanpa_tepi_terang_semua_frame"], "ukuran_total": total, "gif_terbesar": info["ukuran"]["gif_terbesar"]}, indent=1))


if __name__ == "__main__":
    main()
