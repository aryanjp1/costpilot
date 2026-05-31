.PHONY: up down logs migrate seed test test-sdk test-backend backend frontend

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

migrate:
	cd backend && alembic upgrade head

seed:
	cd scripts && python seed.py

test: test-sdk test-backend

test-sdk:
	cd sdk/python && python -m pytest -q

test-backend:
	cd backend && python -m pytest -q

backend:
	cd backend && uvicorn app.main:app --reload --port 8787

frontend:
	cd frontend && npm run dev
