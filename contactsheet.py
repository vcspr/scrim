#!/usr/bin/env python3
"""contactsheet.py — numbered grid of every image in a folder.

The curation pattern: render a sheet, pick numbers by eye, feed the numbers to
your own selection step. Deterministic order (sorted by filename) so a number
always maps to the same image.

Usage:
  python3 contactsheet.py ./photos --out sheet.png [--cols 5 --cell 320]
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw

from core import cover, font

EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--out", default="sheet.png")
    ap.add_argument("--cols", type=int, default=5)
    ap.add_argument("--cell", type=int, default=320)
    a = ap.parse_args()

    files = sorted(p for p in Path(a.folder).iterdir() if p.suffix.lower() in EXTS)
    if not files:
        raise SystemExit(f"no images in {a.folder}")

    cols, cell, pad = a.cols, a.cell, 10
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (cell + pad) + pad, rows * (cell + pad) + pad), (14, 14, 14))
    draw = ImageDraw.Draw(sheet)
    tag = font("mono", 22, 700)

    for i, p in enumerate(files):
        r, c = divmod(i, cols)
        x, y = pad + c * (cell + pad), pad + r * (cell + pad)
        sheet.paste(cover(Image.open(p).convert("RGB"), cell, cell), (x, y))
        label = f"{i + 1:02d}"
        draw.rectangle([x, y, x + 46, y + 30], fill=(0, 0, 0))
        draw.text((x + 8, y + 4), label, font=tag, fill=(255, 255, 255))

    sheet.save(a.out)
    print(f"saved {a.out}  ({len(files)} images, {cols}x{rows})")


if __name__ == "__main__":
    main()
