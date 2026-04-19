from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "photos-ai"
    data_dir: Path = Field(default=Path("../data"))
    db_url: str = "sqlite:///../data/app.db"

    clip_model: str = "ViT-B-32"
    clip_pretrained: str = "laion2b_s34b_b79k"
    clip_batch_size: int = 64
    clip_fp16: bool = True

    thumb_size: int = 512
    hot_workers: int = 4

    faiss_dim: int = 512
    faiss_index_path: Path = Field(default=Path("../data/faiss.index"))

    hdbscan_min_cluster_size: int = 4
    cluster_weight_clip: float = 1.0
    cluster_weight_time: float = 0.5
    cluster_weight_gps: float = 0.3

    nominatim_url: str | None = None
    cors_origins: list[str] = ["http://localhost:3000"]

    @property
    def photos_dir(self) -> Path:
        return self.data_dir / "photos"

    @property
    def thumbs_dir(self) -> Path:
        return self.data_dir / "thumbs"

    @property
    def cache_dir(self) -> Path:
        return self.data_dir / ".cache"

    def ensure_dirs(self) -> None:
        for p in (self.data_dir, self.photos_dir, self.thumbs_dir, self.cache_dir):
            p.mkdir(parents=True, exist_ok=True)


settings = Settings()
