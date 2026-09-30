# Progres Fase 2: Gobyet Character Pack

Catatan kerja untuk melanjutkan tanpa konteks lain. Branch kerja: `claude/gobyet-fase2` (PR #1, draft). **Jangan merge ke `main` dan jangan force-push.** Repo Bertahan-Bukan-hidup tidak boleh berubah. Fase 3 (integrasi arena) di luar Fase 2.

## Gerbang

Huruf gerbang tidak berurutan dengan urutan kerja. Urutan kerja sebenarnya: A, B, C, lalu D, E, G, H, I, J, F.

| Urutan | Gerbang | Isi | Sel | Status | Commit |
|---:|---|---|---:|---|---|
| 1 | A | Referee: idle, thinking | 2 | disetujui, dikunci | `06bc433` |
| 2 | B | Judge, Skeptic, Champion (revisi medali di `73c034b`) | 8 | disetujui, dikunci setelah bagian 3 terverifikasi | `6875e4e`, `73c034b`, kunci di commit persiapan D |
| 3 | C | Greek Philosopher, Academic, Normal | 9 | disetujui, dikunci | `73c034b`, kunci `dd78be8` |
| 4 | D | Scientist (idle, shocked, victory), Mathematician (idle, thinking, victory) | 6 | disetujui, dikunci di commit persiapan G | `056e0dc`, tag `fase2-gate-D` |
| 5 | E | Hacker (3), Detective (4), Lawyer (3) | 10 | disetujui, dikunci di commit persiapan G | `3eb2cdc`, tag `fase2-gate-E` |
| 6 | G | Gamer (7), Normal-GBLK (8) | 15 | selesai, validasi lulus; hash di `sha256-dibuat.txt`; laporan `pack/reports/gate-G.md` | `1d52710`, tag `fase2-gate-G` |
| 7 | H | Knight, Viking, Pirate, Wizard | 24 | belum | |
| 8 | I | Pak Haji, Priest | 10 | belum | |
| 9 | J | 12 varian kelas × idle, attack, victory | 36 | belum | |
| 10 | F | sisa sel 12 kostum lama (14 wajib + 22 opsional), audit, dokumentasi | 36 | belum | |

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
| `normal` | core | 7 | 5 | - | shocked, dance-a |
| `normal-gblk ← normal` | special | 8 | 8 | - | - |
| `referee` | role | 6 | 2 | victory, defeated | shocked, happy |
| `judge` | role | 7 | 3 | victory, defeated | shocked, happy |
| `skeptic` | role | 8 | 3 | thinking, victory, defeated | shocked, happy |
| `champion` | role | 7 | 2 | thinking, defeated | shocked, happy, dance-a |
| `greek-philosopher` | domain | 6 | 4 | - | shocked, happy |
| `academic` | domain | 6 | 4 | - | shocked, happy |
| `scientist` | domain | 6 | 4 | defeated | happy |
| `mathematician` | domain | 6 | 3 | defeated | shocked, happy |
| `lawyer` | domain | 6 | 3 | defeated | shocked, happy |
| `hacker` | domain | 6 | 4 | defeated | happy |
| `detective` | domain | 7 | 5 | defeated | happy |
| `gamer` | domain | 7 | 7 | - | - |
| `knight` | fantasy | 6 | 0 | idle, thinking, victory, defeated | shocked, attack |
| `knight-heavy ← knight` | fantasy | 3 | 0 | idle, victory | attack |
| `knight-archer ← knight` | fantasy | 3 | 0 | idle, victory | attack |
| `knight-manatarms ← knight` | fantasy | 3 | 0 | idle, victory | attack |
| `knight-assassin ← knight` | fantasy | 3 | 0 | idle, victory | attack |
| `viking` | fantasy | 6 | 0 | idle, thinking, victory, defeated | attack, dance-a |
| `viking-berserker ← viking` | fantasy | 3 | 0 | idle, victory | attack |
| `viking-huscarl ← viking` | fantasy | 3 | 0 | idle, victory | attack |
| `viking-gestir ← viking` | fantasy | 3 | 0 | idle, victory | attack |
| `viking-bondi ← viking` | fantasy | 3 | 0 | idle, victory | attack |
| `pirate` | fantasy | 6 | 0 | idle, thinking, victory, defeated | attack, dance-a |
| `pirate-captain ← pirate` | fantasy | 3 | 0 | idle, victory | attack |
| `pirate-skirmisher ← pirate` | fantasy | 3 | 0 | idle, victory | attack |
| `pirate-sharpshooter ← pirate` | fantasy | 3 | 0 | idle, victory | attack |
| `pirate-buccaneer ← pirate` | fantasy | 3 | 0 | idle, victory | attack |
| `wizard` | fantasy | 6 | 0 | idle, thinking, victory, defeated | shocked, attack |
| `pak-haji` | theology | 5 | 0 | idle, thinking, victory, defeated | happy |
| `priest` | theology | 5 | 0 | idle, thinking, victory, defeated | happy |
| **Total** | | **163** | **57** | | |
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
- **`pack/sha256-dibuat.txt`:** aset gerbang G ke atas yang sudah dibuat tetapi belum disetujui. Tiap gerbang berikutnya memverifikasi bahwa file-file ini tidak berubah. Mengubahnya hanya lewat protokol revisi (bagian 10), dengan memperbarui hash secara eksplisit.

Mengembalikan satu gerbang: `git checkout fase2-gate-<X> -- gif sheets src pack` (atau hash commit gerbang dari tabel di atas) (lalu `python3 src/export.py` dan validator), atau `git revert` commit gerbang itu.

## Catatan yang harus diingat

- **README di `main`.** Commit `a7a6d21` (README saja, atas permintaan pemilik) menampilkan galeri Fase 2 dengan URL gambar `raw.githubusercontent.com/.../claude/gobyet-fase2/gif/...`. Setelah PR di-merge, README di branch (path relatif) menggantikannya. Sebelum merge, pastikan tidak ada URL yang masih menunjuk ke branch. Jangan push ke `main` lagi.
- **Profil export.** Aset gerbang A-C dan aset asli memakai jalur lama (palet `PAL`, `optimize=False`, sheet 1× dan 4×). Aset baru mulai D memakai palet lokal (`PAL` + `PAL_EXT`), `optimize=True`, dan hanya sheet 1×. Lihat `pack.modern()` dan `export.local_palette()`.
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
