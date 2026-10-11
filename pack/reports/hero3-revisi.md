# Berserker Hero v3: revisi setelah fase animasi (perisai naga, wajah Gobyet, darah merah, tepi terang, ekor sedang, anggaran 2 MB, evolusi), laporan STOP

Branch `claude/gobyet-hero`. Tidak di-merge, `main` tidak disentuh, tidak ada force-push, repo Bertahan-Bukan-hidup tidak disentuh. Format mengikuti bagian 8 brief awal ("LAPORAN (tiap STOP)").

**Dikerjakan:** jawabanmu atas enam keputusan di `hero3-animasi.md` bagian 10, ditambah perisai naga (tiga pesanmu: "prisainya dibuat semirip mungkin dengan naga", gambar perisai "disesuaikan ukuran dan warnanya", "perbesar lagi prisainya") dan "A. halo dan tepi terang". Sembilan state tetap (jumlah frame, durasi, dan urutan tidak berubah); yang berubah adalah gambar tiap frame. Aset hero di `gif/`, `sheets/`, dan `pack/sha256-hero.txt` diganti; `pack/manifest.json` tidak berubah (jumlah frame dan durasi sama). Galeri evolusi baru di `pack/evolusi/`.

**Tidak diklaim:** gaya bagus, mirip naga, atau disetujui; itu keputusanmu. Hal yang tidak terbukti ditulis "tidak terbukti". **Saya tidak menonton GIF sebagai gerak**: gerak diperiksa lewat lembar frame, pengukuran piksel, validator, dan uji Chromium.

## 1. Ringkasan: keputusanmu dan yang saya buat

| No. | Keputusanmu | Yang saya buat | Angka |
|---|---|---|---|
| 1 | "dalamnya wajah monyet Gobyet" | Rongga mesin diganti **wajah Gobyet asli** (`monkey.head`, skala 1: bulu cokelat, wajah krem bentuk hati, mata besar, hidung, mulut). Pintu topeng sekarang bergeser sampai 10 px (sebelumnya 8) supaya bulu di kedua sisi wajah ikut terlihat. Di puncak bukaan (`victory` f3) Gobyet tersenyum; di frame lain ekspresinya diturunkan dari visor. Zirah dan badan tetap bukan Gobyet. | wajah 244 px, mata 24 px di f3; terlihat hanya di f1-f4 |
| 2 | "ganti jadi merah" | Darah monster `m1..m3` sekarang **merah darah gelap** dengan kilau basah: (74, 2, 12), (140, 10, 22), (232, 96, 88). Saya mencoba empat nada (bagian 3); merah keunguan lebih mudah dibedakan dari api bilah tetapi terlihat pink, merah terang menyatu dengan api. | noda 226 → 0 px, hanya di `victory` |
| 3 | "yang terbaik maksimal 2mb" | Batas total GIF + sheet hero **2.000.000 B** (dibaca ketat, bukan 2 MiB); batas per GIF **262.144 B** (256 KiB, usulan saya, karena kamu tidak menyebut batas per GIF). Ruang tambahan terpakai oleh perisai, tepi terang, dan wajah. | total **1.801.931 B (90,1%)**, GIF terbesar `victory` 232.278 B |
| 4 | Ekor di serangan: "sedang aja" | Di frame tumbukan `attack-leap`, `attack-smash`, `miss` kipas ekor dipindah ke atas-belakang dan dibesarkan supaya tidak tertutup perisai; di frame lain kembali bertahap supaya tidak terpotong tepi kanvas. V11 sekarang mewajibkan 35-80% ekor idle (rentang usulan saya untuk "sedang"). | 148, 148, 149 px = **50%** ekor idle (sebelumnya 0-17% dengan perisai baru, 10-20% di aset lama) |
| 5 | Kode v1/v2: "simpan aja dan up juga sebagai evolusi" | Kode tetap. Galeri `pack/evolusi/` (halaman `index.html`, README, hash `pack/sha256-evolusi.txt`): 8 GIF v1 byte persis dari commit `fd5d899`, pose kunci v1, v2, v3. Tautan dari `pack/preview.html`. | 17 berkas, 951.272 B; di luar manifest dan anggaran hero |
| 6 | "A. halo dan tepi terang" | Penempatan **A** (tidak berubah). **Tepi terang** 1 px `n4` di luar setiap tepi gelap, tanpa warna baru; halo krem di preview tetap ada. | 4,40:1 di latar gelap (garis hitam sendiri 1,15:1) |
| + | Perisai naga, sesuai gambar perisai, diperbesar | Pelindung bahu raksasa diganti **perisai naga**: bentuk dari gambar perisaimu (ujung tombak, sayap mengembang, permata tengah, meruncing ke bawah), dibuat mirip naga (sayap tiga jari tulang berselaput bergerigi, mata celah tegak sebagai permata, dua tanduk, sisik, tepi bawah menyala), warna karakter (perak → besi hitam, emas → merah darah, sian → merah menyala). | idle 43×69 px, 1.267 px terlihat (pelindung bahu lama 419 px) |

Pemetaan emote (keputusan lama nomor 3 di laporan model) belum kamu jawab; pemetaan yang ada tetap dipakai.

## 2. Tabel aset

| State | Frame | Loop | GIF sebelum (`a49e315`) | GIF sekarang | Sheet sekarang |
|---|---:|---|---:|---:|---:|
| idle | 12 | ya | 157.110 | 178.727 | 15.278 |
| run | 12 | ya | 157.639 | 181.994 | 18.924 |
| rage | 12 | tidak | 144.120 | 164.213 | 26.683 |
| attack-leap | 14 | ya | 173.181 | 204.536 | 33.470 |
| attack-smash | 12 | ya | 149.148 | 174.997 | 27.323 |
| miss | 10 | ya | 121.038 | 139.751 | 24.049 |
| exhaustion | 12 | ya | 134.707 | 157.916 | 12.719 |
| defeated | 14 | ya | 140.833 | 167.139 | 12.002 |
| victory | 16 | tidak | 200.253 | 232.278 | 29.932 |
| **total GIF + sheet** | | | 1.563.050 | **1.801.931** (batas 2.000.000) | |

Warna seluruh karakter: **25** (batas 28): 11 kunci hero, 5 kunci wajah Gobyet (`B b F f M`), 9 kunci efek (batu, kayu, darah).

## 3. Tafsiran dan asumsi (salah satu bisa keliru; mohon koreksi)

1. **"Prisai" = pelindung bahu raksasa di kiri**, bukan perisai baru yang dipegang. Alasannya: itu satu-satunya bagian berbentuk perisai, dan tangan kiri memegang pedang di hampir semua state, jadi perisai pegangan akan mengubah semua animasi. Perisai kuletakkan di bahu kiri, di depan lengan, di belakang helm. Kalau maksudmu perisai terpisah (dipegang atau di punggung), bilang saja.
2. **Gambar perisaimu = bentuk dasar**, "mirip naga" = motif yang ditambahkan ke bentuk itu: sayap emas jadi sayap naga, permata sian jadi mata naga, ujung atas diapit dua tanduk, bagian bawah bersisik.
3. **"Perbesar lagi"**: dari percobaan pertama (kira-kira seukuran pelindung bahu lama) ke 43×69 px, hampir setinggi karakter. Lebih besar dari ini membuat sayap terpotong tepi kiri kanvas di state yang badannya di kiri; ujung sayap sudah saya rapatkan 2-3 px dan sumbu perisai digeser 3 px ke kanan untuk itu.
4. **Wajah Gobyet skala 1** (`monkey.head` asli, ukuran sama dengan Gobyet 64×48 dalam piksel kanvas). Di kanvas 128×96 ×4 artinya wajahnya tampil setengah ukuran Gobyet di kostum lain. Garis tepi, pupil, dan putih mata memakai warna hero (`n0`, `wh`) supaya palet tidak lewat 28. Telinga tidak terlihat (tertutup helm).
5. **Ekspresi wajah Gobyet** di `victory`: f1-f2 dan f4 senyum tipis (`smirk`), f3 tersenyum (`smile`) dengan mata terbuka. Mata tertutup bahagia (`^ ^`) hanya 8 px dan gagal batas keterbacaan mata (≥ 12 px), jadi tidak dipakai.
6. **"Maksimal 2mb" = 2.000.000 byte**, total GIF + sheet hero. Batas per GIF 256 KiB adalah usulan saya. Saya tidak menambah frame `victory` (kembali ke 20); perkiraan saya GIF `victory` 20 frame melewati 256 KiB (tidak terbukti; tidak saya ekspor).
7. **"Sedang" = 35-80% ekor idle** di frame tumbukan. Angka itu usulan saya.
8. **Darah merah**: dari empat nada yang saya coba (gambar di folder kerja, bukan repo), merah darah gelap terbaca paling jelas sebagai darah di atas bilah hitam. Jarak warnanya ke merah zirah lebih kecil (Delta E 8,9 ke `q2`) daripada versi keunguan (17-25); bedanya dibawa oleh nada lebih gelap dan kilau terang.
9. **Evolusi**: v1 dan v2 diunggah apa adanya (v1 8 GIF, v2 hanya 3 pose kunci karena tidak pernah dianimasikan). Animasi v3 sebelum revisi ini (rongga mesin, pelindung bahu lama) tidak ikut evolusi; ada di commit `a49e315` bila kamu mau menambahkannya.

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
  idle             12 ya    128x96     4 0     174.5     lulus
      sisi (dx px relatif tengah badan, - kiri / + kanan): perisai naga -27.2..-27.2, bahu bundar 15.6..15.7, jambul -8.4..-7.2, ekor -50.5..-48.7
      mata min 52 px; tinggi kepala 35-35 px (langkah 0.0%, rentang 0.0%); seam 464 <= langkah maks 2638 (seam/median 1.27)
      kunci f0: helm 34x31, mata 86 px, perisai naga 1267 px (badan 723), pedang 836 px, kepalan 176 px, jambul 410 px, ekor 298 px
  run              12 ya    128x96     4 10    177.7     lulus
      sisi (dx px relatif tengah badan, - kiri / + kanan): perisai naga -27.2..-26.9, bahu bundar 13.0..15.4, jambul -6.5..-5.2, ekor -49.1..-47.2
      mata min 86 px; tinggi kepala 35-35 px (langkah 0.0%, rentang 0.0%); seam 4403 <= langkah maks 4867 (seam/median 1.02); IoU run berurutan maks 0.89
      kunci f10: helm 34x31, mata 86 px, perisai naga 1460 px (badan 769), pedang 862 px, kepalan 177 px, jambul 377 px, ekor 272 px
  rage             12 tidak 128x96     4 6     160.4     lulus
      sisi (dx px relatif tengah badan, - kiri / + kanan): perisai naga -28.3..-27.2, bahu bundar 15.1..18.0, jambul -12.2..-6.6, ekor -44.2..-40.8
      mata min 66 px; tinggi kepala 35-35 px (langkah 0.0%, rentang 0.0%); tidak loop; garis kejut f4-f10, merah menyala 328 -> 1206 piksel
      kunci f6: helm 34x31, mata 110 px, perisai naga 1282 px (badan 736), pedang 856 px, kepalan 165 px, jambul 486 px, ekor 78 px
  attack-leap      14 ya    128x96     4 8     199.7     lulus
      sisi (dx px relatif tengah badan, - kiri / + kanan): perisai naga -28.2..-22.7, bahu bundar 14.1..17.9, jambul -8.8..-6.8, ekor -31.6..-3.3
      mata min 86 px; tinggi kepala 35-35 px (langkah 0.0%, rentang 0.0%); seam 3899 <= langkah maks 5719 (seam/median 0.77); smear sebelum tumbukan f[6, 7], frame tumbukan 260 ms (median 105)
      kunci f8: helm 34x31, mata 110 px, perisai naga 1241 px (badan 715), pedang 497 px, kepalan 176 px, jambul 397 px, ekor 148 px (49% ekor idle 298)
  attack-smash     12 ya    128x96     4 7     170.9     lulus
      sisi (dx px relatif tengah badan, - kiri / + kanan): perisai naga -28.1..-22.2, bahu bundar 15.5..17.5, jambul -8.8..-7.0, ekor -29.6..-24.5
      mata min 86 px; tinggi kepala 35-35 px (langkah 0.0%, rentang 0.0%); seam 42 <= langkah maks 5364 (seam/median 0.01); smear sebelum tumbukan f[5, 6], frame tumbukan 240 ms (median 110)
      kunci f7: helm 34x31, mata 110 px, perisai naga 1278 px (badan 734), pedang 524 px, kepalan 176 px, jambul 397 px, ekor 148 px (49% ekor idle 298)
  miss             10 ya    128x96     4 6     136.5     lulus
      sisi (dx px relatif tengah badan, - kiri / + kanan): perisai naga -28.1..-21.7, bahu bundar 14.3..26.0, jambul -9.4..-7.0, ekor -29.1..-23.0
      mata min 66 px; tinggi kepala 35-35 px (langkah 0.0%, rentang 0.0%); seam 2707 <= langkah maks 4954 (seam/median 0.59); smear sebelum tumbukan f[3, 4], frame tumbukan 220 ms (median 140)
      kunci f6: helm 34x31, mata 102 px, perisai naga 1219 px (badan 695), pedang 588 px, kepalan 128 px, jambul 421 px, ekor 149 px (50% ekor idle 298)
  exhaustion       12 ya    128x96     4 5     154.2     lulus
      sisi (dx px relatif tengah badan, - kiri / + kanan): perisai naga -27.6..-27.5, bahu bundar 16.8..17.1, jambul -6.6..-5.9, ekor -47.7..-44.8
      mata min 52 px; tinggi kepala 35-35 px (langkah 0.0%, rentang 0.0%); seam 322 <= langkah maks 2759 (seam/median 0.12)
      kunci f5: helm 34x31, mata 62 px, perisai naga 1339 px (badan 724), pedang 525 px, kepalan 169 px, jambul 368 px, ekor 212 px
  defeated         14 ya    128x96     4 3     163.2     lulus
      sisi (dx px relatif tengah badan, - kiri / + kanan): perisai naga -27.6..-27.5, bahu bundar 17.3..17.4, jambul -6.1..-5.9, ekor -45.1..-43.9
      mata min 52 px; tinggi kepala 35-35 px (langkah 0.0%, rentang 0.0%); seam 125 <= langkah maks 2230 (seam/median 1.11)
      kunci f3: helm 34x31, mata 62 px, perisai naga 1341 px (badan 726), pedang 407 px, kepalan 176 px, jambul 374 px, ekor 120 px
  victory          16 tidak 128x96     4 13    226.8     lulus
      sisi (dx px relatif tengah badan, - kiri / + kanan): perisai naga -28.0..-24.0, bahu bundar 13.7..18.7, jambul -8.4..-6.8, ekor -43.8..-39.3
      mata min 49 px; tinggi kepala 35-35 px (langkah 0.0%, rentang 0.0%); tidak loop
      kunci f13: helm 34x31, mata 86 px, perisai naga 1315 px (badan 725), pedang 683 px, kepalan 176 px, jambul 384 px, ekor 73 px
      urutan: topeng buka f1, puncak f3, tutup f4 (isi topeng puncak 372 px, wajah Gobyet 244 px, mata 24 px); pedang terangkat f7, menusuk f9; kaki di batu f[11, 12, 13, 14, 15]; noda 226 -> 0 px, sebagian f[12, 13, 14]
  warna seluruh karakter: 25 (batas 28); di luar palet yang diizinkan: 0
  kontras luminans WCAG (rasio; laporan, bukan lulus/gagal) warna kunci hero terhadap empat latar pratinjau: terang (250, 247, 240), gelap (24, 28, 44), abu tengah (128, 128, 128), halo krem (232, 218, 186)
    kunci                           terang     gelap  abu tengah | dengan halo (tetangga tepi = halo, sama di semua latar)
    n0   garis tepi besi hitam     18.17:1     1.15:1       4.92:1 | 14.05:1
    n1   besi bayangan             16.08:1     1.02:1       4.36:1 | 12.43:1
    n2   besi dasar                12.80:1     1.24:1       3.47:1 | 9.89:1
    n3   besi terang                7.81:1     2.02:1       2.12:1 | 6.04:1
    n4   baja terang                3.59:1     4.40:1       1.03:1 | 2.78:1
    q1   merah gelap               11.92:1     1.33:1       3.23:1 | 9.21:1
    q2   merah                      7.19:1     2.20:1       1.95:1 | 5.55:1
    q3   merah terang               4.44:1     3.56:1       1.20:1 | 3.43:1
    q4   merah menyala              2.55:1     6.21:1       1.45:1 | 1.97:1
    halo itu sendiri terhadap latar: terang 1.29:1, gelap 12.22:1, abu tengah 2.85:1
  tepi terang aset (keputusan pemilik): garis luar 1 px n4 di sebelah setiap tepi gelap; terhadap latar terang 3.59:1, gelap 4.40:1, abu tengah 1.03:1 (di abu tengah garis hitam di dalamnya yang terbaca: 4.92:1)
  CATATAN: garis tepi besi hitam sendiri terhadap latar gelap 1.15:1; tertutup tepi terang n4 di aset, dan halo pratinjau 14.05:1
  V11: lulus

[V10] Ukuran (baris hero dan anggaran pack)
  gerbang K:  9 aset, GIF terbesar 232278 byte, total file  1801931 byte
  hero: 9 aset, GIF terbesar 232278 byte (batas 262144), total GIF + sheet 1801931 byte (batas 2000000)
  proyeksi pertambahan total: 13009321 byte (12.41 MB); ambang peringatan 15 MB, batas keras 16 MB

HASIL: LULUS
```

### 4.2 Uji unit, resolver, browser

```
$ python3 -m unittest src/test_hero3.py src/test_hero2.py
Ran 24 tests ... OK
$ python3 -m unittest src/test_validate_pack.py
Ran 52 tests ... OK
$ node pack/resolver.test.js
# tests 25  # pass 25  # fail 0
$ node tools/e2e_preview.js
E2E: LULUS
$ node tools/gif_once_check.js
GIF-SEKALI: LULUS   (rage dan victory berhenti di frame terakhir di Chromium 141)
$ python3 tools/hero_hashes.py --check
18 berkas; sama dengan pack/sha256-hero.txt
$ python3 tools/evolusi.py --check
17 berkas evolusi; sama dengan pack/sha256-evolusi.txt
```

Tes baru: wajah Gobyet hanya di balik topeng dan hanya saat terbuka; perisai naga cukup besar dan punya mata celah, tanduk, sisik, sayap; tidak ada tepi gelap tanpa tepi terang di semua frame (dan uji negatif: menghapus tepi terang memunculkan temuan); darah monster benar-benar merah; ekor serangan 35-80% ekor idle. Halaman evolusi diuji di Chromium desktop 1200 px dan ponsel 390 px: 29 gambar termuat, tidak ada yang rusak, tidak ada scroll mendatar.

## 5. Bukti visual (`pack/reports/hero3-revisi/`, dibangkitkan `python3 tools/hero3_revisi.py`)

| Berkas | Isi |
|---|---|
| `perisai-naga.png` | perisai pose idle 8× di latar terang dan gelap; run dan attack-smash 4× |
| `wajah-gobyet.png` | helm dengan topeng 0-100% terbuka (visor look dan angry) dan `victory` f1-f5, 8× |
| `tepi-terang.png` | idle dan attack-smash di latar terang, gelap, abu tengah, tanpa dan dengan tepi terang, 3× |
| `ekor-serangan.png` | frame tumbukan tiga state serangan dengan ekor ditandai merah menyala, dan idle sebagai pembanding |
| `darah-monster.png` | bilah di `victory` f9, f12-f15, 6× |
| `kunci-9-state.png`, `<state>-lembar.png`, `victory-topeng.png`, `victory-usapan.png` | sama seperti fase animasi, dibangkitkan ulang dari aset sekarang |
| `revisi.json`, `ukuran.json` | angka mentah semua tabel di laporan ini |

Halaman evolusi: `pack/evolusi/index.html`.

## 6. Bukti aset lama tidak berubah

- V1: `sha256-asli.txt` 27, `sha256-disetujui.txt` 89, `sha256-dibuat.txt` 242 identik (keluaran 4.1).
- Yang berubah hanya 18 berkas hero (`gif/berserker-hero-*`, `sheets/berserker-hero-*`) dan `pack/sha256-hero.txt`. `pack/manifest.json` tidak berubah (`git diff` kosong).
- GIF v1 di `pack/evolusi/v1/` diperiksa byte demi byte terhadap hash v1 yang dikunci di commit `fd5d899` saat dibangkitkan.
- Repo Bertahan-Bukan-hidup tetap di `696605e`, tanpa perubahan.

## 7. Perubahan rig, pipeline, validator

- `src/hero3.py`: `pauldron_big` menjadi perisai naga (konstanta `SHIELD_*`); `cavity` menggambar wajah Gobyet (`GOBYET_FACE_KEYS`, `GOBYET_REMAP`, `GOBYET_EXPR`, parameter pose `face`); `MASK_MAX_SHIFT` 8 → 10; `edge_light` (tepi terang, setelah efek); pusat ekor bisa digeser (`tail_dx`, `tail_dy`); paku bahu bundar diberi nama bagian sendiri (`shoulder_spike`).
- `src/hero3_fx.py`: warna darah `m1..m3` merah.
- `src/hero3_scenes.py`: `TAIL_PEAK` dan `tail_params` (ekor per frame di state serangan); ekspresi wajah Gobyet di `victory` f1-f4.
- `src/hero3_check.py` dan V11 di `src/validate_pack.py`: identitas (wajah Gobyet hanya di balik topeng terbuka), tepi terang, perisai naga (≥ 650 px di frame kunci), ekor sedang, wajah di puncak victory (≥ 200 px, mata ≥ 12 px); anggaran 2.000.000 B dan 256 KiB per GIF.
- Baru: `tools/evolusi.py`, `tools/hero3_revisi.py`, `pack/evolusi/`, `pack/sha256-evolusi.txt`.
- Dokumen: `pack/README.md` (bagian hero, V11, anggaran, evolusi), `pack/STYLE.md`, `pack/PROGRESS.md`, `pack/preview.html` (tautan evolusi).

## 8. Tebakan dan ketidakpastian

- **Kemiripan dengan gambar perisaimu tidak terbukti.** Gambar itu kecil; yang saya ambil: siluet tinggi dengan ujung atas runcing, dua sayap mengembang di sepertiga atas, permata lonjong di tengah atas, chevron di bawah permata, ujung bawah runcing dengan tepi bercahaya. Hiasan emas di puncak saya ganti tanduk.
- **"Mirip naga" tidak terbukti terbaca** di ukuran asli (128×96, ×4). Yang paling jelas di bukti 8×: sayap bertulang jari dan mata celah. Sisik di bagian bawah bisa terbaca sebagai pola rantai.
- **Wajah Gobyet terbaca sebagai Gobyet?** Tanpa telinga dan pada setengah ukuran Gobyet biasa, wajahnya bisa terbaca sebagai wajah anak berambut cokelat. Tidak diuji pada orang lain.
- **Ekor sedang** dihitung dari jumlah piksel; secara visual sebagian panah menempel di jambul (keduanya merah), jadi "terlihat sebagai ekor" tidak terbukti.

## 9. Kelemahan yang saya lihat sendiri

1. **Ekor di state serangan bercampur dengan jambul**: dipindah ke atas-belakang, panahnya berada di area jambul yang sama merahnya; di `attack-leap` satu panah tampak melayang di kiri atas (`ekor-serangan.png`).
2. **Perisai mendominasi**: perisai 1.267 px terlihat vs seluruh kepala (helm, visor, cakram telinga) 1.030 px di idle; separuh kiri karakter sekarang perisai. Sayap kanan hampir seluruhnya tertutup helm, jadi perisai terlihat tidak simetris.
3. **Siluet `run` lebih mirip antar frame**: IoU berurutan maksimum naik ke 0,89 (batas 0,90), karena perisai besar bergerak sedikit.
4. **Tepi terang di latar terang** terlihat sebagai garis abu tipis di sekeliling karakter (gaya "stiker"); di panah ekor yang tanpa garis tepi, tepi terang hanya muncul di sebagian piksel, jadi kipas ekor tampak berbintik di latar gelap.
5. **Darah merah lebih dekat ke merah zirah** (Delta E 8,9) daripada hijau lama; di bagian tepi api bilah noda kurang menonjol.
6. **Wajah Gobyet kecil** (lihat 8) dan hanya muncul 4 frame (±600 ms).
7. **Sisa ruang anggaran** 198 KB (9,9%); GIF `victory` 232.278 B dari 262.144 B.

## 10. Keputusan yang saya butuhkan darimu

1. **Perisai**: tafsiran nomor 3.1 (perisai menggantikan pelindung bahu kiri) benar, atau mau perisai terpisah? Ukurannya sekarang pas, terlalu besar, atau masih kurang?
2. **Wajah Gobyet**: ukuran skala 1 cukup, atau diperbesar (skala 1,5 seperti v1, tetapi hanya bagian tengah wajah yang terlihat dan palet bisa lewat 28)?
3. **Ekor di serangan**: posisi di atas-belakang (bercampur jambul) boleh, atau lebih baik dikecilkan lagi di belakang perisai?
4. **Darah**: merah darah gelap ini, atau nada lain (merah keunguan lebih mudah dibedakan dari api bilah)?
5. **Batas per GIF 256 KiB** boleh, dan apakah sisa ruang dipakai untuk menambah frame `victory`?
6. **Pemetaan emote** (keputusan lama): pemetaan sekarang tetap?
7. **Evolusi**: animasi v3 sebelum revisi ini (commit `a49e315`) ikut dimasukkan sebagai tahap tersendiri?

## 11. Daftar berkas di fase ini

```
src/hero3.py  src/hero3_fx.py  src/hero3_scenes.py  src/hero3_check.py  src/validate_pack.py
src/test_hero3.py  src/test_validate_pack.py
tools/hero3_animasi.py  tools/hero3_revisi.py (baru)  tools/evolusi.py (baru)
gif/berserker-hero-{idle,run,rage,attack-leap,attack-smash,miss,exhaustion,defeated,victory}.gif
sheets/berserker-hero-{...}.png
pack/sha256-hero.txt  pack/sha256-evolusi.txt (baru)
pack/evolusi/ (baru: index.html, README.md, v1/, v2/, v3/)
pack/README.md  pack/STYLE.md  pack/PROGRESS.md  pack/preview.html
pack/reports/hero3-revisi.md (laporan ini)  pack/reports/hero3-revisi/ (bukti)
```

Menunggu persetujuan gaya untuk Berserker Hero.
