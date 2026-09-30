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
- `"baru"`: aset yang dibuat di Fase 2 dengan rig yang sama, kanvas 64×48, palet `PAL`, dan garis tepi yang sama. Kodenya ada di `src/roles.py` (kostum ROLE) dan `src/domains.py` (Normal dan kostum DOMAIN).

Aset baru juga punya field `gate`, yaitu gerbang persetujuan tempat aset itu dibuat, dan nama file `<kostum>-<state>`. Preview menandai aset baru dengan label **BARU** (biru), berbeda dari **ASLI** (hijau).

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

### Aturan teks

- Glyph hanya dari `MINI` di `src/monkey.py`, maksimal 3 karakter per gelembung.
- Audit V8 mengganti setiap nama yang menunjuk ke `mini_text` di semua modul (termasuk `from monkey import mini_text` dan alias), jadi tidak ada jalur yang lolos.
- Pengecualian yang disahkan pemilik:
  - Papan tulis Scientist `E=mc`, tampilan asli `rambut-einstein`. Harus statis: posisinya sama di setiap frame.
  - Papan tanda `GBLK` milik `normal-gblk` (Gerbang G).
- `GG` milik Gamer tidak perlu pengecualian karena hanya 2 karakter.

### Known issues (Gerbang C, disetujui apa adanya)

- `academic/victory`: topi toga terpotong 1 baris di tepi atas kanvas pada puncak lemparan.
- `academic/defeated`: di 1× hanya berbeda 1-2 px dari idle (badan turun, topi miring, mata). IoU siluet frame kunci defeated vs idle 0,75.

## Anggaran ukuran

- Batas pertambahan `gif/` + `sheets/`: **16 MB** dari kondisi awal Fase 2 lanjutan (commit `dd78be8`). Validator V10 menghitung pertambahan dan proyeksinya sampai semua sel terisi.
- Opsi A (sheet4x opsional) dan B (GIF `optimize=True`) berlaku untuk aset baru mulai Gerbang D. Aset A, B, dan C tidak diekspor ulang.

### Rancangan opsi D: GIF dibuat saat rilis (belum diimplementasikan)

GIF menyumbang sekitar 89% ukuran aset. Preview dan resolver hanya butuh `sheet` 1× dan manifest, jadi GIF bisa dibuat saat rilis, tidak disimpan di repo:

1. Repo menyimpan resep (`src/*.py`), sheet 1×, dan manifest. Field `gif` di manifest tetap ada, tetapi menunjuk ke berkas rilis.
2. Workflow rilis menjalankan `python3 src/export.py`, memverifikasi hash GIF aset terkunci terhadap daftar hash yang tersimpan, lalu mengunggah GIF sebagai aset rilis (pola yang sama dengan paket skill di repo Bertahan).
3. README memakai URL aset rilis, bukan path di repo.
4. Risiko: embed `raw.githubusercontent.com/.../main/gif/...` yang sudah beredar akan rusak kalau GIF dihapus dari `main`. Karena itu GIF lama tetap disimpan, dan hanya GIF baru yang pindah ke rilis.

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

**Disimpan tanpa mengubah schema:** di file sidecar `RUN_DIR/presentation.json`, bukan di `state.json`.

```json
{ "gobyet": { "domain": "greek-philosopher", "source": "auto", "score": 3, "matched": ["filsafat"],
              "rules_version": 1, "decided_at": "2026-01-01T00:00:00+00:00" } }
```

- **Tidak masuk integritas.** `abr.py verify` hanya meng-hash `fighters.jsonl`, `population.json`, `seeding.json`, `map.json`, `dossiers.json`, `rounds/`, dan laporan, jadi sidecar tidak memengaruhi hasil maupun pemeriksaan integritas.
- **Tidak dihitung ulang saat render.** Arena membaca nilai yang tersimpan, jadi replay menampilkan kostum yang sama seperti aslinya. Run lama tanpa sidecar tampil sebagai `normal`.
- **Override manual:** tulis `"source": "manual"` dengan kostum pilihan. Mekanisme resminya, misalnya satu perintah CLI, diputuskan saat integrasi.

## Nada

- Yang kalah tidak dihina. State `defeated` adalah reaksi Gobyet sendiri, misalnya menghela napas, bukan ejekan terhadap argumen yang kalah.
- `champion` berarti "klaim bertahan di bawah rubrik simulasi ini", bukan kebenaran objektif.
