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
| Judge (victory, F) | timbangan emas kecil 13×12 |
| Skeptic (defeated/shocked/victory, F) | monokel tergantung di rantai, sapu tangan putih 4×4 |
| Champion (happy, F) | hati kecil 5×4 |
| Knight | pedang 4×15 (bilah bertepi `s` supaya kontras dengan latar krem; lebarnya di bawah target, panjangnya yang membuatnya terbaca), perisai layang-layang 9×11 dengan pita emas mendatar, helm terbuka 20×8, panji emas 8×5 (hanya di victory) |
| Viking | kapak 10×15, perisai bundar kayu 12×12, helm bertanduk 26×11 dengan pita kulit `D` |
| Pirate | cutlass 9×13 (bilah bertepi `s`), teropong 15×4 (tingginya di bawah target), tricorn 25×8, peti 20×8, koin 4×4 |
| Wizard | tongkat 7×27 dengan permata bersinar, topi runcing 25×12 berbintang, buku mantra 13×7 |
| Pak Haji | kopiah putih polos 18×6, tasbih kayu 9 butir 2×2 (untaian 8×8), koko putih `S` berkerah pendek, sarung kotak `V`/`v` |
| Priest | buku polos tertutup 9×7 (sampul `D`, tepi halaman `C`, tanpa tanda apa pun), kalung salib polos 3×4 (`y`) bertali cokelat `N` (bersama tali 6×5, sengaja kecil sesuai brief), kerah putih 6×2 |
| Knight-Heavy | pedang besar 6×19 (berdiri di sisi kanan, tidak di depan badan), pelindung bahu 8×6, lengan baja `G` |
| Knight-Archer | busur panjang 5×25, tabung panah 7×14 di bahu kiri, papan sasaran bulat 10×22 (attack dan victory) |
| Knight-Manatarms | halberd 6×30, gada 8×13 |
| Knight-Assassin | tudung dan jubah gelap `l`, belati 4×9, bom asap abu 4×6 di sabuk |
| Viking-Berserker | dua kapak, ikat kepala bulu 18×3 (tanpa helm), mantel bulu `c`, mata melebar |
| Viking-Huscarl | kapak besar 6×22, perisai bundar, baju zirah rantai `s` |
| Viking-Gestir | tombak lempar 3×29 (dipegang, tidak dilempar), rompi hijau `k` |
| Viking-Bondi | busur pendek 4×16, seax bersarung 7×4, rompi `d` |
| Pirate-Captain | topi kapten 28×9 berbulu merah, blunderbuss 7×18 (prop, tidak ditembakkan), burung beo 8×10 (victory) |
| Pirate-Skirmisher | bandana 25×9, kaus belang `W`/`R`, pedang lurus, tong mesiu 5×6 (tertutup, tanpa sumbu menyala), tali (victory) |
| Pirate-Sharpshooter | senapan panjang 11×26 (prop; tanpa kilatan atau asap laras), mantel `k` |
| Pirate-Buccaneer | palu besar 10×16, jangkar 14×15, dua sabuk kulit menyilang (aksesori besar, proporsi Gobyet tetap) |

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
| Pak Haji | hijau `V`, sarung kotak | piksel aura tidak dihitung (identik untuk keduanya). Sarung sengaja dipakai agak tinggi supaya hijau, bukan koko putih, yang dominan |
| Priest | abu `g`, jubah (bayangan `5`) | piksel aura tidak dihitung |

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
- **Aksen varian** (ΔE ≥ 10 dari saudara sefaksi) ditetapkan di Gerbang J. Aksen = warna dominan varian (piksel kostum idle, metode V6).

| Faksi | Varian dan aksen | ΔE terkecil antar saudara |
|---|---|---|
| Knight | Heavy baja `G`, Archer hijau `v`, Manatarms biru `J`, Assassin arang `l` | Manatarms–Assassin 25,4 |
| Viking | Berserker krem bulu `c`, Huscarl abu rantai `s`, Gestir hijau tua `k`, Bondi cokelat `d` | Berserker–Huscarl 20,1 |
| Pirate | Captain biru laut `w`, Skirmisher merah `R`, Sharpshooter hijau tua `k`, Buccaneer kulit `x` | Sharpshooter–Buccaneer 35,4 |

### Aura kostum teologi (Gerbang I)

- Aura digambar oleh satu fungsi, `theology.aura_mask(level, pulse, shimmer)`, di kanvas yang masih kosong, jadi selalu paling belakang.
- **Bentuk:** elips 19×13 berpusat di badan `(CX, TOP+7)`. Tepi atasnya di sekitar y 16-17, sejajar telinga, jauh di bawah puncak kepala. Tidak ada lingkaran di atas kepala, tidak ada sinar, tidak ada nyala.
- **Lapisan dithering:**
  - Luar: `C` 25%, atau 50% saat victory.
  - Tengah: `n` 50% dengan titik `O` saat happy dan victory.
  - Dalam: sebagian besar tertutup badan.
- **Level per state:**
  - idle 1, berdenyut ±1 px dalam 16 frame.
  - thinking 1.
  - happy 2.
  - victory 3.
  - defeated: 1, turun ke 0 (redup) di f4-f11, lalu kembali ke 1.
- Pak Haji dan Priest selalu memanggil aura dengan argumen yang sama untuk state dan frame yang sama. Validator `[VT]` (i) membuktikan mask-nya identik.

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
| Pak Haji | Aura menguat (lapisan luar lebih rapat) dengan titik emas yang bergeser pelan. Tanpa konfeti, tanpa lompat. Sama persis dengan Priest karena 7.2e | I |
| Priest | Sama persis dengan Pak Haji (7.2e) | I |
| Knight-Heavy | Tiap mendarat, kepulan debu besar menyembur di kedua sisi | J |
| Knight-Archer | Bintang emas berkedip di tengah papan sasaran di samping (tanpa anak panah) | J |
| Knight-Manatarms | Halberd diputar di atas kepala dengan jejak busur putaran | J |
| Knight-Assassin | Cincin asap berongga naik dan membesar dari bom asap | J |
| Viking-Berserker | Dua kapak diadu di atas kepala dengan percikan kilau di titik temu | J |
| Viking-Huscarl | Perisai dipukul gagang kapak, garis bunyi melengkung di sekitarnya | J |
| Viking-Gestir | Tombak diseimbangkan tegak di ujung jari dan bergoyang | J |
| Viking-Bondi | Tali busur dipetik, garis getar berganti sisi | J |
| Pirate-Captain | Burung beo terbang hinggap di bahu dan mengepakkan sayap | J |
| Pirate-Skirmisher | Bergelantung di tali dari atas dan berayun kiri-kanan | J |
| Pirate-Sharpshooter | Tricorn berputar di ujung laras senapan yang diangkat tegak | J |
| Pirate-Buccaneer | Jangkar diangkat satu tangan dengan garis tenaga | J |
| Referee | Lengan diangkat lurus sebagai isyarat akhir pertandingan, peluit ditiup dengan nada `n` yang naik. Tanpa lompat, tanpa konfeti (role netral) | F |
| Judge | Timbangan emas kecil diangkat, berayun lalu seimbang dan berkilau; palu terangkat. Tanpa lompat, tanpa konfeti | F |
| Skeptic | Monokel dilepas dan digosok sapu tangan putih di depan dada, stempel terangkat. Tanpa lompat, tanpa konfeti | F |

## Teks

- Glyph `MINI` 5×5, jarak 6 px. Maksimal 3 karakter per gelembung.
- Pengecualian: papan `E=mc` (Scientist, statis) dan `GBLK` (normal-gblk).

## Berserker Hero (Gerbang K, 128×96)

Karakter utama original: **zirah bukan Gobyet, wajah monyet Gobyet di dalam helm** (terlihat hanya saat topeng dibuka). Aturan di bagian lain dokumen ini (kanvas 64×48, `PAL`/`PAL_EXT`) berlaku untuk kostum lain; hero memakai aturan sendiri di bawah. Status: disetujui pemilik (perisai naga, `victory`, ekor), difinalisasi; aset dikunci di `pack/sha256-hero.txt`. Riwayat: v1 (kerangka naga di atas kepala Gobyet) dan v2 (Gobyet berzirah hitam-merah) ditolak sebagai gaya, lalu disimpan sebagai evolusi 1 dan 2 (`pack/evolusi/`); v3 ini dirombak total dari dua gambar rujukan pemilik dan satu gambar perisai (tidak disimpan di repo; bentuk diturunkan, bukan disalin piksel).

- **Kanvas:** 128×96, latar transparan, GIF ×4 (512×384), hanya sheet 1×. Kanvas dicatat per sel di manifest (`canvas`, `gif_scale`); 64×48 tidak berubah.
- **Palet lokal:** besi hitam `n0..n4` (garis tepi, bayangan, dasar, terang, baja), merah darah `q0..q4`, inti cahaya `wh` (11 kunci karakter); wajah Gobyet di balik topeng memakai kunci `PAL` asli `B b F f M` (bulu, wajah krem, hidung dan mulut; garis tepi, pupil, dan putih mata memakai `n0` dan `wh`); efek dan properti: batu `s1..s3`, kayu `w1..w3`, darah monster merah darah gelap `m1..m3`. Total seluruh karakter 25 warna (batas 28). Tiga nada dari cahaya kiri-atas, sama di semua frame; tanpa piksel semi-transparan, tanpa anti-aliasing, tanpa teks. Rim light 1 px (`n3`/`n4`) di tepi atas bagian besi.
- **Tepi terang (keputusan pemilik: halo dan tepi terang):** setiap piksel kosong yang bersebelahan (4 arah) dengan piksel karakter gelap (`n0 n1 n2 q0 q1`) diisi `n4`, setelah efek digambar; efek dan properti tidak diberi tepi. Tanpa warna baru. Kontras `n4` terhadap latar gelap `#181c2c` 4,40:1 (garis hitam sendiri 1,15:1).
- **Identitas:** zirah, helm, dan badan bukan Gobyet. Wajah monyet Gobyet (`monkey.head` asli, skala 1) hanya ada di balik topeng; V11 menolak kunci atau bagian Gobyet v1/v2 di mana pun, warna wajah Gobyet di luar wajah, dan wajah yang terlihat saat topeng tertutup. Ekspresi sehari-hari dibawa visor: lengan salib merah (`look`, `angry`, `rage`, `wide`, `glare`, `dim`, `tired`, `shut`, `x`), alis V yang selalu terlihat, dan grill mulut (tertutup atau terbuka bercahaya); ekspresi wajah Gobyet diturunkan dari ekspresi visor bila tidak ditentukan per frame.
- **Desain:** helm penuh besi hitam (kubah dengan plat sensor, garis V merah di atas pelat wajah, salib merah menyala di visor, sayap helm di sisi depan, cakram telinga mekanis, rahang meruncing dengan grill), jambul bilah merah gelap menyapu ke belakang, **perisai naga** di bahu kiri layar (bentuk dari gambar perisai pemilik: ujung tombak di atas, dua tanduk, mata naga bercelah tegak sebagai permata, alis dan chevron merah, sisik di bagian bawah dengan tepi bawah merah menyala, dua sayap naga bertulang tiga jari dengan selaput merah gelap bergerigi; ±43×69 px, sayap kanan sebagian tertutup helm), pelindung bahu bulat di kanan, dada berbingkai merah, perut sisik heksagonal merah darah, sepatu besar bercakar, ekor beruas berujung kipas panah merah, dan pedang agung hitam lebar 19 px dengan tepi api merah bergelombang. Proporsi chibi: kepala + jambul ≈ 60% tinggi badan. "Merah darah" hanya warna dan corak.
- **Topeng buka-tutup (`victory`):** pelat wajah terbelah dua di sumbu helm; tiap pintu meluncur ke samping (0-10 px) dan tersembunyi di sisi helm, memperlihatkan wajah monyet Gobyet (bulu cokelat, wajah krem, mata besar; tersenyum di puncak bukaan) di dalam ruang helm yang gelap.
- **Darah monster (`victory`):** gumpalan merah darah gelap dengan kilau basah di bilah (lebih gelap dari api bilah supaya terbaca), dihapus bertahap oleh sapuan kepalan dari pelindung ke ujung; hanya ada di state ini.
- **Ekor:** batang besi hitam beruas (jari-jari 4,2 → 1,8 px) dengan lima cincin merah, keluar dari pinggang belakang, turun ke dekat lantai di belakang kaki, lalu melengkung naik di kiri bawah (di bawah sayap perisai, di kiri ujung bawah perisai); ujungnya kipas tiga panah (tengah menyala, dua samping lebih gelap) yang menempel di batang. Bergoyang naik-turun mengikuti `tail_phase` (3 px; run 7 px). Ukuran per state di `hero3_scenes.TAIL` (k panjang, rot sudut angkat); di state serangan sedang (35-80% ekor idle di frame tumbukan, keputusan pemilik), di `rage` terangkat mengikuti amarah.
- **Amarah (`rage`):** `heat` menaikkan semua merah badan satu tingkat, jambul dan ekor mengembang (`flare`), visor putih-merah, bara dan garis kejut; state lain tidak memakainya.
- **Animasi:** setiap serangan punya antisipasi, aksi, dan tindak lanjut; satu sampai dua frame smear dan satu frame tumbukan yang ditahan lebih lama dengan serpihan dan debu. Durasi per frame tidak seragam; pose kunci ditahan lebih lama; timing dan urutan beat mengikuti hero v1 yang pernah dilihat pemilik. Run: kontak, serap, lintas, dorong, melayang; debu tiap injakan; garis kecepatan. `rage` dan `victory` tidak berputar dan menahan frame terakhir 1500 ms.
