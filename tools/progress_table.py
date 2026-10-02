#!/usr/bin/env python3
"""Tulis ulang tabel sel di pack/PROGRESS.md (di antara penanda) dari pack/manifest.json.

    python3 tools/progress_table.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START, END = "<!-- tabel-sel:mulai -->", "<!-- tabel-sel:selesai -->"


def table(m):
    lines = ["| Kostum | group | Berlaku | Terisi | Belum terisi (wajib) | Belum terisi (opsional) |", "|---|---|---:|---:|---|---|"]
    tot_app = tot_fill = 0
    for c in m["costumes"]:
        applies = c.get("applies", {})
        row = m["cells"].get(c["id"], {})
        missing_req = [s for s, r in applies.items() if r == "required" and s not in row]
        missing_opt = [s for s, r in applies.items() if r == "optional" and s not in row]
        tot_app += len(applies)
        tot_fill += sum(1 for s in applies if s in row)
        name = c["id"] + (" ← " + c["base"] if c.get("base") else "")
        lines.append("| `%s` | %s | %d | %d | %s | %s |" % (
            name, c["group"], len(applies), sum(1 for s in applies if s in row),
            ", ".join(missing_req) or "-", ", ".join(missing_opt) or "-"))
    lines.append("| **Total** | | **%d** | **%d** | | |" % (tot_app, tot_fill))
    return "\n".join(lines)


def main():
    with open(os.path.join(ROOT, "pack", "manifest.json"), encoding="utf-8") as fh:
        m = json.load(fh)
    path = os.path.join(ROOT, "pack", "PROGRESS.md")
    text = open(path, encoding="utf-8").read()
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    open(path, "w", encoding="utf-8").write(head + START + "\n" + table(m) + "\n" + END + tail)
    print("pack/PROGRESS.md: tabel sel diperbarui")


if __name__ == "__main__":
    main()
