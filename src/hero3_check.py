"""Pengukuran Berserker Hero v3 (tanpa basis Gobyet) untuk validator V11 dan uji; hanya membaca, tidak menulis aset.

Semua ukuran memakai peta pemilik piksel (`hero.PartCanvas`): hanya piksel yang masih terlihat setelah semua lapisan digambar yang dihitung. Angka bersifat
heuristik dan bukan pernyataan bahwa gaya bagus atau disetujui. Batas minimum keterbacaan (MIN_*) adalah usulan saya dari pengukuran sembilan frame kunci
(kira-kira 70-80% dari nilai terendah yang terukur), BUKAN angka dari brief; pemilik dapat mengubahnya.
"""
from collections import Counter

import hero3 as R
from hero_check import bbox, contrast, iou, side_flags, CENTER_TOL  # noqa: F401  (diekspor ulang untuk validator)

FLOOR = R.FLOOR

# identitas: bukan Gobyet
GOBYET_COLOR_KEYS = {"fs", "fb", "fl", "ei", "cs", "cb", "cl", "ra", "rb", "ew", "mo"}          # bulu, telinga, wajah, mata, hidung, mulut Gobyet
GOBYET_PARTS = {"face", "eye", "ear", "mouth", "brow", "skull", "neck", "helm_cap", "socket", "socket_glow"}
ICHOR_KEYS = {"m1", "m2", "m3"}                                                                   # cairan monster (hijau asam): hanya di state victory

FX_PARTS = {"dust", "chip", "burst", "smear", "block", "speed", "sweat", "breath", "spark", "roar", "steam", "ichor", "glint", "rock"}
HEAD_PARTS = {"helm", "visor_plate", "visor", "grill", "brow_band", "cheek", "ear_disc", "chin", "cavity", "cavity_eye", "cavity_teeth", "sensor", "fin"}
CAVITY_PARTS = ("cavity", "cavity_eye", "cavity_teeth")

# elemen asimetris yang harus tetap di sisinya: -1 kiri, +1 kanan, relatif titik tengah badan (acuan "badan") atau titik tengah helm (acuan "helm").
# Pelindung bahu raksasa di kiri layar, bundar di kanan, ekor ke belakang; jambul menyapu ke belakang helm (saat lari badan condong ke depan,
# jadi jambul diukur terhadap helm, bukan terhadap badan).
SIDED = (("pelindung_bahu_raksasa", ("pauldron_big",), -1, True, "badan"), ("pelindung_bahu_bundar", ("pauldron_small",), +1, True, "badan"),
         ("jambul", ("crest",), -1, True, "helm"), ("ekor_panah", ("tail_arrow",), -1, False, "badan"))

# batas keterbacaan frame kunci (piksel terlihat)
MIN_HELM = (30, 28)          # lebar, tinggi helm
MIN_EYES = 40                # visor (lengan salib) atau lensa rongga: piksel
MIN_PAULDRON = 280
MIN_WEAPON = 300
MIN_GAUNTLET = 100
MIN_CREST = 250


def count(cv, names):
    return sum(1 for o in cv.owner.values() if o in names)


def owners_of(cv, names):
    return {k for k, o in cv.owner.items() if o in names}


def element_dx(cv, center, names):
    """(dx rata-rata piksel terlihat relatif titik tengah badan, jumlah piksel)."""
    pts = owners_of(cv, names)
    if not pts:
        return (0.0, 0)
    return (sum(x + 0.5 for x, _ in pts) / len(pts) - center, len(pts))


def sides(cvs, centers, state=None):
    """{nama: {"seri": [(dx, n)], "tanda": [(i, alasan)], "tidak_terlihat": [i], "wajib_terlihat": bool}} untuk SIDED."""
    out = {}
    helm_centers = []
    for cv, c in zip(cvs, centers):
        pts = owners_of(cv, ("helm",))
        helm_centers.append(sum(x + 0.5 for x, _ in pts) / len(pts) if pts else c)
    for name, parts, expect, must_be_seen, ref in SIDED:
        series = [element_dx(cv, hc_ if ref == "helm" else c, parts) for cv, c, hc_ in zip(cvs, centers, helm_centers)]
        out[name] = {"seri": series, "tanda": side_flags(series, expect), "tidak_terlihat": [i for i, (_, n) in enumerate(series) if n == 0],
                     "wajib_terlihat": must_be_seen}
    return out


def head_height(cv):
    b = bbox(owners_of(cv, HEAD_PARTS))
    return b[3] if b else 0


def eyes_visible(cv):
    """(piksel visor, piksel lensa rongga, piksel rongga seluruhnya): mata terbaca bila salah satu dari dua yang pertama cukup banyak."""
    return count(cv, ("visor",)), count(cv, ("cavity_eye",)), count(cv, CAVITY_PARTS)


def readability(cv):
    h = bbox(owners_of(cv, ("helm",)))
    vis, eye, _ = eyes_visible(cv)
    return {"helm": (h[2], h[3]) if h else (0, 0), "mata": vis + eye, "bahu": count(cv, ("pauldron_big",)), "pedang": count(cv, ("weapon",)),
            "kepalan": count(cv, ("gauntlet",)), "jambul": count(cv, ("crest",))}


def readability_failures(r):
    f = []
    if r["helm"][0] < MIN_HELM[0] or r["helm"][1] < MIN_HELM[1]:
        f.append("helm %dx%d < %dx%d" % (r["helm"] + MIN_HELM))
    for key, lo, label in (("mata", MIN_EYES, "visor/lensa"), ("bahu", MIN_PAULDRON, "pelindung bahu raksasa"), ("pedang", MIN_WEAPON, "pedang"),
                           ("kepalan", MIN_GAUNTLET, "kepalan"), ("jambul", MIN_CREST, "jambul")):
        if r[key] < lo:
            f.append("%s terlihat %d piksel < %d" % (label, r[key], lo))
    return f


def identity_findings(cv):
    """Daftar pelanggaran 'bukan Gobyet' pada satu frame: warna kunci Gobyet atau nama bagian Gobyet."""
    bad = []
    keys = set(cv.px.values()) & GOBYET_COLOR_KEYS
    if keys:
        bad.append("warna Gobyet %s" % sorted(keys))
    parts = {o for o in cv.owner.values() if o} & GOBYET_PARTS
    if parts:
        bad.append("bagian Gobyet %s" % sorted(parts))
    return bad


def mirrored(cv, center):
    """Salinan yang dicerminkan horizontal terhadap x = center (untuk uji: harus ditandai oleh `sides`)."""
    import hero
    out = hero.PartCanvas()
    for (x, y), c in cv.px.items():
        nx = int(round(2 * center - x - 1))
        if 0 <= nx < out.w:
            out.px[(nx, y)] = c
            out.owner[(nx, y)] = cv.owner.get((x, y))
    return out


# ------------------------------------------------------------------ victory: urutan yang diminta pemilik
def foot_on_rock(cv):
    """Piksel sepatu terangkat (tumit di atas baris lantai - 11) yang tepat berada di atas piksel batu (selisih 1-3 piksel): kaki bertumpu di batu."""
    boots = [k for k, o in cv.owner.items() if o == "boot" and k[1] <= FLOOR - 11]
    rock = owners_of(cv, ("rock",))
    return sum(1 for (x, y) in boots if any((x, y + d) in rock for d in (1, 2, 3)))


def hand_on_blade(cv):
    """True bila ada piksel kepalan bertetangga (8 arah) dengan piksel bilah atau noda: tangan menyentuh pedang."""
    blade = owners_of(cv, ("weapon", "ichor"))
    return any((x + dx, y + dy) in blade for (x, y) in owners_of(cv, ("gauntlet",)) for dx in (-1, 0, 1) for dy in (-1, 0, 1))


def victory_series(cvs, poses):
    """Deret ukuran per frame untuk memeriksa urutan victory."""
    out = []
    for cv, p in zip(cvs, poses):
        w = [y for (x, y), o in cv.owner.items() if o == "weapon"]
        c = Counter(cv.owner.values())
        out.append({"rongga": sum(c[k] for k in CAVITY_PARTS), "noda": c["ichor"], "batu": c["rock"], "pedang_atas": min(w) if w else None,
                    "pedang_bawah": max(w) if w else None, "sudut": p["ang"], "debu": c["dust"] > 0, "kilau": c["glint"] > 0,
                    "kaki_di_batu": foot_on_rock(cv), "tangan_di_pedang": hand_on_blade(cv)})
    return out


MIN_ROCK = 80                 # batu terlihat di setiap frame victory
MIN_CAVITY_PEAK = 250         # rongga topeng saat terbuka penuh
MIN_STAIN = 150               # noda cairan monster di awal
MIN_FOOT_CONTACT = 6          # piksel sepatu terangkat yang menapak batu


def victory_findings(cvs, poses):
    """Pemeriksaan urutan victory (topeng buka lalu tutup, pedang diangkat lalu ditusukkan ke tanah, kaki naik batu, noda hilang bertahap).
    Mengembalikan (daftar_gagal, info)."""
    bad = []
    s = victory_series(cvs, poses)
    n = len(s)
    info = {"seri": s}
    if any(x["batu"] < MIN_ROCK for x in s):
        bad.append("batu terlihat kurang dari %d piksel di frame %s" % (MIN_ROCK, [i for i, x in enumerate(s) if x["batu"] < MIN_ROCK]))
    cav = [x["rongga"] for x in s]
    opened = [i for i, v in enumerate(cav) if v > 0]
    if cav[0] != 0 or cav[-1] != 0 or not opened:
        bad.append("topeng harus tertutup di frame awal dan akhir dan terbuka di antaranya (rongga %s)" % cav)
    else:
        peak = cav.index(max(cav))
        info["topeng"] = (opened[0], peak, opened[-1], max(cav))
        if max(cav) < MIN_CAVITY_PEAK:
            bad.append("rongga topeng terbuka penuh hanya %d piksel < %d" % (max(cav), MIN_CAVITY_PEAK))
        if not (opened[0] < peak < opened[-1]):
            bad.append("topeng harus membuka lalu menutup (awal buka f%d, puncak f%d, tutup f%d)" % (opened[0], peak, opened[-1]))
        if any(cav[i] > cav[i + 1] for i in range(opened[0], peak)) or any(cav[i] < cav[i + 1] for i in range(peak, opened[-1])):
            bad.append("bukaan topeng tidak naik lalu turun secara berurutan: %s" % cav)
    # pedang: diangkat tinggi di luar tanah, lalu ditusukkan: ujung menyentuh baris tanah, sudut hampir tegak lurus, dan debu
    raised = min(range(n), key=lambda i: s[i]["pedang_atas"] if s[i]["pedang_atas"] is not None else 999)
    stab = next((i for i in range(raised + 1, n) if s[i]["pedang_bawah"] is not None and s[i]["pedang_bawah"] >= FLOOR - 2 and s[i]["sudut"] >= 84 and s[i]["debu"]), None)
    info["angkat"], info["tusuk"] = raised, stab
    if s[raised]["pedang_bawah"] is None or s[raised]["pedang_bawah"] >= FLOOR - 10 or s[raised]["pedang_atas"] > 20:
        bad.append("pedang tidak terangkat tinggi di luar tanah (puncak f%d: y %s-%s)" % (raised, s[raised]["pedang_atas"], s[raised]["pedang_bawah"]))
    if stab is None:
        bad.append("tidak ada frame pedang menusuk tanah (ujung di baris tanah, sudut >= 84, ada debu) setelah diangkat")
    if opened and stab is not None and not (opened[-1] < raised):
        bad.append("urutan: topeng harus sudah menutup (f%d) sebelum pedang diangkat (f%d)" % (opened[-1], raised))
    # kaki naik batu setelah menusuk, dan bertahan sampai akhir
    contact = [i for i, x in enumerate(s) if x["kaki_di_batu"] >= MIN_FOOT_CONTACT]
    info["kaki"] = contact
    if stab is not None and (len(contact) < 3 or contact[0] <= stab or contact[-1] != n - 1):
        bad.append("kaki harus naik ke batu setelah menusuk (f%d) dan bertahan sampai frame akhir: kontak di %s" % (stab if stab is not None else -1, contact))
    # noda: ada di awal, hilang di akhir, menyusut bertahap saat diusap, tangan menyentuh pedang di frame sebagian
    stain = [x["noda"] for x in s]
    info["noda"] = stain
    if stain[0] < MIN_STAIN:
        bad.append("noda cairan monster di awal hanya %d piksel < %d" % (stain[0], MIN_STAIN))
    if stain[-1] != 0:
        bad.append("noda belum hilang di frame akhir (%d piksel)" % stain[-1])
    if stab is not None:
        tail = stain[stab:]
        if any(tail[i] < tail[i + 1] for i in range(len(tail) - 1)):
            bad.append("noda tidak menyusut berurutan setelah menusuk: %s" % tail)
    partial = [i for i, v in enumerate(stain) if 0.1 * stain[0] < v < 0.9 * stain[0]]
    info["sebagian"] = partial
    if len(partial) < 2:
        bad.append("usapan harus menghapus noda bertahap: frame dengan noda 10-90%% dari awal = %s" % partial)
    for i in partial:
        if not s[i]["tangan_di_pedang"]:
            bad.append("f%d: noda sedang dihapus tetapi kepalan tidak menyentuh pedang" % i)
    if not s[-1]["kilau"]:
        bad.append("bilah bersih di frame akhir harus berkilau (tanpa kilau)")
    return bad, info
