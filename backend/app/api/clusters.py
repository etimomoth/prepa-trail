from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import SessionLocal, get_session
from app.models.db_models import Cluster, Photo
from app.models.schemas import ClusterOut, PhotoOut

router = APIRouter(prefix="/clusters", tags=["clusters"])


def _run_recluster() -> None:
    from app.services.clustering import recluster

    with SessionLocal() as session:
        recluster(session)


@router.post("/recluster")
def trigger_recluster(background: BackgroundTasks) -> dict[str, str]:
    background.add_task(_run_recluster)
    return {"status": "scheduled"}


@router.get("", response_model=list[ClusterOut])
def list_clusters(session: Session = Depends(get_session)) -> list[ClusterOut]:
    rows = session.scalars(select(Cluster).order_by(Cluster.start_date.desc())).all()
    return [ClusterOut.model_validate(c) for c in rows]


@router.get("/{cluster_id}/photos", response_model=list[PhotoOut])
def cluster_photos(
    cluster_id: int, session: Session = Depends(get_session)
) -> list[PhotoOut]:
    cluster = session.get(Cluster, cluster_id)
    if cluster is None:
        raise HTTPException(404, "cluster not found")
    photos = session.scalars(
        select(Photo).where(Photo.cluster_id == cluster_id).order_by(Photo.taken_at)
    ).all()
    return [PhotoOut.model_validate(p) for p in photos]
