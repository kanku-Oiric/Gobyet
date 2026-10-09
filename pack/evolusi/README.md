# Evolusi Berserker Hero

Tiga tahap karakter utama pack Gobyet. Keputusan pemilik: kode v1 dan v2 tidak dihapus, disimpan dan diunggah sebagai evolusi. Buka `index.html` di folder ini untuk melihat ketiganya berdampingan (latar terang, gelap, abu tengah).

| Tahap | Ringkas | Status | Berkas |
|---|---|---|---|
| **Evolusi 1** (v1) | Gobyet berzirah besi hitam, helm tengkorak naga, tabard teal; wajah Gobyet terlihat penuh | gaya ditolak pemilik; timing dan emote dipakai lagi di v3 | `v1/berserker-hero-<state>.gif` (8 state), `v1/berserker-hero-v1-<pose>.png` |
| **Evolusi 2** (v2) | Gobyet berzirah hitam-merah, badan chibi mekanis dari rujukan pertama | ditolak pemilik ("rombak dari awal") sebelum dianimasikan | `v2/berserker-hero-v2-<pose>.png` (3 pose kunci) |
| **Evolusi 3** (v3) | zirah bukan Gobyet, helm salib merah, pedang hitam berinti api, perisai naga, tepi terang; wajah monyet Gobyet hanya di balik topeng | sekarang, menunggu persetujuan gaya | `../../gif/berserker-hero-<state>.gif` (9 state), `v3/berserker-hero-v3-<pose>.png` |

- GIF v1 adalah byte persis dari commit `fd5d899` (diambil dengan `git show`, diperiksa terhadap `pack/sha256-hero.txt` pada commit itu).
- Pose kunci PNG (4×, latar transparan) dirender ulang dari `src/hero.py`, `src/hero2.py`, dan `src/hero3.py`.
- `python3 tools/evolusi.py` menulis ulang folder ini dan `pack/sha256-evolusi.txt`; `--check` hanya memeriksa. Pose kunci v3 ikut berubah bila rig v3 berubah.
- Aset di sini bukan bagian manifest dan tidak dihitung dalam anggaran hero. Ukuran: ±0,95 MB.
- Tidak ada pernyataan bahwa salah satu gaya bagus atau disetujui.
