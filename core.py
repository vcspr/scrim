"""card-forge core: image fitting, gradients, tracked type, and variable fonts.

Everything here is pure Pillow. No browser, no network, no config files.
"""
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONTS = Path(__file__).parent / "fonts"

SIZES = {
    "4x5": (1080, 1350),
    "1x1": (1080, 1080),
    "9x16": (1080, 1920),
    "16x9": (1920, 1080),
}


def font(family, size, weight=400):
    """Load a vendored variable font at a given weight."""
    paths = {
        "mono": FONTS / "GeistMono-Variable.ttf",
        "serif": FONTS / "PlayfairDisplay-Variable.ttf",
    }
    f = ImageFont.truetype(str(paths[family]), size)
    f.set_variation_by_axes([weight])
    return f


def cover(im, w, h):
    """Scale-to-fill and center-crop, like CSS object-fit: cover."""
    sw, sh = im.size
    s = max(w / sw, h / sh)
    nw, nh = int(sw * s + 0.5), int(sh * s + 0.5)
    im = im.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - w) // 2, (nh - h) // 2
    return im.crop((left, top, left + w, top + h))


def vgrad(w, h, amax, power, top_dark=False):
    """Vertical alpha gradient. amax = peak opacity, power shapes the curve
    (higher = fade stays subtle longer, then commits at the edge)."""
    g = Image.new("L", (1, h), 0)
    px = g.load()
    for y in range(h):
        t = y / (h - 1)
        if top_dark:
            t = 1 - t
        px[0, y] = int(amax * (t ** power))
    return g.resize((w, h))


def scrim(card, height_frac=0.34, amax=224, power=2.1, top=False):
    """Paste a black fade onto the bottom (or top) of a card, in place."""
    w, h = card.size
    sh = int(h * height_frac)
    grad = vgrad(w, sh, amax, power, top_dark=top)
    y = 0 if top else h - sh
    card.paste(Image.new("RGB", (w, sh), (0, 0, 0)), (0, y), grad)
    return card


def parse_runs(headline, caps=False):
    """Split '**bold**' markup into [(text, is_bold)] runs."""
    runs = [(p, i % 2 == 1) for i, p in enumerate(re.split(r"\*\*", headline)) if p != ""]
    return [(t.upper(), b) for t, b in runs] if caps else runs


def run_width(draw, s, f, track):
    if not s:
        return 0
    return sum(draw.textlength(c, font=f) for c in s) + track * len(s)


def draw_tracked(draw, x, y, s, f, fill, track):
    """Draw text with per-character letterspacing. Returns the end x."""
    for c in s:
        draw.text((x, y), c, font=f, fill=fill)
        x += draw.textlength(c, font=f) + track
    return x


def autofit(draw, runs, family, max_w, start_size, min_size=24, track=0,
            weights=(400, 700), step=2):
    """Shrink from start_size until the tracked runs fit max_w.
    Returns (size, regular_font, bold_font, total_width)."""
    size = start_size
    while size > min_size:
        fr, fb = font(family, size, weights[0]), font(family, size, weights[1])
        total = sum(run_width(draw, t, (fb if b else fr), track) for t, b in runs)
        if total <= max_w:
            return size, fr, fb, total
        size -= step
    fr, fb = font(family, min_size, weights[0]), font(family, min_size, weights[1])
    total = sum(run_width(draw, t, (fb if b else fr), track) for t, b in runs)
    return min_size, fr, fb, total


def paste_logo(canvas, logo_path, height=32, pos=(52, 54)):
    """Optional logo/wordmark in the top-left safe area."""
    logo = Image.open(logo_path).convert("RGBA")
    logo = logo.resize((int(logo.width * height / logo.height), height), Image.LANCZOS)
    canvas.paste(logo, pos, logo)
