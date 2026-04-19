from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.models.schemas import PhotoOut, SearchHit, SearchRequest
from app.services.search import search_text

router = APIRouter(prefix="/search", tags=["search"])


@router.post("", response_model=list[SearchHit])
def search(req: SearchRequest, session: Session = Depends(get_session)) -> list[SearchHit]:
    hits = search_text(session, req.query, k=req.k)
    return [SearchHit(photo=PhotoOut.model_validate(p), score=s) for p, s in hits]
