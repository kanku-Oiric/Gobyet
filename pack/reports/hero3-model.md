# Berserker Hero v3: rombak total tanpa basis Gobyet (model, zirah, pedang), laporan STOP

Branch `claude/gobyet-hero`. Tidak di-merge, `main` tidak disentuh, tidak ada force-push, repo Bertahan-Bukan-hidup tidak disentuh. Format mengikuti bagian 8 brief awal ("LAPORAN (tiap STOP)").

**Yang dikerjakan:** model karakter baru dari awal dalam tiga pose kunci statis (`idle`, `run` puncak, `attack-smash` saat tumbukan), kode rig baru, tes, dan bukti gambar. Karena kamu mengirim permintaan yang sama dan minta dirombak dari awal, fase Body dan fase Armor yang sebelumnya direncanakan terpisah saya gabung: badan, helm, zirah, dan pedang agung sekarang ada di satu lembar bukti. **Belum ada GIF, sheet, manifest, atau hash baru.** v2 (Gobyet berzirah) kamu tolak; kodenya masih ada di repo hanya untuk perbandingan.

**Tidak diklaim:** gaya bagus, mirip, atau disetujui. Itu keputusanmu. Hal yang tidak terbukti ditulis "tidak terbukti".

## 1. Ringkasan

| Hal | Hasil |
|---|---|
| Basis | **Bukan Gobyet.** Tidak ada kepala, wajah, telinga, bulu, mata, hidung, atau mulut Gobyet. Karakter ini prajurit mesin berhelm penuh. Diuji otomatis (bagian 6.1). |
| Model badan | Dari referensi 1: kepala + jambul sangat besar, pelindung bahu raksasa bersirip tanduk dengan panel "wajah" mesin, pelindung bahu bulat di sisi senjata, perut sisik heksagonal, kaki pendek bersepatu besar, ekor kipas panah. |
| Kepala | Dari referensi 1 dipertahankan (jambul menyapu ke belakang, pita V di atas wajah, kubah bertapak plat, sayap di sisi), tetapi coraknya dari referensi 2: besi hitam, garis merah darah, **salib merah menyala di visor**. Mata = lengan datar salib. |
| Zirah | Dari referensi 2: pelat hitam berbingkai garis merah tipis, garis V di dada, strip cahaya merah, jambul merah gelap seperti plume. |
| Senjata | Dari referensi 2: pedang agung hitam lebar (19 px) dengan tepi api merah bergelombang di kedua sisi dan inti hitam, pelindung, gagang bergaris merah. Bukan pengganti lagi. |
| Kesan "modern" | Strip cahaya tipis, panel rapi, baut, ventilasi, lampu indikator; garis bersih, bukan paku semua. Kesan mekanis tetap (cakram telinga, panel wajah mesin, cincin inti). |
| Palet | 11 kunci baru (`n0..n4` besi hitam, `q0..q4` merah darah, `wh` inti cahaya); 22 di pose smash karena efek balok kayu memakai kunci HERO_PAL v1. Batas 28. |
| Tes | `src/test_hero3.py`: 9 OK. `src/test_hero2.py`: 8 OK (tidak diubah). Lihat bagian 6. |

## 2. Spesifikasi yang saya ambil dari tiap referensi

Referensi tidak disimpan di repo; saya mengukur dan menurunkan bentuk (tanpa menjiplak piksel, tanpa salin 1:1 karakter berlisensi). Potongan perbesaran untuk analisis ada di folder kerja sementara, bukan di repo.

**Referensi 1 (`261…jpg`): bentuk badan dan kepala.** Setelah melihat ulang perbesarannya, hal yang saya perbaiki dari pembacaan sebelumnya: kepalanya bukan wajah manusia atau monyet; ini helm bertopeng (pelat abu bergaris putih di dahi, pita V emas, moncong biru-abu, bawahnya wajah tengkorak-mesin gelap). Badan hampir seluruhnya tertutup kepala dan dua pelindung bahu; perut sisik, sepatu kecil bercakar.

| Ciri di referensi | Saya terjemahkan menjadi | No. |
|---|---|---|
| Kepala + jambul sangat besar, hampir tanpa leher | Helm 34 px lebar, jambul 22 px di atasnya; kepala + jambul 60% tinggi tubuh (bagian 6.2) | 1-7 |
| Pelat dahi bergaris putih, pita V emas | Plat sensor di kubah dengan urat merah; pita V merah menyala | 2, 3 |
| Pelindung bahu raksasa abu dengan sirip tanduk, panel kecil seperti wajah (dua kotak), batu bundar, cakar bawah | Cangkang 27 px, dua sirip tanduk tinggi, panel wajah mesin dengan dua jendela mata merah, cincin berinti merah, tiga cakar merah | 8-11 |
| Pelindung bahu bulat di sisi senjata, kepalan besar | Cakram berlapis cincin, kepalan baja besar bermanset merah | 12, 19 |
| Perut sisik heksagonal | Panel sisik merah darah di bawah dada | 14 |
| Sepatu pendek bercakar | Sepatu besar dengan penutup ujung dan bibir merah | 17 |
| Ekor kipas panah melengkung, gradien | Dua busur panah merah menyala (terang ke gelap), mengelilingi belakang bahu | 18 |

**Referensi 2 (`4a36c…jpg`): zirah, palet, senjata, corak kepala.**

| Ciri | Saya terjemahkan menjadi |
|---|---|
| Helm hitam rata dengan salib merah menyala | Visor gelap dengan salib merah: batang tegak dan lengan datar sebagai mata |
| Plume api merah gelap bergerigi | Jambul bilah merah gelap (tiga nada), ujung runcing |
| Pelat hitam dengan garis tepi merah | Semua pelat besi hitam dengan bingkai merah 1 px dan garis V merah di dada |
| Pedang hitam raksasa, inti hitam, tepi api merah menyala | Bilah 19 px, inti hitam bergelombang, api merah di kedua sisi, kilatan api menjulur di tepi |
| Pelindung bahu abu tipis | Dua pelindung bahu hitam dengan cincin berinti merah |

## 3. Asumsi (salah satu bisa keliru; mohon koreksi)

1. **"Basis bukan Gobyet" = karakter ini bukan Gobyet sama sekali.** Saya hapus kepala, wajah, telinga, dan bulu Gobyet; bukan hanya wajahnya ditutup helm. Akibatnya ini bukan lagi "kostum Gobyet" seperti 33 kostum lain di pack (bagian 8).
2. **Emote dibawa visor, bukan wajah.** Kamu sebelumnya bilang emote bagus; wajah Gobyet sudah tidak ada, jadi ekspresi sekarang: lengan salib (datar, miring marah, tebal kaget, redup lelah, garis tipis tutup mata, silang kalah), alis V yang selalu terlihat, dan grill mulut (tertutup atau terbuka bercahaya saat berteriak). Durasi dan timing animasi v1 yang kamu setujui tetap dipakai saat porting; bentuk ekspresinya yang berganti (bagian 5.2).
3. **"Red blood" = warna dan corak saja.** Aturan keras nomor 4 tetap: tidak ada darah, luka, atau kematian brutal; efek serangan hanya mengenai lantai atau balok kayu.
4. **Hitam + merah boleh.** Brief awal melarang palet itu untuk v1; saya baca "pakai referensi 2" sebagai pencabutan larangan.
5. **Pedang sudah desain penuh**, bukan pengganti, karena fase Armor digabung.
6. **Kanvas tetap 128×96, GIF skala 4** (belum diekspor).
7. **Menghadap kanan**, dengan pelindung bahu raksasa di kiri layar seperti referensi 1; senjata di kanan.

## 4. Tabel aset

Fase ini tidak mengekspor aset. Yang ada hanya tiga pose kunci statis (PNG, bukan bagian pack):

| Pose | State tujuan | Frame | Durasi | Tinggi × lebar badan (tanpa ekor dan pedang) | Kotak semua piksel (x0, y0, x1, y1) dengan efek | Warna |
|---|---|---:|---|---|---|---:|
| idle | `idle` (frame 0) | 1 (statis) | tidak berlaku | 87 × 78 | 4, 3, 110, 89 | 11 |
| run | `run` (puncak langkah) | 1 (statis) | tidak berlaku | 85 × 79 | 3, 1, 123, 85 | 11 |
| attack-smash | `attack-smash` (tumbukan) | 1 (statis) | tidak berlaku | 81 × 74 | 3, 9, 126, 89 | 22 (efek balok kayu v1) |

Keyframe tiap pose ada di `src/hero3.py` (`pose_idle`, `pose_run_peak`, `pose_smash_hit`): idle menancapkan pedang di sisi kanan; run melayang dengan pedang diacungkan ke depan-atas; smash menancapkan ujung bilah di sisi atas balok kayu 11 px dengan busur sapuan dan percikan.

## 5. Bukti visual

Semua gambar di `pack/reports/hero3-model/`.

| Berkas | Isi |
|---|---|
| `kunci-3-pose.png` | tiga pose di latar terang, gelap, dan abu tengah (4×) |
| `peta-bagian.png` | pose idle dengan 20 bagian bernomor (legenda di 5.1) |
| `kepala-12x.png` | kepala 12× latar terang dan gelap |
| `emosi-visor.png` | sembilan ekspresi visor (5.2) |
| `siluet.png` | siluet hitam tiga pose di dua latar |
| `bandingan-v2-v3.png` | v2 (ditolak) di samping v3 |
| `detail-idle-8x.png`, `detail-run-8x.png`, `detail-attack-smash-8x.png` | tiap pose 8× |
| `ukuran.json` | semua angka laporan (kotak, proporsi, piksel per bagian, palet, rasio warna, kontras) |

### 5.1 Legenda bagian (piksel terlihat di pose idle)

| No | Bagian | Piksel |
|---:|---|---:|
| 1 | jambul merah darah | 412 |
| 2 | kubah helm + plat sensor | 315 |
| 3 | alis V merah menyala | 59 |
| 4 | visor salib | 400 |
| 5 | grill mulut | 30 |
| 6 | sayap helm | 86 |
| 7 | cakram telinga mekanis + ventilasi pipi | 132 |
| 8 | pelindung bahu raksasa | 419 |
| 9 | sirip tanduk bahu | 284 |
| 10 | panel wajah mesin | 108 |
| 11 | cincin inti merah + cakar | 180 |
| 12 | pelindung bahu bundar | 111 |
| 13 | dada bergaris merah + gorget | 337 |
| 14 | perut sisik heksagonal | 100 |
| 15 | sabuk + gesper | 40 |
| 16 | pelat pinggul | 84 |
| 17 | sepatu, lutut, paha | 321 |
| 18 | ekor kipas panah | 372 |
| 19 | kepalan baja | 176 |
| 20 | pedang agung hitam inti api | 836 |

### 5.2 Ekspresi visor yang sudah ada di rig

`look` (datar, normal), `angry` (ujung luar naik: alis V jadi marah), `rage` (lebih tebal, ditambah mulut terbuka), `wide` (tebal, kaget), `glare`, `dim` dan `tired` (redup, ujung luar turun), `shut` (garis tipis), `x` (kalah). Pemetaan ke state belum dibuat; usulan: idle `look`, run `angry`, rage `rage`, attack `angry` atau `rage`, miss `wide`, exhaustion `tired`, defeated `x`. Ini usulan, bukan keputusan.

## 6. Pengukuran dan validasi (keluaran mentah)

### 6.1 Uji unit

`python3 -W ignore -m unittest src/test_hero3.py src/test_hero2.py`:

```
.................
----------------------------------------------------------------------
Ran 17 tests in 3.776s

OK
```

Sembilan tes hero3: tiga pose ada; kanvas 128×96, tidak ada piksel di baris lantai dan di bawahnya, tidak ada piksel di tepi (y ≥ 1, x antara 1 dan lebar−2); **tidak ada warna kunci bulu, wajah, mata, hidung, mulut Gobyet dan tidak ada bagian bernama face, eye, ear, mouth, brow, skull, neck** (efek balok kayu dikecualikan; semua sembilan ekspresi juga diuji); palet ≤ 28, tepat 11 kunci tanpa efek, semua terdaftar di `PAL_HERO`; tidak ada alfa parsial; pelindung bahu raksasa selalu di kiri tengah badan, pelindung bulat di kanan, ekor di kiri; salib visor ada (lebar ≥ 15, tinggi ≥ 11) dan setiap ekspresi tampil berbeda; pedang berinti hitam dan tepi api merah (≥ 300 piksel, merah > 80, hitam > 60); tiga hash piksel pose kunci hero v1 tidak berubah (`idle 11974b75`, `run 08796a4b`, `attack-smash 76ba21ad`). Delapan tes hero2 tidak diubah dan tetap lulus.

### 6.2 Proporsi dan ukuran (dari `ukuran.json`)

| Pose | Kepala + jambul | Dagu ke sabuk | Sabuk ke lantai | Lebar helm | Lebar bahu raksasa | Lebar bilah |
|---|---:|---:|---:|---:|---:|---:|
| idle | 59,8% | 23,0% | 17,2% | 34 | 27 | 19 |
| run | 61,2% | 22,4% | 16,5% | 34 | 28 | 19 |
| attack-smash | 64,2% | 24,7% | 11,1% (jongkok) | 34 | 28 | 19 |

Ukur ulang referensi 1 di perbesaran: kepala (jambul sampai dagu/moncong) kira-kira 60-70% tinggi karakter; ini pembacaan mata atas gambar kecil yang di-JPEG, bukan angka pasti.

Rasio piksel digambar (idle): merah (`q0`-`q4`) 37,9%, besi hitam (`n0`-`n4`) 62,0%, lain 0,1%.

### 6.3 Kontras tepi (WCAG, rasio; laporan, bukan lulus/gagal)

| Kunci | Latar terang | Latar gelap | Abu tengah | Dengan halo krem |
|---|---:|---:|---:|---:|
| `n0` garis tepi hitam | 18,17 | **1,15** | 4,92 | 14,05 |
| `n1` | 16,08 | 1,02 | 4,36 | 12,43 |
| `n2` | 12,80 | 1,24 | 3,47 | 9,89 |
| `n3` | 7,81 | 2,02 | 2,12 | 6,04 |
| `n4` | 3,59 | 4,40 | 1,03 | 2,78 |
| `q1` merah gelap | 11,92 | 1,33 | 3,23 | 9,21 |
| `q2` | 7,19 | 2,20 | 1,95 | 5,55 |
| `q3` | 4,44 | 3,56 | 1,20 | 3,43 |
| `q4` merah menyala | 2,55 | 6,21 | 1,45 | 1,97 |

Besi hitam hampir tak terlihat di latar gelap tanpa halo (1,02-1,24); karakter terbaca di sana lewat garis merah, visor, dan pedang. Halo dan latar abu di preview (perbaikan teknis sebelumnya) membantu; aset yang dipakai tanpa halo di latar gelap tidak terbukti terbaca.

### 6.4 Aset lama dan hero v1 tidak berubah

`python3 -W ignore src/validate_pack.py --hero-only` (bagian V1; seluruh keluaran LULUS, exit 0):

```
[V1] Hash aset yang dikunci dan aset yang sudah dibuat
  sha256-asli.txt: 27 identik, 0 berubah/hilang
  sha256-disetujui.txt: 89 identik, 0 berubah/hilang
  sha256-dibuat.txt: 242 identik, 0 berubah/hilang
  sha256-hero.txt: 16 identik, 0 berubah/hilang
...
HASIL (--hero-only; bukan pengganti validasi penuh): LULUS
```

`python3 -W ignore -m unittest src/test_validate_pack.py`: `Ran 44 tests in 162.614s`, `OK`, exit 0.

`git status --short` hanya menunjukkan berkas baru; tidak ada berkas `gif/`, `sheets/`, `pack/manifest.json`, atau `pack/sha256-*.txt` yang berubah. Validasi penuh (`validate_pack.py` tanpa `--hero-only`) tidak dijalankan ulang karena tidak ada aset atau kode pack yang berubah; itu **tidak dibuktikan ulang**.

## 7. Perubahan rig dan pipeline

Semuanya aditif; tidak ada berkas yang sudah ada diubah.

| Berkas | Isi |
|---|---|
| `src/hero3.py` (baru) | `HERO3_PAL`, helm penuh (`helm3`, `visor`, `grill`, `crest`), badan (`chest`, `belly`, `hip_plates`, `pauldron_big`, `pauldron_small`, `gauntlet`, `boot`, `leg`), `tail_fan`, `sword3`, `pose`, `geometry`, `draw_hero`, `render_pose`, tiga pose kunci. Memakai pustaka rig v1 (`PartCanvas`, `solid3`, `poly`, `ik`, `SwordFrame`, efek `fx_*`); tidak memakai `head_hd` atau bagian Gobyet apa pun. |
| `src/test_hero3.py` (baru) | 9 tes (6.1). |
| `tools/hero3_model.py` (baru) | Pembuat bukti gambar dan `ukuran.json`. |
| `pack/reports/hero3-model/`, `hero3-model.md` (baru) | Bukti dan laporan ini. |

`src/hero2.py`, `src/test_hero2.py`, `tools/hero2_body.py`, `pack/reports/hero2-body*` (v2 yang kamu tolak) tidak diubah dan hanya dipakai untuk gambar perbandingan; bisa saya hapus sekalian saat porting bila kamu setuju.

**Belum ada, dan akan berubah kalau v3 disetujui:** `COSTUMES` / `APPLIES` / gerbang K, ekspor ke 8 state, validator V11 (spesifikasinya mengunci wajah, telinga, kepala Gobyet, dan angka 4.4 helm tengkorak naga; semua itu harus ditulis ulang untuk desain ini), resolver dan preview, `sha256-hero.txt` (16 hash akan berubah; hanya dengan persetujuanmu).

## 8. Konsekuensi "bukan Gobyet" untuk pack (butuh keputusanmu)

Pack ini berisi kostum yang dipakai Gobyet. v3 bukan Gobyet, jadi ada tiga cara menaruhnya:

| Opsi | Arti | Risiko |
|---|---|---|
| A. Tetap sebagai satu "kostum" bernama `berserker-hero` | Slot sel tidak berubah (8 state), resolver tetap sama; tetapi namanya menyesatkan karena tidak ada Gobyet di dalamnya | Kecil di kode; V11 harus ditulis ulang |
| B. Karakter terpisah dengan grup sendiri | Manifest ada kategori baru; resolver dan preview perlu mengenalinya | Perubahan skema; lebih besar |
| C. Tetap kostum Gobyet tapi dengan helm penuh yang menutup seluruh kepala | Tidak sesuai arahanmu "jangan pakai Gobyet" | Bertentangan dengan permintaan |

Rekomendasi saya A untuk sekarang (paling sedikit perubahan, menunggu gaya disetujui dulu), tetapi itu keputusanmu.

## 9. Tebakan dan ketidakpastian

- **Kemiripan dengan gambar di kepalamu tidak terbukti.** Bentuk saya turunkan dari dua gambar kecil ber-JPEG; bagian yang paling mungkin meleset: bentuk helm (referensi 1 bertopeng dengan moncong dan pita emas, saya buat topeng gelap tanpa moncong), pelat dahi, ekor, dan jumlah/bentuk bilah jambul.
- **Wajah-tengkorak di referensi 1** (bagian bawah kepala) tidak saya salin; saya ganti jadi grill mulut dan pelat pipi. Apakah kamu mau wajah itu muncul tidak diketahui.
- **Pembacaan ekspresi hanya dari visor.** Tidak diuji pada orang lain; saya tidak membuktikan bahwa sembilan ekspresi cukup untuk menggantikan wajah Gobyet v1. Bagian "marah" bergantung pada alis V yang selalu terlihat.
- **Ukuran kecil.** Tidak diuji di skala 1 (128×96 sebenarnya); gambar bukti diperbesar. Garis merah 1 px, jahitan pelat pipi, dan sisik heksagonal kemungkinan hilang di ukuran kecil.
- **Merah vs hitam.** 38% merah menurut hitungan piksel; rasio yang kamu mau tidak diketahui.
- **"Modern".** Tafsir saya: strip cahaya, panel, lampu indikator. Ukuran "sedikit" tidak terbukti.
- **Kepatuhan hak cipta.** Saya tidak menyalin piksel; bentuk, proporsi, dan susunan bagian mengikuti referensi yang kamu berikan. Tingkat kemiripan yang aman untuk proyekmu adalah keputusanmu; saya tidak menilai itu.

## 10. Kelemahan yang kamu lihat sendiri

1. **Helm terlalu mirip blok hitam polos.** Pelat wajah gelap luas dengan sedikit detail; terbaca lewat salib dan alis V, tapi kurang "wajah" dibanding referensi 1.
2. **Latar gelap.** Besi hitam menyatu dengan latar `#181c2c` (6.3); tubuh hampir hilang tanpa halo.
3. **Run: kaki kurang jelas.** Satu kaki terangkat menekuk di bawah perut dan satu terlempar ke belakang; pelindung bahu raksasa memakan banyak ruang sehingga siklus kaki harus diatur hati-hati saat dianimasikan. Lengan kanan yang memegang pedang tipis dan hanya terlihat sebagai batang kecil di bawah pelindung bahu bulat.
4. **Pelindung bahu raksasa dan ekor berdempetan di kiri.** Ekor hanya terlihat sebagian di balik sirip dan dipaksa muat kanvas (jari-jari diperkecil di run dan smash); di referensi 1 ekor jauh lebih besar dan terpisah.
5. **Lengan tipis dan jangkauan pendek (16,1 px).** Hanya satu tangan memegang pedang; tangan lain tidak terlihat (tersembunyi di balik pelindung bahu); genggaman dua tangan tidak dipakai.
6. **Ekor panah tanpa garis tepi**, sehingga sedikit bergerigi di sisi terang; tepinya tidak sebersih bagian lain.
7. **Efek balok kayu masih memakai warna bulu Gobyet** (`fb`, `fl`, `fs`, dan krem-perunggu v1) karena efek `fx_*` dipakai ulang; tes "bukan Gobyet" mengecualikan efek. Warna ini bukan bagian karakter tetapi menambah palet smash jadi 22.
8. **Tidak ada GIF.** Pose statis tidak membuktikan animasi akan terbaca; 8 state × 10-14 frame belum dikerjakan di rig baru.

## 11. Keputusan yang saya butuhkan darimu

1. Apakah **bentuk umum v3** (helm hitam salib merah, pelindung bahu raksasa bermuka mesin, pedang agung inti api, ekor panah) sudah mendekati yang kamu mau? Kalau tidak, bagian mana yang diubah (nomor di 5.1).
2. **Wajah referensi 1** (topeng bermoncong, pita emas, wajah tengkorak-mesin): dipakai atau tetap helm salib gelap seperti sekarang?
3. **Penempatan di pack** (bagian 8): A, B, atau C?
4. **Latar gelap:** pakai halo di preview saja, atau tambah garis tepi terang tipis pada aset (menambah warna)?
5. **Ekor panah:** dibesarkan dengan cara menggeser badan/pedang (mengubah komposisi), dipertahankan seperti sekarang, atau diperkecil?
6. **Emote:** pemetaan ekspresi ke state di 5.2 boleh dipakai?

## 12. Daftar berkas baru di fase ini

```
pack/reports/hero3-model.md
pack/reports/hero3-model/bandingan-v2-v3.png
pack/reports/hero3-model/detail-attack-smash-8x.png
pack/reports/hero3-model/detail-idle-8x.png
pack/reports/hero3-model/detail-run-8x.png
pack/reports/hero3-model/emosi-visor.png
pack/reports/hero3-model/kepala-12x.png
pack/reports/hero3-model/kunci-3-pose.png
pack/reports/hero3-model/peta-bagian.png
pack/reports/hero3-model/siluet.png
pack/reports/hero3-model/ukuran.json
src/hero3.py
src/test_hero3.py
tools/hero3_model.py
```

Menunggu persetujuan gaya untuk Berserker Hero.
