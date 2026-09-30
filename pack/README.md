# Gobyet Character Pack

Kostum menentukan **siapa** Gobyet. State menentukan **sedang apa** dia.
Folder ini berisi sistemnya:

| File | Isi |
|---|---|
| `manifest.json` | Peta kostum × state ke asset, dengan ukuran kanvas, jumlah frame, durasi per frame, loop, dan frame kunci. **Dibangkitkan** oleh `python3 src/export.py` dari `src/pack.py`; jangan diedit tangan. |
| `resolver.js` | `resolve(manifest, kostum, state)` dengan fallback berantai. Tanpa dependensi, jalan di browser (`window.GobyetPack`) dan Node (`require`). |
| `resolver.test.js` | Uji resolver dan manifest, termasuk ukuran PNG dan GIF setiap aset. Jalankan `node --test pack/resolver.test.js`. |
| `preview.html` | Matriks 12 kostum × 9 state, panel banding gaya 1× dan 4×, dan tes buta (idle 1× tanpa label, urutan acak dengan seed tetap). Buka lewat server: `python3 -m http.server` di akar repo, lalu `/pack/preview.html`. |

## Kostum dan state

- **CORE:** `normal`
- **ROLE:** `referee`, `judge`, `skeptic`, `champion`
- **DOMAIN:** `greek-philosopher`, `academic`, `scientist`, `mathematician`, `lawyer`, `hacker`, `detective`

State wajib untuk semua kostum: `idle`, `thinking`, `victory`, `defeated`.

State opsional:

| State | Berlaku untuk |
|---|---|
| `judging` | `judge` saja |
| `suspicious` | `skeptic` saja |
| `attack` | `skeptic` saja |
| `shocked` | semua kostum |
| `happy` | semua kostum |

Kostum tidak wajib punya semua state; fallback yang menutupinya.

## Resolver

```js
const r = GobyetPack.resolve(manifest, "hacker", "victory");
// r.kind:     "exact" | "fallback" | "placeholder"
// r.step:     "costume+state" | "costume+idle" | "normal+state" | "normal+idle" | "placeholder"
// r.resolved: { costume, state } atau null
// r.cell:     { sheet, gif, frames, durations_ms, loop, keyframe, ... } atau null
// r.tried:    ["hacker/victory", "hacker/idle"]
```

Urutan fallback: **kostum+state → kostum+idle → normal+state → normal+idle → placeholder CSS**.

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
python3 src/validate_pack.py --gate C    # hash, palet, kanvas, seam loop, IoU siluet, ukuran, teks, prop, beat, warna
node --test pack/resolver.test.js        # resolver dan manifest
```

- `pack/sha256-asli.txt` mengunci 27 file `gif/` dan `sheets/` yang ada sebelum Fase 2.
- `pack/sha256-disetujui.txt` mengunci aset baru yang gayanya sudah disetujui pemilik (saat ini Gerbang A).
- Validator keluar dengan kode 1 bila ada hash berubah, warna di luar `PAL`, piksel semi-transparan, ukuran salah, atau seam loop aset baru melebihi ambang.
- Ambang seam loop = 1,25 × selisih piksel terbesar antar-frame berurutan di aset itu sendiri. Aset yang terkunci hash dan melewati ambang dilaporkan **DIKETAHUI**, bukan GAGAL, karena tidak boleh diubah.
- Jarak warna dominan antar-kostum dihitung sebagai CIE76 ΔE di ruang Lab, setelah warna bulu, kulit, dan garis tepi yang sama di semua kostum dikeluarkan.

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
