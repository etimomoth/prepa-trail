# photos-ai

Local-first photo library with CLIP-based semantic search and automatic event
clustering. Drop a folder, get clusters.

## Quick start

```bash
# 1. backend
cd backend
cp .env.example .env
pip install -e ".[dev]"
uvicorn app.main:app --reload

# 2. frontend (in another shell)
cd frontend
cp .env.example .env
npm install
npm run dev
```

Open <http://localhost:3000> and paste the absolute path to a folder of photos.

## Architecture

Two pipelines:

- **HOT** (GPU, blocks first display):
  `SHA256 → EXIF → thumbnail 512px → CLIP ViT-B/32 → zero-shot scene → SQLite + FAISS`
- **COLD** (background, optional): BLIP captioning, YOLO detection, quality
  scoring, near-dup dedup.

Clustering: HDBSCAN on `[clip || time || gps]` (weighted), run after the hot
pass completes.

Storage:

- SQLite (WAL) for metadata
- FAISS `IndexIDMap(IndexFlatIP)` for embeddings
- Thumbnails on disk; originals are never copied.

## Layout

```
photos-ai/
├── backend/              FastAPI + ML
├── frontend/             Nuxt 3 + Pinia + Tailwind
├── data/                 photos, thumbs, faiss.index, app.db (gitignored)
├── scripts/              seed, benchmarks
├── Makefile
└── ROADMAP.md
```

See `CLAUDE.md` for the full design brief and `ROADMAP.md` for status.
