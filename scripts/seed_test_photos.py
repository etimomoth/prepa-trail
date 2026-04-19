"""Generate a handful of synthetic photos under data/photos/_seed/ for local tests."""

from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "photos" / "_seed"


def synth(path: Path, palette: tuple[int, int, int]) -> None:
    img = Image.new("RGB", (640, 480), palette)
    draw = ImageDraw.Draw(img)
    for _ in range(12):
        x1, y1 = random.randint(0, 600), random.randint(0, 440)
        x2, y2 = x1 + random.randint(20, 80), y1 + random.randint(20, 80)
        draw.rectangle([x1, y1, x2, y2], fill=tuple(random.randint(0, 255) for _ in range(3)))
    img.save(path, "JPEG", quality=85)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    palettes = [(40, 60, 120), (180, 120, 40), (30, 120, 60), (120, 30, 60)]
    for i in range(24):
        synth(OUT / f"seed_{i:03d}.jpg", palettes[i % len(palettes)])
    print(f"wrote 24 photos into {OUT}")


if __name__ == "__main__":
    main()
