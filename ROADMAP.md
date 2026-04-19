# Roadmap

## MVP (current)

- [x] Backend scaffolding: FastAPI app, config, logging, SQLite WAL, FAISS store
- [x] SQLAlchemy models: `Photo`, `Cluster`, `Detection`, `Job`
- [x] Hot pipeline: SHA256, EXIF, thumbnails, CLIP ViT-B/32 (FP16 on CUDA),
      zero-shot scene
- [x] Ingest service + background job with progress persisted in DB
- [x] HDBSCAN clustering on `[clip || time || gps]` (weighted)
- [x] Text search endpoint (CLIP text → FAISS inner product)
- [x] Cluster naming from dominant scene + date range
- [x] Frontend: Nuxt 3, Pinia stores, pages for ingest / clusters / timeline / search
- [x] SSE progress stream for ingest jobs
- [x] Basic tests: hash, scan, clustering label, quality score

## V1

- [ ] Cold pipeline wiring with BackgroundTasks after hot pass completes
- [ ] Near-duplicate dedup using FAISS neighbors + pHash
- [ ] Alembic initial migration (currently using `create_all`)
- [ ] Reverse geocoding integration into cluster naming
- [ ] Interactive cluster editing: rename, split, merge
- [ ] Filters: date range, scene, has GPS, quality threshold
- [ ] Persistent timeline view with virtualized scrolling
- [ ] Benchmark script hitting 1000 photos/min target on RTX 3060+

## V2+

- [ ] Face clustering (opt-in, local only)
- [ ] "People" view
- [ ] Export: generate symlink trees by cluster
- [ ] Multi-process ingestion if > 100k photos
- [ ] Optional Celery/Redis only if measured necessary
- [ ] Desktop packaging (Tauri or similar)

## Known limits of the MVP

- Ingest reads a server-side folder path (browser can't send a folder path
  securely). V1 will add drag-and-drop upload for files + a folder picker
  variant.
- HDBSCAN min_cluster_size is static; small libraries may produce mostly noise.
- No auth. The backend is meant to run locally.
- Thumbnails are JPEG 85; no format selection per source type.
