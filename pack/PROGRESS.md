# Progres Fase 2: Gobyet Character Pack

Catatan kerja untuk melanjutkan tanpa konteks lain. Branch kerja: `claude/gobyet-fase2` (PR #1, draft). **Jangan merge ke `main` dan jangan force-push.** Repo Bertahan-Bukan-hidup tidak boleh berubah. Fase 3 (integrasi arena) di luar Fase 2.

## Gerbang

Huruf gerbang tidak berurutan dengan urutan kerja. Urutan kerja sebenarnya: A, B, C, lalu D, E, G, H, I, J, F.

| Urutan | Gerbang | Isi | Sel | Status | Commit |
|---:|---|---|---:|---|---|
| 1 | A | Referee: idle, thinking | 2 | disetujui, dikunci | `06bc433` |
| 2 | B | Judge, Skeptic, Champion (revisi medali di `73c034b`) | 8 | disetujui, dikunci setelah bagian 3 terverifikasi | `6875e4e`, `73c034b`, kunci di commit persiapan D |
| 3 | C | Greek Philosopher, Academic, Normal | 9 | disetujui, dikunci | `73c034b`, kunci `dd78be8` |
| 4 | D | Scientist (idle, shocked, victory), Mathematician (idle, thinking, victory) | 6 | belum | |
| 5 | E | Hacker (3), Detective (4), Lawyer (3); STOP-1 | 10 | belum | |
| 6 | G | Gamer (7), Normal-GBLK (8); STOP-2 | 15 | belum | |
| 7 | H | Knight, Viking, Pirate, Wizard; STOP-3 | 24 | belum | |
| 8 | I | Pak Haji, Priest (STOP-4 setelah idle keduanya) | 10 | belum | |
| 9 | J | 12 varian kelas × idle, attack, victory | 36 | belum | |
| 10 | F | sisa sel 12 kostum lama (14 wajib + 22 opsional), audit, dokumentasi; STOP-5 | 36 | belum | |

Mode kerja: tiap gerbang = produksi, validasi, commit (pesan menyebut gerbang), perbarui file ini dan `STYLE.md`, lalu terbitkan ulang preview. Lanjut otomatis bila validasi lulus, kecuali di titik STOP.

## Sel

Dibangkitkan oleh `python3 tools/progress_table.py` dari `pack/manifest.json`. Jangan diedit tangan.

<!-- tabel-sel:mulai -->
| Kostum | group | Berlaku | Terisi | Belum terisi (wajib) | Belum terisi (opsional) |
|---|---|---:|---:|---|---|
| `normal` | core | 7 | 5 | - | shocked, dance-a |
| `normal-gblk ← normal` | special | 8 | 0 | idle, victory, defeated | reveal, happy, dance-a, dance-b, dance-c |
| `referee` | role | 6 | 2 | victory, defeated | shocked, happy |
| `judge` | role | 7 | 3 | victory, defeated | shocked, happy |
| `skeptic` | role | 8 | 3 | thinking, victory, defeated | shocked, happy |
| `champion` | role | 7 | 2 | thinking, defeated | shocked, happy, dance-a |
| `greek-philosopher` | domain | 6 | 4 | - | shocked, happy |
| `academic` | domain | 6 | 4 | - | shocked, happy |
| `scientist` | domain | 6 | 1 | idle, victory, defeated | shocked, happy |
| `mathematician` | domain | 6 | 0 | idle, thinking, victory, defeated | shocked, happy |
| `lawyer` | domain | 6 | 0 | idle, thinking, victory, defeated | shocked, happy |
| `hacker` | domain | 6 | 1 | thinking, victory, defeated | shocked, happy |
| `detective` | domain | 7 | 1 | idle, victory, defeated | shocked, happy, suspicious |
| `gamer` | domain | 7 | 0 | idle, thinking, victory, defeated | happy, shocked, dance-a |
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
| **Total** | | **163** | **26** | | |
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

Mengunci gerbang yang disetujui: tambahkan `sha256sum` dari `gif/<nama>.gif`, `sheets/<nama>.png`, dan `sheets/<nama>@4x.png` (bila ada) ke `pack/sha256-disetujui.txt`. Kerjakan hanya setelah pemilik menyetujui.

## Catatan yang harus diingat

- **README di `main`.** Commit `a7a6d21` (README saja, atas permintaan pemilik) menampilkan galeri Fase 2 dengan URL gambar `raw.githubusercontent.com/.../claude/gobyet-fase2/gif/...`. Setelah PR di-merge, README di branch (path relatif) menggantikannya. Sebelum merge, pastikan tidak ada URL yang masih menunjuk ke branch. Jangan push ke `main` lagi.
- **Profil export.** Aset gerbang A-C dan aset asli memakai jalur lama (palet `PAL`, `optimize=False`, sheet 1× dan 4×). Aset baru mulai D memakai palet lokal (`PAL` + `PAL_EXT`), `optimize=True`, dan hanya sheet 1×. Lihat `pack.modern()` dan `export.local_palette()`.
- **`PAL_EXT`.** Kunci yang sudah dipakai: `p`, `j` (ungu, rompi Mathematician). Rencana: `J` (jas Lawyer, biru gelap), biru baja untuk Wizard. Kunci bebas: `t w z i o` dan angka.
- **Pengecualian teks.** `E=mc` (papan Scientist, statis) dan `GBLK` (papan normal-gblk). Selain itu maksimal 3 karakter per gelembung.
- **Known issues Gerbang C:** topi Academic terpotong 1 baris di puncak lemparan; `academic/defeated` di 1× hanya berbeda 1-2 px dari idle.
