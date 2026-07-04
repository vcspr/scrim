"""editorial — full-bleed photo, left-aligned serif headline, mono kicker.

High-contrast Playfair Display over a deep bottom fade. Headline sits in the
lower-left with a thin rule above it. Manual line breaks with "|"; bold words
via **markup** (rendered at heavier weight).
"""
from PIL import Image, ImageDraw

from core import cover, scrim, parse_runs, run_width, draw_tracked, autofit, paste_logo, font


def render(image_path, out_path, headline="", *, size=(1080, 1350), kicker=None,
           logo=None, margin=72, bg=(0, 0, 0)):
    W, H = size
    canvas = cover(Image.open(image_path).convert("RGB"), W, H)

    if headline:
        scrim(canvas, 0.46, 236, 1.9)
        scrim(canvas, 0.14, 100, 1.5, top=True)

    if logo:
        paste_logo(canvas, logo)

    if headline:
        draw = ImageDraw.Draw(canvas)
        lines = [ln.strip() for ln in headline.split("|") if ln.strip()]
        run_lines = [parse_runs(ln) for ln in lines]

        max_w = W - 2 * margin
        start = int(W * 0.083)  # ~90px at 1080 wide
        fitted = []
        size_px = start
        for runs in run_lines:  # fit every line at a shared size
            s, *_ = autofit(draw, runs, "serif", max_w, size_px, weights=(500, 800))
            size_px = min(size_px, s)
        fr, fb = font("serif", size_px, 500), font("serif", size_px, 800)
        asc, desc = fr.getmetrics()
        line_h = int((asc + desc) * 1.02)

        y = H - int(H * 0.083) - line_h * len(run_lines)
        rule_y = y - 26
        draw.rectangle([margin, rule_y, margin + 64, rule_y + 3], fill=(255, 255, 255))

        if kicker:
            kf = font("mono", 20, 500)
            draw_tracked(draw, margin, rule_y - 44, kicker.upper(), kf, (235, 235, 235), 4)

        for runs in run_lines:
            x = margin
            for t, b in runs:
                f = fb if b else fr
                x = draw_tracked(draw, x, y, t, f, (255, 255, 255), 0)
            y += line_h

    canvas.save(out_path, "PNG")
    return out_path
