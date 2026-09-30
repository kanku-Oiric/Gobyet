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
- **Ekor:** `tail()` keriting, digambar paling awal (di belakang badan). Mulai Gerbang H, fase ekor memakai `wag(t, n)` (`src/fantasy.py`): satu putaran penuh per n frame, jadi frame terakhir menyambung mulus ke frame 0. Aset lama tidak diubah.
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
| Scientist | papan tulis asli 29×16 (statis, `E=mc`), kapur 2×2 |
| Mathematician | batu tulis 11×9, jangka 7×9 (diputar di samping bahu supaya di luar siluet) |
| Detective | kaca pembesar asli 12×13; saat suspicious di depan mata dengan mata menyipit |
| Lawyer | map tertutup 10×9, map terbuka 16×8, dasi hitam 2×8 (prop sekunder, di bawah target) |
| Gamer | gamepad 14×6, headset 26×19 (cincin di kepala = siluet pembeda dari Hacker), kaleng 4×6 (prop sekunder, hanya di idle) |
| Normal-GBLK | papan GBLK 27×11 bertongkat, teks 23×5 kontras tinggi (K di atas `n`) |
| Knight | pedang 4×15 (bilah bertepi `s` supaya kontras dengan latar krem; lebarnya di bawah target, panjangnya yang membuatnya terbaca), perisai layang-layang 9×11 dengan pita emas mendatar, helm terbuka 20×8, panji emas 8×5 (hanya di victory) |
| Viking | kapak 10×15, perisai bundar kayu 12×12, helm bertanduk 26×11 dengan pita kulit `D` |
| Pirate | cutlass 9×13 (bilah bertepi `s`), teropong 15×4 (tingginya di bawah target), tricorn 25×8, peti 20×8, koin 4×4 |
| Wizard | tongkat 7×27 dengan permata bersinar, topi runcing 25×12 berbintang, buku mantra 13×7 |

Prop utama sebaiknya berada di luar siluet badan (samping bahu, di atas kepala, atau di lantai) supaya terbaca di 1×. Contoh: idle Mathematician versi pertama (batu tulis dan jangka di pangkuan) memberi IoU 0,90 dengan Referee. Setelah jangka dipindah ke samping bahu, IoU-nya turun ke 0,84.

## Pola pose per state

| State | Pola |
|---|---|
| idle | Gerak halus. Kedip 1 frame (≈120 ms), melirik 2-3 frame, prop kostum terlihat jelas. |
| thinking | Tangan di dagu atau memeriksa prop. Gelembung `dots_or_mark()`: "…" bertambah, lalu satu glyph (`?`). Gelembung 11×9 di kanan atas. |
| victory | Lengan naik, prop terangkat, lompat 1 px di frame selang-seling, konfeti piksel atau kilau. |
| defeated | Lunglai atau rebah. Mata `relief`, alis `worried`, helaan napas `puff()`. Tidak brutal, tanpa simbol kematian. |
| shocked | `eyes=wide`, `brows=up`, `mouth=o`, mundur sedikit, efek kecil (`puff`, `spark_lines`, `!`). |
| attack | Metafora: menghentak atau menancapkan prop ke lantai atau ke kertas. Tidak pernah diarahkan ke karakter. |
| dance-* | Tepat 16 frame × 120 ms. Perubahan pose besar pada f0, f4, f8, f12; di dalam beat hanya ekor yang bergerak halus. Badan duduk bergoyang, meniru cara `kondangan` (tanpa badan berdiri). Papan atau prop tidak boleh keluar dari kanvas di frame mana pun. |

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
| Lawyer | biru jas `J` (40,56,104) (PAL_EXT) | ΔE 25,6 dari Hacker, 30,3 dari Judge, 67,1 dari Detective |
| Gamer | oranye `o` (PAL_EXT), kaus | 38% piksel kostum |
| Normal-GBLK | krem-kuning `n`, papan | 84%; ΔE 23,1 dari Greek |
| Knight | merah tua `z` (PAL_EXT), tabard | 36%. Lengan zirah rantai `s` dan tabard selebar badan supaya baja `G` tidak dominan (versi pertama: `G` 40%, ΔE 13,4 dari Referee/Academic). ΔE 24,9 dari Pirate |
| Viking | cokelat tua `D`, rompi tertutup dan pita helm | 33%. Versi pertama: helm abu `s` dominan |
| Pirate | marun `i` (PAL_EXT), mantel | 44%; ΔE 24,9 dari Knight |
| Wizard | biru kerajaan `3` (PAL_EXT), jubah | 68% |

### Alokasi warna global (sebelum Gerbang G)

Dicari lewat kombinasi yang memaksimalkan ΔE minimum terhadap 12 dominan yang ada dan antar-kostum baru. ΔE minimum yang tercapai: 23,1.

| Kostum | Dominan | Kunci | Terdekat |
|---|---|---|---|
| Gamer | oranye (238,142,52), kaus | `o`/`t` (PAL_EXT) | Champion ΔE 34,8 |
| Normal-GBLK | krem-kuning `n`, papan | PAL | Greek ΔE 23,1 |
| Knight | merah tua (164,32,40), tabard | `z`/`1` (PAL_EXT) | Pirate ΔE 24,9 |
| Viking | cokelat tua `D`, rompi kulit | PAL | Normal ΔE 25,2 |
| Pirate | marun (122,32,52), mantel | `i`/`2` (PAL_EXT) | Knight ΔE 24,9 |
| Wizard | biru kerajaan (66,110,220), jubah | `3`/`4` (PAL_EXT) | Mathematician ΔE 29,9 |
| Pak Haji | hijau `V`, sarung kotak `V`/`v` (koko krem `C`) | PAL | Skeptic ΔE 23,8 |
| Priest | abu `g`, jubah (bayangan `5`) | PAL + `5` | Greek ΔE 30,1 |

- **Wizard, tiga kandidat:** kobalt (40,84,196) ΔE 25,8; **biru kerajaan (66,110,220) ΔE 29,9, dipilih**; indigo terang (92,80,200) ΔE 23,8. Cadangan teal tua (20,100,110) ΔE 20,5.
- **Pak Haji:** koko putih atau krem selalu < 15 dari Academic (`C` 11,2; `S`, `H`, `m` < 7). Karena itu warna dominannya harus sarung hijau: sarung dibuat lebih luas daripada koko.
- **Priest:** jubah abu (bukan hitam) supaya jauh dari Judge `L`.
- **Aksen varian** (ΔE ≥ 10 dari saudara sefaksi) ditetapkan di Gerbang J dan dicatat di bawah.

## Aksi khas victory

Setiap victory baru wajib punya minimal satu elemen yang belum dipakai kostum lain, selain pola "lengan naik + prop naik + lompat 1 px". Tabel ini diperbarui tiap gerbang.

| Kostum | Aksi khas victory | Gerbang |
|---|---|---|
| Champion | Piala diangkat dengan konfeti piksel (konfeti pertama) | B |
| Greek Philosopher | Gulungan dibuka menjuntai dari rol di atas kepala | C |
| Academic | Topi toga dilempar berputar melambung, lalu ditangkap | C |
| Normal | Pisang diangkat seperti piala | C |
| Scientist | Menulis "!" di papan tulis, lidah menjulur | D |
| Mathematician | Menggoreskan centang `v` di batu tulis lalu mengangkatnya | D |
| Hacker | Semua baris terminal berubah hijau, gelembung "OK" | E |
| Detective | Kilau berpindah di lensa kaca pembesar | E |
| Lawyer | Map diangkat. Tidak ada elemen khas di luar pola dasar (dicatat; aset E tidak direvisi) | E |
| Gamer | Gamepad bergetar (garis getar di kedua sisi) dan gelembung "GG" | G |
| Normal-GBLK | Tulisan papan berkedip merah dan gelap bergantian | G |
| Knight | Panji emas kecil berkibar di ujung pedang. Kilau yang menyapu bilah diminta brief, tetapi kilau berpindah sudah dipakai Detective, jadi tidak dihitung sebagai elemen khas | H |
| Viking | Garis teriakan dari mulut yang terbuka lebar, gelembung "!" | H |
| Pirate | Koin emas memercik lalu jatuh. Lempar topi diminta brief, tetapi mirip lempar toga Academic, jadi tidak dihitung sebagai elemen khas | H |
| Wizard | Hujan bintang emas dari tongkat yang terangkat | H |

## Teks

- Glyph `MINI` 5×5, jarak 6 px. Maksimal 3 karakter per gelembung.
- Pengecualian: papan `E=mc` (Scientist, statis) dan `GBLK` (normal-gblk).
