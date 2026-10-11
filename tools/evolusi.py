#!/usr/bin/env python3
"""Galeri evolusi Berserker Hero (keputusan pemilik: kode v1 dan v2 disimpan dan diunggah sebagai evolusi).

    python3 tools/evolusi.py            # tulis pack/evolusi/ dan pack/sha256-evolusi.txt
    python3 tools/evolusi.py --check    # hanya periksa hash; kode keluar 1 bila berbeda

Isi pack/evolusi/:
  v1/berserker-hero-<state>.gif     8 GIF hero v1 (Gobyet berhelm tengkorak naga), byte persis dari commit V1_COMMIT (diambil dengan git show)
  v2/berserker-hero-v2-<pose>.png   3 pose kunci hero v2 (Gobyet berzirah hitam-merah; ditolak pemilik), render ulang dari src/hero2.py, 4x
  v1/berserker-hero-v1-<pose>.png   3 pose kunci hero v1 dari src/hero.py, 4x (pembanding statis dengan v2 dan v3)
  v3/berserker-hero-v3-<pose>.png   3 pose kunci hero v3 sekarang dari src/hero3.py, 4x
GIF v3 tidak disalin: halaman evolusi memakai ../../gif/berserker-hero-*.gif (aset pack yang sedang dikerjakan).
Aset di sini bukan bagian manifest dan tidak dihitung dalam anggaran hero (GIF + sheet di gif/ dan sheets/).
"""
import hashlib
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

OUT = os.path.join(ROOT, "pack", "evolusi")
HASHES = os.path.join(ROOT, "pack", "sha256-evolusi.txt")
V1_COMMIT = "fd5d899"            # commit terakhir yang masih memuat GIF hero v1 (8 state) di gif/
V1_STATES = ("idle", "run", "rage", "attack-leap", "attack-smash", "miss", "exhaustion", "defeated")
POSES = ("idle", "run", "attack-smash")
SCALE = 4


def git_bytes(path):
    return subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (V1_COMMIT, path)], check=True, capture_output=True).stdout


def v1_locked():
    """Hash GIF v1 yang tercatat di sha256-hero.txt pada commit V1_COMMIT."""
    out = {}
    for line in git_bytes("pack/sha256-hero.txt").decode("utf-8").splitlines():
        h, name = line.split()
        out[name] = h
    return out


def png_bytes(cv):
    im = cv.image(SCALE)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return buf.getvalue()


def build():
    import hero
    import hero2
    import hero3
    files = {}
    locked = v1_locked()
    for s in V1_STATES:
        src = "gif/berserker-hero-%s.gif" % s
        data = git_bytes(src)
        if hashlib.sha256(data).hexdigest() != locked[src]:
            raise SystemExit("GIF v1 %s tidak sama dengan hash terkunci di %s" % (src, V1_COMMIT))
        files["v1/berserker-hero-%s.gif" % s] = data
    for tag, mod in (("v1", hero), ("v2", hero2), ("v3", hero3)):
        for name in POSES:
            files["%s/berserker-hero-%s-%s.png" % (tag, tag, name)] = png_bytes(mod.render_pose(mod.KEYPOSES[name]()))
    return files


def lines_of(files):
    return ["%s  pack/evolusi/%s\n" % (hashlib.sha256(files[k]).hexdigest(), k) for k in sorted(files)]


def on_disk():
    files = {}
    for dirpath, _, names in os.walk(OUT):
        for n in names:
            if n.endswith((".gif", ".png")):
                p = os.path.join(dirpath, n)
                files[os.path.relpath(p, OUT)] = open(p, "rb").read()
    return files


if __name__ == "__main__":
    if "--check" in sys.argv:
        have = open(HASHES, encoding="utf-8").readlines() if os.path.exists(HASHES) else []
        now = lines_of(on_disk())
        print("%d berkas evolusi; %s" % (len(now), "sama dengan pack/sha256-evolusi.txt" if have == now else "BERBEDA dari pack/sha256-evolusi.txt"))
        sys.exit(0 if have == now else 1)
    files = build()
    for k, data in files.items():
        p = os.path.join(OUT, k)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(data)
    with open(HASHES, "w", encoding="utf-8") as f:
        f.writelines(lines_of(files))
    total = sum(len(v) for v in files.values())
    print("pack/evolusi: %d berkas, %d byte; pack/sha256-evolusi.txt ditulis" % (len(files), total))
