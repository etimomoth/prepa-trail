"""Generate synthetic photos grouped into visually similar events.

Produces 4 events × 6 photos: same palette & composition pattern within each
event, staggered dates. Lets HDBSCAN actually form clusters.

Usage:
    python scripts/seed_test_photos.py
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path

import piexif
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "photos" / "_seed"


EVENTS = [
    {"name": "sunset", "bg": (220, 100, 40), "accent": (40, 20, 80), "day": 1},
    {"name": "forest", "bg": (30, 90, 40), "accent": (15, 50, 25), "day": 10},
    {"name": "beach", "bg": (200, 220, 240), "accent": (250, 220, 140), "day": 20},
    {"name": "city", "bg": (60, 60, 70), "accent": (230, 210, 80), "day": 30},
]


def _exif_with_date(when: datetime) -> bytes:
    stamp = when.strftime("%Y:%m:%d %H:%M:%S").encode()
    exif_dict = {
        "0th": {},
        "Exif": {
            piexif.ExifIFD.DateTimeOriginal: stamp,
            piexif.ExifIFD.DateTimeDigitized: stamp,
        },
        "GPS": {},
        "1st": {},
        "thumbnail": None,
    }
    return piexif.dump(exif_dict)


def synth_event_photo(path: Path, event: dict, index: int, when: datetime) -> None:
    rng = random.Random(hash((event["name"], index)) & 0xFFFFFFFF)
    img = Image.new("RGB", (640, 480), event["bg"])
    draw = ImageDraw.Draw(img)
    for _ in range(10):
        x = rng.randint(0, 560)
        y = rng.randint(0, 400)
        w = rng.randint(40, 120)
        h = rng.randint(40, 120)
        jitter = tuple(min(255, max(0, c + rng.randint(-25, 25))) for c in event["accent"])
        draw.rectangle([x, y, x + w, y + h], fill=jitter)
    img = img.filter(ImageFilter.GaussianBlur(radius=1.0))
    exif = _exif_with_date(when)
    img.save(path, "JPEG", quality=85, exif=exif)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    base = datetime(2025, 6, 1, 12, 0)
    written = 0
    for event in EVENTS:
        for i in range(6):
            when = base + timedelta(days=event["day"], hours=i)
            path = OUT / f"{event['name']}_{i:02d}.jpg"
            synth_event_photo(path, event, i, when)
            written += 1
    print(f"wrote {written} photos across {len(EVENTS)} events into {OUT}")


if __name__ == "__main__":
    main()
