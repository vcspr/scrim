"""mono — rounded photo card on black, ALL-CAPS tracked monospace headline.

Full-bleed photo inside a rounded rectangle with a slim frame, a bottom fade
that stays subtle until it grounds the type, and a centered letterspaced
headline. Bold words via **markup**. Optional kicker line above.
"""
from PIL import Image, ImageDraw

from core import cover, scrim, parse_runs, run_width, draw_tracked, autofit, paste_logo, font


def render(image_path, out_path, headline="", *, size=(1080, 1350), kicker=None,
           logo=None, margin=16, radius=26, track=3, bg=(0, 0, 0)):
    W, H = size
    cw, ch = W - 2 * margin, H - 2 * margin
    canvas = Image.new("RGB", (W, H), bg)

    card = cover(Image.open(image_path).convert("RGB"), cw, ch)
    if headline:
        scrim(card, 0.34, 224, 2.1)
        scrim(card, 0.16, 120, 1.4, top=True)

    mask = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, cw - 1, ch - 1], radius=radius, fill=255)
    canvas.paste(card, (margin, margin), mask)

    if logo:
        paste_logo(canvas, logo)

    if headline:
        draw = ImageDraw.Draw(canvas)
        runs = parse_runs(headline, caps=True)
        start = int(W * 0.0426)  # ~46px at 1080 wide
        _, fr, fb, total = autofit(draw, runs, "mono", cw - 120, start, track=track)
        asc, desc = fr.getmetrics()
        y = H - int(H * 0.0978) - (asc + desc)  # ~132px above the bottom at 4:5
        x = (W - total) / 2
        for t, b in runs:
            f = fb if b else fr
            draw_tracked(draw, x, y + 2, t, f, (0, 0, 0), track)      # soft shadow pass
            x = draw_tracked(draw, x, y, t, f, (255, 255, 255), track)

        if kicker:
            kf = font("mono", 19, 400)
            kt = kicker.upper()
            kw = run_width(draw, kt, kf, 4)
            draw_tracked(draw, (W - kw) / 2, y - 42, kt, kf, (230, 230, 230), 4)

    canvas.save(out_path, "PNG")
    return out_path
