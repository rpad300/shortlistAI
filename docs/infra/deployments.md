# Deployment & Docker Workflow

In one sentence: build and run both services locally with `docker compose`, relying on the same environment variables already defined in `.env`.

## Prerequisites
- Docker Desktop (v4.26+) or compatible Docker Engine with Compose v2 support.
- Project root `.env` populated with Supabase credentials and AI provider keys (never commit this file).
- Ports `3399` and `8000` available on the host.

## Build & Run Locally
```bash
docker compose up --build
```
- Builds `backend` and `frontend` images, installs dependencies, and starts both containers.
- Access the app at `http://localhost:3399`.
- Backend docs remain available at `http://localhost:8000/api/docs` (direct) and `http://localhost:3399/api/docs` (proxied).

To run in detached mode:
```bash
docker compose up --build -d
```

## Stopping & Cleanup
```bash
docker compose down
```
- Stops containers and releases ports.
- Add `--volumes` if you introduce named volumes in the future (currently none are used).

## Overriding Build Arguments
- Default frontend build uses `VITE_API_BASE_URL=/api`. Override during build:
  ```bash
  docker compose build \
    --build-arg VITE_API_BASE_URL=https://your-api.example.com frontend
  ```
- For automation, add environment variables to a Compose override file or CI pipeline instead of hardcoding secrets.

## Logs & Troubleshooting
- Tail backend logs: `docker compose logs -f backend`
- Tail frontend logs: `docker compose logs -f frontend`
- Rebuild only one service after code changes: `docker compose up --build backend`
- Verify Supabase connectivity with `curl http://localhost:3399/api/health`

## Next Steps
- Add CI/CD jobs that build and push the two images to a registry.
- Define infrastructure-as-code for production (e.g., Cloud Run, ECS, Azure App Service) that pulls these images and wires secrets from a secure store.

