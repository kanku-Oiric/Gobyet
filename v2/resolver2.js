// Resolver aset Gobyet v2 (sama persis dengan v2/src/resolve2.py): karakter -> fallback -> normal-gblk;
// per karakter: state, alias inti, idle. Kandidat dipakai hanya bila exists(sheet) benar. Tidak ada -> null.
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
    var out = [], core = c.core || {};
    if (c.states[state]) out.push(state);
    if (core[state] && out.indexOf(core[state]) < 0) out.push(core[state]);
    var idle = core.idle || "idle";
    if (c.states[idle] && out.indexOf(idle) < 0) out.push(idle);
    return out;
  };
  Resolver.prototype.resolve = function (cid, state) {
    var ch = this.chain(cid);
    for (var i = 0; i < ch.length; i++) {
      var c = this.chars[ch[i]], cs = this.candidates(c, state);
      for (var j = 0; j < cs.length; j++) {
        var st = c.states[cs[j]];
        if (this.exists(st.sheet)) return { character: ch[i], state: cs[j], sheet: st.sheet, frames: st.frames, ms: st.ms,
                                            loop: st.loop, exact: ch[i] === cid && cs[j] === state };
      }
    }
    return null;
  };
  if (typeof module !== "undefined" && module.exports) module.exports = { Resolver: Resolver };
  else root.GobyetResolver = Resolver;
})(this);
