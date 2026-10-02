# Laporan: Berserker Gobyet, varian pedang raksasa dark fantasy

Brief: "CREATE / REWORK: GOBYET BERSERKER — DARK FANTASY GIANT-SWORD VARIANT" (bagian 1-37), dengan ralat
pemilik: berserker yang dimaksud bergaya pendekar pedang raksasa (arketipe "Guts"), bukan berserker kapak ganda.

## Keputusan

- **Karakter baru `berserker`** (kategori fantasy, fallback `normal-gblk`). Viking Berserker kapak ganda tetap ada
  sebagai kelas Viking (`viking-berserker`, nama tampil diganti menjadi "Viking Berserker Gobyet" supaya tidak
  tertukar). Bila pemilik ingin kelas Viking itu dihapus atau diganti, itu perubahan terpisah.
- **Desain orisinal.** Yang dipakai hanya prinsip umum arketipe: zirah hitam babak belur dan asimetris, pedang
  selebar papan, jubah pendek sobek, kuda-kuda rendah. Tidak ada helm, tangan prostetik, lambang, atau bekas luka
  yang meniru karakter tertentu. Kepala Gobyet tidak diubah.
- **Kanvas 144×100.** Pedang 55 px dan salto 360° tidak muat di 64×64. Badan digambar di koordinat rig yang sama,
  jadi skala piksel Gobyet identik dengan 38 karakter lain. Jangkar gambar: x = 56, baseline = 95.
- **Darah hanya sprite VFX terpisah.** Darah dimunculkan mesin pada event `hit` hanya bila serangan kena. Sheet
  karakter tidak pernah berisi warna darah (diuji di semua 39 karakter, termasuk lapisan dan tingkat kerusakan).

## Desain

| Bagian | Isi |
|---|---|
| Identitas | `head()` v1 dan ekor yang sama (diuji `Berserker.head is Char.head`). Wajah terlihat di semua 294 frame, minimal 50 piksel krem. |
| Zirah | Pelat dada bersegmen dengan tepi aus hangat. Pauldron kiri besar tiga lapis. Bahu kanan hanya cop kecil, dan lengan atas kanan memperlihatkan bulu Gobyet (asimetris). Vambrace dan sarung tangan besi. Greave, pelindung lutut, sepatu bot besar. Bulu gelap di pinggul, dua lidah kain merah redup, jubah arang pendek bertepi sobek. |
| Palet | `bk0`–`bk3` baja hitam (lebih terang dari garis tepi `K` supaya bentuk terbaca), `sw1/sw2/ir1` besi pedang, `df` bulu gelap, `mr` merah redup, `cl` jubah. Tanpa emas dan tanpa kilau. |
| Pedang | Gagang 11 px berbalut kulit, palang besi sederhana, pangkal bilah diperkuat dua paku keling. Bilah 9 px lebar, ujung tumpul miring, tiga takik, goresan, tepi aus. Panjang total 55,4 px = **1,42×** tinggi badan berdiri (39 px). |
| Pembeda dari Heavy Knight | Tanpa helm dan perisai; baja hitam, bukan baja terang; kuda-kuda jongkok condong, tidak tegak. |
| Kerusakan (visual) | `damaged`: goresan, penyok, jubah berlubang, takik pauldron. `heavily_damaged`: pauldron sompal, pelat dada pecah memperlihatkan bulu, retak, jubah lebih pendek dengan tiga lubang. |

## State (23)

17 state dari brief, 5 varian idle, dan 1 varian attack. Durasi per frame berkelipatan 10 ms.

| State | Frame | Total ms | Jenis | Frame kena |
|---|---:|---:|---|---|
| idle (F0–F4) | 5 | 940 | loop | |
| idle_breath, idle_grip, idle_drag, idle_look, idle_twitch | 8, 8, 10, 10, 6 | 1340, 1100, 1520, 1720, 860 | loop, varian idle | |
| ready | 6 | 690 | loop | |
| run | 8 | 640 | loop | |
| jump | 10 | 980 | sekali | |
| attack / attack_b | 12 / 12 | 1130 / 1160 | sekali | 6 / 5 |
| heavy_attack | 16 | 1790 | sekali | 7 |
| overhead_smash | 18 | 2160 | sekali | 7 |
| air_slash | 14 | 1200 | sekali | 6 |
| **leap_spin_slash** | 23 | 2160 | sekali | 15 |
| rage | 10 | 1100 | sekali | |
| rage_attack | 22 | 1810 | sekali | 4, 6, 8, 14 |
| combo | 24 | 2040 | sekali | 3, 6, 8, 17 |
| hit | 8 | 750 | sekali | |
| miss | 21 | 3070 | sekali + tahan | |
| exhausted | 8 | 1030 | loop | |
| victory | 16 | 2120 | sekali + tahan | |
| defeat | 19 | 2970 | sekali + tahan | |

Nama brief `berserker_*` tercatat sebagai alias (`aliases`); resolver memetakannya ke state di atas.

**Jurus khas `leap_spin_slash`**:

| Fase | Frame | Tempo per frame |
|---|---|---|
| Ancang-ancang | 0–3 | 120–180 ms (lambat) |
| Isi tenaga | 4–6 | 90–110 ms |
| Lompat | 7–10 | 50–70 ms (cepat) |
| Salto | 11–14 | 40 ms (sangat cepat) |
| Hantaman | 15 | 160 ms (ditahan) |
| Debu dan puing | 16–18 | 90–100 ms |
| Pulih | 19–22 | 80–140 ms |

Pada salto, seluruh figur diputar 90° per frame (piksel tetap utuh) dengan jejak bulan sabit di sekeliling badan.
Frame 15 membawa event `hit`, `hitstop` 110 ms, `screen_shake` 5 px / 260 ms, dan `vfx ground_impact` + `debris`.

Catatan gerak per state:

- **rage_attack**: memakai putaran gasing. Figur dicerminkan sesaat dan jejaknya berupa elips pipih, jadi berbeda
  dari salto vertikal.
- **rage**: aksen merahnya halus. Wajah memerah dua frame, ada bara kecil dan garis aura merah redup terputus,
  bukan cahaya merah penuh.
- **miss**: pedang tertancap miring di tanah, ditarik-tarik sambil berkeringat, Gobyet menatap pedang, lalu
  menatap penonton dengan "...".
- **defeat**: pedang terlalu berat, terjungkal ke belakang dan jatuh. Gobyet duduk, menunjuk pedang dengan "!",
  lalu cemberut dengan "...".
- **victory**: susah payah mengangkat pedang, mengacungkannya tegak, lalu mengaum.

## VFX (13 sprite + 2 jenis event)

| Sprite | Ukuran |
|---|---|
| `slash_arc` | 64×64 |
| `sword_trail` | 64×64 |
| `dust` | 48×16 |
| `impact` | 48×48 |
| `debris` | 48×32 |
| `spark` | 24×24 |
| `ground_impact` | 96×40 |
| `blood_small` (tingkat 1) | 32×24 |
| `blood_medium` (tingkat 2) | 40×28 |
| `blood_burst` (tingkat 3) | 48×36 |
| `blood_arc` | 48×40 |
| `blood_particles` | 32×28 |
| `blood_ground` | 32×4 |

`screen_shake_trigger` dan `hitstop` adalah event untuk mesin, bukan sprite. Darah: maksimal 6 frame, total
paling lama 520 ms, paling banyak 160 piksel per frame (diuji). Bentuknya tetesan dan cipratan bintang kartun
bergaris tepi gelap. Tidak ada gore.

Konfirmasi kena (`tools/hit_confirm_preview.py`, keluaran `preview/berserker-leap_spin_slash-hit.gif`):
hantaman → lawan berkilat → hit-stop → darah tingkat 2 di titik kena setinggi badan → lawan recoil dan terdorong
→ percikan → debu. Pratinjau ini membaca registry dan sheet hasil ekspor, sama seperti cara mesin membacanya.

## Lapisan dan registry

- Tiap state punya `layers.body` (karakter + zirah), `layers.weapon` (piksel pedang yang terlihat), dan
  `layers.vfx`. Ketiganya ditumpuk berurutan sama persis dengan komposit di semua 882 frame (294 × 3 tingkat).
- `damage.damaged/heavily_damaged` memuat sheet, GIF, dan lapisan per tingkat. Lapisan senjata atau VFX yang
  identik dengan tingkat normal memakai berkas normal.
- `variants` dipilih deterministik oleh `Resolver.variant(id, state, seed)` (FNV-1a). Python dan JS menghasilkan
  pilihan yang sama (diuji untuk 40 seed).
- `registry.vfx`, `registry.blood` (tingkat 0–3, default 2, `only_on_hit`), dan `registry.event_types`.

## Verifikasi

| Pemeriksaan | Hasil |
|---|---|
| `python3 -m unittest v2/tests/test_v2.py` | 47 tes lulus (34 lama + 13 Berserker) |
| 38 karakter lama setelah ekspor ulang penuh | sheet dan GIF identik byte per byte (git: tidak ada perubahan) |
| Berserker kanvas penuh, 3 tingkat (QA visual) | 0 piksel di bawah lantai, wajah min 50 px, 0 lapisan tidak cocok, 0 piksel darah di sheet |
| Pengenalan siluet (proksi), semua karakter | 87,3 / 86,4 / 84,5 / 74,5% pada skala 100/75/50/25% |
| Pengenalan siluet (proksi), roster | 88,2 / 87,3 / 87,3 / 81,8% |
| Salah kenal yang melibatkan Berserker | 0 |
| IoU siluet dalam faksi dan pasangan bagian 54 | tidak berubah |
| Seam loop | 0 gagal; 69 pop 1 px (sebelumnya 68; tambahannya napas idle Berserker) |
| Ukuran aset baru | sheet 1,2 MB, GIF 3,6 MB, VFX 160 KB, preview 164 KB |

## Yang belum

- Arena Battle Royale masih menggambar frame 64×64, jadi `tools/vendor_skill.py` sengaja melewati Berserker.
  Agar Berserker tampil di arena, arena perlu dukungan kanvas per karakter. Repo Bertahan tidak diubah dalam
  pekerjaan ini.
- Pengenalan siluet di atas adalah proksi otomatis, bukan uji dengan manusia.
