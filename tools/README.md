# tools/

Alat pengembangan. Tidak dibutuhkan untuk memakai Gobyet atau character pack, dan bukan dependensi proyek (proyek tetap tanpa `package.json`).

## `e2e_preview.js`: uji browser untuk `pack/preview.html`

```bash
node tools/e2e_preview.js [folder-keluaran]    # bawaan: tools/out/
```

Butuh [Playwright](https://playwright.dev) dan Chromium di mesinmu, dipasang **di luar** proyek, misalnya `npm i -g playwright` lalu `npx playwright install chromium`. Kalau modulnya ada di tempat lain, set `PLAYWRIGHT_MODULE=/path/ke/playwright`.

Skrip ini menyalakan server statis kecil memakai modul bawaan Node, jadi tidak perlu `python3 -m http.server`. Yang diperiksa:

- Jumlah sel asli, baru, placeholder, dan tidak berlaku sama dengan `pack/manifest.json`.
- 0 console error dan 0 request gagal, di desktop maupun ponsel.
- Mode Animasi bergerak. Tombol Statis dan `prefers-reduced-motion` berhenti di frame kunci, dicocokkan per piksel dengan sheet 1×.
- Tampilan 4× (sheet 1× diperbesar tanpa smoothing) sama per piksel dengan `sheet4x`, untuk sel yang masih punya file itu.
- Tes buta: label tersembunyi sampai tombol ditekan, dan urutannya tetap setelah halaman dimuat ulang.
- Tidak ada scroll horizontal di viewport ponsel 390 px.
- Filter panel banding: gabungan semua pilihan gerbang sama dengan semua sel bergerbang, jumlah per gerbang cocok, dan tinggi satu tampilan gerbang di ponsel ≤ 3000 px.
  - Gerbang dengan lebih dari 24 aset (J dan F) dipecah menjadi beberapa pilihan per keluarga atau faksi, misalnya `J:knight` dan `F:peran`.
  - Jumlah per gerbang dihitung dari semua pilihan dengan huruf gerbang yang sama.

Hasilnya ditulis ke `e2e.json` beserta screenshot (`compare-static.png`, `blind-*.png`, `preview-*.png`). Skrip keluar dengan kode 1 bila ada pemeriksaan yang gagal. Folder `tools/out/` diabaikan git.
