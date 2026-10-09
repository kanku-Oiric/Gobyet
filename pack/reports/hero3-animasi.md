# Berserker Hero v3: animasi sembilan state (delapan state + `victory` baru), laporan STOP

Branch `claude/gobyet-hero`. Tidak di-merge, `main` tidak disentuh, tidak ada force-push, repo Bertahan-Bukan-hidup tidak disentuh. Format mengikuti bagian 8 brief awal ("LAPORAN (tiap STOP)").

**Dikerjakan:** delapan state hero v3 dianimasikan ulang di atas rig baru (timing dan urutan beat v1 yang pernah kamu lihat dipertahankan), ditambah **satu state baru `victory`** sesuai permintaanmu: topeng membuka dan menutup, pedang ditusukkan ke tanah, satu kaki naik ke batu sambil tangan mengusap cairan monster dari pedang. Aset hero di `gif/`, `sheets/`, `pack/manifest.json`, dan `pack/sha256-hero.txt` diganti total (v1 dan v2 sudah kamu tolak; aset kelas lain tidak berubah, bagian 6).

**Tidak diklaim:** gaya bagus atau disetujui; itu keputusanmu. Hal yang tidak terbukti ditulis "tidak terbukti". **Saya tidak menonton GIF sebagai gerak**: gerak diperiksa lewat lembar frame, pengukuran piksel, validator, dan uji Chromium; kehalusan gerak sebenarnya tidak terbukti oleh saya.

Saya membaca "Lanjut ke Fase animasi" sebagai persetujuan model v3 untuk lanjut, tetapi enam keputusan di laporan model (bagian 11 `hero3-model.md`) belum kamu jawab; saya memakai rekomendasi saya yang paling kecil perubahannya dan menandainya di bagian 8.

## 1. Ringkasan

| Hal | Hasil |
|---|---|
| State | 9 sel hero, semuanya "wajib": `idle` 12, `run` 12, `rage` 12 (tidak loop), `attack-leap` 14, `attack-smash` 12, `miss` 10, `exhaustion` 12, `defeated` 14, **`victory` 16 (tidak loop)**. Jumlah frame dan pola durasi delapan state lama sama dengan v1. |
| `victory` | Memakai state global `victory` yang sudah ada di manifest untuk 32 kostum lain, jadi arena kelak memakai nama state yang sama. Tidak berputar; frame terakhir ditahan 1500 ms seperti `rage`. |
| Topeng | Pelat wajah terbelah dua di sumbu helm, tiap pintu meluncur ke samping 0-8 px masuk ke sisi helm, membuka rongga mesin (tungku merah gelap, dua lensa menyala, celah hidung, gigi baja). Bukan wajah Gobyet atau manusia. |
| Cairan monster | Hijau asam, bukan merah, supaya terbaca di atas api merah bilah. Hanya ada di `victory` (V11 menolaknya di state lain). |
| Ukuran | GIF terbesar (`victory`) 200.253 B dari batas 204.800 B; total GIF + sheet 1.563.050 B dari batas 1.572.864 B: **sisa hanya 9,8 KB (0,6%)**. Untuk muat, detail dikurangi (bagian 8). |
| Validasi | `validate_pack.py` penuh: **LULUS**. 49 + 21 uji Python OK, 25 uji Node OK, e2e Chromium LULUS, uji GIF-sekali Chromium LULUS. |
| Aset lain | Ekspor penuh ulang: hanya 18 berkas hero yang berbeda (bagian 6). |

## 2. Tabel aset

| State | Frame | Loop | Total ms | Kunci | GIF (B) | Sheet (B) | Langkah maks (piksel) | Seam (piksel) |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| `idle` | 12 | ya | 1950 | f0 | 157.110 | 13.623 | 2457 | 402 |
| `run` | 12 | ya | 880 | f10 | 157.639 | 17.122 | 4482 | 4009 |
| `rage` | 12 | **tidak** | 2760 | f6 | 144.120 | 25.074 | 5477 | - |
| `attack-leap` | 14 | ya | 1470 | f8 | 173.181 | 30.401 | 5028 | 3203 |
| `attack-smash` | 12 | ya | 1350 | f7 | 149.148 | 24.756 | 4806 | 39 |
| `miss` | 10 | ya | 1400 | f6 | 121.038 | 22.301 | 4453 | 2369 |
| `exhaustion` | 12 | ya | 2130 | f5 | 134.707 | 11.619 | 2558 | 370 |
| `defeated` | 14 | ya | 2640 | f3 | 140.833 | 11.157 | 2051 | 122 |
| **`victory`** | 16 | **tidak** | 3510 | f13 | 200.253 | 28.968 | 5093 | - |
| Jumlah | 116 | | | | 1.378.029 | 185.021 | | |

Durasi per frame (ms): idle 240/140/140/160/160/200/180/160/90/140/160/180; run 70/80/70/60/100/60/70/80/70/60/100/60; rage 200/140/140/180/70/90/110/70/70/70/120/**1500**; attack-leap 140/130/60/60/120/50/40/40/260/130/110/100/100/130; attack-smash 120/100/120/180/50/40/40/240/120/100/100/140; miss 140/100/130/50/40/200/220/240/140/140; exhaustion 200/150/150/170/220/260/220/150/90/150/170/200; defeated 200/180/180/200/200/220/200/160/120/180/200/200/200/200; victory 160/100/100/300/100/140/100/70/60/200/140/160/120/120/140/**1500**.

Isi tiap state: `idle` napas satu piksel, jambul bergoyang, ekor melambai, visor berkedip dan meredup sebentar; `run` miring ke depan dengan pedang diacungkan ke depan-atas, debu tiap injakan, garis kecepatan; `rage` mengumpulkan amarah (merunduk, visor redup lalu menyipit), meledak (merah badan naik satu tingkat, jambul dan ekor mengembang, pedang diacungkan, visor putih-merah, bara, garis kejut), lalu menahan pose; `attack-leap` jongkok, melompat (kaki ditekuk), tebas turun dengan smear, mendarat dan menghantam balok kayu; `attack-smash` antisipasi, pedang diangkat tinggi, ayunan dengan smear, tumbukan ditahan 240 ms; `miss` ayunan penuh tenaga, pedang menancap lantai di depan balok, goyah, malu; `exhaustion` bungkuk bertumpu pada pedang, uap napas, keringat; `defeated` berlutut rendah bertumpu pada pedang, kepala tertunduk, visor dan api bilah meredup (tanpa kekerasan).

## 3. Urutan `victory` (permintaanmu), frame demi frame

| Frame | ms | Isi | Terukur |
|---:|---:|---|---|
| f0 | 160 | berdiri, pedang berlumur cairan monster hijau tertancap di sisi kanan, batu di depan kaki | rongga 0, noda 226 px |
| f1 | 100 | topeng mulai terbelah, celah bercahaya | rongga 100 px |
| f2 | 100 | pintu topeng bergeser, uap keluar | rongga 206 px |
| f3 | 300 | **topeng terbuka penuh**: dua lensa menyala, gigi baja | rongga 308 px |
| f4 | 100 | menutup separuh, kepala menoleh ke pedang | rongga 170 px |
| f5 | 140 | **topeng tertutup**, percikan klik di tengah pelat, visor melebar | rongga 0 |
| f6 | 100 | pedang dicabut dari tanah | ujung bilah tidak lagi di baris tanah (y 82) |
| f7 | 70 | pedang diangkat tinggi di kanan | puncak bilah y 5 |
| f8 | 60 | menukik dengan sapuan terang | sudut 70° |
| f9 | 200 | **pedang menancap ke tanah**, debu, serpihan, tetesan terlempar, visor `rage` | ujung di baris tanah, sudut 88°, debu ada |
| f10 | 140 | tangan dilepas, lutut mulai terangkat | noda 223 px |
| f11 | 160 | **kaki naik ke batu**, tangan turun ke bilah | sepatu menapak batu 17 px |
| f12 | 120 | **mengusap** 1: olesan hijau terdorong di depan kepalan | noda 195 px |
| f13 | 120 | mengusap 2: noda menyusut, tetesan jatuh | noda 97 px (kunci) |
| f14 | 140 | mengusap 3: hampir bersih, bilah berkilau mulai | noda 55 px, kilau |
| f15 | 1500 | bilah bersih, kaki di batu, kilau, tangan di gagang; ditahan | noda 0, sepatu di batu 21 px |

Semua baris "Terukur" diperiksa V11 (bagian 4) dari piksel, bukan dari niat tabel pose.

## 4. Validasi (keluaran mentah)

### 4.1 Validator penuh

`python3 -W ignore src/validate_pack.py` (exit 0). Bagian yang relevan:

```
[V1] Hash aset yang dikunci dan aset yang sudah dibuat
  sha256-asli.txt: 27 identik, 0 berubah/hilang
  sha256-disetujui.txt: 89 identik, 0 berubah/hilang
  sha256-dibuat.txt: 242 identik, 0 berubah/hilang
  sha256-hero.txt: 18 identik, 0 berubah/hilang

[V2] Manifest dan schema, [V3] palet, kanvas, alfa, isi GIF
  33 kostum, 19 state, 172 sel berlaku, 172 sel terisi; 0 gagal

  berserker-hero/idle        baru       2457    328  3071.2    402     1.23  lulus
  berserker-hero/run         baru       4482   3858  5602.5   4009     1.04  lulus
  berserker-hero/rage        baru     tidak loop (loop=false), seam tidak berlaku
  berserker-hero/attack-leap baru       5028   4562  6285.0   3203     0.70  lulus
  berserker-hero/attack-smash baru       4806   3832  6007.5     39     0.01  lulus
  berserker-hero/miss        baru       4453   4187  5566.2   2369     0.57  lulus
  berserker-hero/exhaustion  baru       2558   2412  3197.5    370     0.15  lulus
  berserker-hero/defeated    baru       2051    106  2563.8    122     1.15  lulus
  berserker-hero/victory     baru     tidak loop (loop=false), seam tidak berlaku

[V11] Berserker Hero (kanvas 128x96, GIF x4, bukan Gobyet) ...
  idle .. defeated  : lulus (rincian per state di keluaran validator; kunci, sisi, kepala, seam)
  victory          16 tidak 128x96     4 13    195.6     lulus
      urutan: topeng buka f1, puncak f3, tutup f4 (rongga puncak 308 px); pedang terangkat f7, menusuk f9; kaki di batu f[11, 12, 13, 14, 15]; noda 226 -> 0 px, sebagian f[12, 13, 14]
  warna seluruh karakter: 20 (batas 28); di luar palet yang diizinkan: 0
  PERINGATAN: garis tepi besi hitam terhadap latar gelap hanya 1.15:1 tanpa halo; dengan halo 14.05:1
  V11: lulus

  gerbang K:  9 aset, GIF terbesar 200253 byte, total file  1563050 byte
  hero: 9 aset, GIF terbesar 200253 byte (batas 204800), total GIF + sheet 1563050 byte (batas 1572864)
  sel berlaku 172, terisi 172, tersisa 0
  proyeksi pertambahan total: 12770440 byte (12.18 MB); ambang peringatan 15 MB, batas keras 16 MB

HASIL: LULUS
```

Keluaran lengkap (semua state, kontras empat latar, sisi per state) tersimpan di sesi ini dan dapat dibangkitkan ulang dengan perintah di atas; ringkasan angka per state ada di bagian 2 dan `pack/reports/hero3-animasi/ukuran.json`.

V11 ditulis ulang untuk v3 (pemeriksaan wajah/telinga Gobyet dan angka keterbacaan helm naga dibuang karena tidak berlaku): spesifikasi 9 state, aset = kode, **bukan Gobyet**, tidak ada piksel di tepi kanvas, cairan monster hanya di `victory`, mata terlihat di tiap frame, sisi pelindung bahu raksasa/bundar/jambul/ekor, tinggi kepala, seam, IoU `run`, aturan serangan, aturan `rage`, urutan `victory`, keterbacaan frame kunci, warna, kontras. Batas keterbacaan adalah **usulan saya** dari pengukuran sembilan frame kunci (±70-80% dari nilai terendah), bukan angka dari brief.

### 4.2 Uji unit, resolver, browser

```
python3 -W ignore -m unittest src/test_validate_pack.py        Ran 49 tests ... OK
python3 -W ignore -m unittest src/test_hero3.py src/test_hero2.py   Ran 21 tests ... OK
node --test pack/resolver.test.js                               tests 25, pass 25, fail 0
node tools/e2e_preview.js <folder>                              E2E: LULUS (172/172 sel berlaku terisi; lembar kontak 9 state; Putar ulang rage dan victory)
node tools/gif_once_check.js <folder>                           GIF-SEKALI: LULUS (rage dan victory berhenti di frame terakhir di Chromium 141; kontrol run tetap bergerak)
```

Uji baru untuk `victory` (`HeroVictorySequence`) merusak urutan dan harus ditolak: topeng tidak pernah terbuka, topeng terus terbuka, noda tidak hilang, noda hilang sekaligus, kaki tidak mencapai batu, batu hilang, pedang tidak pernah ditusukkan. Uji rig baru: wajah tertutup simetris tepat terhadap sumbu helm, topeng membuka monoton tanpa warna Gobyet, noda terhapus bertahap, kaki tidak pernah lepas dari pinggul.

Firefox dan Safari tidak diuji (hanya Chromium tersedia).

## 5. Bukti visual

Semua di `pack/reports/hero3-animasi/` (dibuat `python3 tools/hero3_animasi.py`):

| Berkas | Isi |
|---|---|
| `<state>-lembar.png` (9 berkas) | semua frame state itu berurutan, 3×, bernomor dengan durasi; frame kunci ditandai |
| `kunci-9-state.png` | frame kunci sembilan state di latar terang, gelap, dan abu tengah |
| `victory-topeng.png` | kepala di frame topeng membuka dan menutup, 8× |
| `victory-usapan.png` | bilah dan kepalan di frame kaki-di-batu: noda menyusut sampai bersih, 6× |
| `ukuran.json` | frame, durasi, ukuran, seam, keterbacaan, dan deret ukuran `victory` per frame |

## 6. Bukti aset lama tidak berubah

- `validate_pack.py` V1: 27 + 89 + 242 berkas terkunci identik, 0 berubah.
- Ekspor penuh dari kode (`python3 src/export.py`, semua animasi) lalu `git status`: **tidak ada** berkas `gif/` atau `sheets/` selain hero yang berubah; berkas hero yang berbeda dari commit sebelumnya 16 berubah + 2 baru (`victory`). `python3 tools/hero_hashes.py --check`: 18 berkas sama dengan `pack/sha256-hero.txt`.
- `pack/manifest.json`: satu-satunya perbedaan struktur adalah (a) sel `berserker-hero` (durasi, kunci, `victory` baru), (b) `applies` hero bertambah `victory`, (c) entri state global `victory` kehilangan daftar `costumes` karena kini berlaku untuk semua 33 kostum. Sel kostum lain identik.
- Tiga berkas kunci lama (`sha256-asli.txt`, `-disetujui.txt`, `-dibuat.txt`) tidak disentuh. `sha256-hero.txt` ditulis ulang karena seluruh aset hero berganti dari v1 ke v3 (18 berkas); saya menganggap itu termasuk permintaan "lanjut ke fase animasi".

## 7. Perubahan rig dan pipeline

| Berkas | Perubahan |
|---|---|
| `src/hero3.py` | tambahan: pintu topeng dan rongga mesin (`mask`), noda cairan monster di bilah (`stain_u`), `heat` (merah badan naik tingkat), `flare` (jambul mengembang), properti `props`, jangkauan kaki dijepit ke pinggul, jambul tidak keluar dari tepi atas, simetri helm diperbaiki (batas kolom hx-1 | hx), ekor dihitung ulang di sekitar bahu raksasa dan disederhanakan (dua nada, tanpa garis tepi), urat jambul dibuang |
| `src/hero3_fx.py` (baru) | debu, serpihan, ledakan, smear, balok kayu, garis kecepatan, keringat, napas, uap, bara, garis kejut, **batu**, tetesan cairan monster, kilau; semuanya berpalet v3 (kunci `s1..s3`, `w1..w3`, `m1..m3`), tanpa warna bulu atau wajah Gobyet |
| `src/hero3_scenes.py` (baru) | tabel keyframe sembilan state, interpolasi, durasi, efek, penyesuaian ekor per state agar tidak terpotong tepi kiri |
| `src/hero3_check.py` (baru) | pengukuran V11 v3 (identitas, mata, sisi, keterbacaan, urutan `victory`) |
| `src/pack.py` | `victory` wajib untuk hero, frame kunci baru, `NO_LOOP` bertambah `victory` |
| `src/export.py` | memakai `hero3_scenes`; sheet PNG kanvas non-64×48 diekspor dengan `optimize` (piksel identik, hanya hero) |
| `src/validate_pack.py` | V11 ditulis ulang; `HERO_SPEC` 9 state; tahan frame terakhir `victory` 1500 ms |
| `src/test_validate_pack.py`, `src/test_hero3.py` | uji hero diganti ke v3 dan ditambah |
| `pack/resolver.test.js`, `pack/preview.html`, `tools/e2e_preview.js`, `tools/gif_once_check.js` | 9 sel hero; indikator "diputar sekali" dan Putar ulang untuk `rage` dan `victory` |
| `pack/README.md`, `STYLE.md`, `PROGRESS.md` | bagian hero ditulis ulang untuk v3 dan sembilan state |
| `tools/hero3_animasi.py` (baru) | pembuat bukti bagian 5 |

Kode v1/v2 yang ditolak (`src/hero_scenes.py`, `src/hero2.py`, `src/test_hero2.py`, `tools/hero2_body.py`, `tools/hero_phase_*.py`) tidak dihapus dan tidak dipakai pipeline; `src/hero.py` tetap dipakai sebagai pustaka rig. Saya bisa membersihkannya bila kamu setuju.

## 8. Tebakan dan ketidakpastian

- **Isi balik topeng.** Karena basis bukan Gobyet, yang terlihat saat topeng terbuka adalah rongga mesin (lensa merah, gigi baja), bukan wajah. Kamu tidak pernah menyebut wajah apa yang ada di baliknya; ini tebakan saya.
- **Darah monster.** Aturan keras brief awal melarang darah. Permintaanmu eksplisit memintanya di `victory`, jadi saya terapkan hanya di sana, berwarna hijau asam dan bergaya kartun (gumpalan dan olesan, sedikit tetesan, tanpa luka, tanpa tubuh monster). Warna hijau (bukan merah) adalah pilihan saya supaya terbaca di atas api merah dan tidak berkesan sebagai darah manusia. Kalau kamu ingin merah, cukup tiga nilai `m1..m3`.
- **"Kakinya naik batu 1".** Saya baca satu batu yang ada di semua frame `victory` (agar tidak muncul tiba-tiba); satu kaki (kanan layar) naik, kaki lain tetap di tanah.
- **"Mengusap".** Tangan kanan (kepalan baja) menyapu bilah dari pelindung ke bawah; pedang berdiri sendiri karena tertancap. Tangan kiri tidak terlihat (tertutup bahu raksasa), jadi tidak ada kain atau pembersih lain.
- **Posisi pack.** Saya melanjutkan dengan pilihan A dari laporan model (tetap slot kostum `berserker-hero`, base `viking-berserker`) karena itu perubahan terkecil dan kamu tidak memintanya diubah; ini belum kamu putuskan.
- **Pemetaan ekspresi ke state** (usulan di laporan model) dipakai apa adanya: idle `look` (kedip `shut`, `dim`), run `angry`, rage `rage`, serangan `angry`/`rage`, miss `wide` lalu `dim`, exhaustion `tired`, defeated `tired`/`dim`/`shut`.
- **Gerak.** Tidak ada yang menonton GIF sebagai animasi; keterbacaan gerak (terutama `run` dan lompatan) hanya terbukti dari angka dan lembar frame. Perbedaan siluet antar-frame `run` terukur IoU maks 0,83 (batas 0,90).
- **Penampil lain.** Perilaku GIF tanpa loop hanya diuji di Chromium.
- **Batas keterbacaan** di V11 adalah angka usulan saya.

## 9. Kelemahan yang saya lihat sendiri

1. **Anggaran ukuran hampir habis.** `victory` 200.253 B dari 204.800 B dan total 1.563.050 B dari 1.572.864 B. Untuk muat saya membuang urat jambul dan sorot ujung ekor, menyederhanakan panah ekor, dan menghemat PNG sheet. Frame tambahan atau detail baru melewati batas (kamu yang menentukan batas itu; saya tidak mengubahnya).
2. **Lompatan nyaris tidak meninggalkan tanah.** Kepala + jambul sudah ±60% tinggi badan dan kanvas hanya menyisakan ±3 px di atas, jadi `attack-leap` hanya terbaca sebagai lompatan lewat kaki yang ditekuk, debu, dan gerak miring; ketinggian lompat tidak terbukti terbaca.
3. **Ekor panah kecil atau tersembunyi di state serangan.** Pelindung bahu raksasa menahan badan di x ≥ 46 agar tidak terpotong tepi kiri, jadi ekor diputar dan dikecilkan; di `attack-leap` hanya 38 piksel terlihat di frame kunci, di `attack-smash` 75, di `idle` 372. Ekor tampak berubah-ubah antar state.
4. **Noda hanya di bagian atas bilah.** Jangkauan lengan (16 px) tidak sampai ke ujung bilah, jadi noda digambar dekat pelindung (u ≤ 29), bukan di ujung tempat seharusnya paling kotor.
5. **Kepalan sebagian tertutup saat mengusap**, sehingga olesan lebih jelas terlihat daripada tangannya; di f14 kepalan hampir tidak terlihat.
6. **Defeated dan exhaustion mirip** (sama-sama bungkuk bertumpu pada pedang); pembedanya hanya tinggi badan, redupnya visor dan api, dan lutut. Kaki berlutut tidak terbaca jelas karena tertutup pelindung bahu dan sabuk.
7. **Latar gelap.** Garis tepi besi hitam 1,15:1 terhadap latar `#181c2c` tanpa halo (14,05:1 dengan halo); di sana yang terbaca hanya garis merah, visor, dan pedang.
8. **`run`: kaki pendek.** Panjang kaki 10 px membatasi langkah; ayunan terbaca dari badan dan pedang lebih daripada dari kaki.
9. **Tidak ada GIF `victory` untuk dilihat bergerak oleh saya**, dan seam/loop tidak berlaku (tidak berputar), jadi tidak ada uji kehalusan sambungan.

## 10. Keputusan yang saya butuhkan darimu

1. Apakah **rongga mesin di balik topeng** cocok, atau ada wajah/mata yang ingin kamu lihat di baliknya?
2. **Cairan monster hijau** dipertahankan, atau diganti merah (atau warna lain)?
3. **Anggaran 200 KB per GIF / 1,5 MB total hero:** dipertahankan (artinya tidak ada ruang untuk menambah detail atau frame), atau dinaikkan?
4. **Ekor panah di state serangan:** dibiarkan kecil, atau badan digeser ke kanan dengan mengorbankan jangkauan pedang dan balok (mengubah komposisi)?
5. **Pembersihan kode** v1/v2 yang tidak dipakai: dihapus sekarang atau dibiarkan?
6. Dari laporan model, tiga keputusan yang masih terbuka: penempatan di pack (A/B/C), halo atau garis tepi terang untuk latar gelap, dan pemetaan ekspresi.

## 11. Daftar berkas di fase ini

```
gif/berserker-hero-{idle,run,rage,attack-leap,attack-smash,miss,exhaustion,defeated,victory}.gif
sheets/berserker-hero-{idle,run,rage,attack-leap,attack-smash,miss,exhaustion,defeated,victory}.png
pack/manifest.json, pack/sha256-hero.txt, pack/README.md, pack/STYLE.md, pack/PROGRESS.md, pack/preview.html, pack/resolver.test.js
pack/reports/hero3-animasi.md, pack/reports/hero3-animasi/ (13 berkas)
src/hero3.py, src/hero3_fx.py, src/hero3_scenes.py, src/hero3_check.py, src/pack.py, src/export.py, src/validate_pack.py
src/test_hero3.py, src/test_validate_pack.py
tools/hero3_animasi.py, tools/e2e_preview.js, tools/gif_once_check.js
```

Menunggu persetujuan gaya untuk Berserker Hero.
