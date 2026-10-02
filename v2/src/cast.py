"""Daftar semua karakter v2 (id -> instance)."""
import knights
import vikings
import pirates
import domain
import special2
import berserker

MODULES = [knights, vikings, pirates, domain, special2, berserker]
_CACHE = {}


def all_ids():
    return [c.id for m in MODULES for c in m.CHARS]


def get(cid):
    if cid not in _CACHE:
        for m in MODULES:
            for c in m.CHARS:
                if c.id == cid:
                    _CACHE[cid] = c()
    return _CACHE[cid]
