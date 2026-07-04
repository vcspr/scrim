#!/usr/bin/env python3
"""card-forge — branded social cards from the command line. Pure Pillow.

Usage:
  python3 cardforge.py photo.jpg --headline "OPENING **NIGHT**"
  python3 cardforge.py photo.jpg --template editorial --size 9x16 \
      --headline "The Night | **Shift**" --kicker "Chapter Two" --out story.png

Options:
  --template mono|editorial   (default: mono)
  --size 4x5|1x1|9x16|16x9    (default: 4x5)
  --headline "TEXT **BOLD**"  bold words via **markup**; editorial breaks lines on |
  --kicker "small line"       eyebrow text above the headline
  --logo path.png             optional wordmark, top-left safe area
  --out out.png               (default: output/<image>_<template>_<size>.png)
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from core import SIZES  # noqa: E402
from templates import mono, editorial, quote  # noqa: E402

TEMPLATES = {"mono": mono.render, "editorial": editorial.render, "quote": quote.render}


def main():
    ap = argparse.ArgumentParser(description="Branded social cards from the command line.")
    ap.add_argument("image", nargs="?", default=None, help="source photo (optional for the quote template)")
    ap.add_argument("--template", choices=sorted(TEMPLATES), default="mono")
    ap.add_argument("--size", choices=sorted(SIZES), default="4x5")
    ap.add_argument("--headline", default="")
    ap.add_argument("--kicker")
    ap.add_argument("--logo")
    ap.add_argument("--out")
    a = ap.parse_args()

    out = a.out
    if not out:
        Path("output").mkdir(exist_ok=True)
        out = f"output/{(Path(a.image).stem if a.image else a.template)}_{a.template}_{a.size}.png"

    TEMPLATES[a.template](
        a.image, out, a.headline,
        size=SIZES[a.size], kicker=a.kicker, logo=a.logo,
    )
    print(f"saved {out}")


if __name__ == "__main__":
    main()
