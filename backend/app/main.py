from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import clusters, ingest, jobs, search
from app.core.config import settings
from app.core.db import engine
from app.core.faiss_index import store as faiss_store
from app.core.logging import configure_logging, get_logger
from app.models.db_models import Base

log = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    settings.ensure_dirs()
    Base.metadata.create_all(engine)
    faiss_store.load()
    log.info("photos-ai backend ready; index size=%d", faiss_store.size)
    yield
    faiss_store.save()


app = FastAPI(title="Photos AI", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings.ensure_dirs()
app.mount("/thumbs", StaticFiles(directory=str(settings.thumbs_dir)), name="thumbs")

app.include_router(ingest.router)
app.include_router(search.router)
app.include_router(clusters.router)
app.include_router(jobs.router)


@app.get("/health")
def health() -> dict[str, str | int]:
    return {"status": "ok", "index_size": faiss_store.size}
