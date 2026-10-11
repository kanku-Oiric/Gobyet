# Berserker Hero, laporan Fase A dan Fase B (STOP 1)

Branch `claude/gobyet-hero`, dibuat dari `claude/gobyet-fase2`. Tidak ada merge, `main` tidak disentuh, tidak ada force-push.
Repo Bertahan-Bukan-hidup tidak disentuh (bukti di bagian 6).

Status: Fase A selesai, Fase B selesai (hanya tiga pose kunci). Fase C (delapan state) dan Fase D belum dimulai.
Tidak ada frame lain yang dibuat. Gaya belum dinilai pemilik; laporan ini tidak menyatakan gaya bagus atau disetujui.

## 1. Fase A: pra-cek terhadap repo

Brief ditulis untuk sistem **pack v1** (`src/`, `pack/`, kanvas 64×48). Nama berkas dan fungsi diverifikasi; yang berbeda ditulis
di sini dan repo yang diikuti.

| Brief | Di repo | Tindakan |
|---|---|---|
| `pack/sha256-asli.txt`, `-disetujui.txt`, `-dibuat.txt` | ada, 27 / 89 / 242 baris | sesuai |
| `Canvas(w=64, h=48)`, konstanta `W`, `H` | `monkey.Canvas()` tanpa argumen, `W, H = 64, 48` | **diubah aditif**: `Canvas(w=None, h=None)`; `W`, `H` tetap 64, 48 |
| `APPLIES` | `src/pack.py`, 13 state di `STATE_IDS` | sesuai; `run`, `rage`, `attack-leap`, `attack-smash`, `miss`, `exhaustion` belum ada dan ditambah di Fase C |
| field `canvas` opsional per sel | manifest hanya punya `canvas` global dan `gif_scale: 8`. V2, V3, `resolver.test.js`, dan `preview.html` memakai 64×48 dan GIF 512×384 | belum diubah; Fase C |
| GIF skala 4 (512×384) | repo memakai skala 8 untuk 64×48 | hero 128×96 × 4 = 512×384, ukuran GIF sama dengan sel lain |
| kostum `viking-berserker` sebagai `base` | ada, `base: viking`. `resolver.js` hanya satu tingkat `base` | rantai hero: `berserker-hero → viking-berserker → normal` (tidak sampai `viking`) |
| `rage` dengan `loop=false` | V2 gagal bila `loop` bukan `true`; manifest menulis `loop: true` untuk semua sel | validator dan `pack.py` perlu relaksasi aditif di Fase C |
| V1 sampai V4, V10, SEAM-POP | ada (V1–V10, SEAM-POP di V4). V10: batas per GIF baru = GIF terbesar pra-Fase 2 = 171.429 B | brief 200 KB lebih longgar; V10 akan diberi aturan hero 200 KB |
| palet lokal | `export.local_palette` memakai `PAL` + `PAL_EXT`; V3 mengizinkan union keduanya | hero memakai `monkey.PAL_HERO` sendiri (26 warna), V3 diberi pemeriksaan khusus hero |
| `gate` | semua sel baru wajib `gate` (huruf); V2 mengecek nama berkas `<kostum>-<state>` | usul gerbang `K` untuk hero |
| `tools/` | `e2e_preview.js`, `seam_diag.py`, dan lain-lain | sesuai |

Catatan lain: `claude/gobyet-fase2` juga berisi folder `v2/` (rework 64×64, 38 karakter, plus satu karakter `berserker` pedang lempeng
yang dibuat atas brief sebelumnya). Hero ini tidak memakai, mengimpor, atau menyalin satu pun dari `v2/`.

### Angka bagian 4.4 diukur di kanvas 128×96

Bukan dummy: helm dan pedang sungguhan digambar di pose idle, lalu diukur dari peta pemilik piksel (hanya piksel yang masih terlihat).
Skala kepala Gobyet: 1,5× relatif `monkey.head` (digambar ulang, proporsi sama; alasan di bagian 5).
Alat: `tools/hero_phase_b.py`; angka lengkap di `hero-fase-b/ukuran.json`.

| Batas | Minimum | Terukur (pose idle) | Hasil |
|---|---|---|---|
| Helm total (dengan tanduk dan moncong) | 34×26 | 65×47 | lulus |
| Helm tanpa tanduk dan moncong (kubah + rahang + punggung) | 34×26 | 37×41 | lulus |
| Moncong | 10×8 | 34×14 | lulus |
| Tanduk, jarak terjauh piksel yang terlihat, melengkung | 14 px | 21,9 dan 21,9 (panjang busur desain 27,8 dan 22,4; busur/tali 1,21) | lulus |
| Rongga mata, tiap sisi | 4×3 | 7×6 dan 7×7 | lulus |
| Gigi rahang terlihat, lebar 2 px | 6 | 6 (lebar 2 px); ditambah 3 taring moncong | lulus |
| Bilah di titik terlebar | 10 px | 16 px (render sendiri), 16,8 px di pose idle | lulus |
| Luk gelombang | 5 | 5 per sisi (terukur) | lulus |
| Amplitudo luk (puncak ke pinggang) | 3 px | min 4, rata-rata 4,0 (desain 4,6) | lulus |
| Bahu berlapis, 3 pelat terpisah | 3 | piksel terlihat 38 / 45 / 139 | lulus |
| Panjang pedang / tinggi tubuh | ≈ 1,2 | 72,1 / 60,8 = 1,19 | lulus |
| Siluet isi hitam memperlihatkan tanduk, moncong, bilah | langsung terbaca | lihat `siluet.png` | **subjektif, penilaian pemilik** |

Definisi yang saya pilih: tinggi tubuh = telapak sampai puncak tengkorak Gobyet (tanpa helm dan tanduk); panjang pedang = ujung pommel
sampai ujung bilah. Semua angka lolos, jadi tidak ada usul kanvas lebih besar (160×120).

### Rencana teknis singkat (Fase C dan D, belum dikerjakan)

1. `src/hero.py`: delapan state dari keyframe pose yang diinterpolasi (idle 12, run 12, rage 12 `loop=false`, attack-leap 14,
   attack-smash 12, miss 10, exhaustion 12, defeated 14); durasi per frame tidak seragam; terdaftar di `SCENES` sebagai `berserker-hero-<state>`.
2. `src/pack.py`: kostum `berserker-hero` (label "Berserker Hero", group `fantasy`, base `viking-berserker`), tambah state, `APPLIES`, sel baru
   gerbang `K`, field sel `canvas` ({w:128, h:96}), `gif_scale: 4`, dan `loop: false` hanya untuk sel yang memintanya.
3. `src/export.py`: `indexed()` dan sheet memakai `cv.w`, `cv.h`; skala GIF per sel; palet lokal dari `PAL_HERO`.
4. `src/validate_pack.py`: V2/V3 per-sel (kanvas, skala GIF, `loop`); V3 palet hero ≤ 28; V4 hanya untuk sel loop; V10 aturan 200 KB hero dan 1,5 MB total;
   pemeriksaan baru hero (wajah, variasi tinggi kepala ≤ 10%, ukuran minimum 4.4 di keyframe, kontras); tes unit.
5. `pack/resolver.js`: helper `canvasOf` (aditif); manifest lama tanpa field `canvas` tetap valid.
6. `pack/preview.html` dan `tools/e2e_preview.js`: kanvas per sel, contact sheet per state (frame berurutan, nomor, 2×, bisa digulir di ponsel 390 px),
   pilihan latar terang atau gelap, mode statis dari keyframe.

## 2. Fase B: tiga pose kunci

Hanya tiga frame yang dibuat. Semua di kanvas 128×96, palet lokal 26 warna (25 terpakai di tiga pose), tanpa alfa parsial, tanpa teks.

| Pose | Frame | Durasi | Berkas 1× (RGBA) | Ukuran berkas | Keyframe |
|---|---|---|---|---|---|
| idle | 1 dari 12 rencana | belum ditentukan | `hero-fase-b/pose-1x-idle.png` | 3.656 B | napas di puncak |
| run | 1 dari 12 rencana | belum ditentukan | `hero-fase-b/pose-1x-run.png` | 3.845 B | puncak langkah (melayang) |
| attack-smash | 1 dari 12 rencana | belum ditentukan | `hero-fase-b/pose-1x-attack-smash.png` | 3.922 B | titik tumbukan |

Bukti gambar (semuanya terang di atas, gelap di bawah):

| Berkas | Isi |
|---|---|
| `hero-fase-b/kontak-1x.png`, `kontak-2x.png`, `kontak-4x.png` | viking-berserker 64×48 (dibesarkan 2×, 4×, 8× supaya kanvasnya sama tinggi dalam piksel layar) lalu idle, run, attack-smash hero |
| `hero-fase-b/helm-8x.png` | close-up helm pose idle, 8× |
| `hero-fase-b/pedang-4x.png` | close-up pedang pose idle, 4× |
| `hero-fase-b/siluet.png` | siluet isi hitam tiga pose (4×) |
| `hero-fase-b/ukuran.json` | semua angka terukur |

Desain (hanya dari bagian 4 brief): helm tengkorak naga besi hitam (moncong lurus ke depan dengan dua lubang hidung dan taring,
dua tanduk melengkung ke belakang dengan satu patah di ujung, rongga mata gelap dengan dua sumbu teal untuk rage yang belum dipakai di pose ini,
punggung bergerigi, paku keling, rahang menjadi pelindung pipi dengan enam gigi krem); pedang dua tangan bilah lima luk dengan garis pamor, pelindung sayap
melengkung ke arah pommel, gagang berbalut tali krem, pommel perunggu; pauldron kiri tiga pelat tumpuk, pauldron kanan satu pelat bergerigi, dada berpelat
bergaris tengah dan paku keling, sabuk lebar dengan gesper perunggu, rok rantai, sarung tangan dan sepatu pelat, tabard teal pendek. Tidak ada
jubah, bulu, mata menyala, darah, atau skema hitam-merah. Wajah Gobyet (mata, hidung, mulut), telinga, bulu tengkorak, dan ekor terlihat.

Hue shift: bayangan lebih dingin, sorotan lebih hangat; garis tepi 1 px turunan (hangat `(42,26,34)` untuk organik dan kain, dingin
`(22,26,40)` untuk besi); tiga nada per bahan, cahaya kiri atas; rim light biru baja 1 px pada tepi atas semua besi.

Wajah terlihat di semua tiga frame (piksel wajah / telinga): idle 288 / 58, run 297 / 58, attack-smash 298 / 58.
Tinggi bbox kepala (termasuk helm dan tanduk): 48, 47, 49 px, selisih terbesar 2 px (sekitar 4,3%).

Kontras luminans (WCAG), latar terang `(250,247,240)` dan gelap `(24,28,44)`:

| Warna | vs terang | vs gelap |
|---|---|---|
| garis tepi besi `(22,26,40)` | 16,19 : 1 | 1,02 : 1 |
| besi dasar `(54,60,82)` | 10,20 : 1 | 1,55 : 1 |
| rim biru baja `(120,158,204)` | 2,60 : 1 | 6,09 : 1 |

## 3. Perubahan rig (aditif)

`src/monkey.py` (diff 16 tambah, 6 hapus):

- `Canvas.__init__(self, w=None, h=None)`: `self.w, self.h = w or W, h or H`; `put` dan `image` memakai `self.w`, `self.h`. `Canvas()` identik dengan sebelumnya.
- `PAL_HERO = {}` (kosong secara bawaan) dan `rgb()` dengan fallback: `PAL`, lalu `PAL_EXT`, lalu `PAL_HERO`.
- `W`, `H`, `PAL`, `PAL_EXT` tidak diubah.

Berkas baru: `src/hero.py` (belum diimpor oleh `export.py`, jadi tidak memengaruhi aset apa pun), `tools/hero_phase_b.py`, `pack/reports/hero-fase-b/`, laporan ini.
Tidak ada dependensi baru (`requirements.txt` tidak diubah).

## 4. Output validasi mentah

Bukti aset lama identik byte, sebelum dan sesudah perubahan rig.

**Sebelum** (commit asal, `python3 src/validate_pack.py`, 9 m 12 s, kode keluar 0):

```
[V1] Hash aset yang dikunci dan aset yang sudah dibuat
  sha256-asli.txt: 27 identik, 0 berubah/hilang
  sha256-disetujui.txt: 89 identik, 0 berubah/hilang
  sha256-dibuat.txt: 242 identik, 0 berubah/hilang
...
[V2] ... 32 kostum, 13 state, 163 sel berlaku, 163 sel terisi; 0 gagal
...
  proyeksi pertambahan total: 11207390 byte (10.69 MB); ambang peringatan 15 MB, batas keras 16 MB
HASIL: LULUS
```

**Ekspor ulang penuh, kode sebelum dan sesudah perubahan `monkey.py`**, masing-masing di worktree terpisah (`python3 src/export.py`, kira-kira 7 menit):

- kode asal: `git status` kosong (semua 165 GIF dan sheet yang diekspor identik dengan yang ada di commit);
- kode dengan `monkey.py` baru: `git status` tidak menunjukkan satu pun berkas `gif/`, `sheets/`, atau `pack/` berubah; `diff -rq gif`, `diff -rq sheets`, dan `diff manifest.json` terhadap ekspor kode asal: identik.

**Sesudah** (pohon kerja dengan `monkey.py` baru):

```
[V1] Hash aset yang dikunci dan aset yang sudah dibuat
  sha256-asli.txt: 27 identik, 0 berubah/hilang
  sha256-disetujui.txt: 89 identik, 0 berubah/hilang
  sha256-dibuat.txt: 242 identik, 0 berubah/hilang
FAILS: []
```

Tes: `python3 -m unittest src/test_validate_pack.py`: `Ran 9 tests ... OK`. `node --test pack/resolver.test.js`: `# tests 19, # pass 19, # fail 0`.
Validator penuh sesudah perubahan (`python3 src/validate_pack.py`, 8 m 58 s, kode keluar 0): `HASIL: LULUS`, 0 baris GAGAL,
V1 27 / 89 / 242 identik, 163 sel berlaku dan terisi, proyeksi pertambahan 11.207.390 byte (10,69 MB). Keluaran lengkapnya **sama persis baris per baris**
dengan keluaran sebelum perubahan (`diff` tidak menunjukkan satu baris pun berbeda).

Belum diuji (bukan bagian Fase B): seam loop, durasi, ukuran GIF/total, resolver hero, preview, uji browser. Semuanya "tidak terbukti" sampai Fase C dan D.

## 5. Tebakan dan ketidakpastian

1. **Skala kepala 1,5×.** Helm minimal 34×26 tidak muat wajar di kepala `monkey.head` skala 1× (tengkorak ±19 px, dengan telinga ±28). Saya menggambar ulang kepala
   Gobyet pada 1,5× (tengkorak 28,8×25,2, mata di ±6, telinga di ±15,75). Proporsi dan warna wajah sama, hue shift halus, tapi ini **bukan fungsi `monkey.head` yang sama**.
   Bila pemilik ingin kepala identik piksel dengan v1, helm perlu diperkecil atau kanvas diperbesar.
2. **"Berdiri tegak, ujung pedang bertumpu di lantai, kedua tangan di gagang"** bertabrakan dengan pedang 1,2× tinggi tubuh. Pada sudut curam, tangan harus lebih
   tinggi dari bahu dan menutupi wajah. Pilihan saya: pedang landai (20°) di depan perut, tangan di pinggang, ujung menyentuh lantai 54 px di depan. Ini kompromi.
3. **"Ujung melengkung ke bawah"** pada pelindung sayap: saya tafsirkan relatif pedang tegak (ujung sayap turun ke arah pommel). Bila maksud pemilik "ke arah bilah", cukup membalik satu tanda.
4. **"5 luk"**: saya tafsirkan lima tonjolan simetris di tiap tepi (gaya flamberge), bukan bilah meliuk seperti keris. Dua-duanya memenuhi angka 4.4 yang diukur.
5. **Gigi.** Enam gigi rahang (3 per sisi) dihitung sebagai "gigi" 4.4; tiga taring moncong tambahan.
6. **Pose run.** Pedang dibawa tangan kiri (belakang) dan diseret di belakang; tangan kanan mengepal ke depan. Pemilik tidak menyebut tangan mana.
7. **Pose smash.** Pedang menancap ke balok kayu di lantai (sasaran, bukan karakter). Kepala digambar di depan tangan supaya wajah tidak tertutup; secara fisik tangan berada di
   depan dagu, jadi ini akal-akalan urutan gambar.
8. **Dua nada hitam.** Garis tepi dingin `o2` untuk besi dan hangat `o1` untuk lainnya. Brief hanya menyebut "warna gelap turunan"; dua tepi adalah keputusan saya.
9. **Warna.** 26 warna didefinisikan (batas 28) dan 25 terpakai di tiga pose; satu (wajah merah `ra`) menunggu state rage, dan tersisa dua slot kosong. Belum terbukti cukup untuk delapan state.
10. **Latar uji**: terang `(250,247,240)` dan gelap `(24,28,44)` adalah pilihan saya; pemilik tidak menetapkan warna.

## 6. Kelemahan yang saya lihat sendiri

- Lengan dan tangan di pose idle menumpuk di perut dan sulit dibaca; siku IK terlihat pendek dan agak kaku.
- Lima luk bilah terbaca seperti gergaji di 1× dan 2× karena rim light menegaskan puncak tiap luk. Pelindung sayap kecil dan kontrasnya rendah.
- Tanduk dan moncong di siluet masih bisa terbaca seperti telinga, terutama tanduk kiri. Moncong sudah lebih jelas daripada versi pertama saya, tapi belum diuji dengan orang.
- Besi di latar gelap: garis tepi 1,02 : 1 dan besi dasar 1,55 : 1, jadi bentuk bergantung pada rim light dan sorotan. Siluet gelap lebih lemah dari siluet terang.
- Pose run: kaki sebagian tertutup rok dan tabard; garis kecepatan hanya tiga baris; debu berupa gumpalan datar.
- Pose smash: bilah yang terlihat pendek karena sebagian terpotong lantai dan tertutup balok; efek kilat dan serpihan masih sederhana.
- Ekor, tabard, dan rok belum diberi gerak sekunder (hanya satu frame per pose).
- Pauldron tiga pelat terbaca sebagai tiga garis bertumpuk, bukan bahu melengkung.
- Rim pass menyorot setiap piksel besi di bawah garis tepi gelap, termasuk garis sambungan di dalam bentuk, jadi permukaan helm agak ramai.
- Belum ada pengujian dengan pengamat manusia; semua "terbaca" di sini hanya dari angka dan pandangan saya.

## 7. Bukti tambahan

Repo Bertahan-Bukan-hidup (`/home/user/Bertahan-Bukan-hidup`): `git status` kosong, cabang `claude/argument-battle-royale-skill-3wzgmg`, HEAD `696605e`
(commit 2026-10-01, sebelum tugas ini dimulai). Tidak ada perintah tulis yang saya jalankan di sana untuk tugas ini.

Diff stat terhadap `claude/gobyet-fase2` (delta tugas ini, commit `7e43deb`): 14 berkas, 1.396 tambah, 6 hapus. Satu-satunya berkas lama yang
berubah adalah `src/monkey.py` (22 baris). Tidak ada berkas di `gif/`, `sheets/`, `asli/`, atau `pack/sha256-*.txt` yang berubah.

Diff stat terhadap `main`: 1.390 berkas, 39.418 tambah, 259 hapus. Hampir semuanya berasal dari pekerjaan sebelumnya di `claude/gobyet-fase2`
(gerbang A–J dan folder `v2/`), bukan dari tugas ini.

Menunggu persetujuan gaya untuk Berserker Hero.
