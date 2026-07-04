#!/usr/bin/env python3
"""batch.py — a folder of finished posts from one manifest.

Manifest is JSON (a list of jobs) or CSV with the same field names:

  [
    { "image": "shoot/01.jpg", "template": "mono", "size": "4x5",
      "headline": "OPENING **NIGHT**", "kicker": "vol. 04", "out": "output/01.png" }
  ]

Usage:
  python3 batch.py jobs.json
  python3 batch.py jobs.csv
"""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from core import SIZES  # noqa: E402
from templates import mono, editorial, quote  # noqa: E402

TEMPLATES = {"mono": mono.render, "editorial": editorial.render, "quote": quote.render}


def load_jobs(path):
    p = Path(path)
    if p.suffix.lower() == ".csv":
        with open(p, newline="") as f:
            return [dict(row) for row in csv.DictReader(f)]
    return json.loads(p.read_text())


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    jobs = load_jobs(sys.argv[1])
    Path("output").mkdir(exist_ok=True)
    done = failed = 0
    for i, job in enumerate(jobs, 1):
        try:
            template = job.get("template", "mono")
            size = SIZES[job.get("size", "4x5")]
            image = job.get("image") or None
            out = job.get("out") or f"output/batch_{i:03d}.png"
            TEMPLATES[template](
                image, out, job.get("headline", ""),
                size=size, kicker=job.get("kicker") or None, logo=job.get("logo") or None,
            )
            print(f"  {i:>3} ✓ {out}")
            done += 1
        except Exception as e:
            print(f"  {i:>3} ✗ {job.get('out', '?')}: {e}")
            failed += 1
    print(f"\n{done} rendered, {failed} failed")


if __name__ == "__main__":
    main()
