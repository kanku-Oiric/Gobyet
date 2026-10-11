"""Lembar pratinjau satu karakter: semua state, semua frame, 4x, warna + siluet.

    python3 v2/tools/sheet_preview.py knight-heavy out.png [--sil]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
from PIL import Image, ImageDraw  # noqa: E402
import cast  # noqa: E402
import char2  # noqa: E402

BG = (250, 247, 240)


def sheet(cid, out, sc=4, sil=False, states=None, maxf=16):
    ch = cast.get(cid)
    names = states or list(ch.states)
    fw, fh = 64 * sc + 2, 64 * sc + 14
    im = Image.new("RGB", (120 + fw * maxf, fh * len(names)), BG)
    d = ImageDraw.Draw(im)
    for r, name in enumerate(names):
        st = ch.states[name]
        d.text((4, r * fh + fh // 2), name, fill=(60, 40, 30))
        for i in range(min(st.n, maxf)):
            cv = char2.render(ch, name, i)
            fr = cv.image(1)
            if sil:
                a = fr.split()[3]
                fr = Image.new("RGBA", fr.size, (0, 0, 0, 0))
                fr.paste((20, 20, 20, 255), mask=a)
            fr = fr.resize((64 * sc, 64 * sc), Image.NEAREST)
            x, y = 120 + i * fw, r * fh + 12
            d.rectangle([x, y, x + 64 * sc - 1, y + 64 * sc - 1], outline=(225, 218, 205))
            d.line([x, y + (char2.BASE) * sc, x + 64 * sc, y + char2.BASE * sc], fill=(230, 200, 190))
            im.paste(fr, (x, y), fr)
            d.text((x + 2, r * fh), "f%d" % i, fill=(120, 100, 80))
    im.save(out)
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sheet(args[0], args[1], sil="--sil" in sys.argv, sc=int(os.environ.get("SC", "3")))
    print(args[1])
