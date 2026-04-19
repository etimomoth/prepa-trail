from __future__ import annotations

import uuid
from pathlib import Path

import aiofiles
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import SessionLocal, get_session
from app.core.logging import get_logger
from app.models.db_models import Job
from app.models.schemas import IngestRequest, IngestResponse
from app.services.ingest import IMAGE_EXTS, run_ingest_job, scan_folder

log = get_logger(__name__)
router = APIRouter(prefix="/ingest", tags=["ingest"])

UPLOAD_SUBDIR = "uploads"


def _run(job_id: int, folder: str, recursive: bool) -> None:
    with SessionLocal() as session:
        job = session.get(Job, job_id)
        if job is None:
            return
        try:
            run_ingest_job(session, job, Path(folder), recursive=recursive)
        except Exception as e:
            log.exception("ingest job %s crashed", job_id)
            job.status = "error"
            job.message = str(e)
            session.commit()
            return

    # Chain clustering after ingest completes so the UI sees named clusters.
    try:
        from app.services.clustering import recluster

        with SessionLocal() as session:
            recluster(session)
    except Exception:
        log.exception("auto-recluster after job %s failed", job_id)


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


@router.post("/upload", response_model=IngestResponse)
async def upload_files(
    background: BackgroundTasks,
    files: list[UploadFile] = File(...),
    session: Session = Depends(get_session),
) -> IngestResponse:
    """Accept a batch of browser-uploaded image files and ingest them."""
    if not files:
        raise HTTPException(400, "no files")
    settings.ensure_dirs()
    batch_dir = settings.photos_dir / UPLOAD_SUBDIR / uuid.uuid4().hex[:12]
    batch_dir.mkdir(parents=True, exist_ok=True)

    saved = 0
    for upload in files:
        name = Path(upload.filename or "upload.bin").name
        ext = Path(name).suffix.lower()
        if ext not in IMAGE_EXTS:
            continue
        dest = batch_dir / name
        async with aiofiles.open(dest, "wb") as f:
            while chunk := await upload.read(1 << 20):
                await f.write(chunk)
        saved += 1

    if saved == 0:
        raise HTTPException(400, "no usable images in upload")

    job = Job(kind="ingest", status="pending", total=saved)
    session.add(job)
    session.commit()
    session.refresh(job)
    background.add_task(_run, job.id, str(batch_dir), True)
    return IngestResponse(job_id=job.id, scheduled=saved)
