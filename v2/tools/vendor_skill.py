"""Salin subset aset Gobyet v2 yang dibutuhkan arena Battle Royale ke folder skill.

    python3 v2/tools/vendor_skill.py /path/ke/.claude/skills/argument-battle-royale

Yang disalin:
  assets/gobyet/registry.json      registry v2 dipangkas ke state yang dipakai arena
  assets/gobyet/sheets/<id>/*.png  state inti tiap karakter + state peran (wasit, juri, skeptic, champion, defeated)
  assets/gobyet/icons/*.png        ikon aksesori sekunder
  scripts/engine/gobyet_context.py salinan v2/src/context2.py (pemilih karakter per topik)
  scripts/engine/gobyet_resolve.py salinan v2/src/resolve2.py (fallback berantai)
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
    for c in reg["characters"]:
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
    icons = {}
    for name, rel in reg.get("icons", {}).items():
        dst = os.path.join(out_dir, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(os.path.join(V2, rel), dst)
        icons[name] = rel
        size += os.path.getsize(dst)
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
                "- `icons/`: ikon aksesori 16x16 untuk topik dua domain (satu primer + satu sekunder).\n" % rev)
    eng = os.path.join(dest, "scripts", "engine")
    for src_name, dst_name in (("context2.py", "gobyet_context.py"), ("resolve2.py", "gobyet_resolve.py")):
        with open(os.path.join(SRC, src_name)) as f:
            body = f.read()
        with open(os.path.join(eng, dst_name), "w") as f:
            f.write(header(src_name, rev) + body)
    print("karakter %d, sheet %d, ukuran aset %.1f KB, commit %s" % (len(chars), n_files, size / 1024.0, rev))


if __name__ == "__main__":
    main(sys.argv[1])
