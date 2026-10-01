# Gobyet v2: sistem sprite karakter

Rework total karakter Gobyet: 38 karakter, 305 state animasi, 3.871 frame. Semua karakter berdiri dengan
kuda-kuda, senjata, dan siluet sesuai perannya, dengan kepala Gobyet yang sama persis dengan v1.

Aset v1 (`gif/`, `sheets/`, `pack/`) **tidak diubah**. v2 berdiri sendiri di folder ini. Pemilik yang memutuskan kapan
v2 menggantikan v1.

| Galeri warna | Siluet | Grayscale |
|:---:|:---:|:---:|
| <img src="qa/galeri-warna.png" width="260" alt="Galeri 38 karakter Gobyet v2 berwarna, dikelompokkan FANTASY, DOMAIN, ROLE, SPECIAL"> | <img src="qa/galeri-siluet.png" width="260" alt="Galeri siluet hitam 38 karakter"> | <img src="qa/galeri-grayscale.png" width="260" alt="Galeri grayscale 38 karakter"> |

## Isi folder

```
v2/
  registry.json        data karakter: state, frame, durasi, loop, alias state inti, fallback, jangkar, ikon
  context.json         peta domain topik -> karakter + ikon aksesori (data untuk aplikasi non-Python)
  resolver2.js         resolver fallback untuk browser/Node (sama persis dengan src/resolve2.py)
  sheets/<id>/<state>.png   strip frame 64x64 berpalet, transparan (sumber kebenaran)
  gif/<id>/<state>.gif      pratinjau 256x256
  icons/<nama>.png          ikon aksesori 16x16 (domain sekunder)
  qa/                  galeri, uji skala, metrik QA visual (visual-qa.json)
  STYLE.md             tata bahasa visual v2
  src/                 rig dan definisi karakter (Python + Pillow)
  tests/test_v2.py     tes registry, aset, fallback, konteks, siluet, baseline, wajah, seam
  tools/               pratinjau, QA visual, vendor ke skill Battle Royale
```

## Membangun ulang

```bash
pip install Pillow
python3 v2/src/export2.py                 # semua karakter (sekitar 2 menit)
python3 v2/src/export2.py knight-heavy    # satu karakter (registry tetap ditulis lengkap)
python3 -m unittest v2/tests/test_v2.py   # 34 tes
python3 v2/tools/visual_qa.py             # metrik + galeri ke v2/qa
SC=3 python3 v2/tools/sheet_preview.py knight-heavy out.png   # semua state satu karakter
SC=2 python3 v2/tools/overview.py out.png knight-heavy viking-huscarl
```

## Registry dan state inti

Setiap karakter punya `core`: peta state inti arena (`idle`, `attack`, `hit`, `victory`, `defeat`) ke state khasnya,
mis. `pirate-sharpshooter.attack = shoot`, `philosopher.attack = arguing`, `defeated.idle = sit`. Semua karakter
kategori fantasy, domain, dan special punya kelima state inti sendiri (diuji).

## Fallback (bagian 62)

`src/resolve2.py` dan `resolver2.js`:

1. Rantai karakter: kelas → basis faksi → Normal GBLK. Contoh: `viking-huscarl → viking → fantasy-viking → normal-gblk`,
   `knight-archer → fantasy-knight → normal-gblk`, karakter domain dan peran → `normal-gblk`. Id tak dikenal mulai dari
   `normal-gblk`.
2. Per karakter: state yang diminta → alias inti → idle.
3. Kandidat dipakai hanya bila berkas sheet-nya ada. Bila tidak ada sama sekali, hasilnya `None`/`null`: pemanggil
   tidak menggambar apa pun. Tidak pernah gambar rusak, tidak pernah mengaku aset ada.

## Context mapping (bagian 59-60)

`src/context2.py` (hanya pustaka standar): `select(topik)` → satu karakter primer + paling banyak satu ikon aksesori.

- Kata kunci per domain (Indonesia dan Inggris), dicocokkan per kata utuh.
- Teknologi jadi primer hanya bila berdiri sendiri: "AI + filsafat" → Philosopher + laptop, "AI + matematika" →
  Mathematician + laptop, "pendidikan + teknologi" → Academic + laptop. "Hukum + sejarah" → Lawyer + gulungan arsip.
- Kata teologi umum (agama, Tuhan, teologi) → Philosopher. Hanya kata yang jelas merujuk tradisi tertentu yang memilih
  Pak Haji atau Priest; ikon aksesori kedua tradisi sama (buku polos).
- Kata yang muncul di semua teks turnamen (argumen, premis) bukan kata kunci.
- Peran turnamen tetap: referee, judge, skeptic, champion, defeated.

## Integrasi Battle Royale

`tools/vendor_skill.py DEST` menyalin subset aset (state inti + state peran) dan `context2.py`/`resolve2.py` ke skill
`argument-battle-royale`. Arena HTML skill memilih karakter tiap petarung dari teks argumennya dan memutar duel,
putusan juri, uji falsifikasi, dan pemenang dengan karakter Gobyet; tanpa aset, arena kembali ke sprite Clawd.
