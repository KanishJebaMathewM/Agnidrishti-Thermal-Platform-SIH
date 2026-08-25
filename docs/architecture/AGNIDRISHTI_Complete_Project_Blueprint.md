# AGNIDRISHTI

## National Thermal Anomaly Intelligence Platform

**Problem Statement:** SIH26162 — AI-Based Detection and Classification of Industrial Fires and Persistent Thermal Sources Using NASA FIRMS, OSM & Satellite Data  
**Team:** Tech Pulse  
**Organisation:** National Technical Research Organisation (NTRO)  
**Category:** Software  
**Geographic Scope:** India-focused operational system  
**Prototype Historical Window:** January 2020 to August 2026  
**Core Output:** Classified, monitored, spatially contextualized thermal events  
**Operational Extension:** Human-verified, configurable alert routing — not autonomous emergency command

---

# 1. Project Overview

AGNIDRISHTI is an India-focused geospatial intelligence platform for detecting, classifying, monitoring, and prioritizing thermal anomalies related to industrial activity, persistent thermal sources, forest fires, agricultural burns, and unknown thermal events.

The project is not simply a fire map and not a single machine-learning model.

It is a complete **spatio-temporal decision-support pipeline**:

```text
Detect
  ↓
Contextualize
  ↓
Classify
  ↓
Compare with historical behaviour
  ↓
Form events
  ↓
Prioritize
  ↓
Present on GIS dashboard
  ↓
Human review/action
  ↓
Learn from verified feedback
```

The key idea behind AGNIDRISHTI is **behavioural intelligence**.

A refinery flare, industrial kiln, or thermal facility may be hot every day as part of normal operation. Therefore, simply detecting heat is not enough.

The system answers two separate questions:

1. **What type of thermal source is this?**
2. **Is this source behaving abnormally compared with its own historical behaviour?**

---

# 2. Problem Statement

The SIH problem asks for an AI-based system capable of:

- Detecting thermal anomalies from satellite-based observations.
- Separating industrial fires from forest fires and other natural fires.
- Classifying persistent thermal sources.
- Using thermal anomaly data, satellite imagery, land-cover information, and industrial infrastructure data.
- Storing and visualizing results using a GIS-based interface.

AGNIDRISHTI extends this idea further by adding:

- Historical thermal-source profiling.
- Persistence analysis.
- Anomaly detection.
- Space-time event formation.
- Risk/severity prioritization.
- India-specific administrative jurisdiction mapping.
- Human-reviewed authority routing.
- Operator feedback and periodic model retraining.

> Authority notification is treated as an operational extension. It is not assumed to be a mandatory requirement of the original SIH problem statement.

---

# 3. Core Questions the System Answers

| Question | System Component | Output |
|---|---|---|
| Where is the thermal anomaly? | FIRMS / INSAT ingestion | Observation with location and time |
| What type of source is it? | XGBoost multiclass classifier | 5-class probability vector |
| Is it normal for this location? | Temporal history and baseline engine | Expected range / deviation |
| Is current behaviour abnormal? | Isolation Forest + statistical baseline | Anomaly score |
| Do multiple detections belong to the same event? | ST-DBSCAN + temporal rules | Unified event |
| How important is the event? | Decision engine | Severity / priority |
| Which authority role is relevant? | Jurisdiction + routing rules | Recommended authority role |
| What should the operator do? | Dashboard | Confirm / dismiss / reclassify / notify |

---

# 4. Design Principles

## 4.1 India-First

The system is designed around:

- Indian state boundaries
- Indian district boundaries
- Indian industrial context
- Indian forest/fire context
- India-specific operational jurisdiction mapping

## 4.2 Event-Driven Inference

Every newly available satellite observation can enter inference immediately.

The model is **not retrained** every time new satellite data arrives.

## 4.3 Two-Loop Architecture

The system separates:

### Online Inference Loop
Fast and continuous.

### Offline Training Loop
Periodic and evidence-driven.

## 4.4 Hybrid AI

Different algorithms solve different tasks:

- XGBoost → thermal source classification
- Isolation Forest → anomaly detection
- Statistical baselines → historical deviation
- ST-DBSCAN → space-time event clustering
- Deterministic scoring → prioritization

## 4.5 Historical Memory Lives in the Database

The model itself does not need recurrent memory.

Historical behaviour is stored in:

- thermal-source registry
- event history
- H3 spatial history
- seasonal baselines

## 4.6 Human-in-the-Loop

Operators can:

- confirm detections
- reject false alarms
- reclassify events
- dismiss events
- trigger communication actions

The system does **not** autonomously order:

- plant shutdown
- evacuation
- emergency dispatch

## 4.7 Explainability

Every important event should expose:

- class probabilities
- classification confidence
- anomaly score
- historical baseline
- persistence
- nearby context
- evidence trail
- model version
- operator decisions

## 4.8 Graceful Degradation

Missing satellite data is recorded as missing.

A missing observation must never be interpreted as:

> “There is definitely no fire.”

---

# 5. Finalized System Architecture

```text
NASA FIRMS / INSAT / OSM / Bhuvan / FSI / Admin GIS
                        ↓
                  Data Ingestion
                        ↓
                   Normalization
                        ↓
              Geospatial Enrichment
                        ↓
                Feature Engineering
                        ↓
        ┌───────────────┴────────────────┐
        ↓                                ↓
 XGBoost Classification        History + Anomaly Engine
        ↓                       Statistical Baseline
        ↓                       Isolation Forest
        └───────────────┬────────────────┘
                        ↓
                 Event Formation
              ST-DBSCAN + Rules
                        ↓
                  Decision Engine
                        ↓
              Jurisdiction Routing
                        ↓
                  GIS Dashboard
                        ↓
                 Human Review
                        ↓
                Verified Feedback
                        ↓
              Periodic Retraining
```

---

# 6. Layer-by-Layer Architecture

| Layer | Responsibility | Primary Technologies |
|---|---|---|
| Data Sources | Acquire fire observations, thermal imagery, and context | NASA FIRMS, INSAT/MOSDAC, OSM, Bhuvan, FSI |
| Ingestion | Schedule, download, validate and queue jobs | Python, Celery, Redis |
| Normalization | Standardize coordinates, timestamps, quality fields, IDs | Pandas, NumPy, GeoPandas, Shapely |
| Geospatial Enrichment | Add industrial, land-use, forest, admin context | PostGIS, H3, GeoPandas |
| Feature Engineering | Build thermal, temporal, spatial, historical features | Python, NumPy, Pandas |
| Classification | Estimate source class | XGBoost |
| History / Anomaly | Compare present activity against normal behaviour | Statistical baselines, Isolation Forest |
| Event Engine | Combine multiple observations into one incident/event | ST-DBSCAN + temporal rules |
| Decision Engine | Assign severity and priority | Deterministic scoring / rules |
| Routing | Resolve jurisdiction and authority profile | PostGIS + routing rules |
| Frontend | Display map, evidence, history, actions | React, TypeScript, MapLibre, deck.gl |
| Learning Loop | Store feedback and periodically retrain | Python, XGBoost, model registry |

---

# 7. Data Sources

## 7.1 NASA FIRMS — VIIRS S-NPP 375 m

**Role:**
Primary active-fire / thermal anomaly detection.

**Useful attributes:**
- Fire Radiative Power (FRP)
- brightness temperature
- confidence
- day/night
- acquisition time
- latitude/longitude

**Availability:**
January 2012 to present.

**Prototype Use:**
2020–2026 historical window + Near Real-Time data.

---

## 7.2 NASA FIRMS — VIIRS NOAA-20 375 m

**Role:**
Additional active-fire detections for broader temporal/spatial coverage.

**Availability:**
April 2018 to present.

**Prototype Use:**
2020–2026 + live/NRT.

---

## 7.3 NASA FIRMS — VIIRS NOAA-21 375 m

**Role:**
Newer VIIRS stream for additional coverage.

**Availability:**
January 2024 to present.

**Prototype Use:**
2024–2026 + live/NRT.

---

## 7.4 ISRO INSAT-3D / MOSDAC — 3DIMG_L1C

**Role:**
High-frequency geolocated thermal context between polar satellite detections.

**Characteristics:**
- six-channel imagery
- geolocated
- thermal infrared channels
- approximately half-hourly availability

**Prototype Use:**
2020–2026 selective historical extraction + live data where accessible.

---

## 7.5 ISRO INSAT-3DR / MOSDAC — 3RIMG_L1C

**Role:**
Complementary high-frequency thermal imagery.

**Prototype Use:**
2020–2026 selective extraction + live data where accessible.

---

# 8. Context and Reference Data

## 8.1 OpenStreetMap / Overpass API

Used for:

- refineries
- power plants
- industrial facilities
- roads
- settlements
- infrastructure
- proximity calculations

Strategy:

- current snapshot
- periodic refresh
- no requirement to maintain six years of historical OSM for MVP

---

## 8.2 ISRO Bhuvan

Used for:

- land-use
- land-cover
- thematic geospatial context

Each dataset version should store:

- source
- version
- acquisition date

---

## 8.3 Forest Survey of India

Used for:

- forest boundaries
- forest-fire context
- weak labeling support
- fire segregation support

---

## 8.4 Administrative GIS Boundaries

Used for:

- state mapping
- district mapping
- regional aggregation
- jurisdiction lookup

---

## 8.5 Authority Directory

Used only for the optional human notification layer.

Important design rule:

> Contact information must be maintained as deployment configuration and must not be dynamically scraped from the web at runtime.

---

# 9. Historical Window and Data Split

Recommended prototype historical window:

```text
1 January 2020 → August 2026
```

Suggested temporal ML split:

```text
Training   : 2020–2024
Validation : 2025
Test       : 2026
```

After evaluation:

```text
Production training = entire verified 2020–2026 dataset
```

Why temporal splitting?

Because randomly mixing observations across years can create data leakage.

A temporal split better tests whether the model generalizes to future observations.

---

# 10. Data Ingestion Pipeline

## 10.1 Scheduled Jobs

| Job | Trigger | Output |
|---|---|---|
| FIRMS Poll | Frequent scheduled polling | New thermal observations |
| INSAT Fetch | Availability-aware schedule | Thermal imagery/product records |
| Context Refresh | Daily/weekly/version-based | Updated OSM/Bhuvan/FSI/admin layers |
| Historical Backfill | Manual/controlled batch | Historical observations/features |
| Quality Check | After ingestion batch | Valid records + rejection log |

---

# 11. Normalization Rules

All incoming observations should follow these rules:

1. Convert timestamps internally to UTC.
2. Retain original acquisition timestamp/timezone where available.
3. Normalize coordinates to a common geospatial reference system.
4. Preserve original geometry for audit.
5. Store source-specific observation IDs.
6. Prevent duplicate insertion.
7. Store quality/confidence/cloud information explicitly.
8. Treat missing observations as unknown, not as evidence of no fire.
9. Keep source data linked to derived features.
10. Store processing/version metadata.

---

# 12. Feature Engineering

The machine-learning model does **not** operate on screenshots of maps.

Instead, every detection becomes a structured feature record.

## 12.1 Satellite / Fire Features

Examples:

- FRP
- confidence
- day/night
- acquisition time
- satellite sensor/instrument

Purpose:

Immediate thermal/fire characterization.

---

## 12.2 Thermal Spectral Features

Examples:

- bright_ti4
- bright_ti5
- INSAT TIR-channel values

Purpose:

Thermal characterization.

> Only use fields confirmed to exist in the selected API/product.

---

## 12.3 Temporal Features

Examples:

- hour
- day of week
- month
- day of year
- duration
- time since previous detection

Purpose:

Understand daily and seasonal behaviour.

---

## 12.4 Persistence Features

Examples:

- detections in last 6 hours
- detections in last 24 hours
- detections in last 72 hours
- active days in last 7 days
- active days in last 30 days
- consecutive detections

Purpose:

Differentiate persistent heat sources from one-off incidents.

---

## 12.5 Historical Baseline Features

Examples:

- mean
- median
- standard deviation
- percentiles
- recent deviation
- seasonal baseline

Purpose:

Compare present behaviour against expected behaviour.

---

## 12.6 Spatial / Context Features

Examples:

- distance to industrial facility
- distance to forest
- distance to farmland
- distance to settlement
- land-use type

Purpose:

Understand what kind of environment surrounds a thermal point.

---

## 12.7 Spatial Shape / Event Features

Examples:

- cluster size
- density
- spread
- centroid movement

Purpose:

Support event formation and severity analysis.

---

## 12.8 Source Identity Features

Examples:

- known source flag
- source age
- historical class stability
- persistence score

Purpose:

Support the thermal-source registry.

---

# 13. Machine-Learning Architecture

AGNIDRISHTI contains three distinct AI/analytics jobs.

| AI Component | Question | Method | Output |
|---|---|---|---|
| Classifier | What kind of thermal source is this? | XGBoost multiclass | Class probabilities |
| Anomaly Detector | Is current behaviour unusual? | Isolation Forest + statistics | Anomaly score |
| Event Formation | Which detections belong together? | ST-DBSCAN + temporal rules | Unified event ID |

---

# 14. XGBoost Multiclass Classifier

## 14.1 Target Classes

The classifier predicts five classes:

1. Industrial Incident
2. Persistent Flare / Kiln
3. Agricultural Burn
4. Forest Fire
5. Unknown

## 14.2 Input

A feature vector containing:

- current thermal observation
- geospatial context
- temporal features
- persistence features
- historical information

## 14.3 Output

Example:

```text
Industrial Incident   0.74
Persistent Flare      0.18
Agricultural Burn     0.04
Forest Fire           0.02
Unknown               0.02
```

## 14.4 Confidence Policy

If the highest model probability is below the configured confidence threshold:

```text
Class = Unknown
```

The system must not force low-confidence events into a known category.

## 14.5 Explainability

For each prediction, expose:

- top contributing features
- feature importance
- class probabilities
- model version

---

# 15. Anomaly Detection

The anomaly detector is not another fire classifier.

Its job is to answer:

> Is this thermal source behaving differently from what is normally expected?

Example:

```text
Source: Refinery Flare
Historical FRP: 145–180 MW
Current FRP: 620 MW

Classification: Persistent Flare
Anomaly Score: Very High
```

The source can still be correctly classified as a flare while behaving abnormally.

This distinction is one of the core innovations of AGNIDRISHTI.

---

# 16. Historical Baselines

A baseline can be created for:

- known thermal source
- spatial H3 cell
- seasonal period
- time-of-day period

Important statistics include:

- expected intensity
- duration
- activation frequency
- variability
- seasonal patterns
- persistence

Example:

```text
SOURCE-001284

Expected Class: Persistent Flare
Typical FRP: 145–180 MW
Typical Time: 18:00–06:00
Active Days: 93%
Current FRP: 620 MW

Result:
Classification may remain "Persistent Flare"
but behaviour is highly anomalous.
```

---

# 17. Isolation Forest

Isolation Forest provides a multivariate anomaly score.

Possible inputs:

- FRP
- brightness temperature
- duration
- frequency
- time-of-day
- persistence
- spatial context
- deviation from historical baseline

Why Isolation Forest?

- works well with structured numerical data
- does not require every anomaly to be manually labeled
- suitable when anomalous cases are rare
- easy to combine with deterministic historical rules

---

# 18. Event Formation

One real-world fire can produce many satellite observations.

The system should not create one alert for every pixel.

Example:

```text
Observation 1 → 10:02 at Location A
Observation 2 → 10:05 at Location A + 120 m
Observation 3 → 10:08 at Location A + 180 m

        ↓
ST-DBSCAN + Temporal Rules
        ↓

EVENT-1042
```

This converts multiple satellite detections into one operational event.

---

# 19. Why ST-DBSCAN?

ST-DBSCAN extends density-based clustering using both:

- spatial distance
- temporal distance

It is suitable for satellite observations because a physical event may:

- appear at slightly different coordinates
- be observed several times
- persist over time

The output is a stable event ID containing multiple related observations.

---

# 20. Observation vs Source vs Event

| Entity | Meaning | Example |
|---|---|---|
| Observation | One satellite detection | VIIRS detection at 14:05 |
| Thermal Source | Recurring physical location | Refinery flare stack |
| Event | One bounded incident/episode | Abnormal episode from 14:05–15:10 |

This distinction is important for database design and alert deduplication.

---

# 21. Online Inference Loop

For every new observation:

1. New FIRMS or INSAT observation arrives.
2. Ingestion worker validates and stores it.
3. Spatial context is attached.
4. Thermal-source history is fetched.
5. Feature vector is generated.
6. XGBoost performs inference.
7. Isolation Forest and baseline logic calculate anomaly.
8. Event engine merges observation into an existing event or creates a new one.
9. Decision engine assigns severity/priority.
10. Dashboard updates.
11. Human routing actions are shown if appropriate.

No retraining occurs during this loop.

---

# 22. Offline Training Loop

Training happens periodically:

1. Collect historical observations.
2. Include verified operator outcomes.
3. Construct labels.
4. Generate the same production feature schema.
5. Split data temporally.
6. Train candidate XGBoost model.
7. Evaluate:
   - precision
   - recall
   - F1-score
   - confusion matrix
   - calibration
   - false-alarm behaviour
8. Register model version.
9. Deploy only if acceptance criteria are met.
10. Keep previous model available for rollback.

---

# 23. Training Label Strategy

There is no assumption that a perfect, ready-made labeled Indian industrial-fire dataset exists.

Labels are constructed using **weak supervision + human verification**.

## 23.1 Persistent Flare / Kiln

Possible evidence:

- known persistent thermal locations
- repeated detections
- long-duration recurrence
- industrial context
- independent reference data

## 23.2 Forest Fire

Possible evidence:

- FSI forest-fire references
- intersection with forest boundaries
- temporal fire context
- verified incident information

## 23.3 Agricultural Burn

Possible evidence:

- farmland context
- seasonal recurrence
- independent fire evidence

## 23.4 Industrial Incident

Possible evidence:

- documented incident records
- proximity to industrial facility
- human verification

## 23.5 Unknown

Used when:

- evidence is insufficient
- confidence is low
- the event cannot reliably be classified

---

# 24. Label Confidence

Every training label should store:

- label source
- confidence level
- evidence
- human verification status

Weak labels can be:

- weighted
- filtered
- replaced by verified human labels later

---

# 25. Human Feedback Loop

```text
Model Prediction
      ↓
Operator Review
      ↓
 ┌───────────────┬──────────────┬───────────────┐
 Confirm      False Alarm     Reclassify
 └───────────────┴──────────────┴───────────────┘
      ↓
Verified Training Record
      ↓
Periodic Retraining
      ↓
New Model Version
```

---

# 26. Backend Architecture

| Component | Responsibility | Technology |
|---|---|---|
| API Layer | Dashboard queries, event details, feedback | FastAPI |
| Task Scheduler | Periodic data fetching and processing | Celery Beat |
| Workers | Ingestion, features, inference, events | Celery |
| Broker/Cache | Job queues and short-lived state | Redis |
| Primary Database | Spatial and operational data | PostgreSQL + PostGIS |
| Object Storage | Raw files / selected raster data | S3-compatible storage / local filesystem |
| Model Registry | Model artifacts and metadata | Versioned filesystem/object storage |
| Frontend | GIS dashboard | React + TypeScript |
| Map Rendering | Map and geospatial overlays | MapLibre + deck.gl |
| Deployment | Reproducible environment | Docker / Docker Compose |

---

# 27. Suggested API Endpoints

```http
GET /events
```

List/filter events by:

- region
- class
- severity
- time
- status

```http
GET /events/{id}
```

Return:

- event details
- evidence
- history
- class probabilities
- anomaly score

```http
GET /sources/{id}
```

Return:

- thermal-source history
- historical baseline
- persistence information

```http
GET /map/features
```

Return GIS overlay features.

```http
POST /events/{id}/feedback
```

Actions:

- confirm
- reject
- reclassify

```http
GET /authorities/resolve?lat=&lon=&class=
```

Return configured authority profile.

```http
GET /contacts/{jurisdiction}
```

Return verified official contact details.

```http
GET /models
```

Return active and historical model versions.

```http
GET /health
```

Service health/readiness.

---

# 28. Database Design

## 28.1 satellite_observations

Suggested fields:

- observation_id
- source
- timestamp
- latitude
- longitude
- FRP
- brightness temperature fields
- confidence
- quality

Purpose:

Immutable or append-oriented record of raw/normalized detections.

---

## 28.2 thermal_sources

Fields:

- source_id
- geometry
- expected class
- baseline
- seasonality
- persistence
- status

Purpose:

Long-lived memory for recurring thermal locations.

---

## 28.3 events

Fields:

- event_id
- first_seen
- last_seen
- geometry
- class
- confidence
- anomaly_score
- severity
- status

Purpose:

Operational incident shown on dashboard.

---

## 28.4 event_observations

Fields:

- event_id
- observation_id

Purpose:

Connect observations to events.

---

## 28.5 industrial_facilities

Fields:

- facility_id
- geometry
- type
- name
- provenance

Purpose:

Industrial context and proximity analysis.

---

## 28.6 context_layers

Fields:

- layer_type
- version
- geometry
- attributes

Purpose:

Bhuvan, FSI, admin, land-use and other geospatial layers.

---

## 28.7 authority_contacts

Fields:

- jurisdiction
- role
- email
- phone
- portal
- verified_at
- active

Purpose:

Deployment-managed official contact directory.

---

## 28.8 operator_feedback

Fields:

- event_id
- prediction
- human_label
- decision
- timestamp

Purpose:

Audit evidence + learning data.

---

## 28.9 model_versions

Fields:

- version
- feature_schema
- metrics
- artifact_path
- active

Purpose:

Model reproducibility and rollback.

---

# 29. Authority Routing Architecture

The system routes to an **authority role**, not a random person.

Example logic:

| Event Type | Primary Route | Secondary Route |
|---|---|---|
| High-priority industrial fire | Plant/site emergency role | Local emergency/fire role |
| Abnormal persistent industrial source | Plant/pollution role | District monitoring role |
| Forest fire | Forest/fire response role | District emergency role |
| Agricultural burn | Monitoring/aggregation role | District analyst |
| Unknown high-risk anomaly | Authorized analyst | District role if configured |

The prototype should show:

- verified contact
- pre-filled email option
- call action
- official portal action

---

# 30. Why Not Auto-Discover Contacts?

Government contacts change.

Runtime web scraping creates risks:

- outdated contact
- wrong jurisdiction
- personal contact exposure
- unreliable emergency routing

Therefore:

> Official contacts should be stored in a versioned administrator-managed directory.

---

# 31. Anti-Spam Policy

1. One event gets one event ID.
2. Repeated observations update the same event.
3. Persistent normal sources stay visible but do not repeatedly alert.
4. Escalation may require:
   - sustained anomaly
   - minimum priority
   - human confirmation
5. Notification history is stored.

---

# 32. Dashboard Design

## 32.1 Map View

Filters:

- time
- class
- severity
- district
- status

## 32.2 Event Card

Example:

```text
Classification : Industrial Fire
Confidence     : 91%
Anomaly Score  : 0.94
Current FRP    : 620 MW
Historical     : 145–180 MW
First Seen     : 14:21 UTC
Last Seen      : 15:02 UTC
Jurisdiction   : District X, State Y
```

Actions:

```text
[Confirm]
[Reclassify]
[Dismiss]
[Send Email]
[Call]
[Open Official Portal]
```

---

# 33. What an Operator Should See

The dashboard should expose:

- map location
- event geometry
- current class probabilities
- winning class
- confidence
- anomaly score
- plain-language anomaly reason
- current vs historical comparison
- event timeline
- nearby industrial context
- nearby forest context
- nearby farmland context
- nearby settlements
- jurisdiction
- recommended authority role
- contact information
- notification history
- reviewer decisions

---

# 34. Worked Example — Normal Refinery Flare

1. VIIRS detects recurring heat near a known refinery.
2. OSM/industrial context confirms refinery proximity.
3. Thermal-source registry contains long historical activity.
4. XGBoost predicts:

```text
Persistent Flare / Kiln
```

5. Current FRP is within normal historical range.
6. Isolation Forest anomaly score is low.
7. Dashboard displays:

```text
Normal Persistent Source
```

8. No emergency alert is generated.

---

# 35. Worked Example — Abnormally Hot Persistent Source

1. Known refinery flare is detected.
2. Historical FRP is normally:

```text
145–180 MW
```

3. Current FRP becomes:

```text
620 MW
```

4. XGBoost still classifies:

```text
Persistent Flare
```

5. Anomaly detector identifies severe deviation.
6. Subsequent observations confirm persistent abnormal behaviour.
7. Decision engine assigns high priority.
8. Jurisdiction is resolved.
9. Operator reviews the evidence.
10. Operator may contact the configured authority.
11. Verified outcome is stored for future training.

---

# 36. Worked Example — New Industrial Fire

1. New hotspot appears.
2. No historical thermal-source profile exists.
3. Current thermal/context features are built.
4. XGBoost predicts:

```text
Industrial Incident
```

with high confidence.

5. Since no source-specific baseline exists, the system uses:
   - H3 cell baseline
   - population baseline
   - current persistence
6. Repeated detections are merged into one event.
7. Human review determines whether escalation is necessary.
8. Verified outcome becomes a new training record.

---

# 37. Limitations and Risks

## 37.1 Cloud Cover / Missing Observations

Problem:

Satellite coverage can be blocked or degraded.

Response:

- explicitly record observation gaps
- never interpret missing data as “no fire”

---

## 37.2 Small Fires Below Satellite Detection Limits

Problem:

Some fires may not be detectable.

Response:

AGNIDRISHTI complements ground reporting; it does not replace it.

---

## 37.3 False Alarms

Possible causes:

- hot surfaces
- reflections
- unusual industrial activity

Response:

Use:

- confidence
- thermal context
- spatial context
- persistence
- history
- human feedback

---

## 37.4 No Perfect Indian Labeled Dataset

Problem:

A complete ground-truth dataset may not exist.

Response:

Use:

- weak supervision
- independently verified references
- operator feedback
- temporal evaluation

---

## 37.5 Incomplete Industrial Mapping

Problem:

OSM and other infrastructure maps may be incomplete.

Response:

- fuse multiple context sources
- allow administrator corrections
- keep provenance

---

## 37.6 Changing Authority Contacts

Response:

Use a versioned deployment-managed authority directory.

---

## 37.7 Near-Real-Time Latency

Response:

Measure actual end-to-end prototype latency.

Do not claim an invented real-time guarantee.

---

## 37.8 Model Drift

Response:

- monitor feature distributions
- periodically retrain
- version models
- keep rollback capability

---

## 37.9 Alert Fatigue

Response:

- event-level deduplication
- minimum severity thresholds
- persistence rules
- no repeated alerts for normal persistent sources

---

## 37.10 Sensitive Operational Use

Response:

- on-premise deployment capability
- least-privilege access
- audit logs
- human confirmation

---

# 38. Explicit Non-Goals

AGNIDRISHTI should **not**:

- autonomously shut down industrial plants
- autonomously order evacuation
- autonomously dispatch emergency services
- claim satellite detections are absolute ground truth
- claim uninterrupted universal coverage
- scrape personal contacts
- send uncontrolled mass notifications
- force uncertain events into known classes
- claim prototype latency as a guaranteed operational SLA

---

# 39. Implementation Plan

## Phase 1 — Data Foundation

Build:

- FIRMS India ingestion
- PostGIS schema
- basic context layers

Acceptance:

New observations appear in database with IDs and timestamps.

---

## Phase 2 — Historical Feature Store

Build:

- 2020–2026 FIRMS history
- event-centered INSAT extraction
- context joins

Acceptance:

Feature table can be generated reproducibly.

---

## Phase 3 — Baseline and Persistence

Build:

- thermal-source registry
- H3 history
- seasonal baselines

Acceptance:

Known persistent sources have normal behavioural profiles.

---

## Phase 4 — Classification MVP

Build:

- weak-label dataset
- XGBoost multiclass classifier
- evaluation pipeline

Acceptance:

Produce:

- confusion matrix
- precision
- recall
- F1-score
- per-class metrics

---

## Phase 5 — Anomaly Engine

Build:

- statistical deviation scoring
- Isolation Forest

Acceptance:

Normal and abnormal source behaviour can be distinguished.

---

## Phase 6 — Event Engine

Build:

- ST-DBSCAN
- temporal merging logic

Acceptance:

Multiple detections collapse into one event ID.

---

## Phase 7 — Dashboard

Build:

- India map
- filters
- event cards
- evidence view
- feedback controls

Acceptance:

Operator can review and reclassify events.

---

## Phase 8 — Routing

Build:

- jurisdiction matching
- authority directory
- contact actions

Acceptance:

One event resolves to one configured authority profile.

---

## Phase 9 — Learning Loop

Build:

- feedback store
- model versioning
- retraining script

Acceptance:

Verified labels can become training examples.

---

## Phase 10 — Demo Hardening

Build:

- Docker Compose
- logs
- audit trail
- latency measurement
- reproducible deployment

Acceptance:

Complete system runs end-to-end on a standard server.

---

# 40. Recommended MVP Scope

For SIH, do not attempt every production-grade feature immediately.

A practical MVP should focus on:

1. NASA FIRMS ingestion for India.
2. OSM industrial/land context.
3. PostGIS storage.
4. Feature engineering.
5. XGBoost 5-class classification.
6. Historical baseline.
7. Isolation Forest anomaly score.
8. ST-DBSCAN event clustering.
9. React GIS dashboard.
10. Human feedback.

Optional later enhancements:

- INSAT imagery
- Bhuvan
- FSI weak labels
- authority routing
- automatic periodic retraining
- richer satellite fusion

---

# 41. Recommended Tech Stack

## Backend

- Python
- FastAPI
- Celery
- Redis

## ML / Analytics

- XGBoost
- scikit-learn
- Isolation Forest
- NumPy
- Pandas

## Geospatial

- PostgreSQL
- PostGIS
- GeoPandas
- Shapely
- H3
- ST-DBSCAN

## Frontend

- React
- TypeScript
- MapLibre
- deck.gl

## Deployment

- Docker
- Docker Compose

## Storage

- PostgreSQL/PostGIS
- S3-compatible object storage or local filesystem for prototype

---

# 42. Why XGBoost Instead of Deep Learning?

For the initial prototype, the main limitation is reliable labeled data.

Structured features are already available:

- FRP
- temporal features
- persistence
- industrial proximity
- forest proximity
- seasonality
- historical deviation

XGBoost is:

- strong on tabular data
- faster to train
- easier to explain
- easier to debug
- easier to deploy
- suitable when labeled data is limited

Deep learning can be explored later when a larger verified dataset exists.

---

# 43. Why Not Retrain Every Few Hours?

Training and inference are separate.

New observation:

```text
New data
  ↓
Existing deployed model
  ↓
Immediate inference
```

Training happens only periodically:

```text
Accumulated verified labels
  ↓
Offline retraining
  ↓
Evaluation
  ↓
Model registry
  ↓
Controlled deployment
```

This keeps live inference fast and stable.

---

# 44. Cold-Start Logic

If the system sees a location for the first time:

1. Build current thermal/context features.
2. Use XGBoost classifier.
3. Use H3 or population-level baseline.
4. Calculate anomaly score.
5. If confidence is insufficient:

```text
Class = Unknown
```

6. Human verification may convert it into a new thermal source.

---

# 45. Fire-Image Classifier? No.

AGNIDRISHTI is not merely:

```text
Image → CNN → Fire / No Fire
```

It is a multimodal spatio-temporal system combining:

- active-fire observations
- thermal imagery
- geospatial context
- industrial infrastructure
- forest context
- land-use context
- historical behaviour
- persistence
- anomaly detection
- event clustering

---

# 46. Final System Output

Each operational event should contain:

- event ID
- location
- geometry
- first seen
- last seen
- source class
- class probabilities
- confidence
- anomaly score
- persistence
- current thermal intensity
- historical baseline
- contextual evidence
- nearby facilities
- nearby forest/farmland
- severity
- status
- model version
- audit trail
- recommended routing profile

---

# 47. Judge-Ready Technical Answers

## Q1. Why don't you retrain the model every three hours?

Because training and inference are different processes.

Every incoming satellite observation uses the currently deployed model.

Retraining happens periodically using accumulated verified labels.

---

## Q2. How do you know whether a flare is normal?

The thermal-source registry stores historical:

- intensity
- timing
- duration
- frequency
- seasonal behaviour

The new observation is compared against this baseline.

---

## Q3. What if the system has never seen the location before?

Use:

- current observation
- spatial context
- H3 cell history
- population baseline

If confidence is low, classify as:

```text
Unknown
```

---

## Q4. How do you avoid one alert per satellite pixel?

Related detections are merged using:

- ST-DBSCAN
- temporal rules
- thermal-source history

Notifications are event-based, not pixel-based.

---

## Q5. How do you determine which authority should see an event?

1. Resolve jurisdiction using event coordinates.
2. Determine event type.
3. Map it to configured authority role.
4. Look up verified official contact from deployment-managed directory.

---

## Q6. Does the SIH problem explicitly require authority alerting?

No.

The mandatory core is classification/segregation and GIS-based storage/visualization.

Authority routing is an operational extension.

---

## Q7. Why not deep learning?

Because the prototype's main constraint is labeled data.

Tabular spatial, temporal and physical features are available and easier to explain.

Deep models can be evaluated later.

---

## Q8. What happens during cloud cover?

The observation-quality system records the gap.

Missing data is not interpreted as proof that no fire exists.

---

## Q9. What exactly is the final output?

A GIS-based thermal event record containing:

- class
- confidence
- anomaly score
- persistence
- historical evidence
- spatial context
- severity
- recommended operational routing profile

---

# 48. Novelty

Key novelty areas of AGNIDRISHTI include:

## 48.1 Classification + Behavioural Anomaly Intelligence

Most systems focus on:

> “Is there a hotspot?”

AGNIDRISHTI asks:

> “What is the source, and is this source behaving abnormally?”

---

## 48.2 Persistent Source Intelligence

A refinery flare that burns every day should not generate the same emergency response as a sudden industrial incident.

The system learns long-term thermal behaviour.

---

## 48.3 Space-Time Event Formation

Satellite pixels are converted into meaningful real-world events.

This prevents alert duplication.

---

## 48.4 Explainable Risk Prioritization

Every prioritized event exposes:

- classification
- confidence
- anomaly
- historical baseline
- context
- persistence
- evidence

---

## 48.5 India-Specific Operational Context

The platform is designed around:

- Indian administrative regions
- industrial geography
- forest context
- Indian geospatial sources

---

## 48.6 Human-Verified Learning

Human corrections become verified training evidence for future model versions.

---

# 49. Evaluation Metrics

## Classification Metrics

- Precision
- Recall
- F1-score
- Confusion matrix
- Per-class recall
- Calibration

## Anomaly Metrics

- false positive rate
- anomaly detection precision
- operator confirmation rate
- deviation correctness

## Event Metrics

- clustering accuracy
- duplicate reduction
- event continuity

## Operational Metrics

- end-to-end latency
- number of observations processed
- dashboard response time
- number of false alerts
- model confidence distribution

---

# 50. Suggested Demo Scenario

A strong SIH demo can show three events:

## Scenario A — Normal Persistent Flare

```text
Class: Persistent Flare
Confidence: 94%
Anomaly: 0.12
Status: Normal
Action: No escalation
```

## Scenario B — Abnormal Persistent Flare

```text
Class: Persistent Flare
Confidence: 92%
Historical FRP: 145–180 MW
Current FRP: 620 MW
Anomaly: 0.95
Severity: High
Action: Human review
```

## Scenario C — New Industrial Incident

```text
Class: Industrial Incident
Confidence: 89%
Known Source: No
Industrial Facility Nearby: Yes
Persistence: Increasing
Severity: High
Action: Verify / escalate
```

This demo clearly shows why simple hotspot mapping is insufficient.

---

# 51. Suggested Repository Structure

```text
agnidrishti/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── services/
│   │   ├── ingestion/
│   │   ├── features/
│   │   ├── inference/
│   │   ├── events/
│   │   └── routing/
│   └── requirements.txt
│
├── ml/
│   ├── datasets/
│   ├── labeling/
│   ├── features/
│   ├── training/
│   ├── evaluation/
│   ├── anomaly/
│   └── model_registry/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── map/
│   │   ├── events/
│   │   └── services/
│   └── package.json
│
├── database/
│   ├── migrations/
│   └── seed/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── context/
│
├── scripts/
│   ├── backfill_firms.py
│   ├── fetch_osm.py
│   ├── build_features.py
│   ├── train_classifier.py
│   └── train_anomaly.py
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

# 52. Suggested Development Order

Do not start with the frontend.

Recommended order:

```text
1. FIRMS historical data
2. Database schema
3. OSM context
4. Feature engineering
5. Weak labels
6. XGBoost classifier
7. Historical baseline
8. Isolation Forest
9. ST-DBSCAN
10. FastAPI
11. React GIS dashboard
12. Operator feedback
13. Authority routing
14. Docker deployment
```

---

# 53. Prototype Success Criteria

A successful SIH prototype should demonstrate:

- FIRMS data ingestion works.
- India hotspot observations are stored.
- Industrial/forest/geographic context is joined.
- Thermal events are classified.
- Persistent sources are recognized.
- Abnormal behaviour is detected.
- Repeated detections become one event.
- Events appear on a GIS dashboard.
- Evidence and historical baseline are visible.
- Operator can confirm/reject/reclassify.
- Feedback is stored.
- Model version is recorded.
- Entire demo can run reproducibly.

---

# 54. Final Architecture Checklist

- [ ] India is the operational scope.
- [ ] NASA FIRMS VIIRS is the primary thermal source.
- [ ] INSAT is used as higher-frequency thermal context where accessible.
- [ ] Historical prototype window is 2020–August 2026.
- [ ] Training/validation/test are separated temporally.
- [ ] Inference runs on each newly available observation.
- [ ] Training happens periodically.
- [ ] XGBoost handles source classification.
- [ ] Isolation Forest + statistical history handles anomalies.
- [ ] ST-DBSCAN + temporal rules form events.
- [ ] PostgreSQL/PostGIS stores spatial operational data.
- [ ] H3 supports spatial aggregation/history.
- [ ] Low-confidence cases remain Unknown.
- [ ] Authority routing is optional and configurable.
- [ ] Contact data is deployment-managed.
- [ ] Notifications require human review.
- [ ] No autonomous emergency action is performed.
- [ ] Predictions and operator actions are auditable.
- [ ] Model versions are stored and rollback is possible.

---

# 55. One-Line Architecture

```text
Satellite observations
→ ingestion
→ normalization
→ geospatial context
→ thermal/temporal feature engineering
→ XGBoost classification
→ historical baseline + Isolation Forest anomaly detection
→ ST-DBSCAN event formation
→ priority decision
→ India jurisdiction lookup
→ GIS dashboard
→ human review/notification
→ verified feedback
→ periodic retraining
```

---

# 56. Primary References

## NASA FIRMS

- FIRMS Archive Download  
  https://firms.modaps.eosdis.nasa.gov/download/

- FIRMS VIIRS Fire Hotspots  
  https://firms.modaps.eosdis.nasa.gov/content/descriptions/FIRMS_VIIRS_Firehotspots.html

- FIRMS Active Fire Data  
  https://firms.modaps.eosdis.nasa.gov/content/active_fire/

## ISRO / MOSDAC

- INSAT-3D 3DIMG_L1C_SGP  
  https://mosdac.gov.in/doi/117/

- INSAT-3D Asian Sector L1C  
  https://mosdac.gov.in/doi/123/

- INSAT-3DR 3RIMG_L1C_SGP  
  https://mosdac.gov.in/doi/158/

## India Context

- ISRO Bhuvan  
  https://bhuvan.nrsc.gov.in/

- Forest Survey of India — Forest Fire  
  https://fsiforestfire.gov.in/

- India Government Contact Directory  
  https://www.india.gov.in/directory/contact-directory

## Geospatial / ML Technologies

- OpenStreetMap Overpass API  
  https://wiki.openstreetmap.org/wiki/Overpass_API

- PostGIS  
  https://postgis.net/

- H3  
  https://h3geo.org/docs/

- XGBoost  
  https://xgboost.readthedocs.io/

- scikit-learn Isolation Forest  
  https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html

---

# 57. Final Project Summary

AGNIDRISHTI is designed as a complete thermal anomaly intelligence platform rather than a basic fire-detection map.

Its strongest idea is the separation between:

```text
SOURCE CLASSIFICATION
"What is this?"
```

and:

```text
BEHAVIOURAL ANOMALY DETECTION
"Is it behaving abnormally?"
```

This allows the platform to distinguish:

- normal persistent industrial heat
- abnormal persistent industrial heat
- new industrial incidents
- forest fires
- agricultural burns
- unknown thermal anomalies

The result is an explainable, auditable, India-focused geospatial decision-support system capable of converting raw satellite observations into meaningful operational events.

---

**Project:** AGNIDRISHTI  
**Team:** Tech Pulse  
**Problem Statement:** SIH26162  
**Category:** Software  
**Architecture Baseline:** 25 August 2026
