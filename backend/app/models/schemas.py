from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PhotoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sha256: str
    path: str
    thumb_path: str | None = None
    width: int | None = None
    height: int | None = None
    taken_at: datetime | None = None
    latitude: float | None = None
    longitude: float | None = None
    scene: str | None = None
    caption: str | None = None
    quality_score: float | None = None
    cluster_id: int | None = None


class ClusterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    label: str
    scene: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    place: str | None = None
    photo_count: int
    cover_photo_id: int | None = None


class IngestRequest(BaseModel):
    folder: str = Field(..., description="Absolute or relative folder to scan recursively.")
    recursive: bool = True


class IngestResponse(BaseModel):
    job_id: int
    scheduled: int


class SearchRequest(BaseModel):
    query: str
    k: int = 20


class SearchHit(BaseModel):
    photo: PhotoOut
    score: float


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: str
    status: str
    progress: float
    total: int
    message: str | None = None
    started_at: datetime
    ended_at: datetime | None = None
