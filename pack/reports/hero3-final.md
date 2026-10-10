# Berserker Hero v3: finalisasi dan masuk arena (laporan akhir)

Branch `claude/gobyet-hero` (repo Gobyet) dan `claude/argument-battle-royale-skill-3wzgmg` (repo Bertahan-Bukan-hidup). Tidak di-merge, tidak ada force-push. `main` Gobyet hanya disentuh untuk README halaman depan, atas izinmu. Format mengikuti bagian 8 brief awal.

**Dikerjakan:** pesanmu "udah ok. lanjut ke step selanjutnya" lalu jawaban "semuanya". Ada empat bagian: (1) merapikan keputusan yang tersisa, (2) finalisasi status dan kunci aset, (3) Fase 3: hero masuk arena Battle Royale, (4) hero tampil di README `main`.

**Status gaya:** disetujui pemilik. Perisai naga kamu sebut "udah good", `victory` "udah ok", ekor "udah ok", lalu kamu meminta finalisasi. Aset hero tidak berubah sejak commit ekor `94f87ad`.

## 1. Ringkasan

| Bagian | Hasil |
|---|---|
| Rapikan sisa | Ada tiga keputusan lama yang belum kamu jawab. Ketiganya dikunci sesuai yang sudah berjalan: pemetaan ekspresi per state, wajah Gobyet skala 1, dan batas per GIF 300 KiB. Rinciannya di `pack/README.md`, bagian "Keputusan akhir Berserker Hero". |
| Finalisasi | Status "disetujui pemilik" tercatat di `pack/README.md`, `STYLE.md`, `PROGRESS.md`, dan halaman evolusi. Hash 18 berkas di `pack/sha256-hero.txt` cocok. Tiga berkas kunci lama tidak disentuh. Label di artifact Gobyet Universe sudah diganti. |
| Fase 3: arena | Berserker Hero membuka setiap tayangan dari awal (lari masuk lalu `rage`). Hero juga menjadi petarung untuk topik atau argumen bertema pahlawan, perang, naga, monster, atau prajurit. Sebagai petarung ia lari masuk duel, menyerang bergantian smash/leap, memakai `exhaustion` saat terkena, dan memutar `victory` 20 frame saat menang. 38 karakter lama tidak berubah. |
| README `main` | Halaman depan repo Gobyet menampilkan hero: animasi `victory`, `attack-smash`, dan `run`, tautan ke galeri evolusi, dan catatan arena. Gambarnya diambil lewat URL raw branch `claude/gobyet-hero`, pola yang sama dengan bagian Gobyet Universe. |

## 2. Keputusan akhir (dikunci saat finalisasi)

| Butir | Keputusan |
|---|---|
| Ekspresi visor per state | idle `look` (sesekali berkedip `shut`/`dim`), run `angry` dengan mulut teriak, rage `glare` lalu `rage` dengan teriak, attack-leap/attack-smash `look` → `angry` → `rage` saat tumbukan, miss `angry` → `wide` → `dim`, exhaustion `tired`, defeated `tired` → `dim` → `shut`, victory `look` dengan topeng terbuka (wajah Gobyet tersenyum). Ini usulan di `hero3-model.md` bagian 5.2 yang tidak pernah kamu koreksi. |
| Wajah Gobyet di balik topeng | skala 1 (kepala `monkey.head` asli). V11 mewajibkan wajah ≥ 200 px dan mata ≥ 12 px saat topeng terbuka penuh. |
| Anggaran | total GIF + sheet ≤ 2.000.000 B (keputusanmu), sekarang 1.870.074 B. Per GIF ≤ 307.200 B (usulan saya); GIF terbesar `victory` 305.069 B. |
| Kunci aset | `pack/sha256-hero.txt` berdiri sendiri, sehingga `sha256-disetujui.txt` tetap byte-identik sesuai aturanmu. |

## 3. Fase 3: hero di arena

| Hal | Isi |
|---|---|
| Aset di skill | `assets/gobyet/sheets/berserker-hero/` memuat 8 state: idle, run, rage, attack-smash, attack-leap, exhaustion, defeated, victory. `miss` tidak dipakai arena, jadi tidak disalin. Ukurannya 188 KB dan disalin oleh `v2/tools/vendor_skill.py` dari `pack/`. |
| Registry arena | `canvas` 128×96, `anchor` x 66 / baseline 90, `px` [2, 3], `durations` per frame, `core.attack` = attack-smash, `core.hit` = exhaustion (hero tidak punya state hit), `variants.attack` = smash dan leap bergantian, fallback viking-berserker. |
| Skala gambar | 1 piksel hero = 2/3 piksel Gobyet, dibulatkan ke atas ke bilangan bulat, dan tetap muat di atas lantai. Di desktop (kanvas 600 px) Gobyet digambar 3× dan hero 2×, sehingga hero setinggi Gobyet berzirah ditambah jambulnya. Di ponsel 390 px keduanya 1×, jadi hero tampak sekitar 1,5× lebih besar. Skala piksel tidak bisa di bawah 1 tanpa membuang piksel. |
| Pemilihan topik | Domain baru `hero` di `v2/src/context2.py`. Contoh: "Apakah perang bisa dibenarkan?" memilih Berserker Hero. "Etika perang" memilih Philosopher dengan ikon pedang. "Perang salib" tetap Fantasy Knight. Kata "battle", "petarung", dan "fighter" sengaja bukan kata kunci. |
| Pembuka | `INTRO` di `scripts/engine/gobyet.py`, dengan ticker "Berserker Hero membuka arena", diputar sekali di awal. Penonton yang bergabung di tengah run tidak melihatnya. Pembuka bisa dimatikan dengan `INTRO = None`. |
| Ukuran halaman | Arena contoh (sample-run) naik dari 654.631 B menjadi 890.474 B. Batas selftest 2.500.000 B. Zip skill 640 KB. |

## 4. Tafsiran dan asumsi (bisa keliru; mohon koreksi)

1. **"Masuk arena" = pembuka + petarung bertema.** Peran turnamen (Referee, Judge, Skeptic, Champion) tidak diganti. Hero tidak otomatis menjadi petarung di semua topik, karena pemilihan karakter per topik sudah kamu setujui di Fase 2.
2. **`exhaustion` sebagai reaksi terkena.** Alternatifnya `rage`, tetapi `rage` ditahan 1,5 detik di akhir dan terlalu lama untuk satu pukulan.
3. **Balok kayu kecil** (sasaran bawaan animasi serangan) ikut terlihat di depan kaki saat menyerang. Aset yang sudah disetujui tidak saya ubah.
4. **Finalisasi = status disetujui + kunci hash + laporan.** Tag git dan merge tidak dibuat.

## 5. Validasi (keluaran mentah, ringkas)

```
Gobyet (claude/gobyet-hero):
  python3 src/validate_pack.py            HASIL: LULUS (proyeksi pertambahan 12,47 MB; batas 16 MB)
  python3 -m unittest test_hero3 test_validate_pack   Ran 69 tests ... OK
  node pack/resolver.test.js              # tests 25  # pass 25  # fail 0
  node tools/e2e_preview.js               E2E: LULUS
  node tools/gif_once_check.js            GIF-SEKALI: LULUS
  python3 tools/hero_hashes.py --check    18 berkas; sama dengan pack/sha256-hero.txt
  python3 tools/evolusi.py --check        17 berkas evolusi; sama dengan pack/sha256-evolusi.txt
  python3 -m unittest tests.test_v2 (v2/) Ran 47 tests ... OK
Arena (claude/argument-battle-royale-skill-3wzgmg):
  scripts/selftest.py                     SEMUA UJI LULUS (termasuk data hero, pembuka, topik perang -> hero)
  .github/scripts/e2e_arena.js            E2E LULUS, 15 pemeriksaan (pembuka tampil pertama; hero menang sampai
                                          TOURNAMENT WINNER, kanvas tidak pernah kosong, tanpa error halaman)
  .github/scripts/package_skill.py        258 file, 640 KB
```

## 6. Bukti visual (`pack/reports/hero3-final/`)

| Berkas | Isi |
|---|---|
| `arena-desktop.png` | Pembuka (lari masuk, mengamuk), masuk duel, serangan smash dan leap, terkena, serta hero di sisi kanan (dicerminkan). Kanvas 600 px. |
| `arena-pemenang.png` | Momen TOURNAMENT WINNER: `victory` hero (topeng membuka, wajah Gobyet, pedang ditancap, kaki di batu, usapan) di samping Champion. |
| `arena-ponsel.png` | Tayangan yang sama di lebar ponsel 390 px. |

Saya tidak menonton tayangan sebagai gerak. Pemeriksaan dilakukan lewat tangkapan layar Chromium berkala dan uji otomatis.

## 7. Bukti aset lama tidak berubah

- `pack/sha256-asli.txt` (27), `sha256-disetujui.txt` (89), `sha256-dibuat.txt` (242): `sha256sum -c` lulus, dan berkasnya tidak ada di diff.
- Aset hero: hash 18 berkas sama dengan kunci, tidak diekspor ulang.
- Arena: 38 karakter 64×64 tetap byte-identik (sheet tidak muncul di diff). `registry.json` hanya bertambah entri hero, dan nama `viking-berserker` mengikuti v2 terbaru ("Viking Berserker Gobyet").

## 8. Perubahan kode

- Gobyet: `v2/src/context2.py` (domain `hero`, `PACK_CHARS`), `v2/tests/test_v2.py`, `v2/context.json`, `v2/tools/vendor_skill.py` (menyalin hero dari `pack/`), `v2/README.md`. Dokumen: `pack/README.md`, `STYLE.md`, `PROGRESS.md`, `pack/evolusi/README.md`, `pack/evolusi/index.html`.
- Arena: `scripts/engine/gobyet.py` (kanvas/jangkar/px/durs per karakter, varian, `INTRO`), `templates/arena.html` (frame berdurasi, skala per karakter, lari masuk duel, serangan bergantian, pembuka, jarak pemenang lebar), salinan ulang `gobyet_context.py`/`gobyet_resolve.py`/aset, `scripts/selftest.py`, `.github/scripts/e2e_arena.js`, `README.md`, `SKILL.md`, dan `examples/sample-run/arena.html` yang dibuat ulang.

## 9. Kelemahan yang saya lihat sendiri

1. Di ponsel hero terlihat sekitar 1,5× Gobyet dan pedangnya bisa menutupi Judge sejenak saat palu diketuk.
2. Saat menyerang, balok kayu kecil tampak sebagai benda asing di arena.
3. Di topik campuran, ikon pedang bisa muncul dua kali makna. Contoh: Fantasy Knight dengan aksesori pedang dari domain hero.
4. GIF `victory` tinggal 2.131 B di bawah batas per GIF, jadi sisa ruang untuk menambah frame sangat kecil.

## 10. Keputusan yang saya butuhkan darimu

1. Pembuka hero di setiap tayangan dipertahankan, atau cukup hero sebagai petarung?
2. Kata kunci domain `hero` (pahlawan, perang, naga, monster, prajurit, keberanian, gladiator) sudah pas?
3. Merge kedua branch tetap menunggu perintahmu.

## 11. Daftar berkas

```
pack/reports/hero3-final.md (laporan ini)  pack/reports/hero3-final/ (3 tangkapan arena)
pack/README.md  pack/STYLE.md  pack/PROGRESS.md  pack/evolusi/README.md  pack/evolusi/index.html
v2/src/context2.py  v2/tests/test_v2.py  v2/context.json  v2/tools/vendor_skill.py  v2/README.md   (commit d24d0cb)
Bertahan-Bukan-hidup: commit 138af17 (arena)
README.md di main (commit terpisah, hanya README)
```

Berserker Hero disetujui pemilik dan sudah masuk arena.
