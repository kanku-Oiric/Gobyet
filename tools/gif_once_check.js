#!/usr/bin/env node
// Uji perilaku GIF tanpa loop (berserker-hero-rage.gif) di Chromium headless (Playwright, alat dev opsional).
//
//   node tools/gif_once_check.js [folder-keluaran] [gif-pembanding-sebelum.gif]
//
// Menampilkan GIF di <img> 512x384 pada latar abu, lalu mengambil tangkapan layar pada beberapa waktu:
//  - rage (loop=false): setelah total durasi harus berhenti di frame terakhir dan tidak berubah lagi;
//  - kontrol positif: run (loop tak hingga) harus tetap bergerak (tangkapan berbeda) pada waktu yang sama;
//  - frame terakhir yang tampil harus sama dengan frame terakhir sheet (frame 11 x4) yang dirender di kanvas pada latar yang sama.
// Hanya Chromium yang tersedia di lingkungan ini; penampil lain tidak diuji (lihat pack/README.md).
"use strict";
const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");

function loadPlaywright() {
  for (const t of [process.env.PLAYWRIGHT_MODULE, "playwright", "/opt/node22/lib/node_modules/playwright"].filter(Boolean)) {
    try { return require(t); } catch (e) { /* berikutnya */ }
  }
  console.error("Playwright tidak ditemukan."); process.exit(2);
}
const ROOT = path.resolve(__dirname, "..");
const OUT = path.resolve(process.argv[2] || path.join(ROOT, "tools", "out"));
const BEFORE = process.argv[3] ? path.resolve(process.argv[3]) : null;
const manifest = JSON.parse(fs.readFileSync(path.join(ROOT, "pack", "manifest.json"), "utf8"));
const rage = manifest.cells["berserker-hero"].rage;
const total = rage.durations_ms.reduce((a, b) => a + b, 0);

function serve() {
  const server = http.createServer((req, res) => {
    const rel = decodeURIComponent(new URL(req.url, "http://x").pathname);
    let file = rel === "/before.gif" && BEFORE ? BEFORE : path.join(ROOT, rel);
    if (!fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); res.end(); return; }
    const ext = path.extname(file);
    res.writeHead(200, { "content-type": ext === ".gif" ? "image/gif" : ext === ".png" ? "image/png" : "text/html", "cache-control": "no-store" });
    fs.createReadStream(file).pipe(res);
  });
  return new Promise((ok) => server.listen(0, "127.0.0.1", () => ok(server)));
}

(async () => {
  const { chromium } = loadPlaywright();
  fs.mkdirSync(OUT, { recursive: true });
  const server = await serve();
  const base = "http://127.0.0.1:" + server.address().port;
  const browser = await chromium.launch();
  const report = { chromium: browser.version(), rage_total_ms: total, rage_last_frame_ms: rage.durations_ms[rage.frames - 1], fails: [] };
  const check = (ok, msg) => { if (!ok) report.fails.push(msg); };
  const same = (a, b) => Buffer.compare(a, b) === 0;

  async function shots(src, times) {
    const ctx = await browser.newContext({ viewport: { width: 560, height: 430 } });
    const p = await ctx.newPage();
    await p.setContent('<body style="margin:0;background:#808080"><img id="g" style="display:block;margin:10px" width="512" height="384"></body>');
    const t0 = Date.now();
    await p.evaluate((u) => { document.getElementById("g").src = u + "?t=" + Date.now(); }, base + src);
    await p.waitForFunction(() => { const i = document.getElementById("g"); return i.complete && i.naturalWidth === 512; });
    const loadedAt = Date.now();
    const out = [];
    for (const t of times) {
      const wait = loadedAt + t - Date.now();
      if (wait > 0) await p.waitForTimeout(wait);
      out.push({ t, png: await p.locator("#g").screenshot() });
    }
    await ctx.close();
    return out;
  }

  // frame terakhir acuan: sheet frame 11 diperbesar 4x tanpa smoothing pada latar yang sama
  async function reference() {
    const ctx = await browser.newContext({ viewport: { width: 560, height: 430 } });
    const p = await ctx.newPage();
    await p.setContent('<body style="margin:0;background:#808080"><canvas id="c" width="512" height="384" style="display:block;margin:10px"></canvas></body>');
    await p.evaluate(async (args) => {
      const im = new Image(); await new Promise((r, j) => { im.onload = r; im.onerror = j; im.src = args.url; });
      const c = document.getElementById("c").getContext("2d"); c.imageSmoothingEnabled = false;
      c.drawImage(im, args.k * 128, 0, 128, 96, 0, 0, 512, 384);
    }, { url: base + "/sheets/berserker-hero-rage.png", k: rage.frames - 1 });
    const png = await p.locator("#c").screenshot();
    await ctx.close();
    return png;
  }

  const times = [400, total + 500, total + 3000, total + 6500];
  const r = await shots("/gif/berserker-hero-rage.gif", times);
  r.forEach((x, i) => fs.writeFileSync(path.join(OUT, "rage-t" + x.t + ".png"), x.png));
  const ref = await reference();
  fs.writeFileSync(path.join(OUT, "rage-frame-terakhir-acuan.png"), ref);
  report.rage_times_ms = times;
  report.rage_stops_after_total = same(r[1].png, r[2].png) && same(r[2].png, r[3].png);
  report.rage_last_frame_equals_sheet_frame = same(r[3].png, ref);
  report.rage_early_differs_from_last = !same(r[0].png, r[3].png);
  check(report.rage_stops_after_total, "rage: tangkapan setelah total durasi berubah (GIF berputar lagi)");
  check(report.rage_last_frame_equals_sheet_frame, "rage: frame akhir yang tampil beda dari frame terakhir sheet");

  // kontrol positif: run berputar tak hingga, jadi tangkapan pada waktu berbeda harus berbeda
  const run = await shots("/gif/berserker-hero-run.gif", [300, 420, 540, 660, 780]);
  report.run_control_distinct_frames = new Set(run.map((x) => x.png.toString("base64"))).size;
  check(report.run_control_distinct_frames >= 3, "kontrol run: GIF berputar tidak terlihat bergerak (uji tidak sahih)");

  if (BEFORE) {      // GIF rage sebelum perubahan (frame akhir 400 ms): perilaku Chromium yang sama?
    const b = await shots("/before.gif", [400, 1660 + 500, 1660 + 3000, 1660 + 6500]);
    report.before_stops = same(b[1].png, b[2].png) && same(b[2].png, b[3].png);
    report.before_last_equals_after_last = same(b[3].png, r[3].png);
  }
  await browser.close(); server.close();
  fs.writeFileSync(path.join(OUT, "gif-sekali.json"), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report, null, 2));
  console.log(report.fails.length ? "GIF-SEKALI: " + report.fails.length + " GAGAL" : "GIF-SEKALI: LULUS");
  process.exit(report.fails.length ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });
