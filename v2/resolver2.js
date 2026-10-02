// Resolver aset Gobyet v2 (sama persis dengan v2/src/resolve2.py): karakter -> fallback -> normal-gblk;
// per karakter: state, alias nama, alias inti, idle. Kandidat dipakai hanya bila exists(sheet) benar. Tidak ada -> null.
// resolve(c, s, damage) memakai sheet tingkat kerusakan bila ada; variant(c, s, seed) memilih varian deterministik.
(function (root) {
  function Resolver(registry, exists) {
    this.reg = registry;
    this.exists = exists || function () { return true; };
    this.chars = {};
    for (var i = 0; i < registry.characters.length; i++) this.chars[registry.characters[i].id] = registry.characters[i];
    this.rootId = registry.root_fallback || "normal-gblk";
  }
  Resolver.prototype.chain = function (cid) {
    var seen = {}, out = [], cur = this.chars[cid] ? cid : this.rootId;
    while (cur && !seen[cur] && this.chars[cur]) { out.push(cur); seen[cur] = 1; cur = this.chars[cur].fallback; }
    if (!seen[this.rootId] && this.chars[this.rootId]) out.push(this.rootId);
    return out;
  };
  Resolver.prototype.candidates = function (c, state) {
    var out = [], core = c.core || {}, named = (c.aliases || {})[state];
    if (c.states[state]) out.push(state);
    if (named && c.states[named] && out.indexOf(named) < 0) out.push(named);
    if (core[state] && out.indexOf(core[state]) < 0) out.push(core[state]);
    var idle = core.idle || "idle";
    if (c.states[idle] && out.indexOf(idle) < 0) out.push(idle);
    return out;
  };
  Resolver.prototype.resolve = function (cid, state, damage) {
    var ch = this.chain(cid);
    for (var i = 0; i < ch.length; i++) {
      var c = this.chars[ch[i]], cs = this.candidates(c, state);
      for (var j = 0; j < cs.length; j++) {
        var st = c.states[cs[j]], sheet = st.sheet, layers = st.layers || null;
        var dm = damage && st.damage ? st.damage[damage] : null;
        if (dm && this.exists(dm.sheet)) { sheet = dm.sheet; layers = dm.layers || null; }
        if (this.exists(sheet)) {
          var durs = st.durations || [];
          if (!st.durations) for (var k = 0; k < st.frames; k++) durs.push(st.ms);
          return { character: ch[i], state: cs[j], sheet: sheet, frames: st.frames, ms: st.ms, durations: durs,
                   loop: st.loop, hold: st.hold || 0, events: st.events || [], layers: layers,
                   canvas: c.canvas || this.reg.canvas, anchor: c.anchor || this.reg.anchor,
                   exact: ch[i] === cid && cs[j] === state };
        }
      }
    }
    return null;
  };
  function fnv1a(s) {
    var h = 0x811c9dc5, bytes = unescape(encodeURIComponent(s));
    for (var i = 0; i < bytes.length; i++) { h ^= bytes.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; }
    return h >>> 0;
  }
  Resolver.prototype.variant = function (cid, state, seed) {
    var c = this.chars[cid];
    if (!c || seed === undefined || seed === null) return state;
    var opts = (c.variants || {})[state];
    if (!opts || !opts.length) return state;
    return opts[fnv1a(String(seed)) % opts.length];
  };
  Resolver.fnv1a = fnv1a;
  if (typeof module !== "undefined" && module.exports) module.exports = { Resolver: Resolver };
  else root.GobyetResolver = Resolver;
})(this);
