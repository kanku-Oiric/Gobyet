# Gobyet Character Pack

Kostum menentukan **siapa** Gobyet. State menentukan **sedang apa** dia.
Folder ini berisi sistemnya:

| File | Isi |
|---|---|
| `manifest.json` | Peta kostum × state ke asset, dengan ukuran kanvas, jumlah frame, durasi per frame, loop, dan frame kunci. **Dibangkitkan** oleh `python3 src/export.py` dari `src/pack.py`; jangan diedit tangan. |
| `resolver.js` | `resolve(manifest, kostum, state)` dengan fallback berantai. Tanpa dependensi, jalan di browser (`window.GobyetPack`) dan Node (`require`). |
| `resolver.test.js` | Uji resolver dan manifest, termasuk ukuran PNG dan GIF setiap aset. Jalankan `node --test pack/resolver.test.js`. |
| `preview.html` | Matriks semua kostum × state, panel banding gaya 1× dan 4×, dan tes buta per keluarga kostum (idle 1× tanpa label, urutan acak dengan seed tetap). Buka lewat server: `python3 -m http.server` di akar repo, lalu `/pack/preview.html`. |
| `PROGRESS.md` | Status tiap gerbang Fase 2, commit, dan sel yang sudah atau belum terisi. |
| `STYLE.md` | Acuan gaya rig: outline, cahaya, shading, ukuran kepala dan prop, pola pose. |

## Kostum dan state

Setiap kostum di manifest punya `id`, `label`, dan `group`, plus field opsional:
- `base`: kostum induk. Dipakai varian kelas dan `normal-gblk`.
- `caption`: keterangan singkat.
- `applies`: sel yang berlaku untuk kostum itu, `{state: "required" | "optional"}`.

| group | Kostum |
|---|---|
| `core` | `normal` |
| `special` | `normal-gblk` (base `normal`) |
| `role` | `referee`, `judge`, `skeptic`, `champion` |
| `domain` | `greek-philosopher`, `academic`, `scientist`, `mathematician`, `lawyer`, `hacker`, `detective`, `gamer` |
| `fantasy` | `knight`, `viking`, `pirate`, `wizard`, dan 12 varian kelas (base = kostum faksinya) |
| `theology` | `pak-haji`, `priest` |

State: `idle`, `thinking`, `victory`, `defeated`, `judging`, `suspicious`, `attack`, `shocked`, `happy`, `dance-a`, `dance-b`, `dance-c`, `reveal`.

**Sel yang berlaku ditentukan oleh `APPLIES` di `src/pack.py`**, satu-satunya sumber. Totalnya 163 sel: 78 untuk 12 kostum lama dan 85 untuk kostum baru. `states[]` di manifest (`required` dan allowlist `costumes`) diturunkan dari tabel itu, hanya untuk kompatibilitas. Sel yang tidak berlaku tampil `—` di preview. Kostum tidak wajib punya semua state; fallback yang menutupinya.

## Resolver

```js
const r = GobyetPack.resolve(manifest, "hacker", "victory");
// r.kind:     "exact" | "fallback" | "placeholder"
// r.step:     "costume+state" | "costume+idle" | "base+state" | "base+idle" | "normal+state" | "normal+idle" | "placeholder"
// r.resolved: { costume, state } atau null
// r.cell:     { sheet, gif, frames, durations_ms, loop, keyframe, ... } atau null
// r.tried:    ["hacker/victory", "hacker/idle"]
```

Urutan fallback: **kostum+state → kostum+idle → base+state → base+idle → normal+state → normal+idle → placeholder CSS**.

`base` diambil dari field `base` kostum di `manifest.costumes`. Kalau kosong, tidak valid, atau sama dengan `normal`, langkah base dilewati, jadi manifest lama tanpa `base` tetap memakai rantai lama.

`cellRule(costume, state)` memberi `"required"`, `"optional"`, atau `null` dari `applies`. Manifest lama tanpa `applies` memakai aturan state lama.

`resolve` tidak pernah melempar error. Hal-hal berikut semuanya dianggap "tidak ada" lalu dilewati:
- manifest `null` atau bukan objek
- sel yang rusak: tanpa `sheet`, jumlah durasi tidak sama dengan jumlah frame, atau durasi ≤ 0
- getter yang melempar error
- nama yang tidak dikenal

`frameAt(cell, t, reduced)` memberi indeks frame pada waktu `t` (ms) sesuai `durations_ms`. Bila `reduced` bernilai true, yang dipakai frame kunci (`keyframe`), untuk `prefers-reduced-motion` dan tombol Statis di preview.

`keyframe` dipilih sebagai pose yang paling mewakili state, tidak harus frame 0.

`canvasOf(manifest, cell)` memberi `{ w, h }` kanvas satu sel: field opsional `canvas` milik sel bila ada, bila tidak `manifest.canvas` (64×48). `gifScaleOf(manifest, cell)` begitu juga untuk `gif_scale` (bawaan 8). Sel dengan `canvas` atau `gif_scale` yang tidak valid dianggap rusak dan dilewati resolver (tidak dirender dengan ukuran tebakan). Manifest lama tanpa field itu tidak berubah perilakunya. `frameAt` memperlakukan `loop: false` sebagai berhenti di frame terakhir.

## Asset

- Semua frame berukuran 64×48 dan transparan.
- `sheet` berisi satu baris frame berukuran 1×. Format ini yang dipakai untuk render di halaman: gambar per frame dengan `image-rendering: pixelated`.
- `gif` adalah versi 8× untuk README dan embed.
- `sheet4x` wajib untuk aset lama (asli dan gerbang A–C) dan **opsional untuk aset baru mulai Gerbang D**. Preview menggambar 4× dari sheet 1× tanpa smoothing. Uji browser membuktikan hasilnya sama per piksel dengan `sheet4x` untuk semua sel yang masih punya file itu.
- **Profil export aset baru (Gerbang D ke atas):**
  - GIF memakai `optimize=True` dan palet lokal, berisi hanya warna yang dipakai aset itu.
  - Validator memeriksa bahwa setiap frame hasil decode, total durasi, dan loop GIF sama dengan sheet 1×.
  - Aset lama tetap diekspor lewat jalur lama, jadi byte-nya tidak berubah.
- **Palet:** aset lama hanya memakai `PAL`. Aset baru boleh memakai `PAL` + `PAL_EXT` (warna tambahan di `src/monkey.py`, misalnya ungu). Karena palet GIF aset baru bersifat lokal, menambah kunci `PAL_EXT` tidak mengubah aset baru yang sudah ada.
- Path di manifest relatif terhadap `manifest.json`.
- Sel yang tidak ada di `cells` adalah **PLACEHOLDER**: belum ada asset, dan yang tampil adalah hasil fallback. Preview menandainya dengan latar arsir, garis putus-putus, dan label `PLACEHOLDER`.

Animasi lama berisi beberapa beat, jadi pemetaannya ke state adalah kecocokan terdekat:

| Sel | Asset | Catatan |
|---|---|---|
| `normal/idle` | `ngopi-santai` | |
| `normal/happy` | `makan-pisang` | |
| `greek-philosopher/thinking` | `filsuf-yunani` | berakhir dengan `!` |
| `academic/idle` | `wisuda` | dipindah dari `academic/victory` di Gerbang B; 78% loop adalah pose tenang memegang ijazah |
| `scientist/thinking` | `rambut-einstein` | berakhir menjulurkan lidah |
| `hacker/idle` | `hacker` | berakhir dengan `OK` |
| `detective/thinking` | `detektif-bug` | berisi momen kaget |

`marah-debug` dan `kondangan` tetap ada, tetapi di luar matriks (lihat `extras` di manifest).

### Asal sel

Setiap sel di manifest punya field `origin`:

- `"asli"`: 7 aset yang sudah ada sebelum Fase 2.
- `"baru"`: aset yang dibuat di Fase 2 dengan rig yang sama, kanvas 64×48, palet `PAL` (+ `PAL_EXT` mulai Gerbang D), dan garis tepi yang sama. Kodenya per modul:

  | Modul | Isi |
  |---|---|
  | `src/roles.py` | Referee, Judge, Skeptic, Champion (gerbang A, B) |
  | `src/domains.py` | Normal dan kostum domain, termasuk Gamer (gerbang C, D, E, G) |
  | `src/special.py` | Normal-GBLK (G) |
  | `src/fantasy.py` | Knight, Viking, Pirate, Wizard (H) |
  | `src/theology.py` | Pak Haji, Priest (I) |
  | `src/variants.py` | 12 varian kelas (J) |
  | `src/pelengkap.py` | sel sisa kostum lama (F) |

Aset baru juga punya field `gate`, yaitu gerbang persetujuan tempat aset itu dibuat, dan nama file `<kostum>-<state>`. Preview menandai aset baru dengan label **BARU** (biru), berbeda dari **ASLI** (hijau).

## Format manifest lengkap

`pack/manifest.json` (format `gobyet-pack/1`) dibangkitkan dari `src/pack.py`. Field tingkat atas:

| Field | Isi |
|---|---|
| `format` | `"gobyet-pack/1"` |
| `generated_by`, `paths` | keterangan asal dan basis path (relatif terhadap manifest) |
| `canvas` | `{ "w": 64, "h": 48 }`: kanvas bawaan semua sel. Sel boleh menimpanya dengan field `canvas` sendiri. |
| `gif_scale` | `8` (GIF 512×384): skala bawaan. Sel boleh menimpanya dengan `gif_scale` sendiri. |
| `costumes[]` | `{ id, label, group, base?, caption?, applies }`. `group` adalah kategori (`core`, `special`, `role`, `domain`, `fantasy`, `theology`). `base` = kostum induk untuk fallback varian. `caption` = keterangan (mis. kepanjangan GBLK). `applies` = `{ state: "required" \| "optional" }`. |
| `states[]` | `{ id, label, required, costumes? }`. Diturunkan dari `applies`, hanya untuk kompatibilitas manifest lama. |
| `fallback` | urutan langkah resolver (lihat Resolver) |
| `cells` | `{ kostum: { state: sel } }` hanya untuk sel yang punya aset |
| `extras[]` | aset di luar matriks: `{ source, note, gif, sheet }` (`marah-debug`, `kondangan`) |

Isi satu sel:

```json
{ "status": "final", "origin": "baru", "source": "knight-idle", "gate": "H",
  "sheet": "../sheets/knight-idle.png", "gif": "../gif/knight-idle.gif",
  "frames": 12, "durations_ms": [180, 180, 180, 180, 180, 180, 180, 120, 180, 180, 180, 180],
  "loop": true, "keyframe": 0 }
```

`sheet4x` hanya ada di aset lama (asli dan gerbang A-C). `gate` hanya ada di aset baru.

Field sel opsional, ditulis hanya bila ada: `canvas` (`{ "w", "h" }`, bilangan bulat positif) dan `gif_scale` (bilangan bulat ≥ 1). Sel tanpa field itu memakai `canvas` dan `gif_scale` tingkat atas, jadi manifest dan sel lama tetap valid dan tidak berubah. `loop` boleh `false` (sel tidak berputar: GIF diekspor tanpa blok loop dan berhenti di frame terakhir; validator melewati seam loop sel itu). Satu-satunya pemakai sejauh ini adalah Berserker Hero:

```json
{ "status": "final", "origin": "baru", "source": "berserker-hero-rage", "gate": "K",
  "sheet": "../sheets/berserker-hero-rage.png", "gif": "../gif/berserker-hero-rage.gif",
  "frames": 12, "durations_ms": [200, 140, 140, 180, 70, 90, 110, 70, 70, 70, 120, 1500],
  "loop": false, "keyframe": 6, "canvas": { "w": 128, "h": 96 }, "gif_scale": 4 }
```

## Berserker Hero (Gerbang K, kanvas 128×96)

Karakter utama original, kostum `berserker-hero` (label "Berserker Hero", group `fantasy`, `base: viking-berserker`; penempatan opsi A, keputusan pemilik). **Zirah bukan Gobyet, wajah di dalamnya Gobyet:** prajurit mesin berhelm penuh; wajah monyet Gobyet (`monkey.head` asli) hanya terlihat saat topeng dibuka di `victory` (keputusan pemilik). Dirombak total atas arahan pemilik (v3) dari dua gambar rujukan yang tidak disimpan di repo: model badan dan kepala dari rujukan pertama (jambul menyapu ke belakang, perut sisik, ekor panah), zirah dan pedang dari rujukan kedua (pelat hitam bergaris merah, salib merah di visor, pedang hitam berinti api merah). **Perisai naga** di bahu kiri menggantikan pelindung bahu raksasa: bentuk dari gambar perisai pemilik (ujung tombak di atas, sayap mengembang, permata tengah, meruncing ke bawah), dibuat mirip naga (sayap bertulang tiga jari dengan selaput bergerigi, mata celah sebagai permata, dua tanduk, sisik, tepi bawah menyala), warnanya disesuaikan karakter (perak → besi hitam, emas → merah darah, sian → merah menyala), dan diperbesar atas permintaan pemilik (±43×69 px). **Tepi terang:** setiap tepi gelap diberi garis luar 1 px baja terang `n4` (keputusan pemilik: halo di preview dan tepi terang di aset; tanpa warna baru). Bentuk dan warna diturunkan, bukan disalin piksel. Mata dan ekspresi dibawa visor (lengan salib), alis V, dan grill mulut. **Status: menunggu persetujuan gaya dari pemilik.** Dokumen ini tidak menyatakan gayanya bagus atau disetujui. Tahap sebelumnya (v1, v2) disimpan sebagai **evolusi** di `pack/evolusi/` (bagian di bawah).

| State | Frame | Loop | Isi |
|---|---:|---|---|
| `idle` | 12 | ya | berdiri tegak, pedang tertancap di sisi kanan, napas, jambul bergoyang, visor berkedip |
| `run` | 12 | ya | lari condong ke depan dengan pedang diacungkan: kontak, serap, lintas, dorong, melayang; debu dan garis kecepatan |
| `rage` | 12 | **tidak** | mengumpulkan amarah lalu meledak: visor putih-merah, merah badan naik satu tingkat (`heat`), jambul dan ekor mengembang, pedang diacungkan, bara dan garis kejut; frame terakhir ditahan 1500 ms |
| `attack-leap` | 14 | ya | jongkok, melompat, tebas turun, mendarat di balok kayu |
| `attack-smash` | 12 | ya | antisipasi, pedang diangkat tinggi, ayunan dengan smear, tumbukan ditahan ke balok kayu |
| `miss` | 10 | ya | ayunan meleset, pedang menancap lantai di depan balok, malu |
| `exhaustion` | 12 | ya | bungkuk bertumpu pada pedang, napas berat (uap), keringat |
| `defeated` | 14 | ya | berlutut bertumpu pada pedang, kepala tertunduk, visor dan api bilah meredup |
| `victory` | 20 | **tidak** | permintaan pemilik: topeng (pelat wajah) terbelah dan meluncur ke samping memperlihatkan wajah monyet Gobyet (senyum tipis lalu tersenyum, ±0,9 detik) lalu menutup dengan bunyi klik, pedang dicabut lalu ditusukkan ke tanah, satu kaki naik ke puncak rata batu sambil kepalan kanan menyusuri bilah dalam lima tahap dan mengusap darah monster (merah darah gelap) sampai bersih dan berkilau; frame terakhir ditahan 1500 ms |

- **Kode:** `src/hero3.py` (rig v3: helm penuh, visor, topeng buka-tutup dengan wajah Gobyet di dalamnya, perisai naga, badan, pedang, noda darah monster, `heat`, tepi terang), `src/hero3_fx.py` (efek dan batu berpalet v3), `src/hero3_scenes.py` (tabel pose per frame dan durasi, sembilan state; ekor per state dan per frame), `src/hero3_check.py` (pengukuran untuk validator). `src/hero.py` (rig v1) tetap sebagai pustaka rig (`PartCanvas`, `solid3`, `ik`, `SwordFrame`) dan sumber evolusi 1; `src/hero_scenes.py`, `src/hero2.py`, `src/test_hero2.py`, dan `tools/hero2_body.py` disimpan (keputusan pemilik) dan dipakai `tools/evolusi.py`, bukan pipeline ekspor. Rig lama tidak berubah: `monkey.Canvas(w, h)` dan `monkey.PAL_HERO` aditif, nilai bawaan 64×48 tetap.
- **Target serangan** selalu lantai atau balok kayu; tidak ada karakter lain di kanvas, tidak ada luka atau kematian. `defeated` adalah berlutut yang tenang. **Pengecualian dari permintaan pemilik:** state `victory` memperlihatkan darah monster di bilah (merah darah gelap `m1..m3` dengan kilau basah, lebih gelap dari api bilah; digambar kartun: gumpalan dan olesan, bukan percikan banyak) lalu menghapusnya. Darah itu hanya boleh ada di `victory` (V11 menolaknya di state lain).
- **Ekspor cepat hanya hero:** `python3 src/export.py berserker-hero` (argumen = awalan nama animasi; manifest tetap ditulis lengkap). Tanpa argumen mengekspor semuanya.
- **Validasi cepat hero:** `python3 src/validate_pack.py --hero-only` (V1, V2/V3, V4, V10, V11). Validasi penuh tanpa flag itu tetap yang menentukan.
- **Hash:** `pack/sha256-hero.txt` (`python3 tools/hero_hashes.py`, `--check` untuk memeriksa). Berkas ini berdiri sendiri; `sha256-asli.txt`, `-disetujui.txt`, `-dibuat.txt` tidak disentuh.
- **Bukti gaya:** `python3 tools/hero3_model.py` menulis tiga pose kunci, peta bagian, ekspresi visor, siluet, dan ukuran ke `pack/reports/hero3-model/` (bukti fase model; bagian lama seperti panel wajah mesin sudah tidak ada); `python3 tools/hero3_animasi.py [folder]` menulis lembar kontak tiap state, frame kunci di tiga latar, topeng, dan usapan; `python3 tools/hero3_revisi.py` menulis bukti revisi (perisai naga, wajah Gobyet, tepi terang, darah merah, ekor) ke `pack/reports/hero3-revisi/`; `python3 tools/hero3_victory.py` menulis bukti `victory` 20 frame (lembar, topeng, tusukan, batu dan usapan, angka per frame) ke `pack/reports/hero3-victory/`. Laporan: `pack/reports/hero3-model.md`, `pack/reports/hero3-animasi.md`, `pack/reports/hero3-revisi.md`, dan `pack/reports/hero3-victory.md` (terbaru). Laporan v1/v2 tetap di `pack/reports/` sebagai riwayat.
- **Preview:** `pack/preview.html` punya bagian "Berserker Hero: lembar kontak per state": pemutar 2× per state, semua frame berurutan, bernomor, 2×, bisa digulir mendatar (termasuk di ponsel 390 px), pilihan latar terang, gelap, atau abu tengah `#808080`, tombol **Halo** (kontur krem 1 px CSS di luar siluet, `drop-shadow`; hanya pratinjau, aset tidak berubah), dan mode Statis = frame kunci. State yang tidak berputar (`rage`, `victory`) ditandai "diputar sekali" dan punya tombol **Putar ulang** (dinonaktifkan di mode Statis). Kostum berkanvas sendiri tidak ikut tes buta (ukurannya membocorkan identitas).
- **Kontras tepi** (laporan V11; dihitung dari palet): garis tepi besi hitam `n0` sendiri terhadap latar terang 18,17:1, gelap **1,15:1**, abu tengah 4,92:1. Karena itu aset sekarang punya **tepi terang** `n4` di luar setiap tepi gelap: 3,59:1 di latar terang, **4,40:1 di latar gelap**, 1,03:1 di abu tengah (di sana garis hitam di dalamnya yang terbaca, 4,92:1). V11 menggagalkan frame yang masih punya tepi gelap tanpa tepi terang. Halo krem di preview tetap tersedia (14,05:1).

### Rekomendasi untuk integrasi arena (Fase 3)

Pemilik memilih **halo dan tepi terang**. Tepi terang `n4` sudah ada di aset (4,40:1 terhadap latar `#181c2c`), jadi siluet terbaca di arena gelap tanpa bantuan. Halo krem 1 px (CSS `filter: drop-shadow` empat arah tanpa blur pada kanvas atau gambar, dengan latar ada di pembungkus, bukan di elemen yang difilter) tetap disarankan di arena yang sangat ramai, karena tepi `n4` hampir hilang di latar abu tengah (1,03:1; di sana garis hitam di dalamnya yang terbaca).

### Evolusi Berserker Hero (`pack/evolusi/`)

Keputusan pemilik: kode v1 dan v2 disimpan dan diunggah sebagai evolusi. `python3 tools/evolusi.py` menulis isinya, `--check` memeriksa `pack/sha256-evolusi.txt`.

| Tahap | Isi | Berkas |
|---|---|---|
| Evolusi 1 (v1) | Gobyet berzirah besi hitam, helm tengkorak naga, tabard teal; 8 state animasi | `pack/evolusi/v1/berserker-hero-<state>.gif` (byte persis dari commit `fd5d899`, diperiksa terhadap hash yang dikunci saat itu) dan 3 pose kunci PNG 4× |
| Evolusi 2 (v2) | Gobyet berzirah hitam-merah, badan chibi mekanis; ditolak pemilik sebelum dianimasikan | 3 pose kunci PNG 4× dari `src/hero2.py` |
| Evolusi 3 (v3, sekarang) | zirah bukan Gobyet, perisai naga, tepi terang, wajah Gobyet di balik topeng; 9 state animasi | GIF di `gif/` (tidak disalin) dan 3 pose kunci PNG 4× |

Halaman `pack/evolusi/index.html` menampilkan ketiganya (latar terang, gelap, abu tengah). Aset evolusi bukan bagian manifest dan tidak dihitung dalam anggaran hero; ukurannya ±0,95 MB (8 GIF v1 888.110 B). Pose kunci v3 di folder ini ikut berubah bila rig v3 berubah, jadi jalankan ulang `tools/evolusi.py` setelah mengubah rig.

### GIF tanpa loop (`berserker-hero/rage` dan `berserker-hero/victory`, `loop: false`)

GIF diekspor tanpa blok aplikasi NETSCAPE2.0 (tanpa `loop`), dan frame terakhir ditahan 1500 ms (rage: total 2760 ms; victory: total 3980 ms) supaya penampil yang tetap mengulang tampak berhenti lebih lama. Menahan 1500 ms tidak membuat penampil pengulang benar-benar berhenti: ia akan memutar ulang setelah total durasi (2,76 atau 3,98 detik).

| Penampil | Perilaku GIF tanpa loop | Status |
|---|---|---|
| Chromium 141 (headless, Playwright; `<img>`) | berhenti di frame terakhir dan tidak berubah lagi untuk `rage` dan `victory` (diuji sampai total + 6,5 detik; frame yang tampil = frame terakhir sheet piksel demi piksel; kontrol: GIF `run` yang berputar tetap bergerak). | **diuji** (`node tools/gif_once_check.js`) |
| Firefox, Safari/WebKit | spesifikasi GIF89a: tanpa blok loop, animasi diputar sekali | **belum diuji** (hanya Chromium tersedia di lingkungan pengujian) |
| Penampil gambar sistem (Windows, macOS, Android, iOS), WhatsApp, Telegram, Slack, Discord, GitHub (README), editor gambar | tidak diketahui; sebagian penampil mengabaikan ketiadaan blok loop dan mengulang tanpa henti | **belum diuji** |

Preview memakai sheet PNG dan `frameAt`, bukan `<img>` GIF, jadi perilakunya di preview ditentukan manifest (`loop: false` = berhenti di frame terakhir), bukan penampil GIF. Pemakai yang perlu pasti berhenti sebaiknya memakai sheet + manifest (`GobyetPack.frameAt`), bukan GIF.


## Menambah kostum, state, atau varian

1. **Kostum baru:**
   - Tambahkan `(id, label, group)` ke `COSTUMES` di `src/pack.py`, plus `base` dan `caption` di `COSTUME_META` bila perlu.
   - Tentukan sel yang berlaku di `APPLIES`, minimal `idle` wajib.
   - Pilih warna dominan dengan ΔE ≥ 15 dari semua kostum dasar (lihat tabel alokasi di `STYLE.md`). Warna baru masuk `PAL_EXT`, dengan kunci yang tidak bertabrakan dengan `PAL`.
2. **Gambar di modul kostumnya:**
   - Pakai rig `head()`, `sitting_body()` atau `dressed_body()`, dan `arm()` apa adanya. Wajah dan badan Gobyet terkunci; kostum hanya lapisan.
   - Daftarkan `SCENES = {"<kostum>-<state>": (fungsi_frame, jumlah_frame, fungsi_durasi)}` dan `PROPS` untuk V7.
   - Modul baru didaftarkan di `export.all_scenes()` dan di `props()` pada validator.
3. **Petakan sel:** tambahkan `(kostum, state): ("<kostum>-<state>", frame_kunci, "<gerbang>")` ke `NEW`. Frame kunci adalah pose yang paling informatif, dan untuk state non-idle harus jelas berbeda dari idle.
4. **Jalankan:** `python3 src/export.py`, lalu `python3 src/validate_pack.py --gate <X>`, `node --test pack/resolver.test.js`, dan `node tools/e2e_preview.js`.
   - Sebelum dan sesudah export, verifikasi `sha256sum -c` untuk `pack/sha256-asli.txt`, `pack/sha256-disetujui.txt`, dan `pack/sha256-dibuat.txt`. Aset lain tidak boleh berubah byte.
5. **Varian:** kostum dengan `base` = kostum faksi. Varian mewarisi fallback ke kostum dasarnya dan hanya mengubah prop, aksesori, dan warna aksen (ΔE ≥ 10 dari saudara sefaksi).
6. **State baru:** tambahkan ke `STATE_IDS` di `src/pack.py`, lalu ke `APPLIES` untuk kostum yang memakainya. Resolver tidak perlu diubah.

## Aturan tarian

- `dance-*` tepat 16 frame × 120 ms.
- Pose besar berganti di f0, f4, f8, dan f12. Di dalam beat hanya ekor yang bergerak halus. V9 memeriksa bahwa perubahan di transisi beat lebih besar daripada di transisi lain, dan seam lulus.
- Badan tetap duduk dan bergoyang, meniru cara `kondangan`. Tidak ada badan berdiri baru.
- Prop tidak boleh keluar dari kanvas atau menutupi wajah di frame mana pun.
- Yang menari: Normal, Champion, Gamer, Normal-GBLK (tiga tarian), Viking, dan Pirate.
- Role netral (Referee, Judge, Skeptic) dan kostum teologi tidak pernah menari (7.2d, 7.3).

## Guardrail konten

- **7.1 Senjata (fantasi dan varian):**
  - Gaya kartun. Tanpa darah, luka, proyektil melayang, kilatan tembakan, atau asap laras.
  - `attack` adalah metafora: prop dihentak atau ditancapkan ke lantai, balok, atau papan kayu; pose membidik ke papan sasaran bulat tanpa melepas anak panah; atau senapan diarahkan ke atas.
  - Tidak ada yang diarahkan ke karakter lain. Senjata api hanya prop yang dipegang.
  - Nama kelas adalah arketipe generik; tidak meniru seni atau UI game mana pun.
- **7.2 Teologi:** lihat bagian "Kostum teologi" di bawah dan audit `[VT]` di Validasi.
- **7.3 Role netral** (Referee, Judge, Skeptic) tidak menari dan tidak dibuat konyol. Victory mereka tanpa lompat dan tanpa konfeti. Champion boleh menari.
- **7.4 Defeated:** tidak brutal dan tidak merendahkan. Tanpa darah, tengkorak, atau simbol kematian; cukup lunglai atau rebah, prop terjatuh, dan helaan napas.

## Validasi

```sh
python3 src/validate_pack.py --gate D          # V1-V10; --all untuk tabel beat semua aset baru
python3 src/validate_pack.py --palette-study   # tambahan: studi palet (bagian 6.1)
python3 src/validate_pack.py --hero-only       # cepat: hanya Berserker Hero (V1, V2/V3, V4, V10, V11)
python3 -m unittest src/test_validate_pack.py  # audit teks V8 menangkap semua pemanggil mini_text
node --test pack/resolver.test.js              # resolver, rantai varian, applies, manifest
node tools/e2e_preview.js                      # uji browser (Playwright, alat dev opsional; lihat tools/README.md)
```

- `pack/sha256-asli.txt` mengunci 27 file `gif/` dan `sheets/` yang ada sebelum Fase 2.
- `pack/sha256-disetujui.txt` mengunci aset baru yang gayanya sudah disetujui pemilik.
- `pack/sha256-hero.txt` mengunci aset Berserker Hero (Gerbang K) yang sudah dibuat dan belum disetujui. V1 memeriksanya bersama tiga berkas lain.
- **V11 (Berserker Hero, v3):** spesifikasi (9 state, jumlah frame, loop, canvas 128×96, `gif_scale` 4, ≤ 28 warna); setiap frame sheet identik piksel dengan render ulang dari kode; durasi tidak seragam, frame terakhir `rage` dan `victory` 1500 ms; **identitas**: tidak ada kunci atau bagian Gobyet hero v1/v2 di mana pun, warna wajah Gobyet (`B b F f M`) hanya di bagian wajah di balik topeng, dan wajah tidak terlihat saat topeng tertutup; **tepi terang**: tidak ada piksel karakter berwarna gelap (`n0 n1 n2 q0 q1`) yang bersebelahan langsung dengan piksel kosong; tidak ada piksel di tepi kanvas; **darah monster (merah darah gelap, `m1..m3`) hanya di `victory`**; visor salib atau mata Gobyet terlihat di setiap frame; **sisi**: perisai naga tetap di kiri, bahu bundar di kanan, jambul di belakang helm, ekor di kiri, diukur dari centroid x piksel elemen relatif titik tengah badan (jambul: relatif helm), dengan uji unit yang menandai frame yang dicerminkan; tinggi kotak kepala berubah ≤ 10%; seam loop ≤ langkah terbesar; siluet `run` berurutan IoU ≤ 0,90; serangan: 1-2 frame smear sebelum tumbukan, frame tumbukan ≥ 1,5 × median durasi, ada debu dan serpihan, **ekor sedang** (35-80% ekor idle f0 di frame tumbukan; keputusan pemilik, rentang usulan saya); `rage`: garis kejut dan bara hanya di rage (tiga frame awal tenang), merah menyala di frame kunci ≥ 1,25 × frame awal; **`victory`**: topeng tertutup di frame awal dan akhir lalu membuka-menutup berurutan (isi topeng puncak ≥ 250 piksel, wajah Gobyet ≥ 200 piksel dengan mata ≥ 12 piksel), topeng sudah tertutup sebelum pedang diangkat tinggi di luar tanah lalu ditusukkan (ujung di baris tanah, sudut ≥ 84°, ada debu), batu terlihat di semua frame, kaki terangkat menapak batu setelah menusuk sampai frame akhir, noda ≥ 150 piksel di awal, menyusut berurutan, ≥ 2 frame sebagian dengan kepalan menyentuh pedang, 0 di frame akhir yang berkilau; batas keterbacaan frame kunci (usulan saya dari pengukuran, bukan angka brief: helm ≥ 30×28, visor atau mata ≥ 40 px, badan perisai naga ≥ 280 px, seluruh perisai naga ≥ 650 px, pedang ≥ 300 px, kepalan ≥ 100 px, jambul ≥ 250 px); kontras luminans warna kunci terhadap empat latar pratinjau (terang, gelap, abu tengah #808080, dan halo krem) dan kontras tepi terang dilaporkan (bukan lulus/gagal).
- Validator keluar dengan kode 1 bila:
  - ada hash yang berubah;
  - warna di luar palet yang diizinkan, atau ada piksel semi-transparan;
  - ukuran salah, atau isi GIF berbeda dari sheet;
  - seam loop aset baru melebihi ambang;
  - IoU defeated vs idle aset baru di atas 0,85;
  - teks melanggar aturan glyph;
  - tarian tidak 16 × 120 ms;
  - proyeksi ukuran melewati anggaran 16 MB.
- **Metrik pelengkap seam:** `seam/median` = selisih frame terakhir → frame pertama dibanding median selisih antar-frame berurutan di dalam aset (kolom `seam/med` di V4, dan di V11 untuk hero). Nilai ≈ 1 berarti sambungan loop sebesar langkah biasa.
- **SEAM-POP dikecualikan dengan alasan tertulis:** mekanisme `POP_EXEMPT` di `src/validate_pack.py` tetap ada untuk `berserker-hero/run` (alasan: siklus lari bergerak seragam; berlaku hanya bila seam/median ≤ 1,25 dan median ≥ 0,9 × maks), tetapi pada aset v3 tidak ada sel yang memicu SEAM-POP, jadi tidak ada pengecualian yang dipakai (seam/median run 1,04). Aset tidak diubah untuk menghilangkan peringatan; satu penyesuaian posisi pose pendaratan dan debu kontak dilakukan sebelum aset dikunci supaya seam run tidak melebihi langkah terbesar.
- Ambang seam loop = 1,25 × selisih piksel terbesar antar-frame berurutan di aset itu sendiri. Aset yang terkunci hash dan melewati ambang dilaporkan **DIKETAHUI**, bukan GAGAL, karena tidak boleh diubah.
- Warna dominan dihitung dari piksel kostum saja, yaitu piksel frame kunci yang berbeda dari Normal idle pada posisi sama. Warna tubuh (bulu, kulit, garis tepi) tidak dihitung. Jaraknya CIE76 ΔE di ruang Lab.
  - Untuk Pak Haji dan Priest, piksel aura juga tidak dihitung. Posisinya diambil dari `theology.aura_mask` untuk frame kunci. Aura sengaja identik untuk keduanya (7.2e), jadi tidak bisa menjadi pembeda. Kalau dihitung, `n` aura menjadi dominan Pak Haji dan menyamakan keduanya.
- **Audit teologi `[VT]`** (keputusan pemilik 11c) selalu dijalankan dan wajib lulus. `python3 src/validate_pack.py --theology-only` menjalankan audit ini saja; dipakai di Gerbang I sebelum state selain idle dibuat.
  - (i) Mask aura kedua kostum identik per state dan frame, digambar paling awal (di belakang badan), hanya C/n/O, dan tidak naik di atas pusat kepala.
  - (ii) Jumlah state, jumlah frame, dan durasi identik.
  - (iii) Tidak ada teks selain ".". Titik gelembung thinking digambar sebagai piksel, jadi `mini_text` tidak dipanggil sama sekali.
  - (iv) Warna kalung salib `y` tidak muncul di Pak Haji, dan di Priest hanya sebagai salib 3×4. Buku Priest hanya berwarna sampul, halaman, dan tepi.
  - (v) Zona dagu tanpa warna janggut putih atau abu, dan zona di atas alis tanpa hijau daun.
  - (vi) Zona kopiah tanpa hitam, tidak ada warna batik, dan kopiah putih Pak Haji utuh.
  - Kontrol positif: pemeriksaan yang sama dijalankan pada Greek (janggut dan daun) dan `kondangan` (peci hitam dan batik). Kalau tidak terdeteksi di sana, validator GAGAL karena pemeriksaannya rusak.

### Aturan teks

- Glyph hanya dari `MINI` di `src/monkey.py`, maksimal 3 karakter per gelembung.
- Audit V8 mengganti setiap nama yang menunjuk ke `mini_text` di semua modul (termasuk `from monkey import mini_text` dan alias), jadi tidak ada jalur yang lolos.
- Pengecualian yang disahkan pemilik:
  - Papan tulis Scientist `E=mc`, tampilan asli `rambut-einstein`. Harus statis: posisinya sama di setiap frame.
  - Papan tanda `GBLK` milik `normal-gblk` (Gerbang G).
- `GG` milik Gamer tidak perlu pengecualian karena hanya 2 karakter.

### Pengecualian warna yang diketahui (diterima pemilik)

Pasangan kostum dasar dengan ΔE di bawah 15. Semuanya melibatkan tampilan asli yang terkunci, jadi tidak diubah:

| Pasangan | Dominan | ΔE |
|---|---|---:|
| Referee – Academic | `W` – `W` (kaus wasit putih, kemeja wisuda putih) | 0,0 |
| Judge – Hacker | `L` – `q` (jubah hitam, hoodie abu gelap) | 7,2 |
| Normal – Detective | `B` – `d` (bulu, mantel cokelat) | 12,2 |

Pembeda pasangan ini adalah siluet dan prop, bukan warna.

### Known issues (disetujui apa adanya, tanpa revisi)

- `academic/victory` (C): topi toga terpotong 1 baris di tepi atas kanvas pada puncak lemparan.
- `academic/defeated` (C): di 1× hanya berbeda 1-2 px dari idle (badan turun, topi miring, mata). IoU siluet frame kunci defeated vs idle 0,75.
- `hacker/thinking` (E): mata yang menyipit di balik kacamata yang diturunkan hampir tidak terlihat; kesan menyipit dibawa alis.
- Jangka Mathematician (D): kaki 1 px abu terang, tipis di 1×.
- Dasi Lawyer (E): 2×8, di bawah target prop 6×6 (prop sekunder).
- Audit teks V8: nama yang menunjuk ke `mini_text` di semua modul ditangkap. Pemanggilan lewat closure atau argumen default secara teori bisa lolos; belum ada kasusnya di kode.

## Anggaran ukuran

- **Definisi (keputusan pemilik):** "total pack ≤ 16 MB" berarti **pertambahan `gif/` + `sheets/` sejak commit `dd78be8`**. Ukuran seluruh pohon repo (`pack/`, `src/`, `v2/`, laporan, gambar bukti) **tidak dihitung**. V10 mencetak definisi ini di setiap keluaran.
- Batas pertambahan `gif/` + `sheets/`: **16 MB** dari kondisi awal Fase 2 lanjutan (commit `dd78be8`). **Ambang peringatan 15 MB:** bila proyeksi melewatinya, validator GAGAL (STOP-DARURAT).
- V10 memisahkan total GIF dan total sheet, masing-masing dengan pertambahan dan proyeksi sampai semua sel terisi. Contoh sebelum Gerbang G (42 dari 163 sel terisi):

  | | di `dd78be8` | sekarang | pertambahan | proyeksi akhir |
  |---|---:|---:|---:|---:|
  | GIF | 3.029.800 | 4.593.307 | 1.563.507 | 13.387.528 |
  | sheet | 365.586 | 422.018 | 56.432 | 483.199 |

  Proyeksi total 13,23 MB. Pada profil baru, GIF menyumbang sekitar 96% ukuran aset (rata-rata 97.719 B GIF vs 3.527 B sheet 1×).
- **Akhir Fase 2 (163/163 sel, nyata):**

  | | di `dd78be8` | akhir | pertambahan |
  |---|---:|---:|---:|
  | GIF | 3.029.800 | 13.799.243 | 10.769.443 |
  | sheet | 365.586 | 803.533 | 437.947 |

  Total pertambahan 11.207.390 B (10,69 MB), di bawah ambang 15 MB dan batas 16 MB. Proyeksi awal 13,23 MB turun karena aset baru rata-rata lebih kecil (GIF 78.609 B).
- Opsi A (sheet4x opsional) dan B (GIF `optimize=True`) berlaku untuk aset baru mulai Gerbang D. Aset A, B, dan C tidak diekspor ulang.
- **Berserker Hero (Gerbang K):** total GIF + sheet satu karakter ≤ **2.000.000 B** (keputusan pemilik "maksimal 2 MB", dibaca ketat sebagai 2.000.000 byte; sebelumnya 1,5 MiB), tiap GIF ≤ 307.200 B (300 KiB, usulan saya karena pemilik tidak menetapkan batas per GIF; 256 KiB saat revisi perisai, dinaikkan saat `victory` menjadi 20 frame; sebelumnya 200 KB); V10 memeriksanya sebagai GAGAL bila lewat. Angka nyata (9 state): lihat `pack/reports/hero3-victory.md`. Ruang tambahan terpakai oleh perisai naga, tepi terang, wajah Gobyet, dan 4 frame tambahan `victory`. GIF hero memakai `disposal=2` (tiap frame utuh, supaya latar transparan benar), jadi ukurannya naik hampir linear dengan jumlah frame. Sheet hero diekspor dengan PNG `optimize` (piksel identik).

### Rancangan opsi D: GIF dibuat saat rilis (belum diimplementasikan)

Preview dan resolver hanya butuh `sheet` 1× dan manifest, jadi GIF bisa dibuat saat rilis, tidak disimpan di repo.

**Angka hemat (V10):** GIF aset profil baru yang sudah ada 1.563.507 B. Di akhir Fase 2, proyeksinya sekitar 13,4 MB tidak perlu masuk riwayat git. Yang tetap disimpan hanya sheet 1× (proyeksi pertambahan sekitar 0,5 MB).

Langkahnya:

1. Repo menyimpan resep (`src/*.py`), sheet 1×, dan manifest. Field `gif` di manifest tetap ada, tetapi menunjuk ke berkas rilis.
2. Workflow rilis menjalankan `python3 src/export.py`, memverifikasi hash GIF aset terkunci terhadap daftar hash yang tersimpan, lalu mengunggah GIF sebagai aset rilis (pola yang sama dengan paket skill di repo Bertahan).
3. README memakai URL aset rilis, bukan path di repo.
4. Risiko: embed `raw.githubusercontent.com/.../main/gif/...` yang sudah beredar akan rusak kalau GIF dihapus dari `main`. Karena itu GIF lama tetap disimpan, dan hanya GIF baru yang pindah ke rilis.

**Catatan untuk Fase 3 (arena):** jangan memuat seluruh manifest dan semua sheet sekaligus. Arena cukup memuat manifest (sekitar 40-60 KB JSON), lalu mengambil sheet 1× **per kostum** yang benar-benar dipakai turnamen itu: satu kostum domain, empat kostum peran, dan Normal sebagai fallback. Satu sheet 1× rata-rata sekitar 3,5 KB, jadi satu kostum lengkap kurang dari 30 KB. GIF tidak dibutuhkan arena.

## Keputusan gaya dari pemilik

Aturan 3 (kostum yang sudah punya tampilan memakai tampilan itu) menang atas brief lama.

| Kostum | Keputusan |
|---|---|
| Greek Philosopher | Laurel hijau tetap, karena aset asli `filsuf-yunani` yang terkunci memakainya. Aturan "tanpa laurel" dicabut. |
| Champion | Laurel emas dihapus. Penggantinya medali emas di selempang merah; piala tetap. |
| Scientist | Mengikuti `rambut-einstein` asli, yaitu sweter abu-abu. Aturan jas lab dicabut. |
| Lawyer | Dasi biru tua atau hitam, bukan merah. Map cokelat, bukan putih, supaya beda dari kertas Skeptic. |
| Mathematician | Batu tulis genggam kecil berbingkai dan kapur kecil, tidak meniru papan atau kapur Einstein. |
| Semua | Reduced motion memakai `keyframe` dari manifest. Aturan "frame 0 = pose statis" dicabut. |

## Rancangan aturan pemilihan (untuk integrasi arena, belum diimplementasikan)

**Kostum ROLE mengikuti fase turnamen**, memakai acara arena yang sudah ada:

| Fase | Acara | Kostum |
|---|---|---|
| Awal babak | `r:<n>` | `referee` |
| Penilaian duel | `m:<id>` | `judge` (state `judging`) |
| Falsifikasi | `f:<i>` | `skeptic` |
| Pemenang | `w` | `champion` |

**Kostum DOMAIN dipakai di fase lain** (persiapan, jeda, laporan). Kostum ini dipilih **sekali** di awal turnamen, setelah peta ruang argumen ada.

- **Sinyal:** teks topik, `map.json.question_type`, dan `map.json.evidence_domains`.
- **Metode:** berbasis aturan kata kunci per kostum, deterministik, tanpa LLM. Hanya satu kostum dengan skor tertinggi yang dipakai, termasuk untuk topik campuran.
- **Jatuh ke `normal`:** bila tidak ada yang cocok, skor di bawah ambang, atau dua kostum teratas seri.

**Kostum lain (rancangan, belum diimplementasikan):**

- **Fantasi dan Gamer** hanya untuk topik bertema, misalnya pertanyaan tentang abad pertengahan, bajak laut, atau game. Pemilihannya memakai aturan kata kunci yang sama dengan kostum domain, dipilih sekali per turnamen, dan varian kelas hanya bila topiknya menyebut kelas itu.
- **Teologi** netral (lihat bagian Kostum teologi).
- **Normal-GBLK** adalah maskot spesial. Tidak dipilih otomatis oleh aturan topik; hanya dipakai lewat override manual atau acara khusus yang diputuskan saat integrasi.

**Disimpan tanpa mengubah schema:** di file sidecar `RUN_DIR/presentation.json`, bukan di `state.json`.

```json
{ "gobyet": { "domain": "greek-philosopher", "source": "auto", "score": 3, "matched": ["filsafat"],
              "rules_version": 1, "decided_at": "2026-01-01T00:00:00+00:00" } }
```

- **Tidak masuk integritas.** `abr.py verify` hanya meng-hash `fighters.jsonl`, `population.json`, `seeding.json`, `map.json`, `dossiers.json`, `rounds/`, dan laporan, jadi sidecar tidak memengaruhi hasil maupun pemeriksaan integritas.
- **Tidak dihitung ulang saat render.** Arena membaca nilai yang tersimpan, jadi replay menampilkan kostum yang sama seperti aslinya. Run lama tanpa sidecar tampil sebagai `normal`.
- **Override manual:** tulis `"source": "manual"` dengan kostum pilihan. Mekanisme resminya, misalnya satu perintah CLI, diputuskan saat integrasi.

## Kostum teologi: presentasi, bukan penilaian (aturan 7.2)

- Pak Haji dan Priest adalah **kostum presentasi**. Kostum ini tidak menilai tradisi mana pun.
- **Menang atau kalah tidak boleh diartikan benar atau salah secara teologis.** Seperti `champion` di bagian Nada, state `victory` berarti "klaim bertahan di bawah rubrik simulasi ini". State `defeated` pada kostum teologi digambar sebagai tenang menerima: badan tegak, senyum tipis, aura meredup sesaat lalu kembali.
- Kedua kostum diperlakukan identik: state, jumlah frame, durasi, ritme angguk, ekspresi, dan aura sama persis. Validator memeriksanya (`[VT]` i dan ii).
- Tidak ada aksara Arab, kutipan kitab, kaligrafi, atau simbol suci selain kalung salib polos kecil Priest. Tidak ada gestur ritual: tasbih hanya digeser, buku hanya dipegang tertutup. Tidak menari dan tidak slapstick.

**Rancangan Fase 3 (belum diimplementasikan):**

- Pemetaan state untuk kostum teologi harus netral. Kostum teologi tidak dipetakan ke `w` (pemenang) atau ke hasil duel secara khusus. Kalau kostum teologi dipakai, dua tokoh mendapat state yang sama untuk acara yang sama.
- Kostum teologi hanya dipakai bila topik **menyebut satu tradisi secara eksplisit** (mis. "menurut fikih ..." atau "dalam teologi Katolik ..."). Untuk pertanyaan teologis yang tidak menyebut satu tradisi, sistem **tidak boleh otomatis memilih salah satu tokoh**. Pilihannya: tampilkan keduanya berdampingan dengan state identik, atau jatuh ke `normal`. Pilihan di antara keduanya diputuskan saat integrasi.
- Kostum teologi tidak dipakai untuk peran turnamen (`referee`, `judge`, `skeptic`, `champion`).
- Tokoh teologi tradisi lain (mis. Biksu, Pandita) ada di backlog. Kalau ditambahkan, berlaku aturan identik yang sama, termasuk aura yang sama persis.

## Backlog (hanya dicatat, tidak dikerjakan di Fase 2)

- **Kostum domain:** Historian, Economist, Psychologist, Sociologist, Journalist, Doctor, Engineer, Professor, Archivist.
- **Tokoh teologi tradisi lain** (mis. Biksu, Pandita), dengan aturan 7.2 yang sama dan aura yang identik.
- **Kostum absurd lain.**
- Opsi D (GIF dibuat saat rilis), bila anggaran ukuran menjadi masalah.

## Nada

- Yang kalah tidak dihina. State `defeated` adalah reaksi Gobyet sendiri, misalnya menghela napas, bukan ejekan terhadap argumen yang kalah.
- `champion` berarti "klaim bertahan di bawah rubrik simulasi ini", bukan kebenaran objektif.
