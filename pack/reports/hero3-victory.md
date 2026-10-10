# Berserker Hero v3: `victory` dipoles (16 → 20 frame), laporan STOP

Branch `claude/gobyet-hero`. Tidak di-merge, `main` tidak disentuh, tidak ada force-push, repo Bertahan-Bukan-hidup tidak disentuh. Format mengikuti bagian 8 brief awal ("LAPORAN (tiap STOP)").

**Dikerjakan:** pesanmu "prisainya udah good. lanjutkan ke victory". Perisai naga tidak diubah. `victory` dikerjakan ulang memakai sisa anggaran 2 MB: 20 frame (sebelumnya 16), wajah Gobyet terlihat lebih lama, kaki di batu dibuat terbaca, dan usapan darah dibuat bertahap dengan tangan yang benar-benar menyusuri bilah. Urutan permintaan awalmu tetap: topeng buka-tutup → pedang ditusuk ke tanah → kaki naik batu sambil mengusap darah monster. Delapan state lain tidak berubah (GIF dan sheet identik byte).

**Tidak diklaim:** gaya bagus atau disetujui; itu keputusanmu. **Saya tidak menonton GIF sebagai gerak**: diperiksa lewat lembar frame, pengukuran piksel, validator, dan uji Chromium.

## 1. Ringkasan

| Hal | Sebelum (16 frame) | Sekarang (20 frame) |
|---|---|---|
| Wajah Gobyet di balik topeng | f1-f4, ±600 ms; tersenyum hanya di f3 | **f1-f6, 880 ms**: senyum tipis (f1-f3) → tersenyum ditahan 350 ms (f4) → senyum tipis (f5-f6) → klik tertutup (f7) |
| Tusukan pedang | f6-f9 | f8-f11 (sama: dicabut, diangkat tinggi, menukik dengan smear, menancap dengan debu dan serpihan) |
| Kaki di batu | sepatu melayang di tepi kiri batu yang lebih rendah; batu sebagian tertutup pedang | batu **berpuncak rata** 20×10 px di antara kaki dan pedang; sol sepatu tepat di atas puncak (f13-f19); badan condong di atas lutut |
| Usapan darah | 3 tahap; tangan berhenti di tengah sementara noda bagian bawah hilang sendiri | **5 tahap** (f14-f18); kepalan turun 57 → 72 px menyusuri sisi kiri bilah tepat di depan batas noda; noda 189 → 155 → 111 → 59 → 58 → 0 px; olesan terdorong ke bawah |
| Akhir | bilah bersih berkilau, tahan 1500 ms | sama; kepalan kembali ke gagang (f19) |
| Durasi total | 3510 ms | 3980 ms |
| GIF / sheet | 232.278 / 29.932 B | **296.819 / 30.947 B** |
| Total hero GIF + sheet | 1.801.931 B | **1.867.487 B** (batas 2.000.000) |

## 2. Frame demi frame

| f | ms | Isi | Topeng | Wajah Gobyet (px, mata) | Noda (px) | Kaki di batu (px) |
|---:|---:|---|---:|---|---:|---:|
| 0 | 160 | berdiri, pedang berdarah tertancap di kanan batu | 0 | - | 203 | 0 |
| 1 | 100 | topeng mulai terbelah | 0,25 | 30, 0 | 203 | 0 |
| 2 | 100 | pintu bergeser, uap dari celah | 0,625 | 154, 20 | 203 | 0 |
| 3 | 150 | terbuka penuh, senyum tipis | 1 | 244, 24 | 203 | 0 |
| 4 | 350 | **tersenyum**, ditahan | 1 | 244, 24 | 203 | 0 |
| 5 | 100 | menutup | 0,625 | 154, 20 | 203 | 0 |
| 6 | 80 | hampir tertutup | 0,25 | 30, 0 | 203 | 0 |
| 7 | 140 | klik: percikan di tengah pelat, visor melebar | 0 | - | 203 | 0 |
| 8 | 100 | pedang dicabut, visor marah | 0 | - | 206 | 0 |
| 9 | 70 | pedang diangkat tinggi | 0 | - | 209 | 0 |
| 10 | 60 | menukik, smear, berteriak | 0 | - | 205 | 0 |
| 11 | 200 | **menancap**: debu, serpihan, percikan, tetes darah | 0 | - | 205 | 0 |
| 12 | 140 | lutut naik | 0 | - | 201 | 0 |
| 13 | 160 | kaki di puncak batu, kepalan ke pangkal bilah | 0 | - | 197 | 37 |
| 14-18 | 110-130 | usapan 5 tahap, tetes darah jatuh (f15-f16), kilau (f18) | 0 | - | 189 → 58 | 37 |
| 19 | 1500 | bilah bersih, dua kilau, kepalan di gagang | 0 | - | 0 | 38 |

Frame kunci: **f16** (tengah usapan). Ekor dan jambul dibuat diam selama topeng (f0-f6) dan usapan (f13-f19) supaya perhatian ke wajah dan bilah.

## 3. Tafsiran dan asumsi (salah satu bisa keliru; mohon koreksi)

1. **"Lanjutkan ke victory" = poles `victory` dan pakai sisa anggaran untuk frame tambahan** (pertanyaan nomor 5 di laporan sebelumnya). Kalau maksudmu hal lain di `victory` (misalnya mengganti urutan, menambah monster atau aksi lain), bilang saja.
2. **Batas per GIF dinaikkan ke 300 KiB (307.200 B)**. GIF `victory` 20 frame 296.819 B tidak muat di 256 KiB yang saya usulkan sebelumnya. Batas total 2.000.000 B darimu tetap. GIF hero memakai `disposal=2` (frame utuh supaya latar transparan benar), jadi ukurannya naik hampir linear dengan jumlah frame; membuat ekor diam hampir tidak mengubah ukuran.
3. **Noda darah digeser ke dekat pelindung pedang** (gumpalan ±3 satuan bilah ke atas). Lengan hero pendek (16 px), dan di pose kaki-di-batu tangan tidak bisa mencapai bagian bawah bilah; dengan noda di atas, seluruh noda terlihat diusap oleh tangan.
4. **Batu lebih kecil dan berpuncak rata** (20×10, sebelumnya 24×12 bulat) supaya sol sepatu duduk tepat di atasnya; batu digeser supaya tidak tertutup kaki saat berdiri.
5. **Wajah Gobyet tetap skala 1** (belum kamu jawab); hanya durasinya yang diperpanjang.

## 4. Validasi (keluaran mentah)

### 4.1 Validator penuh (`python3 src/validate_pack.py`)

```
[V1] Hash aset yang dikunci dan aset yang sudah dibuat
  sha256-asli.txt: 27 identik, 0 berubah/hilang
  sha256-disetujui.txt: 89 identik, 0 berubah/hilang
  sha256-dibuat.txt: 242 identik, 0 berubah/hilang
  sha256-hero.txt: 18 identik, 0 berubah/hilang

[V11] Berserker Hero (kanvas 128x96, GIF x4; zirah bukan Gobyet, wajah Gobyet di balik topeng): spesifikasi, aset = kode, identitas, tepi terang, mata, sisi, kepala, seam, ekor, victory, warna, kontras
  state         frame loop  kanvas skala kunci GIF KB    temuan
  victory          20 tidak 128x96     4 16    289.9     lulus
      sisi (dx px relatif tengah badan, - kiri / + kanan): perisai naga -27.9..-24.1, bahu bundar 15.4..18.5, jambul -8.4..-6.9, ekor -44.0..-39.5
      mata min 50 px; tinggi kepala 35-35 px (langkah 0.0%, rentang 0.0%); tidak loop
      kunci f16: helm 34x31, mata 86 px, perisai naga 1342 px (badan 734), pedang 702 px, kepalan 176 px, jambul 384 px, ekor 66 px
      urutan: topeng buka f1, puncak f4, tutup f6 (isi topeng puncak 372 px, wajah Gobyet 244 px, mata 24 px); pedang terangkat f9, menusuk f11; kaki di batu f[13, 14, 15, 16, 17, 18, 19]; noda 203 -> 0 px, sebagian f[15, 16, 17, 18]
  warna seluruh karakter: 25 (batas 28); di luar palet yang diizinkan: 0
  V11: lulus

[V10] Ukuran (baris hero dan anggaran pack)
  gerbang K:  9 aset, GIF terbesar 296819 byte, total file  1867487 byte
  hero: 9 aset, GIF terbesar 296819 byte (batas 307200), total GIF + sheet 1867487 byte (batas 2000000)
  proyeksi pertambahan total: 13074877 byte (12.47 MB); ambang peringatan 15 MB, batas keras 16 MB

HASIL: LULUS
```

### 4.2 Uji unit, resolver, browser

```
$ python3 -m unittest src/test_hero3.py src/test_hero2.py
Ran 24 tests ... OK
$ python3 -m unittest src/test_validate_pack.py
Ran 52 tests ... OK
$ node pack/resolver.test.js
# pass 25  # fail 0          (spesifikasi victory diperbarui: 20 frame)
$ node tools/e2e_preview.js
E2E: LULUS
$ node tools/gif_once_check.js
GIF-SEKALI: LULUS   victory_total_ms 3980, victory_last_frame_ms 1500, berhenti di frame terakhir, frame terakhir = frame sheet
$ python3 tools/hero_hashes.py --check
18 berkas; sama dengan pack/sha256-hero.txt
$ python3 tools/evolusi.py --check
17 berkas evolusi; sama dengan pack/sha256-evolusi.txt
```

## 5. Bukti visual (`pack/reports/hero3-victory/`, dibangkitkan `python3 tools/hero3_victory.py`)

| Berkas | Isi |
|---|---|
| `lembar.png` | 20 frame berurutan, 3×, dengan durasi; frame kunci ditandai |
| `topeng.png` | kepala f0-f7, 6×: topeng membuka, wajah Gobyet tersenyum, menutup dengan klik |
| `tusuk.png` | f8-f11: dicabut, diangkat, menukik, menancap |
| `batu-dan-usapan.png` | f11-f19 bagian kanan bawah, 5×: kaki naik ke batu, kepalan menyusuri bilah, noda hilang, kilau |
| `kunci-3-latar.png` | frame kunci f16 di latar terang, gelap, abu tengah |
| `victory.json` | angka per frame (topeng, wajah, mata, noda, batu, kontak kaki, posisi kepalan, sudut pedang) |

## 6. Bukti aset lama tidak berubah

- V1: `sha256-asli.txt` 27, `sha256-disetujui.txt` 89, `sha256-dibuat.txt` 242 identik (keluaran 4.1).
- Dari 18 berkas hero, hanya `gif/berserker-hero-victory.gif` dan `sheets/berserker-hero-victory.png` yang berubah; 8 state lain identik byte.
- `pack/manifest.json`: hanya sel `berserker-hero/victory` (jumlah frame 20, frame kunci 16, durasi).
- Galeri evolusi tidak berubah (`tools/evolusi.py --check`). Repo Bertahan-Bukan-hidup tetap di `696605e`.

## 7. Perubahan kode

- `src/hero3_scenes.py`: trek `victory` baru (`VICT_KEYS` 20 frame, `_wipe`, `_ON_ROCK`, `_WIPE`, batu `ROCK_*`, pedang `_XS = _VC + 36`), efek per frame, durasi, frame kunci 16.
- `src/hero3_fx.py`: `rock` berpuncak rata (`ROCK_TOP`).
- `src/hero3.py`: `STAIN_BLOBS` digeser ke dekat pelindung.
- `src/pack.py`: frame kunci `victory` 13 → 16. `src/validate_pack.py`: spesifikasi `victory` 20 frame, batas per GIF 300 KiB.
- `pack/resolver.test.js`, `tools/e2e_preview.js`: angka victory 20 frame. `tools/hero3_victory.py` (baru); `tools/hero3_revisi.py` memakai nomor frame baru.
- Dokumen: `pack/README.md` (tabel state, durasi GIF tanpa loop, anggaran, daftar bukti), `pack/PROGRESS.md`.

## 8. Tebakan dan ketidakpastian

- **Kehalusan gerak tidak terbukti** (tidak saya tonton sebagai GIF). Langkah topeng 0 → 0,25 → 0,625 → 1 cukup rapat di lembar frame; lompatan terbesar ada di f9 → f10 (pedang dari atas ke bawah dalam 60 ms, disengaja sebagai tebasan dengan smear).
- **Kaki di batu terbaca di 5×**; di ukuran asli (128×96 ×4) sepatu dan batu sama-sama kecil (batu 20×10 px), jadi keterbacaannya di layar sebenarnya tidak terbukti.
- **Senyum Gobyet** di ukuran asli hanya beberapa piksel mulut; perbedaan senyum tipis dan tersenyum mungkin tidak terlihat tanpa perbesaran.

## 9. Kelemahan yang saya lihat sendiri

1. **Tangan di frame usap terakhir (f18) 2 px di atas batas noda**: lengan tidak cukup panjang, jadi kepalan dijepit ke jangkauan maksimal (71,8 vs target 76). Masih menyentuh bilah.
2. **Noda f17 → f18 hampir sama** (59 → 58 px): sisa noda kecil, ditambah olesan yang terdorong ke bawah.
3. **Ekor kecil di `victory`** (66 px di frame kunci, 22% ekor idle) karena tertutup perisai; tidak termasuk keputusan "ekor sedang" yang hanya untuk state serangan.
4. **Ukuran**: GIF `victory` 296.819 B, sisa 3,4% dari batas per GIF yang baru; total hero 93,4% dari 2 MB.

## 10. Keputusan yang saya butuhkan darimu

1. `victory` 20 frame ini sudah sesuai, atau ada bagian yang mau diubah (topeng, tusukan, kaki di batu, usapan, akhir)?
2. Batas per GIF 300 KiB boleh?
3. Wajah Gobyet tetap skala 1, atau diperbesar?
4. Ekor di `victory` dibiarkan kecil, atau dibuat "sedang" seperti state serangan?
5. Pertanyaan lama yang belum terjawab: posisi ekor di state serangan (bercampur jambul), nada merah darah, pemetaan emote, dan animasi v3 sebelum revisi untuk galeri evolusi.

## 11. Daftar berkas di fase ini

```
src/hero3_scenes.py  src/hero3_fx.py  src/hero3.py  src/pack.py  src/validate_pack.py
pack/resolver.test.js  tools/e2e_preview.js  tools/hero3_victory.py (baru)  tools/hero3_revisi.py  tools/hero3_animasi.py
gif/berserker-hero-victory.gif  sheets/berserker-hero-victory.png  pack/manifest.json  pack/sha256-hero.txt
pack/README.md  pack/PROGRESS.md
pack/reports/hero3-victory.md (laporan ini)  pack/reports/hero3-victory/ (bukti)
```

Menunggu persetujuan gaya untuk Berserker Hero.
