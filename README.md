# VAYU-COP

AI decision support for dynamic air operations & resource optimisation.

> SIH 2026 · Problem Statement ID 26250 — "Air Power: Dynamic Air Operations & Resource Optimisation"
> Ministry of Defence (MoD) · Defence Services Staff College

This is a prototype built against **[IMPLEMENTATION.md](IMPLEMENTATION.md)**, the single source of
truth for scope, architecture, data model, API contract, UI spec and the phase-by-phase build plan.
Progress is tracked in **[PROGRESS.md](PROGRESS.md)**; agent build rules are in **[AGENTS.md](AGENTS.md)**
/ **[CLAUDE.md](CLAUDE.md)**.

All data in this system is **synthetic** (fictional exercise "VAYU SHIELD"). No real unit, basing,
threat or performance data is used.

## Quick start

```bash
cp .env.example .env
make setup   # installs backend (Python venv) and frontend (npm) dependencies
make dev     # backend on http://localhost:8000, frontend on http://localhost:5173
```

Or with Docker:

```bash
cp .env.example .env
docker compose up --build
```

Check the backend is up:

```bash
curl http://localhost:8000/api/v1/health
# {"status":"ok","version":"0.1.0"}
```

## Repository layout

See [IMPLEMENTATION.md §5](IMPLEMENTATION.md#5-repository-layout) for the full target layout.

```text
backend/    FastAPI + SQLAlchemy + OR-Tools backend
frontend/   React + Vite + TypeScript frontend
docs/       architecture notes, demo script, UI reference image
```

## Common commands

| Command | What it does |
|---|---|
| `make setup` | Install backend + frontend dependencies |
| `make dev` | Run backend and frontend dev servers together |
| `make seed` | Populate the database with the synthetic exercise scenario |
| `make test` | Run backend (pytest) and frontend (vitest) test suites |
| `make lint` | Run ruff (backend) and eslint (frontend) |
| `make docker-up` | Run the full stack via Docker Compose |
