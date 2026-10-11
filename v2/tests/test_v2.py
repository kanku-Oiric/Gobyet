"""Tes Gobyet v2: registry, aset hasil ekspor, resolver + fallback, context mapping, dan uji visual otomatis.

    python3 -m unittest v2/tests/test_v2.py -v

Uji visual di sini memakai sheet hasil `python3 v2/src/export2.py`; jalankan ekspor dulu bila kode sprite berubah
(tes RegistrySync akan gagal bila registry tidak sinkron dengan kode).
"""
import itertools
import json
import os
import shutil
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(V2, "src"))

from PIL import Image  # noqa: E402

import context2  # noqa: E402
from resolve2 import Resolver  # noqa: E402

W = H = 64
BASE = 59
FACE = {(226, 172, 128), (198, 142, 100), (236, 140, 108), (206, 110, 84)}
# warna darah VFX (rig2 bl0-bl3): tidak boleh muncul di sheet karakter mana pun
BLOOD = {(236, 112, 100), (198, 36, 44), (144, 22, 32), (96, 14, 24)}

with open(os.path.join(V2, "registry.json")) as f:
    REG = json.load(f)
CH = {c["id"]: c for c in REG["characters"]}


def size_of(cid):
    """Ukuran kanvas karakter (64x64 standar, atau kanvas sendiri seperti Berserker)."""
    cv = CH[cid].get("canvas", REG["canvas"])
    return cv["w"], cv["h"]


def base_of(cid):
    return CH[cid].get("anchor", REG["anchor"])["baseline"]

# state yang diminta brief per karakter (nama huruf kecil). Karakter tanpa daftar di brief: minimal state inti.
REQUIRED = {
    "knight-heavy": "idle walk guard attack block hit victory defeat",
    "knight-archer": "idle aim draw fire recoil victory defeat",
    "knight-man-at-arms": "idle ready attack swing block recover victory defeat",
    "knight-assassin": "idle stealth attack backstab smoke disappear victory defeat",
    "viking": "idle attack victory defeat",
    "viking-berserker": "idle rage roar axe_attack double_attack hit victory defeat",
    "viking-huscarl": "idle attack victory defeat",
    "viking-gestir": "aim throw recover melee victory",
    "viking-bondi": "idle attack victory defeat",
    "pirate-captain": "command sword pistol point victory",
    "pirate-skirmisher": "run dash attack throw explosion recover",
    "pirate-sharpshooter": "aim shoot recoil reload victory",
    "pirate-buccaneer": "heavy_attack hammer_smash anchor_attack hit victory defeat",
    "hacker": "typing debugging error panic success victory defeat",
    "normal-gblk": "idle think confused sign_raise victory defeat dance_01 dance_02 dance_03 victory_dance",
    "philosopher": "thinking reading contemplating arguing pointing victory",
    "academic": "read write lecture think present victory",
    "scientist": "observe experiment write compare shocked success",
    "mathematician": "calculate write erase think eureka confused",
    "lawyer": "read present object point judge victory",
    "historian": "read_archive compare search write discover",
    "economist": "calculate graph check shocked analyze",
    "psychologist": "observe write think analyze suspicious",
    "sociologist": "observe_crowd draw_network compare analyze",
    "engineer": "measure design build inspect fix",
    "detective": "search inspect magnify discover suspicious point",
    "pak-haji": "read think consult calm present",
    "priest": "read think present calm judge",
    "referee": "enter signal_start signal_stop point_winner exit",
    "judge": "read compare write_score think finalize",
    "skeptic": "inspect squint point contradiction_found counterattack falsification",
    "researcher": "search read compare write archive",
    "champion": "trophy_raise victory celebrate dance",
    "defeated": "hit stagger fall sit leave",
    "wizard": "cast spell_success spell_fail read confused victory",
    "fantasy-knight": "idle attack victory defeat",
    "fantasy-pirate": "idle attack victory defeat",
    "fantasy-viking": "idle attack victory defeat",
    "berserker": "idle ready rage run jump attack heavy_attack leap_spin_slash overhead_smash air_slash rage_attack "
                 "combo hit miss exhausted victory defeat",
}
FIGHTER_CATS = ("fantasy", "domain", "special")
# frame tanpa wajah yang disengaja: hilang di balik asap, berjalan keluar/masuk tepi kanvas
NO_FACE_OK = {("knight-assassin", "disappear"), ("knight-assassin", "defeat"), ("defeated", "leave"), ("referee", "enter"),
              ("referee", "exit")}
_FRAMES = {}


def strip(cid, rel, n):
    w, h = size_of(cid)
    with Image.open(os.path.join(V2, rel)) as src:
        im = src.convert("RGBA")
    return [im.crop((i * w, 0, (i + 1) * w, h)) for i in range(n)]


def frames(cid, state):
    key = (cid, state)
    if key not in _FRAMES:
        st = CH[cid]["states"][state]
        _FRAMES[key] = strip(cid, st["sheet"], st["frames"])
    return _FRAMES[key]


def mask(im):
    a = im.split()[3].load()
    return {(x, y) for y in range(im.size[1]) for x in range(im.size[0]) if a[x, y]}


def iou(a, b):
    return len(a & b) / len(a | b) if (a | b) else 1.0


class Registry(unittest.TestCase):
    def test_all_brief_ids(self):
        self.assertEqual(set(CH), set(REQUIRED))
        self.assertEqual(len(REG["characters"]), len(set(c["id"] for c in REG["characters"])))

    def test_brief_states(self):
        for cid, req in REQUIRED.items():
            missing = [s for s in req.split() if s not in CH[cid]["states"]]
            self.assertEqual(missing, [], cid)

    def test_minimum_frames(self):
        for c in REG["characters"]:
            for s, st in c["states"].items():
                self.assertGreaterEqual(st["frames"], 5, "%s/%s" % (c["id"], s))

    def test_fallback_chain_terminates_at_root(self):
        r = Resolver(REG, V2)
        for cid in CH:
            ch = r.chain(cid)
            self.assertEqual(ch[-1], "normal-gblk", cid)
            self.assertEqual(len(ch), len(set(ch)), cid)

    def test_fighters_have_core_states_themselves(self):
        r = Resolver(REG, V2)
        for cid, c in CH.items():
            if c["category"] not in FIGHTER_CATS:
                continue
            for core in REG["core_states"]:
                got = r.resolve(cid, core)
                self.assertIsNotNone(got, (cid, core))
                self.assertEqual(got["character"], cid, (cid, core))

    def test_champion_label(self):
        self.assertEqual(CH["champion"].get("label"), "TOURNAMENT WINNER")
        self.assertNotIn("ABSOLUTE TRUTH", json.dumps(REG).upper())

    def test_silhouette_tags(self):
        for cid, c in CH.items():
            self.assertGreaterEqual(len(c["silhouette"]), 2, cid)


class RegistrySync(unittest.TestCase):
    """Registry harus sinkron dengan kode (state dan jumlah frame)."""

    def test_sync(self):
        import cast
        for cid in cast.all_ids():
            ch = cast.get(cid)
            self.assertEqual(sorted(ch.states), sorted(CH[cid]["states"]), cid)
            for s, st in ch.states.items():
                self.assertEqual(st.n, CH[cid]["states"][s]["frames"], (cid, s))


class Assets(unittest.TestCase):
    def test_sheets_and_gifs(self):
        for cid, c in CH.items():
            for s, st in c["states"].items():
                sp, gp = os.path.join(V2, st["sheet"]), os.path.join(V2, st["gif"])
                self.assertTrue(os.path.exists(sp), sp)
                self.assertTrue(os.path.exists(gp), gp)
                w, h = size_of(cid)
                with Image.open(sp) as im:
                    self.assertEqual(im.size, (w * st["frames"], h), sp)
                    alphas = set(im.convert("RGBA").split()[3].tobytes())
                self.assertTrue(alphas <= {0, 255}, sp)
                with Image.open(gp) as g:
                    self.assertEqual(g.size, (w * REG["gif_scale"], h * REG["gif_scale"]), gp)
                    total = 0
                    for k in range(getattr(g, "n_frames", 1)):
                        g.seek(k)
                        total += g.info.get("duration", 0)
                # Pillow menggabungkan frame identik berurutan; yang dijaga adalah total durasi animasi.
                durs = st.get("durations") or [st["ms"]] * st["frames"]
                self.assertEqual(len(durs), st["frames"], sp)
                self.assertTrue(all(d % 10 == 0 for d in durs), sp)
                want = sum(durs) + (st["hold"] * st["ms"] if not st["loop"] else 0)
                self.assertEqual(total, want, gp)

    def test_icons(self):
        for name, path in REG["icons"].items():
            self.assertTrue(os.path.exists(os.path.join(V2, path)), name)
        pack = json.load(open(os.path.join(os.path.dirname(V2), "pack", "manifest.json"), encoding="utf-8"))
        for dom, (char, acc, _) in context2.DOMAINS.items():
            self.assertIn(acc, REG["icons"], dom)
            if char in context2.PACK_CHARS:
                # kostum berkanvas sendiri dari pack/ (Berserker Hero): harus ada di manifest pack dengan state inti arena
                self.assertIn(char, pack["cells"], dom)
                self.assertTrue({"idle", "attack-smash", "victory", "defeated"} <= set(pack["cells"][char]), dom)
            else:
                self.assertIn(char, CH, dom)


class Resolve(unittest.TestCase):
    def setUp(self):
        self.r = Resolver(REG, V2)

    def test_exact(self):
        got = self.r.resolve("knight-heavy", "guard")
        self.assertEqual((got["character"], got["state"], got["exact"]), ("knight-heavy", "guard", True))

    def test_core_alias(self):
        self.assertEqual(self.r.resolve("pirate-sharpshooter", "attack")["state"], "shoot")
        self.assertEqual(self.r.resolve("defeated", "idle")["state"], "sit")

    def test_missing_state_falls_to_idle(self):
        got = self.r.resolve("lawyer", "dance_99")
        self.assertEqual((got["character"], got["state"], got["exact"]), ("lawyer", "idle", False))

    def test_unknown_character_goes_to_root(self):
        got = self.r.resolve("pak-guru", "idle")
        self.assertEqual(got["character"], "normal-gblk")

    def test_missing_file_uses_fallback_character(self):
        r = Resolver(REG, V2, exists=lambda rel: not rel.startswith("sheets/knight-heavy/"))
        got = r.resolve("knight-heavy", "attack")
        self.assertEqual(got["character"], "fantasy-knight")
        self.assertFalse(got["exact"])

    def test_nothing_available_returns_none(self):
        r = Resolver(REG, V2, exists=lambda rel: False)
        self.assertIsNone(r.resolve("pak-haji", "idle"))

    def test_js_resolver_matches_python(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node tidak tersedia")
        cases = [("knight-heavy", "guard"), ("pirate-sharpshooter", "attack"), ("lawyer", "dance_99"), ("pak-guru", "idle"),
                 ("defeated", "idle"), ("referee", "attack")]
        js = ("const {Resolver}=require(%r);const reg=require(%r);const r=new Resolver(reg);"
              "console.log(JSON.stringify(%s.map(([c,s])=>{const x=r.resolve(c,s);return [x.character,x.state]})))"
              % (os.path.join(V2, "resolver2.js"), os.path.join(V2, "registry.json"), json.dumps(cases)))
        out = json.loads(subprocess.check_output([node, "-e", js]).decode())
        py = [[self.r.resolve(c, s)["character"], self.r.resolve(c, s)["state"]] for c, s in cases]
        self.assertEqual(out, py)


class Context(unittest.TestCase):
    EXPECT = [
        ("Apakah AI bisa punya kesadaran?", "philosopher", "laptop"),
        ("AI + matematika: bisakah LLM membuktikan teorema?", "mathematician", "laptop"),
        ("Hukum dan sejarah kolonial: warisan undang-undang", "lawyer", "oldscroll"),
        ("Apakah bunga bank haram menurut fikih?", "pak-haji", "calculator"),
        ("Apakah perang bisa dibenarkan?", "berserker-hero", None),
        ("Etika perang", "philosopher", "sword"),
        ("Apakah Alkitab mendukung hukuman mati?", "priest", None),
        ("Apakah Tuhan ada?", "philosopher", None),
        ("Apakah pajak kekayaan adil?", "economist", None),
        ("Kenapa kucing suka kotak?", "normal-gblk", None),
        ("Pembangkit listrik nuklir untuk Indonesia", "engineer", None),
        ("Apakah sihir dalam mitologi Jawa nyata?", "wizard", None),
        ("Bajak laut di Selat Malaka", "fantasy-pirate", None),
        ("Siapa pelaku korupsi terbesar?", "detective", None),
        ("Apakah sejarah ditulis pemenang?", "historian", None),
        ("Apakah ujian nasional perlu di sekolah?", "academic", None),
        ("Apakah vaksin aman? cek fakta hoaks", "skeptic", "flask"),
    ]

    def test_expected(self):
        for topic, char, acc in self.EXPECT:
            s = context2.select(topic)
            self.assertEqual((s["primary"], s["accessory"]), (char, acc), topic)

    def test_max_one_secondary(self):
        s = context2.select("AI etika hukum ekonomi sejarah matematika psikologi")
        self.assertIsInstance(s["primary"], str)
        self.assertTrue(s["accessory"] is None or isinstance(s["accessory"], str))
        self.assertNotIn("tertiary", s)

    def test_theology_parity(self):
        a, b = context2.DOMAINS["islam"], context2.DOMAINS["christianity"]
        self.assertEqual(a[1], b[1])
        for generic in ("Apakah agama perlu?", "Apakah Tuhan itu ada?", "teologi dan sains"):
            self.assertNotIn(context2.select(generic)["primary"], ("pak-haji", "priest"), generic)

    def test_word_boundary(self):
        self.assertEqual(context2.select("pantai dan santai")["primary"], "normal-gblk")

    def test_cast_for_fighters(self):
        out = context2.cast_for("Apakah AI bisa punya kesadaran?", ["argumen dari sudut ekonomi pasar", "argumen tanpa kata kunci"])
        self.assertEqual(out[0]["primary"], "economist")
        self.assertEqual(out[1]["primary"], "philosopher")

    def test_brief_section_60_examples(self):
        cases = [("AI dan filsafat: apakah mesin punya kesadaran?", "philosopher", "laptop"),
                 ("AI dan matematika: pembuktian teorema otomatis", "mathematician", "laptop"),
                 ("Pendidikan dan teknologi di sekolah", "academic", "laptop"),
                 ("Hukum dan sejarah: undang-undang kolonial", "lawyer", "oldscroll")]
        for topic, char, acc in cases:
            s = context2.select(topic)
            self.assertEqual((s["primary"], s["accessory"]), (char, acc), topic)

    def test_technology_alone_is_hacker(self):
        self.assertEqual(context2.select("Bagaimana algoritma enkripsi bekerja?")["primary"], "hacker")

    def test_alt_swaps_roles(self):
        s = context2.select("Apakah AI bisa punya kesadaran?")
        self.assertEqual((s["alt"], s["alt_accessory"]), ("hacker", "scroll"))
        self.assertIsNone(context2.select("Kenapa kucing suka kotak?")["alt"])

    def test_tournament_words_are_not_keywords(self):
        for w in ("argumen", "premis", "klaim", "argument", "premise", "claim", "battle", "petarung", "fighter"):
            self.assertEqual(context2.select("Argumen contoh: " + w)["primary"], "normal-gblk", w)

    def test_roles_are_registered(self):
        for role, cid in context2.ROLES.items():
            self.assertIn(cid, CH, role)


class Visual(unittest.TestCase):
    """Uji siluet, grayscale, baseline, identitas, dan seam pada sheet hasil ekspor."""

    def idle(self, cid):
        return frames(cid, CH[cid]["core"].get("idle", "idle"))

    def test_faction_silhouettes_distinct(self):
        for fac in ("knights", "vikings", "pirates"):
            ids = [c for c in CH if CH[c]["faction"] == fac]
            ms = {c: mask(self.idle(c)[0]) for c in ids}
            for a, b in itertools.combinations(ids, 2):
                self.assertLessEqual(iou(ms[a], ms[b]), 0.80, "%s vs %s" % (a, b))

    def test_brief_pairs_section_54(self):
        for a, b in (("knight-heavy", "viking-huscarl"), ("pirate-captain", "pirate-sharpshooter"), ("scientist", "academic")):
            fa, fb = self.idle(a)[0], self.idle(b)[0]
            self.assertLessEqual(iou(mask(fa), mask(fb)), 0.80, (a, b))
            ga, gb = fa.convert("LA").tobytes(), fb.convert("LA").tobytes()
            diff = sum(1 for k in range(0, len(ga), 2) if abs(ga[k] - gb[k]) > 24 or ga[k + 1] != gb[k + 1])
            self.assertGreater(diff, 300, (a, b))

    def test_nothing_below_floor_and_idle_on_baseline(self):
        for cid, c in CH.items():
            idle = c["core"].get("idle", "idle")
            base = base_of(cid)
            for s in c["states"]:
                for i, fr in enumerate(frames(cid, s)):
                    m = mask(fr)
                    if not m:
                        continue
                    low = max(y for _, y in m)
                    self.assertLessEqual(low, base - 1, "%s/%s f%d" % (cid, s, i))
                    if s == idle:
                        self.assertEqual(low, base - 1, "%s/%s f%d" % (cid, s, i))

    def test_gobyet_face_visible(self):
        for cid, c in CH.items():
            for s in c["states"]:
                if (cid, s) in NO_FACE_OK:
                    continue
                for i, fr in enumerate(frames(cid, s)):
                    px = fr.load()
                    n = sum(1 for y in range(fr.size[1]) for x in range(fr.size[0]) if px[x, y][3] and px[x, y][:3] in FACE)
                    self.assertGreaterEqual(n, 25, "%s/%s f%d wajah %d px" % (cid, s, i, n))

    def test_loop_seams(self):
        for cid, c in CH.items():
            for s, st in c["states"].items():
                if not st["loop"]:
                    continue
                raw = [f.tobytes() for f in frames(cid, s)]
                fr = [[b[k:k + 4] for k in range(0, len(b), 4)] for b in raw]
                steps = [sum(1 for a, b in zip(fr[k], fr[(k + 1) % len(fr)]) if a != b) for k in range(len(fr))]
                self.assertLessEqual(steps[-1], 1.25 * max(steps[:-1]) + 1, "%s/%s seam %s" % (cid, s, steps))


class Berserker(unittest.TestCase):
    """Berserker pedang raksasa: kanvas sendiri, lapisan, kerusakan, tempo, event, VFX, darah hanya VFX."""
    CID = "berserker"

    def setUp(self):
        self.c = CH[self.CID]

    def test_canvas_and_anchor(self):
        self.assertEqual((self.c["canvas"]["w"], self.c["canvas"]["h"]), (144, 100))
        # badan Gobyet tetap di koordinat rig yang sama: jangkar kaki = (RX, BASE) digeser offset kanvas
        self.assertEqual((self.c["anchor"]["x"], self.c["anchor"]["baseline"]), (56, 95))

    def test_same_head_as_everyone(self):
        import berserker
        import char2
        self.assertIs(berserker.Berserker.head, char2.Char.head)
        self.assertIs(berserker.Berserker.draw_tail, char2.Char.draw_tail)

    def test_brief_aliases_resolve(self):
        r = Resolver(REG, V2)
        for brief, st in self.c["aliases"].items():
            self.assertTrue(brief.startswith("berserker_"), brief)
            self.assertEqual(r.resolve(self.CID, brief)["state"], st, brief)

    def _stack(self, cid, layers, n):
        parts = [strip(cid, layers[k], n) for k in ("body", "weapon", "vfx")]
        out = []
        for i in range(n):
            im = parts[0][i].copy()
            im.alpha_composite(parts[1][i])
            im.alpha_composite(parts[2][i])
            out.append(im)
        return out

    def test_layers_stack_to_composite(self):
        for s, st in self.c["states"].items():
            levels = [(st["sheet"], st["layers"])] + [(d["sheet"], d["layers"]) for d in st["damage"].values()]
            for sheet, layers in levels:
                for k in ("body", "weapon", "vfx"):
                    self.assertTrue(os.path.exists(os.path.join(V2, layers[k])), layers[k])
                comp = strip(self.CID, sheet, st["frames"])
                stack = self._stack(self.CID, layers, st["frames"])
                for i in range(st["frames"]):
                    self.assertEqual(comp[i].tobytes(), stack[i].tobytes(), "%s f%d" % (sheet, i))

    def test_layers_are_separate(self):
        st = self.c["states"]["leap_spin_slash"]
        body = strip(self.CID, st["layers"]["body"], st["frames"])
        weapon = strip(self.CID, st["layers"]["weapon"], st["frames"])
        vfx = strip(self.CID, st["layers"]["vfx"], st["frames"])
        self.assertTrue(all(mask(f) for f in body))
        self.assertGreater(sum(len(mask(f)) for f in weapon), 1000)
        self.assertGreater(len(mask(vfx[15])), 200)  # frame hantaman punya VFX besar
        self.assertEqual(len(mask(vfx[0])), 0)  # idle awal tanpa VFX
        for f in body:  # lapisan karakter tidak berisi piksel pedang (warna bilah sw1)
            cols = {c[1][:3] for c in f.getcolors(1 << 16) if c[1][3]}
            self.assertNotIn((106, 106, 112), cols)

    def test_damage_levels(self):
        self.assertEqual(self.c["damage_levels"], ["normal", "damaged", "heavily_damaged"])
        st = self.c["states"]["idle"]
        n = strip(self.CID, st["sheet"], 1)[0].tobytes()
        d1 = strip(self.CID, st["damage"]["damaged"]["sheet"], 1)[0].tobytes()
        d2 = strip(self.CID, st["damage"]["heavily_damaged"]["sheet"], 1)[0].tobytes()
        self.assertTrue(n != d1 != d2 and n != d2)
        r = Resolver(REG, V2)
        self.assertEqual(r.resolve(self.CID, "attack", damage="damaged")["sheet"], self.c["states"]["attack"]["damage"]["damaged"]["sheet"])
        self.assertEqual(r.resolve("knight-heavy", "attack", damage="damaged")["sheet"], CH["knight-heavy"]["states"]["attack"]["sheet"])

    def test_sword_length_vs_body(self):
        """Pedang 1.2-1.5x tinggi badan berdiri. Panjang pedang dari lapisan senjata idle f0 (pedang utuh terlihat);
        tinggi badan berdiri = tinggi terbesar lapisan karakter di state victory (berdiri tegak, crouch 0)."""
        st = self.c["states"]["idle"]
        weapon = mask(strip(self.CID, st["layers"]["weapon"], 1)[0])
        pts = sorted(weapon)
        far = max(((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5 for a in (pts[0], pts[-1]) for b in pts)
        v = self.c["states"]["victory"]
        h = 0
        for f in strip(self.CID, v["layers"]["body"], v["frames"]):
            m = mask(f)
            h = max(h, max(y for _, y in m) - min(y for _, y in m) + 1)
        self.assertGreaterEqual(far / h, 1.2, (far, h))
        self.assertLessEqual(far / h, 1.5, (far, h))

    def test_signature_timing_and_events(self):
        st = self.c["states"]["leap_spin_slash"]
        self.assertEqual(st["frames"], 23)
        d = st["durations"]
        phases = [e for e in st["events"] if e["type"] == "phase"][0]["phases"]
        self.assertEqual(phases, {"anticipation": [0, 3], "charge": [4, 6], "jump": [7, 10], "spin": [11, 14],
                                  "impact": [15, 15], "aftermath": [16, 18], "recovery": [19, 22]})
        self.assertGreater(min(d[0:4]), max(d[7:11]))  # ancang-ancang lambat, lepas cepat
        self.assertLess(max(d[11:15]), min(d[7:11]) + 1)  # putaran paling cepat
        self.assertEqual(max(d[11:19]), d[15])  # frame hantam ditahan
        types = {(e["frame"], e["type"]) for e in st["events"]}
        self.assertTrue({(15, "hit"), (15, "hitstop"), (15, "screen_shake")} <= types)

    def test_hit_events_use_registered_blood(self):
        w, h = size_of(self.CID)
        ax, base = self.c["anchor"]["x"], self.c["anchor"]["baseline"]
        n_hit = 0
        for s, st in self.c["states"].items():
            for e in st.get("events", []):
                self.assertLess(e["frame"], st["frames"], (s, e))
                if e["type"] != "hit":
                    continue
                n_hit += 1
                self.assertTrue(0 <= ax + e["x"] < w and 0 <= base + e["y"] < h, (s, e))
                for lvl, name in e["blood"].items():
                    self.assertIn(name, REG["vfx"], (s, name))
                    self.assertEqual(REG["vfx"][name]["kind"], "blood")
        self.assertGreaterEqual(n_hit, 8)
        for s in ("idle", "ready", "run", "hit", "miss", "exhausted", "victory", "defeat", "rage"):
            self.assertFalse([e for e in self.c["states"][s].get("events", []) if e["type"] == "hit"], s)

    def test_vfx_sprites(self):
        need = ["slash_arc", "sword_trail", "dust", "impact", "debris", "spark", "ground_impact", "blood_small",
                "blood_medium", "blood_burst", "blood_ground", "blood_arc", "blood_particles", "screen_shake_trigger"]
        for name in need:
            self.assertIn(name, REG["vfx"], name)
            v = REG["vfx"][name]
            if v["kind"] == "event":
                continue
            with Image.open(os.path.join(V2, v["sheet"])) as im:
                self.assertEqual(im.size, (v["canvas"]["w"] * v["frames"], v["canvas"]["h"]), name)
            self.assertTrue(os.path.exists(os.path.join(V2, v["gif"])), name)
            self.assertEqual(len(v["durations"]), v["frames"])
        for lvl in ("1", "2", "3"):
            for name in REG["blood"]["levels"][lvl]:
                self.assertEqual(REG["vfx"][name]["kind"], "blood")
        self.assertEqual(REG["blood"]["levels"]["0"], [])

    def test_blood_never_in_character_sheets(self):
        for cid, c in CH.items():
            for s, st in c["states"].items():
                sheets = [st["sheet"]] + list(st.get("layers", {}).values())
                for d in st.get("damage", {}).values():
                    sheets += [d["sheet"]] + list(d["layers"].values())
                for rel in set(sheets):
                    with Image.open(os.path.join(V2, rel)) as im:
                        cols = {c[1][:3] for c in im.convert("RGBA").getcolors(1 << 16) if c[1][3]}
                    self.assertFalse(cols & BLOOD, rel)

    def test_blood_vfx_is_small_and_brief(self):
        for name, v in REG["vfx"].items():
            if v.get("kind") != "blood":
                continue
            self.assertLessEqual(v["frames"], 6, name)
            self.assertLessEqual(sum(v["durations"]), 520, name)
            for k, f in enumerate(strip_vfx(v)):
                self.assertLessEqual(len(mask(f)), 160, (name, k))

    def test_variants_deterministic(self):
        r = Resolver(REG, V2)
        v = self.c["variants"]
        self.assertEqual(v["idle"], ["idle", "idle_breath", "idle_grip", "idle_drag", "idle_look", "idle_twitch"])
        self.assertIn("attack_b", v["attack"])
        picks = [r.variant(self.CID, "idle", seed) for seed in range(40)]
        self.assertEqual(picks, [r.variant(self.CID, "idle", seed) for seed in range(40)])
        self.assertGreaterEqual(len(set(picks)), 4)
        self.assertEqual(r.variant(self.CID, "idle"), "idle")
        node = shutil.which("node")
        if node:
            js = ("const {Resolver}=require(%r);const reg=require(%r);const r=new Resolver(reg);"
                  "console.log(JSON.stringify([...Array(40).keys()].map(s=>r.variant('berserker','idle',s))))"
                  % (os.path.join(V2, "resolver2.js"), os.path.join(V2, "registry.json")))
            self.assertEqual(json.loads(subprocess.check_output([node, "-e", js]).decode()), picks)


def strip_vfx(v):
    w, h = v["canvas"]["w"], v["canvas"]["h"]
    with Image.open(os.path.join(V2, v["sheet"])) as src:
        im = src.convert("RGBA")
    return [im.crop((i * w, 0, (i + 1) * w, h)) for i in range(v["frames"])]


class TheologyParity(unittest.TestCase):
    def test_parallel_states(self):
        a, b = CH["pak-haji"]["states"], CH["priest"]["states"]
        self.assertEqual(len(a), len(b))
        common = {"idle", "read", "think", "present", "calm", "hit", "victory", "defeat"}
        self.assertTrue(common <= set(a) and common <= set(b))
        for s in common:
            self.assertEqual((a[s]["frames"], a[s]["ms"]), (b[s]["frames"], b[s]["ms"]), s)

    def test_same_aura_code(self):
        import domain
        self.assertIs(domain.PakHaji.front, domain.Priest.front)


if __name__ == "__main__":
    unittest.main()
