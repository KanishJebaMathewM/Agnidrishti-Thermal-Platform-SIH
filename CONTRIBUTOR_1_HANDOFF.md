# Contributor 1 Handoff

Contributor 1 owns the infrastructure layer: PostgreSQL/PostGIS schema, Alembic
migrations, FastAPI API contracts, Redis/Celery wiring, deployment configuration,
and backend tests.

## Start the stack

1. Copy `.env.example` to `.env` for local non-container commands.
2. Start Docker Desktop.
3. Run `docker compose -f deployment/docker-compose.yml up --build`.
4. Check `http://localhost:8000/health` and open `http://localhost:8000/docs`.

The Compose backend uses `postgres` and `redis` service names automatically. Do not
replace them with `localhost` inside containers.

## Database

Run migrations from the repository root with:

```powershell
$env:PYTHONPATH = "backend"
alembic -c db/alembic.ini upgrade head
```

The initial migration creates the PostGIS-backed domain tables and spatial indexes.
H3 values remain application-side strings; no H3 PostgreSQL extension is required.

## API surfaces

- `/health`, `/ready`
- `/events`
- `/sources`
- `/dashboard/summary`, `/dashboard/map`, `/dashboard/trends`
- `/authorities`, `/authorities/routing/resolve`
- `/events/{event_id}/confirm`, `/false-alarm`, `/reclassify`
- `/events/{event_id}/notification-preview`, `/notification-log`
- `/model/current`, `/model/reload`

The Pydantic schemas in `backend/app/schemas/` preserve the frontend field names
such as `lat`, `lon`, `routedTo`, and `isAnomaly`.

## Extension points

Data ingestion and preprocessing contributors should implement the Celery task
bodies in `workers/ingestion/` and `workers/preprocessing/`. ML contributors own
classification and model artifacts. Routing and notification contributors can
extend the existing authority and notification APIs. The current task files are
intentional stubs and should not be treated as completed pipeline logic.

## Validation

```powershell
npm run build
python -m compileall -q backend db workers
docker compose -f deployment/docker-compose.yml config --quiet
$env:PYTHONPATH = "backend"
python -m pytest backend/tests -q
```

The test command requires the packages in `backend/requirements.txt` and a usable
Python environment. Full `/ready`, migration, and worker checks require running
PostgreSQL and Redis services.