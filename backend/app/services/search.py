from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.faiss_index import store as faiss_store
from app.ml.hot_pipeline import ClipEncoder
from app.models.db_models import Photo

_encoder: ClipEncoder | None = None


def _get_encoder() -> ClipEncoder:
    global _encoder
    if _encoder is None:
        _encoder = ClipEncoder()
    return _encoder


def search_text(session: Session, query: str, k: int = 20) -> list[tuple[Photo, float]]:
    vec = _get_encoder().encode_query(query)
    ids, dists = faiss_store.search(vec, k=k)
    if ids.size == 0:
        return []
    id_list = [int(i) for i in ids if i >= 0]
    photos = {
        p.id: p for p in session.scalars(select(Photo).where(Photo.id.in_(id_list))).all()
    }
    hits: list[tuple[Photo, float]] = []
    for pid, score in zip(ids.tolist(), dists.tolist()):
        if pid < 0 or pid not in photos:
            continue
        hits.append((photos[pid], float(score)))
    return hits
