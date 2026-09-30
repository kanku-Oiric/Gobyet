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
| `canvas` | `{ "w": 64, "h": 48 }` |
| `gif_scale` | `8` (GIF 512×384) |
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
python3 -m unittest src/test_validate_pack.py  # audit teks V8 menangkap semua pemanggil mini_text
node --test pack/resolver.test.js              # resolver, rantai varian, applies, manifest
node tools/e2e_preview.js                      # uji browser (Playwright, alat dev opsional; lihat tools/README.md)
```

- `pack/sha256-asli.txt` mengunci 27 file `gif/` dan `sheets/` yang ada sebelum Fase 2.
- `pack/sha256-disetujui.txt` mengunci aset baru yang gayanya sudah disetujui pemilik.
- Validator keluar dengan kode 1 bila:
  - ada hash yang berubah;
  - warna di luar palet yang diizinkan, atau ada piksel semi-transparan;
  - ukuran salah, atau isi GIF berbeda dari sheet;
  - seam loop aset baru melebihi ambang;
  - IoU defeated vs idle aset baru di atas 0,85;
  - teks melanggar aturan glyph;
  - tarian tidak 16 × 120 ms;
  - proyeksi ukuran melewati anggaran 16 MB.
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
