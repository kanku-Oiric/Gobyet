# Acuan gaya Gobyet

Diturunkan dari rig di `src/monkey.py` dan dari aset yang sudah disetujui. Dipakai sebagai acuan konsistensi dan diperbarui tiap gerbang.

## Kanvas dan skala

- Kanvas 64×48 piksel, latar transparan.
- GIF ×8 (512×384). Sheet 1× wajib; sheet 4× hanya untuk aset lama.
- Tidak ada piksel semi-transparan dan tidak ada anti-aliasing. Warna hanya dari `PAL`, atau `PAL` + `PAL_EXT` untuk aset baru.

## Garis tepi dan cahaya

- Setiap bentuk digambar dengan `solid(cv, mask, fill, shade)`: isi, bayangan, lalu garis tepi 1 px `K` (cokelat sangat gelap) di tepi 4-arah bentuk itu.
- Pengecualian garis tepi:
  - Rambut dan janggut putih memakai `g` atau `h`.
  - Peluit memakai `l`.
  - Lensa memakai `g`.
  - Kepulan asap memakai `s`.
- **Cahaya dari kiri atas.** Bayangan jatuh di sisi kanan-bawah bentuk: `shade_off=(2, 2)` untuk badan dan kepala, `(1, 1)` untuk prop kecil dan telapak.
- Kilau: 1-2 piksel `W` di kiri atas benda mengilap (piala, medali, gelas).

## Tubuh (identitas terkunci)

- **Kepala `head(cv, cx, cy, ...)`:**
  - Tengkorak elips rx 9,6 × ry 8,4. Telinga di ±10,5, jadi kepala + telinga sekitar 28×17 px.
  - Mata putih 4×4 dengan pupil 2×2 di `cx ± 4`. Mulut di `cy + 4`.
- **Opsi ekspresi yang ada:**
  - `eyes`: look wide down side left blink happy angry relief.
  - `brows`: flat worried angry up raised.
  - `mouth`: frown flat smile smirk shout chew chomp o.
  - `face`: F (biasa) atau A (memerah).
- **Posisi baku kostum baru:** `CX, CY, TOP = 32, 14, 23` (pusat kepala dan puncak badan). Aset asli punya posisi sendiri; state baru mengikuti posisi aset aslinya:

  | Kostum | Posisi |
  |---|---|
  | Academic | CY+3, TOP+3 |
  | Greek Philosopher | cx 36, tiang di kiri |
  | Scientist | cx 21, papan tulis di kanan |
  | Hacker | cx 22, cy 16, badan elips, laptop di depan |
  | Detective | CX, CY, TOP |

- **Badan:** `sitting_body` (bulu) atau `dressed_body` (baju). Torso elips 8,2 × 7,2 di `top + 6,5`, dua paha, dan dua telapak kaki.
- **Lengan:** `arm(cv, bahu, tangan, elbow=siku, fur=warna_lengan)`, tebal r 1,8, telapak r 2,0. Lengan jubah lebar r 2,2. Bahu di `(CX ± 7, TOP + 3)`.
- **Ekor:** `tail()` keriting, digambar paling awal (di belakang badan).
- **Pose rebah (defeated):** `lying_body()` di `src/domains.py`. Badan menyamping ke kanan, kepala tetap menghadap kamera.

## Prop yang berhasil (ukuran di 1×, target heuristik ≥ 6×6)

| Kostum | Prop dan ukuran |
|---|---|
| Referee | peluit 9×8, papan klip 8×10 |
| Judge | palu 9×9, papan skor 9×12 (landasan 7×3 di bawah target) |
| Skeptic | monokel 8×14, stempel 7×9, kertas "?" 10×7 |
| Champion | piala 12×11, medali 7×7 |
| Greek | gulungan terbuka 10×11 |
| Academic | topi toga 21×10, ijazah terbuka 15×8, ijazah kusut 8×6 |
| Normal | pisang 6×17 |

Prop utama sebaiknya berada di luar siluet badan (samping bahu, di atas kepala, atau di lantai) supaya terbaca di 1×.

## Pola pose per state

| State | Pola |
|---|---|
| idle | Gerak halus. Kedip 1 frame (≈120 ms), melirik 2-3 frame, prop kostum terlihat jelas. |
| thinking | Tangan di dagu atau memeriksa prop. Gelembung `dots_or_mark()`: "…" bertambah, lalu satu glyph (`?`). Gelembung 11×9 di kanan atas. |
| victory | Lengan naik, prop terangkat, lompat 1 px di frame selang-seling, konfeti piksel atau kilau. |
| defeated | Lunglai atau rebah. Mata `relief`, alis `worried`, helaan napas `puff()`. Tidak brutal, tanpa simbol kematian. |
| shocked | `eyes=wide`, `brows=up`, `mouth=o`, mundur sedikit, efek kecil (`puff`, `spark_lines`, `!`). |
| attack | Metafora: menghentak atau menancapkan prop ke lantai atau ke kertas. Tidak pernah diarahkan ke karakter. |
| dance-* | Tepat 16 frame × 120 ms. Perubahan pose besar pada f0, f4, f8, f12. |

- Loop 12-20 frame.
- Seam: selisih frame terakhir ke frame pertama ≤ 1,25 × selisih antar-frame terbesar.
- Frame kunci = pose paling informatif. Untuk state non-idle, frame kunci harus jelas berbeda dari idle.

## Warna dominan per kostum (dari piksel kostum saja)

| Kostum | Dominan | Catatan |
|---|---|---|
| Normal | `B` bulu | tanpa kostum |
| Referee | `W` | sama dengan Academic (pengecualian yang diketahui) |
| Judge | `L` | |
| Skeptic | `v` | |
| Champion | `O` | |
| Greek | `c` | |
| Academic | `W` | |
| Scientist | `k` papan tulis, lalu `h` sweter | |
| Hacker | `q` | |
| Detective | `d` | |
| Mathematician | ungu `p`/`j` (PAL_EXT) | ΔE 48,6 dari dominan terdekat; lebih jauh dari `T` (33,2) |

Rencana gerbang berikutnya:
- Lawyer: jas biru gelap `J` (PAL_EXT).
- Wizard: biru baja (PAL_EXT).

## Teks

- Glyph `MINI` 5×5, jarak 6 px. Maksimal 3 karakter per gelembung.
- Pengecualian: papan `E=mc` (Scientist, statis) dan `GBLK` (normal-gblk).
