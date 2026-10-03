# Progres Fase 2: Gobyet Character Pack

Catatan kerja untuk melanjutkan tanpa konteks lain. Branch kerja: `claude/gobyet-fase2` (PR #1, draft). **Jangan merge ke `main` dan jangan force-push.** Repo Bertahan-Bukan-hidup tidak boleh berubah. Fase 3 (integrasi arena) di luar Fase 2.

## Gerbang

Huruf gerbang tidak berurutan dengan urutan kerja. Urutan kerja sebenarnya: A, B, C, lalu D, E, G, H, I, J, F, lalu K (tugas terpisah di branch `claude/gobyet-hero`).

| Urutan | Gerbang | Isi | Sel | Status | Commit |
|---:|---|---|---:|---|---|
| 1 | A | Referee: idle, thinking | 2 | disetujui, dikunci | `06bc433` |
| 2 | B | Judge, Skeptic, Champion (revisi medali di `73c034b`) | 8 | disetujui, dikunci setelah bagian 3 terverifikasi | `6875e4e`, `73c034b`, kunci di commit persiapan D |
| 3 | C | Greek Philosopher, Academic, Normal | 9 | disetujui, dikunci | `73c034b`, kunci `dd78be8` |
| 4 | D | Scientist (idle, shocked, victory), Mathematician (idle, thinking, victory) | 6 | disetujui, dikunci di commit persiapan G | `056e0dc`, tag `fase2-gate-D` |
| 5 | E | Hacker (3), Detective (4), Lawyer (3) | 10 | disetujui, dikunci di commit persiapan G | `3eb2cdc`, tag `fase2-gate-E` |
| 6 | G | Gamer (7), Normal-GBLK (8) | 15 | selesai, validasi lulus; hash di `sha256-dibuat.txt`; laporan `pack/reports/gate-G.md` | `1d52710`, tag `fase2-gate-G` |
| 7 | H | Knight (6), Viking (6), Pirate (6), Wizard (6) | 24 | selesai, validasi lulus; hash di `sha256-dibuat.txt`; laporan `pack/reports/gate-H.md` | `bd42c0c`, tag `fase2-gate-H` |
| 8 | I | Pak Haji (5), Priest (5), audit 7.2 otomatis `[VT]` | 10 | selesai, validasi lulus; idle lebih dulu, pemeriksaan i-vi lulus sebelum state lain; hash di `sha256-dibuat.txt`; laporan `pack/reports/gate-I.md` | `316fe79`, tag `fase2-gate-I` |
| 9 | J | 12 varian kelas × idle, attack, victory | 36 | selesai, validasi lulus; hash di `sha256-dibuat.txt`; laporan `pack/reports/gate-J.md` | `13fe94f`, tag `fase2-gate-J` |
| 10 | F | sisa sel 12 kostum lama (14 wajib + 22 opsional), dokumentasi bagian 14, laporan akhir | 36 | selesai, validasi lulus; 163/163 sel terisi; hash di `sha256-dibuat.txt`; laporan `pack/reports/gate-F.md` dan `pack/reports/final.md` | `7fc8b43`, tag `fase2-gate-F` |
| 11 | K | Berserker Hero (kanvas 128×96): idle, run, rage, attack-leap, attack-smash, miss, exhaustion, defeated | 8 | dibuat, **menunggu persetujuan gaya pemilik**; hash di `sha256-hero.txt`; laporan `pack/reports/hero-fase-cd.md` (Fase B: `hero-fase-b.md`; perbaikan teknis: `hero-fase-teknis.md`); branch `claude/gobyet-hero`, tidak di-merge | lihat `git log claude/gobyet-hero` |

**Mode kerja (keputusan pemilik setelah STOP-1):** G, H, I, J, lalu F dijalankan berurutan tanpa berhenti. Yang tetap berlaku hanya STOP-DARURAT dan STOP final setelah F. Syarat lanjut otomatis: validasi bagian 11 lulus. GAGAL baru diperbaiki di dalam gerbang itu tanpa menyentuh aset yang sudah dikunci atau ditandai. STOP-DARURAT berlaku bila:
- GAGAL tidak bisa diperbaiki;
- hash aset terkunci atau aset yang sudah dibuat berubah;
- proyeksi ukuran melewati 15 MB;
- perubahan terpaksa menyentuh file di luar `pack/`, `src/`, dan `tools/`;
- palet tidak cukup tanpa menyentuh aset lama.

Pengaman per gerbang:
1. Laporan lengkap di `pack/reports/gate-<X>.md`.
2. Commit tersendiri dengan tag `fase2-gate-<X>`. Tag dibuat di sesi, tetapi **tidak bisa di-push** dari sesi Claude (remote menolak push selain branch kerja). Karena itu pemetaan gerbang → commit dicatat di tabel di atas dan di `tools/tag_gates.sh`; jalankan `sh tools/tag_gates.sh` dari mesinmu untuk membuat dan mem-push semua tag.
3. Hash aset gerbang itu ditambahkan ke `pack/sha256-dibuat.txt`.
4. File ini dan `STYLE.md` diperbarui, lalu preview diterbitkan ulang.

Kalau sesi terputus, lanjutkan dari gerbang terakhir yang punya tag dan baris "selesai" di tabel ini.

## Sel

Dibangkitkan oleh `python3 tools/progress_table.py` dari `pack/manifest.json`. Jangan diedit tangan.

<!-- tabel-sel:mulai -->
| Kostum | group | Berlaku | Terisi | Belum terisi (wajib) | Belum terisi (opsional) |
|---|---|---:|---:|---|---|
| `normal` | core | 7 | 7 | - | - |
| `normal-gblk ← normal` | special | 8 | 8 | - | - |
| `referee` | role | 6 | 6 | - | - |
| `judge` | role | 7 | 7 | - | - |
| `skeptic` | role | 8 | 8 | - | - |
| `champion` | role | 7 | 7 | - | - |
| `greek-philosopher` | domain | 6 | 6 | - | - |
| `academic` | domain | 6 | 6 | - | - |
| `scientist` | domain | 6 | 6 | - | - |
| `mathematician` | domain | 6 | 6 | - | - |
| `lawyer` | domain | 6 | 6 | - | - |
| `hacker` | domain | 6 | 6 | - | - |
| `detective` | domain | 7 | 7 | - | - |
| `gamer` | domain | 7 | 7 | - | - |
| `knight` | fantasy | 6 | 6 | - | - |
| `knight-heavy ← knight` | fantasy | 3 | 3 | - | - |
| `knight-archer ← knight` | fantasy | 3 | 3 | - | - |
| `knight-manatarms ← knight` | fantasy | 3 | 3 | - | - |
| `knight-assassin ← knight` | fantasy | 3 | 3 | - | - |
| `viking` | fantasy | 6 | 6 | - | - |
| `viking-berserker ← viking` | fantasy | 3 | 3 | - | - |
| `viking-huscarl ← viking` | fantasy | 3 | 3 | - | - |
| `viking-gestir ← viking` | fantasy | 3 | 3 | - | - |
| `viking-bondi ← viking` | fantasy | 3 | 3 | - | - |
| `pirate` | fantasy | 6 | 6 | - | - |
| `pirate-captain ← pirate` | fantasy | 3 | 3 | - | - |
| `pirate-skirmisher ← pirate` | fantasy | 3 | 3 | - | - |
| `pirate-sharpshooter ← pirate` | fantasy | 3 | 3 | - | - |
| `pirate-buccaneer ← pirate` | fantasy | 3 | 3 | - | - |
| `wizard` | fantasy | 6 | 6 | - | - |
| `pak-haji` | theology | 5 | 5 | - | - |
| `priest` | theology | 5 | 5 | - | - |
| `berserker-hero ← viking-berserker` | fantasy | 8 | 8 | - | - |
| **Total** | | **171** | **171** | | |
<!-- tabel-sel:selesai -->

## Cara melanjutkan

```bash
python3 src/export.py                          # bangun ulang aset dan manifest; aset terkunci harus tetap identik
python3 src/validate_pack.py --gate <X>        # V1-V10
python3 -m unittest src/test_validate_pack.py  # audit teks
node --test pack/resolver.test.js
node tools/e2e_preview.js                      # butuh Playwright di luar proyek
python3 tools/progress_table.py                # perbarui tabel sel di atas
```

File hash:
- **`pack/sha256-asli.txt`:** 27 file pra-Fase 2.
- **`pack/sha256-disetujui.txt`:** aset gerbang yang disetujui pemilik (A-E). Tambahkan `sha256sum` dari `gif/<nama>.gif`, `sheets/<nama>.png`, dan `sheets/<nama>@4x.png` (bila ada) hanya setelah pemilik menyetujui.
- **`pack/sha256-hero.txt`:** 16 file aset Berserker Hero (8 GIF + 8 sheet 1×), dibuat dan belum disetujui. Dibangkitkan `python3 tools/hero_hashes.py`; V1 memeriksanya. Berkas ini berdiri sendiri supaya tiga berkas kunci lain tidak berubah.
- **`pack/sha256-dibuat.txt`:** aset gerbang G ke atas yang sudah dibuat tetapi belum disetujui. Tiap gerbang berikutnya memverifikasi bahwa file-file ini tidak berubah. Mengubahnya hanya lewat protokol revisi (bagian 10), dengan memperbarui hash secara eksplisit.

Mengembalikan satu gerbang: `git checkout fase2-gate-<X> -- gif sheets src pack` (atau hash commit gerbang dari tabel di atas) (lalu `python3 src/export.py` dan validator), atau `git revert` commit gerbang itu.

## Catatan yang harus diingat

- **README di `main`.** Commit `a7a6d21` (README saja, atas permintaan pemilik) menampilkan galeri Fase 2 dengan URL gambar `raw.githubusercontent.com/.../claude/gobyet-fase2/gif/...`. Setelah PR di-merge, README di branch (path relatif) menggantikannya. Sebelum merge, pastikan tidak ada URL yang masih menunjuk ke branch. Jangan push ke `main` lagi.
- **Profil export.** Aset gerbang A-C dan aset asli memakai jalur lama (palet `PAL`, `optimize=False`, sheet 1× dan 4×). Aset baru mulai D memakai palet lokal (`PAL` + `PAL_EXT`), `optimize=True`, dan hanya sheet 1×. Lihat `pack.modern()` dan `export.local_palette()`. Gerbang K menambah `PAL_HERO` di urutan palet lokal (sesudah `PAL_EXT`), kanvas 128×96 per sel (`pack.CANVAS_OF`), GIF ×4, dan `loop: false` untuk `berserker-hero/rage` (`pack.NO_LOOP`); semuanya aditif.
- **`PAL_EXT`:** 13 kunci.
  - `p j`: ungu Mathematician.
  - `J w`: jas Lawyer.
  - `o t`: oranye Gamer.
  - `z 1`: merah tua Knight.
  - `i 2`: marun Pirate.
  - `3 4`: biru kerajaan Wizard.
  - `5`: bayangan abu Priest.

  Semuanya ditambahkan sekaligus sebelum Gerbang G; 116 file aset lama tetap identik. Tabel alokasinya ada di `STYLE.md`.
- **Pengecualian teks.** `E=mc` (papan Scientist, statis) dan `GBLK` (papan normal-gblk). Selain itu maksimal 3 karakter per gelembung.
- **Known issues Gerbang C:** topi Academic terpotong 1 baris di puncak lemparan; `academic/defeated` di 1× hanya berbeda 1-2 px dari idle.
