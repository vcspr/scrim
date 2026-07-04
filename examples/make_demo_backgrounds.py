#!/usr/bin/env python3
"""Generate license-free demo backgrounds procedurally (no stock photos).

Usage: python3 examples/make_demo_backgrounds.py
Writes three 1400x1800 PNGs into examples/.
"""
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).parent
W, H = 1400, 1800
random.seed(7)


def grain(im, strength=14):
    noise = Image.frombytes("L", im.size, bytes(random.getrandbits(8) for _ in range(im.width * im.height)))
    return Image.blend(im, Image.merge("RGB", (noise, noise, noise)), strength / 255)


def blobs(name, palette, bg):
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im)
    for _ in range(9):
        color = random.choice(palette)
        cx, cy = random.randint(0, W), random.randint(0, H)
        r = random.randint(280, 640)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    im = im.filter(ImageFilter.GaussianBlur(180))
    grain(im, 12).convert("RGB").save(OUT / name, quality=88)
    print("wrote", name)


def arcs(name):
    im = Image.new("RGB", (W, H), (12, 12, 14))
    d = ImageDraw.Draw(im)
    for i in range(14):
        r = 140 + i * 110
        hue = 200 + i * 4
        d.arc([W // 2 - r, H - r - 200, W // 2 + r, H + r - 200], 180, 360,
              fill=(hue % 255, 90 + i * 8, 70), width=26)
    im = im.filter(ImageFilter.GaussianBlur(3))
    grain(im, 10).convert("RGB").save(OUT / name, quality=88)
    print("wrote", name)


blobs("demo-dusk.jpg", [(224, 92, 60), (140, 60, 120), (30, 40, 90), (240, 170, 90)], (18, 14, 26))
blobs("demo-moss.jpg", [(40, 90, 70), (150, 180, 120), (16, 40, 36), (220, 220, 190)], (12, 24, 20))
arcs("demo-signal.jpg")
