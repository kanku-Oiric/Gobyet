"""Salin subset aset Gobyet v2 yang dibutuhkan arena Battle Royale ke folder skill.

    python3 v2/tools/vendor_skill.py /path/ke/.claude/skills/argument-battle-royale

Yang disalin:
  assets/gobyet/registry.json      registry v2 dipangkas ke state yang dipakai arena
  assets/gobyet/sheets/<id>/*.png  state inti tiap karakter + state peran (wasit, juri, skeptic, champion, defeated)
  assets/gobyet/icons/*.png        ikon aksesori sekunder
  scripts/engine/gobyet_context.py salinan v2/src/context2.py (pemilih karakter per topik)
  scripts/engine/gobyet_resolve.py salinan v2/src/resolve2.py (fallback berantai)
Ditambah Berserker Hero (tokoh utama) dari pack/: kanvas 128x96, durasi per frame, jangkar sendiri, dan skala gambar
2/3 piksel Gobyet (lihat HERO). Karakter v2 berkanvas besar lain (berserker 144x100) tidak disalin: tidak ada domain
atau peran arena yang memilihnya, jadi hanya menambah ukuran halaman.
Sumber kebenaran tetap repo Gobyet; berkas salinan diberi kepala "jangan edit di sini".
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.dirname(HERE)
SRC = os.path.join(V2, "src")
PACK = os.path.join(os.path.dirname(V2), "pack")

CORE = ("idle", "attack", "hit", "victory", "defeat")
# state peran dan adegan arena (selain state inti)
EXTRA = {
    "referee": ["signal_start", "point_winner"],
    "judge": ["write_score", "finalize"],
    "skeptic": ["inspect", "falsification"],
    "champion": ["trophy_raise", "celebrate"],
    "defeated": ["sit", "fall"],
    "wizard": ["cast"],
    "normal-gblk": ["confused", "victory_dance"],
}

# Berserker Hero dari pack/manifest.json. Tidak punya state "hit": exhaustion (bungkuk bertumpu pada pedang, napas
# berat) dipakai sebagai reaksi terkena. Serangan bergantian smash dan leap (variants). run dipakai saat masuk duel dan
# di pembuka arena, rage di pembuka arena. miss tidak dipakai arena, jadi tidak disalin.
HERO = {
    "id": "berserker-hero",
    "name": "Berserker Hero",
    "category": "fantasy",
    "faction": "vikings",
    "role": "hero",
    "silhouette": ["dragon_shield", "masked_helm_with_crest", "greatsword", "segmented_tail_with_arrow_fan", "black_red_armor"],
    "fallback": "viking-berserker",
    "core": {"idle": "idle", "attack": "attack-smash", "hit": "exhaustion", "victory": "victory", "defeat": "defeated"},
    "variants": {"attack": ["attack-smash", "attack-leap"]},
    "anchor": {"x": 66, "baseline": 90, "facing": "right"},
    # 1 piksel hero = 2/3 piksel Gobyet 64x64 (dibulatkan ke atas ke bilangan bulat saat digambar): tinggi helm-ke-lantai
    # hero 66 px, Gobyet tertinggi sekitar 49 px, jadi di skala desktop hero setinggi Gobyet berzirah dan lebih lebar.
    "px": [2, 3],
    "labels": {
        "idle": "berdiri siaga dengan perisai naga dan pedang besar, napas pelan",
        "run": "lari berat, ekor berayun",
        "rage": "kumpul amarah, meledak, pedang diacungkan, frame terakhir ditahan",
        "attack-smash": "ancang-ancang lalu hantaman pedang ke balok kayu",
        "attack-leap": "melompat lalu menebas turun ke balok kayu",
        "exhaustion": "kelelahan: bungkuk bertumpu pada pedang, napas berat (dipakai sebagai reaksi terkena)",
        "defeated": "berlutut bertumpu pada pedang, tertunduk",
        "victory": "topeng membuka (wajah Gobyet), pedang ditancapkan, kaki di batu, darah monster diusap dari bilah",
    },
}


def hero_entry(out_dir):
    """Entri registry + sheet Berserker Hero dari pack/. Mengembalikan (entri, jumlah berkas, ukuran) atau None bila pack tidak ada."""
    man_path = os.path.join(PACK, "manifest.json")
    if not os.path.exists(man_path):
        return None
    with open(man_path, encoding="utf-8") as f:
        cells = json.load(f)["cells"].get(HERO["id"])
    if not cells:
        return None
    states, n, size = {}, 0, 0
    for s, label in HERO["labels"].items():
        cell = cells[s]
        src = os.path.normpath(os.path.join(PACK, cell["sheet"]))
        rel = "sheets/%s/%s.png" % (HERO["id"], s)
        dst = os.path.join(out_dir, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
        n += 1
        size += os.path.getsize(dst)
        durs = list(cell["durations_ms"])
        states[s] = {"frames": cell["frames"], "ms": int(round(sum(durs) / float(len(durs)))), "durations": durs,
                     "loop": cell["loop"], "hold": 0, "label": label, "sheet": rel}
    entry = {k: HERO[k] for k in ("id", "name", "category", "faction", "role", "silhouette", "fallback", "core", "variants",
                                  "anchor", "px")}
    entry.update({"acc_anchor": None, "canvas": dict(cells["idle"]["canvas"]), "states": states, "source": "pack/manifest.json",
                  "note": "Tokoh utama Gobyet (pack/, src/hero3.py). Kanvas sendiri; arena menggambarnya dengan jangkar dan skala px."})
    return entry, n, size


def commit():
    try:
        return subprocess.check_output(["git", "-C", V2, "rev-parse", "--short", "HEAD"]).decode().strip()
    except Exception:
        return "tidak diketahui"


def header(src_name, rev):
    return ('# Disalin dari repo Gobyet: v2/src/%s (commit %s) oleh v2/tools/vendor_skill.py.\n'
            '# Jangan edit di sini; ubah di repo Gobyet lalu salin ulang.\n' % (src_name, rev))


def main(dest):
    with open(os.path.join(V2, "registry.json")) as f:
        reg = json.load(f)
    rev = commit()
    out_dir = os.path.join(dest, "assets", "gobyet")
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)
    chars = []
    n_files = 0
    size = 0
    skipped = []
    for c in reg["characters"]:
        if "canvas" in c and (c["canvas"]["w"], c["canvas"]["h"]) != (reg["canvas"]["w"], reg["canvas"]["h"]):
            # karakter v2 berkanvas besar (berserker 144x100): tidak dipilih domain atau peran arena mana pun
            skipped.append(c["id"])
            continue
        keep = []
        for core in CORE:
            s = c["core"].get(core)
            if s and s not in keep:
                keep.append(s)
        for s in EXTRA.get(c["id"], []):
            if s in c["states"] and s not in keep:
                keep.append(s)
        states = {}
        for s in keep:
            st = dict(c["states"][s])
            st.pop("gif", None)
            src = os.path.join(V2, st["sheet"])
            dst = os.path.join(out_dir, st["sheet"])
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src, dst)
            n_files += 1
            size += os.path.getsize(dst)
            states[s] = st
        core = {k: v for k, v in c["core"].items() if v in states}
        entry = dict(c, states=states, core=core)
        chars.append(entry)
    hero = hero_entry(out_dir)
    if hero:
        chars.append(hero[0])
        n_files += hero[1]
        size += hero[2]
    icons = {}
    for name, rel in reg.get("icons", {}).items():
        dst = os.path.join(out_dir, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(os.path.join(V2, rel), dst)
        icons[name] = rel
        size += os.path.getsize(dst)
    for k in ("vfx", "blood", "event_types"):
        reg.pop(k, None)
    sub = dict(reg, characters=chars, icons=icons, source={"repo": "kanku-Oiric/Gobyet", "path": "v2", "commit": rev},
               note="Subset untuk arena Battle Royale. Sumber kebenaran: repo Gobyet v2 (registry.json lengkap, GIF, sheet semua state).")
    with open(os.path.join(out_dir, "registry.json"), "w") as f:
        json.dump(sub, f, ensure_ascii=False, indent=1)
        f.write("\n")
    with open(os.path.join(out_dir, "README.md"), "w") as f:
        f.write("# Aset Gobyet untuk arena\n\n"
                "Disalin otomatis dari repo Gobyet (`v2/`, commit `%s`) oleh `v2/tools/vendor_skill.py`. "
                "Jangan edit berkas di sini; ubah di repo Gobyet, ekspor ulang, lalu salin ulang.\n\n"
                "- `registry.json`: karakter, state yang dipakai arena, alias state inti, rantai fallback, jangkar.\n"
                "- `sheets/<id>/<state>.png`: strip frame 64x64 berpalet, latar transparan.\n"
                "- `sheets/berserker-hero/<state>.png`: Berserker Hero (tokoh utama) dari `pack/` repo Gobyet, strip frame 128x96 "
                "dengan durasi per frame; entri registry-nya punya `canvas`, `anchor`, `px` (skala gambar relatif Gobyet), "
                "`variants` (serangan bergantian), dan `hit` -> `exhaustion`.\n"
                "- `icons/`: ikon aksesori 16x16 untuk topik dua domain (satu primer + satu sekunder).\n" % rev)
    eng = os.path.join(dest, "scripts", "engine")
    for src_name, dst_name in (("context2.py", "gobyet_context.py"), ("resolve2.py", "gobyet_resolve.py")):
        with open(os.path.join(SRC, src_name)) as f:
            body = f.read()
        with open(os.path.join(eng, dst_name), "w") as f:
            f.write(header(src_name, rev) + body)
    print("karakter %d, sheet %d, ukuran aset %.1f KB, commit %s" % (len(chars), n_files, size / 1024.0, rev))
    if skipped:
        print("dilewati (karakter v2 berkanvas besar yang tidak dipakai arena):", ", ".join(skipped))


if __name__ == "__main__":
    main(sys.argv[1])
