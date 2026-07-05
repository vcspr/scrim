"""duotone — photo mapped to a two-color duotone, ALL-CAPS tracked headline.

The image is flattened to luminance and remapped between a shadow color and a
highlight color, so any photo takes the brand's two-tone. A bottom fade grounds
a centered letterspaced headline. Bold words via **markup**. Optional kicker.
"""
from PIL import Image, ImageOps, ImageDraw

from core import cover, scrim, parse_runs, run_width, draw_tracked, autofit, paste_logo, font


def render(image_path, out_path, headline="", *, size=(1080, 1350), kicker=None,
           logo=None, shadow=(16, 22, 43), highlight=(233, 229, 214), track=3):
    W, H = size
    card = cover(Image.open(image_path).convert("RGB"), W, H)
    gray = ImageOps.autocontrast(ImageOps.grayscale(card), cutoff=1)
    canvas = ImageOps.colorize(gray, black=shadow, white=highlight).convert("RGB")

    if headline:
        scrim(canvas, 0.42, 205, 2.0)
    if logo:
        paste_logo(canvas, logo)

    if headline:
        draw = ImageDraw.Draw(canvas)
        runs = parse_runs(headline, caps=True)
        start = int(W * 0.0518)  # ~56px at 1080 wide
        _, fr, fb, total = autofit(draw, runs, "mono", W - 140, start, track=track)
        asc, desc = fr.getmetrics()
        y = H - int(H * 0.09) - (asc + desc)
        x = (W - total) / 2
        for t, b in runs:
            f = fb if b else fr
            draw_tracked(draw, x, y + 2, t, f, shadow, track)          # shadow pass for legibility
            x = draw_tracked(draw, x, y, t, f, highlight, track)

        if kicker:
            kf = font("mono", 19, 400)
            kt = kicker.upper()
            kw = run_width(draw, kt, kf, 4)
            draw_tracked(draw, (W - kw) / 2, y - 42, kt, kf, highlight, 4)

    canvas.save(out_path, "PNG")
    return out_path
