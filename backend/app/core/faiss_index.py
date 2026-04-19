from __future__ import annotations

import threading
from pathlib import Path

import faiss
import numpy as np

from app.core.config import settings
from app.core.logging import get_logger

log = get_logger(__name__)


class FaissStore:
    """IndexIDMap wrapped around an inner product index over L2-normalized vectors."""

    def __init__(self, dim: int, path: Path):
        self.dim = dim
        self.path = path
        self._lock = threading.RLock()
        self._index: faiss.IndexIDMap | None = None

    def _build(self) -> faiss.IndexIDMap:
        inner = faiss.IndexFlatIP(self.dim)
        return faiss.IndexIDMap(inner)

    def load(self) -> None:
        with self._lock:
            if self.path.exists():
                log.info("loading faiss index from %s", self.path)
                self._index = faiss.read_index(str(self.path))
            else:
                log.info("creating new faiss index dim=%d", self.dim)
                self._index = self._build()

    def save(self) -> None:
        with self._lock:
            if self._index is None:
                return
            self.path.parent.mkdir(parents=True, exist_ok=True)
            faiss.write_index(self._index, str(self.path))

    def add(self, ids: np.ndarray, vectors: np.ndarray) -> None:
        if vectors.size == 0:
            return
        assert vectors.shape[1] == self.dim, f"expected dim={self.dim}, got {vectors.shape[1]}"
        with self._lock:
            if self._index is None:
                self.load()
            assert self._index is not None
            self._index.add_with_ids(vectors.astype(np.float32), ids.astype(np.int64))

    def search(self, query: np.ndarray, k: int = 20) -> tuple[np.ndarray, np.ndarray]:
        with self._lock:
            if self._index is None:
                self.load()
            assert self._index is not None
            if self._index.ntotal == 0:
                return np.zeros((0,), dtype=np.int64), np.zeros((0,), dtype=np.float32)
            q = query.astype(np.float32).reshape(1, -1)
            dists, ids = self._index.search(q, k)
            return ids[0], dists[0]

    @property
    def size(self) -> int:
        with self._lock:
            return 0 if self._index is None else int(self._index.ntotal)


store = FaissStore(dim=settings.faiss_dim, path=settings.faiss_index_path)
