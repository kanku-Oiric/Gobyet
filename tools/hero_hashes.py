#!/usr/bin/env python3
"""Tulis pack/sha256-hero.txt: hash SHA-256 semua aset Berserker Hero (gif/ dan sheets/ berawalan berserker-hero-).

    python3 tools/hero_hashes.py            # tulis ulang berkas kunci
    python3 tools/hero_hashes.py --check    # hanya periksa, kode keluar 1 bila ada yang berbeda

Berkas ini berdiri sendiri: tiga berkas kunci lama (sha256-asli.txt, -disetujui.txt, -dibuat.txt) tidak disentuh.
"""
import glob
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "pack", "sha256-hero.txt")


def files():
    return sorted(glob.glob(os.path.join(ROOT, "gif", "berserker-hero-*.gif")) + glob.glob(os.path.join(ROOT, "sheets", "berserker-hero-*.png")))


def lines():
    return ["%s  %s\n" % (hashlib.sha256(open(f, "rb").read()).hexdigest(), os.path.relpath(f, ROOT)) for f in files()]


if __name__ == "__main__":
    want = lines()
    if "--check" in sys.argv:
        have = open(OUT, encoding="utf-8").readlines() if os.path.exists(OUT) else []
        print("%d berkas; %s" % (len(want), "sama dengan %s" % os.path.relpath(OUT, ROOT) if have == want else "BERBEDA dari berkas kunci"))
        sys.exit(0 if have == want else 1)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.writelines(want)
    print("%s: %d berkas" % (os.path.relpath(OUT, ROOT), len(want)))
