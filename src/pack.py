"""Spesifikasi Gobyet Character Pack: kostum = identitas, state = sedang apa.

Ini satu-satunya tempat yang memetakan animasi yang ada ke sel kostum x state.
Sel "asli" adalah 7 aset yang sudah ada sebelum Fase 2; sel "baru" dibuat di Fase 2.
src/export.py membaca modul ini untuk menulis pack/manifest.json, lengkap dengan
jumlah frame dan durasi per frame yang diambil langsung dari SCENES.
"""

FORMAT = "gobyet-pack/1"

# Kostum: (id, label, group). Urutan = urutan tampilan di preview (baris dikelompokkan per group).
# 12 kostum MVP lama, lalu kostum baru Fase 2 lanjutan (group special, fantasy, theology, dan gamer).
COSTUMES = [
    ("normal", "Normal", "core"),
    ("normal-gblk", "Normal GBLK", "special"),
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
    ("gamer", "Gamer", "domain"),
    ("knight", "Knight", "fantasy"),
    ("knight-heavy", "Knight: Heavy", "fantasy"),
    ("knight-archer", "Knight: Archer", "fantasy"),
    ("knight-manatarms", "Knight: Man-at-Arms", "fantasy"),
    ("knight-assassin", "Knight: Assassin", "fantasy"),
    ("viking", "Viking", "fantasy"),
    ("viking-berserker", "Viking: Berserker", "fantasy"),
    ("viking-huscarl", "Viking: Huscarl", "fantasy"),
    ("viking-gestir", "Viking: Gestir", "fantasy"),
    ("viking-bondi", "Viking: Bondi", "fantasy"),
    ("pirate", "Pirate", "fantasy"),
    ("pirate-captain", "Pirate: Captain", "fantasy"),
    ("pirate-skirmisher", "Pirate: Skirmisher", "fantasy"),
    ("pirate-sharpshooter", "Pirate: Sharpshooter", "fantasy"),
    ("pirate-buccaneer", "Pirate: Buccaneer", "fantasy"),
    ("wizard", "Wizard", "fantasy"),
    ("pak-haji", "Pak Haji", "theology"),
    ("priest", "Priest", "theology"),
]

# Field opsional per kostum, ditulis ke manifest hanya bila ada. base = kostum induk untuk fallback.
COSTUME_META = {
    "normal-gblk": {"base": "normal", "caption": "GBLK = Gamers Berkembang Lewat Kebodohan"},
}
for _faction, _variants in (("knight", ("heavy", "archer", "manatarms", "assassin")),
                            ("viking", ("berserker", "huscarl", "gestir", "bondi")),
                            ("pirate", ("captain", "skirmisher", "sharpshooter", "buccaneer"))):
    for _v in _variants:
        COSTUME_META["%s-%s" % (_faction, _v)] = {"base": _faction}

STATE_IDS = ["idle", "thinking", "victory", "defeated", "judging", "suspicious", "attack", "shocked", "happy",
             "dance-a", "dance-b", "dance-c", "reveal"]

# APPLIES: satu-satunya sumber sel yang berlaku. {kostum: {state: "required" | "optional"}}.
# Sel yang tidak tercantum tidak berlaku ("-" di preview).
R, O = "required", "optional"
_CORE4 = {"idle": R, "thinking": R, "victory": R, "defeated": R}
APPLIES = {c: dict(_CORE4, shocked=O, happy=O) for c, _, g in COSTUMES if g in ("core", "role") or c in (
    "greek-philosopher", "academic", "scientist", "mathematician", "lawyer", "hacker", "detective")}
APPLIES["judge"]["judging"] = O
APPLIES["skeptic"].update(suspicious=O, attack=O)
APPLIES["detective"]["suspicious"] = O  # keputusan pemilik (Fase 2 lanjutan)
APPLIES["normal"]["dance-a"] = O
APPLIES["champion"]["dance-a"] = O
APPLIES["gamer"] = dict(_CORE4, happy=O, shocked=O, **{"dance-a": O})
APPLIES["normal-gblk"] = {"idle": R, "victory": R, "defeated": R, "reveal": O, "happy": O,
                          "dance-a": O, "dance-b": O, "dance-c": O}
for _c in ("knight", "wizard"):
    APPLIES[_c] = dict(_CORE4, shocked=O, attack=O)
for _c in ("viking", "pirate"):
    APPLIES[_c] = dict(_CORE4, attack=O, **{"dance-a": O})
for _c in ("pak-haji", "priest"):
    APPLIES[_c] = dict(_CORE4, happy=O)
for _c, _meta in COSTUME_META.items():
    if _meta.get("base") in ("knight", "viking", "pirate"):
        APPLIES[_c] = {"idle": R, "victory": R, "attack": O}


def _states():
    """Daftar state untuk kompatibilitas manifest lama: "required" bila wajib di setiap kostum yang
    memakainya, "costumes" = allowlist bila state tidak berlaku untuk semua kostum."""
    out = []
    all_ids = [c for c, _, _ in COSTUMES]
    for sid in STATE_IDS:
        users = [c for c in all_ids if sid in APPLIES[c]]
        st = {"id": sid, "label": sid, "required": all(APPLIES[c][sid] == R for c in users)}
        if users != all_ids:
            st["costumes"] = users
        out.append(st)
    return out


STATES = _states()

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

# Aset baru hasil Fase 2, per gerbang persetujuan. Dibuat dengan rig yang sama (src/roles.py untuk
# kostum ROLE, src/domains.py untuk Normal dan kostum DOMAIN). Angka kedua = frame kunci: frame yang
# ditampilkan saat reduced motion / mode statis, dipilih sebagai pose yang paling mewakili state.
NEW = {
    ("referee", "idle"): ("referee-idle", 2, "A"),
    ("referee", "thinking"): ("referee-thinking", 12, "A"),
    ("judge", "idle"): ("judge-idle", 0, "B"),
    ("judge", "thinking"): ("judge-thinking", 0, "B"),
    ("judge", "judging"): ("judge-judging", 9, "B"),
    ("skeptic", "idle"): ("skeptic-idle", 0, "B"),
    ("skeptic", "suspicious"): ("skeptic-suspicious", 0, "B"),
    ("skeptic", "attack"): ("skeptic-attack", 7, "B"),
    ("champion", "idle"): ("champion-idle", 0, "B"),
    ("champion", "victory"): ("champion-victory", 4, "B"),
    ("greek-philosopher", "idle"): ("greek-philosopher-idle", 0, "C"),
    ("greek-philosopher", "victory"): ("greek-philosopher-victory", 6, "C"),
    ("greek-philosopher", "defeated"): ("greek-philosopher-defeated", 7, "C"),
    ("academic", "thinking"): ("academic-thinking", 10, "C"),
    ("academic", "victory"): ("academic-victory", 4, "C"),
    ("academic", "defeated"): ("academic-defeated", 0, "C"),
    ("normal", "thinking"): ("normal-thinking", 10, "C"),
    ("normal", "victory"): ("normal-victory", 4, "C"),
    ("normal", "defeated"): ("normal-defeated", 0, "C"),
    ("scientist", "idle"): ("scientist-idle", 0, "D"),
    ("scientist", "shocked"): ("scientist-shocked", 6, "D"),
    ("scientist", "victory"): ("scientist-victory", 4, "D"),
    ("mathematician", "idle"): ("mathematician-idle", 0, "D"),
    ("mathematician", "thinking"): ("mathematician-thinking", 10, "D"),
    ("mathematician", "victory"): ("mathematician-victory", 5, "D"),
    ("hacker", "thinking"): ("hacker-thinking", 8, "E"),
    ("hacker", "shocked"): ("hacker-shocked", 6, "E"),
    ("hacker", "victory"): ("hacker-victory", 5, "E"),
    ("detective", "idle"): ("detective-idle", 0, "E"),
    ("detective", "suspicious"): ("detective-suspicious", 8, "E"),
    ("detective", "shocked"): ("detective-shocked", 5, "E"),
    ("detective", "victory"): ("detective-victory", 5, "E"),
    ("lawyer", "idle"): ("lawyer-idle", 6, "E"),
    ("lawyer", "thinking"): ("lawyer-thinking", 10, "E"),
    ("lawyer", "victory"): ("lawyer-victory", 5, "E"),
    ("gamer", "idle"): ("gamer-idle", 2, "G"),
    ("gamer", "thinking"): ("gamer-thinking", 7, "G"),
    ("gamer", "happy"): ("gamer-happy", 3, "G"),
    ("gamer", "shocked"): ("gamer-shocked", 4, "G"),
    ("gamer", "victory"): ("gamer-victory", 5, "G"),
    ("gamer", "defeated"): ("gamer-defeated", 9, "G"),
    ("gamer", "dance-a"): ("gamer-dance-a", 0, "G"),
    ("normal-gblk", "idle"): ("normal-gblk-idle", 0, "G"),
    ("normal-gblk", "reveal"): ("normal-gblk-reveal", 9, "G"),
    ("normal-gblk", "happy"): ("normal-gblk-happy", 3, "G"),
    ("normal-gblk", "victory"): ("normal-gblk-victory", 5, "G"),
    ("normal-gblk", "defeated"): ("normal-gblk-defeated", 0, "G"),
    ("normal-gblk", "dance-a"): ("normal-gblk-dance-a", 0, "G"),
    ("normal-gblk", "dance-b"): ("normal-gblk-dance-b", 0, "G"),
    ("normal-gblk", "dance-c"): ("normal-gblk-dance-c", 0, "G"),
    ("knight", "idle"): ("knight-idle", 0, "H"),
    ("knight", "thinking"): ("knight-thinking", 6, "H"),
    ("knight", "shocked"): ("knight-shocked", 5, "H"),
    ("knight", "attack"): ("knight-attack", 5, "H"),
    ("knight", "victory"): ("knight-victory", 6, "H"),
    ("knight", "defeated"): ("knight-defeated", 8, "H"),
    ("viking", "idle"): ("viking-idle", 0, "H"),
    ("viking", "thinking"): ("viking-thinking", 6, "H"),
    ("viking", "attack"): ("viking-attack", 5, "H"),
    ("viking", "victory"): ("viking-victory", 6, "H"),
    ("viking", "defeated"): ("viking-defeated", 8, "H"),
    ("viking", "dance-a"): ("viking-dance-a", 0, "H"),
    ("pirate", "idle"): ("pirate-idle", 0, "H"),
    ("pirate", "thinking"): ("pirate-thinking", 6, "H"),
    ("pirate", "attack"): ("pirate-attack", 5, "H"),
    ("pirate", "victory"): ("pirate-victory", 4, "H"),
    ("pirate", "defeated"): ("pirate-defeated", 8, "H"),
    ("pirate", "dance-a"): ("pirate-dance-a", 0, "H"),
    ("wizard", "idle"): ("wizard-idle", 0, "H"),
    ("wizard", "thinking"): ("wizard-thinking", 6, "H"),
    ("wizard", "shocked"): ("wizard-shocked", 4, "H"),
    ("wizard", "attack"): ("wizard-attack", 4, "H"),
    ("wizard", "victory"): ("wizard-victory", 6, "H"),
    ("wizard", "defeated"): ("wizard-defeated", 8, "H"),
    ("pak-haji", "idle"): ("pak-haji-idle", 0, "I"),
    ("pak-haji", "thinking"): ("pak-haji-thinking", 6, "I"),
    ("pak-haji", "happy"): ("pak-haji-happy", 4, "I"),
    ("pak-haji", "victory"): ("pak-haji-victory", 6, "I"),
    ("pak-haji", "defeated"): ("pak-haji-defeated", 8, "I"),
    ("priest", "idle"): ("priest-idle", 0, "I"),
    ("priest", "thinking"): ("priest-thinking", 6, "I"),
    ("priest", "happy"): ("priest-happy", 4, "I"),
    ("priest", "victory"): ("priest-victory", 6, "I"),
    ("priest", "defeated"): ("priest-defeated", 8, "I"),
    ("knight-heavy", "idle"): ("knight-heavy-idle", 0, "J"),
    ("knight-heavy", "attack"): ("knight-heavy-attack", 5, "J"),
    ("knight-heavy", "victory"): ("knight-heavy-victory", 5, "J"),
    ("knight-archer", "idle"): ("knight-archer-idle", 0, "J"),
    ("knight-archer", "attack"): ("knight-archer-attack", 6, "J"),
    ("knight-archer", "victory"): ("knight-archer-victory", 4, "J"),
    ("knight-manatarms", "idle"): ("knight-manatarms-idle", 0, "J"),
    ("knight-manatarms", "attack"): ("knight-manatarms-attack", 5, "J"),
    ("knight-manatarms", "victory"): ("knight-manatarms-victory", 4, "J"),
    ("knight-assassin", "idle"): ("knight-assassin-idle", 0, "J"),
    ("knight-assassin", "attack"): ("knight-assassin-attack", 5, "J"),
    ("knight-assassin", "victory"): ("knight-assassin-victory", 4, "J"),
    ("viking-berserker", "idle"): ("viking-berserker-idle", 0, "J"),
    ("viking-berserker", "attack"): ("viking-berserker-attack", 5, "J"),
    ("viking-berserker", "victory"): ("viking-berserker-victory", 4, "J"),
    ("viking-huscarl", "idle"): ("viking-huscarl-idle", 0, "J"),
    ("viking-huscarl", "attack"): ("viking-huscarl-attack", 5, "J"),
    ("viking-huscarl", "victory"): ("viking-huscarl-victory", 4, "J"),
    ("viking-gestir", "idle"): ("viking-gestir-idle", 0, "J"),
    ("viking-gestir", "attack"): ("viking-gestir-attack", 5, "J"),
    ("viking-gestir", "victory"): ("viking-gestir-victory", 4, "J"),
    ("viking-bondi", "idle"): ("viking-bondi-idle", 0, "J"),
    ("viking-bondi", "attack"): ("viking-bondi-attack", 6, "J"),
    ("viking-bondi", "victory"): ("viking-bondi-victory", 4, "J"),
    ("pirate-captain", "idle"): ("pirate-captain-idle", 0, "J"),
    ("pirate-captain", "attack"): ("pirate-captain-attack", 5, "J"),
    ("pirate-captain", "victory"): ("pirate-captain-victory", 4, "J"),
    ("pirate-skirmisher", "idle"): ("pirate-skirmisher-idle", 0, "J"),
    ("pirate-skirmisher", "attack"): ("pirate-skirmisher-attack", 5, "J"),
    ("pirate-skirmisher", "victory"): ("pirate-skirmisher-victory", 4, "J"),
    ("pirate-sharpshooter", "idle"): ("pirate-sharpshooter-idle", 0, "J"),
    ("pirate-sharpshooter", "attack"): ("pirate-sharpshooter-attack", 6, "J"),
    ("pirate-sharpshooter", "victory"): ("pirate-sharpshooter-victory", 6, "J"),
    ("pirate-buccaneer", "idle"): ("pirate-buccaneer-idle", 0, "J"),
    ("pirate-buccaneer", "attack"): ("pirate-buccaneer-attack", 5, "J"),
    ("pirate-buccaneer", "victory"): ("pirate-buccaneer-victory", 4, "J"),
    ("normal", "shocked"): ("normal-shocked", 4, "F"),
    ("normal", "dance-a"): ("normal-dance-a", 0, "F"),
    ("referee", "victory"): ("referee-victory", 4, "F"),
    ("referee", "defeated"): ("referee-defeated", 8, "F"),
    ("referee", "shocked"): ("referee-shocked", 4, "F"),
    ("referee", "happy"): ("referee-happy", 5, "F"),
    ("judge", "victory"): ("judge-victory", 8, "F"),
    ("judge", "defeated"): ("judge-defeated", 8, "F"),
    ("judge", "shocked"): ("judge-shocked", 4, "F"),
    ("judge", "happy"): ("judge-happy", 4, "F"),
    ("skeptic", "thinking"): ("skeptic-thinking", 9, "F"),
    ("skeptic", "victory"): ("skeptic-victory", 4, "F"),
    ("skeptic", "defeated"): ("skeptic-defeated", 8, "F"),
    ("skeptic", "shocked"): ("skeptic-shocked", 4, "F"),
    ("skeptic", "happy"): ("skeptic-happy", 4, "F"),
    ("champion", "thinking"): ("champion-thinking", 9, "F"),
    ("champion", "defeated"): ("champion-defeated", 8, "F"),
    ("champion", "shocked"): ("champion-shocked", 4, "F"),
    ("champion", "happy"): ("champion-happy", 5, "F"),
    ("champion", "dance-a"): ("champion-dance-a", 0, "F"),
    ("greek-philosopher", "shocked"): ("greek-philosopher-shocked", 5, "F"),
    ("greek-philosopher", "happy"): ("greek-philosopher-happy", 4, "F"),
    ("academic", "shocked"): ("academic-shocked", 4, "F"),
    ("academic", "happy"): ("academic-happy", 5, "F"),
    ("scientist", "defeated"): ("scientist-defeated", 8, "F"),
    ("scientist", "happy"): ("scientist-happy", 5, "F"),
    ("mathematician", "defeated"): ("mathematician-defeated", 8, "F"),
    ("mathematician", "shocked"): ("mathematician-shocked", 4, "F"),
    ("mathematician", "happy"): ("mathematician-happy", 5, "F"),
    ("lawyer", "defeated"): ("lawyer-defeated", 8, "F"),
    ("lawyer", "shocked"): ("lawyer-shocked", 4, "F"),
    ("lawyer", "happy"): ("lawyer-happy", 5, "F"),
    ("hacker", "defeated"): ("hacker-defeated", 8, "F"),
    ("hacker", "happy"): ("hacker-happy", 5, "F"),
    ("detective", "defeated"): ("detective-defeated", 8, "F"),
    ("detective", "happy"): ("detective-happy", 4, "F"),
}

# Profil export. Aset gerbang A-C (dan semua aset asli) diekspor dengan pengaturan lama: palet PAL saja,
# optimize=False, sheet 1x dan @4x. Aset baru mulai Gerbang D: palet PAL + PAL_EXT, GIF optimize=True,
# dan hanya sheet 1x (sheet4x opsional; preview memperbesar sheet 1x tanpa smoothing).
LEGACY_GATES = ("A", "B", "C")


def modern(name):
    """True bila animasi `name` adalah aset baru yang memakai profil export Gerbang D ke atas."""
    for src, _, gate in NEW.values():
        if src == name:
            return gate not in LEGACY_GATES
    return False


# Animasi yang ada tetapi sengaja tidak dimasukkan ke matriks MVP.
EXTRAS = {
    "marah-debug": "Normal: ngamuk ke laptop. Tidak cocok dengan state standar (campuran shocked dan marah).",
    "kondangan": "Kostum peci + batik, di luar 12 kostum MVP.",
}

FALLBACK = ["costume+state", "costume+idle", "base+state", "base+idle", "normal+state", "normal+idle", "placeholder"]


def costume_entry(c, label, group):
    entry = {"id": c, "label": label, "group": group}
    entry.update(COSTUME_META.get(c, {}))
    entry["applies"] = APPLIES[c]
    return entry


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
        if modern(name):
            del cell["sheet4x"]
    return {
        "format": FORMAT,
        "generated_by": "src/export.py (dari src/pack.py)",
        "paths": "relatif terhadap file manifest ini",
        "canvas": {"w": 64, "h": 48},
        "gif_scale": 8,
        "costumes": [costume_entry(c, label, group) for c, label, group in COSTUMES],
        "states": STATES,
        "fallback": FALLBACK,
        "cells": cells,
        "extras": [{"source": name, "note": note, "gif": "../gif/%s.gif" % name, "sheet": "../sheets/%s.png" % name}
                   for name, note in EXTRAS.items()],
    }
