"""Test untuk audit teks V8 di validate_pack.py (pustaka standar unittest).

    python3 -m unittest src/test_validate_pack.py -v

Membuktikan bahwa instrumentasi menangkap semua pemanggil mini_text: lewat monkey.mini_text, impor
langsung (from monkey import mini_text), dan alias (from monkey import mini_text as tulis).
"""
import os
import sys
import types
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import monkey  # noqa: E402
import validate_pack as vp  # noqa: E402


def fake_module(name, source):
    mod = types.ModuleType(name)
    sys.modules[name] = mod
    exec(source, mod.__dict__)
    return mod


class TextAudit(unittest.TestCase):
    def audit(self, scene_name, fn, n=2):
        rows = vp.instrumented(fn, n, lambda i: 100)
        return rows, vp.text_violations(scene_name, rows)

    def test_alias_import_with_glyph_outside_mini(self):
        mod = fake_module("uji_alias", (
            "from monkey import Canvas, mini_text as tulis\n"
            "def frame(i):\n"
            "    cv = Canvas()\n"
            "    tulis(cv, 'Z', 1, 1, 'K')\n"
            "    return cv\n"))
        rows, bad = self.audit("uji-alias", mod.frame)
        self.assertEqual([t[0] for t in rows[0][5]], ["Z"])
        self.assertTrue(any("di luar MINI" in b for b in bad), bad)

    def test_direct_import_too_long(self):
        mod = fake_module("uji_langsung", (
            "from monkey import Canvas, mini_text\n"
            "def frame(i):\n"
            "    cv = Canvas()\n"
            "    mini_text(cv, '!!!!', 1, 1, 'K')\n"
            "    return cv\n"))
        _, bad = self.audit("uji-langsung", mod.frame)
        self.assertTrue(any("lebih dari 3" in b for b in bad), bad)

    def test_module_attribute_call(self):
        mod = fake_module("uji_modul", (
            "import monkey\n"
            "def frame(i):\n"
            "    cv = monkey.Canvas()\n"
            "    monkey.mini_text(cv, '?', 1, 1, 'K')\n"
            "    return cv\n"))
        rows, bad = self.audit("uji-modul", mod.frame)
        self.assertEqual([t[0] for t in rows[1][5]], ["?"])
        self.assertEqual(bad, [])

    def test_exception_only_for_its_owner_and_static(self):
        mod = fake_module("uji_papan", (
            "from monkey import Canvas, mini_text\n"
            "def frame(i):\n"
            "    cv = Canvas()\n"
            "    mini_text(cv, 'E=mc', 2 + i, 2, 'W')\n"
            "    return cv\n"))
        _, bad_owner = self.audit("scientist-idle", mod.frame)
        self.assertTrue(any("tidak statis" in b for b in bad_owner), bad_owner)
        _, bad_other = self.audit("mathematician-idle", mod.frame)
        self.assertTrue(any("lebih dari 3" in b for b in bad_other), bad_other)

    def test_patch_is_restored(self):
        real = monkey.mini_text
        mod = fake_module("uji_pulih", "from monkey import Canvas, mini_text as m\ndef frame(i):\n    return Canvas()\n")
        self.audit("uji-pulih", mod.frame)
        self.assertIs(monkey.mini_text, real)
        self.assertIs(mod.m, real)


if __name__ == "__main__":
    unittest.main()


class SeamPop(unittest.TestCase):
    """V4: SEAM-POP harus menandai loop bergigi gergaji (perubahan besar di sambungan) dan tidak menandai loop
    mulus. Frame sintetik 64x48 dibandingkan dengan vp.diff, sama seperti sheet sungguhan."""

    @staticmethod
    def frames(xs, w=30, h=20):
        from PIL import Image
        out = []
        for x in xs:
            im = Image.new("RGBA", (64, 48), (0, 0, 0, 0))
            for yy in range(10, 10 + h):
                for xx in range(x, x + w):
                    im.putpixel((xx, yy), (226, 58, 48, 255))
            out.append(im)
        return out

    def metrics(self, xs, **k):
        fr = self.frames(xs, **k)
        steps = [vp.diff(fr[i], fr[i + 1]) for i in range(len(fr) - 1)]
        return vp.seam_metrics(steps, vp.diff(fr[-1], fr[0]))

    def test_sawtooth_flagged(self):
        # balok 30x20 bergeser 3 px per frame lalu meloncat kembali ke awal di sambungan loop
        r = self.metrics([3 * k for k in range(11)])
        self.assertEqual(r["maks"], 120)
        self.assertEqual(r["seam"], 1200)
        self.assertTrue(r["pop"], r)
        self.assertTrue(r["gagal"], r)

    def test_smooth_loop_not_flagged(self):
        # gerak bolak-balik kosinus: langkah terbesar di tengah, seam di titik balik yang lambat
        import math
        xs = [int(round(15 * (1 - math.cos(2 * math.pi * k / 12)) / 2)) for k in range(12)]
        r = self.metrics(xs)
        self.assertGreater(r["maks"], 100)
        self.assertFalse(r["pop"], r)
        self.assertFalse(r["gagal"], r)

    def test_small_motion_below_minimum(self):
        # gigi gergaji kecil (maks <= 100 px) tidak memicu SEAM-POP, tetapi tetap GAGAL lewat ambang 1,25 x maks
        r = self.metrics([k for k in range(8)], w=6, h=4)
        self.assertLessEqual(r["maks"], 100)
        self.assertFalse(r["pop"], r)
        self.assertTrue(r["gagal"], r)

    def test_static_loop(self):
        r = self.metrics([5] * 6)
        self.assertEqual((r["maks"], r["seam"], r["pop"], r["gagal"]), (0, 0, False, False))


class HeroCanvasSchema(unittest.TestCase):
    """Kanvas per sel (field opsional `canvas` dan `gif_scale`): bawaan tetap 64x48 dan skala 8; sel hero 128x96 dan x4."""

    def test_defaults_are_the_global_canvas(self):
        self.assertEqual(vp.cell_canvas({}), (64, 48))
        self.assertEqual(vp.cell_scale({}), 8)
        self.assertEqual(vp.cell_canvas({"canvas": {"w": 128, "h": 96}}), (128, 96))
        self.assertEqual(vp.cell_scale({"gif_scale": 4}), 4)
        self.assertEqual((monkey.W, monkey.H), (64, 48))
        cv = monkey.Canvas()
        self.assertEqual((cv.w, cv.h), (64, 48))
        self.assertEqual((monkey.Canvas(128, 96).w, monkey.Canvas(128, 96).h), (128, 96))

    def test_canvas_problems(self):
        self.assertEqual(vp.canvas_problems({}), [])
        self.assertEqual(vp.canvas_problems({"canvas": {"w": 128, "h": 96}, "gif_scale": 4}), [])
        for bad in ({"canvas": {"w": 0, "h": 96}}, {"canvas": {"w": 128}}, {"canvas": [128, 96]}, {"canvas": {"w": 128.0, "h": 96}},
                    {"canvas": {"w": True, "h": 96}}, {"gif_scale": 0}, {"gif_scale": "4"}, {"gif_scale": True}):
            self.assertTrue(vp.canvas_problems(bad), bad)

    def test_frames_of_uses_the_cell_canvas(self):
        import tempfile
        from PIL import Image
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "s.png")
            Image.new("RGBA", (256, 96), (1, 2, 3, 255)).save(path)
            fr = vp.frames_of(path, 1, (128, 96))
            self.assertEqual((len(fr), fr[0].size), (2, (128, 96)))
            Image.new("RGBA", (192, 48), (1, 2, 3, 255)).save(path)
            fr = vp.frames_of(path)                                  # tanpa canvas: kanvas global 64x48 seperti dulu
            self.assertEqual((len(fr), fr[0].size), (3, (64, 48)))

    def test_gif_timeline_with_cell_scale_and_no_loop(self):
        import tempfile
        import export
        import hero
        from PIL import Image
        cvs = []
        for k in range(2):
            cv = hero.PartCanvas()
            for x in range(10 + k, 30 + k):
                for y in range(20, 40):
                    cv.put(x, y, "o2" if k == 0 else "rb")
            cvs.append(cv)
        index, palette = export.local_palette(cvs)
        gif = [export.indexed(cv, 4, index, palette) for cv in cvs]
        self.assertEqual(gif[0].size, (512, 384))
        cell = {"canvas": {"w": 128, "h": 96}, "gif_scale": 4, "durations_ms": [100, 200], "loop": False}
        sheet = []
        for cv in cvs:
            im = cv.image(1)
            sheet.append(im)
        with tempfile.TemporaryDirectory() as d:
            for loop in (False, True):
                path = os.path.join(d, "a%d.gif" % loop)
                opts = dict(save_all=True, append_images=gif[1:], duration=[100, 200], transparency=0, disposal=2, optimize=True)
                if loop:
                    opts["loop"] = 0
                gif[0].save(path, **opts)
                n, t, lp, bad = vp.gif_timeline_matches(cell, path, sheet)
                self.assertEqual((n, t, bad), (2, 300, []))
                self.assertEqual(lp, 0 if loop else None)
            # skala yang salah di manifest harus terdeteksi sebagai frame beda
            wrong = dict(cell, gif_scale=8)
            _, _, _, bad = vp.gif_timeline_matches(wrong, path, sheet)
            self.assertTrue(bad)


class HeroPackSpec(unittest.TestCase):
    def test_canvas_loop_and_manifest(self):
        import export
        import pack
        self.assertEqual(pack.canvas_of("berserker-hero-run"), (128, 96, 4))
        self.assertEqual(pack.canvas_of("normal-idle"), (64, 48, 8))
        self.assertEqual(pack.canvas_of("ngopi-santai"), (64, 48, 8))
        self.assertFalse(pack.loops("berserker-hero-rage"))
        self.assertTrue(pack.loops("berserker-hero-run"))
        m = pack.manifest(export.all_scenes())
        hero = m["cells"]["berserker-hero"]
        self.assertEqual(sorted(hero), sorted(vp.HERO_SPEC))
        for state, (frames, loop) in vp.HERO_SPEC.items():
            c = hero[state]
            self.assertEqual((c["frames"], c["loop"], c["canvas"], c["gif_scale"], c["gate"]), (frames, loop, {"w": 128, "h": 96}, 4, "K"), state)
            self.assertNotIn("sheet4x", c)
        entry = next(c for c in m["costumes"] if c["id"] == "berserker-hero")
        self.assertEqual((entry["label"], entry["group"], entry["base"]), ("Berserker Hero", "fantasy", "viking-berserker"))
        # sel lama tidak mendapat field baru
        for costume, row in m["cells"].items():
            if costume != "berserker-hero":
                for cell in row.values():
                    self.assertNotIn("canvas", cell)
                    self.assertNotIn("gif_scale", cell)
                    self.assertIs(cell["loop"], True)
        self.assertEqual(m["canvas"], {"w": 64, "h": 48})
        self.assertEqual(m["gif_scale"], 8)


class HeroMeasure(unittest.TestCase):
    def setUp(self):
        import hero
        import hero_check
        import hero_scenes
        self.hero, self.hc, self.hs = hero, hero_check, hero_scenes

    def test_spec_frames_loop_keyframes_and_non_uniform_durations(self):
        self.assertEqual(sorted(self.hs.TRACKS), sorted(vp.HERO_SPEC))
        for state, (frames, loop) in vp.HERO_SPEC.items():
            t = self.hs.TRACKS[state]
            self.assertEqual((t.n, t.loop), (frames, loop), state)
            self.assertTrue(0 <= t.keyframe < t.n, state)
            self.assertGreaterEqual(len({t.duration(i) for i in range(t.n)}), 3, state)

    def test_all_frames_stay_in_palette_canvas_and_above_the_floor(self):
        keys = set(self.hero.HERO_PAL)
        used = set()
        for t in self.hs.TRACKS.values():
            for i in range(t.n):
                cv = t.frame(i)
                self.assertEqual((cv.w, cv.h), (128, 96))
                used |= set(cv.px.values())
                self.assertFalse([k for k in cv.px if k[1] >= self.hero.FLOOR], (t.name, i))
        self.assertLessEqual(used, keys | set(self.hero.monkey.PAL) | set(self.hero.monkey.PAL_EXT))
        self.assertLessEqual(len(used), 28)

    def test_idle_keyframe_passes_readability_and_blade(self):
        cv = self.hero.render_pose(self.hero.pose_idle())
        r = self.hc.readability(cv)
        self.assertEqual(self.hc.readability_failures(r), [], r)
        self.assertEqual(self.hc.blade_failures(self.hc.blade_static()), [])

    def test_readability_failures_each_limit(self):
        ok = {"helm": (40, 30), "snout": (12, 9), "horn_px": [20.0, 20.0], "socket": [(5, 4), (5, 4)], "teeth": 6, "teeth_width": [2],
              "plates": [20, 20, 20]}
        self.assertEqual(self.hc.readability_failures(ok), [])
        for key, bad in (("helm", (30, 30)), ("helm", (40, 20)), ("snout", (8, 9)), ("horn_px", [20.0, 10.0]), ("socket", [(5, 4), (3, 4)]),
                         ("teeth", 5), ("teeth_width", [1]), ("plates", [20, 20, 4])):
            self.assertTrue(self.hc.readability_failures(dict(ok, **{key: bad})), (key, bad))
        self.assertTrue(self.hc.blade_failures({"lebar": 8, "luk": [5, 5], "amplitudo_min": 4}))
        self.assertTrue(self.hc.blade_failures({"lebar": 16, "luk": [4, 4], "amplitudo_min": 4}))
        self.assertTrue(self.hc.blade_failures({"lebar": 16, "luk": [5, 5], "amplitudo_min": 2}))

    def test_visibility_detects_a_covered_face(self):
        hero = self.hero
        p = hero.pose_idle()
        clean = hero.render_pose(p)
        self.assertEqual({k: v[0] == v[1] for k, v in self.hc.visibility(clean, p).items()},
                         {"face": True, "eye": True, "mouth": True, "ear": True})
        hx, hy = hero.geometry(p)["head"]

        def cover(cv, g):
            hero.part(cv, "penutup")
            for x in range(int(hx) - 6, int(hx) + 7):
                for y in range(int(hy), int(hy) + 6):
                    cv.put(x, y, "o2")
        q = dict(p, fx=[cover])
        vis = self.hc.visibility(hero.render_pose(q), q)
        self.assertLess(vis["eye"][0], vis["eye"][1])
        self.assertLess(vis["face"][0], vis["face"][1])

    def test_head_height_is_stable_within_a_state(self):
        for state in ("idle", "run", "defeated"):
            t = self.hs.TRACKS[state]
            hh = [self.hc.head_height(t.frame(i)) for i in range(t.n)]
            self.assertLessEqual((max(hh) - min(hh)) / float(max(hh)), vp.HERO_HEAD_VARIATION, (state, hh))

    def test_run_silhouettes_differ_between_consecutive_frames(self):
        t = self.hs.TRACKS["run"]
        masks = [set(t.frame(i).px) for i in range(t.n)]
        ious = [self.hc.iou(masks[i], masks[(i + 1) % t.n]) for i in range(t.n)]
        self.assertLessEqual(max(ious), vp.HERO_RUN_IOU_MAX, ious)

    def test_loop_seam_not_larger_than_largest_step(self):
        for state, (frames, loop) in vp.HERO_SPEC.items():
            if not loop:
                continue
            t = self.hs.TRACKS[state]
            ims = [t.frame(i).image(1) for i in range(t.n)]
            steps = [vp.diff(ims[i], ims[i + 1]) for i in range(t.n - 1)]
            self.assertLessEqual(vp.diff(ims[-1], ims[0]), max(steps), state)

    def test_contrast_helper(self):
        self.assertAlmostEqual(self.hc.contrast((0, 0, 0), (255, 255, 255)), 21.0, places=1)
        self.assertAlmostEqual(self.hc.contrast((10, 20, 30), (10, 20, 30)), 1.0)

    def test_no_blood_color_outside_face_and_mouth(self):
        for t in self.hs.TRACKS.values():
            for i in range(t.n):
                cv = t.frame(i)
                owners = {cv.owner.get(k) for k, c in cv.px.items() if c in ("ra", "rb")}
                self.assertLessEqual(owners - {None}, {"face", "mouth"}, (t.name, i))

    def test_additive_rig_defaults_leave_phase_b_keyposes_unchanged(self):
        import hashlib
        want = {"idle": "11974b75", "run": "08796a4b", "attack-smash": "76ba21ad"}      # hash piksel pose kunci Fase B (disetujui pemilik)
        for name, fn in self.hero.KEYPOSES.items():
            got = hashlib.sha256(self.hero.render_pose(fn()).image(1).tobytes()).hexdigest()[:8]
            self.assertEqual(got, want[name], name)
