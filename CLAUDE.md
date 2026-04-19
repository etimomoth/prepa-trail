# Photos AI — Brief Projet

## Objectif

Application 100% locale pour importer, analyser, classer et rechercher
une bibliothèque photo personnelle. Vision par ordinateur + recherche
sémantique CLIP. Pas de cloud, priorité vie privée.

## Contrainte de performance

- Ingestion cible: 1000 photos/minute sur GPU (RTX 3060+ ou équivalent).
- Budget: ~60 ms/photo en passe "hot" (CLIP only).
- Enrichissements (BLIP captioning, YOLO détection) en passe "cold" background.

## Stack

- **Backend**: Python 3.11, FastAPI, PyTorch 2.x, open_clip_torch, FAISS, SQLite (WAL mode)
- **Frontend**: Nuxt 3, Vue 3, TypeScript, Tailwind CSS, Pinia, @vueuse/core
- **GPU**: CUDA prioritaire, MPS (Mac Apple Silicon) fallback, CPU dernier recours
- **Async**: asyncio + ThreadPoolExecutor pour I/O, jobs avec SSE (Server-Sent Events)
- **ORM**: SQLAlchemy 2.x + Alembic migrations

## Architecture

Deux pipelines ML séparés :

1. **HOT** (GPU, bloquant avant 1er affichage) :
   hash SHA256 → EXIF → thumbnail 512px → CLIP ViT-B/32 FP16 batch 64
   → classif zero-shot scène → insertion SQLite + ajout FAISS.
2. **COLD** (background, non bloquant, démarre après la passe hot) :
   BLIP captioning → YOLOv8n détection objets → score qualité
   (Laplacian pour flou + histogram pour expo) → dédup near-duplicate.

Clustering événements : HDBSCAN sur features combinées
`[emb_clip*1.0 || timestamp_normalisé*0.5 || gps*0.3]` déclenché après
la passe hot. Nommage de cluster : top objets détectés + scène dominante
+ range de dates + ville (reverse geocoding Nominatim si dispo).

## Règles de code

- **Python** : type hints partout, pydantic v2 pour les schémas API, ruff + black.
- **Vue** : Composition API uniquement, `<script setup lang="ts">`, pas d'Options API.
- **Filesystem** : JAMAIS de copie de photos, uniquement symlinks pour l'arborescence générée.
- **Idempotence** : réimporter les mêmes photos = 0 calcul ML (check SHA256).
- **Secrets** : pas de secret en dur, tout via `.env` chargé par pydantic-settings.
- **Tests** : pytest pour backend, vitest pour front. Au moins un test par module core.

## Structure attendue

```
photos-ai/
├── backend/
│   ├── app/
│   │   ├── api/          # routes FastAPI (ingest, search, clusters, jobs)
│   │   ├── core/         # config, db session, faiss index, logging
│   │   ├── ml/           # hot_pipeline, cold_pipeline, models loading
│   │   ├── services/     # ingest, clustering, search, dedup, naming
│   │   └── models/       # sqlalchemy models + pydantic schemas
│   ├── tests/
│   ├── alembic/          # migrations DB
│   └── pyproject.toml
├── frontend/
│   ├── components/       # PhotoGrid, Dropzone, ProgressBar, SearchBar
│   ├── composables/      # useIngest, useSearch, useJobs
│   ├── pages/            # index, clusters, timeline
│   ├── stores/           # photos, jobs (Pinia)
│   ├── nuxt.config.ts
│   └── package.json
├── data/                 # gitignored: photos/, thumbs/, faiss.index, app.db
├── scripts/              # seed_test_photos.py, benchmark.py
├── Makefile
├── docker-compose.yml    # optionnel, seulement pour V1+
├── ROADMAP.md
└── CLAUDE.md
```

## Workflow git

- Branche `main` protégée.
- Feature branches : `feat/xxx`, `fix/xxx`, `chore/xxx`.
- **Commits conventionnels** : `feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`.
- Avant tout commit : lancer `make lint && make test`.

## Priorités

**MVP d'abord.** Ne pas sur-ingénierer :

- Pas de Kafka, Redis, RabbitMQ au début.
- SQLite + FAISS en local suffisent pour < 100k photos.
- Celery/Redis seulement si mesuré nécessaire (V2+).
- Un seul processus Python au départ, FastAPI + BackgroundTasks.

## Ce que tu ne fais JAMAIS sans me demander explicitement

- Supprimer des fichiers en dehors de `data/.cache/`
- Faire `git push --force` ou `git reset --hard` sur un commit déjà pushé
- Modifier `CLAUDE.md` ou `ROADMAP.md`
- Télécharger des modèles > 5 GB
- Installer des dépendances système (apt, brew, choco)
- Ouvrir une PR ou merger sur main

## Style de communication

- Explique ton plan AVANT de coder quand la tâche fait > 50 lignes.
- Résume ce que tu as fait en fin de tâche (fichiers modifiés, tests lancés, résultat).
- Si tu hésites entre deux approches, pose-moi la question, ne choisis pas tout seul.
- Si un test échoue que tu ne comprends pas, stop et montre-moi le traceback.
