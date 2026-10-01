"""Resolver aset Gobyet v2 dengan fallback berantai (bagian 62). Hanya pustaka standar.

resolve(char_id, state) mencoba, berurutan, untuk tiap karakter di rantai (karakter -> fallback -> ... -> normal-gblk):
  1. state itu sendiri, 2. alias inti (attack/hit/victory/defeat/idle -> state khas karakter), 3. idle.
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
        alias = c.get("core", {}).get(state)
        if alias and alias not in out:
            out.append(alias)
        idle = c.get("core", {}).get("idle", "idle")
        if idle in c["states"] and idle not in out:
            out.append(idle)
        return out

    def resolve(self, cid, state):
        notes = []
        if cid not in self.chars:
            notes.append("karakter %r tidak ada di registry" % cid)
        for k in self.chain(cid):
            c = self.chars[k]
            for s in self.candidates(c, state):
                st = c["states"][s]
                if self.exists(st["sheet"]):
                    exact = (k == cid and s == state)
                    return {"character": k, "state": s, "sheet": st["sheet"], "gif": st["gif"], "frames": st["frames"],
                            "ms": st["ms"], "loop": st["loop"], "requested": [cid, state], "exact": exact,
                            "notes": notes}
                notes.append("berkas hilang: %s" % st["sheet"])
        return None
