"""Event clustering on combined CLIP + time + GPS features."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.models.db_models import Cluster, Photo

log = get_logger(__name__)


def _time_feature(taken: datetime | None) -> float:
    if taken is None:
        return 0.0
    epoch = taken.replace(tzinfo=timezone.utc).timestamp()
    return epoch / 86400.0  # days


def _normalize(x: np.ndarray) -> np.ndarray:
    if x.size == 0:
        return x
    mean = x.mean(axis=0, keepdims=True)
    std = x.std(axis=0, keepdims=True) + 1e-8
    return (x - mean) / std


def _stack_features(
    embs: np.ndarray, times: np.ndarray, gps: np.ndarray
) -> np.ndarray:
    t = _normalize(times.reshape(-1, 1)) * settings.cluster_weight_time
    g = _normalize(gps) * settings.cluster_weight_gps
    g = np.where(np.isnan(g), 0.0, g)
    return np.hstack([embs * settings.cluster_weight_clip, t, g]).astype(np.float32)


def _embedding_by_id(ids: list[int]) -> np.ndarray:
    from app.core.faiss_index import store as faiss_store

    if faiss_store._index is None:
        faiss_store.load()
    assert faiss_store._index is not None
    out = np.zeros((len(ids), settings.faiss_dim), dtype=np.float32)
    for i, pid in enumerate(ids):
        try:
            vec = faiss_store._index.reconstruct(int(pid))
            out[i] = vec
        except RuntimeError:
            # vector missing: leave zeros
            continue
    return out


def recluster(session: Session) -> list[Cluster]:
    """Re-run HDBSCAN on all photos and rewrite cluster assignments."""
    try:
        import hdbscan
    except ImportError as e:
        raise RuntimeError("hdbscan not installed") from e

    photos: list[Photo] = list(session.scalars(select(Photo)).all())
    if not photos:
        return []

    ids = [p.id for p in photos]
    embs = _embedding_by_id(ids)
    times = np.array([_time_feature(p.taken_at) for p in photos], dtype=np.float32)
    gps = np.array(
        [[p.latitude or np.nan, p.longitude or np.nan] for p in photos], dtype=np.float32
    )

    feats = _stack_features(embs, times, gps)
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=max(2, settings.hdbscan_min_cluster_size),
        metric="euclidean",
    )
    labels = clusterer.fit_predict(feats)
    log.info("HDBSCAN produced %d clusters (+ noise)", len({int(x) for x in labels if x >= 0}))

    # Wipe prior clusters; reassign fresh.
    for p in photos:
        p.cluster_id = None
    session.query(Cluster).delete()
    session.flush()

    by_label: dict[int, list[Photo]] = {}
    for p, lbl in zip(photos, labels):
        lbl_i = int(lbl)
        if lbl_i < 0:
            continue
        by_label.setdefault(lbl_i, []).append(p)

    created: list[Cluster] = []
    for lbl, members in sorted(by_label.items()):
        start = min((m.taken_at for m in members if m.taken_at), default=None)
        end = max((m.taken_at for m in members if m.taken_at), default=None)
        scene_top = Counter(m.scene for m in members if m.scene).most_common(1)
        scene = scene_top[0][0] if scene_top else None
        cluster = Cluster(
            label=_label_from(scene, start, end),
            scene=scene,
            start_date=start,
            end_date=end,
            photo_count=len(members),
            cover_photo_id=members[0].id,
        )
        session.add(cluster)
        session.flush()
        for m in members:
            m.cluster_id = cluster.id
        created.append(cluster)

    session.commit()
    return created


def _label_from(scene: str | None, start: datetime | None, end: datetime | None) -> str:
    parts: list[str] = []
    if scene:
        parts.append(scene)
    if start and end:
        if start.date() == end.date():
            parts.append(start.strftime("%Y-%m-%d"))
        else:
            parts.append(f"{start.strftime('%Y-%m-%d')} → {end.strftime('%Y-%m-%d')}")
    elif start:
        parts.append(start.strftime("%Y-%m-%d"))
    return " · ".join(parts) or "unnamed"
