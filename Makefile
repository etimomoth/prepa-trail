.PHONY: help install install-backend install-frontend dev backend frontend lint format test test-backend test-frontend seed clean

help:
	@echo "Photos AI - common targets"
	@echo "  make install           Install backend + frontend deps"
	@echo "  make dev               Run backend and frontend together"
	@echo "  make backend           Run FastAPI (uvicorn)"
	@echo "  make frontend          Run Nuxt dev server"
	@echo "  make lint              Ruff + TypeScript checks"
	@echo "  make format            Black + ruff --fix"
	@echo "  make test              Backend + frontend tests"
	@echo "  make seed              Generate test photos"
	@echo "  make clean             Remove caches and generated data"

install: install-backend install-frontend

install-backend:
	cd backend && pip install -e ".[dev]"

install-frontend:
	cd frontend && npm install

dev:
	@echo "Start backend and frontend in two terminals:"
	@echo "  make backend"
	@echo "  make frontend"

backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

lint:
	cd backend && ruff check app tests
	cd frontend && npm run typecheck

format:
	cd backend && ruff check --fix app tests && black app tests

test: test-backend test-frontend

test-backend:
	cd backend && pytest -q

test-frontend:
	cd frontend && npm test --silent

seed:
	cd backend && python ../scripts/seed_test_photos.py

clean:
	rm -rf backend/.pytest_cache backend/.ruff_cache backend/.mypy_cache
	rm -rf frontend/.nuxt frontend/.output frontend/node_modules/.cache
	rm -rf data/.cache
