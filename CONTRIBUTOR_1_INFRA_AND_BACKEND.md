# CONTRIBUTOR 1 — Infrastructure, Backend API & Database

> **Branch name to create:** `feat/infra-backend`
> **Your domain:** `backend/`, `db/`, `deployment/`, `scripts/`, root config files
> **Do NOT touch:** `frontend/`, `workers/`, `ml/`, anything in another contributor's domain
> **Push rule:** Always push to `feat/infra-backend`. Never push to `main`.

---

## Who you are

You are building the foundational layer that every other contributor depends on.
Without your work, nothing else runs. You own:

- The PostgreSQL + PostGIS database schema and migrations
- The FastAPI REST API that the frontend consumes
- The Docker Compose environment that boots the entire stack
- The Celery + Redis task queue infrastructure
- The `.env` configuration system
- Health endpoints and logging

---

## Repository context

The project is a monorepo called **AGNIDRISHTI** — an India-focused thermal anomaly
detection and monitoring platform. It ingests satellite fire data (NASA FIRMS / VIIRS
and ISRO INSAT), classifies thermal events using ML, and routes alerts to the correct
government authority.

The existing frontend (`src/` at the repo root) is a React + TypeScript prototype
that already has a working UI with mock data. Your job is to build the backend so
that frontend can eventually connect to real data.

**The frontend already defines the data contracts.** Study `src/data/mockData.ts`
before designing any schema — the shapes used there are your ground truth for what
the API must return.

---

## Step 0 — First actions (do these before anything else)

```
git checkout -b feat/infra-backend
```

Then read these files before writing a single line of code:

- `src/data/mockData.ts` — the TypeScript interfaces define exactly what API shapes the frontend expects
- `src/App.tsx` — the routes tell you which pages exist
- `AGNIDRISHTI_PLAN.md` — the master plan with architectural decisions

Do not deviate from the architecture decisions in AGNIDRISHTI_PLAN.md unless you
find a concrete implementation blocker.

---

## Step 1 — Root environment files

### 1.1 Create `.env.example`

Create at repo root. This is the template — never commit real secrets.

```
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=agnidrishti
POSTGRES_USER=agnidrishti
POSTGRES_PASSWORD=changeme

# Redis
REDIS_URL=redis://localhost:6379/0

# FastAPI
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true
SECRET_KEY=changeme-generate-a-real-key

# NASA FIRMS
FIRMS_API_KEY=your_firms_key_here
FIRMS_MAP_KEY=your_firms_map_key_here

# CORS (comma-separated origins)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 1.2 Create `backend/app/config.py`

Use `pydantic-settings` to load from environment:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "agnidrishti"
    postgres_user: str = "agnidrishti"
    postgres_password: str = "changeme"
    redis_url: str = "redis://localhost:6379/0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True
    secret_key: str = "changeme"
    firms_api_key: str = ""
    firms_map_key: str = ""
    cors_origins: list[str] = ["http://localhost:5173"]

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Step 2 — Docker Compose environment

Create `deployment/docker-compose.yml`.

Services required:

```yaml
services:

  postgres:
    image: postgis/postgis:16-3.4
    environment:
      POSTGRES_DB: agnidrishti
      POSTGRES_USER: agnidrishti
      POSTGRES_PASSWORD: changeme
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U agnidrishti"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ../backend
      dockerfile: Dockerfile
    env_file: ../.env
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ../backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  worker:
    build:
      context: ../workers
      dockerfile: Dockerfile
    env_file: ../.env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: celery -A celery_app worker --loglevel=info

volumes:
  postgres_data:
```

Create `deployment/docker/backend.Dockerfile` for the backend image.
Create `deployment/docker/worker.Dockerfile` for the worker image.

---

## Step 3 — Database schema

### 3.1 Create `backend/app/models/` SQLAlchemy models

Use SQLAlchemy 2.x with mapped_column syntax. Use GeoAlchemy2 for PostGIS columns.

Create one file per domain area:

**`backend/app/models/observation.py`**

```python
# Table: observations
# Columns (implement all of these):
#   id              UUID primary key
#   source_type     VARCHAR (FIRMS_VIIRS, INSAT)
#   source_product  VARCHAR
#   satellite       VARCHAR
#   timestamp_utc   TIMESTAMPTZ not null
#   latitude        DOUBLE PRECISION not null
#   longitude       DOUBLE PRECISION not null
#   geometry        GEOMETRY(Point, 4326)  -- PostGIS
#   h3_cell         VARCHAR(15)
#   frp             DOUBLE PRECISION  -- Fire Radiative Power MW
#   bright_ti4      DOUBLE PRECISION  -- 4µm brightness temp
#   bright_ti5      DOUBLE PRECISION  -- 11µm brightness temp
#   confidence      VARCHAR(10)  -- 'low','nominal','high' for VIIRS
#   quality_flags   JSONB
#   thermal_features JSONB  -- extracted INSAT features
#   raw_record_ref  JSONB  -- original record for replay
#   ingested_at     TIMESTAMPTZ default now()
#   source_id       UUID FK -> thermal_sources (nullable)
```

**`backend/app/models/thermal_source.py`**

```python
# Table: thermal_sources
# Columns:
#   id              UUID primary key
#   h3_cell         VARCHAR(15) unique
#   representative_lat  DOUBLE PRECISION
#   representative_lon  DOUBLE PRECISION
#   geometry        GEOMETRY(Point, 4326)
#   first_seen      TIMESTAMPTZ
#   last_seen       TIMESTAMPTZ
#   observation_count   INTEGER default 0
#   expected_class  VARCHAR(50)
#   mean_frp        DOUBLE PRECISION
#   frp_std         DOUBLE PRECISION
#   median_frp      DOUBLE PRECISION
#   monthly_profile JSONB  -- {month: avg_frp}
#   seasonal_profile JSONB
#   typical_hours   JSONB  -- active hour distribution
#   status          VARCHAR(30) default 'NEW'
#               -- NEW, OBSERVED, CANDIDATE, CONFIRMED, MONITORED, ARCHIVED
#   classification_confidence   DOUBLE PRECISION
#   last_updated    TIMESTAMPTZ default now()
```

**`backend/app/models/event.py`**

```python
# Table: events
#   id              UUID primary key
#   first_seen      TIMESTAMPTZ
#   last_seen       TIMESTAMPTZ
#   centroid_lat    DOUBLE PRECISION
#   centroid_lon    DOUBLE PRECISION
#   centroid        GEOMETRY(Point, 4326)
#   observation_count   INTEGER
#   source_id       UUID FK -> thermal_sources (nullable)
#   classification  VARCHAR(50)
#   classification_confidence   DOUBLE PRECISION
#   anomaly_score   DOUBLE PRECISION
#   anomaly_flag    BOOLEAN default false
#   severity        VARCHAR(20)  -- NORMAL, OBSERVE, REVIEW, HIGH, CRITICAL
#   status          VARCHAR(30)  -- NEW, ANALYZING, CANDIDATE, HUMAN_REVIEW,
#                                    CONFIRMED, FALSE_ALARM, RECLASSIFIED
#   state           VARCHAR(100)
#   district        VARCHAR(100)
#   model_version   VARCHAR(50)
#   created_at      TIMESTAMPTZ default now()
#   updated_at      TIMESTAMPTZ default now()
#
# Table: event_observations (join table)
#   event_id        UUID FK -> events
#   observation_id  UUID FK -> observations
#   PRIMARY KEY (event_id, observation_id)
```

**`backend/app/models/authority.py`**

```python
# Table: authorities
#   id              UUID primary key
#   state           VARCHAR(100)
#   district        VARCHAR(100)
#   authority_type  VARCHAR(50)
#       -- PLANT_EMERGENCY, FIRE_RESPONSE, FOREST_RESPONSE,
#          POLLUTION_CONTROL, DISTRICT_EMERGENCY, SYSTEM_OPERATOR
#   department      VARCHAR(200)
#   role            VARCHAR(100)
#   official_email  VARCHAR(200)
#   official_phone  VARCHAR(20)
#   portal_url      TEXT
#   active          BOOLEAN default true
#   verified_on     DATE
#   source_url      TEXT
#   created_at      TIMESTAMPTZ default now()
#   updated_at      TIMESTAMPTZ default now()
#
# Table: routing_profiles
#   id              UUID primary key
#   name            VARCHAR(100)  -- e.g. "industrial_fire_kerala"
#   state           VARCHAR(100)
#   district        VARCHAR(100)
#   classification  VARCHAR(50)
#   primary_authority_id    UUID FK -> authorities
#   secondary_authority_ids UUID[]  -- array of FKs
#   rules           JSONB
```

**`backend/app/models/notification.py`**

```python
# Table: notifications
#   id              UUID primary key
#   event_id        UUID FK -> events
#   authority_id    UUID FK -> authorities
#   channel         VARCHAR(20)  -- EMAIL, PHONE, PORTAL
#   status          VARCHAR(30)  -- READY, PRESENTED, ACTION_TAKEN
#   alert_content   JSONB
#   presented_at    TIMESTAMPTZ
#   action_taken_at TIMESTAMPTZ
#   operator_id     VARCHAR(100)  -- who triggered it
#   created_at      TIMESTAMPTZ default now()
#
# Table: operator_feedback
#   id              UUID primary key
#   event_id        UUID FK -> events
#   model_prediction    VARCHAR(50)
#   model_confidence    DOUBLE PRECISION
#   human_label     VARCHAR(50)
#   reviewer        VARCHAR(100)
#   comment         TEXT
#   verified_at     TIMESTAMPTZ default now()
```

**`backend/app/models/geography.py`**

```python
# Table: admin_boundaries
#   id              UUID primary key
#   level           VARCHAR(20)  -- COUNTRY, STATE, DISTRICT
#   state_id        VARCHAR(50)
#   state_name      VARCHAR(100)
#   district_id     VARCHAR(50)
#   district_name   VARCHAR(100)
#   geometry        GEOMETRY(MultiPolygon, 4326)
#   SPATIAL INDEX on geometry
#
# Table: industrial_facilities
#   id              UUID primary key
#   name            TEXT
#   facility_type   VARCHAR(50)
#   geometry        GEOMETRY(Point, 4326)
#   osm_id          BIGINT
#   state           VARCHAR(100)
#   district        VARCHAR(100)
#   tags            JSONB
#
# Table: landuse_features
#   id              UUID primary key
#   class           VARCHAR(50)  -- FOREST, AGRICULTURAL, INDUSTRIAL, etc.
#   geometry        GEOMETRY(MultiPolygon, 4326)
#   source          VARCHAR(50)  -- BHUVAN, OSM
#
# Table: forest_boundaries
#   id              UUID primary key
#   name            TEXT
#   category        VARCHAR(50)
#   geometry        GEOMETRY(MultiPolygon, 4326)
#   source          VARCHAR(50)  -- FSI
```

**`backend/app/models/ml.py`**

```python
# Table: model_versions
#   id              UUID primary key
#   version_tag     VARCHAR(50) unique  -- e.g. xgb_v1.0
#   feature_set_version VARCHAR(50)
#   training_data_version   VARCHAR(50)
#   trained_at      TIMESTAMPTZ
#   metrics         JSONB  -- precision, recall, f1 per class
#   artifact_path   TEXT  -- path inside ml/models/
#   is_active       BOOLEAN default false
#   notes           TEXT
#
# Table: training_labels
#   id              UUID primary key
#   observation_id  UUID FK -> observations
#   label           VARCHAR(50)
#   label_source    VARCHAR(100)
#   label_confidence    DOUBLE PRECISION
#   verification_status VARCHAR(30)  -- UNVERIFIED, VERIFIED, DISPUTED
#   labeled_at      TIMESTAMPTZ default now()
```

### 3.2 Database migrations with Alembic

- Initialize Alembic in `db/`
- Create an initial migration that creates all tables above
- Create PostGIS extension in migration: `CREATE EXTENSION IF NOT EXISTS postgis`
- Create H3 extension if available: `CREATE EXTENSION IF NOT EXISTS h3`
- Create all spatial indexes

Migration file goes in `db/migrations/versions/`.
Config file at `db/alembic.ini`.

---

## Step 4 — FastAPI application

### 4.1 `backend/app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import health, events, sources, dashboard, authorities, feedback, notifications

app = FastAPI(
    title="AGNIDRISHTI API",
    version="0.1.0",
    description="Thermal anomaly detection and monitoring platform"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(sources.router, prefix="/sources", tags=["sources"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(authorities.router, prefix="/authorities", tags=["authorities"])
app.include_router(feedback.router, tags=["feedback"])
app.include_router(notifications.router, tags=["notifications"])
```

### 4.2 Implement these API route files

Create each under `backend/app/api/routes/`:

**`health.py`**
```
GET /health   → {"status": "ok", "timestamp": "..."}
GET /ready    → checks DB + Redis connectivity, returns 200 or 503
```

**`events.py`**
```
GET  /events
     query params: page (int), limit (int), state (str), classification (str),
                   status (str), anomaly_only (bool), from_date (datetime), to_date (datetime)
     returns: { items: [EventSummary], total: int, page: int, pages: int }

GET  /events/{event_id}
     returns: EventDetail (full event with all fields)

GET  /events/{event_id}/observations
     returns: list of observations for that event

GET  /events/{event_id}/timeline
     returns: chronological list of observations with timestamps
```

**`sources.py`**
```
GET  /sources
     query params: page, limit, state, status, type
     returns: { items: [SourceSummary], total, page, pages }

GET  /sources/{source_id}
     returns: SourceDetail

GET  /sources/{source_id}/history
     returns: observation history for source (paginated)

GET  /sources/{source_id}/baseline
     returns: baseline statistics for source
```

**`dashboard.py`**
```
GET  /dashboard/summary
     returns:
     {
       total_events_24h: int,
       anomaly_events_24h: int,
       critical_events: int,
       active_sources: int,
       classification_distribution: [{name, value, pct, color}],
       risk_level_summary: [{name, count, pct, color}],
       state_anomaly_data: [{state, anomalies, total}],
       recent_events: [EventSummary]  # last 5
     }

GET  /dashboard/map
     returns: list of all active events with lat/lon for map rendering
     { events: [{id, lat, lon, classification, severity, confidence, anomaly_flag}] }

GET  /dashboard/trends
     returns: hourly trend data last 24h
     { points: [{date, industrial, flare, agricultural, forest, unknown}] }
```

**`authorities.py`**
```
GET  /authorities
     query params: state, district, authority_type, active_only
     returns: list of authorities

GET  /authorities/{authority_id}
     returns: authority detail

POST /authorities
     body: AuthorityCreate schema
     returns: created authority

PATCH /authorities/{authority_id}
     body: AuthorityUpdate schema
     returns: updated authority

GET  /routing/resolve?lat=&lon=&classification=&severity=
     returns: { state, district, routing_profile, primary_authority, secondary_authorities }
```

**`feedback.py`**
```
POST /events/{event_id}/confirm
     body: { reviewer: str, comment: str }

POST /events/{event_id}/false-alarm
     body: { reviewer: str, comment: str }

POST /events/{event_id}/reclassify
     body: { new_classification: str, reviewer: str, comment: str }
```

**`notifications.py`**
```
POST /events/{event_id}/notification-preview
     returns: full alert content object (does NOT send anything)

POST /events/{event_id}/notification-log
     body: { authority_id, channel, operator_id }
     Logs that a human took action. Does not send anything automatically.
```

**`model.py`**
```
GET  /model/current
     returns: active model version info

POST /model/reload
     triggers reload of active model artifact into memory
```

### 4.3 Pydantic schemas

Create `backend/app/schemas/` with one file per domain:
- `event_schemas.py` — EventSummary, EventDetail, EventFilter
- `source_schemas.py` — SourceSummary, SourceDetail, BaselineStats
- `authority_schemas.py` — AuthorityCreate, AuthorityUpdate, AuthorityDetail, RoutingResult
- `dashboard_schemas.py` — DashboardSummary, MapEvent, TrendPoint
- `observation_schemas.py` — ObservationDetail

All schemas must match the TypeScript interfaces in `src/data/mockData.ts`.
Map each TypeScript field to its Pydantic equivalent.

### 4.4 Database connection

Create `backend/app/utils/database.py`:
- SQLAlchemy async engine
- Session factory
- `get_db()` FastAPI dependency

---

## Step 5 — Celery infrastructure (skeleton)

Create `workers/celery_app.py`:

```python
from celery import Celery
from app.config import settings  # import from backend config

celery_app = Celery(
    "agnidrishti",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "workers.ingestion.firms_worker",
        "workers.preprocessing.preprocess_worker",
        "workers.events.event_worker",
        "workers.notifications.notification_worker",
    ]
)

celery_app.conf.task_routes = {
    "workers.ingestion.*": {"queue": "ingestion"},
    "workers.preprocessing.*": {"queue": "processing"},
    "workers.events.*": {"queue": "events"},
    "workers.notifications.*": {"queue": "notifications"},
}
```

Create empty placeholder task files (leave implementation for Contributor 2):
- `workers/ingestion/firms_worker.py` — define `ingest_firms_snapshot` task stub
- `workers/preprocessing/preprocess_worker.py` — define `preprocess_observation` task stub
- `workers/events/event_worker.py` — define `process_event` task stub
- `workers/notifications/notification_worker.py` — define `send_notification` task stub

Each stub should just `pass` or `raise NotImplementedError` for now.
Add a module docstring explaining what each task will eventually do.

---

## Step 6 — Backend requirements

Create `backend/requirements.txt` with pinned versions:

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
sqlalchemy==2.0.36
alembic==1.13.3
geoalchemy2==0.15.2
psycopg[async]==3.2.3
pydantic==2.9.2
pydantic-settings==2.5.2
redis==5.1.1
celery==5.4.0
httpx==0.27.2
python-dotenv==1.0.1
pytest==8.3.3
pytest-asyncio==0.24.0
httpx==0.27.2
```

---

## Step 7 — Seed data

Create `db/seeds/seed_authorities.py`:
- Populate `authorities` table with at least 5 realistic entries per major state
  (e.g., Fire Services, CPCB officer, Forest Department, District Emergency)
- Use data from public government directory sources where possible
- Include a `source_url` and `verified_on` for each entry

Create `db/seeds/seed_routing_profiles.py`:
- Create routing profiles linking event classifications to authority types per state

---

## Step 8 — Logging format

Create `backend/app/utils/logging.py`:
- Structured JSON logging
- Every log line must include: timestamp, level, service, event_type, trace_id (if available)
- Use Python's `logging` module with a JSON formatter

---

## Step 9 — Backend tests

Create `backend/tests/`:
- `test_health.py` — test `/health` and `/ready` endpoints
- `test_events.py` — test CRUD and filtering on events endpoints
- `test_dashboard.py` — test dashboard summary endpoint
- `test_routing.py` — test jurisdiction resolver

Use `pytest` + `httpx.AsyncClient` against a test database.
Use SQLite or a test Postgres container (whichever is simpler).

---

## Step 10 — Push

```
git add .
git commit -m "feat: infrastructure, database schema, FastAPI backend, Docker Compose"
git push -u origin feat/infra-backend
```

---

## Files you will create or modify

```
.env.example                                 (new)
backend/
  requirements.txt                           (new)
  Dockerfile                                 (new)
  app/
    main.py                                  (new)
    config.py                                (new)
    api/
      routes/
        health.py                            (new)
        events.py                            (new)
        sources.py                           (new)
        dashboard.py                         (new)
        authorities.py                       (new)
        feedback.py                          (new)
        notifications.py                     (new)
        model.py                             (new)
    models/
      base.py                                (new)
      observation.py                         (new)
      thermal_source.py                      (new)
      event.py                               (new)
      authority.py                           (new)
      notification.py                        (new)
      geography.py                           (new)
      ml.py                                  (new)
    schemas/
      event_schemas.py                       (new)
      source_schemas.py                      (new)
      authority_schemas.py                   (new)
      dashboard_schemas.py                   (new)
      observation_schemas.py                 (new)
    services/
      jurisdiction_service.py               (new)
      routing_service.py                    (new)
    repositories/
      event_repository.py                   (new)
      source_repository.py                  (new)
      authority_repository.py               (new)
    utils/
      database.py                            (new)
      logging.py                             (new)
  tests/
    test_health.py                           (new)
    test_events.py                           (new)
    test_dashboard.py                        (new)
    test_routing.py                          (new)
db/
  alembic.ini                                (new)
  migrations/
    env.py                                   (new)
    versions/
      0001_initial_schema.py                 (new)
  seeds/
    seed_authorities.py                      (new)
    seed_routing_profiles.py                 (new)
workers/
  celery_app.py                              (new — skeleton only)
  ingestion/firms_worker.py                  (new — stub)
  preprocessing/preprocess_worker.py         (new — stub)
  events/event_worker.py                     (new — stub)
  notifications/notification_worker.py       (new — stub)
deployment/
  docker-compose.yml                         (new)
  docker/
    backend.Dockerfile                       (new)
    worker.Dockerfile                        (new)
```

---

## Key rules for this contributor

1. **The frontend is the API contract.** Every field in `mockData.ts` must be returnable by your API.
2. **Use PostGIS properly.** Spatial queries (point-in-polygon for jurisdiction) must use PostGIS, not Python-side loops.
3. **No real government contact data in seeds.** Use clearly fake placeholder names and emails (e.g., `officer@example.gov.in`).
4. **Stub workers correctly.** Workers are just stubs. The actual ingestion logic is Contributor 2's job. Do not implement it.
5. **Docker Compose must boot from cold** with a single `docker compose up`.
6. **Return HTTP 503** from `/ready` if database or Redis is unreachable — do not return 200 with an error body.
