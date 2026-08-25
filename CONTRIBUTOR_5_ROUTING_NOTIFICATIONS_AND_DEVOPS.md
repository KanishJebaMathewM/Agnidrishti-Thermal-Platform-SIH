# CONTRIBUTOR 5 — Routing Engine, Notification Workflows & DevOps / CI-CD

> **Branch name to create:** `feat/routing-notifications-devops`  
> **Your domain:** `backend/app/services/`, `workers/notifications/`, `deployment/`, `docs/`, `.github/`  
> **Do NOT touch:** `frontend/src/`, `workers/ingestion/`, `workers/preprocessing/`, `ml/training/`  
> **Push rule:** Always push to `feat/routing-notifications-devops`. Never push to `main`.  

---

## Who you are

You are building the operational decision, routing, alerting, and deployment infrastructure of AGNIDRISHTI.
You own:

- The deterministic PostGIS jurisdiction lookup and agency routing service
- The notification worker system for generating, presenting, and logging alert notifications
- Human-in-the-loop audit logging and verification workflow backend implementation
- The production-grade Docker Compose, Nginx reverse proxy, and environment security setup
- The continuous integration and testing pipeline (GitHub Actions)
- System architecture, deployment, and operational documentation (`docs/`)

---

## Repository context

**AGNIDRISHTI** classifies satellite observations and identifies thermal events across India. Once an event is formed, your subsystem determines:
1. Which district/state authority has jurisdiction over the location (via PostGIS polygon query).
2. Which primary and secondary emergency response teams (Fire, CPCB, Forest Dept, District Collector) should receive the alert.
3. Composes actionable, human-readable alert payloads with map links, severity scores, and satellite metadata.
4. Logs operator confirmation, false-alarm marking, or reclassifications into immutable audit logs.
5. Packages the entire project into production-ready Docker containers with automated CI/CD checks.

---

## Step 0 — First actions (do these before anything else)

```bash
git checkout -b feat/routing-notifications-devops
```

Then read:

1. `AGNIDRISHTI_PLAN.md` — Section 2 (Non-Negotiable Architecture Decisions: 2.4 ML != routing authority, 2.5 Do not discover government contacts dynamically, 2.6 No mass alert spam).
2. `CONTRIBUTOR_1_INFRA_AND_BACKEND.md` — Step 3.1 (`authority.py`, `notification.py`, `geography.py` DB models).
3. `CONTRIBUTOR_3_ML_PIPELINE.md` — Step 6 (Event formation status and severity scores).

---

## Step 1 — Jurisdiction & Agency Routing Service

Create `backend/app/services/jurisdiction_service.py` and `routing_service.py`.

### 1.1 `backend/app/services/jurisdiction_service.py`

```python
"""
Jurisdiction service.

Performs PostGIS spatial queries to determine state, district,
and sub-district administrative boundaries for a given latitude and longitude.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

async def resolve_jurisdiction(db: AsyncSession, lat: float, lon: float) -> dict:
    """
    Query PostGIS admin_boundaries table using ST_Contains.
    Returns:
      {
        "state_id": str,
        "state_name": str,
        "district_id": str,
        "district_name": str,
        "country": "India"
      }
    """
    query = text("""
        SELECT state_id, state_name, district_id, district_name
        FROM admin_boundaries
        WHERE ST_Contains(geometry, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326))
        LIMIT 1
    """)
    result = await db.execute(query, {"lat": lat, "lon": lon})
    row = result.fetchone()
    
    if not row:
        return {
            "state_id": "UNKNOWN",
            "state_name": "Unknown / Offshore",
            "district_id": "UNKNOWN",
            "district_name": "Unknown",
            "country": "India"
        }

    return {
        "state_id": row.state_id,
        "state_name": row.state_name,
        "district_id": row.district_id,
        "district_name": row.district_name,
        "country": "India"
    }
```

### 1.2 `backend/app/services/routing_service.py`

```python
"""
Routing service.

Matches an event (jurisdiction + classification + severity) to specific
authority contacts stored in the authorities table.

Rule mapping:
  - Industrial Incident → Plant Emergency Response + District Emergency
  - Forest Fire         → Forest Department (Range Officer) + State Disaster Mgt
  - Agricultural Burn   → Pollution Control Board (CPCB/SPCB) + Agriculture Officer
  - Persistent Flare    → CPCB / Industrial Safety Inspector
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.jurisdiction_service import resolve_jurisdiction
from app.repositories.authority_repository import get_authorities_by_district

async def resolve_alert_route(
    db: AsyncSession,
    lat: float,
    lon: float,
    classification: str,
    severity: str
) -> dict:
    jurisdiction = await resolve_jurisdiction(db, lat, lon)
    
    state = jurisdiction["state_name"]
    district = jurisdiction["district_name"]

    # Target authority type mapping based on classification
    type_map = {
        "Industrial Incident": ["PLANT_EMERGENCY", "FIRE_RESPONSE", "DISTRICT_EMERGENCY"],
        "Forest Fire": ["FOREST_RESPONSE", "FIRE_RESPONSE", "DISTRICT_EMERGENCY"],
        "Agricultural Burn": ["POLLUTION_CONTROL", "DISTRICT_EMERGENCY"],
        "Persistent Flare/Kiln": ["POLLUTION_CONTROL", "PLANT_EMERGENCY"],
        "Unknown": ["DISTRICT_EMERGENCY"]
    }

    target_types = type_map.get(classification, ["DISTRICT_EMERGENCY"])
    authorities = await get_authorities_by_district(db, state, district, target_types)

    primary = authorities[0] if authorities else None
    secondary = authorities[1:] if len(authorities) > 1 else []

    return {
        "jurisdiction": jurisdiction,
        "classification": classification,
        "severity": severity,
        "primary_authority": primary,
        "secondary_authorities": secondary,
        "routing_rule_matched": f"{classification.lower()}_{state.lower()}_rule"
    }
```

---

## Step 2 — Alert Composition & Notification Worker

Create `workers/notifications/alert_composer.py` and replace `workers/notifications/notification_worker.py`.

### 2.1 `workers/notifications/alert_composer.py`

```python
"""
Alert Payload Composer.

Constructs structured human-readable notification messages and JSON payloads
for official dispatch.
"""
def compose_event_alert_payload(event: dict, route: dict) -> dict:
    """
    Build structured alert package.
    """
    event_id = event["id"]
    lat, lon = event["centroid_lat"], event["centroid_lon"]
    severity = event["severity"]
    classification = event["classification"]
    confidence = event.get("classification_confidence", 0.0)
    
    map_link = f"https://agnidrishti.gov.in/events?id={event_id}&lat={lat}&lon={lon}"
    
    subject = f"[AGNIDRISHTI {severity} ALERT] {classification} detected in {route['jurisdiction']['district_name']}, {route['jurisdiction']['state_name']}"
    
    body = f"""
====================================================================
AGNIDRISHTI THERMAL ANOMALY INTELLIGENCE ALERT
====================================================================
Event ID: {event_id}
Severity: {severity}
Classification: {classification} (Confidence: {confidence*100:.1f}%)
Location: {lat:.4f}° N, {lon:.4f}° E ({route['jurisdiction']['district_name']}, {route['jurisdiction']['state_name']})
First Seen: {event.get('first_seen')}
Observation Count: {event.get('observation_count')}

RECOMMENDED ACTIONS:
1. Verify ground situation via Ops Center portal: {map_link}
2. Contact primary authority: {route.get('primary_authority', {}).get('department', 'District Emergency Center')}
====================================================================
"""
    return {
        "event_id": event_id,
        "subject": subject,
        "body_text": body.strip(),
        "map_url": map_link,
        "primary_recipient": route.get("primary_authority"),
        "secondary_recipients": route.get("secondary_authorities"),
    }
```

### 2.2 `workers/notifications/notification_worker.py`

```python
"""
Notification Worker.

Handles alert presentation generation and logging dispatch events.
NOTE: Per AGNIDRISHTI architecture, alerts are PRESENTED to human operators.
Direct mass SMS/Email dispatch requires manual operator click.
"""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task(name="workers.notifications.send_notification")
def send_notification(event_id: str, authority_id: str, channel: str, operator_id: str):
    """
    Log and record manual operator dispatch action.
    """
    logger.info(f"[Notification Worker] Dispatching {channel} for event {event_id} to authority {authority_id} by operator {operator_id}")
    
    # Insert record into notifications table with status='ACTION_TAKEN'
    return {
        "status": "DISPATCHED",
        "event_id": event_id,
        "authority_id": authority_id,
        "channel": channel,
        "operator_id": operator_id
    }
```

---

## Step 3 — Operator Feedback & Audit Workflow

Create `backend/app/services/feedback_service.py` to persist human reviewer actions into `operator_feedback` and `training_labels` tables for downstream ML retraining.

```python
"""
Feedback service.

Processes human confirmations, false alarms, and reclassifications.
Ensures human feedback feeds into the training dataset pipeline.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.event_repository import update_event_status, update_event_classification

async def record_human_confirmation(db: AsyncSession, event_id: str, reviewer: str, comment: str):
    await update_event_status(db, event_id, "CONFIRMED")
    # Log to operator_feedback table
    return {"status": "CONFIRMED", "event_id": event_id}

async def record_false_alarm(db: AsyncSession, event_id: str, reviewer: str, comment: str):
    await update_event_status(db, event_id, "FALSE_ALARM")
    return {"status": "FALSE_ALARM", "event_id": event_id}

async def record_reclassification(db: AsyncSession, event_id: str, new_class: str, reviewer: str, comment: str):
    await update_event_classification(db, event_id, new_class, "RECLASSIFIED")
    return {"status": "RECLASSIFIED", "event_id": event_id, "new_classification": new_class}
```

---

## Step 4 — Production Docker Deployment Infrastructure

Create production deployment configs in `deployment/`:

### 4.1 `deployment/docker-compose.prod.yml`

```yaml
version: '3.8'

services:
  postgres:
    image: postgis/postgis:16-3.4
    restart: always
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: always
    volumes:
      - redis_prod_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ../backend
      dockerfile: Dockerfile
    restart: always
    env_file: ../.env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

  worker:
    build:
      context: ../workers
      dockerfile: Dockerfile
    restart: always
    env_file: ../.env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: celery -A celery_app worker --loglevel=info -c 4

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ../frontend/dist:/usr/share/nginx/html:ro
    depends_on:
      - backend

volumes:
  postgres_prod_data:
  redis_prod_data:
```

### 4.2 `deployment/nginx/nginx.conf`

Create Nginx reverse proxy configuration handling SPA routing and API reverse proxying to FastAPI.

---

## Step 5 — CI/CD Pipeline Configuration

Create `.github/workflows/ci.yml`:

```yaml
name: AGNIDRISHTI CI/CD Pipeline

on:
  push:
    branches: [ main, feat/* ]
  pull_request:
    branches: [ main ]

jobs:
  lint-and-test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytest httpx ruff
          pip install -r backend/requirements.txt
      - name: Run Backend Tests
        run: pytest backend/tests

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install dependencies & Build
        run: |
          npm ci
          npm run typecheck
          npm run build

  docker-build-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Test Docker Compose Build
        run: docker compose -f deployment/docker-compose.yml build
```

---

## Step 6 — System Documentation (`docs/`)

Create comprehensive documentation files:

1. `docs/architecture/system_overview.md` — Monorepo layout, Online vs Offline loop diagrams, and PostGIS/H3 indexing strategy.
2. `docs/operations/deployment_guide.md` — Step-by-step setup guide for dev and production Docker Compose deployments.
3. `docs/api/swagger_spec.md` — API endpoint reference listing request parameters and response schemas.

---

## Step 7 — Push

```bash
git add .
git commit -m "feat: routing service, alert composer, production Docker Compose, Nginx config, CI/CD pipeline, and docs"
git push -u origin feat/routing-notifications-devops
```

---

## Files you will create or modify

```text
backend/
  app/
    services/
      jurisdiction_service.py                (new)
      routing_service.py                     (new)
      feedback_service.py                    (new)
workers/
  notifications/
    alert_composer.py                        (new)
    notification_worker.py                   (REPLACE stub)
deployment/
  docker-compose.prod.yml                    (new)
  nginx/
    nginx.conf                               (new)
.github/
  workflows/
    ci.yml                                   (new)
docs/
  architecture/
    system_overview.md                       (new)
  operations/
    deployment_guide.md                      (new)
  api/
    swagger_spec.md                          (new)
```

---

## Key rules for this contributor

1. **Routing is deterministic.** Never guess or hallucinate emergency contacts dynamically. Query PostGIS admin boundaries and look up maintained records in the `authorities` table.
2. **Alerts require human oversight.** Per architecture rule 2.6, no mass automated SMS/Email spam. The worker composes payloads; operators initiate dispatch.
3. **Keep production security tight.** Never commit passwords or secret keys in `docker-compose.prod.yml`. Read everything from `.env`.
4. **Clean separation of boundaries.** Do not edit frontend React components or ML training logic. Focus on routing, notifications, deployment, and CI pipelines.
