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

## Pasang Gobyet di project lain

Tempel di README atau halaman mana pun:

```html
<img src="https://raw.githubusercontent.com/kanku-Oiric/Gobyet/main/gif/marah-debug.gif" width="256" alt="Gobyet ngamuk ke laptop">
```

Ganti `marah-debug` dengan `makan-pisang` atau `ngopi-santai`. Atur ukurannya lewat `width` (kelipatan 64 paling tajam: 128, 256, 512).

## Sprite sheet

Untuk web atau game, pakai sprite sheet di [`sheets/`](sheets): satu baris frame, tiap frame 64×48 (versi `@4x`: 256×192).

| Animasi | Frame | Durasi |
|---|---:|---:|
| `makan-pisang` | 25 | 3,8 detik |
| `marah-debug` | 28 | 4,2 detik |
| `ngopi-santai` | 16 | 2,8 detik |

Durasi tiap frame ada di fungsi `*_ms` di [`src/scenes.py`](src/scenes.py).

## Bikin pose baru

Gobyet tidak digambar per frame, tapi disusun dari "rig" di [`src/monkey.py`](src/monkey.py):

- **`head()`**: ekspresi lewat parameter `eyes`, `brows`, `mouth`, dan `face` (normal atau merah marah).
- **`arm()`**: lengan dengan siku.
- **`tail()`, `sitting_body()`**: ekor keriting dan badan duduk.
- **Properti:** `banana()`, `laptop()`, `mug()`, `bubble()`, `puff()`.

Untuk pose baru, tulis fungsi frame baru di `src/scenes.py`, daftarkan di `SCENES`, lalu jalankan:

```bash
pip install -r requirements.txt
python3 src/export.py
```

GIF di `gif/` dan sprite sheet di `sheets/` akan dibangun ulang.

## Asal-usul

Digambar ulang dari gambar aslinya di [`asli/gobyet-asli.jpg`](asli/gobyet-asli.jpg): monyet cokelat dengan mug kopi, garuk kepala, di depan laptop.
