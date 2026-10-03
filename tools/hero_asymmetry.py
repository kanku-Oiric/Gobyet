#!/usr/bin/env python3
"""Bukti asimetri Berserker Hero: untuk tiap frame tiap state, centroid x piksel elemen asimetris relatif titik tengah badan.

    python3 tools/hero_asymmetry.py [berkas-keluaran.txt]

dx < 0 = kiri titik tengah badan (hero.geometry tcx), dx > 0 = kanan. Elemen yang diminta pemilik: bahu berlapis 3 pelat (pelat 1-3),
gesper, tanduk patah. Pembanding: bahu kecil, ekor, moncong. `cahaya` = rata-rata x piksel sorot gesper dikurangi rata-rata x piksel
bayangan gesper (negatif = sorot di kiri, cahaya kiri-atas). Frame ditandai bila tanda sisi berubah atau salah (kecuali pose berbalik
eksplisit; tidak ada). Hanya membaca kode; tidak menulis aset.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))

import hero  # noqa: E402
import hero_check as hc  # noqa: E402
import hero_scenes as hs  # noqa: E402

NAMES = [n for n, _, _, _ in hc.ASYM_ELEMENTS]


def main():
    out = []
    total_flags = 0
    for state, t in hs.TRACKS.items():
        cvs = [t.frame(i) for i in range(t.n)]
        centers = [hero.geometry(t.pose(i))["tcx"] for i in range(t.n)]
        a = hc.asymmetry(cvs, centers, state)
        out.append("%s (%d frame; ditandai: %s)" % (state, t.n, sum(len(v["tanda"]) for v in a.values())))
        out.append("  f   tcx  " + " ".join("%12s" % n for n in NAMES) + "  cahaya")
        for i in range(t.n):
            cells = []
            for n in NAMES:
                dx, c = a[n]["seri"][i]
                cells.append("%12s" % ("-" if dx is None else "%+.1f" % dx))
            lt = a["cahaya_gesper"]["seri"][i]
            out.append("  %-3d %5.1f  %s  %s" % (i, centers[i], " ".join(cells), "-" if lt is None else "%+.1f" % lt))
        for n, v in a.items():
            for i, why in v["tanda"]:
                out.append("  DITANDAI %s f%d: %s" % (n, i, why))
            total_flags += len(v["tanda"])
        out.append("")
    out.append("total frame-elemen ditandai: %d" % total_flags)
    text = "\n".join(out)
    if len(sys.argv) > 1:
        open(sys.argv[1], "w", encoding="utf-8").write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
