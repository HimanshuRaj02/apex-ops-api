# apex-ops-api

A small incident-tracking API used to demonstrate a safe delivery pipeline: containerised app, Compose deployment, CI that blocks bad releases, versioned deploys with rollback, health checks and structured logs.

Stack: Python (Flask + gunicorn), PostgreSQL 16, Docker Compose, GitHub Actions.

## Architecture

~~~mermaid
flowchart LR
  C[Client / curl] -->|HTTP :8000| A[app container<br/>Flask + gunicorn<br/>non-root user]
  A -->|SQL| D[(db container<br/>Postgres 16)]
  D --- V[(pgdata volume)]
  G[GitHub push / PR] --> T[test: lint + pytest on real Postgres]
  T --> B[build + Trivy scan]
  B --> P[deploy smoke test on main only]
~~~

## Requirements

- Docker Engine with the Compose plugin (docker compose version must work)
- curl, git, bash

## Quick start

~~~bash
git clone https://github.com/HimanshuRaj02/apex-ops-api.git
cd apex-ops-api
cp .env.example .env        # dummy local values only; .env is git-ignored
docker compose up -d --build
docker compose ps           # app and db should both become healthy
curl -s localhost:8000/health
curl -s localhost:8000/ready
~~~

Stop with docker compose down. Do not add -v unless you want to delete the database volume.

## API

| Method | Path | Purpose |
|---|---|---|
| GET | /health | Liveness: process is up, returns the running version |
| GET | /ready | Readiness: 200 if the database is reachable, otherwise 503 |
| GET | /incidents | List incidents |
| POST | /incidents | Create one, JSON body: {"title": "...", "severity": "low or medium or high"} |

~~~bash
curl -s -X POST localhost:8000/incidents -H 'Content-Type: application/json' \
  -d '{"title":"disk full","severity":"high"}'
curl -s localhost:8000/incidents
~~~

Invalid input (empty title, unknown severity) returns 400.

## Tests and lint

Tests need a real Postgres. This starts a throwaway one and runs ruff and pytest in a Python 3.12 container:

~~~bash
docker run -d --name testdb -e POSTGRES_PASSWORD=test -p 5433:5432 postgres:16-alpine
sleep 8
docker run --rm --network host -v "$PWD":/w -w /w \
  -e DATABASE_URL=postgresql://postgres:test@localhost:5433/postgres \
  python:3.12-slim sh -c "pip install -q -r requirements.txt -r requirements-dev.txt && ruff check . && pytest -v -p no:cacheprovider"
docker rm -f testdb
~~~

## CI/CD (.github/workflows/ci.yml)

test (ruff + pytest with a Postgres service) -> build (docker build tagged with the commit SHA, Trivy scan) -> deploy (main only: compose up and smoke test on /ready). Each job has needs: on the previous one, so a failing test blocks build and deploy. This was demonstrated on PR #1 with an intentionally failing test.

The deploy job runs on a temporary GitHub runner as a smoke test; it is not a real server. The Trivy scan currently reports HIGH/CRITICAL findings without failing the build (exit-code 0).

## Release and rollback

~~~bash
./deploy.sh 1.1.0     # builds apex-ops-api:1.1.0, waits for /ready, records the version
./rollback.sh         # re-runs the previous image, no rebuild
./rollback.sh 1.0.0   # or a specific version
~~~

If a new release fails its readiness check, deploy.sh rolls back automatically to the last good version.

Demo hook: a version ending in -bad (for example ./deploy.sh 2.0.0-bad) makes /ready return 503 on purpose, to demonstrate a failed release and automatic rollback. It exists only for this demonstration.

## Configuration and security

- All configuration comes from environment variables (.env, see .env.example); no secrets are in the code or in Git.
- The container runs as a non-root user (appuser, uid 10001).
- Database SQL uses parameterised queries.
- Images are version-tagged; third-party GitHub Actions are pinned to version tags (pinning to commit SHAs is a next step).

## Project layout

~~~
app/                 Flask application (main.py)
tests/               pytest tests
Dockerfile           slim, non-root, HEALTHCHECK
docker-compose.yml   app + Postgres + volume + healthchecks
deploy.sh, rollback.sh
.github/workflows/   CI pipeline
docs/                observability plan, failure investigation, runbook, decision memo
~~~

## Further documents

- docs/observability.md
- docs/failure-investigation.md
- docs/runbook.md
- docs/decisions.md
- docs/ai-disclosure.md
- docs/security-and-cost.md
- evidence/screenshots/ (01-11 terminal, 12-17 CI runs and diagram, 18 fresh clone) and evidence/terminal_demo.txt (deploy, rollback and DB-down log)
