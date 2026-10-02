"""Resolver aset Gobyet v2 dengan fallback berantai (bagian 62). Hanya pustaka standar.

resolve(char_id, state) mencoba, berurutan, untuk tiap karakter di rantai (karakter -> fallback -> ... -> normal-gblk):
  1. state itu sendiri, 2. alias nama (mis. berserker_leap_spin_slash -> leap_spin_slash), 3. alias inti
  (attack/hit/victory/defeat/idle -> state khas karakter), 4. idle.
resolve(..., damage="damaged") memakai sheet tingkat kerusakan bila ada (Berserker), kalau tidak sheet normal.
variant(char_id, state, seed) memilih varian state secara deterministik (seed sama -> varian sama).
Sebuah kandidat hanya dipakai bila berkas sheet-nya benar-benar ada. Bila tidak ada satu pun, hasilnya None:
pemanggil tidak menggambar apa-apa (tidak pernah gambar rusak, tidak pernah mengaku aset ada).
"""
import json
import os


class Resolver:
    def __init__(self, registry, root, exists=None):
        self.reg = registry
        self.root = root
        self.exists = exists or (lambda rel: os.path.exists(os.path.join(root, rel)))
        self.chars = {c["id"]: c for c in registry["characters"]}
        self.root_id = registry.get("root_fallback", "normal-gblk")

    @classmethod
    def load(cls, root, exists=None):
        with open(os.path.join(root, "registry.json")) as f:
            return cls(json.load(f), root, exists)

    def chain(self, cid):
        seen, out = set(), []
        cur = cid if cid in self.chars else self.root_id
        while cur and cur not in seen and cur in self.chars:
            out.append(cur)
            seen.add(cur)
            cur = self.chars[cur].get("fallback")
        if self.root_id not in seen and self.root_id in self.chars:
            out.append(self.root_id)
        return out

    def candidates(self, c, state):
        out = []
        if state in c["states"]:
            out.append(state)
        named = c.get("aliases", {}).get(state)
        if named and named in c["states"] and named not in out:
            out.append(named)
        alias = c.get("core", {}).get(state)
        if alias and alias not in out:
            out.append(alias)
        idle = c.get("core", {}).get("idle", "idle")
        if idle in c["states"] and idle not in out:
            out.append(idle)
        return out

    def resolve(self, cid, state, damage=None):
        notes = []
        if cid not in self.chars:
            notes.append("karakter %r tidak ada di registry" % cid)
        for k in self.chain(cid):
            c = self.chars[k]
            for s in self.candidates(c, state):
                st = c["states"][s]
                sheet, layers = st["sheet"], st.get("layers")
                dm = st.get("damage", {}).get(damage) if damage else None
                if dm and self.exists(dm["sheet"]):
                    sheet, layers = dm["sheet"], dm.get("layers")
                elif damage and damage != "normal":
                    notes.append("tingkat kerusakan %r tidak ada untuk %s/%s, pakai normal" % (damage, k, s))
                if self.exists(sheet):
                    exact = (k == cid and s == state)
                    return {"character": k, "state": s, "sheet": sheet, "gif": st.get("gif"), "frames": st["frames"],
                            "ms": st["ms"], "durations": st.get("durations") or [st["ms"]] * st["frames"],
                            "loop": st["loop"], "hold": st.get("hold", 0), "events": st.get("events", []),
                            "layers": layers, "canvas": c.get("canvas", self.reg.get("canvas")),
                            "anchor": c.get("anchor", self.reg.get("anchor")), "requested": [cid, state],
                            "exact": exact, "notes": notes}
                notes.append("berkas hilang: %s" % sheet)
        return None

    def variant(self, cid, state, seed=None):
        """Nama state varian (idle -> idle_look, ...) dipilih deterministik dari seed (FNV-1a 32 bit).
        Tanpa seed atau tanpa varian: state itu sendiri."""
        c = self.chars.get(cid)
        if not c:
            return state
        opts = c.get("variants", {}).get(state)
        if not opts or seed is None:
            return state
        return opts[fnv1a(str(seed)) % len(opts)]


def fnv1a(s):
    h = 0x811C9DC5
    for b in s.encode("utf-8"):
        h ^= b
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h
