"""Uji rig Berserker Hero v2 (Fase Body): kanvas, keterlihatan wajah dan telinga, palet, sisi elemen asimetris, dan bahwa hero v1 tidak berubah.

    python3 -m unittest src/test_hero2.py -v
"""
import hashlib
import os
import sys
import unittest
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import hero  # noqa: E402
import hero2  # noqa: E402
import monkey  # noqa: E402

FACE_PARTS = ("face", "eye", "mouth", "ear")


def px_hash(cv):
    return hashlib.sha256(cv.image(1).tobytes()).hexdigest()[:8]


class Hero2Body(unittest.TestCase):
    def setUp(self):
        self.poses = {n: f() for n, f in hero2.KEYPOSES.items()}

    def test_three_key_poses_exist(self):
        self.assertEqual(sorted(hero2.KEYPOSES), ["attack-smash", "idle", "run"])

    def test_canvas_floor_and_edges(self):
        for name, p in self.poses.items():
            cv = hero2.render_pose(p)
            self.assertEqual((cv.w, cv.h), (128, 96))
            self.assertFalse([k for k in cv.px if k[1] >= hero2.FLOOR], name)
            ys = [y for _, y in cv.px]
            self.assertGreaterEqual(min(ys), 1, name)                     # jambul tidak terpotong di tepi atas
            xs = [x for x, _ in cv.px]
            self.assertGreaterEqual(min(xs), 1, name)                     # ekor tidak terpotong di tepi kiri
            self.assertLessEqual(max(xs), cv.w - 2, name)                 # bilah, balok, dan busur tidak terpotong di tepi kanan

    def test_face_and_ears_fully_visible_in_every_key_pose(self):
        for name, p in self.poses.items():
            cv = hero2.render_pose(p)
            full, ref = Counter(cv.owner.values()), Counter(hero2.head_only(p).owner.values())
            for part in FACE_PARTS:
                self.assertEqual(full.get(part, 0), ref.get(part, 0), (name, part))
                self.assertGreater(ref.get(part, 0), 0, (name, part))

    def test_palette_within_limit_and_registered(self):
        used = set()
        for p in self.poses.values():
            used |= set(hero2.render_pose(dict(p, fx=())).px.values())
        self.assertLessEqual(len(used), 28, sorted(used))
        for k in used:
            monkey.rgb(k)                                                # semua kunci terdaftar (PAL, PAL_EXT, atau PAL_HERO)
        self.assertFalse(set(hero2.HERO2_PAL) & (set(monkey.PAL) | set(monkey.PAL_EXT) | set(hero.HERO_PAL)))

    def test_no_partial_alpha_or_text(self):
        cv = hero2.render_pose(self.poses["idle"])
        self.assertTrue(all(len(c) <= 2 for c in cv.px.values()))
        alphas = {a for (_, _, _, a) in cv.image(1).getdata()}
        self.assertEqual(alphas, {0, 255})

    def test_asymmetric_elements_keep_their_sides(self):
        side = {"pauldron_big": -1, "horn_fin": None, "pauldron_small": +1, "tail_arrow": -1, "crest": None}
        for name, p in self.poses.items():
            cv = hero2.render_pose(dict(p, fx=()))
            tcx = hero2.geometry(p)["tcx"]
            for part, want in side.items():
                pts = [k for k, o in cv.owner.items() if o == part]
                self.assertTrue(pts, (name, part))
                if want:
                    dx = sum(x + 0.5 for x, _ in pts) / len(pts) - tcx
                    self.assertGreater(dx * want, 0, (name, part, dx))

    def test_weapon_is_marked_placeholder(self):
        self.assertIn("BUKAN desain akhir", hero2.weapon_placeholder.__doc__)

    def test_v1_hero_key_poses_unchanged(self):
        want = {"idle": "11974b75", "run": "08796a4b", "attack-smash": "76ba21ad"}          # hash piksel pose kunci Fase B
        for name, fn in hero.KEYPOSES.items():
            self.assertEqual(px_hash(hero.render_pose(fn())), want[name], name)


if __name__ == "__main__":
    unittest.main()
