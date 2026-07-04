"""quote — typographic card. No photo required.

Giant serif pull-quote over a flat color (or a photo, if you pass one),
mono attribution line below a short rule. Break lines with "|"; bold words
via **markup**. Background color via --bg (hex, no #).
"""
from PIL import Image, ImageDraw

from core import cover, scrim, parse_runs, draw_tracked, autofit, paste_logo, font


def render(image_path, out_path, headline="", *, size=(1080, 1350), kicker=None,
           logo=None, margin=84, bg=(16, 16, 18)):
    W, H = size
    if image_path:
        canvas = cover(Image.open(image_path).convert("RGB"), W, H)
        scrim(canvas, 0.9, 200, 1.2)
    else:
        canvas = Image.new("RGB", (W, H), bg)

    if logo:
        paste_logo(canvas, logo)

    draw = ImageDraw.Draw(canvas)
    lines = [ln.strip() for ln in headline.split("|") if ln.strip()]
    run_lines = [parse_runs(ln) for ln in lines]

    max_w = W - 2 * margin
    size_px = int(W * 0.104)  # ~112px at 1080 wide
    for runs in run_lines:
        s, *_ = autofit(draw, runs, "serif", max_w, size_px, weights=(500, 800))
        size_px = min(size_px, s)
    fr, fb = font("serif", size_px, 500), font("serif", size_px, 800)
    asc, desc = fr.getmetrics()
    line_h = int((asc + desc) * 1.04)

    block_h = line_h * len(run_lines)
    y = (H - block_h) // 2 - int(H * 0.02)

    qf = font("serif", int(size_px * 1.6), 800)
    draw.text((margin - 8, y - int(size_px * 1.1)), "“", font=qf, fill=(255, 255, 255))

    for runs in run_lines:
        x = margin
        for t, b in runs:
            f = fb if b else fr
            x = draw_tracked(draw, x, y, t, f, (255, 255, 255), 0)
        y += line_h

    rule_y = y + 30
    draw.rectangle([margin, rule_y, margin + 64, rule_y + 3], fill=(255, 255, 255))
    if kicker:
        kf = font("mono", 22, 500)
        draw_tracked(draw, margin, rule_y + 24, kicker.upper(), kf, (225, 225, 225), 4)

    canvas.save(out_path, "PNG")
    return out_path
