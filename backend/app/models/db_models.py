from __future__ import annotations

from datetime import datetime

from sqlalchemy import Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Photo(Base):
    __tablename__ = "photos"
    __table_args__ = (UniqueConstraint("sha256", name="uq_photos_sha256"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sha256: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    path: Mapped[str] = mapped_column(Text, nullable=False)
    thumb_path: Mapped[str | None] = mapped_column(Text)

    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    taken_at: Mapped[datetime | None] = mapped_column(index=True)
    camera: Mapped[str | None] = mapped_column(String(255))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)

    quality_score: Mapped[float | None] = mapped_column(Float)
    caption: Mapped[str | None] = mapped_column(Text)
    scene: Mapped[str | None] = mapped_column(String(128))

    cluster_id: Mapped[int | None] = mapped_column(ForeignKey("clusters.id"), index=True)
    cluster: Mapped["Cluster | None"] = relationship("Cluster", back_populates="photos")

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class Cluster(Base):
    __tablename__ = "clusters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    label: Mapped[str] = mapped_column(String(255), default="unnamed")
    scene: Mapped[str | None] = mapped_column(String(128))
    start_date: Mapped[datetime | None] = mapped_column()
    end_date: Mapped[datetime | None] = mapped_column()
    place: Mapped[str | None] = mapped_column(String(255))
    photo_count: Mapped[int] = mapped_column(Integer, default=0)
    cover_photo_id: Mapped[int | None] = mapped_column(ForeignKey("photos.id"))

    photos: Mapped[list[Photo]] = relationship(
        "Photo",
        back_populates="cluster",
        foreign_keys=[Photo.cluster_id],
    )


class Detection(Base):
    __tablename__ = "detections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    photo_id: Mapped[int] = mapped_column(ForeignKey("photos.id", ondelete="CASCADE"), index=True)
    label: Mapped[str] = mapped_column(String(64), index=True)
    score: Mapped[float] = mapped_column(Float)
    bbox: Mapped[str] = mapped_column(String(64))  # "x,y,w,h"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kind: Mapped[str] = mapped_column(String(32))  # ingest|cluster|cold
    status: Mapped[str] = mapped_column(String(16), default="pending")
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    total: Mapped[int] = mapped_column(Integer, default=0)
    message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column()
