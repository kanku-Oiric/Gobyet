"""QA visual v2 (bagian 53-55, 66-67): siluet, grayscale, skala, baseline, seam, identitas wajah.
Membaca sheet hasil ekspor (v2/sheets) lewat registry.json, menulis metrik JSON dan gambar galeri.

    python3 v2/tools/visual_qa.py [--out DIR]

Uji pengenalan otomatis adalah PROKSI, bukan pengenalan manusia: siluet idle f0 tiap karakter menjadi galeri;
frame lain (idle tengah, attack, victory) diperkecil ke 100/75/50/25% lalu dicocokkan ke galeri dengan IoU tertinggi.
Benar bila tetangga terdekat adalah karakter itu sendiri.
"""
import itertools
import json
import os
import statistics
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.dirname(HERE)
W = H = 64
BASE = 59
FACE = {(226, 172, 128), (198, 142, 100), (236, 140, 108), (206, 110, 84)}
BG = (250, 247, 240)

with open(os.path.join(V2, "registry.json")) as f:
    REG = json.load(f)
CH = {c["id"]: c for c in REG["characters"]}

# kelompok galeri (bagian 67)
GROUPS = [
    ("FANTASY", [c for c in CH if CH[c]["category"] == "fantasy"]),
    ("DOMAIN", [c for c in CH if CH[c]["category"] == "domain"]),
    ("ROLE", [c for c in CH if CH[c]["category"] == "role"]),
    ("SPECIAL", [c for c in CH if CH[c]["category"] == "special"]),
]


def frames(cid, state):
    st = CH[cid]["states"][state]
    im = Image.open(os.path.join(V2, st["sheet"])).convert("RGBA")
    return [im.crop((i * W, 0, (i + 1) * W, H)) for i in range(st["frames"])]


def mask(im):
    a = im.split()[3]
    return {(x, y) for y in range(im.size[1]) for x in range(im.size[0]) if a.getpixel((x, y))}


def iou(a, b):
    u = len(a | b)
    return len(a & b) / u if u else 1.0


def scaled_mask(im, s):
    """Siluet pada skala s, dikembalikan ke 64x64 (NEAREST) supaya bisa dibandingkan."""
    if s == 1.0:
        return mask(im)
    w = max(1, int(round(W * s)))
    a = im.split()[3].resize((w, w), Image.BOX).point(lambda v: 255 if v >= 96 else 0)
    a = a.resize((W, H), Image.NEAREST)
    return {(x, y) for y in range(H) for x in range(W) if a.getpixel((x, y))}


def gray(im):
    g = Image.new("L", im.size, 255)
    rgb = im.convert("RGB").convert("L")
    g.paste(rgb, mask=im.split()[3])
    return g


def gray_diff(a, b):
    ga, gb = gray(a), gray(b)
    pa, pb = ga.load(), gb.load()
    tot = 0
    n = 0
    ma, mb = mask(a), mask(b)
    for (x, y) in ma | mb:
        tot += abs(pa[x, y] - pb[x, y])
        n += 1
    return tot / n if n else 0.0


def core_state(cid, core):
    c = CH[cid]
    s = c["core"].get(core)
    if s:
        return s
    return c["core"].get("idle") or list(c["states"])[0]


def queries(cid):
    out = []
    idle = core_state(cid, "idle")
    fr = frames(cid, idle)
    out.append(("idle", fr[len(fr) // 2]))
    for core in ("attack", "victory"):
        s = CH[cid]["core"].get(core)
        if s:
            f2 = frames(cid, s)
            out.append((core, f2[0]))
    return out


def recognition(ids):
    gallery = {c: frames(c, core_state(c, "idle"))[0] for c in ids}
    res = {}
    for s in (1.0, 0.75, 0.5, 0.25):
        gm = {c: scaled_mask(im, s) for c, im in gallery.items()}
        ok, tot, miss = 0, 0, []
        for c in ids:
            for (lab, q) in queries(c):
                qm = scaled_mask(q, s)
                best = max(gm, key=lambda k: iou(qm, gm[k]))
                tot += 1
                if best == c:
                    ok += 1
                else:
                    miss.append("%s/%s->%s" % (c, lab, best))
        res["%d%%" % int(s * 100)] = {"benar": ok, "total": tot, "akurasi": round(ok / tot, 3), "salah": miss}
    return res


def recognition_roster(ids):
    """Proksi kedua: galeri berisi f0 tiap state inti tiap karakter (penonton sudah kenal roster);
    query = frame tengah state inti yang sama. Benar bila tetangga terdekat adalah karakter itu sendiri."""
    gal = []
    for c in ids:
        for core in ("idle", "attack", "victory"):
            s = CH[c]["core"].get(core)
            if s:
                gal.append((c, frames(c, s)[0]))
    res = {}
    for sc in (1.0, 0.75, 0.5, 0.25):
        gm = [(c, scaled_mask(im, sc)) for c, im in gal]
        ok, tot, miss = 0, 0, []
        for c in ids:
            for core in ("idle", "attack", "victory"):
                s = CH[c]["core"].get(core)
                if not s:
                    continue
                fr = frames(c, s)
                q = scaled_mask(fr[len(fr) // 2], sc)
                best = max(gm, key=lambda kv: iou(q, kv[1]))[0]
                tot += 1
                ok += best == c
                if best != c:
                    miss.append("%s/%s->%s" % (c, core, best))
        res["%d%%" % int(sc * 100)] = {"benar": ok, "total": tot, "akurasi": round(ok / tot, 3), "salah": miss}
    return res


def faction_iou(ids):
    out = {}
    fac = {}
    for c in ids:
        f = CH[c]["faction"]
        if f in ("knights", "vikings", "pirates"):
            fac.setdefault(f, []).append(c)
    for f, cs in fac.items():
        ms = {c: mask(frames(c, core_state(c, "idle"))[0]) for c in cs}
        pairs = {"%s vs %s" % (a, b): round(iou(ms[a], ms[b]), 3) for a, b in itertools.combinations(cs, 2)}
        out[f] = {"maks": max(pairs.values()), "pasangan": pairs}
    return out


PAIRS_54 = [("knight-heavy", "viking-huscarl"), ("pirate-captain", "pirate-sharpshooter"), ("scientist", "academic")]


def pair_tests():
    out = {}
    for a, b in PAIRS_54:
        fa, fb = frames(a, core_state(a, "idle"))[0], frames(b, core_state(b, "idle"))[0]
        out["%s vs %s" % (a, b)] = {"iou_siluet": round(iou(mask(fa), mask(fb)), 3), "selisih_grayscale": round(gray_diff(fa, fb), 1)}
    return out


def baseline_and_identity(ids):
    """Baseline: tidak ada piksel di bawah lantai; idle: baris terbawah konstan di BASE-1.
    Identitas: piksel wajah krem (F/f) >= ambang di tiap frame yang tidak kosong."""
    below, idle_bad, face_min, empty = [], [], {}, []
    for c in ids:
        for s, st in CH[c]["states"].items():
            for i, fr in enumerate(frames(c, s)):
                m = mask(fr)
                if not m:
                    empty.append("%s/%s f%d" % (c, s, i))
                    continue
                low = max(y for _, y in m)
                if low > BASE - 1:
                    below.append("%s/%s f%d (y=%d)" % (c, s, i, low))
                if s == core_state(c, "idle") and low != BASE - 1:
                    idle_bad.append("%s/%s f%d (y=%d)" % (c, s, i, low))
                px = fr.load()
                n = sum(1 for (x, y) in m if px[x, y][:3] in FACE)
                face_min[(c, s)] = min(face_min.get((c, s), 999), n)
    worst = sorted(face_min.items(), key=lambda kv: kv[1])[:12]
    return {"di_bawah_lantai": below, "idle_baseline_bergeser": idle_bad,
            "frame_kosong": empty, "piksel_wajah_min_terendah": [["%s/%s" % k, v] for k, v in worst],
            "piksel_wajah_min_global": min(face_min.values())}


def seams(ids):
    out = []
    for c in ids:
        for s, st in CH[c]["states"].items():
            if not st["loop"] or st["frames"] < 3:
                continue
            fr = [list(f.getdata()) for f in frames(c, s)]
            steps = [sum(1 for a, b in zip(fr[k], fr[(k + 1) % len(fr)]) if a != b) for k in range(len(fr))]
            inner, seam = steps[:-1], steps[-1]
            mx = max(inner) if inner else 0
            out.append({"sel": "%s/%s" % (c, s), "maks": mx, "median": statistics.median(inner), "seam": seam,
                        "gagal": seam > 1.25 * mx, "pop": seam >= 0.9 * mx and mx > 100})
    return out


def gallery_images(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for mode in ("warna", "siluet", "grayscale"):
        rows = []
        for gname, ids in GROUPS:
            rows.append((gname, ids))
        sc = 3
        cw, chh = 64 * sc + 6, 64 * sc + 16
        cols = 8
        nrows = sum((len(ids) + cols - 1) // cols for _, ids in rows) + len(rows)
        im = Image.new("RGB", (cols * cw + 8, nrows * chh + 8), BG)
        d = ImageDraw.Draw(im)
        r = 0
        for gname, ids in rows:
            d.text((6, r * chh + chh // 2), gname, fill=(40, 30, 20))
            r += 1
            for k, c in enumerate(ids):
                fr = frames(c, core_state(c, "idle"))[0]
                if mode == "siluet":
                    a = fr.split()[3]
                    fr = Image.new("RGBA", fr.size, (0, 0, 0, 0))
                    fr.paste((24, 24, 24, 255), mask=a)
                elif mode == "grayscale":
                    g = fr.convert("LA")
                    fr = g.convert("RGBA")
                big = fr.resize((64 * sc, 64 * sc), Image.NEAREST)
                x, y = 4 + (k % cols) * cw, (r + k // cols) * chh + 12
                im.paste(big, (x, y), big)
                d.text((x + 2, y - 11), c, fill=(90, 70, 50))
            r += (len(ids) + cols - 1) // cols
        p = os.path.join(out_dir, "galeri-%s.png" % mode)
        im.save(p, optimize=True)
        paths.append(p)
    # uji skala: tiap karakter pada 100/75/50/25% (ukuran asli, tanpa perbesaran) + versi diperbesar 4x untuk dilihat
    ids = [c for _, g in GROUPS for c in g]
    scales = (1.0, 0.75, 0.5, 0.25)
    cw = 64 + 8
    im = Image.new("RGB", (130 + len(scales) * cw, len(ids) * 70 + 20), BG)
    d = ImageDraw.Draw(im)
    for j, s in enumerate(scales):
        d.text((130 + j * cw, 2), "%d%%" % int(s * 100), fill=(40, 30, 20))
    for r, c in enumerate(ids):
        fr = frames(c, core_state(c, "idle"))[0]
        d.text((4, 20 + r * 70 + 28), c, fill=(60, 40, 30))
        for j, s in enumerate(scales):
            w = max(1, int(round(64 * s)))
            small = fr.resize((w, w), Image.NEAREST)
            im.paste(small, (130 + j * cw + (64 - w) // 2, 20 + r * 70 + (64 - w)), small)
    p = os.path.join(out_dir, "uji-skala.png")
    im.save(p, optimize=True)
    paths.append(p)
    return paths


def main():
    out_dir = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else os.path.join(V2, "qa")
    ids = [c for _, g in GROUPS for c in g]
    fighters = [c for c in ids if CH[c]["category"] in ("fantasy", "domain", "special")]
    res = {
        "karakter": len(ids),
        "state": sum(len(CH[c]["states"]) for c in ids),
        "frame": sum(st["frames"] for c in ids for st in CH[c]["states"].values()),
        "iou_siluet_dalam_faksi": faction_iou(ids),
        "pasangan_bagian_54": pair_tests(),
        "pengenalan_siluet_semua": recognition(ids),
        "pengenalan_siluet_petarung": recognition(fighters),
        "pengenalan_siluet_roster": recognition_roster(ids),
        "baseline_identitas": baseline_and_identity(ids),
        "seam": [s for s in seams(ids) if s["gagal"] or s["pop"]],
        "seam_jumlah_loop": len(seams(ids)),
    }
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "visual-qa.json"), "w") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    res["gambar"] = gallery_images(out_dir)
    print(json.dumps({k: v for k, v in res.items() if k not in ("seam",)}, ensure_ascii=False, indent=1)[:6000])
    print("seam gagal/pop:", len(res["seam"]), "dari", res["seam_jumlah_loop"])


if __name__ == "__main__":
    main()
