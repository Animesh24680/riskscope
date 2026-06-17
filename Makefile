.PHONY: help install run test docker-build docker-up clean

help:
	@echo "Usage:"
	@echo "  make install     - Install Python dependencies"
	@echo "  make run         - Run the backend server locally"
	@echo "  make test        - Run tests"
	@echo "  make docker-build - Build Docker images"
	@echo "  make docker-up   - Start all services with Docker Compose"
	@echo "  make clean       - Clean cache and temp files"

install:
	cd backend && pip install -r requirements.txt

run:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	cd backend && python -m pytest tests/ -v --tb=short

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
