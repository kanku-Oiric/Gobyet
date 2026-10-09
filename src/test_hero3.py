"""Uji rig Berserker Hero v3 (zirah bukan Gobyet; wajah monyet Gobyet hanya di balik topeng): kanvas dan tepi, identitas, palet, sisi elemen
asimetris, visor salib, ekspresi, perisai naga, tepi terang, darah monster merah, pedang, dan bahwa hero v1 tidak berubah.

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

GOBYET_COLOR_KEYS = {"fs", "fb", "fl", "ei", "cs", "cb", "cl", "ra", "rb", "ew", "mo"}          # kunci Gobyet hero v1/v2: tidak dipakai v3 sama sekali
GOBYET_PARTS = {"face", "eye", "ear", "mouth", "brow", "skull", "neck", "helm_cap", "tail"}      # nama bagian rig Gobyet v1/v2
FACE_KEYS = set(hero3.GOBYET_FACE_KEYS)                                                          # bulu, wajah, mulut Gobyet di balik topeng


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

    def test_no_gobyet_base_and_face_hidden_when_mask_closed(self):
        """Basis bukan Gobyet: dengan topeng tertutup tidak ada warna atau bagian Gobyet sama sekali (v1/v2 maupun wajah di balik topeng)."""
        for name, p in self.poses.items():
            cv = hero3.render_pose(dict(p, fx=()))
            self.assertFalse(set(cv.px.values()) & (GOBYET_COLOR_KEYS | FACE_KEYS), name)
            self.assertFalse({o for o in cv.owner.values()} & (GOBYET_PARTS | {"gobyet_face", "gobyet_eye"}), name)
        for style in hero3.EYE_STYLES:
            cv = hero3.PartCanvas()
            hero3.helm3(cv, 40, 40, style, "closed")
            self.assertFalse(set(cv.px.values()) & (GOBYET_COLOR_KEYS | FACE_KEYS), style)

    def test_palette_within_limit_and_registered(self):
        keys = set()
        for p in self.poses.values():
            keys |= set(hero3.render_pose(dict(p, fx=())).px.values())
        self.assertLessEqual(len(keys), 28)
        self.assertEqual(len(keys), 11)                                   # tepat 11 kunci hero3 tanpa efek (tepi terang memakai n4; efek: batu, kayu, darah)
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
        self.assertGreaterEqual(max(ys) - min(ys) + 1, 9)                # batang tegak salib (bagian atasnya tertutup garis V)
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

    def test_closed_face_is_mirror_symmetric_about_the_helm_axis(self):
        """Visor salib, grill, dan garis V tepat simetris terhadap sumbu helm (batas kolom hx-1 dan hx); cahaya dari kiri atas hanya menggeser nada cakram telinga."""
        hx, hy = 60, 40
        for eyes in hero3.EYE_STYLES:
            for mouth in ("closed", "shout"):
                cv = hero3.PartCanvas()
                hero3.helm3(cv, hx, hy, eyes, mouth)
                for part in ("visor", "grill", "brow_band"):
                    for (x, y), o in cv.owner.items():
                        if o == part:
                            self.assertEqual(cv.px.get((2 * hx - 1 - x, y)), cv.px[(x, y)], (eyes, mouth, part, x, y))

    def test_mask_opens_monotonically_onto_the_gobyet_monkey_face(self):
        sizes = []
        for m in (0.0, 0.125, 0.25, 0.5, 0.75, 1.0):
            cv = hero3.PartCanvas()
            hero3.helm3(cv, 60, 40, "look", "closed", 0.0, m)
            sizes.append(sum(1 for o in cv.owner.values() if o in ("cavity", "gobyet_face", "gobyet_eye")))
            self.assertFalse(set(cv.px.values()) & GOBYET_COLOR_KEYS, m)                 # kunci v1/v2 tidak pernah dipakai
            face = {c for k, c in cv.px.items() if cv.owner.get(k) in ("gobyet_face", "gobyet_eye")}
            stray = {c for k, c in cv.px.items() if c in FACE_KEYS and cv.owner.get(k) not in ("gobyet_face", "gobyet_eye")}
            self.assertFalse(stray, m)                                                  # warna Gobyet hanya di wajah
            if m >= 0.5:                                   # terbuka lebar: bulu cokelat, wajah krem, dan dua mata Gobyet terlihat
                self.assertGreaterEqual(sum(1 for o in cv.owner.values() if o == "gobyet_eye"), 12, m)
                self.assertTrue({"B", "F"} <= face, (m, face))
        self.assertEqual(sizes[0], 0)
        self.assertEqual(sizes, sorted(sizes))
        self.assertGreaterEqual(sizes[-1], 300)

    def test_dragon_shield_is_big_and_has_dragon_features(self):
        cv = hero3.render_pose(dict(self.poses["idle"], fx=()))
        cnt = {}
        for o in cv.owner.values():
            cnt[o] = cnt.get(o, 0) + 1
        shield = sum(cnt.get(k, 0) for k in ("pauldron_big", "horn_fin", "dragon_horn", "dragon_eye", "dragon_brow", "dragon_scale", "dragon_glow"))
        self.assertGreaterEqual(shield, 1100)                                           # perisai diperbesar atas permintaan pemilik
        for k, lo in (("dragon_eye", 60), ("dragon_horn", 30), ("dragon_scale", 60), ("horn_fin", 200)):
            self.assertGreaterEqual(cnt.get(k, 0), lo, k)                              # mata celah, tanduk, sisik, sayap naga
        pts = [k for k, o in cv.owner.items() if o in ("pauldron_big", "horn_fin")]
        ys = [y for _, y in pts]
        xs = [x for x, _ in pts]
        self.assertGreaterEqual(max(ys) - min(ys) + 1, 60)                             # perisai tinggi (dari ujung tombak ke ujung bawah)
        self.assertGreaterEqual(max(xs) - min(xs) + 1, 30)
        eye = [k for k, o in cv.owner.items() if o == "dragon_eye"]
        slit = [k for k in eye if cv.px[k] == "n0"]
        self.assertGreaterEqual(len(slit), 8)                                           # pupil celah tegak

    def test_every_dark_edge_has_a_light_edge(self):
        for name, p in self.poses.items():
            cv = hero3.render_pose(p)
            unlit = 0
            for (x, y), c in cv.px.items():
                if c in hero3.RIM_DARK and cv.owner.get((x, y)) not in hero3.RIM_SKIP:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        k = (x + dx, y + dy)
                        if k not in cv.px and 0 <= k[0] < cv.w and 0 <= k[1] < hero3.FLOOR:
                            unlit += 1
            self.assertEqual(unlit, 0, name)
            self.assertTrue(all(cv.px[k] == hero3.RIM_COLOR for k, o in cv.owner.items() if o == "rim" and k in cv.px), name)

    def test_monster_blood_is_red(self):
        for k in ("m1", "m2", "m3"):
            r, g, b = monkey.PAL_HERO[k]
            self.assertGreater(r, 2 * max(g, b), k)                                     # merah, bukan hijau atau ungu

    def test_stain_is_wiped_progressively_from_the_guard_toward_the_tip(self):
        counts = []
        for u in (0, 8, 17, 30, 60):
            cv = hero3.PartCanvas()
            hero3.sword3(cv, hero3.SwordFrame(82, 48, 88.0), 1, u)
            counts.append(sum(1 for o in cv.owner.values() if o == "ichor"))
        self.assertGreaterEqual(counts[0], 150)
        self.assertEqual(counts[-1], 0)
        self.assertEqual(counts[1:], sorted(counts[1:], reverse=True))
        cv = hero3.PartCanvas()
        hero3.sword3(cv, hero3.SwordFrame(82, 48, 88.0), 1, None)                # tanpa noda: tidak ada piksel darah monster
        self.assertEqual(sum(1 for o in cv.owner.values() if o == "ichor"), 0)

    def test_feet_never_detach_from_the_hips(self):
        for name, p in self.poses.items():
            g = hero3.geometry(p)
            for hip, foot in (("hip_l", "foot_l"), ("hip_r", "foot_r")):
                d = ((g[hip][0] - g[foot][0]) ** 2 + (g[hip][1] - g[foot][1]) ** 2) ** 0.5
                self.assertLessEqual(d, hero3.THIGH + hero3.SHIN, (name, hip, d))

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
