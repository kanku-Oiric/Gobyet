# Tata bahasa visual Gobyet v2

Acuan desain untuk semua karakter v2. Prinsipnya: **Gobyet yang masuk ke dunia lain, bukan manusia bercostum.**
Urutan prioritas: identitas, siluet, keterbacaan, pengenalan peran, animasi, detail.

## 1. Kanvas, jangkar, skala

- Kanvas 64×64 piksel, latar transparan, tanpa anti-aliasing dan tanpa alfa parsial.
- Jangkar sama untuk semua karakter: tengah kaki di x = 28, baris kaki terbawah di y = 58 (`BASE` = 59 adalah lantai).
  Tidak ada piksel di bawah lantai; idle selalu menapak di y = 58.
- Semua karakter menghadap ke kanan. Arena mencerminkan petarung sisi kanan.
- Sheet 1× (strip 64·n × 64) adalah sumber kebenaran; GIF 4× hanya pratinjau.
- Durasi frame kelipatan 10 ms (GIF hanya menyimpan sentidetik).

Kenapa 64×64 dan bukan 64×48 seperti v1: kelas tempur butuh badan berdiri, kuda-kuda, langkah, dan senjata yang
diangkat di atas kepala. Di 48 px tinggi, helm berjambul atau pedang terangkat akan terpotong.

**Pengecualian kanvas: Berserker (144×100).** Pedangnya 1,2–1,5× tinggi badan dan jurusnya melompat dan bersalto,
jadi kanvasnya diperlebar. Badan tetap digambar di koordinat rig yang sama (skala piksel sama dengan 38 karakter
lain); kanvasnya hanya jendela yang lebih lebar. Jangkar di gambar: x = 56, lantai `baseline` = 95. Registry
menyimpan `canvas` dan `anchor` per karakter; tanpa itu berlaku 64×64.

## 2. Identitas Gobyet (terkunci)

- Kepala memakai `head()` dari rig v1 tanpa perubahan: tengkorak cokelat, telinga besar, wajah krem berbentuk hati,
  mata putih besar dengan pupil, alis, mulut `frown` khas.
- Badan berdiri v2: torso cokelat dengan perut krem, kaki pendek, telapak krem, ekor keriting di belakang pinggul.
  Proporsi chibi: kepala sekitar 40% tinggi badan.
- Helm, topi, dan tudung **tidak menutupi mata**. Telinga Gobyet menyembul di sisi helm (Knight, Viking) atau
  menjadi tonjolan di tudung hoodie (Hacker). Wajah selalu terlihat (diuji: ≥ 25 piksel krem wajah per frame).
- Kostum mengubah siluet, kuda-kuda, prop, dan pakaian. Wajah, telinga, ekor, dan garis tepi tetap.

## 3. Garis tepi dan cahaya

- Setiap bentuk: isi, bayangan kanan-bawah (`shade_off` 2,2 untuk badan, 1,1 untuk prop kecil), garis tepi 1 px `K`.
- Cahaya dari kiri atas. Kilau 1–3 piksel putih pada logam dan benda mengilap.
- Bentuk lokal (senjata) dirasterisasi pada sudut berapa pun lalu diberi garis tepi yang sama, jadi senjata yang
  diputar tetap satu bahasa piksel dengan badan.

## 4. Palet

Palet v1 (`PAL` + `PAL_EXT`) ditambah warna bernama v2:

| Kelompok | Kunci | Dipakai untuk |
|---|---|---|
| Baja kebiruan | `st0`–`st3` | zirah Knight, bilah, umbo perisai |
| Bulu hewan | `fu0`–`fu2` | mantel bulu Viking |
| Kulit | `le1`, `le2` | rompi, sabuk, sepatu |
| Kayu | `wo1`, `wo2` | gagang, busur, perisai bundar |
| Navy, merah tua, emas | `nv1/nv2`, `cr1/cr2`, `go1/go2` | Pirate |
| Efek | `glw`, `mag`, `smk`, `sm2` | cahaya layar, sihir, asap |
| Baja hitam | `bk0`–`bk3` | zirah Berserker (lebih terang dari garis tepi `K` supaya bentuk terbaca); `bk0` = tepi aus hangat |
| Besi pedang | `sw1`, `sw2`, `ir1` | bilah besi gelap, bayangan, tepi aus |
| Bulu gelap, merah redup, jubah | `df1/df2`, `mr1/mr2`, `cl1/cl2` | kerah dan rok bulu, kain sobek, jubah arang |
| VFX | `du1/du2`, `rk1/rk2`, `sl1`–`sl3`, `em1/em2` | debu, puing batu, tebasan, bara amuk |
| Darah (VFX saja) | `bl0`–`bl3` | hanya di sprite VFX darah; diuji tidak pernah muncul di sheet karakter |

Faksi berbagi palet. Warna aksen boleh berbeda antar-kelas, tapi **warna tidak pernah menjadi satu-satunya
pembeda** (diuji dengan siluet dan grayscale).

## 5. Bahasa visual per faksi

| Faksi | Material | Siluet faksi | Pembeda antar-kelas |
|---|---|---|---|
| Knight | baja (pelat besar, pelindung bahu berlapis), putih, aksen merah tua | helm + bahu + senjata panjang | Heavy: helm besar berjambul, perisai menara, pedang besar. Archer: topi baja bertepi lebar, busur panjang, tabung panah. Man-at-Arms: helm runcing, rantai, halberd, kuda-kuda lebar. Assassin: tudung runcing, jubah asimetris, dua belati, kuda-kuda rendah, badan ramping. |
| Viking | bulu bergerigi, kulit, kayu, besi gelap | tanduk + bulu + kapak/perisai bundar | Berserker: tudung kulit serigala, lengan terbuka, dua kapak, amuk. Huscarl: tanduk besar, mantel bulu tebal, baju rantai, kapak Dane, perisai bundar besar. Gestir: helm kerucut, tombak panjang diagonal, lembing di punggung. Bóndi: topi kain, tunik zaitun, busur pendek, seax. |
| Pirate | navy, cokelat, merah, emas | topi + mantel + senjata | Captain: tricorn besar berbulu, mantel panjang mengembang, epolet. Skirmisher: bandana berekor, kaus belang, kaki telanjang, tong mesiu. Sharpshooter: topi lebar datar, senapan panjang. Buccaneer: badan terbesar, mantel berat, palu raksasa, jangkar di punggung. |
| Fantasy | arketipe dongeng | | Fantasy Knight: helm visor, jubah biru, perisai layang-layang. Fantasy Viking: helm emas bertanduk raksasa, janggut kepang, jubah merah. Fantasy Pirate: penutup mata, mantel merah, peta harta, teropong. Wizard: topi runcing tinggi, jubah sampai lantai, tongkat bercahaya. |

Knight = logam. Viking = bulu, kulit, kayu. Heavy Knight dan Huscarl sengaja berbeda material, bentuk perisai,
senjata, dan helm (IoU siluet 0,70).

**Berserker (dark fantasy, `berserker`).** Arketipe pendekar berpedang raksasa berzirah hitam, desain orisinal
(tidak menyalin karakter tertentu). Siluet: pedang selebar papan (bilah 9 px, panjang total ±55 px), pauldron kiri
besar tiga lapis, bahu kanan hanya cop kecil dan lengan atas berbulu Gobyet (asimetris), pelat dada bersegmen,
sarung tangan besi, bulu gelap dan kain merah redup di pinggang, jubah pendek sobek, kuda-kuda jongkok condong.
Beda dari Heavy Knight: tanpa helm dan perisai, zirah hitam babak belur bukan baja terang, kuda-kuda rendah
tidak stabil. Viking Berserker (dua kapak, tudung serigala) tetap kelas Viking.

## 6. Karakter domain dan peran

Prop dan pakaian yang membentuk siluet: papan berkaki (Mathematician rumus, Economist grafik, Sociologist jaringan),
kursi berlengan (Psychologist duduk), meja (Judge), tumpukan buku tinggi (Researcher), topi (toga, deerstalker, helm
proyek, pelindung mata hijau, topi pet, kopiah), jas lab panjang, jubah, koper (Lawyer). Teologi: Pak Haji dan Priest
diperlakukan identik (aura emas halus yang sama, jumlah state paralel, tanpa komedi). Aura adalah efek visual, bukan
penanda argumen benar. Champion berlabel "TOURNAMENT WINNER", tidak pernah "ABSOLUTE TRUTH"; medali menggantikan
laurel emas di kepala (keputusan pemilik di Gerbang B).

## 7. Animasi

- Pose adalah angka (posisi tangan, condong, jongkok, angkat kaki, sudut senjata). Frame dibuat dari keyframe dengan
  interpolasi halus, lalu dibulatkan ke piksel utuh dan sudut kelipatan 5°, supaya bentuk tidak berkedip.
- Idle: napas 1 px, kedip 1 frame, lirikan, prop sedikit bergerak.
- Senjata: pedang dan kapak = ancang-ancang (senjata di belakang kepala, wajah tidak tertutup), ayunan, hantaman,
  kembali. Busur = tarik, lepas, hentakan. Tombak = bidik, lempar/tusuk, kembali. Senjata api = bidik, kepulan kartun,
  hentakan, isi ulang. Sihir = rapal, efek, kembali.
- Victory berbeda per kelas (pedang/kapak/cutlass terangkat, tongkat sihir, terminal OK, gulungan, buku, menunjuk
  bukti, tarian GBLK). Loop victory dimulai dari pose naik, jadi sambungannya mulus.
- Defeat berbeda per kelas: Heavy jatuh berat, Archer busur jatuh, Assassin mundur di balik asap, Viking perisai
  turun dan berlutut, Pirate topi jatuh, Wizard tongkat jatuh + asap, Hacker laptop error, GBLK papan roboh. Rebah
  memutar badan 90° tetapi kepala digambar ulang tegak, jadi wajah tidak terbalik.
- Tanpa darah dan luka di sheet karakter. Ledakan dan tembakan adalah kartun (bintang "pow", kepulan asap).
- Satu pengecualian terkendali: darah bergaya untuk serangan Berserker yang **kena**. Darah hanya sprite VFX
  terpisah (`vfx/blood_*.png`): tetesan dan cipratan merah bergaris tepi gelap, 4–6 frame, ≤ 160 piksel per
  frame, tingkat 1–3 (`registry.blood.levels`, tingkat 0 mematikan). Mesin memunculkannya di titik event `hit`
  hanya bila target memang kena. Tanpa gore: tidak ada potongan tubuh, organ, atau luka realistis.

## 7a. Tempo, event, lapisan, kerusakan, varian (Berserker)

- Tempo tidak rata: `durations` per frame (kelipatan 10 ms). Ancang-ancang lambat, lepas cepat, putaran 40 ms,
  frame hantam ditahan, pemulihan berat.
- Event per state: `hit` (titik kena relatif jangkar, arah, darah per tingkat), `hitstop`, `screen_shake`,
  `vfx` (sudah ada di lapisan VFX, `baked`), `phase` (rentang fase jurus khas).
- Lapisan `body` (karakter + zirah), `weapon` (piksel pedang yang terlihat), `vfx`: ditumpuk berurutan sama persis
  dengan komposit (diuji per frame).
- Kerusakan visual `normal`, `damaged` (goresan, penyok, jubah berlubang), `heavily_damaged` (pauldron sompal,
  pelat dada pecah memperlihatkan bulu, jubah lebih pendek). Hanya visual.
- Varian idle dan attack dipilih deterministik dari seed (`Resolver.variant`, FNV-1a), sama di Python dan JS.
- Salto memutar seluruh figur kelipatan 90° (piksel utuh); putaran gasing mencerminkan figur sesaat.

## 8. Uji yang menjaga aturan ini

`v2/tests/test_v2.py` dan `v2/tools/visual_qa.py`: siluet dalam faksi (IoU ≤ 0,80), pasangan bagian 54, lantai dan
baseline, wajah terlihat, sambungan loop, paritas teologi, registry, fallback, context mapping. Berserker: kanvas
dan jangkar, kepala dari fungsi yang sama, lapisan = komposit, tingkat kerusakan, rasio pedang/badan, tempo dan
event jurus khas, sprite VFX, darah tidak pernah di sheet karakter, darah VFX kecil dan singkat, varian
deterministik (Python = JS).
