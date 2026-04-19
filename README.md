# photos-ai

Local-first photo library with CLIP-based semantic search and automatic event
clustering. Drop photos in the browser → they're embedded, clustered, and
searchable.

## Quick start

Two terminals.

```bash
# Terminal 1 — backend
cd backend
cp .env.example .env          # optional, defaults work
pip install -e ".[dev]"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

```bash
# Terminal 2 — frontend
cd frontend
cp .env.example .env          # optional
npm install
npm run dev
```

Open <http://localhost:3000>, drag a folder of photos onto the dropzone.
The backend hashes, embeds with CLIP, and auto-clusters them. Then:

- `/` — drop photos, watch progress
- `/clusters` — browse event clusters (auto-named from scene + dates)
- `/search` — type natural-language queries ("sunset over the ocean",
  "a bird on a branch")
- `/timeline` — clusters grouped by year

The first ingest downloads the CLIP ViT-B/32 weights (~580 MB) from Hugging
Face into `~/.cache/huggingface/`. Subsequent runs are offline.

## GPU

CUDA is used automatically when available. On Apple Silicon, PyTorch MPS is
used. CPU is the fallback; expect ~0.5 s/photo on CPU vs. ~60 ms/photo on an
RTX 3060+.

## Architecture

Two pipelines:

- **HOT** (blocks first display):
  `SHA256 → EXIF → thumbnail 512px → CLIP ViT-B/32 → zero-shot scene → SQLite + FAISS`
- **COLD** (background, stubs wired, BLIP/YOLO lazy-imported): captioning,
  detection, quality score.

Clustering: HDBSCAN on `[clip*1.0 || time*0.5 || gps*0.3]`, re-run
automatically at the end of every ingest job.

Storage:

- SQLite (WAL) for metadata
- FAISS `IndexIDMap(IndexFlatIP)` for embeddings (L2-normalized, so inner
  product = cosine similarity)
- Thumbnails on disk under `data/thumbs/`
- Uploaded photos kept under `data/photos/uploads/<batch>/`; originals from
  a scanned folder are referenced in place, never copied.

## Layout

```
photos-ai/
├── backend/              FastAPI + ML
├── frontend/             Nuxt 3 + Pinia + Tailwind
├── data/                 photos, thumbs, faiss.index, app.db (gitignored)
├── scripts/              seed_test_photos.py, seed_birds.py, benchmark.py
├── Makefile
├── ROADMAP.md
└── CLAUDE.md
```

## Dev tips

- `make test` runs the backend pytest suite.
- `python scripts/seed_birds.py` downloads 25 real bird photos into
  `data/photos/birds/` for pipeline validation.
- `POST /ingest` still accepts a server-side folder path for bulk imports
  (useful for large libraries where a browser upload isn't practical).

See `ROADMAP.md` for what's next (near-dup dedup, cold pipeline wiring,
cluster editing).
