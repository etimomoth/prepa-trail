from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import SessionLocal, get_session
from app.models.db_models import Job
from app.models.schemas import IngestRequest, IngestResponse
from app.services.ingest import run_ingest_job, scan_folder

router = APIRouter(prefix="/ingest", tags=["ingest"])


def _run(job_id: int, folder: str, recursive: bool) -> None:
    with SessionLocal() as session:
        job = session.get(Job, job_id)
        if job is None:
            return
        try:
            run_ingest_job(session, job, Path(folder), recursive=recursive)
        except Exception as e:
            job.status = "error"
            job.message = str(e)
            session.commit()


@router.post("", response_model=IngestResponse)
def start_ingest(
    req: IngestRequest,
    background: BackgroundTasks,
    session: Session = Depends(get_session),
) -> IngestResponse:
    folder = Path(req.folder).expanduser()
    if not folder.exists():
        raise HTTPException(404, f"folder not found: {folder}")
    paths = scan_folder(folder, recursive=req.recursive)
    job = Job(kind="ingest", status="pending", total=len(paths))
    session.add(job)
    session.commit()
    session.refresh(job)
    background.add_task(_run, job.id, str(folder), req.recursive)
    return IngestResponse(job_id=job.id, scheduled=len(paths))
