#!/bin/sh
# Buat tag git fase2-gate-<X> untuk setiap gerbang Fase 2 dan push ke origin.
# Sesi Claude tidak bisa push tag (hanya branch kerja), jadi jalankan ini dari mesinmu:
#   sh tools/tag_gates.sh
# Pemetaan gerbang -> commit dicatat juga di pack/PROGRESS.md. Baris ditambah tiap gerbang selesai.
set -e
tag() { git rev-parse -q --verify "refs/tags/$1" >/dev/null || git tag -a "$1" "$2" -m "$3"; }
tag fase2-gate-D 056e0dc "Gerbang D: Scientist, Mathematician"
tag fase2-gate-E 3eb2cdc "Gerbang E: Hacker, Detective, Lawyer"
tag fase2-gate-G 1d52710 "Gerbang G: Gamer dan Normal-GBLK (15 aset, termasuk 4 tarian)"
git push origin --tags
