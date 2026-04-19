"""Quick hot-pipeline throughput benchmark.

Usage:
    python scripts/benchmark.py /path/to/folder
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.ml.hot_pipeline import ClipEncoder, run_hot_batch  # noqa: E402
from app.services.ingest import scan_folder  # noqa: E402


def main(folder: str) -> None:
    paths = scan_folder(Path(folder))
    if not paths:
        print("no images found", file=sys.stderr)
        sys.exit(1)
    encoder = ClipEncoder()
    t0 = time.perf_counter()
    results = run_hot_batch(paths, encoder)
    dt = time.perf_counter() - t0
    rate = len(results) / dt * 60.0
    print(
        f"{len(results)} photos in {dt:.2f}s = {rate:.1f} photos/min "
        f"({dt / max(1, len(results)) * 1000:.1f} ms/photo)"
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1])
