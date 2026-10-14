.PHONY: setup dev seed train test test-backend test-frontend e2e lint fmt api-types demo docker-up

BACKEND := backend
FRONTEND := frontend
VENV := $(BACKEND)/.venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

setup:
	cd $(BACKEND) && python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -e "$(BACKEND)[dev]"
	cd $(FRONTEND) && npm install

dev:
	@echo "Starting backend (:8000) and frontend (:5173)..."
	@( cd $(BACKEND) && .venv/bin/uvicorn app.main:app --reload --port 8000 & \
	   cd $(FRONTEND) && npm run dev -- --port 5173 & \
	   wait )

seed:
	cd $(BACKEND) && .venv/bin/python -m app.seed --reset

train:
	cd $(BACKEND) && .venv/bin/python -m app.services.predictive.train

test: test-backend test-frontend

test-backend:
	cd $(BACKEND) && .venv/bin/pytest -q

test-frontend:
	cd $(FRONTEND) && npm run test

e2e:
	cd $(FRONTEND) && npx playwright test

lint:
	cd $(BACKEND) && .venv/bin/ruff check app tests
	cd $(FRONTEND) && npm run lint

fmt:
	cd $(BACKEND) && .venv/bin/ruff format app tests
	cd $(FRONTEND) && npm run format

api-types:
	cd $(FRONTEND) && npx openapi-typescript http://localhost:8000/api/v1/openapi.json -o src/lib/api-types.ts

demo:
	cd $(BACKEND) && .venv/bin/python -m app.seed --reset
	$(MAKE) dev

docker-up:
	docker compose up --build
