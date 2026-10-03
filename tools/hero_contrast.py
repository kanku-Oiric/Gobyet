#!/usr/bin/env python3
"""Kontras tepi besi Berserker Hero terhadap empat latar pratinjau, dengan dan tanpa halo (hanya melaporkan; aset tidak diubah).

    python3 tools/hero_contrast.py [folder-tangkapan]

Bagian 1 (analitik): rasio luminans WCAG (L1+0,05)/(L2+0,05) antara warna tepi hero (o2 garis tepi besi, o1 garis tepi organik,
rm rim light) dan latar: terang, gelap, abu tengah #808080, serta halo krem (nada tulang `bb`, 1 px CSS) yang menggantikan latar tepat
di luar siluet. Dengan halo, yang bersebelahan dengan tepi adalah halo, bukan latar.

Bagian 2 (terukur dari hasil render, bila folder tangkapan diberikan): tangkapan layar Chromium kotak latar frame idle f0 per
kombinasi latar x halo (dibuat oleh tools/e2e_preview.js ke <keluaran>/halo/idle-<latar>[-halo].png). Tiap piksel layar sprite yang
bersebelahan (4 arah) dengan piksel bukan-sprite membentuk satu pasangan tepi; dihitung rasio kontras warna yang benar-benar tampil
pada tiap pasangan (median, persentil ke-10, minimum) dan bagian piksel luar yang berwarna halo.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

from PIL import Image  # noqa: E402

import hero  # noqa: E402
import hero_check as hc  # noqa: E402

BGS = (("terang", (250, 247, 240)), ("gelap", (24, 28, 44)), ("abu tengah", (128, 128, 128)))
HALO = hero.HERO_PAL["bb"]
KEYS = (("o2", "garis tepi besi"), ("o1", "garis tepi organik"), ("rm", "rim light baja-biru"))


def analytic():
    lines = ["kontras luminans WCAG (rasio) tepi hero terhadap latar; halo = krem %s (nada tulang bb)" % (HALO,),
             "  %-4s %-20s %9s %9s %11s | %s" % ("kunci", "", "terang", "gelap", "abu tengah", "dengan halo (tetangga tepi = halo, sama di semua latar)")]
    for key, label in KEYS:
        c = hero.HERO_PAL[key]
        lines.append("  %-4s %-20s %8.2f:1 %8.2f:1 %10.2f:1 | %.2f:1" % (
            (key, label) + tuple(hc.contrast(c, bg) for _, bg in BGS) + (hc.contrast(c, HALO),)))
    lines.append("  halo itu sendiri terhadap latar (terlihat atau tidak): " + ", ".join("%s %.2f:1" % (n, hc.contrast(HALO, bg)) for n, bg in BGS))
    return lines


def rendered(shots):
    sheet = Image.open(os.path.join(ROOT, "sheets", "berserker-hero-idle.png")).convert("RGBA")
    frame = sheet.crop((0, 0, 128, 96))
    mask = frame.getchannel("A").point(lambda a: 255 if a else 0).resize((256, 192), Image.NEAREST).load()
    lines = ["terukur dari tangkapan layar (frame idle f0, 2x, Chromium); pasangan = piksel sprite dan tetangganya yang bukan sprite"]
    lines.append("  %-11s %-6s %7s %9s %9s %9s %12s" % ("latar", "halo", "pasang", "median", "persen10", "minimum", "luar=halo"))
    for name, bg in BGS:
        for halo in (False, True):
            path = os.path.join(shots, "idle-%s%s.png" % ("abu" if name == "abu tengah" else name, "-halo" if halo else ""))
            if not os.path.exists(path):
                lines.append("  %-11s %-6s tangkapan tidak ada: %s" % (name, "ya" if halo else "tidak", os.path.relpath(path, ROOT)))
                continue
            im = Image.open(path).convert("RGB")
            if im.width != 256 or im.height not in (192, 193, 194):
                lines.append("  %-11s %-6s ukuran tangkapan %s, harus 256 x 192..194" % (name, "ya" if halo else "tidak", im.size))
                continue
            # Tata letak halaman kadang menggeser kotak latar sebesar pecahan piksel sehingga tangkapan setinggi 193: pilih baris awal
            # yang paling cocok dengan topeng sprite (piksel sprite harus berbeda dari warna latar).
            best = None
            for oy in range(im.height - 192 + 1):
                crop = im.crop((0, oy, 256, oy + 192)).load()
                score = sum(1 for y in range(192) for x in range(256) if mask[x, y] and crop[x, y] != bg)
                if best is None or score > best[0]:
                    best = (score, oy)
            im = im.crop((0, best[1], 256, best[1] + 192))
            px = im.load()
            ratios, halo_hits, outer = [], 0, 0
            for y in range(192):
                for x in range(256):
                    if not mask[x, y]:
                        continue
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < 256 and 0 <= ny < 192 and not mask[nx, ny]:
                            ratios.append(hc.contrast(px[x, y], px[nx, ny]))
                            outer += 1
                            if all(abs(a - b) <= 3 for a, b in zip(px[nx, ny], HALO)):
                                halo_hits += 1
            ratios.sort()
            n = len(ratios)
            lines.append("  %-11s %-6s %7d %8.2f:1 %8.2f:1 %8.2f:1 %11.1f%%" % (
                name, "ya" if halo else "tidak", n, ratios[n // 2], ratios[n // 10], ratios[0], 100.0 * halo_hits / max(1, outer)))
    return lines


if __name__ == "__main__":
    out = analytic()
    if len(sys.argv) > 1:
        out += [""] + rendered(os.path.abspath(sys.argv[1]))
    print("\n".join(out))
