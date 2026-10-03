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


class HeroFindings(unittest.TestCase):
    """vp.hero_findings (V11 per state) pada sheet yang dibangun dari kode: lulus untuk 8 state, dan gagal bila dirusak."""

    @classmethod
    def setUpClass(cls):
        import hero_scenes
        cls.hs = hero_scenes
        cls.cache = {}

    def build(self, state):
        if state not in self.cache:
            t = self.hs.TRACKS[state]
            sheet = [t.frame(i).image(1) for i in range(t.n)]
            cell = {"frames": t.n, "durations_ms": [int(t.duration(i)) for i in range(t.n)], "loop": t.loop, "keyframe": t.keyframe}
            self.cache[state] = (t, sheet, cell)
        return self.cache[state]

    def test_every_state_passes(self):
        for state in vp.HERO_SPEC:
            t, sheet, cell = self.build(state)
            bad, info = vp.hero_findings(state, t, sheet, cell)
            self.assertEqual(bad, [], state)

    def test_attack_needs_smear_before_impact_and_a_held_impact_frame(self):
        t, sheet, cell = self.build("attack-smash")
        bad, _ = vp.hero_findings("attack-smash", t, sheet, dict(cell, keyframe=0))          # kunci di awal: tidak ada smear sebelumnya
        self.assertTrue(any("smear" in b for b in bad), bad)
        flat = dict(cell, durations_ms=[100] * cell["frames"])
        bad, _ = vp.hero_findings("attack-smash", t, sheet, flat)
        self.assertTrue(any("1,5 x median" in b for b in bad), bad)

    def test_red_face_and_teal_dots_only_in_rage(self):
        t, sheet, cell = self.build("rage")
        bad, info = vp.hero_findings("rage", t, sheet, cell)
        self.assertEqual(bad, [])
        self.assertIsNotNone(info["amuk"])
        bad, _ = vp.hero_findings("idle", t, sheet, dict(cell))                                # rage dinilai sebagai state lain
        self.assertTrue(any("selain rage" in b for b in bad), bad)
        bad, _ = vp.hero_findings("rage", *self.build("idle")[:2], self.build("idle")[2])      # idle dinilai sebagai rage: tidak ada frame marah
        self.assertTrue(any("frame marah" in b for b in bad), bad)

    def test_manifest_keyframes_match_the_code(self):
        import pack
        for state, (frames, loop) in vp.HERO_SPEC.items():
            name, kf, gate = pack.NEW[("berserker-hero", state)]
            self.assertEqual(kf, self.hs.META[state]["keyframe"], state)
            self.assertEqual(name, "berserker-hero-" + state)


class HeroAsymmetry(unittest.TestCase):
    """Elemen asimetris (bahu berlapis 3 pelat, gesper, tanduk patah) harus tetap di sisinya: sprite yang dicerminkan ditandai,
    yang tidak dicerminkan lolos."""

    def setUp(self):
        import hero
        import hero_check
        import hero_scenes
        self.hero, self.hc, self.hs = hero, hero_check, hero_scenes

    def synthetic(self, flip_frames=(), n=5, center=50, shift=0):
        """Frame sintetik: tiga pelat bahu di kiri, tanduk patah di kiri, gesper di tengah (sorot kiri, bayangan kanan)."""
        out = []
        for i in range(n):
            cv = self.hero.PartCanvas()
            f = (lambda x: 2 * center - 1 - x) if i in flip_frames else (lambda x: x)
            for k, name in enumerate(("pauldron1", "pauldron2", "pauldron3")):
                self.hero.part(cv, name)
                for dx in range(4):
                    cv.put(f(center - 20 + k * 3 + dx), 40 + k, "ib")
            self.hero.part(cv, "horn_break")
            for dx in range(3):
                cv.put(f(center - 18 + dx), 20, "il")
            self.hero.part(cv, "buckle")
            cv.put(f(center - 2 + shift), 50, "kl")
            cv.put(f(center + 2 + shift), 50, "ks")
            out.append(cv)
        return out

    def flagged(self, frames, center=50, state=None):
        a = self.hc.asymmetry(frames, [center] * len(frames), state)
        return {k: [i for i, _ in v["tanda"]] for k, v in a.items() if v["tanda"]}

    def test_unmirrored_synthetic_passes(self):
        self.assertEqual(self.flagged(self.synthetic()), {})

    def test_mirrored_synthetic_frame_is_flagged_only_there(self):
        got = self.flagged(self.synthetic(flip_frames=(3,)))
        for name in ("pelat_bahu_1", "pelat_bahu_2", "pelat_bahu_3", "tanduk_patah", "cahaya_gesper"):
            self.assertEqual(got.get(name), [3], name)
        self.assertNotIn("gesper", got)                     # gesper di tengah: posisinya tidak berubah saat dicerminkan, sorotnya yang berubah

    def test_second_half_flip_is_caught(self):
        got = self.flagged(self.synthetic(flip_frames=(6, 7, 8, 9, 10, 11), n=12))
        self.assertEqual(got["pelat_bahu_2"], [6, 7, 8, 9, 10, 11])

    def test_buckle_off_centre_is_flagged(self):
        got = self.flagged(self.synthetic(shift=4))
        self.assertEqual(sorted(got["gesper"]), [0, 1, 2, 3, 4])

    def test_explicit_turn_is_exempt(self):
        frames = self.synthetic(flip_frames=(2,))
        self.hc.EXPLICIT_TURNS["uji-balik"] = {2}
        try:
            self.assertEqual(self.flagged(frames, state="uji-balik"), {})
        finally:
            del self.hc.EXPLICIT_TURNS["uji-balik"]
        self.assertTrue(self.flagged(frames))

    def test_unknown_side_uses_the_first_visible_frame_and_skips_hidden(self):
        self.assertEqual(self.hc.side_flags([(-5, 1), (-6, 1), (5, 1)]), [(2, "pindah sisi: dx 5.0, seharusnya kiri")])
        self.assertEqual(self.hc.side_flags([(None, 0), (4, 1), (None, 0), (3, 1), (-2, 1)])[0][0], 4)
        self.assertEqual(self.hc.side_flags([(-5, 1), (None, 0), (-1, 1)]), [])

    def test_real_frames_pass_and_their_mirror_is_flagged(self):
        sided = ["pelat_bahu_1", "pelat_bahu_2", "pelat_bahu_3", "tanduk_patah", "bahu_kecil", "ekor", "moncong", "cahaya_gesper"]
        for state, i in (("idle", 0), ("run", 3), ("run", 9), ("attack-smash", 7), ("attack-leap", 4), ("defeated", 3)):
            t = self.hs.TRACKS[state]
            cv, tc = t.frame(i), self.hero.geometry(t.pose(i))["tcx"]
            self.assertEqual(self.flagged([cv], tc), {}, (state, i))
            got = self.flagged([self.hc.mirrored(cv, tc)], tc)
            for name in sided:
                self.assertEqual(got.get(name), [0], (state, i, name))
            self.assertNotIn("gesper", got)

    def test_every_hero_frame_keeps_its_side(self):
        for state, t in self.hs.TRACKS.items():
            cvs = [t.frame(i) for i in range(t.n)]
            a = self.hc.asymmetry(cvs, [self.hero.geometry(t.pose(i))["tcx"] for i in range(t.n)], state)
            for name, v in a.items():
                self.assertEqual(v["tanda"], [], (state, name))
                self.assertEqual(v["tidak_terlihat"], [], (state, name))


class SeamPopExempt(unittest.TestCase):
    """Pengecualian SEAM-POP berserker-hero/run: hanya bila daftarnya cocok DAN datanya memang gerak seragam."""

    def test_uniform_run_is_exempt_with_a_written_reason(self):
        r = vp.seam_metrics([3600, 3500, 3747, 3600, 3550, 3700], 3679)
        self.assertTrue(r["pop"], r)
        why = vp.pop_exempt("berserker-hero", "run", r)
        self.assertIn("seragam", why)
        self.assertLessEqual(r["seam_per_median"], vp.POP_UNIFORM_SEAM_PER_MEDIAN)

    def test_other_cells_are_never_exempt(self):
        r = vp.seam_metrics([3600, 3500, 3747, 3600, 3550, 3700], 3679)
        self.assertIsNone(vp.pop_exempt("viking", "idle", r))
        self.assertIsNone(vp.pop_exempt("berserker-hero", "idle", r))

    def test_listed_cell_with_a_real_pop_is_still_warned(self):
        # langkah kecil dan tidak seragam, seam hampir sebesar langkah terbesar: ini lonjakan di sambungan, bukan gerak seragam
        r = vp.seam_metrics([120, 150, 130, 3700, 140, 125], 3500)
        self.assertTrue(r["pop"], r)
        self.assertIsNone(vp.pop_exempt("berserker-hero", "run", r))

    def test_no_pop_means_nothing_to_exempt(self):
        r = vp.seam_metrics([3600, 3500, 3747], 300)
        self.assertFalse(r["pop"])
        self.assertIsNone(vp.pop_exempt("berserker-hero", "run", r))

    def test_complementary_metric_is_seam_over_median(self):
        r = vp.seam_metrics([100, 200, 300], 400)
        self.assertAlmostEqual(r["seam_per_median"], 2.0)


class HeroRageHold(unittest.TestCase):
    def test_rage_last_frame_is_held_1500_ms_and_only_the_last_changed(self):
        import hero_scenes
        t = hero_scenes.TRACKS["rage"]
        self.assertEqual(t.duration(t.n - 1), 1500)
        self.assertEqual([t.duration(i) for i in range(t.n - 1)], [200, 140, 140, 180, 70, 90, 110, 70, 70, 70, 120])
        self.assertEqual(vp.HERO_LAST_HOLD_MS, {"rage": 1500})

    def test_validator_rejects_a_rage_with_a_short_last_frame(self):
        import hero_scenes
        t = hero_scenes.TRACKS["rage"]
        sheet = [t.frame(i).image(1) for i in range(t.n)]
        ms = [int(t.duration(i)) for i in range(t.n)]
        cell = {"frames": t.n, "durations_ms": ms, "loop": False, "keyframe": t.keyframe}
        self.assertEqual(vp.hero_findings("rage", t, sheet, cell)[0], [])
        short = dict(cell, durations_ms=ms[:-1] + [400])
        bad = vp.hero_findings("rage", t, sheet, short)[0]
        self.assertTrue(any("frame terakhir 400 ms" in b for b in bad), bad)
