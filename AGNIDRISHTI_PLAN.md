\
# AGNIDRISHTI — Implementation PLAN.md

> **Project:** AGNIDRISHTI  
> **Team:** Tech Pulse  
> **Problem Statement:** SIH26162  
> **Scope:** India-only thermal anomaly detection, classification, monitoring and GIS decision support  
> **Current implementation status:** **Frontend prototype implemented. Backend, data pipeline, ML pipeline, database, authority directory, notification workflow, deployment and production integration remain to be implemented.**

---

## 0. Purpose of This Plan

This file is the master implementation plan for AGNIDRISHTI.

The architecture has already been finalized conceptually. This document converts that architecture into an implementation sequence so the project can be split into smaller tasks/issues without losing the end-to-end design.

The most important architectural rule is:

```text
ONLINE INFERENCE
New satellite observation
        ↓
Preprocessing
        ↓
Feature extraction
        ↓
Classification
        ↓
Historical baseline / anomaly detection
        ↓
Event aggregation
        ↓
Priority / routing
        ↓
Dashboard + human action

OFFLINE LEARNING
Historical observations
        +
Weak labels
        +
Human-verified labels
        ↓
Training dataset
        ↓
Model training
        ↓
Validation / evaluation
        ↓
Model version
        ↓
Deploy model
```

**Do not retrain the model every time new satellite data arrives.**

New observations use the currently deployed model. Training is periodic and independent.

---

# 1. Current Status

## 1.1 Already implemented

### Frontend prototype
- [x] Main application shell
- [x] Dashboard / map-oriented interface
- [x] Event visualization UI
- [x] Event detail / information presentation
- [x] Initial authority/contact interaction concepts
- [x] Main visual language and navigation
- [x] Frontend screens required to demonstrate the product concept

> The existing frontend should now be treated as the **UI contract**. Backend APIs should be designed around the information the current screens need rather than redesigning the product every time a backend feature is added.

## 1.2 Not yet implemented

- [ ] Real FIRMS data ingestion
- [ ] INSAT/MOSDAC data ingestion
- [ ] Raw data storage
- [ ] Data normalization and quality-control pipeline
- [ ] OSM/Overpass ingestion
- [ ] Bhuvan / land-use integration
- [ ] FSI / forest boundary/reference integration
- [ ] Administrative boundary integration
- [ ] PostgreSQL/PostGIS database
- [ ] H3 spatial indexing
- [ ] Thermal-source registry
- [ ] Historical baseline generation
- [ ] Feature engineering pipeline
- [ ] Initial labeled/weakly labeled training dataset
- [ ] XGBoost classifier
- [ ] Anomaly detection engine
- [ ] Temporal/event clustering
- [ ] Event scoring and priority engine
- [ ] Authority directory
- [ ] Jurisdiction-based routing
- [ ] Human verification workflow
- [ ] Alert composition
- [ ] Email/call/portal actions
- [ ] FastAPI backend
- [ ] Celery workers
- [ ] Redis
- [ ] Model registry/versioning
- [ ] Authentication/authorization
- [ ] Audit logs
- [ ] Docker deployment
- [ ] Evaluation and benchmark suite
- [ ] End-to-end integration
- [ ] Production-like demo data
- [ ] Final documentation

---

# 2. Non-Negotiable Architecture Decisions

These decisions are frozen unless implementation evidence proves a change is necessary.

## 2.1 India-only operational scope

The system operates on Indian territory and Indian administrative jurisdictions.

The satellite may observe a larger footprint, but the operational intelligence layer is clipped/routed to India.

```text
Satellite footprint
      ↓
India boundary / AOI
      ↓
Indian observations
      ↓
Indian context layers
      ↓
Indian district/state routing
```

## 2.2 Observation != Source != Event

These are three different objects.

### Observation
A single satellite detection/measurement.

### Thermal source
A recurring physical location/pattern, such as a known flare or kiln.

### Event
A time-bounded episode consisting of one or more observations.

```text
Observations
   ↓
Source history
   +
Event aggregation
```

## 2.3 Online inference != training

### Online
Every newly available observation goes through inference.

### Offline
Verified historical data is periodically used to retrain and evaluate models.

## 2.4 ML != routing authority

ML determines:
- likely class
- confidence
- anomaly score

A deterministic routing layer determines:
- jurisdiction
- applicable authority role
- notification options

A human remains responsible for operational escalation.

## 2.5 Do not discover government contacts dynamically during an emergency

Do not build:

```text
AI → web search → guess officer → send message
```

Build:

```text
Event coordinates
    ↓
District/state
    ↓
Routing profile
    ↓
Authority directory
    ↓
Verified official contact
```

Contacts are configuration data maintained by an authorized administrator.

## 2.6 No mass alert spam

One event should become one actionable case.

Use:
- deduplication
- cooldowns
- event aggregation
- severity thresholds
- primary contact
- optional secondary contact

Do not send one message for every satellite pixel.

---

# 3. Final Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React + TypeScript | Existing product UI |
| Map | MapLibre GL JS | Open-source mapping |
| Large-scale visualization | deck.gl | Event/point rendering |
| Backend API | FastAPI | REST API |
| Job processing | Celery | Background ingestion/processing |
| Broker/cache | Redis | Task queue/cache |
| Database | PostgreSQL | Core application data |
| Spatial DB | PostGIS | Spatial queries/geometries |
| Spatial indexing | H3 | Stable spatial identity/aggregation |
| Data processing | Python, Pandas, NumPy | ETL/features |
| Geospatial processing | GeoPandas, Shapely, GDAL/Rasterio | Geospatial ETL |
| Fire data | NASA FIRMS / VIIRS | Active-fire observations |
| Indian satellite context | ISRO MOSDAC / INSAT products | Frequent thermal context |
| Infrastructure context | OpenStreetMap / Overpass | Industrial/geographic context |
| Land-use context | Bhuvan / available official layers | Land-use/land-cover |
| Forest context | FSI / official forest layers | Forest context/reference |
| Classification | XGBoost | Multiclass source classification |
| Anomaly detection | Isolation Forest + statistical baseline | Abnormality detection |
| Event clustering | ST-DBSCAN / deterministic spatio-temporal rules | Observation → event |
| Deployment | Docker / Docker Compose | Reproducible local/on-prem deployment |
| Alerts | Email + tel actions + official portal links | Human-controlled notification |
| Testing | Pytest + frontend test suite | Unit/integration testing |

---

# 4. Repository Structure

Recommended final monorepo:

```text
agnidrishti/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── tests/
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   └── utils/
│   └── tests/
│
├── workers/
│   ├── ingestion/
│   ├── preprocessing/
│   ├── enrichment/
│   ├── inference/
│   ├── events/
│   └── notifications/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── reference/
│   └── samples/
│
├── ml/
│   ├── datasets/
│   ├── features/
│   ├── training/
│   ├── evaluation/
│   ├── models/
│   └── inference/
│
├── db/
│   ├── migrations/
│   ├── seeds/
│   └── sql/
│
├── scripts/
│   ├── bootstrap.py
│   ├── backfill_firms.py
│   ├── build_baselines.py
│   ├── seed_authorities.py
│   └── evaluate_model.py
│
├── deployment/
│   ├── docker/
│   └── docker-compose.yml
│
├── docs/
│   ├── architecture/
│   ├── api/
│   ├── ml/
│   └── operations/
│
└── PLAN.md
```

---

# 5. Phase 0 — Repository and Environment Foundation

## Goal

Make the project reproducible before implementing individual subsystems.

### Tasks

- [ ] Create monorepo structure.
- [ ] Pin Python version.
- [ ] Pin Node.js/frontend version.
- [ ] Add `.env.example`.
- [ ] Create development Docker Compose.
- [ ] Add PostgreSQL + PostGIS.
- [ ] Add Redis.
- [ ] Add FastAPI service.
- [ ] Add Celery worker service.
- [ ] Add frontend service.
- [ ] Add shared configuration.
- [ ] Add logging format.
- [ ] Add health endpoints.
- [ ] Add database migration system.
- [ ] Add pre-commit/linting/formatting.
- [ ] Add CI pipeline.

### Acceptance criteria

```text
docker compose up
        ↓
frontend reachable
backend reachable
postgres reachable
redis reachable
celery worker connected
```

No ML yet.

---

# 6. Phase 1 — Freeze and Connect the Existing Frontend

## Goal

Preserve the existing UI and make every data dependency explicit.

### Tasks

- [ ] Inventory every screen already implemented.
- [ ] List every card, table, map layer and detail field.
- [ ] Create frontend mock JSON matching the final API schema.
- [ ] Replace hardcoded values only after API contracts exist.
- [ ] Add loading states.
- [ ] Add empty states.
- [ ] Add error states.
- [ ] Add "data freshness" indicators.
- [ ] Add observation/source/event status.
- [ ] Add event severity.
- [ ] Add confidence/anomaly display.
- [ ] Add authority/contact panel.
- [ ] Add verification actions.
- [ ] Keep existing visual design unless a missing backend field requires a minor UI adjustment.

### Important

Do not spend the next development cycles redesigning the frontend.

The frontend is now the **consumer** of the platform.

---

# 7. Phase 2 — Acquire and Standardize Reference Geography

## Goal

Create the static/context layers required to understand a detected point.

## 7.1 Administrative boundaries

Need:
- [ ] India boundary
- [ ] state boundaries
- [ ] district boundaries
- [ ] required sub-district/local boundaries if needed

Store in PostGIS.

Each polygon needs stable identifiers:

```text
state_id
state_name
district_id
district_name
geometry
```

## 7.2 Industrial/geographic infrastructure

Use OSM/Overpass where useful.

Need:
- [ ] industrial areas
- [ ] refineries
- [power plants
- [factories]
- [mining areas where available]
- [LNG/petrochemical infrastructure where mapped]
- [kilns where mapped]
- [settlements
- [roads]

Do not assume OSM is complete.

## 7.3 Land use

Need:
- [ ] land-use/land-cover data
- [ ] agricultural areas
- [industrial context
- [forest context]

## 7.4 Forest

Need:
- [ ] official forest boundary/reference layers
- [ ] FSI-compatible fire/reference data where accessible

### Acceptance criteria

For an arbitrary point:

```text
(lat, lon)
    ↓
state
district
land-use
forest/not forest
nearest industrial facility
distances to context objects
```

must be queryable from PostGIS.

---

# 8. Phase 3 — NASA FIRMS Ingestion

## Goal

Create a reliable, repeatable India FIRMS ingestion pipeline.

## Primary fire observation source

Use VIIRS FIRMS as the primary active-fire feed.

Initial historical window:

```text
2020–2026
```

Potential later historical expansion:

```text
2012–2026
```

for S-NPP where useful.

### Important

Do not treat the FIRMS record as a conventional full satellite image.

Treat it as an active-fire observation containing fire attributes.

### Tasks

- [ ] Identify exact FIRMS endpoints/products to use.
- [ ] Obtain access/API credentials if required.
- [ ] Build ingestion client.
- [ ] Implement request retries.
- [ ] Implement timeout handling.
- [ ] Implement rate limiting.
- [ ] Store ingestion timestamp.
- [ ] Store source/product/satellite metadata.
- [ ] Clip/query to India + small context buffer.
- [ ] Deduplicate records.
- [ ] Handle NRT vs archived records.
- [ ] Track ingestion status.
- [ ] Build historical backfill script.
- [ ] Build live polling job.
- [ ] Add freshness monitoring.

### Raw observation fields

At minimum, retain fields actually provided by the selected FIRMS product, including where applicable:

```text
latitude
longitude
acq_date
acq_time
satellite
instrument
confidence
FRP
bright_ti4
bright_ti5
daynight
scan
track
```

### Acceptance criteria

Given a FIRMS response:
- it can be stored;
- duplicates are not created;
- timestamps are normalized;
- observations can be spatially queried;
- observations can be replayed through the pipeline.

---

# 9. Phase 4 — INSAT / MOSDAC Integration

## Goal

Use geostationary thermal observations as temporal/context data rather than assuming they are simply another FIRMS feed.

### Initial history target

```text
2020–2026
```

Subject to actual access/product availability.

INSAT-3D imager products provide frequent geolocated observations and relevant thermal channels.

### Tasks

- [ ] Identify the exact MOSDAC product(s) accessible to the team.
- [ ] Confirm authentication/access process.
- [ ] Confirm exact file format.
- [ ] Confirm temporal frequency.
- [ ] Confirm spatial resolution.
- [ ] Confirm available thermal bands.
- [ ] Implement downloader.
- [ ] Implement raster/geolocation parsing.
- [ ] Build quality flags.
- [ ] Store or archive source files.
- [ ] Build spatial extraction around FIRMS candidate points.
- [ ] Avoid storing the entire country at every time step unless required.
- [ ] Create extracted thermal features for candidate regions.

### Key design

Instead of:

```text
Store every pixel over India forever
```

prefer:

```text
INSAT product
   ↓
candidate FIRMS location/window
   ↓
extract relevant thermal values
   ↓
feature record
```

This is much more manageable for the prototype.

---

# 10. Phase 5 — Unified Observation Model

## Goal

Normalize FIRMS and INSAT-derived information into one internal observation representation.

Conceptual schema:

```text
Observation
-----------
id
source_type
source_product
satellite
timestamp_utc
latitude
longitude
geometry
h3_cell
frp
bright_ti4
bright_ti5
thermal_features
confidence
quality_flags
raw_record_reference
created_at
```

Some fields may be null depending on source.

### Acceptance criteria

A downstream feature-engineering function should accept a single normalized observation object regardless of which source produced it.

---

# 11. Phase 6 — Data Quality and Preprocessing

## Goal

Prevent garbage from reaching ML.

### Tasks

- [ ] Coordinate validation.
- [ ] Timestamp normalization to UTC.
- [ ] India-boundary filtering.
- [ ] Duplicate detection.
- [ ] Impossible-value checks.
- [ ] Missing-value handling.
- [ ] satellite/product consistency checks.
- [ ] quality flags.
- [ ] cloud/data-gap indicator where applicable.
- [ ] source availability monitoring.
- [ ] observation provenance.

### Critical rule

```text
No usable observation
        ≠
No fire
```

Missing/cloud-obscured data must not be interpreted as a negative fire observation.

---

# 12. Phase 7 — H3 Spatial Indexing

## Goal

Give each observation a stable spatial identity.

### Tasks

- [ ] Select H3 resolution.
- [ ] Benchmark resolution against event density and feature scale.
- [ ] Store H3 cell for each observation.
- [ ] Aggregate historical observations by cell.
- [ ] Use exact PostGIS geometries for precise boundary/distance queries.

### Acceptance criteria

Every valid observation can return:

```text
H3 cell
state
district
nearest industrial context
land-use context
forest context
```

---

# 13. Phase 8 — Thermal Source Registry

## Goal

Create the "memory" of AGNIDRISHTI.

A thermal source is a recurring spatial pattern, not just a single observation.

## Registry fields

```text
source_id
representative_geometry
h3_cell
first_seen
last_seen
observations_count
expected_class
mean_frp
frp_std
median_frp
typical_hours
typical_days
monthly_profile
seasonal_profile
typical_duration
active_days
classification_confidence
status
last_updated
```

### Source lifecycle

```text
NEW
 ↓
OBSERVED
 ↓
CANDIDATE SOURCE
 ↓
CONFIRMED SOURCE
 ↓
MONITORED SOURCE
 ↓
ARCHIVED / INACTIVE
```

### Tasks

- [ ] Create source matching logic.
- [ ] Associate observations with nearby known sources.
- [ ] Create new source candidates.
- [ ] Update source statistics.
- [ ] Distinguish known/unknown sources.
- [ ] Track first and last observation.
- [ ] Build seasonal baseline.

---

# 14. Phase 9 — Historical Baseline Engine

## Goal

Answer:

> "What is normal for this source/location?"

### Baseline dimensions

- [ ] location
- [ ] month
- [ ] day/night
- [ ] time-of-day
- [ ] day-of-week where useful
- [ ] FRP
- [ ] thermal features
- [ ] observation frequency
- [ ] duration
- [ ] persistence

### Example

```text
Source 001

Normal FRP:
150–180 MW

Typical period:
18:00–05:00

Typical frequency:
Daily

Expected class:
Persistent flare
```

### Acceptance criteria

For any known source and new observation:

```text
current_features
        ↓
baseline lookup
        ↓
expected behaviour
        ↓
deviation features
```

---

# 15. Phase 10 — Feature Engineering

## Goal

Convert the observation + context + history into the ML feature vector.

## Feature groups

### A. Thermal

- [ ] FRP
- [ ] brightness temperature fields available from selected source
- [ ] temperature differences where physically valid
- [ ] extracted INSAT thermal values
- [ ] thermal trend
- [ ] quality/confidence indicators

### B. Temporal

- [ ] hour
- [ ] day/night
- [ ] day of week
- [ ] month
- [ ] season
- [ ] recent observation count
- [ ] consecutive activity
- [ ] event duration

### C. Historical

- [ ] historical mean FRP
- [ ] historical median
- [ ] historical variance
- [ ] current-vs-baseline deviation
- [ ] source age
- [ ] observation frequency
- [ ] seasonal deviation

### D. Geographic

- [ ] industrial distance
- [ ] nearest facility type
- [ ] forest distance
- [ ] farmland distance
- [ ] settlement distance
- [ ] land-use class
- [ ] district/state
- [ ] H3 cell

### E. Source state

- [ ] known source?
- [ ] new source?
- [ ] source class history
- [ ] historical confidence

### Output

One reproducible feature vector with a version identifier:

```text
feature_set_version = v1
```

---

# 16. Phase 11 — Build the Initial Training Dataset

## Goal

Create a defensible labeled dataset without pretending a perfect Indian industrial-fire dataset already exists.

## Label strategy

Use:

### Persistent flare / known industrial thermal sources
- official/independent known-source references where accessible
- repeated historical behaviour
- verified sources

### Forest fire
- official forest/fire reference information
- forest spatial context

### Agricultural burning
- agricultural land context
- seasonal patterns
- historical fire observations
- weak rules

### Industrial incident
- documented incident records
- human verification

### Unknown
- observations not confidently belonging to existing classes

## Store label provenance

Every label should have:

```text
label
label_source
label_confidence
label_timestamp
verification_status
```

### Do not force uncertain records

Maintain:

```text
unknown / uncertain
```

rather than introducing incorrect labels.

---

# 17. Phase 12 — Temporal Dataset Split

Do not randomly mix all years.

Recommended prototype evaluation:

```text
TRAIN
2020–2024

VALIDATION
2025

TEST
2026
```

Then, after validating the approach:

```text
PRODUCTION TRAINING
2020–2026
```

This tests whether the model generalizes to future observations.

---

# 18. Phase 13 — XGBoost Classification

## Goal

Classify each observation/event into:

```text
1. industrial incident
2. persistent flare / kiln
3. agricultural burn
4. forest fire
5. unknown
```

## Tasks

- [ ] Build training matrix.
- [ ] Handle categorical features appropriately.
- [ ] Handle missing features.
- [ ] Train baseline model.
- [ ] Tune only after a valid baseline exists.
- [ ] Save model artifact.
- [ ] Save feature schema.
- [ ] Save training data version.
- [ ] Save model version.
- [ ] Evaluate confusion matrix.
- [ ] Evaluate per-class precision/recall/F1.
- [ ] Calibrate or interpret confidence where appropriate.
- [ ] Test class imbalance.
- [ ] Compare against simple rules baseline.

### Acceptance criteria

The model must produce:

```text
class_probabilities
predicted_class
model_version
```

and the inference output must be reproducible.

---

# 19. Phase 14 — Anomaly Detection

## Goal

Determine whether current behaviour differs meaningfully from expected behaviour.

Use two complementary layers.

## 14.1 Statistical baseline

Calculate:

```text
current_value
-
expected_value
```

normalized by historical variation.

This is interpretable.

## 14.2 Isolation Forest

Use historical feature vectors to identify unusual patterns.

### Output

```text
anomaly_score
anomaly_flag
anomaly_reason_features
baseline_deviation
```

### Important

Anomaly detection is NOT the same as classification.

```text
XGBoost
"What is it?"

Anomaly engine
"Is it behaving unusually?"
```

---

# 20. Phase 15 — Spatio-Temporal Event Formation

## Goal

Prevent multiple satellite detections from becoming multiple alerts.

### Input

```text
observation_1
observation_2
observation_3
...
```

### Logic

Group observations based on:

- geographic proximity
- timestamp proximity
- source identity where available
- H3 neighbourhood
- persistence

Use ST-DBSCAN or a simpler deterministic spatio-temporal grouping method for the prototype.

### Event object

```text
event_id
first_seen
last_seen
centroid
geometry
observation_count
source_id
classification
classification_confidence
anomaly_score
severity
status
```

### Acceptance criteria

A single physical episode should become a single event whenever the grouping criteria indicate they belong together.

---

# 21. Phase 16 — Event State Machine

Each event should have an explicit status.

Recommended:

```text
NEW
 ↓
ANALYZING
 ↓
CANDIDATE
 ↓
HUMAN_REVIEW
 ├── CONFIRMED
 ├── FALSE_ALARM
 └── RECLASSIFIED
```

For an alert:

```text
READY_TO_NOTIFY
 ↓
CONTACT_PRESENTED
 ↓
ACTION_TAKEN
```

This makes the system auditable.

---

# 22. Phase 17 — Severity / Priority Engine

Do not make severity equal to ML confidence.

Create an explicit priority score using:

- classification confidence
- anomaly score
- persistence
- intensity
- proximity to sensitive/industrial infrastructure
- event size
- duration
- uncertainty/data quality

Conceptually:

```text
Classification confidence
        +
Anomaly
        +
Persistence
        +
Context
        +
Data quality
        ↓
Priority
```

Possible states:

```text
NORMAL
OBSERVE
REVIEW
HIGH
CRITICAL
```

Thresholds must be calibrated using prototype results.

---

# 23. Phase 18 — Authority Directory

## Goal

Map each jurisdiction/event type to official operational contacts.

## Do NOT

- scrape individuals dynamically
- guess email addresses
- use random public personal numbers
- automatically message many authorities

## Do

Create a configurable directory:

```text
authority_id
state
district
authority_type
department
role
official_email
official_phone
portal_url
active
verified_on
source_url
```

Examples of role types:

```text
PLANT_EMERGENCY
FIRE_RESPONSE
FOREST_RESPONSE
POLLUTION_CONTROL
DISTRICT_EMERGENCY
SYSTEM_OPERATOR
```

### Data governance

- [ ] Contact verification date
- [ ] Contact source URL
- [ ] Active/inactive flag
- [ ] Admin update UI
- [ ] Audit log

---

# 24. Phase 19 — Jurisdiction Resolver

## Goal

Given:

```text
latitude
longitude
classification
severity
```

return:

```text
state
district
routing_profile
primary authority role
secondary authority role(s)
```

### Example

```text
POINT
 ↓
PostGIS boundary lookup
 ↓
Kerala / Ernakulam
 ↓
industrial_fire profile
 ↓
configured official contact
```

This must be deterministic.

---

# 25. Phase 20 — Routing Policy Engine

## Goal

Prevent alert spam and route events sensibly.

Example rules:

```text
IF normal persistent source
    → dashboard only

IF unknown low-risk source
    → analyst review

IF high-confidence industrial incident
    → primary operational contact

IF forest-fire classification
    → forest/fire response profile

IF abnormal persistent flare
    → plant/pollution profile

IF high severity
    → designated escalation profile
```

### Deduplication rules

- [ ] one notification per event state transition
- [ ] cooldown period
- [ ] no notification for duplicate observations
- [ ] update existing event rather than create another
- [ ] manual resend action only
- [ ] notification audit trail

---

# 26. Phase 21 — Human Notification Interface

## Recommended SIH implementation

Do not make government messaging fully autonomous.

Display:

```text
EVENT
↓
CORRECT JURISDICTION
↓
RECOMMENDED AUTHORITY
↓
VERIFIED CONTACT
```

Actions:

### Send Email

Use either:
- backend-controlled official email integration, OR
- pre-filled `mailto:` link for the prototype

### Call

Use:

```text
tel:+91XXXXXXXXXX
```

### Open portal

Use official portal URL.

### Share alert

Generate a concise alert package containing:
- event ID
- location
- classification
- confidence
- anomaly score
- first/last seen
- supporting evidence
- dashboard link

### Important

The final send/call action remains with the authorized human in the SIH prototype.

---

# 27. Phase 22 — Alert Content

Every alert should contain concise evidence.

Example:

```text
AGNIDRISHTI — High Priority Thermal Event

Event ID:
EVT-2026-001024

Location:
10.1234 N, 76.4567 E

District:
Example District

Classification:
Industrial Fire

Confidence:
91%

Anomaly Score:
0.94

Current FRP:
520 MW

Historical Typical Range:
150–180 MW

First Seen:
2026-08-25 14:21 UTC

Last Seen:
2026-08-25 15:02 UTC

Observations:
7

Reason:
Thermal intensity significantly exceeds
historical baseline for this source.

Dashboard:
<event URL>
```

---

# 28. Phase 23 — FastAPI Backend

## Core API groups

### Health

```text
GET /health
GET /ready
```

### Events

```text
GET /events
GET /events/{event_id}
GET /events/{event_id}/observations
GET /events/{event_id}/timeline
```

### Thermal sources

```text
GET /sources
GET /sources/{source_id}
GET /sources/{source_id}/history
GET /sources/{source_id}/baseline
```

### Dashboard

```text
GET /dashboard/summary
GET /dashboard/map
GET /dashboard/trends
```

### Feedback

```text
POST /events/{event_id}/confirm
POST /events/{event_id}/false-alarm
POST /events/{event_id}/reclassify
```

### Authorities

```text
GET /authorities
GET /authorities/{authority_id}
GET /routing/resolve
```

### Notifications

```text
POST /events/{event_id}/notification-preview
POST /events/{event_id}/notification-log
```

### Administration

```text
POST /authorities
PATCH /authorities/{authority_id}
POST /model/reload
GET /model/current
```

---

# 29. Phase 24 — Celery Worker Architecture

Recommended workers:

```text
firm_ingest_worker
insat_ingest_worker
context_refresh_worker
preprocessing_worker
feature_worker
inference_worker
event_worker
baseline_worker
notification_worker
```

The exact separation can start simpler.

Minimum prototype:

```text
ingestion_worker
processing_worker
notification_worker
```

Then split services if load requires it.

---

# 30. Phase 25 — Database Schema

Minimum production-style tables:

```text
observations
thermal_sources
source_baselines
events
event_observations
industrial_facilities
landuse_features
forest_boundaries
admin_boundaries
authorities
routing_profiles
notifications
operator_feedback
training_labels
model_versions
data_ingestion_runs
audit_logs
```

Important relationships:

```text
thermal_sources 1 ─── N observations

events 1 ─── N observations

events N ─── 1 thermal_source (where applicable)

events N ─── 1 authority/routing profile

events 1 ─── N feedback

models 1 ─── N inference results
```

---

# 31. Phase 26 — Model Versioning

Every prediction should be traceable.

Store:

```text
model_version
feature_set_version
training_dataset_version
prediction_timestamp
```

Example:

```text
model_version = xgb_v1.2
feature_set = features_v1
training_data = dataset_2026_08
```

If a judge asks:

> "Which model generated this alert?"

you should be able to answer exactly.

---

# 32. Phase 27 — Human Feedback / Learning Loop

This is a core feature.

## Operator sees

```text
Prediction:
Industrial fire
Confidence:
84%
```

Operator chooses:

```text
CONFIRM
FALSE ALARM
RECLASSIFY
```

Store:

```text
event_id
model_prediction
model_confidence
human_label
reviewer
timestamp
comment
```

Then:

```text
verified labels
      ↓
training store
      ↓
periodic retraining
      ↓
evaluation
      ↓
new model
```

---

# 33. Phase 28 — Retraining Policy

Do NOT retrain continuously on every observation.

Start with:

```text
manual/on-demand retraining
```

Then consider:

```text
periodic retraining
```

only when enough verified labels accumulate.

Possible trigger:

```text
N new verified labels
OR
scheduled training window
OR
model performance degradation
```

The trigger and N should be decided experimentally.

---

# 34. Phase 29 — Cold Start Strategy

At first deployment, there may be no history.

## Stage 1

Historical backfill:

```text
2020–2026
```

## Stage 2

Build thermal-source candidates.

## Stage 3

Generate initial baselines.

## Stage 4

Train first classifier.

## Stage 5

Deploy.

## Stage 6

Human feedback improves the dataset.

## Stage 7

Retrain.

---

# 35. Phase 30 — Handling Unknown Sources

Never force every hotspot into a known class.

For a new location:

```text
No history
+
uncertain classification
```

create:

```text
UNKNOWN / NEW SOURCE
```

Then monitor.

If it repeatedly appears:

```text
new source candidate
 ↓
source profile
 ↓
human verification
 ↓
thermal registry
```

This is one of the key mechanisms for persistent-source discovery.

---

# 36. Phase 31 — Handling a Normal Persistent Flare

Expected:

```text
Day 1 → active
Day 2 → active
Day 3 → active
...
```

System learns:

```text
known persistent source
normal behaviour
```

Result:

```text
No repeated emergency notification
```

But if:

```text
normal source
    ↓
sudden huge deviation
    ↓
new abnormal event
```

then create an alert candidate.

This behaviour must be explicitly tested.

---

# 37. Phase 32 — Handling Agricultural Fire

Example:

```text
thermal observation
 ↓
farmland
 ↓
known agricultural season
 ↓
historical pattern
 ↓
classification = agricultural burn
```

The event can still appear on the map and contribute to regional statistics.

Do not treat every agricultural hotspot as an industrial emergency.

---

# 38. Phase 33 — Handling Forest Fire

Example:

```text
observation
 ↓
forest boundary
 ↓
FSI/forest context
 ↓
classification
 ↓
forest-fire candidate
 ↓
routing profile
```

Again, routing remains configurable and human-controlled.

---

# 39. Phase 34 — Handling Unknown High-Risk Events

Example:

```text
new hotspot
+
high FRP
+
near industrial facility
+
no historical source
```

Output:

```text
UNKNOWN HIGH-PRIORITY THERMAL EVENT
```

Human review is mandatory.

Do not let "unknown" silently become "industrial fire."

---

# 40. Phase 35 — Backend-to-Frontend Integration

Once APIs work:

### Replace frontend mock data with:

```text
GET /dashboard/summary
GET /events
GET /events/{id}
GET /sources
GET /authorities
```

### Map should consume:

```text
GeoJSON
```

or an equivalent optimized spatial format.

### Event detail should consume:

```text
event
timeline
confidence
anomaly
source history
authority
```

### Feedback actions

Frontend:

```text
Confirm
False Alarm
Reclassify
```

Backend:

```text
POST feedback endpoint
```

---

# 41. Phase 36 — Map Layer Plan

At minimum:

```text
Layer 1: Active events
Layer 2: Persistent sources
Layer 3: Industrial facilities
Layer 4: Forest boundary
Layer 5: Land-use context
Layer 6: District/state boundaries
```

Optional:

```text
Layer 7: Historical thermal density
Layer 8: Anomaly heatmap
Layer 9: event tracks/timeline
```

Do not render every historical observation by default.

Use aggregation/tiling/filtered views.

---

# 42. Phase 37 — Event Detail Page

Every event should answer:

### What?

```text
classification
confidence
```

### Where?

```text
lat/lon
district
nearby facility
```

### When?

```text
first_seen
last_seen
timeline
```

### How severe?

```text
anomaly
priority
```

### Why?

```text
explanation/reasons
```

### What can the user do?

```text
confirm
reclassify
false alarm
contact authority
```

---

# 43. Phase 38 — Explainability

For each prediction, store a small human-readable explanation.

Example:

```text
Likely persistent flare because:
- source has 63 prior active observations
- current location overlaps known industrial context
- thermal pattern matches historical flare behaviour
- no forest/farmland context
```

For anomaly:

```text
Flagged as abnormal because:
- current FRP is 3.4× historical median
- intensity exceeds normal seasonal range
- event duration exceeds historical duration
```

This is more useful than showing raw ML internals to the operator.

---

# 44. Phase 39 — Testing Strategy

## Unit tests

Test:

- [ ] coordinate conversion
- [ ] India boundary filtering
- [ ] H3 assignment
- [ ] spatial joins
- [ ] feature generation
- [ ] baseline calculation
- [ ] anomaly calculation
- [ ] event grouping
- [ ] routing rules
- [ ] notification formatting

## ML tests

- [ ] train/test split correctness
- [ ] leakage checks
- [ ] class imbalance
- [ ] confusion matrix
- [ ] per-class metrics
- [ ] unknown handling
- [ ] model serialization/deserialization
- [ ] prediction reproducibility

## API tests

- [ ] event retrieval
- [ ] source history
- [ ] dashboard statistics
- [ ] feedback
- [ ] authority lookup
- [ ] routing resolution

## Integration tests

```text
FIRMS sample
 ↓
ingestion
 ↓
database
 ↓
features
 ↓
ML
 ↓
event
 ↓
API
 ↓
frontend
```

## E2E test

One synthetic incident should appear on the dashboard and produce the correct human-notification workflow.

---

# 45. Phase 40 — Build a Replay Simulator

This is extremely useful for the SIH demo.

Instead of waiting for live satellite updates during presentation:

```text
historical observations
        ↓
replay engine
        ↓
simulate time progression
        ↓
AGNIDRISHTI processes events
        ↓
dashboard updates
```

Example:

```text
09:00
normal flare

09:30
normal

10:00
normal

10:30
abnormal thermal spike

11:00
persistent anomaly
```

Then demonstrate the entire system without depending on live API availability.

This should be a major demo feature.

---

# 46. Phase 41 — Demo Dataset

Prepare a small deterministic dataset containing:

### Scenario A
Normal persistent flare

### Scenario B
Abnormal flare

### Scenario C
Agricultural burn

### Scenario D
Forest fire

### Scenario E
New unknown source

### Scenario F
Multiple observations belonging to one event

Each scenario should have:
- observations
- expected class
- expected event ID/grouping
- expected severity
- expected routing profile

---

# 47. Phase 42 — Live Data Mode vs Demo Mode

The application should support:

```text
DATA MODE
├── Demo / replay
└── Live
```

### Demo
Uses frozen deterministic data.

### Live
Uses real APIs/configured feeds.

This protects the SIH presentation from:
- API downtime
- rate limits
- network failures
- missing satellite observations

---

# 48. Phase 43 — Observability

Add system metrics:

```text
last_firms_ingestion
last_insat_ingestion
observations_ingested
observations_processed
events_created
events_updated
alerts_generated
false_alarms
processing_latency
model_version
```

Dashboard/admin health:

```text
FIRMS:     ONLINE
INSAT:     ONLINE
DATABASE:  ONLINE
ML MODEL:  READY
CELERY:    ONLINE
```

---

# 49. Phase 44 — Data Freshness

Every source should have:

```text
last_success
last_attempt
status
lag
error
```

Example:

```text
NASA FIRMS
Last update: 17:31 UTC
Status: Healthy

INSAT
Last update: 17:30 UTC
Status: Healthy
```

Do not claim "real time" if the feed isn't.

Use:

> **near-real-time / data-source-dependent**

until actual end-to-end latency is measured.

---

# 50. Phase 45 — Security

Minimum:

- [ ] environment secrets
- [ ] no API keys in frontend
- [ ] backend authentication
- [ ] role-based permissions
- [ ] admin-only authority changes
- [ ] audit logs
- [ ] rate limiting
- [ ] input validation
- [ ] notification confirmation
- [ ] no unauthorized contact modification

---

# 51. Phase 46 — Deployment

Prototype deployment:

```text
Docker Compose
│
├── frontend
├── backend
├── worker
├── redis
└── postgres/postgis
```

Optional separate:

```text
nginx/reverse proxy
```

Later:

```text
on-premise government infrastructure
```

The architecture should not depend on foreign cloud services.

---

# 52. Phase 47 — Data Storage Strategy

Use three levels:

## Raw

Original downloaded source data.

```text
data/raw/
```

## Processed

Normalized observations and extracted features.

```text
data/processed/
```

## Database

Operational records and indexes.

```text
PostgreSQL/PostGIS
```

## ML artifacts

```text
ml/models/
ml/datasets/
ml/evaluation/
```

Never overwrite raw data.

---

# 53. Phase 48 — Data Provenance

Every derived record should be traceable.

Example:

```text
event
 ↓
observations
 ↓
source product
 ↓
raw file/request
```

Store references such as:

```text
source_product
source_record_id
ingestion_run_id
raw_reference
feature_version
model_version
```

This is critical for trust.

---

# 54. Phase 49 — Performance Targets

Do not invent unrealistic final numbers.

Measure:

### Pipeline latency

```text
observation available
        ↓
ingested
        ↓
processed
        ↓
predicted
        ↓
event visible
```

### API latency

Measure:

```text
p50
p95
```

### ML latency

Measure per observation/batch.

### Map loading

Measure first render and event retrieval.

Use measured values in the final presentation.

---

# 55. Phase 50 — Model Evaluation

At minimum calculate:

### Classification

```text
Accuracy
Precision
Recall
F1
Per-class F1
Confusion matrix
```

### Operational

```text
false-alert rate
duplicate-event rate
event detection rate
notification rate
```

### Anomaly detection

Use manually verified abnormal/normal sets.

### Critical

Do not optimize only for accuracy.

For this system:

> Missing a genuinely important abnormal event can be more consequential than producing an extra review candidate.

Therefore report class-wise recall and false-alert behaviour.

---

# 56. Phase 51 — Final SIH Demo Flow

The demo should not be:

```text
Open map
zoom
show dots
```

Instead:

```text
1. Open dashboard
2. Show known persistent thermal source
3. Open source history
4. Show normal baseline
5. Replay new abnormal observations
6. Watch observations merge into one event
7. XGBoost classifies event
8. anomaly engine detects deviation
9. priority becomes HIGH
10. map highlights event
11. authority is resolved from jurisdiction
12. operator opens contact panel
13. preview notification
14. human confirms action
15. operator marks event confirmed
16. feedback becomes training data
```

That demonstrates the whole product.

---

# 57. Recommended Work Breakdown

This is the practical order to give to the team.

## Milestone 1 — Foundation

- [ ] Repository
- [ ] Docker
- [ ] PostgreSQL/PostGIS
- [ ] Redis
- [ ] FastAPI
- [ ] Celery
- [ ] migrations

## Milestone 2 — Data

- [ ] FIRMS ingestion
- [ ] historical backfill
- [ ] administrative boundaries
- [ ] OSM/industrial context
- [ ] land-use
- [ ] forest context

## Milestone 3 — Thermal context

- [ ] MOSDAC/INSAT access
- [ ] thermal extraction
- [ ] quality handling
- [ ] observation normalization

## Milestone 4 — Intelligence

- [ ] source registry
- [ ] baseline
- [ ] features
- [ ] labeled dataset
- [ ] XGBoost
- [ ] anomaly engine
- [ ] event clustering

## Milestone 5 — Operations

- [ ] severity
- [ ] authority directory
- [ ] routing rules
- [ ] notification workflow
- [ ] feedback

## Milestone 6 — Integration

- [ ] FastAPI ↔ DB
- [ ] Frontend ↔ API
- [ ] map layers
- [ ] event details
- [ ] source history
- [ ] authority panel

## Milestone 7 — Demo / Hardening

- [ ] replay engine
- [ ] demo scenarios
- [ ] tests
- [ ] monitoring
- [ ] security
- [ ] Docker finalization
- [ ] architecture documentation
- [ ] SIH demo rehearsal

---

# 58. Suggested Team Task Split

## Developer A — Backend/Data

Own:
- FastAPI
- PostgreSQL/PostGIS
- migrations
- data models
- APIs

## Developer B — Data/Geospatial

Own:
- FIRMS
- MOSDAC
- OSM
- Bhuvan/FSI
- spatial processing
- H3
- preprocessing

## Developer C — ML

Own:
- feature engineering
- labels
- XGBoost
- anomaly detection
- evaluation
- model versioning

## Developer D — Event/Operations

Own:
- event engine
- routing
- authority directory
- notification workflow
- audit/feedback

## Developer E — Frontend Integration

Own:
- existing UI integration
- API consumption
- map layers
- timelines
- event detail
- contact/action UI

> If fewer developers are available, merge Data/Geospatial with ML and Operations with Backend.

---

# 59. Dependency Order

Do not work randomly.

The dependency chain is:

```text
Environment
   ↓
Database
   ↓
Admin boundaries
   ↓
FIRMS ingestion
   ↓
Normalized observations
   ↓
Context enrichment
   ↓
Historical registry
   ↓
Features
   ↓
Training dataset
   ↓
Classifier
   ↓
Anomaly engine
   ↓
Event engine
   ↓
Severity
   ↓
Authority routing
   ↓
FastAPI
   ↓
Frontend integration
   ↓
Notifications
   ↓
Replay/demo
   ↓
Testing
```

Some branches can run in parallel:

```text
Frontend API mocks  ─────────────┐
Database  ──────────────────────┤
FIRMS ingestion ────────────────┤
Admin boundaries ───────────────┤
                                ▼
                         Integration
```

---

# 60. What NOT to Build Before the Core Pipeline Works

Do not spend significant time on:

- [ ] fancy AI chat interface
- [ ] WhatsApp automation
- [ ] fully automated government emailing
- [ ] global coverage
- [ ] deep-learning image model
- [ ] huge cloud infrastructure
- [ ] elaborate mobile app
- [ ] advanced 3D maps
- [ ] autonomous shutdown commands

First prove:

```text
real observation
 ↓
correct features
 ↓
correct classification
 ↓
correct anomaly
 ↓
correct event
 ↓
correct map
```

---

# 61. Minimum Viable AGNIDRISHTI

If implementation time becomes limited, build this exact MVP:

```text
NASA FIRMS
    ↓
India filter
    ↓
PostGIS
    ↓
OSM / admin context
    ↓
Feature extraction
    ↓
XGBoost
    ↓
Historical source baseline
    ↓
Anomaly score
    ↓
Event grouping
    ↓
FastAPI
    ↓
Existing frontend
```

Then add:

```text
authority directory
↓
contact display
↓
email/call/portal actions
```

Then:

```text
human feedback
↓
training dataset
↓
retraining
```

Then add INSAT thermal context if the required MOSDAC access/product is available to the team.

---

# 62. Definition of Done for the Complete Project

The project is considered complete only when:

- [ ] A real FIRMS observation can enter the system.
- [ ] It is stored with provenance.
- [ ] Its geographic context can be resolved.
- [ ] Its historical source context can be retrieved.
- [ ] Features are generated deterministically.
- [ ] The trained model can classify it.
- [ ] Anomaly detection can compare it with history.
- [ ] Multiple detections can become one event.
- [ ] A final event has confidence, anomaly and priority.
- [ ] Event appears in the existing frontend.
- [ ] Correct jurisdiction can be determined.
- [ ] Correct configured authority role can be selected.
- [ ] Contact information can be displayed.
- [ ] Human can preview notification.
- [ ] Human can call/email/open official portal.
- [ ] Human can confirm/reject/reclassify.
- [ ] Feedback is stored.
- [ ] Feedback can enter the training dataset.
- [ ] Model can be retrained.
- [ ] Model version is tracked.
- [ ] Complete flow can run using demo/replay data.
- [ ] Complete flow can run with live data when configured.
- [ ] No major component depends on manual hidden steps.

---

# 63. The Single End-to-End Mental Model

Every team member should understand this:

```text
                  DATA
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
     FIRMS                    INSAT
        │                       │
        └───────────┬───────────┘
                    ▼
              OBSERVATION
                    │
                    ▼
              GEO CONTEXT
                    │
                    ▼
             FEATURE VECTOR
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
     CLASSIFICATION       HISTORY
       XGBoost             BASELINE
          │                   │
          │                   ▼
          │              ANOMALY
          │                   │
          └─────────┬─────────┘
                    ▼
                 EVENT
                    │
                    ▼
               PRIORITY
                    │
                    ▼
              JURISDICTION
                    │
                    ▼
            AUTHORITY DIRECTORY
                    │
                    ▼
             HUMAN VERIFICATION
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
       ACTION              FEEDBACK
          │                   │
          │                   ▼
          │              TRAINING DATA
          │                   │
          │                   ▼
          │              RETRAIN MODEL
          │                   │
          └───────────┬───────┘
                      ▼
                 IMPROVED SYSTEM
```

---

# 64. Final Project Principle

AGNIDRISHTI should **not** be thought of as:

> "an AI model attached to FIRMS."

It is:

> **an India-focused spatio-temporal thermal intelligence platform consisting of data ingestion, geospatial enrichment, historical source memory, classification, anomaly detection, event formation, human verification and configurable authority routing.**

The AI is one part of that system.

The strongest implementation strategy is:

```text
FIRST:
Make one observation go end-to-end.

THEN:
Make historical behaviour work.

THEN:
Make multiple observations become one event.

THEN:
Make the event explainable.

THEN:
Connect it to the existing frontend.

THEN:
Add human feedback.

THEN:
Add retraining.

THEN:
Add authority routing and operational polish.
```

---

# 65. Immediate Next Tasks

These should be the **first concrete development tickets after the current frontend prototype**:

- [ ] **T01 — Create PostgreSQL + PostGIS + Redis Docker environment**
- [ ] **T02 — Create initial database migrations**
- [ ] **T03 — Create administrative boundary seed**
- [ ] **T04 — Implement FIRMS client**
- [ ] **T05 — Import a small India FIRMS sample**
- [ ] **T06 — Store normalized observations**
- [ ] **T07 — Build point → district/state lookup**
- [ ] **T08 — Build OSM/industrial enrichment**
- [ ] **T09 — Create observation API**
- [ ] **T10 — Connect one existing frontend map screen to real API data**
- [ ] **T11 — Build historical-source registry**
- [ ] **T12 — Build feature extraction**
- [ ] **T13 — Prepare first labeled/weakly labeled dataset**
- [ ] **T14 — Train baseline XGBoost**
- [ ] **T15 — Build anomaly baseline**
- [ ] **T16 — Build event grouping**
- [ ] **T17 — Expose event API**
- [ ] **T18 — Connect event detail UI**
- [ ] **T19 — Build authority directory**
- [ ] **T20 — Build routing resolver**
- [ ] **T21 — Build notification preview/action workflow**
- [ ] **T22 — Build feedback endpoints**
- [ ] **T23 — Build replay/demo engine**
- [ ] **T24 — Full end-to-end test**

---

# 66. Definition of the First Working Prototype

The first real milestone should be:

```text
FIRMS sample
   ↓
FastAPI / worker
   ↓
PostGIS
   ↓
district + industrial context
   ↓
basic feature vector
   ↓
baseline XGBoost
   ↓
event object
   ↓
existing frontend
```

Do **not** wait for the complete ML system before integrating the frontend.

Get the first observation onto the existing dashboard as early as possible.

Then progressively replace the mock layers with real intelligence.

---

# 67. Final Implementation Rule

When choosing between a theoretically impressive feature and a feature that can be demonstrated reliably, prioritize:

```text
Reliable
→ Explainable
→ Testable
→ Demonstrable
→ Scalable
```

over:

```text
Complex
→ Unverified
→ Hard to reproduce
→ Dependent on unavailable data
```

The final SIH prototype should be able to demonstrate a **complete, reproducible, India-focused observation-to-decision workflow**, even if some advanced production capabilities remain configurable or future extensions.
