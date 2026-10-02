<p align="center">
  <img src="gif/ngopi-santai.gif" width="384" alt="Gobyet memegang mug kopi, menggaruk kepala sambil melirik laptop, lalu menyeruput kopi">
</p>

<h1 align="center">Gobyet</h1>

<p align="center">
  <b>Goblok monyet.</b> Maskot dari semua project saya: dikerjakan buat have fun,<br>
  oleh monyet bodoh yang lagi larping jadi programmer.
</p>

## Gobyet Universe

Satu monyet, banyak dunia. Rework v2 membuat setiap karakter Gobyet berdiri dengan kuda-kuda, senjata, dan siluet sesuai perannya, sementara kepala, wajah, telinga, dan ekornya tetap Gobyet yang sama.

**39 karakter · 328 state animasi · 4.165 frame · kanvas 64×64 (Berserker 144×100) · 13 sprite VFX**

### Animasi andalan

| Heavy Knight | Viking Berserker | Pirate Skirmisher | Wizard |
|:---:|:---:|:---:|:---:|
| <img src="v2/gif/knight-heavy/attack.gif" width="128" alt="Heavy Knight: ancang-ancang, ayunan pedang besar, hantaman"> | <img src="v2/gif/viking-berserker/rage.gif" width="128" alt="Viking Berserker: mode amuk: lebih rendah, wajah memerah, kapak terangkat, lebih cepat"> | <img src="v2/gif/pirate-skirmisher/explosion.gif" width="128" alt="Pirate Skirmisher: tong meledak kartun, menutup telinga"> | <img src="v2/gif/wizard/spell_fail.gif" width="128" alt="Wizard: mantra gagal: POOF, wajah jelaga, bingung"> |
| `attack` | `rage` | `explosion` | `spell_fail` |

| Hacker | Skeptic | Normal GBLK | Champion |
|:---:|:---:|:---:|:---:|
| <img src="v2/gif/hacker/error.gif" width="128" alt="Hacker: layar error, menatap layar, diam, lalu menatap penonton"> | <img src="v2/gif/skeptic/inspect.gif" width="128" alt="Skeptic: melihat klaim, diam, menyipit, menunjuk premis"> | <img src="v2/gif/normal-gblk/victory_dance.gif" width="128" alt="Normal GBLK: tarian kemenangan dengan konfeti"> | <img src="v2/gif/champion/trophy_raise.gif" width="128" alt="Champion: piala diangkat tinggi dengan dua tangan"> |
| `error` | `inspect` | `victory_dance` | `trophy_raise` |

### Berserker: pedang raksasa (dark fantasy)

Pendekar berzirah hitam dengan pedang dua tangan selebar papan (1,4× tinggi badan). Desain orisinal dari
arketipe umum, dengan kepala dan badan Gobyet berskala sama seperti karakter lain; kanvasnya saja yang 144×100.
Ada 23 state (17 dari brief, 5 varian idle, 1 varian attack), tempo per frame, event `hit`/`hitstop`/`screen_shake`,
lapisan karakter/senjata/VFX, dan tiga tingkat kerusakan zirah. Darah hanya muncul sebagai sprite VFX terpisah yang
bergaya piksel, singkat, dan muncul hanya saat serangan kena.

| `leap_spin_slash` (jurus khas) | konfirmasi kena |
|:---:|:---:|
| <img src="v2/gif/berserker/leap_spin_slash.gif" width="288" alt="Berserker: jongkok, isi tenaga, melompat, salto 360 dengan tebasan bulan sabit, menghantam tanah sampai retak dan puing beterbangan, lalu pulih"> | <img src="v2/preview/berserker-leap_spin_slash-hit.gif" width="288" alt="Berserker menghantam Fantasy Knight: kilat hantaman, jeda hit-stop, darah bergaya kecil, lawan terdorong, percikan, debu"> |

| `idle` | `rage_attack` | `miss` | `defeat` |
|:---:|:---:|:---:|:---:|
| <img src="v2/gif/berserker/idle.gif" width="192" alt="Berserker jongkok condong ke depan, ujung pedang raksasa bertumpu di lantai"> | <img src="v2/gif/berserker/rage_attack.gif" width="192" alt="Berserker amuk: meledak maju, sabetan rendah, sabetan naik, putaran gasing, tebasan berat"> | <img src="v2/gif/berserker/miss.gif" width="192" alt="Berserker meleset: pedang tertancap, ditarik-tarik, menatap pedang lalu menatap penonton"> | <img src="v2/gif/berserker/defeat.gif" width="192" alt="Berserker: pedang terlalu berat dan jatuh, duduk, menyalahkan pedang"> |

### FANTASY (18)

| Heavy Knight | Archer | Man-at-Arms | Assassin |
|:---:|:---:|:---:|:---:|
| <img src="v2/gif/knight-heavy/idle.gif" width="128" alt="Heavy Knight: berdiri berat, zirah naik-turun pelan"> | <img src="v2/gif/knight-archer/idle.gif" width="128" alt="Archer: busur panjang di sisi, tabung panah di punggung"> | <img src="v2/gif/knight-man-at-arms/idle.gif" width="128" alt="Man-at-Arms: halberd tegak, berat badan berpindah"> | <img src="v2/gif/knight-assassin/idle.gif" width="128" alt="Assassin: kuda-kuda rendah, dua belati terbalik"> |

| Fantasy Knight | Viking | Viking Berserker | Huscarl |
|:---:|:---:|:---:|:---:|
| <img src="v2/gif/fantasy-knight/idle.gif" width="128" alt="Fantasy Knight: pedang panjang, perisai layang-layang biru, jubah biru"> | <img src="v2/gif/viking/idle.gif" width="128" alt="Viking: kapak dan perisai bundar"> | <img src="v2/gif/viking-berserker/idle.gif" width="128" alt="Viking Berserker: memantul tak sabar, dua kapak siap"> | <img src="v2/gif/viking-huscarl/idle.gif" width="128" alt="Huscarl: kapak Dane besar dan perisai bundar besar"> |

| Gestir | Bondi | Fantasy Viking | Pirate Captain |
|:---:|:---:|:---:|:---:|
| <img src="v2/gif/viking-gestir/idle.gif" width="128" alt="Gestir: tombak panjang tegak, lembing di punggung"> | <img src="v2/gif/viking-bondi/idle.gif" width="128" alt="Bondi: busur pendek, seax di sabuk, pakaian sederhana"> | <img src="v2/gif/fantasy-viking/idle.gif" width="128" alt="Fantasy Viking: kapak dan perisai bundar"> | <img src="v2/gif/pirate-captain/idle.gif" width="128" alt="Pirate Captain: dada membusung, cutlass dan pistol"> |

| Pirate Skirmisher | Pirate Sharpshooter | Pirate Buccaneer | Fantasy Pirate |
|:---:|:---:|:---:|:---:|
| <img src="v2/gif/pirate-skirmisher/idle.gif" width="128" alt="Pirate Skirmisher: memantul ringan, tong mesiu di tangan"> | <img src="v2/gif/pirate-sharpshooter/idle.gif" width="128" alt="Pirate Sharpshooter: senapan panjang di bahu, topi lebar"> | <img src="v2/gif/pirate-buccaneer/idle.gif" width="128" alt="Pirate Buccaneer: bertumpu pada palu raksasa, jangkar di punggung"> | <img src="v2/gif/fantasy-pirate/idle.gif" width="128" alt="Fantasy Pirate: peta harta, sesekali meneropong"> |

| Wizard |
|:---:|
| <img src="v2/gif/wizard/idle.gif" width="128" alt="Wizard: topi runcing tinggi, jubah sampai lantai, tongkat bercahaya"> |

### DOMAIN (15)

| Philosopher | Academic | Scientist | Mathematician |
|:---:|:---:|:---:|:---:|
| <img src="v2/gif/philosopher/idle.gif" width="128" alt="Philosopher: gulungan di tangan, toga"> | <img src="v2/gif/academic/idle.gif" width="128" alt="Academic: toga hitam, buku tebal"> | <img src="v2/gif/scientist/idle.gif" width="128" alt="Scientist: jas lab panjang, labu bergelembung, papan klip"> | <img src="v2/gif/mathematician/idle.gif" width="128" alt="Mathematician: papan tulis berkaki dengan rumus di samping"> |

| Lawyer | Historian | Economist | Psychologist |
|:---:|:---:|:---:|:---:|
| <img src="v2/gif/lawyer/idle.gif" width="128" alt="Lawyer: jas gelap, kitab hukum, berkas"> | <img src="v2/gif/historian/idle.gif" width="128" alt="Historian: jaket wol, kacamata bundar, kotak arsip"> | <img src="v2/gif/economist/idle.gif" width="128" alt="Economist: pelindung mata hijau, kalkulator, buku besar, grafik"> | <img src="v2/gif/psychologist/idle.gif" width="128" alt="Psychologist: duduk di kursi berlengan, kardigan, kacamata besar, buku catatan"> |

| Sociologist | Engineer | Detective | Researcher |
|:---:|:---:|:---:|:---:|
| <img src="v2/gif/sociologist/idle.gif" width="128" alt="Sociologist: papan diagram jaringan, papan klip, syal"> | <img src="v2/gif/engineer/idle.gif" width="128" alt="Engineer: helm proyek, rompi oranye, kunci pas"> | <img src="v2/gif/detective/idle.gif" width="128" alt="Detective: topi deerstalker, mantel berjubah, kaca pembesar"> | <img src="v2/gif/researcher/idle.gif" width="128" alt="Researcher: memeluk tumpukan buku"> |

| Pak Haji | Priest | Hacker |
|:---:|:---:|:---:|
| <img src="v2/gif/pak-haji/idle.gif" width="128" alt="Pak Haji: tenang, aura halus"> | <img src="v2/gif/priest/idle.gif" width="128" alt="Priest: tenang, aura halus"> | <img src="v2/gif/hacker/idle.gif" width="128" alt="Hacker: hoodie, laptop, terminal hijau bergulir"> |

### ROLE (5)

| Referee | Judge | Skeptic | Champion |
|:---:|:---:|:---:|:---:|
| <img src="v2/gif/referee/idle.gif" width="128" alt="Referee: kaus belang, peluit, bendera"> | <img src="v2/gif/judge/idle.gif" width="128" alt="Judge: jubah hakim di balik meja"> | <img src="v2/gif/skeptic/idle.gif" width="128" alt="Skeptic: alis terangkat, monokel, kaca pembesar"> | <img src="v2/gif/champion/idle.gif" width="128" alt="Champion: memamerkan piala, jubah merah, medali"> |

| Defeated |
|:---:|
| <img src="v2/gif/defeated/sit.gif" width="128" alt="Defeated: duduk lesu, pedang di lantai, menghela napas"> |

### SPECIAL (1)

| Normal GBLK |
|:---:|
| <img src="v2/gif/normal-gblk/idle.gif" width="128" alt="Normal GBLK: papan GBLK besar"> |

Aset v1 di bawah (animasi asli dan character pack Fase 2) tidak diubah oleh v2. Detail v2: [`v2/README.md`](v2/README.md), tata bahasa visual [`v2/STYLE.md`](v2/STYLE.md), laporan [`v2/reports/rework-v2.md`](v2/reports/rework-v2.md). Galeri interaktif (semua state, mode siluet dan grayscale, uji skala) ada di [`v2/gallery.html`](v2/gallery.html); buka dari folder `v2/` di komputer.

## Animasi

| Makan pisang | Ngamuk debug | Ngopi santai |
|:---:|:---:|:---:|
| <img src="gif/makan-pisang.gif" width="256" alt="Gobyet duduk makan pisang, mengunyah, lalu garuk pantat dengan lega"> | <img src="gif/marah-debug.gif" width="256" alt="Gobyet mengetik, error muncul, lalu membanting laptop sambil mengumpat"> | <img src="gif/ngopi-santai.gif" width="256" alt="Gobyet ngopi sambil garuk kepala dan melirik laptop"> |
| Tiga gigitan sampai kulitnya terkulai, mengunyah dengan mata `^ ^`, lalu garuk pantat dengan lega. | Mengetik tenang, error merah muncul, muka memerah, laptop dibanting, telinga berasap, lalu menghela napas. | Pose aslinya: garuk kepala, melirik laptop, berkedip, lalu menyeruput kopi. |

Semua GIF transparan, 512×384, dan berulang terus, jadi aman di tema terang maupun gelap.

## Kostum

| Wisuda | Filsuf Yunani | Rambut Einstein |
|:---:|:---:|:---:|
| <img src="gif/wisuda.gif" width="256" alt="Gobyet pakai topi toga, kemeja, dan dasi merah, memegang ijazah lalu melempar topinya"> | <img src="gif/filsuf-yunani.gif" width="256" alt="Gobyet berjanggut putih, bermahkota daun zaitun dan berkain toga di samping pilar, mengelus janggut lalu menemukan ide"> | <img src="gif/rambut-einstein.gif" width="256" alt="Gobyet berambut putih awut-awutan menulis E=mc² di papan tulis lalu menjulurkan lidah"> |
| Topi toga, kemeja, dasi merah. Pegang ijazah, lalu lempar topi sambil konfeti. | Janggut putih, mahkota zaitun, kain toga di samping pilar. Mengelus janggut, `...`, `?`, lalu `!`. | Rambut putih awut-awutan dan kumis tebal. Menulis E=mc², lalu menjulurkan lidah. |

| Hacker | Detektif bug | Kondangan |
|:---:|:---:|:---:|
| <img src="gif/hacker.gif" width="256" alt="Gobyet berhoodie dan kacamata hitam mengetik di laptop dengan terminal hijau di belakangnya"> | <img src="gif/detektif-bug.gif" width="256" alt="Gobyet bertopi detektif menyapu lantai dengan kaca pembesar sampai menemukan bug"> | <img src="gif/kondangan.gif" width="256" alt="Gobyet berpeci dan berbatik joget sambil mengangkat tangan bergantian"> |
| Hoodie dan kacamata hitam, terminal hijau bergulir, lalu `OK`. | Topi detektif dan kaca pembesar. Bug merayap, ketemu, matanya membesar di balik lensa. | Peci dan batik, joget kiri-kanan diiringi not musik. |

## Character pack

Sistem kostum × state untuk dipakai di aplikasi (misalnya arena Battle Royale Argumen) ada di [`pack/`](pack):

- `manifest.json`: peta kostum × state.
- `resolver.js`: resolver dengan fallback berantai.
- `preview.html`: matriks semua kostum × state, panel banding gaya, dan tes buta. Placeholder ditandai jelas.

Detailnya di [`pack/README.md`](pack/README.md).

### Update: Fase 2, aset per gerbang

Aset baru dibuat bertahap per gerbang. Urutan kerjanya A, B, C, D, E, G, H, I, J, F. Status terkini ada di [`pack/PROGRESS.md`](pack/PROGRESS.md).

| Gerbang | Isi | Status |
|---|---|---|
| A | Referee: idle, thinking | disetujui |
| B | Judge: idle, thinking, judging · Skeptic: idle, suspicious, attack · Champion: idle, victory (laurel emas diganti medali) | disetujui |
| C | Greek Philosopher: idle, victory, defeated · Academic: thinking, victory, defeated · Normal: thinking, victory, defeated | disetujui |
| D | Scientist: idle, shocked, victory · Mathematician: idle, thinking, victory | disetujui |
| E | Hacker: thinking, shocked, victory · Detective: idle, suspicious, shocked, victory · Lawyer: idle, thinking, victory | disetujui |
| G | Gamer (7 state), Normal-GBLK (8 state) | dibuat, validasi lulus, menunggu persetujuan akhir |
| H | Knight, Viking, Pirate, Wizard (masing-masing 6 state, termasuk 2 tarian) | dibuat, validasi lulus, menunggu persetujuan akhir |
| I | Pak Haji, Priest (masing-masing idle, thinking, happy, victory, defeated; perlakuan dan aura identik, aturan 7.2) | dibuat, validasi lulus, menunggu persetujuan akhir |
| J | 12 varian kelas Knight, Viking, Pirate (masing-masing idle, attack, victory) | dibuat, validasi lulus, menunggu persetujuan akhir |
| F | Sisa sel 12 kostum lama (14 wajib + 22 opsional), dokumentasi | dibuat, validasi lulus, menunggu persetujuan akhir |

Semua 163 sel yang berlaku terisi: 7 aset asli dan 156 aset baru. Laporan akhir Fase 2: [`pack/reports/final.md`](pack/reports/final.md).

**Kostum peran (idle)**

| Referee | Judge | Skeptic | Champion |
|:---:|:---:|:---:|:---:|
| <img src="gif/referee-idle.gif" width="192" alt="Gobyet berkaus wasit bergaris dengan peluit, tangan di pinggang, menoleh kiri-kanan"> | <img src="gif/judge-idle.gif" width="192" alt="Gobyet berjubah hakim hitam memegang palu di samping landasan"> | <img src="gif/skeptic-idle.gif" width="192" alt="Gobyet bersweter hijau dan bermonokel emas, bersedekap dengan satu alis naik"> | <img src="gif/champion-idle.gif" width="192" alt="Gobyet berselempang merah dengan medali emas, memamerkan piala"> |
| juga: `thinking` | juga: `thinking`, `judging` | juga: `suspicious`, `attack` | juga: `victory` |

**Gerbang C**

| | idle / thinking | victory | defeated |
|---|:---:|:---:|:---:|
| Greek Philosopher | <img src="gif/greek-philosopher-idle.gif" width="192" alt="Filsuf Gobyet mengelus janggut sambil membawa gulungan"> | <img src="gif/greek-philosopher-victory.gif" width="192" alt="Filsuf Gobyet mengangkat gulungan yang terbuka sambil melompat kecil"> | <img src="gif/greek-philosopher-defeated.gif" width="192" alt="Filsuf Gobyet rebah, gulungannya menggelinding menjauh"> |
| Academic | <img src="gif/academic-thinking.gif" width="192" alt="Gobyet bertopi toga membaca ijazah lalu memegang dagu"> | <img src="gif/academic-victory.gif" width="192" alt="Gobyet melempar topi toga tinggi-tinggi lalu menangkapnya lagi"> | <img src="gif/academic-defeated.gif" width="192" alt="Gobyet bertopi toga miring duduk lunglai memegang ijazah kusut"> |
| Normal | <img src="gif/normal-thinking.gif" width="192" alt="Gobyet menggaruk kepala dengan gelembung tanda tanya"> | <img src="gif/normal-victory.gif" width="192" alt="Gobyet mengangkat pisang tinggi-tinggi seperti piala"> | <img src="gif/normal-defeated.gif" width="192" alt="Gobyet rebah menyamping dan menghela napas"> |

Baris Greek Philosopher kolom pertama adalah `idle`; baris Academic dan Normal adalah `thinking` (idle keduanya sudah ada: `wisuda` dan `ngopi-santai`).

Cek sendiri:

```bash
python3 src/validate_pack.py --gate C    # hash aset lama, palet, seam loop, siluet, ukuran, warna
node --test pack/resolver.test.js        # resolver dan manifest
```

## Pasang Gobyet di project lain

Tempel di README atau halaman mana pun:

```html
<img src="https://raw.githubusercontent.com/kanku-Oiric/Gobyet/main/gif/marah-debug.gif" width="256" alt="Gobyet ngamuk ke laptop">
```

Ganti `marah-debug` dengan nama animasi lain: `makan-pisang`, `ngopi-santai`, `wisuda`, `filsuf-yunani`, `rambut-einstein`, `hacker`, `detektif-bug`, atau `kondangan`. Atur ukurannya lewat `width` (kelipatan 64 paling tajam: 128, 256, 512).

Aset character pack (`referee-idle`, `judge-judging`, dan seterusnya; daftar lengkapnya di `pack/manifest.json`) baru bisa dipakai lewat URL `main` setelah Fase 2 digabung ke `main`.

## Sprite sheet

Untuk web atau game, pakai sprite sheet di [`sheets/`](sheets): satu baris frame, tiap frame 64×48 (versi `@4x`: 256×192).

| Animasi | Frame | Durasi |
|---|---:|---:|
| `makan-pisang` | 25 | 3,8 detik |
| `marah-debug` | 28 | 4,2 detik |
| `ngopi-santai` | 16 | 2,8 detik |
| `wisuda` | 18 | 2,7 detik |
| `filsuf-yunani` | 20 | 3,5 detik |
| `rambut-einstein` | 22 | 3,9 detik |
| `hacker` | 16 | 2,1 detik |
| `detektif-bug` | 20 | 3,0 detik |
| `kondangan` | 12 | 1,7 detik |

Durasi tiap frame ada di `SCENES` pada [`src/scenes.py`](src/scenes.py) dan [`src/costumes.py`](src/costumes.py). Jumlah frame dan durasi aset character pack ada di [`pack/manifest.json`](pack/manifest.json).

## Bikin pose baru

Gobyet tidak digambar per frame, tapi disusun dari "rig" di [`src/monkey.py`](src/monkey.py):

- **`head()`**: ekspresi lewat parameter `eyes`, `brows`, `mouth`, dan `face` (normal atau merah marah).
- **`arm()`**: lengan dengan siku.
- **`tail()`, `sitting_body()`**: ekor keriting dan badan duduk.
- **Properti:** `banana()`, `laptop()`, `mug()`, `bubble()`, `puff()`.

Kostum ada di [`src/costumes.py`](src/costumes.py): badan berbaju (`dressed_body()`), aksesori kepala (`mortarboard()`, `laurel()`, `beard()`, `wild_hair()`, `hood()`, `sunglasses()`, `deerstalker()`, `peci()`), dan properti (`scroll()`, `column()`, `chalkboard()`, `magnifier()`, `bug()`).

Aset character pack Fase 2 ada di [`src/roles.py`](src/roles.py) (Referee, Judge, Skeptic, Champion) dan [`src/domains.py`](src/domains.py) (Normal dan kostum domain, termasuk pose rebah `lying_body()`).

Untuk pose atau kostum baru, tulis fungsi frame baru di `src/scenes.py`, `src/costumes.py`, `src/roles.py`, atau `src/domains.py`, daftarkan di `SCENES`-nya, lalu jalankan:

```bash
pip install -r requirements.txt
python3 src/export.py
```

GIF di `gif/` dan sprite sheet di `sheets/` akan dibangun ulang.

## Asal-usul

Digambar ulang dari gambar aslinya di [`asli/gobyet-asli.jpg`](asli/gobyet-asli.jpg): monyet cokelat dengan mug kopi, garuk kepala, di depan laptop.
