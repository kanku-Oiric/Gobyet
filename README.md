<p align="center">
  <img src="gif/ngopi-santai.gif" width="384" alt="Gobyet memegang mug kopi, menggaruk kepala sambil melirik laptop, lalu menyeruput kopi">
</p>

<h1 align="center">Gobyet</h1>

<p align="center">
  <b>Goblok monyet.</b> Maskot dari semua project saya: dikerjakan buat have fun,<br>
  oleh monyet bodoh yang lagi larping jadi programmer.
</p>

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
| H | Knight, Viking, Pirate, Wizard | belum |
| I | Pak Haji, Priest | belum |
| J | 12 varian kelas Knight, Viking, Pirate | belum |
| F | Sisa sel 12 kostum lama, audit, dokumentasi | belum |

Terisi 57 dari 163 sel yang berlaku: 7 aset asli dan 50 aset baru. Sel lainnya memakai fallback.

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
