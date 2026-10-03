#!/usr/bin/env python3
"""Fase C/D Berserker Hero: lembar kontak per state, lembar frame kunci, siluet isi hitam, dan tabel ukuran.

    python3 tools/hero_phase_d.py [folder-keluaran]        # bawaan: pack/reports/hero-fase-cd/

Hanya membaca aset hasil ekspor (sheets/berserker-hero-*.png dan gif/) lewat pack/manifest.json; tidak menulis aset.
Menulis: kontak-<state>.png (latar terang) dan kontak-<state>-gelap.png (frame bernomor, durasi, kunci berbingkai, 2x),
kunci-8-state.png, siluet-kunci.png, ukuran.json. Gambar ini bahan penilaian gaya; bukan pernyataan gaya bagus atau disetujui.
"""
import json
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ROOT, "pack", "reports", "hero-fase-cd")
LIGHT, DARK = (250, 247, 240), (24, 28, 44)
ORDER = ["idle", "run", "rage", "attack-leap", "attack-smash", "miss", "exhaustion", "defeated"]
HERO = "berserker-hero"


def load():
    m = json.load(open(os.path.join(ROOT, "pack", "manifest.json"), encoding="utf-8"))
    out = {}
    for state in ORDER:
        c = m["cells"][HERO][state]
        sheet = Image.open(os.path.normpath(os.path.join(ROOT, "pack", c["sheet"]))).convert("RGBA")
        w, h = c["canvas"]["w"], c["canvas"]["h"]
        out[state] = (c, [sheet.crop((i * w, 0, (i + 1) * w, h)) for i in range(c["frames"])])
    return out


def paste(bg, fr, scale=2):
    base = Image.new("RGBA", fr.size, bg + (255,))
    base.alpha_composite(fr)
    return base.convert("RGB").resize((fr.width * scale, fr.height * scale), Image.NEAREST)


def label(im, text, ink):
    ImageDraw.Draw(im).text((5, 3), text, fill=ink)


def contact(cell, frames, bg, cols=4, scale=2):
    ink = (200, 0, 0) if bg == LIGHT else (255, 200, 120)
    w, h = frames[0].width * scale, frames[0].height * scale
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (w + 6) + 6, rows * (h + 6) + 6), (128, 128, 128))
    for i, fr in enumerate(frames):
        im = paste(bg, fr, scale)
        label(im, "%d  %d ms%s" % (i, cell["durations_ms"][i], "  KUNCI" if i == cell["keyframe"] else ""), ink)
        if i == cell["keyframe"]:
            d = ImageDraw.Draw(im)
            d.rectangle((0, 0, w - 1, h - 1), outline=(47, 95, 168), width=3)
        sheet.paste(im, (6 + (i % cols) * (w + 6), 6 + (i // cols) * (h + 6)))
    return sheet


def silhouette(fr, color):
    px = fr.load()
    im = Image.new("RGBA", fr.size, (0, 0, 0, 0))
    out = im.load()
    for y in range(fr.height):
        for x in range(fr.width):
            if px[x, y][3]:
                out[x, y] = color + (255,)
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    data = load()
    for state in ORDER:
        cell, frames = data[state]
        contact(cell, frames, LIGHT).save(os.path.join(OUT, "kontak-%s.png" % state))
        contact(cell, frames, DARK).save(os.path.join(OUT, "kontak-%s-gelap.png" % state))
    keys = [(s, data[s][1][data[s][0]["keyframe"]]) for s in ORDER]
    w, h = 256, 192
    sheet = Image.new("RGB", (4 * (w + 6) + 6, 4 * (h + 6) + 6), (128, 128, 128))
    for k, (s, fr) in enumerate(keys):
        for r, bg in enumerate((LIGHT, DARK)):
            im = paste(bg, fr)
            label(im, "%s f%d" % (s, data[s][0]["keyframe"]), (200, 0, 0) if bg == LIGHT else (255, 200, 120))
            sheet.paste(im, (6 + (k % 4) * (w + 6), 6 + ((k // 4) * 2 + r) * (h + 6)))
    sheet.save(os.path.join(OUT, "kunci-8-state.png"))
    sil = Image.new("RGB", (4 * (w + 6) + 6, 4 * (h + 6) + 6), (128, 128, 128))
    for k, (s, fr) in enumerate(keys):
        for r, (bg, col) in enumerate(((LIGHT, (0, 0, 0)), (DARK, (0, 0, 0)))):
            im = paste(bg, silhouette(fr, col))
            label(im, "%s siluet isi hitam" % s, (200, 0, 0) if bg == LIGHT else (255, 200, 120))
            sil.paste(im, (6 + (k % 4) * (w + 6), 6 + ((k // 4) * 2 + r) * (h + 6)))
    sil.save(os.path.join(OUT, "siluet-kunci.png"))
    table = []
    for s in ORDER:
        cell, frames = data[s]
        gif = os.path.normpath(os.path.join(ROOT, "pack", cell["gif"]))
        table.append({"state": s, "frames": cell["frames"], "loop": cell["loop"], "keyframe": cell["keyframe"],
                      "durations_ms": cell["durations_ms"], "total_ms": sum(cell["durations_ms"]), "gif_bytes": os.path.getsize(gif),
                      "gif_px": list(Image.open(gif).size), "sheet_px": [frames[0].width * len(frames), frames[0].height]})
    json.dump({"states": table, "gif_bytes_total": sum(t["gif_bytes"] for t in table)}, open(os.path.join(OUT, "ukuran.json"), "w"), indent=2)
    for t in table:
        print("%-13s %2d frame %5d ms  kunci f%-2d  GIF %6d byte  %s" % (t["state"], t["frames"], t["total_ms"], t["keyframe"], t["gif_bytes"], "loop" if t["loop"] else "tidak loop"))
    print("total GIF %d byte; gambar di %s" % (sum(t["gif_bytes"] for t in table), os.path.relpath(OUT, ROOT)))


if __name__ == "__main__":
    main()
