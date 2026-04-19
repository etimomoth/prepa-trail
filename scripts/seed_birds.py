"""Download a small set of real bird photos from loremflickr into data/photos/birds/.

Organized into 5 species × 5 photos with staggered EXIF dates per species so
HDBSCAN has both visual and temporal signal.
"""

from __future__ import annotations

import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import httpx
import piexif
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "photos" / "birds"

SPECIES = ["eagle", "flamingo", "owl", "robin", "mallard"]
PER_SPECIES = 5
BASE_DAY = datetime(2025, 7, 1, 9, 0)


def fetch(url: str, dest: Path) -> bool:
    try:
        with httpx.Client(follow_redirects=True, timeout=20.0) as c:
            r = c.get(url)
            r.raise_for_status()
            dest.write_bytes(r.content)
        return True
    except Exception as e:
        print(f"  ! failed {url}: {e}", file=sys.stderr)
        return False


def stamp_exif(path: Path, when: datetime) -> None:
    try:
        with Image.open(path) as img:
            img.load()
            fmt = img.format
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
            exif_bytes = piexif.dump(exif_dict)
            img.save(path, fmt or "JPEG", exif=exif_bytes, quality=90)
    except Exception as e:
        print(f"  ! exif stamp failed on {path.name}: {e}", file=sys.stderr)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    written = 0
    for si, species in enumerate(SPECIES):
        for i in range(PER_SPECIES):
            # lock is loremflickr's seed for reproducibility
            url = f"https://loremflickr.com/640/480/{species}?lock={si * 100 + i + 1}"
            out = OUT / f"{species}_{i:02d}.jpg"
            if fetch(url, out):
                when = BASE_DAY + timedelta(days=si * 7, hours=i)
                stamp_exif(out, when)
                written += 1
                time.sleep(0.3)  # polite to loremflickr
    print(f"wrote {written} bird photos into {OUT}")


if __name__ == "__main__":
    main()
