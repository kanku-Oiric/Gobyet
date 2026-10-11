# Berserker Hero v2: Fase Body (model badan), laporan STOP

Branch `claude/gobyet-hero`. Tidak di-merge, `main` tidak disentuh, tidak ada force-push, repo Bertahan-Bukan-hidup tidak disentuh. Format mengikuti bagian 8 brief awal ("LAPORAN (tiap STOP)").

**Yang dikerjakan:** hanya model badan v2 dalam tiga pose kunci statis (`idle`, `run` puncak, `attack-smash` saat tumbukan), kode rig baru, tes, dan bukti gambar. **Belum ada GIF, sheet, manifest, atau hash baru.** Armor dan senjata final belum dikerjakan (itu Fase Armor, menunggu persetujuanmu). Pedang di gambar ini adalah **pengganti** (balok polos) agar pose terbaca; bukan desain.

**Tidak diklaim:** gaya bagus, mirip, atau disetujui. Itu keputusanmu. Hal yang tidak terbukti ditulis "tidak terbukti".

## 1. Ringkasan

| Hal | Hasil |
|---|---|
| Arah | v1 (kerangka naga) ditolak oleh pemilik; v2 dibangun ulang dari referensi 1 (bentuk badan, kepala, proporsi) dengan palet hitam-besi dan merah-darah dari referensi 2. Emote wajah dan timing animasi v1 yang kamu setujui tidak dibuang (belum dipindah; itu fase sesudah Armor). |
| Rig | `src/hero2.py` (baru, 529 baris). Kode v1 (`src/hero.py`, `src/hero_scenes.py`, ...) tidak diubah; aset hero v1 tidak diubah (uji hash). |
| Tiga pose kunci | `pack/reports/hero2-body/kunci-3-pose.png` di tiga latar (terang, gelap, abu tengah). |
| Wajah Gobyet | Mata, hidung, mulut, telinga: **100%** terlihat di ketiga pose (diukur terhadap kepala sendirian, bagian 4). |
| Warna | 22 kunci di tiga pose (efek ikut dihitung); batas karakter 28. |
| Tes | `src/test_hero2.py`: 8 OK. `src/test_validate_pack.py`: 44 tes OK (164,7 dtk). `validate_pack.py --hero-only`: **LULUS**, V1 tiga berkas kunci lama dan `sha256-hero.txt` identik (bagian 6). |

## 2. Spesifikasi yang saya ambil dari tiap referensi

Referensi tidak disimpan di repo; saya hanya mengukur dan menurunkan bentuk (tanpa menjiplak piksel, tanpa salin 1:1 karakter berlisensi). Zoom analisis ada di folder kerja sementara, bukan di repo.

**Referensi 1 (`261…jpg`): badan, proporsi, kepala.**

| Ciri di referensi | Saya terjemahkan menjadi | Bagian |
|---|---|---|
| Kepala + jambul sangat besar, hampir separuh tinggi tubuh, tanpa leher | Kepala + jambul **55,2%** tinggi tubuh (idle); badan (kepala ke sabuk) 27,6%; kaki 17,2% | 1, 2, 3 |
| Jambul merah runcing menyebar ke belakang-atas | Lima bilah jambul merah (tiga warna), runcing, menyebar | 1 |
| Pita alis berbentuk V di dahi | Pita alis V gelap dengan garis cahaya merah | 2 |
| Pelindung bahu mekanis raksasa di sisi kiri layar, sirip tanduk tinggi | Cangkang bahu 27 px lebar (kepala 42 px), dua sirip tanduk tinggi, palka tiga celah, cincin berinti merah, paku merah di bawah | 6, 7, 8 |
| Pelindung bahu bulat + kepalan di sisi senjata | Cakram bahu berlapis cincin + sarung tangan besar | 9, 16 |
| Perut sisik heksagonal oranye | Panel perut sisik heksagonal **merah darah** + sabuk + gesper bercahaya | 11, 12 |
| Sepatu pendek bergerigi | Sepatu besar, ujung bertopi, paku merah di belakang pergelangan | 14 |
| Ekor kipas berujung panah | Ekor dua busur konsentris dengan ujung panah (merah), ditempel di pinggang | 15 |

**Referensi 2 (`4a36c…jpg`): zirah, palet, senjata (zirah final di Fase Armor).**

| Ciri | Di Fase Body | Ditunda ke Fase Armor |
|---|---|---|
| Pelat hitam, garis merah | Palet besi hitam `k0-k4` + deret merah `dr, mr, br, hr, gl` dipakai di semua bagian | Pola pelat, garis tepi merah, lampu strip |
| Visor silang merah, plume api merah | Garis dahi vertikal + pita V membentuk silang merah; jambul merah | Visor/penutup bergaya referensi 2 bila kamu minta |
| Pedang hitam raksasa bertepi api merah | Pedang pengganti, polos | Pedang final lebar bertepi api |

## 3. Asumsi yang saya ambil (salah satu bisa keliru; mohon koreksi)

1. **"Kesan red blood" = warna dan pola saja.** Merah gelap sampai merah menyala pada jambul, pita alis, perut, ventilasi, paku, ekor. **Tidak ada darah, luka, atau kematian brutal**; aturan keras brief awal (nomor 4) tetap berlaku, termasuk efek serangan hanya mengenai lantai atau balok kayu.
2. **Wajah dan telinga Gobyet tetap terlihat penuh** di bawah helm (jendela wajah terbuka), bukan tertutup visor. Alasannya emote adalah bagian yang kamu bilang sudah bagus.
3. **Hitam + merah sekarang boleh.** Brief awal melarang palet itu untuk v1; saya baca "pakai referensi 2" sebagai pencabutan larangan itu untuk v2.
4. **Pedang di fase ini pengganti.** Panjang 56 px, lebar 12 px, polos.
5. **Kanvas tetap 128×96, GIF skala 4** (belum diekspor).
6. **"Sedikit modern"** saya terjemahkan sebagai garis cahaya merah tipis (strip) di helm, dada, dan sepatu, serta permukaan pelat yang halus (bukan paku tajam semuanya). Ukuran "sedikit" tidak terbukti; ini tebakan.

## 4. Tabel aset

Fase ini tidak mengekspor aset. Yang ada hanya tiga pose kunci statis (PNG, bukan bagian pack):

| Pose | State tujuan | Frame | Durasi | Ukuran badan (tinggi × lebar px) | Kotak semua piksel (x0, y0, x1, y1) | Warna |
|---|---|---:|---|---|---|---:|
| idle | `idle` (frame 0) | 1 (statis) | tidak berlaku | 87 × 72 | 7, 3, 122, 89 | 20 |
| run | `run` (puncak langkah) | 1 (statis) | tidak berlaku | 85 × 79 | 6, 1, 123, 86 | 22 |
| attack-smash | `attack-smash` (tumbukan) | 1 (statis) | tidak berlaku | 79 × 70 | 6, 11, 119, 89 | 22 |

Keyframe tiap pose ada di `src/hero2.py` (`pose_idle`, `pose_run_peak`, `pose_smash_hit`). Pose smash menampilkan bilah utuh dari genggaman sampai balok kayu. Versi pertama pose ini punya bilah yang sebagian besar tertutup balok dan busur serta balok menyentuh tepi kanan kanvas (x=127); saya temukan sendiri dari pembacaan gambar, memperbaikinya, dan menambah tes tepi (bagian 6.5).

## 5. Bukti visual

Semua gambar di `pack/reports/hero2-body/`.

| Berkas | Isi |
|---|---|
| `kunci-3-pose.png` | tiga pose di latar terang, gelap, dan abu tengah |
| `peta-bagian.png` | pose idle dengan 17 bagian bernomor (legenda di bagian 5.1) |
| `helm-12x.png` | kepala diperbesar 12×: jambul, pita V, silang merah, wajah, telinga |
| `siluet.png` | siluet hitam di dua latar (pembacaan bentuk tanpa warna) |
| `bandingan-v1-v2.png` | v1 (ditolak) di samping v2, latar terang dan gelap |
| `detail-idle-8x.png`, `detail-run-8x.png`, `detail-attack-smash-8x.png` | tiap pose 8× |
| `ukuran.json` | semua angka di laporan ini (kotak, proporsi, piksel per bagian, palet, kontras) |

### 5.1 Legenda bagian (dari `peta-bagian.png`; piksel = jumlah piksel terlihat di pose idle)

| No | Bagian | Piksel |
|---:|---|---:|
| 1 | jambul bilah merah | 375 |
| 2 | tutup dahi + pita alis V (strip cahaya merah) | 323 |
| 3 | wajah Gobyet (mata, hidung, mulut) | 326 |
| 4 | telinga | 113 |
| 5 | sirip helm | 276 |
| 6 | pelindung bahu raksasa (cangkang bersudut) | 416 |
| 7 | sirip tanduk bahu | 144 |
| 8 | palka + cincin inti merah | 239 |
| 9 | pelindung bahu bundar | 74 |
| 10 | dada berventilasi (dua celah merah) | 161 |
| 11 | perut sisik heksagonal merah darah | 98 |
| 12 | sabuk + gesper bercahaya | 40 |
| 13 | pelat pinggul | 87 |
| 14 | sepatu besar + paku merah | 313 |
| 15 | ekor kipas panah | 339 |
| 16 | sarung tangan | 141 |
| 17 | pedang **PENGGANTI** (bukan desain akhir) | 391 |

## 6. Pengukuran dan validasi (keluaran mentah)

### 6.1 Proporsi vertikal (dari `ukuran.json`)

| Pose | Kepala + jambul | Badan (kepala ke sabuk) | Kaki (sabuk ke lantai) |
|---|---:|---:|---:|
| idle | 55,2% | 27,6% | 17,2% |
| run | 55,3% | 27,1% | 17,6% |
| attack-smash | 59,5% | 29,1% | 11,4% (jongkok) |

Lebar kepala dengan telinga 42 px; pelindung bahu raksasa 27 px.

### 6.2 Wajah terlihat dibanding kepala sendirian (piksel terlihat / piksel acuan)

| Pose | wajah | mata | mulut | telinga |
|---|---|---|---|---|
| idle | 217/217 | 64/64 | 13/13 | 113/113 |
| run | 199/199 | 64/64 | 41/41 | 113/113 |
| attack-smash | 211/211 | 52/52 | 41/41 | 113/113 |

(Mulut dan mata berbeda antar pose karena ekspresi berbeda; nilai acuan dihitung per pose, jadi rasio tetap 100%.)

### 6.3 Palet

22 kunci dipakai di tiga pose, termasuk efek (`bb, br, cb, cl, cs, dr, ei, ew, fb, fl, fs, gl, hr, k0, k1, k2, k3, k4, mo, mr, o1, rb`). Kunci baru v2 (`HERO2_PAL`): `k0..k4` besi hitam, `dr, mr, br, hr, gl` deret merah; terdaftar ke `monkey.PAL_HERO` dengan pemeriksaan tabrakan kunci. Batas 28 warna per karakter tidak dilampaui.

### 6.4 Kontras tepi (WCAG, rasio; laporan, bukan lulus/gagal)

| Kunci | Latar terang | Latar gelap | Abu tengah | Dengan halo krem |
|---|---:|---:|---:|---:|
| `k0` garis tepi hitam | 17,93 | **1,13** | 4,86 | 13,85 |
| `k1` | 15,74 | 1,00 | 4,26 | 12,17 |
| `k2` | 11,77 | 1,34 | 3,19 | 9,10 |
| `k3` | 6,91 | 2,29 | 1,87 | 5,34 |
| `k4` | 3,15 | 5,02 | 1,17 | 2,43 |
| `br` merah | 5,60 | 2,82 | 1,52 | 4,33 |
| `hr` merah terang | 3,57 | 4,43 | 1,03 | 2,76 |

Catatan: garis tepi hitam dan besi gelap **tidak terlihat** di latar gelap tanpa halo (1,13:1 dan 1,00:1). Karakter yang hampir hitam di latar `#181c2c` hanya terbaca lewat jambul merah dan wajah. Halo preview (sudah ada dari perbaikan teknis) memperbaiki ini di preview, tetapi aset yang dipakai tanpa halo akan sulit dibaca di latar gelap. Ini keputusan untukmu (bagian 9, nomor 3).

### 6.5 Uji unit

`python3 -W ignore -m unittest src/test_hero2.py`:

```
........
----------------------------------------------------------------------
Ran 8 tests in 2.586s

OK
```

Delapan tes: tiga pose ada; kanvas 128×96, tidak ada piksel di baris lantai dan di bawahnya, tidak ada piksel di tepi (y ≥ 1, x antara 1 dan lebar−2, supaya jambul, ekor, bilah, balok tidak terpotong); wajah dan telinga 100% terlihat; palet ≤ 28 dan terdaftar; tidak ada alfa parsial atau teks; bagian asimetris tetap di sisinya; pedang bertanda "BUKAN desain akhir"; tiga hash piksel pose kunci v1 tidak berubah (`idle 11974b75`, `run 08796a4b`, `attack-smash 76ba21ad`).

`python3 -W ignore -m unittest src/test_validate_pack.py`: `Ran 44 tests in 164.714s`, `OK`, exit 0.

Tes tepi kanvas diperketat di fase ini. Pose smash sebelum perbaikan punya piksel di x=127 (tepi), jadi tes yang baru akan gagal pada pose lama; pose lama lolos tes lama karena tes lama hanya memeriksa tepi atas dan lantai.

### 6.6 Aset lama dan hero v1 tidak berubah

`python3 -W ignore src/validate_pack.py --hero-only` (bagian V1, sisanya LULUS; exit 0):

```
[V1] Hash aset yang dikunci dan aset yang sudah dibuat
  sha256-asli.txt: 27 identik, 0 berubah/hilang
  sha256-disetujui.txt: 89 identik, 0 berubah/hilang
  sha256-dibuat.txt: 242 identik, 0 berubah/hilang
  sha256-hero.txt: 16 identik, 0 berubah/hilang
...
HASIL (--hero-only; bukan pengganti validasi penuh): LULUS
```

`git status --short` menunjukkan hanya berkas baru: `src/hero2.py`, `src/test_hero2.py`, `tools/hero2_body.py`, `pack/reports/hero2-body/`, dan laporan ini. Tidak ada berkas `gif/`, `sheets/`, `pack/manifest.json`, atau `pack/sha256-*.txt` yang berubah. Validasi penuh (`validate_pack.py` tanpa `--hero-only`) tidak dijalankan ulang di fase ini karena tidak ada aset atau kode pack yang berubah; itu **tidak dibuktikan ulang**, hanya V1 dan seluruh `--hero-only` yang dijalankan.

## 7. Perubahan rig dan pipeline

Semuanya aditif. Tidak ada berkas yang sudah ada diubah.

| Berkas | Isi |
|---|---|
| `src/hero2.py` (baru) | `HERO2_PAL`, bagian badan (jambul, helm, kerah, dada, perut, pelat pinggul, bahu raksasa, bahu bulat, sarung tangan, sepatu, kaki, ekor kipas), `pose()`, `geometry()`, `weapon_placeholder()`, `draw_hero()`, `head_only()`, `render_pose()`, tiga pose kunci. Memakai ulang `head_hd` Gobyet (tidak diubah), `PartCanvas`, `solid3`, `rim_pass` dan efek `hero.fx_*` dari v1. |
| `src/test_hero2.py` (baru) | 8 tes (bagian 6.5). |
| `tools/hero2_body.py` (baru) | Pembuat bukti gambar dan `ukuran.json`. |
| `pack/reports/hero2-body/` (baru) | Gambar dan `ukuran.json`. |

Belum ada: perubahan `COSTUMES`, `APPLIES`, `export.py`, validator V11, resolver, preview. Itu fase sesudah gaya disetujui.

## 8. Tebakan dan ketidakpastian

- **Tafsir referensi.** Saya menurunkan bentuk dari dua gambar; kemiripan dengan yang ada di kepalamu **tidak terbukti**. Bagian yang paling mungkin meleset: bentuk cangkang bahu raksasa (saya buat bersudut dengan dua sirip), rasio jambul, dan ekor.
- **Ekor kipas panah.** Pada referensi 1 bentuknya kipas panah; saya menyusunnya sebagai dua busur panah. Apakah itu ekor, bulu, atau sayap bagi pemilik tidak terbukti; saya menyebutnya "ekor".
- **Skala "kepala besar".** Kepala + jambul 55% tinggi tubuh adalah hasil ukur dari referensi dengan estimasi mata, bukan angka dari pemilik.
- **Merah vs hitam.** Diukur pada piksel yang digambar: merah (`dr, mr, br, hr, gl`) 12,6% pada idle, 12,2% pada run, 10,9% pada smash; besi hitam (`k0-k4`) 64,7%, 65,4%, 57,6%; sisanya wajah, telinga, efek. Proporsi merah:hitam yang kamu mau tidak diketahui; referensi 2 terlihat memakai lebih banyak merah pada tepi, tetapi itu pembacaan mata, bukan hitungan.
- **Pembacaan di ukuran kecil.** Tidak diuji pada ukuran GIF skala 1 (128×96 sebenarnya); gambar bukti diperbesar. Detail seperti ventilasi dan hex perut kemungkinan hilang di ukuran kecil.
- **Interpretasi "modern".** Lihat bagian 3 nomor 6.
- **Kepatuhan hak cipta.** Saya tidak menyalin piksel; bentuk, proporsi, dan susunan bagian mengikuti referensi yang kamu berikan. Tingkat kemiripan yang aman bagi proyekmu adalah keputusanmu; saya tidak menilai itu.

## 9. Kelemahan yang kamu lihat sendiri

1. **Pose `run`: kaki nyaris tidak terbaca.** Cangkang bahu raksasa dan pedang menutupi sebagian besar kaki; kaki belakang hanya terlihat sebagai blob kecil di bawah perut (lihat `detail-run-8x.png`). Siklus lari butuh kaki yang bergantian jelas; ini harus diperbaiki di fase animasi (misal pedang naik di bahu, kaki lebih jauh dari badan) dan belum terbukti terbaca.
2. **Lengan pendek.** Jangkauan lengan 16,5 px, jadi satu tangan memegang pedang dan tangan lain diam di pinggang. Genggaman dua tangan tidak dipakai.
3. **Kontras latar gelap.** Besi hitam lenyap di latar `#181c2c` (bagian 6.4); karakter bergantung pada halo atau latar terang.
4. **Siluet hampir satu blob.** Bahu raksasa, kepala, dan jambul menyatu (`siluet.png`); bentuk sulit dibedakan antar pose selain lewat pedang dan ekor.
5. **Ekor tertutup di smash.** Ekor diputar 24° agar muat kanvas; hanya sebagian panah terlihat, sisanya tertutup bahu raksasa.
6. **Pedang pengganti.** Belum bergaya referensi 2 (api, lebar, hitam-merah).
7. **Pose smash baru diperbaiki.** Lihat bagian 4: lengan terangkat lebih tinggi (genggaman di y=56) dan ekor diputar 24° supaya muat; hasilnya bilah terbaca tetapi lengan jadi terlihat lebih menjulur dibanding idle.
8. **Tidak ada GIF.** Pose statis tidak membuktikan animasi akan terbaca; semua animasi (12 frame per state, durasi, keyframe) belum dikerjakan di rig baru.
9. **Poin v1 yang terbawa:** hash `sha256-hero.txt` dan V11 masih mengacu v1. Saat v2 dipindah ke 8 state, V11 (terutama pemeriksaan "4.4 kepala naga") perlu ditulis ulang untuk desain baru.

## 10. Keputusan yang saya butuhkan darimu

1. Apakah **bentuk badan dan proporsi** di `kunci-3-pose.png` dan `peta-bagian.png` mendekati yang kamu mau? Kalau tidak, bagian mana yang diubah (nomor di bagian 5.1).
2. Apakah **wajah dan telinga tetap terlihat** (asumsi 2) benar, atau helm harus menutup lebih banyak?
3. Karena besi hitam hilang di latar gelap: pakai **halo** di preview saja, atau tambah **garis tepi terang tipis** pada aset (menambah warna, mengubah tampilan)?
4. Apakah **ekor kipas panah** dipertahankan, dikecilkan, atau dihapus?
5. Apakah Fase Armor boleh mulai dari **pita merah + pedang api** sesuai referensi 2 di atas badan ini, atau ada bagian badan yang kamu ubah dulu?

## 11. Daftar berkas baru di fase ini

```
pack/reports/hero2-body.md
pack/reports/hero2-body/bandingan-v1-v2.png
pack/reports/hero2-body/detail-attack-smash-8x.png
pack/reports/hero2-body/detail-idle-8x.png
pack/reports/hero2-body/detail-run-8x.png
pack/reports/hero2-body/helm-12x.png
pack/reports/hero2-body/kunci-3-pose.png
pack/reports/hero2-body/peta-bagian.png
pack/reports/hero2-body/siluet.png
pack/reports/hero2-body/ukuran.json
src/hero2.py
src/test_hero2.py
tools/hero2_body.py
```

Menunggu persetujuan gaya untuk Berserker Hero.
