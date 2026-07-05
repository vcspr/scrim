"""grid — full-bleed photo under a thin modular grid, headline in a solid footer band.

A quiet white grid is composited over the photo (rule-of-columns, not a cage),
then a solid band across the bottom carries a centered letterspaced headline.
Bold words via **markup**. Optional kicker above the band.
"""
from PIL import Image, ImageDraw

from core import cover, parse_runs, run_width, draw_tracked, autofit, paste_logo, font


def render(image_path, out_path, headline="", *, size=(1080, 1350), kicker=None,
           logo=None, cols=6, line=(255, 255, 255), line_alpha=44, band=(17, 17, 17), track=3):
    W, H = size
    canvas = cover(Image.open(image_path).convert("RGB"), W, H).convert("RGB")

    # modular grid, composited so the lines stay subtle
    rows = max(1, round(cols * H / W))
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for i in range(1, cols):
        x = round(W * i / cols)
        od.line([(x, 0), (x, H)], fill=line + (line_alpha,), width=1)
    for j in range(1, rows):
        y = round(H * j / rows)
        od.line([(0, y), (W, y)], fill=line + (line_alpha,), width=1)
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")

    draw = ImageDraw.Draw(canvas)
    band_h = int(H * 0.17)
    draw.rectangle([0, H - band_h, W, H], fill=band)

    if logo:
        paste_logo(canvas, logo)

    if headline:
        runs = parse_runs(headline, caps=True)
        start = int(W * 0.0463)  # ~50px at 1080 wide
        _, fr, fb, total = autofit(draw, runs, "mono", W - 120, start, track=track)
        asc, desc = fr.getmetrics()
        y = H - band_h + (band_h - (asc + desc)) // 2
        x = (W - total) / 2
        for t, b in runs:
            f = fb if b else fr
            x = draw_tracked(draw, x, y, t, f, (255, 255, 255), track)

        if kicker:
            kf = font("mono", 18, 400)
            kt = kicker.upper()
            kw = run_width(draw, kt, kf, 4)
            draw_tracked(draw, (W - kw) / 2, H - band_h - 32, kt, kf, (245, 245, 245), 4)

    canvas.save(out_path, "PNG")
    return out_path
