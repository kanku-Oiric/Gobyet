#!/usr/bin/env node
// Uji ujung-ke-ujung pack/preview.html di Chromium headless (Playwright, alat dev opsional).
//
//   node tools/e2e_preview.js [folder-keluaran]
//
// Menyalakan server statis kecil (modul bawaan Node) di akar repo, lalu memeriksa:
// jumlah sel (asli, baru, placeholder, tidak berlaku), console error, request gagal, gerak vs statis,
// mode statis/reduced motion = frame kunci per piksel (kanvas per sel: 64x48, hero 128x96), tampilan 4x =
// sheet 1x diperbesar (dan sama dengan sheet4x bila file itu ada), tes buta (urutan tetap, label tersembunyi),
// lembar kontak Berserker Hero (semua frame, bernomor, 2x, sama dengan sheet per piksel, bisa digulir, pilihan
// latar terang/gelap, GIF termuat 512x384), dan scroll horizontal di ponsel. Keluar dengan kode 1 bila ada
// pemeriksaan yang gagal.
"use strict";
const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");

function loadPlaywright() {
  const tries = [process.env.PLAYWRIGHT_MODULE, "playwright", "/opt/node22/lib/node_modules/playwright"].filter(Boolean);
  for (const t of tries) {
    try { return require(t); } catch (e) { /* coba berikutnya */ }
  }
  console.error("Playwright tidak ditemukan. Pasang di luar proyek (npm i -g playwright) atau set PLAYWRIGHT_MODULE.");
  process.exit(2);
}

const ROOT = path.resolve(__dirname, "..");
const OUT = path.resolve(process.argv[2] || path.join(ROOT, "tools", "out"));
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".json": "application/json", ".png": "image/png", ".gif": "image/gif" };

function serve() {
  const server = http.createServer((req, res) => {
    const rel = decodeURIComponent(new URL(req.url, "http://x").pathname);
    const file = path.join(ROOT, rel);
    if (!file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); res.end(); return; }
    res.writeHead(200, { "content-type": TYPES[path.extname(file)] || "application/octet-stream", "cache-control": "no-store" });
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
  const report = {}, fails = [];
  const manifestData = JSON.parse(fs.readFileSync(path.join(ROOT, "pack", "manifest.json"), "utf8"));
  const check = (ok, msg) => { if (!ok) fails.push(msg); };

  async function open(opts) {
    const ctx = await browser.newContext(opts);
    const p = await ctx.newPage();
    const errors = [], bad = [];
    p.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
    p.on("pageerror", (e) => errors.push("pageerror: " + e.message));
    p.on("requestfailed", (r) => bad.push("failed " + r.url()));
    p.on("response", (r) => { if (r.status() >= 400) bad.push(r.status() + " " + r.url()); });
    await p.goto(base + "/pack/preview.html");
    await p.waitForSelector('html[data-ready="1"]');
    await p.waitForTimeout(1500);
    return { ctx, p, errors, bad };
  }
  const hashOf = (p, sel) => p.$eval(sel, (c) => { const d = c.getContext("2d").getImageData(0, 0, c.width, c.height).data; let h = 0; for (let i = 0; i < d.length; i++) h = (h * 31 + d[i]) >>> 0; return h; });
  // Setiap kanvas yang punya data-src harus menampilkan frame kunci sel itu, digambar dari sheet 1x.
  const staticCheck = (p) => p.evaluate(async () => {
    const cs = [...document.querySelectorAll("canvas[data-src]")].filter((c) => !c.hidden && c.id !== "playCanvas");
    const load = (src) => new Promise((res, rej) => { const im = new Image(); im.onload = () => res(im); im.onerror = rej; im.src = src; });
    const man = await (await fetch("manifest.json")).json();
    const dimOf = {};   // url sheet -> kanvas satu frame (kanvas sel bila ada, bila tidak kanvas global)
    for (const row of Object.values(man.cells)) for (const cell of Object.values(row)) dimOf[new URL(cell.sheet, document.baseURI).href] = cell.canvas || man.canvas;
    const cache = {}, frameMismatch = [], pixelMismatch = [];
    let heroCanvases = 0;
    for (const c of cs) {
      const f = +c.dataset.frame, k = +c.dataset.keyframe, w = c.width, h = c.height;
      const name = c.dataset.src.split("/").pop();
      const d = dimOf[c.dataset.src];
      if (d.w === 128) heroCanvases++;
      if (f !== k) frameMismatch.push(name + " frame " + f + " != kunci " + k);
      const im = cache[c.dataset.src] || (cache[c.dataset.src] = await load(c.dataset.src));
      const off = document.createElement("canvas"); off.width = w; off.height = h;
      const ctx = off.getContext("2d"); ctx.imageSmoothingEnabled = false;
      ctx.drawImage(im, k * d.w, 0, d.w, d.h, 0, 0, w, h);
      const a = ctx.getImageData(0, 0, w, h).data, b = c.getContext("2d").getImageData(0, 0, w, h).data;
      let diff = 0; for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) diff++;
      if (diff) pixelMismatch.push(name + " " + w + "x" + h + " " + diff);
    }
    return { canvases: cs.length, hero_canvases: heroCanvases, frame_mismatch: frameMismatch, pixel_mismatch: pixelMismatch };
  });
  // Filter panel banding: tiap pilihan menampilkan tepat sel gerbangnya; gabungan semua gerbang = semua sel bergerbang.
  const filterCheck = async (p, measure) => {
    const opts = await p.$$eval("#cmpFilter option", (os) => os.map((o) => o.value));
    const out = { options: opts, per_option: {}, union_ok: false, max_gate_height: 0 };
    const union = new Set();
    for (const v of opts) {
      await p.selectOption("#cmpFilter", v);
      await p.waitForTimeout(200);
      const cellsShown = await p.$$eval("#compare figure", (fs) => fs.map((f) => f.dataset.cell));
      const h = await p.$eval('section[aria-labelledby="cmpTitle"]', (e) => Math.round(e.getBoundingClientRect().height));
      out.per_option[v] = { figures: cellsShown.length, height_px: h };
      // pilihan gerbang: "J", atau "J:<keluarga>" bila gerbang besar dipecah per keluarga
      if (/^[A-Z](:[a-z0-9-]+)?$/.test(v)) { cellsShown.forEach((c) => union.add(c)); out.max_gate_height = Math.max(out.max_gate_height, h); }
    }
    const gated = [];
    for (const [costume, row] of Object.entries(manifestData.cells)) for (const [state, cell] of Object.entries(row)) if (cell.gate) gated.push(costume + "/" + state);
    out.gated_cells = gated.length;
    out.union_ok = gated.length === union.size && gated.every((c) => union.has(c));
    const perGate = {};
    for (const c of Object.values(manifestData.cells).flatMap((r) => Object.values(r))) if (c.gate) perGate[c.gate] = (perGate[c.gate] || 0) + 1;
    const shownPerGate = {};
    for (const [v, o] of Object.entries(out.per_option)) if (/^[A-Z](:[a-z0-9-]+)?$/.test(v)) shownPerGate[v[0]] = (shownPerGate[v[0]] || 0) + o.figures;
    out.counts_ok = Object.entries(perGate).every(([g, n]) => shownPerGate[g] === n);
    await p.selectOption("#cmpFilter", "semua");
    await p.waitForTimeout(600);
    return out;
  };
  // Lembar kontak hero: tiap state punya semua frame berurutan, bernomor, 2x, sama dengan sheet per piksel.
  const heroCheck = (p) => p.evaluate(async () => {
    const man = await (await fetch("manifest.json")).json();
    const row = man.cells["berserker-hero"] || {};
    const load = (src) => new Promise((res, rej) => { const im = new Image(); im.onload = () => res(im); im.onerror = () => rej(new Error(src)); im.src = src; });
    const out = { states: {}, problems: [] };
    for (const [state, cell] of Object.entries(row)) {
      const box = document.querySelector('.hero-state[data-state="' + state + '"]');
      if (!box) { out.problems.push(state + ": tidak ada lembar kontak"); continue; }
      const cvs = [...box.querySelectorAll(".strip canvas")];
      const caps = [...box.querySelectorAll(".strip figcaption")].map((c) => c.textContent);
      const seq = cvs.map((c) => +c.dataset.sheetFrame);
      const d = cell.canvas, im = await load(new URL(cell.sheet, document.baseURI).href);
      let pixelBad = 0, undrawn = 0, sizeBad = 0;
      cvs.forEach((c, i) => {
        if (c.dataset.drawn !== "1") undrawn++;
        const r = c.getBoundingClientRect();
        if (c.width !== d.w * 2 || c.height !== d.h * 2 || Math.round(r.width) !== d.w * 2 || Math.round(r.height) !== d.h * 2) sizeBad++;
        const off = document.createElement("canvas"); off.width = d.w * 2; off.height = d.h * 2;
        const ctx = off.getContext("2d"); ctx.imageSmoothingEnabled = false;
        ctx.drawImage(im, i * d.w, 0, d.w, d.h, 0, 0, d.w * 2, d.h * 2);
        const a = ctx.getImageData(0, 0, off.width, off.height).data, b = c.getContext("2d").getImageData(0, 0, off.width, off.height).data;
        for (let k = 0; k < a.length; k++) if (a[k] !== b[k]) { pixelBad++; break; }
      });
      const numbered = caps.every((t, i) => t.indexOf(i + " · " + cell.durations_ms[i] + " ms") === 0);
      const keyed = [...box.querySelectorAll(".strip figure.key")].map((f) => [...f.parentNode.children].indexOf(f));
      const strip = box.querySelector(".strip");
      const player = box.querySelector(".hero-player canvas");
      out.states[state] = { frames: cvs.length, expected: cell.frames, in_order: JSON.stringify(seq) === JSON.stringify(cvs.map((_, i) => i)),
        numbered, keyframe_marked: JSON.stringify(keyed) === JSON.stringify([cell.keyframe]), undrawn, size_bad: sizeBad, pixel_bad: pixelBad,
        scrollable: strip.scrollWidth > strip.clientWidth, strip_client_w: strip.clientWidth, player_ok: !!player && player.width === d.w * 2 };
      const o = out.states[state];
      if (o.frames !== o.expected) out.problems.push(state + ": " + o.frames + " frame tampil, manifest " + o.expected);
      if (!o.in_order) out.problems.push(state + ": frame tidak berurutan");
      if (!o.numbered) out.problems.push(state + ": nomor atau durasi di keterangan salah");
      if (!o.keyframe_marked) out.problems.push(state + ": frame kunci tidak ditandai tepat satu kali");
      if (o.undrawn || o.size_bad || o.pixel_bad) out.problems.push(state + ": undrawn " + o.undrawn + ", ukuran salah " + o.size_bad + ", beda piksel " + o.pixel_bad);
      if (!o.player_ok) out.problems.push(state + ": pemutar tidak ada atau ukuran salah");
    }
    if (!Object.keys(row).length) out.problems.push("manifest tidak punya sel hero");
    return out;
  });
  const heroGifCheck = (p) => p.evaluate(async () => {
    const man = await (await fetch("manifest.json")).json();
    const load = (src) => new Promise((res, rej) => { const im = new Image(); im.onload = () => res(im); im.onerror = () => rej(new Error(src)); im.src = src; });
    const out = {};
    for (const [state, cell] of Object.entries(man.cells["berserker-hero"] || {})) {
      const im = await load(new URL(cell.gif, document.baseURI).href);
      out[state] = im.naturalWidth + "x" + im.naturalHeight;
    }
    return out;
  });
  const blindState = (p) => p.$$eval("#blind figure", (fs) => fs.map((f) => ({ costume: f.dataset.costume, caption: f.querySelector("figcaption").textContent })));

  // ---- desktop
  const d = await open({ viewport: { width: 1280, height: 900 } });
  report.counts = await d.p.evaluate(() => ({
    real: document.querySelectorAll("#matrix .cell.real").length,
    new: document.querySelectorAll("#matrix .cell.new").length,
    new_by_gate: [...document.querySelectorAll("#matrix .cell.new")].reduce((o, e) => { const g = (e.getAttribute("aria-label").match(/gerbang (\w)/) || [])[1]; o[g] = (o[g] || 0) + 1; return o; }, {}),
    placeholder: document.querySelectorAll("#matrix .cell.ph").length,
    css_placeholder: document.querySelectorAll("#matrix .cell.css").length,
    not_applicable: document.querySelectorAll("#matrix .na-cell").length,
    rows: document.querySelectorAll("#matrix tbody tr:not(.group)").length,
    stats: document.getElementById("stats").innerText.replace(/\n/g, " | "),
  }));
  const manifest = manifestData;
  const expected = { cells: 0, applicable: 0 };
  for (const row of Object.values(manifest.cells)) expected.cells += Object.keys(row).length;
  for (const c of manifest.costumes) expected.applicable += Object.keys(c.applies || {}).length;
  report.expected = expected;
  check(report.counts.real + report.counts.new === expected.cells, "jumlah sel terisi di matriks != manifest");
  check(report.counts.real + report.counts.new + report.counts.placeholder === expected.applicable, "jumlah sel berlaku di matriks != applies");
  check(report.counts.css_placeholder === 0, "ada placeholder CSS (aset gagal dimuat)");
  const realSel = "#matrix .cell.real canvas";
  const h1 = await hashOf(d.p, realSel); await d.p.waitForTimeout(900); const h2 = await hashOf(d.p, realSel);
  report.animates = h1 !== h2;
  check(report.animates, "mode animasi tidak bergerak");
  report.blank_cells = await d.p.$$eval("#matrix .cell canvas:not([hidden])", (cs) => cs.filter((c) => { const x = c.getContext("2d").getImageData(0, 0, c.width, c.height).data; for (let i = 3; i < x.length; i += 4) if (x[i]) return false; return true; }).length);
  check(report.blank_cells === 0, "ada sel matriks yang kosong");
  report.blind_before = await blindState(d.p);
  check(report.blind_before.every((b) => /^#\d+$/.test(b.caption)), "label tes buta terlihat sebelum tombol ditekan");
  report.filter_desktop = await filterCheck(d.p);
  check(report.filter_desktop.union_ok && report.filter_desktop.counts_ok, "filter panel banding menghilangkan atau salah menghitung sel");
  await d.p.click("#btnStatic");
  await d.p.waitForTimeout(600);
  report.static_desktop = await staticCheck(d.p);
  check(!report.static_desktop.frame_mismatch.length && !report.static_desktop.pixel_mismatch.length, "mode statis != frame kunci (desktop)");
  check(report.static_desktop.hero_canvases >= 9 + 9, "mode statis: kanvas hero (pemutar + banding) tidak ikut diperiksa");
  report.hero_desktop = await heroCheck(d.p);
  check(!report.hero_desktop.problems.length, "lembar kontak hero (desktop): " + report.hero_desktop.problems.join("; "));
  report.hero_gifs = await heroGifCheck(d.p);
  check(Object.keys(report.hero_gifs).length === 9 && Object.values(report.hero_gifs).every((v) => v === "512x384"), "GIF hero tidak termuat 512x384");
  // latar terang/gelap/abu tengah: warna latar kanvas lembar kontak berganti dan kembali
  const bgOf = () => d.p.$eval(".strip .stage", (c) => getComputedStyle(c).backgroundColor);
  const filterOf = () => d.p.$eval(".strip canvas", (c) => getComputedStyle(c).filter);
  report.hero_bg = { light: await bgOf() };
  await d.p.click("#btnHeroDark"); report.hero_bg.dark = await bgOf();
  await d.p.locator("#heroSection").screenshot({ path: path.join(OUT, "hero-dark.png") });
  await d.p.click("#btnHeroGray"); report.hero_bg.gray = await bgOf();
  await d.p.locator("#heroSection").screenshot({ path: path.join(OUT, "hero-gray.png") });
  await d.p.click("#btnHeroLight"); report.hero_bg.light_again = await bgOf();
  check(report.hero_bg.light === "rgb(250, 247, 240)" && report.hero_bg.dark === "rgb(24, 28, 44)" && report.hero_bg.gray === "rgb(128, 128, 128)" &&
    report.hero_bg.light_again === report.hero_bg.light, "pilihan latar terang/gelap/abu hero tidak bekerja");
  await d.p.locator("#heroSection").screenshot({ path: path.join(OUT, "hero-light.png") });
  // halo: kontur krem 1 px lewat CSS drop-shadow (hanya preview); piksel hasil render diperiksa dari tangkapan layar per kombinasi
  report.hero_halo = { off: await filterOf() };
  await d.p.click("#btnHeroHalo");
  report.hero_halo.on = await filterOf();
  report.hero_halo.pressed = await d.p.$eval("#btnHeroHalo", (b) => b.getAttribute("aria-pressed"));
  check(report.hero_halo.off === "none" && (report.hero_halo.on.match(/drop-shadow/g) || []).length === 4 && report.hero_halo.on.includes("rgb(232, 218, 186)"),
    "halo tidak menyalakan empat drop-shadow krem");
  await d.p.click("#btnHeroHalo");
  report.hero_halo.off_again = await filterOf();
  check(report.hero_halo.off_again === "none", "halo tidak mati kembali");
  fs.mkdirSync(path.join(OUT, "halo"), { recursive: true });
  for (const [bg, btn] of [["terang", "#btnHeroLight"], ["gelap", "#btnHeroDark"], ["abu", "#btnHeroGray"]]) {
    await d.p.click(btn);
    for (const halo of [false, true]) {
      const on = (await d.p.$eval("#btnHeroHalo", (b) => b.getAttribute("aria-pressed"))) === "true";
      if (on !== halo) await d.p.click("#btnHeroHalo");
      await d.p.waitForTimeout(150);
      await d.p.locator('.hero-state[data-state="idle"] .strip figure:first-child .stage').screenshot({ path: path.join(OUT, "halo", "idle-" + bg + (halo ? "-halo" : "") + ".png") });
    }
  }
  await d.p.click("#btnHeroHalo");     // matikan lagi
  await d.p.click("#btnHeroLight");
  // state yang tidak berputar: indikator "diputar sekali" dan tombol Putar ulang hanya untuk rage; Putar ulang memulai dari frame 0, lalu berhenti di frame terakhir
  await d.p.click("#btnAnim");                                    // uji gerak harus di mode Animasi (tombol Statis sudah ditekan di atas)
  report.hero_once = await d.p.evaluate(() => ({
    badges: [...document.querySelectorAll(".hero-state .once")].map((b) => b.closest(".hero-state").dataset.state),
    replay: [...document.querySelectorAll(".hero-state button.replay")].map((b) => b.closest(".hero-state").dataset.state),
  }));
  check(JSON.stringify(report.hero_once.badges) === '["rage","victory"]' && JSON.stringify(report.hero_once.replay) === '["rage","victory"]',
    "indikator diputar sekali dan Putar ulang harus hanya untuk rage dan victory");
  const rageCell = manifestData.cells["berserker-hero"].rage, rageTotal = rageCell.durations_ms.reduce((a, b) => a + b, 0);
  await d.p.locator('.hero-state[data-state="rage"]').scrollIntoViewIfNeeded();
  const frameNow = () => d.p.$eval('.hero-state[data-state="rage"] .hero-player canvas', (c) => +c.dataset.frame);
  await d.p.waitForTimeout(rageTotal + 600);                      // pastikan sudah berhenti sebelum diputar ulang
  report.hero_replay = { before: await frameNow() };
  await d.p.click('.hero-state[data-state="rage"] button.replay');
  await d.p.waitForTimeout(120);
  report.hero_replay.just_after = await frameNow();
  const seen = new Set([report.hero_replay.just_after]);
  for (let k = 0; k < 14; k++) { await d.p.waitForTimeout(220); seen.add(await frameNow()); }
  await d.p.waitForTimeout(rageTotal);                            // total lewat lama, tetap di frame terakhir
  report.hero_replay.frames_seen = [...seen].sort((a, b) => a - b);
  report.hero_replay.after = await frameNow();
  await d.p.waitForTimeout(1200);
  report.hero_replay.later = await frameNow();
  check(report.hero_replay.before === rageCell.frames - 1 && report.hero_replay.just_after <= 2 && report.hero_replay.after === rageCell.frames - 1 &&
    report.hero_replay.later === rageCell.frames - 1 && report.hero_replay.frames_seen.length >= 6,
    "Putar ulang rage: harus mulai dari frame awal, melewati beberapa frame, lalu berhenti di frame terakhir");
  // victory (20 frame, diputar sekali): Putar ulang mulai dari frame awal, melewati banyak frame, lalu berhenti di frame terakhir
  const vicCell = manifestData.cells["berserker-hero"].victory, vicTotal = vicCell.durations_ms.reduce((a, b) => a + b, 0);
  await d.p.locator('.hero-state[data-state="victory"]').scrollIntoViewIfNeeded();
  const vicNow = () => d.p.$eval('.hero-state[data-state="victory"] .hero-player canvas', (c) => +c.dataset.frame);
  await d.p.waitForTimeout(vicTotal + 600);
  const vicBefore = await vicNow();
  await d.p.click('.hero-state[data-state="victory"] button.replay');
  await d.p.waitForTimeout(120);
  const vicSeen = new Set([await vicNow()]);
  for (let k = 0; k < 18; k++) { await d.p.waitForTimeout(220); vicSeen.add(await vicNow()); }
  await d.p.waitForTimeout(vicTotal);
  report.hero_replay_victory = { before: vicBefore, frames_seen: [...vicSeen].sort((a, b) => a - b), after: await vicNow() };
  check(vicBefore === vicCell.frames - 1 && report.hero_replay_victory.after === vicCell.frames - 1 && vicSeen.size >= 6 && Math.min(...vicSeen) <= 2,
    "Putar ulang victory: harus mulai dari frame awal, melewati banyak frame, lalu berhenti di frame terakhir");
  await d.p.click("#btnStatic");                                  // kembali ke mode Statis: Putar ulang dinonaktifkan dan frame kunci tetap
  await d.p.waitForTimeout(300);
  report.hero_replay_static = { frame_before: await frameNow(), disabled: await d.p.$eval('.hero-state[data-state="rage"] button.replay', (b) => b.getAttribute("aria-disabled")) };
  await d.p.click('.hero-state[data-state="rage"] button.replay', { force: true });   // aria-disabled: Playwright menganggapnya tidak aktif, jadi dipaksa
  await d.p.waitForTimeout(400);
  report.hero_replay_static.frame_after = await frameNow();
  check(report.hero_replay_static.frame_before === rageCell.keyframe && report.hero_replay_static.frame_after === rageCell.keyframe && report.hero_replay_static.disabled === "true",
    "mode Statis: Putar ulang harus nonaktif dan rage tetap di frame kunci");
  const s1 = await hashOf(d.p, realSel); await d.p.waitForTimeout(900); const s2 = await hashOf(d.p, realSel);
  report.static_button_holds = s1 === s2;
  check(report.static_button_holds, "tombol Statis tidak menghentikan gerak");
  report.compare_figures = await d.p.$$eval("#compare figure", (fs) => fs.length);
  await d.p.locator('section[aria-labelledby="cmpTitle"]').screenshot({ path: path.join(OUT, "compare-static.png") });
  await d.p.locator('section[aria-labelledby="blindTitle"]').screenshot({ path: path.join(OUT, "blind-hidden.png") });
  await d.p.click("#btnReveal");
  report.blind_revealed_ok = (await blindState(d.p)).every((b) => / · /.test(b.caption));
  check(report.blind_revealed_ok, "tombol label tes buta tidak menampilkan label");
  await d.p.locator('section[aria-labelledby="blindTitle"]').screenshot({ path: path.join(OUT, "blind-revealed.png") });
  // 4x dari sheet 1x = sheet4x (untuk sel yang masih punya sheet4x)
  report.sheet4x_vs_1x_scaled = await d.p.evaluate(async () => {
    const m = await (await fetch("manifest.json")).json();
    const load = (src) => new Promise((res, rej) => { const im = new Image(); im.onload = () => res(im); im.onerror = rej; im.src = new URL(src, location.href).href; });
    let frames = 0, bad = 0, cellsWith = 0, cellsWithout = 0;
    for (const row of Object.values(m.cells)) for (const cell of Object.values(row)) {
      if (!cell.sheet4x) { cellsWithout++; continue; }
      cellsWith++;
      const one = await load(cell.sheet), four = await load(cell.sheet4x);
      for (let i = 0; i < cell.frames; i++) {
        const a = document.createElement("canvas"); a.width = 256; a.height = 192;
        const ca = a.getContext("2d"); ca.imageSmoothingEnabled = false; ca.drawImage(one, i * 64, 0, 64, 48, 0, 0, 256, 192);
        const b = document.createElement("canvas"); b.width = 256; b.height = 192;
        const cb = b.getContext("2d"); cb.drawImage(four, i * 256, 0, 256, 192, 0, 0, 256, 192);
        const x = ca.getImageData(0, 0, 256, 192).data, y = cb.getImageData(0, 0, 256, 192).data;
        frames++; for (let k = 0; k < x.length; k++) if (x[k] !== y[k]) { bad++; break; }
      }
    }
    return { cells_with_sheet4x: cellsWith, cells_without_sheet4x: cellsWithout, frames_compared: frames, frames_different: bad };
  });
  check(report.sheet4x_vs_1x_scaled.frames_different === 0, "sheet 1x diperbesar != sheet4x");
  report.desktop_errors = d.errors; report.desktop_bad_requests = d.bad;
  check(!d.errors.length && !d.bad.length, "console error atau request gagal (desktop)");
  await d.p.screenshot({ path: path.join(OUT, "preview-desktop-static.png"), fullPage: true });
  await d.ctx.close();

  const d2 = await open({ viewport: { width: 1280, height: 900 } });
  report.blind_same_order_after_reload = JSON.stringify((await blindState(d2.p)).map((x) => x.costume)) === JSON.stringify(report.blind_before.map((x) => x.costume));
  check(report.blind_same_order_after_reload, "urutan tes buta berubah setelah muat ulang");
  await d2.ctx.close();

  // ---- ponsel + prefers-reduced-motion
  const m = await open({ viewport: { width: 390, height: 844 }, reducedMotion: "reduce" });
  const r1 = await hashOf(m.p, realSel); await m.p.waitForTimeout(1200); const r2 = await hashOf(m.p, realSel);
  report.reduced_motion_static = r1 === r2;
  check(report.reduced_motion_static, "reduced motion masih bergerak");
  report.filter_phone = await filterCheck(m.p);
  check(report.filter_phone.union_ok && report.filter_phone.counts_ok, "filter panel banding (ponsel) menghilangkan sel");
  check(report.filter_phone.max_gate_height <= 3000, "tampilan satu gerbang di ponsel > 3000 px");
  await m.p.waitForTimeout(600);
  report.static_phone = await staticCheck(m.p);
  check(!report.static_phone.frame_mismatch.length && !report.static_phone.pixel_mismatch.length, "reduced motion != frame kunci (ponsel)");
  report.phone_overflow = await m.p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  check(report.phone_overflow === 0, "scroll horizontal di ponsel");
  report.hero_phone = await heroCheck(m.p);
  check(!report.hero_phone.problems.length, "lembar kontak hero (ponsel): " + report.hero_phone.problems.join("; "));
  report.hero_phone_scroll = await m.p.evaluate(() => [...document.querySelectorAll(".hero-state")].map((b) => {
    const s = b.querySelector(".strip"), before = s.scrollLeft; s.scrollLeft = 400; const moved = s.scrollLeft;
    s.scrollLeft = before;
    return { state: b.dataset.state, strip_w: Math.round(s.getBoundingClientRect().width), scrollable: s.scrollWidth > s.clientWidth, moved_px: moved - before,
      within_viewport: s.getBoundingClientRect().right <= innerWidth };
  }));
  check(report.hero_phone_scroll.length === 9 && report.hero_phone_scroll.every((x) => x.scrollable && x.moved_px > 0 && x.within_viewport),
    "lembar kontak hero di ponsel tidak bisa digulir atau melebihi layar");
  report.phone_overflow_after_hero = await m.p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  check(report.phone_overflow_after_hero === 0, "scroll horizontal di ponsel setelah menggulir lembar kontak hero");
  await m.p.locator("#heroSection").screenshot({ path: path.join(OUT, "hero-phone.png") });
  await m.p.screenshot({ path: path.join(OUT, "preview-phone.png") });
  const latest = report.filter_phone.options.filter((o) => /^[A-Z](:[a-z0-9-]+)?$/.test(o))[0];
  if (latest) { await m.p.selectOption("#cmpFilter", latest); await m.p.waitForTimeout(600); }
  await m.p.locator('section[aria-labelledby="cmpTitle"]').screenshot({ path: path.join(OUT, "compare-phone.png") });
  await m.p.locator('section[aria-labelledby="blindTitle"]').screenshot({ path: path.join(OUT, "blind-phone.png") });
  report.phone_errors = m.errors; report.phone_bad_requests = m.bad;
  check(!m.errors.length && !m.bad.length, "console error atau request gagal (ponsel)");
  await m.ctx.close();

  await browser.close();
  server.close();
  report.fails = fails;
  fs.writeFileSync(path.join(OUT, "e2e.json"), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report, null, 2));
  console.log(fails.length ? "E2E: " + fails.length + " GAGAL" : "E2E: LULUS");
  process.exit(fails.length ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });
