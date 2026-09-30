"""Spesifikasi Gobyet Character Pack: kostum = identitas, state = sedang apa.

Ini satu-satunya tempat yang memetakan animasi yang ada ke sel kostum x state.
Sel "asli" adalah 7 aset yang sudah ada sebelum Fase 2; sel "baru" dibuat di Fase 2.
src/export.py membaca modul ini untuk menulis pack/manifest.json, lengkap dengan
jumlah frame dan durasi per frame yang diambil langsung dari SCENES.
"""

FORMAT = "gobyet-pack/1"

# 12 kostum MVP. Urutan = urutan tampilan di preview.
COSTUMES = [
    ("normal", "Normal", "core"),
    ("referee", "Referee", "role"),
    ("judge", "Judge", "role"),
    ("skeptic", "Skeptic", "role"),
    ("champion", "Champion", "role"),
    ("greek-philosopher", "Greek Philosopher", "domain"),
    ("academic", "Academic", "domain"),
    ("scientist", "Scientist", "domain"),
    ("mathematician", "Mathematician", "domain"),
    ("lawyer", "Lawyer", "domain"),
    ("hacker", "Hacker", "domain"),
    ("detective", "Detective", "domain"),
]

# State wajib untuk semua kostum, lalu state opsional. "costumes" membatasi state
# opsional ke peran tertentu; tanpa "costumes" berarti boleh untuk semua kostum.
STATES = [
    {"id": "idle", "label": "idle", "required": True},
    {"id": "thinking", "label": "thinking", "required": True},
    {"id": "victory", "label": "victory", "required": True},
    {"id": "defeated", "label": "defeated", "required": True},
    {"id": "judging", "label": "judging", "required": False, "costumes": ["judge"]},
    {"id": "suspicious", "label": "suspicious", "required": False, "costumes": ["skeptic"]},
    {"id": "attack", "label": "attack", "required": False, "costumes": ["skeptic"]},
    {"id": "shocked", "label": "shocked", "required": False},
    {"id": "happy", "label": "happy", "required": False},
]

# Sel yang sudah punya asset: (kostum, state) -> (nama animasi, frame kunci untuk tampilan statis).
# Setiap animasi lama berisi beberapa beat; state di sini adalah kecocokan terdekat.
ORIGINAL = {
    ("normal", "idle"): ("ngopi-santai", 0),
    ("normal", "happy"): ("makan-pisang", 4),
    ("greek-philosopher", "thinking"): ("filsuf-yunani", 10),
    # Dipindah dari academic/victory di Gerbang B: 78% loop wisuda adalah pose tenang memegang ijazah.
    ("academic", "idle"): ("wisuda", 0),
    ("scientist", "thinking"): ("rambut-einstein", 8),
    ("hacker", "idle"): ("hacker", 2),
    ("detective", "thinking"): ("detektif-bug", 6),
}

# Aset baru hasil Fase 2, per gerbang persetujuan. Dibuat dengan rig yang sama (src/roles.py).
NEW = {
    ("referee", "idle"): ("referee-idle", 2, "A"),
    ("referee", "thinking"): ("referee-thinking", 12, "A"),
    # Gerbang B: frame kunci 0 (frame pertama = pose tetap yang jelas).
    ("judge", "idle"): ("judge-idle", 0, "B"),
    ("judge", "thinking"): ("judge-thinking", 0, "B"),
    ("judge", "judging"): ("judge-judging", 0, "B"),
    ("skeptic", "idle"): ("skeptic-idle", 0, "B"),
    ("skeptic", "suspicious"): ("skeptic-suspicious", 0, "B"),
    ("skeptic", "attack"): ("skeptic-attack", 0, "B"),
    ("champion", "idle"): ("champion-idle", 0, "B"),
    ("champion", "victory"): ("champion-victory", 0, "B"),
}

# Animasi yang ada tetapi sengaja tidak dimasukkan ke matriks MVP.
EXTRAS = {
    "marah-debug": "Normal: ngamuk ke laptop. Tidak cocok dengan state standar (campuran shocked dan marah).",
    "kondangan": "Kostum peci + batik, di luar 12 kostum MVP.",
}

FALLBACK = ["costume+state", "costume+idle", "normal+state", "normal+idle", "placeholder"]


def manifest(scenes):
    """scenes: {nama: (fungsi_frame, jumlah_frame, fungsi_durasi)} gabungan semua animasi."""
    cells = {}
    entries = [(k, v[0], v[1], "asli", None) for k, v in ORIGINAL.items()]
    entries += [(k, v[0], v[1], "baru", v[2]) for k, v in NEW.items()]
    for (costume, state), name, keyframe, origin, gate in entries:
        _, n, ms = scenes[name]
        cell = cells.setdefault(costume, {})[state] = {
            "status": "final",
            "origin": origin,
            "source": name,
            "sheet": "../sheets/%s.png" % name,
            "sheet4x": "../sheets/%s@4x.png" % name,
            "gif": "../gif/%s.gif" % name,
            "frames": n,
            "durations_ms": [int(ms(i)) for i in range(n)],
            "loop": True,
            "keyframe": keyframe,
        }
        if gate:
            cell["gate"] = gate
    return {
        "format": FORMAT,
        "generated_by": "src/export.py (dari src/pack.py)",
        "paths": "relatif terhadap file manifest ini",
        "canvas": {"w": 64, "h": 48},
        "gif_scale": 8,
        "costumes": [{"id": c, "label": label, "group": group} for c, label, group in COSTUMES],
        "states": STATES,
        "fallback": FALLBACK,
        "cells": cells,
        "extras": [{"source": name, "note": note, "gif": "../gif/%s.gif" % name, "sheet": "../sheets/%s.png" % name}
                   for name, note in EXTRAS.items()],
    }
