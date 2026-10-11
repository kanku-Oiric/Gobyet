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
tag fase2-gate-H bd42c0c "Gerbang H: Knight, Viking, Pirate, Wizard (24 aset, termasuk 2 tarian)"
tag fase2-gate-I 316fe79 "Gerbang I: Pak Haji dan Priest (10 aset, audit teologi 7.2)"
tag fase2-gate-J 13fe94f "Gerbang J: 12 varian kelas Knight, Viking, Pirate (36 aset)"
tag fase2-gate-F 7fc8b43 "Gerbang F: 36 sel sisa kostum lama, dokumentasi bagian 14 (163/163 sel terisi)"
git push origin --tags
