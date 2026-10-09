#!/usr/bin/env python3
"""Bukti animasi Berserker Hero v3 (sembilan state): lembar frame per state, sembilan frame kunci di tiga latar, urutan topeng dan usapan di victory,
dan tabel ukuran (hanya membaca kode dan aset; tidak menulis aset).

    python3 tools/hero3_animasi.py [folder-keluaran]        # bawaan: pack/reports/hero3-animasi/

Menulis:
  <state>-lembar.png      semua frame state itu berurutan (3x, latar terang), bernomor dengan durasi; frame kunci diberi tanda
  kunci-9-state.png       frame kunci tiap state di latar terang, gelap, dan abu tengah (3x)
  victory-topeng.png      kepala di frame victory tempat topeng membuka dan menutup (8x)
  victory-usapan.png      bilah dan kepalan di frame victory saat noda dihapus (6x)
  ukuran.json             frame, durasi, total ms, ukuran GIF dan sheet, seam, keterbacaan frame kunci, urutan victory
Bukan pernyataan bahwa gaya bagus atau disetujui.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import hero3_check as hc  # noqa: E402
import hero3_scenes as hs  # noqa: E402

OUT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ROOT, "pack", "reports", "hero3-animasi")
LIGHT, DARK, GRAY = (250, 247, 240), (24, 28, 44), (128, 128, 128)
ORDER = ["idle", "run", "rage", "attack-leap", "attack-smash", "miss", "exhaustion", "defeated", "victory"]


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def tile(cv, scale, bg, text=None, ink=(200, 0, 0), crop=None):
    im = cv.image(1, bg=bg).convert("RGB")
    if crop:
        im = im.crop(crop)
    im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    if text:
        ImageDraw.Draw(im).text((4, 2), text, fill=ink, font=font(13))
    return im


def grid(tiles, cols, gap=4, bg=(128, 0, 128)):
    w, h = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    out = Image.new("RGB", (cols * (w + gap) + gap, rows * (h + gap) + gap), bg)
    for k, im in enumerate(tiles):
        out.paste(im, (gap + (k % cols) * (w + gap), gap + (k // cols) * (h + gap)))
    return out


def file_size(path):
    return os.path.getsize(os.path.join(ROOT, path))


def main():
    os.makedirs(OUT, exist_ok=True)
    man = json.load(open(os.path.join(ROOT, "pack", "manifest.json"), encoding="utf-8"))
    row = man["cells"]["berserker-hero"]
    info = {"states": {}}
    keyframes = []
    for state in ORDER:
        t = hs.TRACKS[state]
        cvs = [t.frame(i) for i in range(t.n)]
        tiles = [tile(cv, 3, LIGHT, "f%d %dms%s" % (i, t.duration(i), " KUNCI" if i == t.keyframe else "")) for i, cv in enumerate(cvs)]
        grid(tiles, 4).save(os.path.join(OUT, "%s-lembar.png" % state))
        keyframes.append((state, cvs[t.keyframe]))
        cell = row[state]
        ims = [cv.image(1) for cv in cvs]
        import validate_pack as vp
        steps = [vp.diff(ims[i], ims[i + 1]) for i in range(t.n - 1)]
        seam = vp.diff(ims[-1], ims[0]) if t.loop else None
        info["states"][state] = {
            "frame": t.n, "loop": t.loop, "kunci": t.keyframe, "durasi_ms": [int(t.duration(i)) for i in range(t.n)], "total_ms": int(sum(t.duration(i) for i in range(t.n))),
            "gif_byte": file_size(cell["gif"].replace("../", "")), "sheet_byte": file_size(cell["sheet"].replace("../", "")),
            "langkah_maks_piksel": max(steps), "seam_piksel": seam, "keterbacaan_kunci": hc.readability(cvs[t.keyframe]),
        }
    # sembilan frame kunci di tiga latar
    tiles = []
    for bg, ink in ((LIGHT, (200, 0, 0)), (DARK, (255, 200, 120)), (GRAY, (255, 255, 0))):
        for state, cv in keyframes:
            tiles.append(tile(cv, 3, bg, state, ink))
    grid(tiles, 9 if False else 3).save(os.path.join(OUT, "kunci-9-state.png"))
    # victory: topeng dan usapan
    t = hs.TRACKS["victory"]
    cvs = [t.frame(i) for i in range(t.n)]
    poses = [t.pose(i) for i in range(t.n)]
    series = hc.victory_series(cvs, poses)
    mask_frames = [i for i, x in enumerate(series) if x["rongga"] > 0] or [0]
    mask_frames = [max(0, mask_frames[0] - 1)] + mask_frames + [min(t.n - 1, mask_frames[-1] + 1)]
    tiles = []
    for i in mask_frames:
        g = __import__("hero3").geometry(poses[i])
        hx, hy = int(round(g["head"][0])), int(round(g["head"][1]))
        tiles.append(tile(cvs[i], 8, LIGHT, "f%d rongga %d px" % (i, series[i]["rongga"]), crop=(hx - 22, hy - 22, hx + 24, hy + 22)))
    grid(tiles, 3).save(os.path.join(OUT, "victory-topeng.png"))
    wipe = [i for i, x in enumerate(series) if x["kaki_di_batu"] >= hc.MIN_FOOT_CONTACT]
    tiles = [tile(cvs[i], 6, LIGHT, "f%d noda %d px" % (i, series[i]["noda"]), crop=(40, 40, 110, 92)) for i in wipe]
    grid(tiles, 3).save(os.path.join(OUT, "victory-usapan.png"))
    bad, vinfo = hc.victory_findings(cvs, poses)
    info["victory"] = {"gagal": bad, "urutan": {k: v for k, v in vinfo.items() if k != "seri"}, "seri": [{k: (list(v) if isinstance(v, tuple) else v) for k, v in x.items()} for x in series]}
    total_gif = sum(s["gif_byte"] for s in info["states"].values())
    total_sheet = sum(s["sheet_byte"] for s in info["states"].values())
    info["ukuran_total"] = {"gif": total_gif, "sheet": total_sheet, "gif_dan_sheet": total_gif + total_sheet, "batas_total": 2000000, "batas_per_gif": 262144}
    json.dump(info, open(os.path.join(OUT, "ukuran.json"), "w"), indent=2)
    print(json.dumps({"ukuran_total": info["ukuran_total"], "victory_gagal": bad, "victory_urutan": info["victory"]["urutan"]}, indent=1))


if __name__ == "__main__":
    main()
