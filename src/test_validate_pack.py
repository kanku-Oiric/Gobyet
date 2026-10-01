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
