#!/usr/bin/env python3
"""Bukti state `victory` Berserker Hero (20 frame): lembar frame, topeng dan wajah Gobyet, tusukan pedang, kaki di batu, usapan darah, frame kunci di
tiga latar, dan angka per frame. Hanya membaca kode dan aset; tidak menulis aset pack.

    python3 tools/hero3_victory.py [folder-keluaran]        # bawaan: pack/reports/hero3-victory/

Menulis:
  lembar.png              20 frame berurutan (3x, latar terang), bernomor dengan durasi; frame kunci ditandai
  topeng.png              kepala di f0-f7: topeng membuka, wajah Gobyet, menutup dengan klik (6x)
  tusuk.png               f8-f11: pedang dicabut, diangkat, menukik (smear), menancap dengan debu (3x)
  batu-dan-usapan.png     f11-f19 bagian kanan bawah: kaki naik ke batu, kepalan menyusuri bilah, noda hilang, bilah berkilau (5x)
  kunci-3-latar.png       frame kunci di latar terang, gelap, abu tengah (3x)
  victory.json            durasi, isi topeng, wajah, mata Gobyet, noda, batu, kontak kaki, tangan di pedang, posisi kepalan, ukuran berkas
Bukan pernyataan bahwa gaya bagus atau disetujui.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import hero3 as R  # noqa: E402
import hero3_check as hc  # noqa: E402
import hero3_scenes as hs  # noqa: E402

OUT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ROOT, "pack", "reports", "hero3-victory")
LIGHT, DARK, GRAY = (250, 247, 240), (24, 28, 44), (128, 128, 128)


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


def main():
    os.makedirs(OUT, exist_ok=True)
    t = hs.TRACKS["victory"]
    cvs = [t.frame(i) for i in range(t.n)]
    poses = [t.pose(i) for i in range(t.n)]
    grid([tile(cv, 3, LIGHT, "f%d %dms%s" % (i, t.duration(i), " KUNCI" if i == t.keyframe else "")) for i, cv in enumerate(cvs)], 4).save(
        os.path.join(OUT, "lembar.png"))
    tiles = []
    for i in range(0, 8):
        g = R.geometry(poses[i])
        hx, hy = int(round(g["head"][0])), int(round(g["head"][1]))
        tiles.append(tile(cvs[i], 6, LIGHT, "f%d %dms" % (i, t.duration(i)), (hx - 22, hy - 21, hx + 24, hy + 21), (0, 90, 220)))
    grid(tiles, 4).save(os.path.join(OUT, "topeng.png"))
    grid([tile(cvs[i], 3, LIGHT, "f%d %dms" % (i, t.duration(i))) for i in range(8, 12)], 4).save(os.path.join(OUT, "tusuk.png"))
    grid([tile(cvs[i], 5, LIGHT, "f%d" % i, (52, 40, 112, 92)) for i in range(11, t.n)], 3).save(os.path.join(OUT, "batu-dan-usapan.png"))
    kf = cvs[t.keyframe]
    grid([tile(kf, 3, bg, "f%d" % t.keyframe, None, ink) for bg, ink in ((LIGHT, (200, 0, 0)), (DARK, (255, 200, 120)), (GRAY, (255, 255, 0)))], 3).save(
        os.path.join(OUT, "kunci-3-latar.png"))
    series = hc.victory_series(cvs, poses)
    bad, info = hc.victory_findings(cvs, poses)
    cell = json.load(open(os.path.join(ROOT, "pack", "manifest.json"), encoding="utf-8"))["cells"]["berserker-hero"]["victory"]
    gif = os.path.getsize(os.path.join(ROOT, cell["gif"].replace("../", "")))
    sheet = os.path.getsize(os.path.join(ROOT, cell["sheet"].replace("../", "")))
    rows = []
    for i, (x, p) in enumerate(zip(series, poses)):
        g = R.geometry(p)
        rows.append({"f": i, "ms": int(t.duration(i)), "topeng": p["mask"], "isi_topeng": x["rongga"], "wajah": x["wajah"], "mata_gobyet": x["mata_gobyet"],
                     "noda": x["noda"], "batu": x["batu"], "kaki_di_batu": x["kaki_di_batu"], "tangan_di_pedang": x["tangan_di_pedang"],
                     "kepalan_kanan": [round(v, 1) for v in g["rh"]] if g["rh"] else None, "sudut_pedang": p["ang"]})
    out = {"frame": t.n, "kunci": t.keyframe, "total_ms": int(sum(t.duration(i) for i in range(t.n))), "gif_byte": gif, "sheet_byte": sheet,
           "urutan": {k: v for k, v in info.items() if k != "seri"}, "gagal": bad, "per_frame": rows}
    json.dump(out, open(os.path.join(OUT, "victory.json"), "w"), indent=2)
    print(json.dumps({k: out[k] for k in ("frame", "kunci", "total_ms", "gif_byte", "sheet_byte", "urutan", "gagal")}, indent=1))


if __name__ == "__main__":
    main()
