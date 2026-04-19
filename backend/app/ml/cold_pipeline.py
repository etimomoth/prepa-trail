"""Cold pipeline stubs. Imports are lazy so the backend runs without optional deps."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image

from app.core.logging import get_logger

log = get_logger(__name__)


@dataclass
class ColdResult:
    caption: str | None = None
    quality_score: float | None = None
    detections: list[tuple[str, float, tuple[int, int, int, int]]] = field(default_factory=list)


def laplacian_sharpness(path: Path) -> float:
    """Cheap blur proxy via variance of gradients — no OpenCV dependency."""
    with Image.open(path) as img:
        gray = np.asarray(img.convert("L"), dtype=np.float32)
    gx = np.diff(gray, axis=1)
    gy = np.diff(gray, axis=0)
    return float(gx.var() + gy.var())


def histogram_exposure(path: Path) -> float:
    """Return a score in [0, 1]; low if clipped shadows/highlights dominate."""
    with Image.open(path) as img:
        arr = np.asarray(img.convert("L"), dtype=np.uint8)
    hist, _ = np.histogram(arr, bins=32, range=(0, 255))
    hist = hist / max(hist.sum(), 1)
    clipped = float(hist[0] + hist[-1])
    return max(0.0, 1.0 - clipped * 2.0)


def quality_score(path: Path) -> float:
    sharp = laplacian_sharpness(path)
    expo = histogram_exposure(path)
    sharp_norm = min(sharp / 500.0, 1.0)
    return round(0.6 * sharp_norm + 0.4 * expo, 4)


def caption_blip(path: Path) -> str | None:
    try:
        from transformers import BlipForConditionalGeneration, BlipProcessor  # type: ignore
    except ImportError:
        log.debug("BLIP unavailable, skipping captioning")
        return None
    try:
        proc = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        )
        with Image.open(path) as img:
            inputs = proc(img.convert("RGB"), return_tensors="pt")
        out = model.generate(**inputs, max_new_tokens=40)
        return proc.decode(out[0], skip_special_tokens=True)
    except Exception as e:
        log.warning("BLIP failed on %s: %s", path, e)
        return None


def detect_yolo(path: Path) -> list[tuple[str, float, tuple[int, int, int, int]]]:
    try:
        from ultralytics import YOLO  # type: ignore
    except ImportError:
        log.debug("YOLO unavailable, skipping detection")
        return []
    try:
        model = YOLO("yolov8n.pt")
        res = model(str(path), verbose=False)[0]
        out: list[tuple[str, float, tuple[int, int, int, int]]] = []
        for b in res.boxes:
            cls_id = int(b.cls.item())
            label = res.names.get(cls_id, str(cls_id))
            score = float(b.conf.item())
            x1, y1, x2, y2 = (int(v) for v in b.xyxy[0].tolist())
            out.append((label, score, (x1, y1, x2 - x1, y2 - y1)))
        return out
    except Exception as e:
        log.warning("YOLO failed on %s: %s", path, e)
        return []


def run_cold(path: Path) -> ColdResult:
    return ColdResult(
        caption=caption_blip(path),
        quality_score=quality_score(path),
        detections=detect_yolo(path),
    )
