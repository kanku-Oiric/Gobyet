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

with open(os.path.join(V2, "registry.json")) as f:
    REG = json.load(f)
CH = {c["id"]: c for c in REG["characters"]}

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
}
FIGHTER_CATS = ("fantasy", "domain", "special")
# frame tanpa wajah yang disengaja: hilang di balik asap, berjalan keluar/masuk tepi kanvas
NO_FACE_OK = {("knight-assassin", "disappear"), ("knight-assassin", "defeat"), ("defeated", "leave"), ("referee", "enter"),
              ("referee", "exit")}
_FRAMES = {}


def frames(cid, state):
    key = (cid, state)
    if key not in _FRAMES:
        st = CH[cid]["states"][state]
        with Image.open(os.path.join(V2, st["sheet"])) as src:
            im = src.convert("RGBA")
        _FRAMES[key] = [im.crop((i * W, 0, (i + 1) * W, H)) for i in range(st["frames"])]
    return _FRAMES[key]


def mask(im):
    a = im.split()[3].load()
    return {(x, y) for y in range(H) for x in range(W) if a[x, y]}


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
                with Image.open(sp) as im:
                    self.assertEqual(im.size, (W * st["frames"], H), sp)
                    alphas = set(im.convert("RGBA").split()[3].tobytes())
                self.assertTrue(alphas <= {0, 255}, sp)
                with Image.open(gp) as g:
                    self.assertEqual(g.size, (W * REG["gif_scale"], H * REG["gif_scale"]), gp)
                    total = 0
                    for k in range(getattr(g, "n_frames", 1)):
                        g.seek(k)
                        total += g.info.get("duration", 0)
                # Pillow menggabungkan frame identik berurutan; yang dijaga adalah total durasi animasi.
                want = st["ms"] * st["frames"] + (st["hold"] * st["ms"] if not st["loop"] else 0)
                self.assertEqual(total, want, gp)

    def test_icons(self):
        for name, path in REG["icons"].items():
            self.assertTrue(os.path.exists(os.path.join(V2, path)), name)
        for dom, (char, acc, _) in context2.DOMAINS.items():
            self.assertIn(acc, REG["icons"], dom)
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
            for s in c["states"]:
                for i, fr in enumerate(frames(cid, s)):
                    m = mask(fr)
                    if not m:
                        continue
                    low = max(y for _, y in m)
                    self.assertLessEqual(low, BASE - 1, "%s/%s f%d" % (cid, s, i))
                    if s == idle:
                        self.assertEqual(low, BASE - 1, "%s/%s f%d" % (cid, s, i))

    def test_gobyet_face_visible(self):
        for cid, c in CH.items():
            for s in c["states"]:
                if (cid, s) in NO_FACE_OK:
                    continue
                for i, fr in enumerate(frames(cid, s)):
                    px = fr.load()
                    n = sum(1 for y in range(H) for x in range(W) if px[x, y][3] and px[x, y][:3] in FACE)
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
