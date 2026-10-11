#!/usr/bin/env python3
"""Diagnosis seam loop per aset: selisih piksel tiap pasangan frame berurutan (termasuk frame terakhir -> f0),
median dan maksimum, dan peta selisih per elemen (kepala, badan, lengan, ekor, prop, efek).

    python3 tools/seam_diag.py knight-heavy-idle hacker-defeated ...

Setiap piksel diberi label elemen dari fungsi gambar yang terakhir menulisnya: fungsi rig dan kostum
di-instrumentasi seperti audit V8 (semua nama modul yang menunjuk ke fungsi itu diganti sementara).
Selisih = jumlah posisi piksel yang warnanya berbeda (termasuk muncul atau hilang), sama dengan metrik V4.
Elemen per piksel yang berubah diambil dari frame sesudah transisi; bila piksel hilang, dari frame sebelumnya.

Status per elemen pada seam: "loncatan" bila selisih elemen itu di seam > 1,25 x selisih terbesar elemen yang
sama di langkah internal (dihitung searah dan terbalik) DAN > 8 px (elemen tidak kembali mulus ke pose awal);
selain itu "mulus". Bukti pengulangan: pasangan (f[n-1], f0) dicocokkan per piksel, di luar ekor, dengan semua
langkah internal searah dan terbalik; 0 px berarti seam adalah gerakan yang sama dengan langkah internal itu.
"""
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))

import monkey  # noqa: E402
import export  # noqa: E402

LAYERS = {
    "ekor": ["tail"],
    "kepala": ["head", "open_helmet", "horned_helmet", "tricorn", "captain_hat", "bandana", "hood", "fur_headband",
               "wizard_hat", "kopiah", "deerstalker", "mortarboard", "wild_hair", "einstein_moustache", "sunglasses",
               "beard", "laurel", "peci"],
    "badan": ["dressed_body", "sitting_body", "tabard_body", "vest_body", "coat_body", "robe_body", "fur_mantle",
              "koko_sarung", "cassock", "referee_shirt", "judge_robe", "skeptic_sweater", "champion_body", "math_vest",
              "lawyer_suit", "gamer_body", "lying_body", "pauldron"],
    "lengan": ["arm", "referee_arm", "judge_arm", "wizard_arm"],
    "efek": ["puff", "spark_lines", "bubble", "mini_text", "thought_dots", "dots_or_mark", "dust", "confetti", "sigh",
             "aura", "smoke_ring", "bang"],
    "layar": ["terminal"],
}
ORDER = ["kepala", "badan", "lengan", "ekor", "prop", "layar", "efek"]
JUMP_RATIO, JUMP_MIN = 1.25, 8


def instrument():
    """Ganti fungsi gambar di semua modul dengan pembungkus yang mencatat lapisan aktif; Canvas.put mencatat
    lapisan per piksel. Mengembalikan fungsi pemulih."""
    stack = []
    patched = []
    by_name = {n: layer for layer, names in LAYERS.items() for n in names}
    originals = {}
    for mod in list(sys.modules.values()):
        d = getattr(mod, "__dict__", None)
        if not isinstance(d, dict) or not getattr(mod, "__file__", "") or "gobyet" not in (getattr(mod, "__file__", "") or ""):
            continue
        for key, val in list(d.items()):
            if key in by_name and callable(val) and getattr(val, "__module__", "").split(".")[0] in (
                    "monkey", "costumes", "roles", "domains", "special", "fantasy", "theology", "variants", "pelengkap"):
                originals.setdefault(val, None)
    wrappers = {}
    for fn in originals:
        layer = by_name[fn.__name__]

        def make(fn=fn, layer=layer):
            def wrapper(*a, **k):
                stack.append(layer)
                try:
                    return fn(*a, **k)
                finally:
                    stack.pop()
            wrapper.__wrapped_orig__ = fn
            return wrapper
        wrappers[fn] = make()
    for mod in list(sys.modules.values()):
        d = getattr(mod, "__dict__", None)
        if not isinstance(d, dict):
            continue
        for key, val in list(d.items()):
            if callable(val) and getattr(val, "__hash__", None) and val in wrappers:
                d[key] = wrappers[val]
                patched.append((d, key, val))
    real_put = monkey.Canvas.put

    def put(self, x, y, c):
        if 0 <= x < monkey.W and 0 <= y < monkey.H and c:
            if not hasattr(self, "owner"):
                self.owner = {}
            self.owner[(int(x), int(y))] = stack[-1] if stack else "prop"
        return real_put(self, x, y, c)
    monkey.Canvas.put = put

    def restore():
        monkey.Canvas.put = real_put
        for d, key, val in patched:
            d[key] = val
    return restore


def diff(a, b):
    """Posisi yang berbeda antara dua frame, dengan elemen penyebabnya."""
    out = {}
    for p in set(a.px) | set(b.px):
        if a.px.get(p) != b.px.get(p):
            owner = getattr(b, "owner", {}).get(p) if p in b.px else getattr(a, "owner", {}).get(p)
            out[p] = owner or "prop"
    return out


def by_layer(d):
    counts = {k: 0 for k in ORDER}
    for layer in d.values():
        counts[layer] = counts.get(layer, 0) + 1
    return counts


def diagnose(name, scenes):
    fn, n, ms = scenes[name]
    frames = [fn(i) for i in range(n)]
    steps = [diff(frames[i], frames[(i + 1) % n]) for i in range(n)]
    sizes = [len(s) for s in steps]
    internal = sizes[:-1]
    layers = [by_layer(s) for s in steps]
    # atribusi elemen tidak simetris (piksel yang hilang diberi elemen frame sebelumnya), jadi langkah internal
    # juga dihitung dalam arah terbalik; seam yang membalik langkah internal tidak boleh terbaca sebagai loncatan
    layers_rev = [by_layer(diff(frames[i + 1], frames[i])) for i in range(n - 1)]
    kmax = max(range(n - 1), key=lambda i: sizes[i])
    seam_layers = layers[-1]
    verdict = {}
    for layer in ORDER:
        inner_max = max(max(l[layer] for l in layers[:-1]), max(l[layer] for l in layers_rev))
        s = seam_layers[layer]
        if s == 0 and inner_max == 0:
            continue
        jump = s > JUMP_RATIO * inner_max and s > JUMP_MIN
        verdict[layer] = {"seam": s, "maks_internal": inner_max, "status": "loncatan" if jump else "mulus"}
    # bukti pengulangan: cari langkah internal (f[k] -> f[k+1]) yang pasangan framenya sama persis dengan
    # (f[n-1], f0) di luar ekor, searah atau terbalik. 0 px berarti seam adalah gerakan yang sama dengan langkah
    # itu (searah: pola periodik; terbalik: seam membatalkan langkah itu).
    def no_tail(cv):
        own = getattr(cv, "owner", {})
        return {p: c for p, c in cv.px.items() if own.get(p) != "ekor"}

    def dpx(a, b):
        return sum(1 for p in set(a) | set(b) if a.get(p) != b.get(p))
    nt = [no_tail(f) for f in frames]
    best = {}
    for rev in (False, True):  # searah lebih dulu; arah terbalik hanya dipakai bila lebih cocok
        for k in range(n - 1):
            a, b = (nt[k + 1], nt[k]) if rev else (nt[k], nt[k + 1])
            score = (dpx(nt[-1], a), dpx(nt[0], b))
            if rev not in best or sum(score) < sum(best[rev][1]):
                best[rev] = (k, score)
    twin_rev = sum(best[True][1]) < sum(best[False][1])
    twin, (rep_before, rep_after) = best[twin_rev]
    return {
        "aset": name, "frame": n, "selisih": sizes, "median_internal": statistics.median(internal),
        "maks_internal": max(internal), "langkah_maks": "f%d->f%d" % (kmax, kmax + 1), "seam": sizes[-1],
        "seam_per_elemen": seam_layers, "maks_per_elemen": layers[kmax],
        "langkah_kembar": ("f%d->f%d" % (twin + 1, twin)) if twin_rev else ("f%d->f%d" % (twin, twin + 1)),
        "kembar_terbalik": twin_rev, "kembar_per_elemen": layers[twin],
        "elemen": verdict,
        "ulang_sebelum": rep_before, "ulang_sesudah": rep_after, "_frames": frames, "_steps": steps, "_kmax": kmax,
        "loncatan": sorted(k for k, v in verdict.items() if v["status"] == "loncatan"),
    }


COLORS = {"kepala": (220, 60, 50), "badan": (50, 90, 200), "lengan": (240, 150, 30), "ekor": (40, 160, 70),
          "prop": (140, 60, 180), "layar": (30, 170, 190), "efek": (230, 200, 20)}


def diff_images(results, out_path, scale=3):
    """Per aset satu baris: f[n-1], f0, peta selisih seam | f[k], f[k+1], peta selisih langkah terbesar.
    Peta: piksel berubah diwarnai per elemen, piksel tetap abu pucat."""
    from PIL import Image, ImageDraw
    fw, fh = 64 * scale + 6, 48 * scale + 16
    lw = 150
    im = Image.new("RGB", (lw + 6 * fw + 20, len(results) * fh + 40), (250, 247, 240))
    d = ImageDraw.Draw(im)
    x = lw
    for k, c in COLORS.items():
        d.rectangle((x, 6, x + 10, 16), fill=c)
        d.text((x + 14, 6), k, fill=(60, 50, 40))
        x += 80
    for row, r in enumerate(results):
        y = 28 + row * fh
        n, frames, steps, kmax = r["frame"], r["_frames"], r["_steps"], r["_kmax"]
        d.text((4, y + fh // 2 - 12), r["aset"], fill=(60, 50, 40))
        d.text((4, y + fh // 2), "seam %d / maks %d" % (r["seam"], r["maks_internal"]), fill=(110, 90, 70))

        def dmap(a, b, dd):
            m = Image.new("RGB", (64, 48), (250, 247, 240))
            for p in set(a.px) | set(b.px):
                m.putpixel(p, (215, 210, 200))
            for p, layer in dd.items():
                m.putpixel(p, COLORS.get(layer, (0, 0, 0)))
            return m.resize((64 * scale, 48 * scale), Image.NEAREST)
        cells = [(frames[-1].image(scale, bg=(250, 247, 240)), "f%d" % (n - 1)), (frames[0].image(scale, bg=(250, 247, 240)), "f0"),
                 (dmap(frames[-1], frames[0], steps[-1]), "seam"),
                 (frames[kmax].image(scale, bg=(250, 247, 240)), "f%d" % kmax),
                 (frames[kmax + 1].image(scale, bg=(250, 247, 240)), "f%d" % (kmax + 1)),
                 (dmap(frames[kmax], frames[kmax + 1], steps[kmax]), "maks f%d->f%d" % (kmax, kmax + 1))]
        for j, (img, label) in enumerate(cells):
            xx = lw + j * fw + (14 if j >= 3 else 0)
            im.paste(img.convert("RGB"), (xx, y + 12))
            d.text((xx, y), label, fill=(60, 50, 40))
    im.save(out_path, optimize=True)


def main():
    args = sys.argv[1:]
    if "--img" in args:
        i = args.index("--img")
        args = args[:i] + args[i + 2:]
    names = [a for a in args if not a.startswith("--")]
    scenes = export.all_scenes()
    restore = instrument()
    try:
        results = [diagnose(nm, scenes) for nm in names]
    finally:
        restore()
    if "--img" in sys.argv:
        diff_images(results, sys.argv[sys.argv.index("--img") + 1])
    if "--json" in sys.argv:
        print(json.dumps([{k: v for k, v in r.items() if not k.startswith("_")} for r in results], indent=1))
        return
    for r in results:
        print("%s  (%d frame)" % (r["aset"], r["frame"]))
        print("  selisih f0->f1 ... f%d->f0: %s" % (r["frame"] - 1, r["selisih"]))
        print("  median internal %s, maks internal %d (%s), seam %d, seam/median %.2f, seam/maks %.2f" % (
            r["median_internal"], r["maks_internal"], r["langkah_maks"], r["seam"],
            r["seam"] / max(1, r["median_internal"]), r["seam"] / max(1, r["maks_internal"])))
        fmt = lambda d: ", ".join("%s %d" % (k, d[k]) for k in ORDER if d.get(k))  # noqa: E731
        print("  seam per elemen:            %s" % fmt(r["seam_per_elemen"]))
        print("  langkah maks per elemen:    %s" % fmt(r["maks_per_elemen"]))
        print("  langkah kembar %-9s:   %s" % (r["langkah_kembar"], fmt(r["kembar_per_elemen"])))
        print("  per elemen (seam vs maks internal elemen itu): %s" % ", ".join(
            "%s %d/%d %s" % (k, v["seam"], v["maks_internal"], v["status"]) for k, v in r["elemen"].items()))
        print("  pengulangan: pasangan (f%d, f0) vs langkah %s%s: beda %d px dan %d px di luar ekor (0 = seam %s langkah itu persis)" % (
            r["frame"] - 1, r["langkah_kembar"], " (arah terbalik)" if r["kembar_terbalik"] else "", r["ulang_sebelum"],
            r["ulang_sesudah"], "membalik" if r["kembar_terbalik"] else "mengulang"))
        print("  kesimpulan: %s" % ("LONCATAN pada " + ", ".join(r["loncatan"]) if r["loncatan"] else "tidak ada elemen yang meloncat"))
        print()


if __name__ == "__main__":
    main()
