# Berserker Hero v3: ekor baru (batang beruas berujung kipas panah), laporan STOP

Branch `claude/gobyet-hero`. Tidak di-merge, `main` tidak disentuh, tidak ada force-push, repo Bertahan-Bukan-hidup tidak disentuh. Format mengikuti bagian 8 brief awal ("LAPORAN (tiap STOP)").

**Dikerjakan:** pesanmu "victory udah ok sekarang buat ekor". Victory dan perisai tidak diubah (selain ekornya). Ekor lama (dua busur kipas panah tanpa batang di belakang bahu) tertutup perisai naga dan tampil sebagai panah merah yang tersebar; di state serangan ia bercampur dengan jambul. Ekor diganti di rig dan di sembilan state.

**Tidak diklaim:** gaya bagus atau disetujui; itu keputusanmu. **Saya tidak menonton GIF sebagai gerak**: diperiksa lewat lembar frame, pengukuran piksel, validator, dan uji Chromium.

## 1. Ringkasan

| Hal | Sebelum | Sekarang |
|---|---|---|
| Bentuk | dua busur panah merah (11 panah) tanpa batang, di belakang bahu kiri | **batang besi hitam beruas** (jari-jari 4,2 → 1,8 px) dengan lima cincin merah, berujung **kipas tiga panah** (tengah menyala, dua samping lebih gelap) yang menempel di batang |
| Letak | sebagian besar tertutup perisai; di state serangan dipindah ke atas dan bercampur jambul | keluar dari pinggang belakang, turun ke dekat lantai di belakang kaki, melengkung naik di **kiri bawah** (di bawah sayap perisai, di kiri ujung bawah perisai); tidak menyentuh jambul di state mana pun |
| Gerak | kipas berputar sedikit | ujung bergoyang naik-turun 3 px mengikuti fase ekor (run 7 px, mengikuti langkah); di `rage` ekor terangkat mengikuti amarah |
| Ukuran per state | skala dan putaran kipas + geseran per frame di state serangan | satu pasangan per state (`hero3_scenes.TAIL`: k panjang, rot sudut angkat), dicari otomatis supaya tidak terpotong tepi kanvas |
| Ekor di frame kunci (px) | idle 298, serangan 148-149 (50%), victory 66 (22%) | idle 288, serangan **144-155 (50-54%)**, victory **164 (57%)** |
| Warna | merah tanpa garis tepi | besi hitam bergaris tepi + tepi terang `n4` (terbaca di latar gelap); tanpa warna baru (tetap 25) |

## 2. Ekor per state

| State | k, rot | Ekor di frame kunci (px, % idle) | Min-maks sepanjang state (px) |
|---|---|---|---|
| idle | 1,0, −10° | 288 (100%) | 260-292 |
| run | 0,8, −10° | 214 (74%) | 161-214 |
| rage | 0,8, −10° (+ angkat amarah) | 191 (66%) | 151-192 |
| attack-leap | 0,7, 0° | 144 (50%) | 136-162 |
| attack-smash | 0,7, 0° | 144 (50%) | 134-161 |
| miss | 0,7, 0° | 155 (54%) | 135-160 |
| exhaustion | 0,8, 0° | 153 (53%) | 151-167 |
| defeated | 0,7, 0° | 110 (38%) | 99-111 |
| victory | 0,8, −10° | 164 (57%) | 160-181 |

Untuk state serangan dipilih sudut 0°: di −10° ukuran di frame kunci hampir sama, tetapi ekor hanya 59-74 px di frame terkecil.

## 3. Ukuran berkas

| State | GIF sebelum → sekarang (B) | Sheet sebelum → sekarang (B) |
|---|---|---|
| idle | 178.727 → 175.811 | 15.278 → 13.662 |
| run | 181.994 → 178.317 | 18.924 → 17.814 |
| rage | 164.213 → 169.626 | 26.683 → 28.018 |
| attack-leap | 204.536 → 205.041 | 33.470 → 33.079 |
| attack-smash | 174.997 → 176.195 | 27.323 → 26.472 |
| miss | 139.751 → 142.364 | 24.049 → 23.678 |
| exhaustion | 157.916 → 153.938 | 12.719 → 11.922 |
| defeated | 167.139 → 166.109 | 12.002 → 11.701 |
| victory | 296.819 → **305.069** | 30.947 → 31.258 |
| **total GIF + sheet** | 1.867.487 → **1.870.074** (batas 2.000.000) | |

GIF `victory` sekarang 305.069 B, sisa 2.131 B dari batas per GIF 307.200 B (usulan saya).

## 4. Tafsiran dan asumsi (salah satu bisa keliru; mohon koreksi)

1. **"Buat ekor" = rancang ulang ekor supaya terlihat jelas** (keluhan sebelumnya: tertutup perisai, bercampur jambul, kecil di victory). Kalau maksudmu bentuk lain (mis. ekor naga bersisik, ekor mekanis bersegmen kabel, atau kembali ke kipas besar), kirim gambar atau sebutkan.
2. **Kipas panah dari rujukan pertama dipertahankan sebagai ujung ekor**, tidak lagi sebagai busur di belakang bahu, karena ruang di belakang bahu sekarang milik perisai naga.
3. **Ekor diletakkan rendah di kiri bawah**: hanya di situ ada ruang kosong yang tidak tertutup perisai dan tidak bercampur jambul.
4. **"Sedang" di state serangan tetap 35-80% ekor idle** (usulan saya); hasilnya 50-54%.

## 5. Validasi (keluaran mentah)

### 5.1 Validator penuh (`python3 src/validate_pack.py`)

```
[V1] Hash aset yang dikunci dan aset yang sudah dibuat
  sha256-asli.txt: 27 identik, 0 berubah/hilang
  sha256-disetujui.txt: 89 identik, 0 berubah/hilang
  sha256-dibuat.txt: 242 identik, 0 berubah/hilang
  sha256-hero.txt: 18 identik, 0 berubah/hilang

[V11] Berserker Hero (kanvas 128x96, GIF x4; zirah bukan Gobyet, wajah Gobyet di balik topeng): spesifikasi, aset = kode, identitas, tepi terang, mata, sisi, kepala, seam, ekor, victory, warna, kontras
  state         frame loop  kanvas skala kunci GIF KB    temuan
  idle             12 ya    128x96     4 0     171.7     lulus
  run              12 ya    128x96     4 10    174.1     lulus
  rage             12 tidak 128x96     4 6     165.7     lulus
  attack-leap      14 ya    128x96     4 8     200.2     lulus
  attack-smash     12 ya    128x96     4 7     172.1     lulus
  miss             10 ya    128x96     4 6     139.0     lulus
  exhaustion       12 ya    128x96     4 5     150.3     lulus
  defeated         14 ya    128x96     4 3     162.2     lulus
  victory          20 tidak 128x96     4 16    297.9     lulus
      kunci f0: helm 34x31, mata 86 px, perisai naga 1267 px (badan 723), pedang 836 px, kepalan 176 px, jambul 410 px, ekor 288 px
      kunci f10: helm 34x31, mata 86 px, perisai naga 1460 px (badan 769), pedang 862 px, kepalan 177 px, jambul 377 px, ekor 214 px
      kunci f6: helm 34x31, mata 110 px, perisai naga 1282 px (badan 736), pedang 856 px, kepalan 165 px, jambul 486 px, ekor 191 px
      kunci f8: helm 34x31, mata 110 px, perisai naga 1241 px (badan 715), pedang 497 px, kepalan 176 px, jambul 397 px, ekor 144 px (50% ekor idle 288)
      kunci f7: helm 34x31, mata 110 px, perisai naga 1278 px (badan 734), pedang 524 px, kepalan 176 px, jambul 397 px, ekor 144 px (50% ekor idle 288)
      kunci f6: helm 34x31, mata 102 px, perisai naga 1219 px (badan 695), pedang 588 px, kepalan 128 px, jambul 421 px, ekor 155 px (53% ekor idle 288)
      kunci f5: helm 34x31, mata 62 px, perisai naga 1339 px (badan 724), pedang 525 px, kepalan 169 px, jambul 368 px, ekor 153 px
      kunci f3: helm 34x31, mata 62 px, perisai naga 1341 px (badan 726), pedang 407 px, kepalan 176 px, jambul 374 px, ekor 110 px
      kunci f16: helm 34x31, mata 86 px, perisai naga 1342 px (badan 734), pedang 702 px, kepalan 176 px, jambul 384 px, ekor 164 px
  warna seluruh karakter: 25 (batas 28); di luar palet yang diizinkan: 0
  V11: lulus

[V10] Ukuran (baris hero dan anggaran pack)
  gerbang K:  9 aset, GIF terbesar 305069 byte, total file  1870074 byte
  hero: 9 aset, GIF terbesar 305069 byte (batas 307200), total GIF + sheet 1870074 byte (batas 2000000)
  proyeksi pertambahan total: 13077464 byte (12.47 MB); ambang peringatan 15 MB, batas keras 16 MB

HASIL: LULUS
```

### 5.2 Uji unit, resolver, browser

```
$ python3 -m unittest src/test_hero3.py src/test_hero2.py
Ran 25 tests ... OK
$ python3 -m unittest src/test_validate_pack.py
Ran 52 tests ... OK
$ node pack/resolver.test.js
# pass 25  # fail 0
$ node tools/e2e_preview.js
E2E: LULUS
$ node tools/gif_once_check.js
GIF-SEKALI: LULUS
$ python3 tools/hero_hashes.py --check
18 berkas; sama dengan pack/sha256-hero.txt
$ python3 tools/evolusi.py --check
17 berkas evolusi; sama dengan pack/sha256-evolusi.txt
```

Tes baru: ekor adalah batang beruas (≥ 80 px di pose kunci) bercincin merah (≥ 6 px) dengan kipas yang menempel di batang, jauh di belakang badan, tidak menembus lantai. Ekor serangan diukur dari batang + kipas (sebelumnya hanya kipas).

## 6. Bukti visual (`pack/reports/hero3-ekor/`)

| Berkas | Isi |
|---|---|
| `sebelum-sesudah.png` | frame kunci idle, attack-smash, victory: ekor lama dan ekor baru berdampingan |
| `kunci-9-state.png` | frame kunci sembilan state di latar terang dan gelap |
| `goyang-idle-run.png` | semua frame idle dan run, potongan kiri bawah 4×: goyangan ekor |
| `detail-8x.png` | ekor idle 8× di latar terang dan gelap |
| `ekor.json` | k, rot, ekor di frame kunci, min dan maks per state |

## 7. Bukti aset lama tidak berubah

- V1: `sha256-asli.txt` 27, `sha256-disetujui.txt` 89, `sha256-dibuat.txt` 242 identik (keluaran 5.1).
- Berubah: 18 berkas hero (ekor ada di semua state) dan `pack/sha256-hero.txt`; `pack/manifest.json` tidak berubah (jumlah frame dan durasi sama).
- Galeri evolusi: hanya tiga pose kunci v3 yang berubah (ekor baru); GIF v1 tetap byte persis dari commit `fd5d899`. `pack/sha256-evolusi.txt` ditulis ulang.
- Repo Bertahan-Bukan-hidup tetap di `696605e`.

## 8. Perubahan kode

- `src/hero3.py`: `tail_fan` diganti `tail` dan `tail_path` (konstanta `TAIL_PTS`, `TAIL_R`, `TAIL_FAN`; parameter pose baru `tail_wag`); pangkal ekor di pinggang belakang (`hip_l`).
- `src/hero3_scenes.py`: `TAIL_SCALE`, `TAIL_ROT`, `TAIL_PEAK` diganti satu tabel `TAIL` per state; run memakai `tail_wag=7` dan fase ekor yang menjaga IoU siluet berurutan ≤ 0,90.
- `src/hero3_check.py` dan V11: ekor diukur dari `tail_seg` + `tail_arrow` (`TAIL_PARTS`).
- Tes: `src/test_hero3.py` (tes ekor baru), `src/test_validate_pack.py` (ekor serangan memakai `TAIL_PARTS`); `tools/hero3_revisi.py` disesuaikan.
- Dokumen: `pack/README.md`, `pack/STYLE.md`, `pack/PROGRESS.md`.

## 9. Kelemahan yang saya lihat sendiri

1. **Ruang anggaran `victory` hampir habis**: 2.131 B tersisa dari batas per GIF.
2. **Run: IoU siluet berurutan 0,89** (batas 0,90). Ekor besar menambah bagian siluet yang mirip antar frame; fase goyangan dipilih supaya tetap di bawah batas.
3. **Kipas di ujung kecil** (±10-13 px per panah); di ukuran asli kipas terbaca sebagai ujung panah berduri, bukan kipas lebar.
4. **Pangkal ekor tertutup perisai** di semua state; yang terlihat adalah separuh batang luar dan kipas.
5. **`defeated` ekornya paling pendek** (38% idle) karena posisi berlutut dekat tepi kiri.

## 10. Keputusan yang saya butuhkan darimu

1. Bentuk ekor baru ini sesuai, atau ada arah lain (gambar referensi akan sangat membantu)?
2. Ukuran: sekarang idle paling besar, serangan sekitar setengahnya. Perlu lebih besar atau lebih kecil?
3. Ruang anggaran `victory` tinggal 2 KB. Boleh menaikkan batas per GIF lagi bila nanti perlu, atau bagian lain dikurangi?

## 11. Daftar berkas di fase ini

```
src/hero3.py  src/hero3_scenes.py  src/hero3_check.py  src/validate_pack.py  src/test_hero3.py  src/test_validate_pack.py  tools/hero3_revisi.py
gif/berserker-hero-*.gif (9)  sheets/berserker-hero-*.png (9)  pack/sha256-hero.txt
pack/evolusi/v3/*.png  pack/sha256-evolusi.txt
pack/README.md  pack/STYLE.md  pack/PROGRESS.md
pack/reports/hero3-ekor.md (laporan ini)  pack/reports/hero3-ekor/ (bukti)
```

Menunggu persetujuan gaya untuk Berserker Hero.
