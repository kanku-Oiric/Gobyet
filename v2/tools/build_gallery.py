"""Bangun galeri interaktif Gobyet v2 (bagian 67): semua karakter dikelompokkan FANTASY, DOMAIN, ROLE, SPECIAL,
setiap state beranimasi, mode warna/grayscale/siluet, uji skala 100/75/50/25%, arah hadap.

    python3 v2/tools/build_gallery.py OUT.html            # sheet sebagai path relatif (taruh di v2/)
    python3 v2/tools/build_gallery.py OUT.html --embed    # sheet disematkan sebagai data URI (satu berkas)
"""
import base64
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.dirname(HERE)
GROUPS = [("FANTASY", "fantasy"), ("DOMAIN", "domain"), ("ROLE", "role"), ("SPECIAL", "special")]


def uri(rel):
    with open(os.path.join(V2, rel), "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def ev_summary(st):
    out = []
    for e in st.get("events", []):
        if e["type"] == "hit":
            out.append("kena f%d" % e["frame"])
        elif e["type"] == "hitstop":
            out.append("hit-stop %d ms" % e["ms"])
        elif e["type"] == "screen_shake":
            out.append("getar %d px" % e["px"])
    return " · ".join(out)


def data(embed):
    with open(os.path.join(V2, "registry.json")) as f:
        reg = json.load(f)
    src = (lambda rel: uri(rel)) if embed else (lambda rel: rel)
    chars = []
    for c in reg["characters"]:
        cv = c.get("canvas", reg["canvas"])
        an = c.get("anchor", reg["anchor"])
        states = []
        for name, st in c["states"].items():
            e = {"name": name, "n": st["frames"], "ms": st["ms"], "loop": st["loop"], "hold": st["hold"],
                 "label": st["label"], "src": src(st["sheet"]), "w": cv["w"], "h": cv["h"], "base": an["baseline"]}
            if st.get("durations"):
                e["durs"] = st["durations"]
            if st.get("events"):
                e["ev"] = ev_summary(st)
            if st.get("variant_of"):
                e["variant_of"] = st["variant_of"]
            if st.get("layers"):
                e["layers"] = {k: src(v) for k, v in st["layers"].items()}
            if st.get("damage"):
                e["damage"] = {lv: {"src": src(d["sheet"]), "layers": {k: src(v) for k, v in d["layers"].items()}}
                               for lv, d in st["damage"].items()}
            states.append(e)
        chars.append({"id": c["id"], "name": c["name"], "category": c["category"], "faction": c["faction"], "role": c["role"],
                      "silhouette": c["silhouette"], "fallback": c["fallback"], "core": c["core"], "label": c.get("label"),
                      "caption": c.get("caption"), "note": c.get("note"), "states": states, "w": cv["w"], "h": cv["h"],
                      "variants": c.get("variants"), "damage_levels": c.get("damage_levels")})
    fb = {c["id"]: c["fallback"] for c in reg["characters"]}
    vfx = []
    for name, v in reg.get("vfx", {}).items():
        if v.get("kind") == "event":
            continue
        vfx.append({"name": name, "n": v["frames"], "ms": v["durations"][0], "durs": v["durations"], "loop": True,
                    "hold": 3, "label": v.get("note", ""), "src": src(v["sheet"]), "w": v["canvas"]["w"],
                    "h": v["canvas"]["h"], "base": None, "kind": v["kind"]})
    hit = "preview/berserker-leap_spin_slash-hit.gif"
    hit_src = None
    if os.path.exists(os.path.join(V2, hit)):
        if embed:
            with open(os.path.join(V2, hit), "rb") as f:
                hit_src = "data:image/gif;base64," + base64.b64encode(f.read()).decode()
        else:
            hit_src = hit
    return {"canvas": reg["canvas"], "anchor": reg["anchor"], "groups": GROUPS, "chars": chars, "fallback": fb,
            "vfx": vfx, "hit": hit_src,
            "commit": os.popen("git -C %s rev-parse --short HEAD 2>/dev/null" % V2).read().strip()}


PAGE = r"""<title>Gobyet Universe</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;500;600&family=Silkscreen&display=swap">
<style>
/* Tata letak: kepala + kontrol, panel detail karakter terpilih, lalu empat rak (FANTASY, DOMAIN, ROLE, SPECIAL)
   berisi kartu sprite. Keluarga visual sama dengan arena Battle Royale: navy, font piksel untuk judul. */
:root {
  --bg: #eef0f6; --panel: #ffffff; --stage: #e2e6f1; --ink: #1b2033; --dim: #5a6383; --line: #d3d8e6;
  --accent: #a85a28; --gold: #b07d12; --floor: #c9cfe0; --focus: #3d63d8;
  --f-pixel: "Silkscreen", "Courier New", monospace;
  --f-body: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --f-mono: "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #111830; --panel: #182142; --stage: #0d1328; --ink: #e8ecf8; --dim: #8c96b8; --line: #2a3458;
  --accent: #e39a62; --gold: #f9c23c; --floor: #2a3458; --focus: #8fb0ff; color-scheme: dark } }
:root[data-theme="dark"] {
  --bg: #111830; --panel: #182142; --stage: #0d1328; --ink: #e8ecf8; --dim: #8c96b8; --line: #2a3458;
  --accent: #e39a62; --gold: #f9c23c; --floor: #2a3458; --focus: #8fb0ff; color-scheme: dark }
* { box-sizing: border-box }
body { background: var(--bg); color: var(--ink); font: 15px/1.55 var(--f-body); }
.wrap { max-width: 1180px; margin: 0 auto; padding-inline: 16px; padding-block: 20px 48px; display: grid; gap: 28px }
h1, h2, h3 { font-family: var(--f-pixel); font-weight: 400; margin: 0; text-wrap: balance; letter-spacing: .02em }
h1 { font-size: clamp(28px, 5vw, 44px); line-height: 1.05 }
h2 { font-size: 18px; color: var(--dim) }
h3 { font-size: 16px }
p { margin: 0 }
.lede { max-width: 65ch; color: var(--dim) }
.head { display: grid; gap: 10px }
.facts { display: flex; flex-wrap: wrap; gap: 6px 18px; font: 13px var(--f-mono); color: var(--dim); font-variant-numeric: tabular-nums }
.facts b { color: var(--ink); font-weight: 600 }
.controls { display: flex; flex-wrap: wrap; gap: 10px 20px; align-items: center; padding: 12px 14px; background: var(--panel);
  border: 1px solid var(--line); border-radius: 8px; position: sticky; top: env(safe-area-inset-top, 0px); z-index: 2 }
.ctl { display: flex; align-items: center; gap: 6px; flex-wrap: wrap }
.ctl > span { font: 11px var(--f-mono); text-transform: uppercase; letter-spacing: .08em; color: var(--dim) }
.seg { display: inline-flex; border: 1px solid var(--line); border-radius: 6px; overflow: hidden }
.seg button { font: 13px var(--f-body); color: var(--ink); background: transparent; border: 0; padding: 5px 10px; cursor: pointer }
.seg button + button { border-left: 1px solid var(--line) }
.seg button[aria-pressed="true"] { background: var(--ink); color: var(--panel) }
button:focus-visible, .card:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px }
.shelves { display: grid; gap: 28px; min-width: 0 }
.shelf { display: grid; gap: 12px }
.shelf-head { display: flex; align-items: baseline; gap: 12px; border-bottom: 1px solid var(--line); padding-bottom: 6px }
.shelf-head small { font: 12px var(--f-mono); color: var(--dim) }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px }
.card { display: grid; gap: 6px; padding: 8px 8px 10px; background: var(--panel); border: 1px solid var(--line); border-radius: 8px;
  cursor: pointer; text-align: left; color: var(--ink); font: inherit; min-width: 0 }
.card[aria-current="true"] { border-color: var(--accent); box-shadow: 0 0 0 1px var(--accent) inset }
.card canvas { width: 100%; height: auto; aspect-ratio: 1 / 1; background: var(--stage); border-radius: 4px; image-rendering: pixelated }
.card.wide, .st.wide { grid-column: span 2 }
.card.wide canvas, .st.wide canvas { aspect-ratio: auto }
.detail-top.wide { grid-template-columns: minmax(0, 1fr) }
.detail-top.wide .hero-cv { aspect-ratio: auto; max-width: 576px }
.dctl { display: flex; flex-wrap: wrap; gap: 10px 20px; align-items: center }
.hitfig { margin: 0; display: grid; gap: 6px; max-width: 528px }
.hitfig img { width: 100%; height: auto; image-rendering: pixelated; border-radius: 6px; background: var(--stage) }
.hitfig figcaption { font-size: 13px; color: var(--dim) }
.card .nm { font-weight: 600; font-size: 14px; line-height: 1.25 }
.card .meta { font: 11.5px var(--f-mono); color: var(--dim); overflow-wrap: anywhere }
.detail { display: grid; gap: 16px; padding: 16px; background: var(--panel); border: 1px solid var(--line); border-radius: 10px }
.detail-top { display: grid; grid-template-columns: minmax(0, 260px) minmax(0, 1fr); gap: 18px; align-items: start }
.hero-cv { width: 100%; height: auto; aspect-ratio: 1 / 1; background: var(--stage); border-radius: 6px; image-rendering: pixelated }
.kv { display: grid; grid-template-columns: max-content minmax(0, 1fr); gap: 4px 14px; font-size: 14px }
.kv dt { font: 11px var(--f-mono); text-transform: uppercase; letter-spacing: .08em; color: var(--dim); padding-top: 3px }
.kv dd { margin: 0; min-width: 0; overflow-wrap: anywhere }
.chip { display: inline-block; font: 11.5px var(--f-mono); padding: 1px 7px; border: 1px solid var(--line); border-radius: 999px; margin: 0 4px 4px 0 }
.chip.win { border-color: var(--gold); color: var(--gold) }
.states { display: grid; grid-template-columns: repeat(auto-fill, minmax(132px, 1fr)); gap: 10px }
.st { display: grid; gap: 4px; min-width: 0 }
.st canvas { width: 100%; height: auto; aspect-ratio: 1 / 1; background: var(--stage); border-radius: 4px; image-rendering: pixelated }
.st b { font: 600 12.5px var(--f-mono) }
.st small { font: 11px var(--f-mono); color: var(--dim) }
.st p { font-size: 12.5px; color: var(--dim); line-height: 1.35 }
.scale { display: flex; flex-wrap: wrap; align-items: end; gap: 16px; padding: 12px; background: var(--stage); border-radius: 6px }
.scale figure { margin: 0; display: grid; gap: 4px; justify-items: center }
.scale figcaption { font: 11px var(--f-mono); color: var(--dim) }
.scale canvas { image-rendering: pixelated }
.note { font-size: 13px; color: var(--dim); max-width: 75ch }
@media (max-width: 640px) { .detail-top { grid-template-columns: 1fr } .grid { grid-template-columns: repeat(2, minmax(0, 1fr)) }
  .controls { position: static } }
@media (prefers-reduced-motion: reduce) { * { scroll-behavior: auto } }
</style>

<div class="wrap">
  <header class="head">
    <h1>Gobyet Universe</h1>
    <p class="lede">Satu monyet, banyak dunia: setiap karakter memakai kepala Gobyet yang sama, tetapi siluet, kuda-kuda, senjata, dan animasinya mengikuti perannya. Pilih kartu untuk melihat semua state-nya.</p>
    <p class="facts" id="facts"></p>
  </header>

  <div class="controls" role="toolbar" aria-label="Tampilan">
    <div class="ctl"><span>Mode</span>
      <div class="seg" data-ctl="mode"><button type="button" data-v="color" aria-pressed="true">Warna</button><button type="button" data-v="gray" aria-pressed="false">Grayscale</button><button type="button" data-v="sil" aria-pressed="false">Siluet</button></div></div>
    <div class="ctl"><span>Hadap</span>
      <div class="seg" data-ctl="dir"><button type="button" data-v="r" aria-pressed="true">Kanan</button><button type="button" data-v="l" aria-pressed="false">Kiri</button></div></div>
    <div class="ctl"><span>Animasi</span>
      <div class="seg" data-ctl="play"><button type="button" data-v="on" aria-pressed="true">Jalan</button><button type="button" data-v="off" aria-pressed="false">Diam</button></div></div>
    <div class="ctl"><span>Lantai</span>
      <div class="seg" data-ctl="floor"><button type="button" data-v="on" aria-pressed="true">Tampil</button><button type="button" data-v="off" aria-pressed="false">Sembunyi</button></div></div>
  </div>

  <section class="detail" id="detail" aria-live="polite"></section>
  <div id="shelves" class="shelves"></div>
  <p class="note" id="foot"></p>
</div>

<script id="gdata" type="application/json">__DATA__</script>
<script>
(function () {
  "use strict";
  var D = JSON.parse(document.getElementById("gdata").textContent);
  var W = D.canvas.w, H = D.canvas.h, BASE = D.anchor.baseline;
  var $ = function (id) { return document.getElementById(id); };
  var reduce = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  var opt = { mode: "color", dir: "r", play: reduce ? "off" : "on", floor: "on" };
  var byId = {}; D.chars.forEach(function (c) { byId[c.id] = c; });
  var IMG = {}, GRAY = {};
  function img(src) {
    if (!IMG[src]) {
      var im = new Image();
      im.onload = function () {
        var c = document.createElement("canvas"); c.width = im.width; c.height = im.height;
        var x = c.getContext("2d"); x.drawImage(im, 0, 0);
        try {
          var d = x.getImageData(0, 0, c.width, c.height), p = d.data;
          for (var i = 0; i < p.length; i += 4) { var g = Math.round(p[i] * .299 + p[i + 1] * .587 + p[i + 2] * .114); p[i] = p[i + 1] = p[i + 2] = g; }
          x.putImageData(d, 0, 0); GRAY[src] = c;
        } catch (e) { GRAY[src] = null; }
      };
      im.src = src; IMG[src] = im;
    }
    return IMG[src];
  }
  function css(v) { return getComputedStyle(document.documentElement).getPropertyValue(v).trim() || "#000"; }
  var tmp = document.createElement("canvas"); tmp.width = 256; tmp.height = 128; var tctx = tmp.getContext("2d");
  var dopt = { dmg: "normal", layer: "composite", blood: "on" };
  function srcOf(st, detail) {
    if (!detail || !st.layers) return st.src;
    var b = dopt.dmg !== "normal" && st.damage && st.damage[dopt.dmg] ? st.damage[dopt.dmg] : { src: st.src, layers: st.layers };
    return dopt.layer === "composite" ? b.src : b.layers[dopt.layer];
  }

  // daftar kanvas yang dianimasikan: {cv, st, t0}
  var live = [];
  function attach(cv, st) { live.push({ cv: cv, st: st }); img(st.src); }
  function frameIndex(st, t) {
    // durasi per frame (tempo tidak rata) bila ada; non-loop: main sekali, tahan frame terakhir, ulangi
    var d = st.durs || null, n = st.n, hold = st.loop ? 0 : Math.max(st.hold, 4) * st.ms, total = 0, i;
    if (!d) { d = []; for (i = 0; i < n; i++) d.push(st.ms); }
    for (i = 0; i < n; i++) total += d[i];
    t = t % (total + hold);
    for (i = 0; i < n; i++) { if (t < d[i]) return i; t -= d[i]; }
    return n - 1;
  }
  function drawSprite(ctx, st, src0, k, s, ox, oy) {
    var im = img(src0); if (!im || !im.complete || !im.naturalWidth) return;
    var w = st.w, h = st.h;
    var src = opt.mode === "gray" && GRAY[src0] ? GRAY[src0] : im;
    if (tmp.width < w || tmp.height < h) { tmp.width = Math.max(tmp.width, w); tmp.height = Math.max(tmp.height, h); }
    tctx.clearRect(0, 0, tmp.width, tmp.height);
    if (opt.dir === "l") { tctx.save(); tctx.translate(w, 0); tctx.scale(-1, 1); tctx.drawImage(src, k * w, 0, w, h, 0, 0, w, h); tctx.restore(); }
    else tctx.drawImage(src, k * w, 0, w, h, 0, 0, w, h);
    if (opt.mode === "sil") { tctx.globalCompositeOperation = "source-in"; tctx.fillStyle = css("--ink"); tctx.fillRect(0, 0, w, h); tctx.globalCompositeOperation = "source-over"; }
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(tmp, 0, 0, w, h, ox, oy, w * s, h * s);
  }
  function paint(rec, t) {
    var cv = rec.cv, ctx = cv.getContext("2d"), st = rec.st, s = cv.width / st.w;
    ctx.clearRect(0, 0, cv.width, cv.height);
    if (st.kind === "blood" && dopt.blood !== "on") return;
    if (opt.floor === "on" && st.base) { ctx.fillStyle = css("--floor"); ctx.fillRect(0, st.base * s, cv.width, Math.max(1, s)); }
    var k = opt.play === "on" ? frameIndex(st, t) : 0;
    drawSprite(ctx, st, srcOf(st, rec.detail), k, s, 0, 0);
  }
  var t0 = performance.now(), last = 0;
  function loop(now) {
    if (now - last > 30) {
      last = now;
      var t = now - t0;
      for (var i = 0; i < live.length; i++) if (live[i].cv.isConnected) paint(live[i], t);
    }
    requestAnimationFrame(loop);
  }

  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = String(text); return e; }
  function canvas(px, w, h) { var c = document.createElement("canvas"); c.width = (w || W) * px; c.height = (h || H) * px; return c; }
  function wide(o) { return o.w > W; }
  function coreState(c, name) { var s = c.core[name] || name; for (var i = 0; i < c.states.length; i++) if (c.states[i].name === s) return c.states[i]; return c.states[0]; }
  function chain(id) { var out = [], seen = {}, cur = id; while (cur && !seen[cur]) { out.push(cur); seen[cur] = 1; cur = D.fallback[cur]; } return out; }

  var frames = 0, states = 0; D.chars.forEach(function (c) { states += c.states.length; c.states.forEach(function (s) { frames += s.n; }); });
  $("facts").innerHTML = "";
  [["karakter", D.chars.length], ["state", states], ["frame", frames], ["kanvas", W + "×" + H + " (Berserker 144×100)"], ["lantai", "y " + (BASE - 1)], ["VFX", D.vfx.length]].forEach(function (f) {
    var s = el("span"); s.appendChild(el("b", null, f[1])); s.appendChild(document.createTextNode(" " + f[0])); $("facts").appendChild(s);
  });

  var cards = {};
  D.groups.forEach(function (g) {
    var list = D.chars.filter(function (c) { return c.category === g[1]; });
    if (!list.length) return;
    var sec = el("section", "shelf"); sec.setAttribute("aria-label", g[0]);
    var hd = el("div", "shelf-head"); hd.appendChild(el("h2", null, g[0])); hd.appendChild(el("small", null, list.length + " karakter")); sec.appendChild(hd);
    var grid = el("div", "grid");
    list.forEach(function (c) {
      var b = el("button", "card" + (wide(c) ? " wide" : "")); b.type = "button"; b.setAttribute("aria-label", c.name);
      var cv = canvas(2, c.w, c.h); b.appendChild(cv); attach(cv, coreState(c, "idle"));
      b.appendChild(el("span", "nm", c.name.replace(/ Gobyet$/, "")));
      b.appendChild(el("span", "meta", c.id + " · " + c.states.length + " state"));
      b.addEventListener("click", function () { show(c.id, true); });
      grid.appendChild(b); cards[c.id] = b;
    });
    sec.appendChild(grid); $("shelves").appendChild(sec);
  });

  if (D.vfx.length) {
    var vsec = el("section", "shelf"); vsec.setAttribute("aria-label", "VFX");
    var vh = el("div", "shelf-head"); vh.appendChild(el("h2", null, "VFX")); vh.appendChild(el("small", null, D.vfx.length + " sprite · darah hanya saat kena, bisa dimatikan"));
    var bw = el("div", "seg"); [["on", "Darah tampil"], ["off", "Darah sembunyi"]].forEach(function (o) {
      var b = el("button", null, o[1]); b.type = "button"; b.setAttribute("aria-pressed", String(dopt.blood === o[0]));
      b.addEventListener("click", function () { dopt.blood = o[0]; bw.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); }); });
      bw.appendChild(b);
    });
    vh.appendChild(bw); vsec.appendChild(vh);
    var vg = el("div", "grid");
    D.vfx.forEach(function (v) {
      var b = el("div", "card"); var s = Math.max(1, Math.floor(128 / Math.max(v.w, v.h)));
      var cv = canvas(s, v.w, v.h); cv.style.aspectRatio = v.w + " / " + v.h; b.appendChild(cv); attach(cv, v);
      b.appendChild(el("span", "nm", v.name)); b.appendChild(el("span", "meta", v.kind + " · " + v.n + " frame · " + v.label));
      vg.appendChild(b);
    });
    vsec.appendChild(vg); $("shelves").appendChild(vsec);
  }

  function show(id, scroll) {
    var c = byId[id]; if (!c) return;
    Object.keys(cards).forEach(function (k) { cards[k].setAttribute("aria-current", k === id ? "true" : "false"); });
    live = live.filter(function (r) { return !r.detail; });
    var d = $("detail"); d.innerHTML = "";
    var top = el("div", "detail-top" + (wide(c) ? " wide" : ""));
    var hero = canvas(4, c.w, c.h); hero.className = "hero-cv"; top.appendChild(hero);
    var rec = { cv: hero, st: coreState(c, "idle"), detail: true }; live.push(rec); img(rec.st.src);
    var info = el("div"); info.style.display = "grid"; info.style.gap = "10px"; info.style.minWidth = "0";
    info.appendChild(el("h3", null, c.name));
    var kv = el("dl", "kv");
    function row(k, v) { kv.appendChild(el("dt", null, k)); var dd = el("dd"); if (typeof v === "string") dd.textContent = v; else dd.appendChild(v); kv.appendChild(dd); }
    row("id", c.id);
    row("kategori", c.category + (c.faction ? " · " + c.faction : "") + (c.role ? " · " + c.role : ""));
    var sil = el("span"); c.silhouette.forEach(function (t) { sil.appendChild(el("span", "chip", t.replace(/_/g, " "))); }); row("siluet", sil);
    var core = el("span"); ["idle", "attack", "hit", "victory", "defeat"].forEach(function (k) { if (c.core[k]) core.appendChild(el("span", "chip", k + " → " + c.core[k])); }); row("inti arena", core);
    row("fallback", chain(c.id).concat(chain(c.id).indexOf("normal-gblk") < 0 ? ["normal-gblk"] : []).join(" → "));
    if (c.label) { var w = el("span", "chip win", c.label); row("label", w); }
    if (c.caption) row("keterangan", c.caption);
    if (c.note) row("catatan", c.note);
    if (c.variants) {
      var vs = el("span");
      Object.keys(c.variants).forEach(function (k) { vs.appendChild(el("span", "chip", k + ": " + c.variants[k].join(", "))); });
      row("varian", vs);
    }
    info.appendChild(kv);
    top.appendChild(info); d.appendChild(top);
    if (c.damage_levels) {
      var dc = el("div", "dctl");
      function seg(label, key, opts) {
        var w = el("div", "ctl"); w.appendChild(el("span", null, label)); var g = el("div", "seg");
        opts.forEach(function (o) {
          var b = el("button", null, o[1]); b.type = "button"; b.setAttribute("aria-pressed", String(dopt[key] === o[0]));
          b.addEventListener("click", function () { dopt[key] = o[0]; g.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); }); });
          g.appendChild(b);
        });
        w.appendChild(g); dc.appendChild(w);
      }
      seg("Kerusakan", "dmg", [["normal", "Normal"], ["damaged", "Rusak"], ["heavily_damaged", "Rusak berat"]]);
      seg("Lapisan", "layer", [["composite", "Komposit"], ["body", "Karakter"], ["weapon", "Senjata"], ["vfx", "VFX"]]);
      d.appendChild(dc);
    }
    if (c.id === "berserker" && D.hit) {
      var fig = el("figure", "hitfig"); var gi = document.createElement("img"); gi.src = D.hit;
      gi.alt = "Berserker melakukan leap spin slash ke Fantasy Knight: hantaman, jeda hit-stop, darah bergaya, lawan terpental, percikan, debu";
      fig.appendChild(gi);
      fig.appendChild(el("figcaption", null, "Konfirmasi kena (pratinjau mesin): hantaman, hit-stop, darah tingkat 2 (sprite VFX terpisah, hanya saat kena), lawan recoil, percikan, debu."));
      d.appendChild(fig);
    }

    var sh = el("h3", null, "Semua state (" + c.states.length + ")"); d.appendChild(sh);
    var grid = el("div", "states");
    c.states.forEach(function (st) {
      var box = el("div", "st" + (wide(st) ? " wide" : "")); var cv = canvas(2, st.w, st.h); box.appendChild(cv);
      live.push({ cv: cv, st: st, detail: true }); img(st.src);
      box.appendChild(el("b", null, st.name + (st.variant_of ? " (varian " + st.variant_of + ")" : "")));
      var tot = st.durs ? st.durs.reduce(function (a, b) { return a + b; }, 0) : st.n * st.ms;
      box.appendChild(el("small", null, st.n + " frame · " + (st.durs ? "tempo per frame, " + tot + " ms" : st.ms + " ms") + " · " + (st.loop ? "loop" : "sekali" + (st.hold ? " + tahan" : ""))));
      if (st.ev) box.appendChild(el("small", null, st.ev));
      if (st.label) box.appendChild(el("p", null, st.label));
      grid.appendChild(box);
    });
    d.appendChild(grid);

    d.appendChild(el("h3", null, "Uji skala (ukuran piksel asli)"));
    var sc = el("div", "scale");
    [1, .75, .5, .25].forEach(function (f) {
      var fig = el("figure"); var px = Math.round(c.w * f), py = Math.round(c.h * f); var cv = document.createElement("canvas"); cv.width = px; cv.height = py;
      cv.style.width = px + "px"; cv.style.height = py + "px";
      fig.appendChild(cv); fig.appendChild(el("figcaption", null, Math.round(f * 100) + "% · " + px + " px"));
      sc.appendChild(fig);
      live.push({ cv: cv, st: coreState(c, "idle"), detail: false });
    });
    d.appendChild(sc);
    if (scroll) d.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
    try { localStorage.setItem("gobyet-gallery-pick", id); } catch (e) { /* tidak tersedia */ }
  }

  document.querySelectorAll(".seg").forEach(function (seg) {
    var key = seg.getAttribute("data-ctl");
    seg.querySelectorAll("button").forEach(function (b) {
      if (b.getAttribute("data-v") === opt[key]) seg.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
      b.addEventListener("click", function () {
        opt[key] = b.getAttribute("data-v");
        seg.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
      });
    });
  });

  var pick = "knight-heavy";
  try { pick = localStorage.getItem("gobyet-gallery-pick") || pick; } catch (e) { /* tidak tersedia */ }
  if (location.hash && byId[location.hash.slice(1)]) pick = location.hash.slice(1);
  show(byId[pick] ? pick : D.chars[0].id, false);
  $("foot").textContent = "Sprite Gobyet v2 dari registry.json (commit " + (D.commit || "?") + "). Sheet 1x 64×64 (Berserker 144×100 dengan badan berskala sama), digambar dengan skala piksel bulat tanpa penghalusan. Garis lantai adalah jangkar kaki yang sama untuk semua karakter.";
  requestAnimationFrame(loop);
})();
</script>
"""


def main():
    out = sys.argv[1]
    embed = "--embed" in sys.argv
    payload = json.dumps(data(embed), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = PAGE.replace("__DATA__", payload)
    if "--standalone" in sys.argv:  # berkas mandiri (repo): kerangka dokumen sendiri
        html = ('<!doctype html>\n<html lang="id">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                + html.replace("<style>", "<style>\nbody { margin: 0 }", 1).replace('<div class="wrap">', "</head>\n<body>\n<div class=\"wrap\">", 1)
                + "</body>\n</html>\n")
    with open(out, "w") as f:
        f.write(html)
    print(out, "%.1f KB" % (len(html.encode()) / 1024.0))


if __name__ == "__main__":
    main()
