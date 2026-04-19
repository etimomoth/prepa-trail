from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

from app.core.db import SessionLocal, get_session
from app.models.db_models import Job
from app.models.schemas import JobOut

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobOut])
def list_jobs(session: Session = Depends(get_session)) -> list[JobOut]:
    rows = session.scalars(select(Job).order_by(Job.id.desc()).limit(50)).all()
    return [JobOut.model_validate(j) for j in rows]


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, session: Session = Depends(get_session)) -> JobOut:
    job = session.get(Job, job_id)
    if job is None:
        raise HTTPException(404, "job not found")
    return JobOut.model_validate(job)


@router.get("/{job_id}/events")
async def stream_job(job_id: int) -> EventSourceResponse:
    async def emit():
        while True:
            with SessionLocal() as session:
                job = session.get(Job, job_id)
                if job is None:
                    yield {"event": "error", "data": json.dumps({"error": "not found"})}
                    return
                payload = JobOut.model_validate(job).model_dump(mode="json")
                yield {"event": "progress", "data": json.dumps(payload)}
                if job.status in {"done", "error"}:
                    return
            await asyncio.sleep(0.5)

    return EventSourceResponse(emit())
