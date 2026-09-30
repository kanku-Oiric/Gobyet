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
