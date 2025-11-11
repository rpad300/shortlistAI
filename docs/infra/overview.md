# Infrastructure Overview

In one sentence: the application runs as two containers (FastAPI + React build) connected to Supabase, orchestrated locally with Docker Compose.

## Environment Layout
- **Local (Docker Compose)**: intended for day-to-day development and manual QA. Containers expose `frontend` on `http://localhost:3399` and `backend` on `http://localhost:8000`.
- **Supabase**: remains the single source of truth for PostgreSQL, authentication, storage and RLS policies. Docker containers connect to the same Supabase project defined by environment variables.
- **Future environments**: staging and production should mirror this topology (FastAPI container + static frontend container + managed Supabase).

## Container Topology
- `backend`: Python 3.13 slim image running `uvicorn main:app`. Includes required system packages for PDF generation (ReportLab) and AI integrations.
- `frontend`: Multi-stage Node → Nginx image that builds the Vite project and serves static assets. Includes an embedded reverse proxy that forwards `/api/*` requests to the backend service inside the Docker network.
- **Network**: default Docker bridge network; service names (`backend`, `frontend`) resolve automatically. External access uses mapped host ports.

## Configuration & Secrets
- All runtime configuration is injected via environment variables; never bake secrets into images.
- Compose loads variables from the root `.env` file (not committed). Ensure it contains the same keys listed in existing setup docs, including `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and AI provider API keys.
- The frontend build receives `VITE_API_BASE_URL=/api` so the browser calls the backend through the Nginx reverse proxy. Override this build argument if deploying behind a different gateway.

## Observability & Operations
- Logs: use `docker compose logs -f backend|frontend` during local development.
- Health checks: `backend` exposes `/health`; the reverse proxy surfaces it under `http://localhost:3399/api/health`.
- Backups and monitoring continue to rely on Supabase tooling; no additional stateful services are introduced by the Docker setup.

## Next Steps
- Define staging/production deployment pipelines that reuse these Docker images.
- Integrate container builds into CI/CD once the repository workflow is defined (`docs/infra/deployments.md` covers manual commands).

