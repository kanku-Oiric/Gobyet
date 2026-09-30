/*
 * Gobyet Character Pack: resolver kostum x state.
 *
 * resolve(manifest, costume, state) tidak pernah melempar error dan selalu
 * mengembalikan sesuatu yang bisa dirender. Urutan fallback:
 *   kostum+state -> kostum+idle -> normal+state -> normal+idle -> placeholder
 *
 * Dipakai di browser (window.GobyetPack) maupun Node (require). Tanpa dependensi.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.GobyetPack = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  var BASE_COSTUME = "normal";
  var BASE_STATE = "idle";
  var STEPS = ["costume+state", "costume+idle", "normal+state", "normal+idle"];

  function name(value, fallback) {
    if (typeof value !== "string") return fallback;
    var v = value.trim().toLowerCase();
    return v ? v : fallback;
  }

  function isObject(v) {
    return v !== null && typeof v === "object" && !Array.isArray(v);
  }

  /* Sel dianggap layak render hanya bila semua field yang dibutuhkan renderer valid. */
  function validCell(cell) {
    if (!isObject(cell)) return false;
    if (typeof cell.sheet !== "string" || !cell.sheet) return false;
    var n = cell.frames;
    if (typeof n !== "number" || !isFinite(n) || n < 1 || Math.floor(n) !== n) return false;
    var d = cell.durations_ms;
    if (!Array.isArray(d) || d.length !== n) return false;
    for (var i = 0; i < d.length; i++) {
      if (typeof d[i] !== "number" || !isFinite(d[i]) || d[i] <= 0) return false;
    }
    return true;
  }

  function lookup(manifest, costume, state) {
    try {
      if (!isObject(manifest) || !isObject(manifest.cells)) return null;
      var row = manifest.cells[costume];
      if (!isObject(row)) return null;
      var cell = row[state];
      return validCell(cell) ? cell : null;
    } catch (e) {
      return null; // getter yang melempar, proxy aneh, dsb.
    }
  }

  function canvas(manifest) {
    try {
      var c = manifest && manifest.canvas;
      if (isObject(c) && c.w > 0 && c.h > 0) return { w: c.w, h: c.h };
    } catch (e) { /* abaikan */ }
    return { w: 64, h: 48 };
  }

  function placeholder(costume, state, tried, reason) {
    return {
      kind: "placeholder",
      step: "placeholder",
      requested: { costume: costume, state: state },
      resolved: null,
      cell: null,
      tried: tried,
      reason: reason,
    };
  }

  function resolve(manifest, costume, state) {
    var c = name(costume, BASE_COSTUME);
    var s = name(state, BASE_STATE);
    var tried = [];
    try {
      var chain = [[c, s], [c, BASE_STATE], [BASE_COSTUME, s], [BASE_COSTUME, BASE_STATE]];
      var seen = {};
      for (var i = 0; i < chain.length; i++) {
        var key = chain[i][0] + "/" + chain[i][1];
        if (seen[key]) continue;
        seen[key] = true;
        tried.push(key);
        var cell = lookup(manifest, chain[i][0], chain[i][1]);
        if (cell) {
          return {
            kind: i === 0 ? "exact" : "fallback",
            step: STEPS[i],
            requested: { costume: c, state: s },
            resolved: { costume: chain[i][0], state: chain[i][1] },
            cell: cell,
            tried: tried,
            reason: null,
          };
        }
      }
      return placeholder(c, s, tried, isObject(manifest) && isObject(manifest.cells) ? "tidak ada asset di rantai fallback" : "manifest tidak valid");
    } catch (e) {
      return placeholder(c, s, tried, "galat tak terduga: " + (e && e.message ? e.message : String(e)));
    }
  }

  /* Frame yang tampil pada waktu t (ms) untuk sel yang loop; reduced motion memakai keyframe. */
  function frameAt(cell, t, reduced) {
    if (!validCell(cell)) return 0;
    var key = typeof cell.keyframe === "number" && cell.keyframe >= 0 && cell.keyframe < cell.frames ? cell.keyframe : 0;
    if (reduced) return key;
    var total = 0;
    for (var i = 0; i < cell.durations_ms.length; i++) total += cell.durations_ms[i];
    var x = cell.loop === false ? Math.min(t, total - 1) : ((t % total) + total) % total;
    for (var j = 0; j < cell.durations_ms.length; j++) {
      if (x < cell.durations_ms[j]) return j;
      x -= cell.durations_ms[j];
    }
    return cell.frames - 1;
  }

  /* Daftar kostum dan state dari manifest, tahan terhadap manifest rusak. */
  function matrix(manifest) {
    var costumes = [], states = [];
    try {
      if (isObject(manifest) && Array.isArray(manifest.costumes)) {
        manifest.costumes.forEach(function (c) {
          if (isObject(c) && typeof c.id === "string") costumes.push({ id: c.id, label: String(c.label || c.id), group: String(c.group || "") });
        });
      }
      if (isObject(manifest) && Array.isArray(manifest.states)) {
        manifest.states.forEach(function (s) {
          if (isObject(s) && typeof s.id === "string") {
            states.push({ id: s.id, label: String(s.label || s.id), required: s.required === true,
              costumes: Array.isArray(s.costumes) ? s.costumes.slice() : null });
          }
        });
      }
    } catch (e) { /* kembalikan yang sudah terkumpul */ }
    return { costumes: costumes, states: states };
  }

  function applies(state, costumeId) {
    return !state.costumes || state.costumes.indexOf(costumeId) !== -1;
  }

  return { resolve: resolve, frameAt: frameAt, matrix: matrix, applies: applies, canvas: canvas, validCell: validCell,
    STEPS: STEPS.concat(["placeholder"]) };
});
