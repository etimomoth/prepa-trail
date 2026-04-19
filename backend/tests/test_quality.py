from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from app.ml.cold_pipeline import histogram_exposure, laplacian_sharpness, quality_score


def test_sharpness_flat_image_is_low(tmp_path: Path) -> None:
    p = tmp_path / "flat.png"
    Image.new("RGB", (64, 64), (128, 128, 128)).save(p)
    assert laplacian_sharpness(p) < 1.0


def test_sharpness_noise_image_is_higher(tmp_path: Path) -> None:
    p = tmp_path / "noise.png"
    rng = np.random.default_rng(0)
    arr = rng.integers(0, 255, (64, 64, 3), dtype=np.uint8)
    Image.fromarray(arr).save(p)
    assert laplacian_sharpness(p) > 100.0


def test_quality_score_in_range(tmp_path: Path) -> None:
    p = tmp_path / "x.png"
    Image.new("RGB", (32, 32), (80, 80, 80)).save(p)
    s = quality_score(p)
    assert 0.0 <= s <= 1.0
    assert 0.0 <= histogram_exposure(p) <= 1.0
