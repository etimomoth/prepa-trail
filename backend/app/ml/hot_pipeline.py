from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import numpy as np
import torch
from PIL import Image, ImageOps

from app.core.config import settings
from app.core.logging import get_logger
from app.ml.models_loader import load_clip

log = get_logger(__name__)


SCENE_PROMPTS = [
    "a photo of a mountain landscape",
    "a photo of a beach or ocean",
    "a photo of a city street",
    "a photo of a forest",
    "a photo of an indoor scene",
    "a photo of people",
    "a photo of a portrait of a face",
    "a photo of food",
    "a photo of a pet or domestic animal",
    "a photo of a bird",
    "a photo of wildlife",
    "a photo of a flower or plant",
    "a photo of a car or vehicle",
    "a photo of a building",
    "a photo of a sunset sky",
    "a photo of snow or winter scene",
    "a photo of a document or screenshot",
]
SCENE_LABELS = [
    "mountain",
    "beach",
    "urban",
    "forest",
    "indoor",
    "people",
    "portrait",
    "food",
    "pet",
    "bird",
    "wildlife",
    "flower",
    "vehicle",
    "building",
    "sunset",
    "winter",
    "document",
]


@dataclass
class HotResult:
    sha256: str
    path: str
    thumb_path: str
    width: int
    height: int
    taken_at: datetime | None
    latitude: float | None
    longitude: float | None
    camera: str | None
    embedding: np.ndarray  # shape (D,), float32, L2 normalized
    scene: str


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _parse_exif_datetime(raw: str | bytes | None) -> datetime | None:
    if not raw:
        return None
    s = raw.decode() if isinstance(raw, bytes) else raw
    for fmt in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s.strip("\x00 "), fmt)
        except ValueError:
            continue
    return None


def _parse_gps(gps: dict) -> tuple[float | None, float | None]:
    def to_deg(val) -> float:
        d, m, s = val
        def f(x):
            return x[0] / x[1] if isinstance(x, tuple) else float(x)
        return f(d) + f(m) / 60 + f(s) / 3600

    try:
        lat = to_deg(gps[2])
        if gps[1] == b"S":
            lat = -lat
        lon = to_deg(gps[4])
        if gps[3] == b"W":
            lon = -lon
        return lat, lon
    except Exception:
        return None, None


def read_exif(path: Path) -> dict:
    try:
        import piexif

        exif = piexif.load(str(path))
    except Exception:
        return {}
    info: dict = {}
    dt = exif.get("Exif", {}).get(piexif.ExifIFD.DateTimeOriginal)
    info["taken_at"] = _parse_exif_datetime(dt)
    camera = exif.get("0th", {}).get(piexif.ImageIFD.Model)
    info["camera"] = camera.decode(errors="ignore").strip("\x00 ") if camera else None
    gps = exif.get("GPS", {}) or {}
    info["lat"], info["lon"] = _parse_gps(gps) if gps else (None, None)
    return info


def make_thumbnail(path: Path, sha: str) -> tuple[Path, int, int]:
    settings.ensure_dirs()
    sub = settings.thumbs_dir / sha[:2]
    sub.mkdir(parents=True, exist_ok=True)
    out = sub / f"{sha}.jpg"
    with Image.open(path) as img:
        img = ImageOps.exif_transpose(img).convert("RGB")
        w, h = img.size
        img.thumbnail((settings.thumb_size, settings.thumb_size), Image.Resampling.LANCZOS)
        if not out.exists():
            img.save(out, "JPEG", quality=85)
    return out, w, h


def _l2(x: torch.Tensor) -> torch.Tensor:
    return x / x.norm(dim=-1, keepdim=True).clamp(min=1e-8)


class ClipEncoder:
    def __init__(self) -> None:
        state = load_clip()
        self.model = state["model"]
        self.preprocess = state["preprocess"]
        self.tokenizer = state["tokenizer"]
        self.device: torch.device = state["device"]
        self._scene_text = self._encode_text(SCENE_PROMPTS)

    @torch.inference_mode()
    def _encode_text(self, prompts: list[str]) -> torch.Tensor:
        tokens = self.tokenizer(prompts).to(self.device)
        feats = self.model.encode_text(tokens)
        return _l2(feats.float())

    @torch.inference_mode()
    def encode_images(self, pil_images: list[Image.Image]) -> torch.Tensor:
        batch = torch.stack([self.preprocess(img) for img in pil_images]).to(self.device)
        if settings.clip_fp16 and self.device.type == "cuda":
            batch = batch.half()
        feats = self.model.encode_image(batch)
        return _l2(feats.float())

    @torch.inference_mode()
    def encode_query(self, text: str) -> np.ndarray:
        return self._encode_text([text])[0].cpu().numpy().astype(np.float32)

    def zero_shot_scene(self, img_feats: torch.Tensor) -> list[str]:
        sims = (img_feats @ self._scene_text.T).cpu().numpy()
        idx = sims.argmax(axis=1)
        return [SCENE_LABELS[i] for i in idx]


def run_hot_batch(
    paths: Iterable[Path], encoder: ClipEncoder, batch_size: int | None = None
) -> list[HotResult]:
    """Run the hot pipeline on a list of file paths. Returns one HotResult per path."""
    batch_size = batch_size or settings.clip_batch_size
    results: list[HotResult] = []
    buf_paths: list[Path] = []
    buf_images: list[Image.Image] = []
    buf_meta: list[dict] = []

    def flush() -> None:
        if not buf_images:
            return
        feats = encoder.encode_images(buf_images)
        scenes = encoder.zero_shot_scene(feats)
        feats_np = feats.cpu().numpy().astype(np.float32)
        for i, (p, meta) in enumerate(zip(buf_paths, buf_meta)):
            results.append(
                HotResult(
                    sha256=meta["sha"],
                    path=str(p),
                    thumb_path=str(meta["thumb"]),
                    width=meta["w"],
                    height=meta["h"],
                    taken_at=meta["exif"].get("taken_at"),
                    latitude=meta["exif"].get("lat"),
                    longitude=meta["exif"].get("lon"),
                    camera=meta["exif"].get("camera"),
                    embedding=feats_np[i],
                    scene=scenes[i],
                )
            )
        for img in buf_images:
            img.close()
        buf_paths.clear()
        buf_images.clear()
        buf_meta.clear()

    for p in paths:
        try:
            sha = sha256_file(p)
            thumb, w, h = make_thumbnail(p, sha)
            exif = read_exif(p)
            pil = Image.open(thumb).convert("RGB")
        except Exception as e:
            log.warning("skipping %s: %s", p, e)
            continue
        buf_paths.append(p)
        buf_images.append(pil)
        buf_meta.append({"sha": sha, "thumb": thumb, "w": w, "h": h, "exif": exif})
        if len(buf_images) >= batch_size:
            flush()
    flush()
    return results
