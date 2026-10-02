// Jalankan: node --test pack/resolver.test.js   (test runner bawaan Node, tanpa dependensi)
"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const P = require("./resolver.js");

const manifestPath = path.join(__dirname, "manifest.json");
const M = JSON.parse(fs.readFileSync(manifestPath, "utf8"));

function gifSize(file) {
  const b = fs.readFileSync(file);
  assert.equal(b.toString("ascii", 0, 3), "GIF", file + " bukan GIF");
  return { w: b.readUInt16LE(6), h: b.readUInt16LE(8) };
}

function pngSize(file) {
  const b = fs.readFileSync(file);
  assert.equal(b.toString("ascii", 1, 4), "PNG", file + " bukan PNG");
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}

// Fixture kecil dari sel asli: test perilaku fallback tidak ikut berubah saat aset baru ditambahkan ke manifest.
const FIX = { cells: { normal: { idle: M.cells.normal.idle, happy: M.cells.normal.happy }, hacker: { idle: M.cells.hacker.idle } } };

test("kombinasi valid: sel asli terkena tepat (exact)", () => {
  for (const [c, s] of [["normal", "idle"], ["normal", "happy"], ["greek-philosopher", "thinking"], ["academic", "idle"],
    ["scientist", "thinking"], ["hacker", "idle"], ["detective", "thinking"]]) {
    const r = P.resolve(M, c, s);
    assert.equal(r.kind, "exact", c + "/" + s);
    assert.deepEqual(r.resolved, { costume: c, state: s });
    assert.equal(r.cell.status, "final");
    assert.equal(r.cell.origin, "asli", c + "/" + s);
  }
});

test("state hilang: jatuh ke kostum+idle bila ada", () => {
  const r = P.resolve(FIX, "hacker", "victory");
  assert.equal(r.kind, "fallback");
  assert.equal(r.step, "costume+idle");
  assert.deepEqual(r.resolved, { costume: "hacker", state: "idle" });
  assert.deepEqual(r.tried, ["hacker/victory", "hacker/idle"]);
});

test("state hilang tanpa idle kostum: jatuh ke normal+state, lalu normal+idle", () => {
  const a = P.resolve(FIX, "greek-philosopher", "happy");
  assert.equal(a.step, "normal+state");
  assert.deepEqual(a.resolved, { costume: "normal", state: "happy" });
  const b = P.resolve(FIX, "greek-philosopher", "victory");
  assert.equal(b.step, "normal+idle");
  assert.deepEqual(b.tried, ["greek-philosopher/victory", "greek-philosopher/idle", "normal/victory", "normal/idle"]);
});

test("kostum hilang atau tidak dikenal: jatuh ke normal", () => {
  assert.equal(P.resolve(FIX, "judge", "judging").step, "normal+idle");
  // Kostum yang tidak dikenal manifest (contoh ini dulu memakai "pirate", yang sejak Gerbang H punya idle sendiri).
  assert.equal(P.resolve(M, "kostum-tak-dikenal", "happy").step, "normal+state");
  assert.equal(P.resolve(M, "kostum-tak-dikenal", "tidak-ada").step, "normal+idle");
  // Kostum yang sudah punya idle: state tanpa aset jatuh ke idle kostum itu sendiri, bukan ke normal.
  assert.equal(P.resolve(M, "pirate", "happy").step, "costume+idle");
});

test("pemetaan Gerbang B: wisuda di academic/idle, academic/victory bukan wisuda", () => {
  const idle = P.resolve(M, "academic", "idle");
  assert.equal(idle.kind, "exact");
  assert.equal(idle.cell.source, "wisuda");
  assert.equal(idle.cell.keyframe, 0);
  const v = P.resolve(M, "academic", "victory");
  assert.ok(!(v.kind === "exact" && v.cell.source === "wisuda"), "wisuda masih terpetakan ke academic/victory");
});

test("Gerbang C: sembilan sel baru terpetakan exact dan bergerbang C, sel asli di baris yang sama tidak tergeser", () => {
  const want = [["greek-philosopher", "idle"], ["greek-philosopher", "victory"], ["greek-philosopher", "defeated"],
    ["academic", "thinking"], ["academic", "victory"], ["academic", "defeated"],
    ["normal", "thinking"], ["normal", "victory"], ["normal", "defeated"]];
  for (const [c, s] of want) {
    const r = P.resolve(M, c, s);
    assert.equal(r.kind, "exact", c + "/" + s);
    assert.equal(r.cell.gate, "C", c + "/" + s);
    assert.equal(r.cell.source, c + "-" + s);
  }
  assert.equal(P.resolve(M, "greek-philosopher", "thinking").cell.source, "filsuf-yunani");
  assert.equal(P.resolve(M, "academic", "idle").cell.source, "wisuda");
  assert.equal(P.resolve(M, "normal", "idle").cell.source, "ngopi-santai");
  assert.equal(P.resolve(M, "normal", "happy").cell.source, "makan-pisang");
});

test("keyframe: setiap sel punya frame kunci valid dan reduced motion selalu menampilkan frame itu", () => {
  for (const [costume, row] of Object.entries(M.cells)) {
    for (const [state, cell] of Object.entries(row)) {
      const tag = costume + "/" + state;
      assert.ok(Number.isInteger(cell.keyframe), tag + ": keyframe bukan bilangan bulat");
      assert.ok(cell.keyframe >= 0 && cell.keyframe < cell.frames, tag + ": keyframe di luar rentang frame");
      const total = cell.durations_ms.reduce((a, b) => a + b, 0);
      for (const t of [0, 1, 99, Math.floor(total / 3), total - 1, total, total * 7 + 13]) {
        assert.equal(P.frameAt(cell, t, true), cell.keyframe, tag + " t=" + t);
      }
    }
  }
});

test("input dinormalkan: spasi, huruf besar, kosong, bukan string", () => {
  assert.equal(P.resolve(M, "  Normal ", "IDLE").kind, "exact");
  assert.deepEqual(P.resolve(M, "", "").resolved, { costume: "normal", state: "idle" });
  assert.deepEqual(P.resolve(M, null, undefined).resolved, { costume: "normal", state: "idle" });
  assert.deepEqual(P.resolve(M, 42, {}).resolved, { costume: "normal", state: "idle" });
});

test("manifest rusak: selalu placeholder, tidak pernah melempar", () => {
  const throwing = {};
  Object.defineProperty(throwing, "cells", { get() { throw new Error("boom"); } });
  const brokenCell = (cell) => ({ cells: { normal: { idle: cell } } });
  const cases = [
    null, undefined, "bukan json", 42, [], {}, { cells: null }, { cells: [] }, { cells: { normal: "x" } },
    throwing,
    brokenCell(null), brokenCell({}), brokenCell({ sheet: 5, frames: 1, durations_ms: [100] }),
    brokenCell({ sheet: "a.png", frames: 2, durations_ms: [100] }),
    brokenCell({ sheet: "a.png", frames: 1, durations_ms: [0] }),
    brokenCell({ sheet: "a.png", frames: 1.5, durations_ms: [100] }),
    brokenCell({ sheet: "", frames: 1, durations_ms: [100] }),
  ];
  for (const m of cases) {
    let r;
    assert.doesNotThrow(() => { r = P.resolve(m, "judge", "victory"); });
    assert.equal(r.kind, "placeholder", JSON.stringify(m));
    assert.equal(r.cell, null);
    assert.ok(r.tried.length >= 1 && r.tried.length <= 4);
    assert.ok(typeof r.reason === "string" && r.reason);
  }
});

test("sel rusak dilewati, rantai berlanjut ke sel valid berikutnya", () => {
  const m = { cells: { hacker: { victory: { sheet: "x.png" } }, normal: { idle: M.cells.normal.idle } } };
  const r = P.resolve(m, "hacker", "victory");
  assert.equal(r.step, "normal+idle");
});

test("seluruh matriks kostum x state teresolusi tanpa error", () => {
  // Dimensi matriks mengikuti manifest (dulu 12 x 9; sejak Fase 2 lanjutan 32 kostum x 13 state).
  const { costumes, states } = P.matrix(M);
  assert.equal(costumes.length, M.costumes.length);
  assert.equal(states.length, M.states.length);
  const kinds = { exact: 0, fallback: 0, placeholder: 0 };
  for (const c of costumes) for (const s of states) {
    const r = P.resolve(M, c.id, s.id);
    kinds[r.kind]++;
    assert.ok(r.cell, "manifest asli selalu punya normal/idle, jadi tidak boleh placeholder");
  }
  // Jumlah sel exact mengikuti isi manifest; 7 aset asli pra-Fase 2 harus tetap ada.
  const all = Object.values(M.cells).flatMap((row) => Object.values(row));
  assert.equal(kinds.exact, all.length);
  assert.equal(all.filter((c) => c.origin === "asli").length, 7);
  assert.equal(kinds.exact + kinds.fallback, costumes.length * states.length);
});

test("applies: tabel sel berlaku 163 (78 kostum lama + 85 kostum baru), semua sel terisi berlaku", () => {
  const { costumes, states } = P.matrix(M);
  let total = 0, req = 0;
  const old12 = ["normal", "referee", "judge", "skeptic", "champion", "greek-philosopher", "academic", "scientist",
    "mathematician", "lawyer", "hacker", "detective"];
  let oldTotal = 0;
  for (const c of costumes) for (const s of states) {
    const rule = P.cellRule(c, s);
    if (!rule) continue;
    total++; if (rule === "required") req++;
    if (old12.includes(c.id)) oldTotal++;
  }
  assert.equal(total, 163);
  assert.equal(oldTotal, 78);
  for (const [costume, row] of Object.entries(M.cells)) {
    const c = costumes.find((x) => x.id === costume);
    for (const state of Object.keys(row)) {
      assert.ok(P.cellRule(c, states.find((x) => x.id === state)), costume + "/" + state + " terisi tapi tidak berlaku");
    }
  }
  // state tanpa "applies" (manifest lama) tetap memakai aturan required + allowlist
  const legacy = { id: "judge" };
  assert.equal(P.cellRule(legacy, { id: "judging", required: false, costumes: ["judge"] }), "optional");
  assert.equal(P.cellRule({ id: "normal" }, { id: "judging", required: false, costumes: ["judge"] }), null);
  assert.equal(P.cellRule({ id: "normal" }, { id: "idle", required: true }), "required");
});

test("varian tanpa aset jatuh ke induk; induk tanpa aset jatuh ke normal", () => {
  const cell = (n) => ({ sheet: n + ".png", frames: 1, durations_ms: [100] });
  const m = {
    costumes: [{ id: "normal" }, { id: "knight" }, { id: "knight-heavy", base: "knight" }, { id: "viking-gestir", base: "viking" },
      { id: "normal-gblk", base: "normal" }],
    cells: { normal: { idle: cell("n"), happy: cell("nh") }, knight: { idle: cell("k"), attack: cell("ka") } },
  };
  let r = P.resolve(m, "knight-heavy", "attack");
  assert.equal(r.step, "base+state");
  assert.deepEqual(r.tried, ["knight-heavy/attack", "knight-heavy/idle", "knight/attack"]);
  r = P.resolve(m, "knight-heavy", "victory");
  assert.equal(r.step, "base+idle");
  assert.deepEqual(r.resolved, { costume: "knight", state: "idle" });
  r = P.resolve(m, "viking-gestir", "happy");  // induk ada di daftar tapi tanpa aset
  assert.equal(r.step, "normal+state");
  assert.deepEqual(r.tried, ["viking-gestir/happy", "viking-gestir/idle", "viking/happy", "viking/idle", "normal/happy"]);
  r = P.resolve(m, "normal-gblk", "reveal");  // base = normal: langkah base dilewati
  assert.equal(r.step, "normal+idle");
  assert.deepEqual(r.tried, ["normal-gblk/reveal", "normal-gblk/idle", "normal/reveal", "normal/idle"]);
  // manifest tanpa field base: rantai lama
  const old = { cells: m.cells };
  assert.deepEqual(P.resolve(old, "knight-heavy", "attack").tried, ["knight-heavy/attack", "knight-heavy/idle", "normal/attack", "normal/idle"]);
  // base yang rusak tidak membuat error
  for (const bad of [42, null, {}, "", "   "]) {
    const mb = { costumes: [{ id: "x", base: bad }], cells: m.cells };
    assert.doesNotThrow(() => P.resolve(mb, "x", "victory"));
    assert.deepEqual(P.resolve(mb, "x", "victory").tried, ["x/victory", "x/idle", "normal/victory", "normal/idle"]);
  }
  const thrower = { cells: m.cells };
  Object.defineProperty(thrower, "costumes", { get() { throw new Error("boom"); } });
  assert.equal(P.resolve(thrower, "knight-heavy", "victory").step, "normal+idle");
});

test("frame kunci keputusan pemilik: champion-victory f4, judge-judging f9, skeptic-attack f7", () => {
  assert.equal(M.cells.champion.victory.keyframe, 4);
  assert.equal(M.cells.judge.judging.keyframe, 9);
  assert.equal(M.cells.skeptic.attack.keyframe, 7);
});

test("sheet4x opsional: sel tanpa sheet4x tetap valid dan teresolusi exact", () => {
  const cell = { sheet: "a.png", frames: 2, durations_ms: [100, 100], loop: true, keyframe: 1 };
  assert.ok(P.validCell(cell));
  const r = P.resolve({ cells: { normal: { idle: cell } } }, "normal", "idle");
  assert.equal(r.kind, "exact");
  assert.equal(P.frameAt(cell, 0, true), 1);
});

test("frameAt: mengikuti durasi, loop, dan reduced motion", () => {
  const cell = { sheet: "a.png", frames: 3, durations_ms: [100, 200, 300], loop: true, keyframe: 2 };
  assert.equal(P.frameAt(cell, 0), 0);
  assert.equal(P.frameAt(cell, 99), 0);
  assert.equal(P.frameAt(cell, 100), 1);
  assert.equal(P.frameAt(cell, 350), 2);
  assert.equal(P.frameAt(cell, 600), 0); // loop
  assert.equal(P.frameAt(cell, 150, true), 2); // statis
  assert.equal(P.frameAt({ ...cell, loop: false }, 5000), 2);
  assert.equal(P.frameAt(null, 100), 0);
});

test("manifest: setiap asset yang dirujuk benar-benar ada dan ukurannya cocok", () => {
  const dir = path.dirname(manifestPath);
  const { w, h } = M.canvas;
  for (const [costume, row] of Object.entries(M.cells)) {
    for (const [state, cell] of Object.entries(row)) {
      assert.ok(P.validCell(cell), costume + "/" + state);
      for (const key of ["sheet", "gif"].concat(cell.sheet4x ? ["sheet4x"] : [])) {
        assert.ok(fs.existsSync(path.join(dir, cell[key])), costume + "/" + state + " " + key + " hilang: " + cell[key]);
      }
      const s1 = pngSize(path.join(dir, cell.sheet));
      assert.deepEqual(s1, { w: w * cell.frames, h: h }, cell.sheet);
      if (cell.sheet4x) {  // opsional untuk aset baru sejak Gerbang D
        const s4 = pngSize(path.join(dir, cell.sheet4x));
        assert.deepEqual(s4, { w: w * 4 * cell.frames, h: h * 4 }, cell.sheet4x);
      }
      assert.ok(cell.keyframe >= 0 && cell.keyframe < cell.frames);
    }
  }
  for (const x of M.extras) {
    assert.ok(fs.existsSync(path.join(dir, x.gif)) && fs.existsSync(path.join(dir, x.sheet)), x.source);
  }
});

test("aset baru: ditandai, punya gerbang, terhubung ke file yang ada dengan ukuran cocok", () => {
  const dir = path.dirname(manifestPath);
  const baru = [];
  for (const [costume, row] of Object.entries(M.cells)) {
    for (const [state, cell] of Object.entries(row)) {
      assert.ok(cell.origin === "asli" || cell.origin === "baru", costume + "/" + state + " origin: " + cell.origin);
      if (cell.origin !== "baru") continue;
      baru.push(costume + "/" + state);
      assert.ok(/^[A-Z]$/.test(cell.gate || ""), costume + "/" + state + " tanpa gerbang");
      assert.equal(cell.source, costume + "-" + state, "nama file aset baru mengikuti <kostum>-<state>");
      assert.deepEqual(pngSize(path.join(dir, cell.sheet)), { w: 64 * cell.frames, h: 48 });
      if (cell.sheet4x) assert.deepEqual(pngSize(path.join(dir, cell.sheet4x)), { w: 256 * cell.frames, h: 192 });
      assert.deepEqual(gifSize(path.join(dir, cell.gif)), { w: 512, h: 384 });
      assert.equal(P.resolve(M, costume, state).kind, "exact");
    }
  }
  assert.ok(baru.length >= 1, "belum ada aset baru di manifest");
});

test("GIF semua sel berukuran 512x384 (kanvas 64x48 x8)", () => {
  const dir = path.dirname(manifestPath);
  for (const row of Object.values(M.cells)) {
    for (const cell of Object.values(row)) {
      assert.deepEqual(gifSize(path.join(dir, cell.gif)), { w: M.canvas.w * M.gif_scale, h: M.canvas.h * M.gif_scale }, cell.gif);
    }
  }
});
