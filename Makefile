.PHONY: help install run test docker-build docker-up docker-down clean dev migrate

help:
	@echo "Usage:"
	@echo "  make install       - Install Python dependencies"
	@echo "  make npm-install   - Install frontend/root npm dependencies"
	@echo "  make dev           - Run backend + frontend concurrently (hot reload)"
	@echo "  make dev-api       - Run backend only"
	@echo "  make dev-web       - Run frontend only (Vite)"
	@echo "  make test          - Run tests"
	@echo "  make build         - Build frontend for production"
	@echo "  make migrate       - Run Alembic migrations"
	@echo "  make migrate-new   - Create a new migration (Alembic autogenerate)"
	@echo "  make docker-build  - Build Docker images"
	@echo "  make docker-up     - Start all services with Docker Compose"
	@echo "  make docker-down   - Stop Docker Compose services"
	@echo "  make clean         - Clean cache and temp files"

install:
	cd backend && pip install -r requirements.txt

npm-install:
	npm install && cd frontend && npm install

dev:
	npm run dev

dev-api:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-web:
	cd frontend && npx vite

test:
	cd backend && python -m pytest tests/ -v --tb=short

build:
	cd frontend && npx vite build

migrate:
	cd backend && alembic upgrade head

migrate-new:
	cd backend && alembic revision --autogenerate

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf frontend/dist node_modules frontend/node_modules
