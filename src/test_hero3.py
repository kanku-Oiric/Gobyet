"""Uji rig Berserker Hero v3 (tanpa basis Gobyet): kanvas dan tepi, tidak ada unsur Gobyet, palet, sisi elemen asimetris, visor salib, ekspresi,
pedang, dan bahwa hero v1 tidak berubah.

    python3 -m unittest src/test_hero3.py -v
"""
import hashlib
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import hero  # noqa: E402
import hero3  # noqa: E402
import monkey  # noqa: E402

GOBYET_COLOR_KEYS = {"fs", "fb", "fl", "ei", "cs", "cb", "cl", "ra", "rb", "ew", "mo"}          # bulu, telinga, wajah, mata, hidung dan mulut Gobyet
GOBYET_PARTS = {"face", "eye", "ear", "mouth", "brow", "skull", "neck", "helm_cap", "tail"}      # nama bagian rig Gobyet v1/v2


def px_hash(cv):
    return hashlib.sha256(cv.image(1).tobytes()).hexdigest()[:8]


class Hero3Model(unittest.TestCase):
    def setUp(self):
        self.poses = {n: f() for n, f in hero3.KEYPOSES.items()}

    def test_three_key_poses_exist(self):
        self.assertEqual(sorted(hero3.KEYPOSES), ["attack-smash", "idle", "run"])

    def test_canvas_floor_and_edges(self):
        for name, p in self.poses.items():
            cv = hero3.render_pose(p)
            self.assertEqual((cv.w, cv.h), (128, 96))
            self.assertFalse([k for k in cv.px if k[1] >= hero3.FLOOR], name)
            xs = [x for x, _ in cv.px]
            ys = [y for _, y in cv.px]
            self.assertGreaterEqual(min(ys), 1, name)                     # jambul tidak terpotong di tepi atas
            self.assertGreaterEqual(min(xs), 1, name)                     # ekor panah tidak terpotong di tepi kiri
            self.assertLessEqual(max(xs), cv.w - 2, name)                 # pedang, balok, debu tidak terpotong di tepi kanan

    def test_no_gobyet_base(self):
        """Basis bukan Gobyet: tanpa warna bulu/wajah/mata Gobyet dan tanpa bagian wajah, telinga, atau mulut Gobyet (efek balok kayu dikecualikan)."""
        for name, p in self.poses.items():
            cv = hero3.render_pose(dict(p, fx=()))
            self.assertFalse(set(cv.px.values()) & GOBYET_COLOR_KEYS, name)
            self.assertFalse({o for o in cv.owner.values()} & GOBYET_PARTS, name)
        for style in hero3.EYE_STYLES:
            cv = hero3.PartCanvas()
            hero3.helm3(cv, 40, 40, style, "closed")
            self.assertFalse(set(cv.px.values()) & GOBYET_COLOR_KEYS, style)

    def test_palette_within_limit_and_registered(self):
        keys = set()
        for p in self.poses.values():
            keys |= set(hero3.render_pose(dict(p, fx=())).px.values())
        self.assertLessEqual(len(keys), 28)
        self.assertEqual(len(keys), 11)                                   # tepat 11 kunci hero3 tanpa efek
        for k in keys:
            self.assertIn(k, monkey.PAL_HERO)
        self.assertTrue(set(hero3.HERO3_PAL) <= set(monkey.PAL_HERO))

    def test_no_partial_alpha_or_text(self):
        for name, p in self.poses.items():
            cv = hero3.render_pose(p)
            alphas = {a for (_, _, _, a) in cv.image(1).getdata()}
            self.assertEqual(alphas, {0, 255})

    def test_asymmetric_elements_keep_their_sides(self):
        side = {"pauldron_big": -1, "horn_fin": None, "pauldron_small": +1, "tail_arrow": -1, "crest": None}
        for name, p in self.poses.items():
            cv = hero3.render_pose(dict(p, fx=()))
            tcx = hero3.geometry(p)["tcx"]
            for part, want in side.items():
                pts = [k for k, o in cv.owner.items() if o == part]
                self.assertTrue(pts, (name, part))
                if want:
                    dx = sum(x + 0.5 for x, _ in pts) / len(pts) - tcx
                    self.assertGreater(dx * want, 0, (name, part, dx))

    def test_cross_visor_present_and_changes_with_expression(self):
        cv = hero3.PartCanvas()
        hero3.helm3(cv, 40, 40, "look", "closed")
        vis = [k for k, o in cv.owner.items() if o == "visor"]
        xs = [x for x, _ in vis]
        ys = [y for _, y in vis]
        self.assertGreaterEqual(max(xs) - min(xs) + 1, 15)               # lengan datar salib
        self.assertGreaterEqual(max(ys) - min(ys) + 1, 11)               # batang tegak salib
        base = {k: cv.px[k] for k in vis}
        seen = {}
        for style in hero3.EYE_STYLES:
            c2 = hero3.PartCanvas()
            hero3.helm3(c2, 40, 40, style, "closed")
            seen[style] = {k: v for k, v in c2.px.items() if c2.owner.get(k) == "visor"}
        self.assertEqual(len({tuple(sorted(v.items())) for v in seen.values()}), len(hero3.EYE_STYLES))   # tiap ekspresi tampil berbeda
        c3 = hero3.PartCanvas()
        hero3.helm3(c3, 40, 40, "x", "closed")
        self.assertTrue([k for k, o in c3.owner.items() if o == "visor"])
        self.assertNotEqual({k: c3.px[k] for k in c3.px if c3.owner.get(k) == "visor"}, base)

    def test_sword_is_black_core_with_red_flame(self):
        for name, p in self.poses.items():
            cv = hero3.render_pose(dict(p, fx=()))
            cols = [c for k, c in cv.px.items() if cv.owner.get(k) == "weapon"]
            self.assertGreaterEqual(len(cols), 300, name)
            reds = sum(1 for c in cols if c in ("q2", "q3", "q4"))
            blacks = sum(1 for c in cols if c in ("n1", "n2", "n3"))
            self.assertGreater(reds, 80, name)                            # tepi api merah
            self.assertGreater(blacks, 60, name)                          # inti hitam

    def test_v1_hero_key_poses_unchanged(self):
        want = {"idle": "11974b75", "run": "08796a4b", "attack-smash": "76ba21ad"}          # hash piksel pose kunci Fase B
        for name, fn in hero.KEYPOSES.items():
            self.assertEqual(px_hash(hero.render_pose(fn())), want[name], name)


if __name__ == "__main__":
    unittest.main()
