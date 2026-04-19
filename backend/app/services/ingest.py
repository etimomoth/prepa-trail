from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.faiss_index import store as faiss_store
from app.core.logging import get_logger
from app.ml.hot_pipeline import ClipEncoder, HotResult, run_hot_batch
from app.models.db_models import Job, Photo

log = get_logger(__name__)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".tif", ".tiff", ".bmp"}


def scan_folder(folder: Path, recursive: bool = True) -> list[Path]:
    folder = folder.expanduser().resolve()
    if not folder.exists():
        raise FileNotFoundError(folder)
    it = folder.rglob("*") if recursive else folder.glob("*")
    return sorted(p for p in it if p.is_file() and p.suffix.lower() in IMAGE_EXTS)


def _existing_shas(session: Session) -> set[str]:
    return set(session.scalars(select(Photo.sha256)).all())


def persist_hot(session: Session, results: list[HotResult]) -> list[Photo]:
    """Insert new photos, ignoring those already present (sha256 unique)."""
    existing = _existing_shas(session)
    photos: list[Photo] = []
    vectors: list[np.ndarray] = []
    for r in results:
        if r.sha256 in existing:
            continue
        existing.add(r.sha256)
        ph = Photo(
            sha256=r.sha256,
            path=r.path,
            thumb_path=r.thumb_path,
            width=r.width,
            height=r.height,
            taken_at=r.taken_at,
            camera=r.camera,
            latitude=r.latitude,
            longitude=r.longitude,
            scene=r.scene,
        )
        session.add(ph)
        photos.append(ph)
        vectors.append(r.embedding)
    session.flush()
    if vectors:
        ids = np.array([p.id for p in photos], dtype=np.int64)
        vecs = np.vstack(vectors).astype(np.float32)
        faiss_store.add(ids, vecs)
        faiss_store.save()
    session.commit()
    return photos


def run_ingest_job(session: Session, job: Job, folder: Path, recursive: bool = True) -> int:
    """Runs hot pipeline on every image under folder. Returns count of new photos."""
    settings.ensure_dirs()
    paths = scan_folder(folder, recursive=recursive)
    existing = _existing_shas(session)

    job.total = len(paths)
    job.status = "running"
    session.commit()

    encoder = ClipEncoder()
    BATCH = settings.clip_batch_size
    new_count = 0

    for start in range(0, len(paths), BATCH):
        chunk = paths[start : start + BATCH]
        results = run_hot_batch(chunk, encoder, batch_size=BATCH)
        fresh = [r for r in results if r.sha256 not in existing]
        if fresh:
            persist_hot(session, fresh)
            existing.update(r.sha256 for r in fresh)
            new_count += len(fresh)
        job.progress = float(min(start + len(chunk), len(paths)))
        session.commit()
        log.info("ingest progress: %d/%d (+%d new)", int(job.progress), job.total, new_count)

    job.status = "done"
    job.ended_at = datetime.utcnow()
    job.message = f"{new_count} new photos"
    session.commit()
    return new_count
