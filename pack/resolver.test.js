// Jalankan: node --test pack/resolver.test.js   (test runner bawaan Node, tanpa dependensi)
"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const P = require("./resolver.js");

const manifestPath = path.join(__dirname, "manifest.json");
const M = JSON.parse(fs.readFileSync(manifestPath, "utf8"));

function pngSize(file) {
  const b = fs.readFileSync(file);
  assert.equal(b.toString("ascii", 1, 4), "PNG", file + " bukan PNG");
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}

test("kombinasi valid: sel asli terkena tepat (exact)", () => {
  for (const [c, s] of [["normal", "idle"], ["normal", "happy"], ["greek-philosopher", "thinking"], ["academic", "victory"],
    ["scientist", "thinking"], ["hacker", "idle"], ["detective", "thinking"]]) {
    const r = P.resolve(M, c, s);
    assert.equal(r.kind, "exact", c + "/" + s);
    assert.deepEqual(r.resolved, { costume: c, state: s });
    assert.equal(r.cell.status, "final");
  }
});

test("state hilang: jatuh ke kostum+idle bila ada", () => {
  const r = P.resolve(M, "hacker", "victory");
  assert.equal(r.kind, "fallback");
  assert.equal(r.step, "costume+idle");
  assert.deepEqual(r.resolved, { costume: "hacker", state: "idle" });
  assert.deepEqual(r.tried, ["hacker/victory", "hacker/idle"]);
});

test("state hilang tanpa idle kostum: jatuh ke normal+state, lalu normal+idle", () => {
  const a = P.resolve(M, "greek-philosopher", "happy");
  assert.equal(a.step, "normal+state");
  assert.deepEqual(a.resolved, { costume: "normal", state: "happy" });
  const b = P.resolve(M, "greek-philosopher", "victory");
  assert.equal(b.step, "normal+idle");
  assert.deepEqual(b.tried, ["greek-philosopher/victory", "greek-philosopher/idle", "normal/victory", "normal/idle"]);
});

test("kostum hilang atau tidak dikenal: jatuh ke normal", () => {
  assert.equal(P.resolve(M, "judge", "judging").step, "normal+idle");
  assert.equal(P.resolve(M, "pirate", "happy").step, "normal+state");
  assert.equal(P.resolve(M, "pirate", "tidak-ada").step, "normal+idle");
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

test("seluruh matriks 12 x 9 teresolusi tanpa error", () => {
  const { costumes, states } = P.matrix(M);
  assert.equal(costumes.length, 12);
  assert.equal(states.length, 9);
  const kinds = { exact: 0, fallback: 0, placeholder: 0 };
  for (const c of costumes) for (const s of states) {
    const r = P.resolve(M, c.id, s.id);
    kinds[r.kind]++;
    assert.ok(r.cell, "manifest asli selalu punya normal/idle, jadi tidak boleh placeholder");
  }
  assert.equal(kinds.exact, 7);
  assert.equal(kinds.exact + kinds.fallback, 108);
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
      for (const key of ["sheet", "sheet4x", "gif"]) {
        assert.ok(fs.existsSync(path.join(dir, cell[key])), costume + "/" + state + " " + key + " hilang: " + cell[key]);
      }
      const s1 = pngSize(path.join(dir, cell.sheet));
      assert.deepEqual(s1, { w: w * cell.frames, h: h }, cell.sheet);
      const s4 = pngSize(path.join(dir, cell.sheet4x));
      assert.deepEqual(s4, { w: w * 4 * cell.frames, h: h * 4 }, cell.sheet4x);
      assert.ok(cell.keyframe >= 0 && cell.keyframe < cell.frames);
    }
  }
  for (const x of M.extras) {
    assert.ok(fs.existsSync(path.join(dir, x.gif)) && fs.existsSync(path.join(dir, x.sheet)), x.source);
  }
});
