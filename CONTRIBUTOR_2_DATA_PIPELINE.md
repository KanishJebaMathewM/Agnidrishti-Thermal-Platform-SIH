# CONTRIBUTOR 2 — Data Ingestion & Processing Pipeline

> **Branch name to create:** `feat/data-pipeline`
> **Your domain:** `workers/ingestion/`, `workers/preprocessing/`, `workers/enrichment/`, `scripts/`, `data/`
> **Do NOT touch:** `frontend/`, `backend/app/api/`, `ml/`, `db/migrations/`
> **Push rule:** Always push to `feat/data-pipeline`. Never push to `main`.

---

## Who you are

You are building the data engine of AGNIDRISHTI.
You write the code that fetches real satellite fire data, cleans it, enriches it with
geographic context, and stores it in a form the ML pipeline can consume.

If your pipeline is broken, no real data enters the system. Everything else depends on you.

---

## Repository context

**AGNIDRISHTI** detects thermal anomalies in India using:
- **NASA FIRMS / VIIRS** — the primary active-fire feed (satellite point observations)
- **ISRO INSAT / MOSDAC** — geostationary thermal context data

The project uses:
- **PostgreSQL + PostGIS** for storage
- **Celery + Redis** for background job processing
- **Python, Pandas, GeoPandas, Shapely, GDAL/Rasterio** for processing
- **H3** for spatial indexing

Study `AGNIDRISHTI_PLAN.md` before starting. All architecture decisions there are frozen.

---

## Step 0 — First actions

```
git checkout -b feat/data-pipeline
```

Then read:
- `AGNIDRISHTI_PLAN.md` sections 8 through 12 (Phases 3–7)
- `backend/app/models/observation.py` — this is the schema you must populate
- `workers/celery_app.py` — the task stubs Contributor 1 created
- `src/data/mockData.ts` — the `ThermalEvent` and `DataSourceInfo` types show what fields are displayed

You must produce normalized observations that match the `observations` database table schema.
You do NOT design the schema — you write to it.

---

## Step 1 — Workers Python requirements

Create `workers/requirements.txt`:

```
celery==5.4.0
redis==5.1.1
sqlalchemy==2.0.36
geoalchemy2==0.15.2
psycopg[async]==3.2.3
pandas==2.2.3
numpy==2.1.2
geopandas==1.0.1
shapely==2.0.6
pyproj==3.7.0
h3==3.7.7
httpx==0.27.2
rasterio==1.3.11
netCDF4==1.7.1
requests==2.32.3
python-dotenv==1.0.1
pytest==8.3.3
```

---

## Step 2 — Shared utilities

### 2.1 `workers/utils/db.py`

SQLAlchemy synchronous session factory for Celery workers (Celery runs sync tasks):

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://agnidrishti:changeme@localhost/agnidrishti")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_session():
    return SessionLocal()
```

### 2.2 `workers/utils/geo.py`

```python
import h3
from shapely.geometry import Point, shape
import geopandas as gpd

INDIA_H3_RESOLUTION = 7  # approx 5km cells — benchmark this

def lat_lon_to_h3(lat: float, lon: float, resolution: int = INDIA_H3_RESOLUTION) -> str:
    """Convert lat/lon to H3 cell index."""
    return h3.geo_to_h3(lat, lon, resolution)

def is_within_india(lat: float, lon: float, india_geom) -> bool:
    """Check whether a point is inside India's boundary polygon."""
    point = Point(lon, lat)
    return india_geom.contains(point)

def point_to_wkt(lat: float, lon: float) -> str:
    return f"SRID=4326;POINT({lon} {lat})"
```

### 2.3 `workers/utils/india_boundary.py`

```python
# Load the India boundary polygon once at import time.
# The boundary GeoJSON file must be placed at:
#   data/reference/boundaries/india_boundary.geojson
#
# This file is downloaded by the bootstrap script (see Step 5).
# Source: Natural Earth / GADM India boundary (public domain).

import geopandas as gpd
from shapely.ops import unary_union
import os

_india_geom = None

def get_india_geom():
    global _india_geom
    if _india_geom is None:
        path = os.path.join(
            os.path.dirname(__file__), "../../data/reference/boundaries/india_boundary.geojson"
        )
        gdf = gpd.read_file(path)
        _india_geom = unary_union(gdf.geometry)
    return _india_geom
```

---

## Step 3 — NASA FIRMS ingestion worker

### 3.1 FIRMS API overview

NASA FIRMS provides active-fire data via:
- **CSV download API**: `https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/VIIRS_SNPP_NRT/{area}/{days}`
- Area format: `west,south,east,north` bounding box

For India: `65.0,6.0,98.0,38.0`

You need a free MAP_KEY from https://firms.modaps.eosdis.nasa.gov/api/area/

### 3.2 `workers/ingestion/firms_client.py`

Build the HTTP client:

```python
import httpx
import pandas as pd
from io import StringIO
from datetime import date, timedelta
import os
import time

FIRMS_BASE_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"
INDIA_BBOX = "65.0,6.0,98.0,38.0"

# VIIRS SNPP NRT (Near Real-Time) product
PRODUCT_NRT = "VIIRS_SNPP_NRT"
# VIIRS SNPP Standard product (archived)
PRODUCT_STANDARD = "VIIRS_SNPP_SP"

class FIRMSClient:
    def __init__(self, map_key: str):
        self.map_key = map_key
        self.session = httpx.Client(timeout=60.0)

    def fetch_nrt(self, days: int = 1) -> pd.DataFrame:
        """Fetch NRT data for last N days over India bounding box."""
        # days: 1 to 10 for NRT
        url = f"{FIRMS_BASE_URL}/{self.map_key}/{PRODUCT_NRT}/{INDIA_BBOX}/{days}"
        return self._fetch_csv(url)

    def fetch_archive(self, start_date: date, end_date: date) -> pd.DataFrame:
        """Fetch archived data for a date range."""
        # Use the FIRMS archive CSV endpoint
        # Implement date-chunked fetching (max 10 days per request)
        frames = []
        current = start_date
        while current <= end_date:
            chunk_end = min(current + timedelta(days=9), end_date)
            days = (chunk_end - current).days + 1
            url = f"{FIRMS_BASE_URL}/{self.map_key}/{PRODUCT_STANDARD}/{INDIA_BBOX}/{days}"
            try:
                df = self._fetch_csv(url)
                frames.append(df)
            except Exception as e:
                print(f"Warning: failed chunk {current} – {chunk_end}: {e}")
            current = chunk_end + timedelta(days=1)
            time.sleep(1)  # rate limiting
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    def _fetch_csv(self, url: str) -> pd.DataFrame:
        resp = self.session.get(url)
        resp.raise_for_status()
        return pd.read_csv(StringIO(resp.text))
```

### 3.3 `workers/ingestion/firms_normalizer.py`

Convert raw FIRMS DataFrame rows into normalized observation dicts:

```python
import pandas as pd
from datetime import datetime, timezone
import uuid
from workers.utils.geo import lat_lon_to_h3, point_to_wkt

# VIIRS SNPP column names from FIRMS CSV:
# latitude, longitude, bright_ti4, bright_ti5, scan, track,
# acq_date, acq_time, satellite, instrument, confidence,
# version, bright_t31, frp, daynight, type

def normalize_firms_row(row: pd.Series) -> dict:
    """
    Convert a single FIRMS VIIRS row to a normalized observation dict.
    Returns None if the row is invalid.
    """
    try:
        lat = float(row["latitude"])
        lon = float(row["longitude"])
    except (ValueError, KeyError):
        return None

    # Validate coordinates are within plausible India bounding box
    if not (6.0 <= lat <= 38.0 and 65.0 <= lon <= 98.0):
        return None

    # Parse timestamp
    try:
        acq_date = str(row["acq_date"])  # YYYY-MM-DD
        acq_time = str(row.get("acq_time", "0000")).zfill(4)
        timestamp_str = f"{acq_date} {acq_time[:2]}:{acq_time[2:]}:00"
        timestamp_utc = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except Exception:
        return None

    # Confidence: VIIRS uses 'low', 'nominal', 'high'
    confidence = str(row.get("confidence", "nominal")).lower().strip()
    if confidence not in ("low", "nominal", "high"):
        confidence = "nominal"

    frp = _safe_float(row.get("frp"))
    bright_ti4 = _safe_float(row.get("bright_ti4"))
    bright_ti5 = _safe_float(row.get("bright_ti5"))

    # FRP sanity check — VIIRS physically cannot report > 200,000 MW
    if frp is not None and (frp < 0 or frp > 200_000):
        frp = None

    h3_cell = lat_lon_to_h3(lat, lon)
    geometry_wkt = point_to_wkt(lat, lon)

    return {
        "id": str(uuid.uuid4()),
        "source_type": "FIRMS_VIIRS",
        "source_product": str(row.get("version", PRODUCT_NRT)),
        "satellite": str(row.get("satellite", "SNPP")),
        "timestamp_utc": timestamp_utc,
        "latitude": lat,
        "longitude": lon,
        "geometry": geometry_wkt,
        "h3_cell": h3_cell,
        "frp": frp,
        "bright_ti4": bright_ti4,
        "bright_ti5": bright_ti5,
        "confidence": confidence,
        "quality_flags": {
            "daynight": str(row.get("daynight", "D")),
            "scan": _safe_float(row.get("scan")),
            "track": _safe_float(row.get("track")),
        },
        "thermal_features": None,
        "raw_record_ref": row.to_dict(),
        "source_id": None,
    }

def _safe_float(val) -> float | None:
    try:
        v = float(val)
        return None if pd.isna(v) else v
    except (ValueError, TypeError):
        return None
```

### 3.4 `workers/ingestion/firms_worker.py`

Replace the stub from Contributor 1:

```python
from celery import shared_task
from workers.utils.db import get_session
from workers.ingestion.firms_client import FIRMSClient
from workers.ingestion.firms_normalizer import normalize_firms_row
from workers.utils.india_boundary import get_india_geom
from workers.utils.geo import is_within_india
import os
import logging

logger = logging.getLogger(__name__)

@shared_task(name="workers.ingestion.ingest_firms_snapshot", bind=True, max_retries=3)
def ingest_firms_snapshot(self, days: int = 1):
    """
    Celery task: fetch latest FIRMS NRT data and store new observations.

    Steps:
    1. Fetch CSV from FIRMS API for last `days` days
    2. For each row: normalize, validate, deduplicate, persist
    3. Return count of new observations inserted

    Deduplication key: (source_type, satellite, timestamp_utc, latitude, longitude)
    Do not insert if a record with the same key already exists.
    """
    map_key = os.getenv("FIRMS_MAP_KEY", "")
    if not map_key:
        raise ValueError("FIRMS_MAP_KEY not configured")

    client = FIRMSClient(map_key=map_key)
    india_geom = get_india_geom()

    try:
        df = client.fetch_nrt(days=days)
    except Exception as exc:
        logger.error(f"FIRMS fetch failed: {exc}")
        raise self.retry(exc=exc, countdown=60)

    inserted = 0
    session = get_session()
    try:
        for _, row in df.iterrows():
            obs = normalize_firms_row(row)
            if obs is None:
                continue
            # Final India boundary check using PostGIS or shapely
            if not is_within_india(obs["latitude"], obs["longitude"], india_geom):
                continue
            # Deduplication: check if already exists
            # INSERT ... ON CONFLICT DO NOTHING using composite unique constraint
            # (add unique constraint on observations table: satellite + timestamp_utc + latitude + longitude)
            try:
                _insert_observation(session, obs)
                inserted += 1
            except Exception as e:
                session.rollback()
                logger.warning(f"Skipped observation: {e}")
        session.commit()
    finally:
        session.close()

    logger.info(f"FIRMS ingest complete. Inserted: {inserted}")
    return {"inserted": inserted}

def _insert_observation(session, obs: dict):
    """Insert a single normalized observation. Raises on duplicate."""
    from sqlalchemy import text
    session.execute(
        text("""
            INSERT INTO observations
              (id, source_type, source_product, satellite, timestamp_utc,
               latitude, longitude, geometry, h3_cell, frp, bright_ti4,
               bright_ti5, confidence, quality_flags, raw_record_ref)
            VALUES
              (:id, :source_type, :source_product, :satellite, :timestamp_utc,
               :latitude, :longitude, ST_GeomFromText(:geometry),
               :h3_cell, :frp, :bright_ti4, :bright_ti5,
               :confidence, :quality_flags::jsonb, :raw_record_ref::jsonb)
            ON CONFLICT (satellite, timestamp_utc, latitude, longitude) DO NOTHING
        """),
        {**obs, "quality_flags": str(obs["quality_flags"]), "raw_record_ref": str(obs["raw_record_ref"])}
    )
```

---

## Step 4 — Historical backfill script

Create `scripts/backfill_firms.py`:

```python
"""
Run this script once to backfill FIRMS data from 2020 to present.

Usage:
  python scripts/backfill_firms.py --start 2020-01-01 --end 2026-08-25

This will chunk the date range into 10-day windows and ingest each chunk.
Expect this to take several hours for 6 years of data.
Progress is logged so it can be resumed if interrupted.

The script checks the data_ingestion_runs table before each chunk to skip
already-completed runs.
"""
import argparse
from datetime import date, timedelta
from workers.ingestion.firms_client import FIRMSClient
from workers.ingestion.firms_normalizer import normalize_firms_row
# ... implement full script
```

---

## Step 5 — Bootstrap script

Create `scripts/bootstrap.py`:

```python
"""
One-time setup script. Run this before anything else.

What it does:
1. Downloads India boundary GeoJSON from Natural Earth
   and saves to data/reference/boundaries/india_boundary.geojson
2. Downloads India state/district boundaries from GADM
   and saves to data/reference/boundaries/
3. Fetches industrial facility data from OSM Overpass API
   (power plants, refineries, factories) and saves to data/reference/osm/
4. Runs Alembic migrations to initialize the database

Run with:
  python scripts/bootstrap.py
"""

INDIA_BOUNDARY_URL = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
# Note: filter for India from this source or use GADM:
# https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_IND_0.json  (country boundary)
# https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_IND_1.json  (states)
# https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_IND_2.json  (districts)

OSM_OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Overpass query for Indian industrial facilities:
OVERPASS_QUERY = """
[out:json][timeout:300];
area["ISO3166-1"="IN"]->.india;
(
  node["industrial"](area.india);
  way["industrial"](area.india);
  node["power"="plant"](area.india);
  way["power"="plant"](area.india);
  node["man_made"="petroleum_well"](area.india);
  node["man_made"="flare"](area.india);
);
out center;
"""
```

---

## Step 6 — Preprocessing worker

Create `workers/preprocessing/preprocess_worker.py`:

```python
"""
Preprocessing worker.

This worker is triggered after new raw observations are inserted.
It applies quality checks and enrichment to each observation.

Tasks:
1. Validate coordinates are within India boundary (PostGIS check)
2. Check timestamp is reasonable (not in the future, not before 2000)
3. Check FRP is within physical bounds (0 – 200,000 MW)
4. Check brightness temps are within physical bounds (200–500 K)
5. Assign H3 cell if missing
6. Mark quality_flags appropriately
7. Attempt source matching (see Step 7)
"""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task(name="workers.preprocessing.preprocess_observation")
def preprocess_observation(observation_id: str):
    """
    Quality-check and enrich a single observation by ID.
    Updates the observation record in place.
    Does not delete invalid observations — marks them with quality flags.
    """
    # Implement full preprocessing logic here
    pass
```

---

## Step 7 — Enrichment worker: geographic context

Create `workers/enrichment/enrich_geography.py`:

```python
"""
Geographic enrichment worker.

For a given observation (lat, lon), look up:
1. State and district via PostGIS point-in-polygon on admin_boundaries table
2. Nearest industrial facility from industrial_facilities table
3. Land use class from landuse_features table
4. Forest / non-forest from forest_boundaries table

All lookups are PostGIS spatial queries, NOT Python loops.

This data is stored back into the observation or used to build the feature record.

Critical rule from AGNIDRISHTI_PLAN.md:
  "Missing data must not be interpreted as a negative fire observation."
  If geography lookup fails, set fields to NULL — do not guess.
"""
from celery import shared_task

@shared_task(name="workers.enrichment.enrich_geography")
def enrich_geography(observation_id: str):
    """Enrich observation with geographic context from PostGIS."""
    pass
```

---

## Step 8 — Thermal Source Registry updater

Create `workers/enrichment/update_source_registry.py`:

```python
"""
Source registry updater.

After an observation is preprocessed and enriched, this task:
1. Looks for an existing thermal_source with the same H3 cell
2. If found: updates the source statistics (count, last_seen, mean FRP, etc.)
3. If not found: creates a new source record with status=NEW

Source lifecycle transitions handled here:
  NEW → OBSERVED (after first observation stored)
  OBSERVED → CANDIDATE (after N observations over M days, configurable)
  CANDIDATE → MONITORED (after human confirmation via feedback API)
  MONITORED → ARCHIVED (after no observations for K days)

Thresholds (start with these, adjust based on data):
  N = 3 observations before becoming CANDIDATE
  M = 7 days window
  K = 90 days inactivity before ARCHIVED
"""
from celery import shared_task

@shared_task(name="workers.enrichment.update_source_registry")
def update_source_registry(observation_id: str):
    pass
```

---

## Step 9 — Data ingestion run tracking

Create `workers/ingestion/ingestion_tracker.py`:

```python
"""
Track each ingestion run in the data_ingestion_runs table.
This is used by the backfill script to resume interrupted runs
and by the dashboard to show data freshness.

Schema for data_ingestion_runs:
  id UUID
  source_type VARCHAR  -- FIRMS_VIIRS, INSAT
  run_start TIMESTAMPTZ
  run_end TIMESTAMPTZ
  status VARCHAR  -- RUNNING, SUCCESS, FAILED
  records_fetched INT
  records_inserted INT
  error_message TEXT
  parameters JSONB  -- date range, product, etc.
"""
```

---

## Step 10 — Sample data for development

Create `data/samples/sample_firms_india.csv`:

A small CSV with 20–30 manually crafted realistic FIRMS VIIRS rows
covering a mix of Indian states, classifications, and confidence levels.

Columns must match actual FIRMS VIIRS CSV format:
`latitude,longitude,bright_ti4,bright_ti5,scan,track,acq_date,acq_time,satellite,instrument,confidence,version,bright_t31,frp,daynight,type`

Example row:
```
28.6139,77.2090,365.2,308.1,0.39,0.36,2026-08-25,0315,N,VIIRS,nominal,2.0NRT,300.4,42.1,N,0
```

This sample data lets Contributor 3 (ML) and Contributor 4 (frontend) work without needing
a live FIRMS API key.

---

## Step 11 — Worker tests

Create `workers/tests/`:
- `test_firms_normalizer.py` — unit tests for normalize_firms_row
  - valid row → correct dict
  - row with invalid coordinates → returns None
  - row with out-of-India coordinates → skipped after india_boundary check
  - row with NaN FRP → frp=None in output
- `test_geo_utils.py` — unit tests for H3 conversion and WKT generation
- `test_ingestion_dedup.py` — test that duplicate rows are not inserted twice

---

## Step 12 — Push

```
git add .
git commit -m "feat: FIRMS ingestion pipeline, preprocessing, geographic enrichment, source registry"
git push -u origin feat/data-pipeline
```

---

## Files you will create or modify

```
workers/
  requirements.txt                           (new)
  Dockerfile                                 (new)
  celery_app.py                              (REPLACE stub from Contributor 1)
  utils/
    db.py                                    (new)
    geo.py                                   (new)
    india_boundary.py                        (new)
  ingestion/
    firms_client.py                          (new)
    firms_normalizer.py                      (new)
    firms_worker.py                          (REPLACE stub)
    ingestion_tracker.py                     (new)
  preprocessing/
    preprocess_worker.py                     (REPLACE stub)
    quality_checks.py                        (new)
  enrichment/
    enrich_geography.py                      (new)
    update_source_registry.py                (new)
  tests/
    test_firms_normalizer.py                 (new)
    test_geo_utils.py                        (new)
    test_ingestion_dedup.py                  (new)
scripts/
  bootstrap.py                               (new)
  backfill_firms.py                          (new)
data/
  reference/boundaries/                      (bootstrap downloads here)
  reference/osm/                             (bootstrap downloads here)
  samples/
    sample_firms_india.csv                   (new)
```

---

## Key rules for this contributor

1. **Preserve raw records.** Store the original FIRMS row in `raw_record_ref` JSONB so observations can be replayed.
2. **Never interpret missing data as "no fire."** If a lookup fails, store NULL — do not infer absence.
3. **India boundary clips first.** The FIRMS bounding box is rectangular. The actual India boundary is not. Always do the PostGIS point-in-polygon check after the initial bbox filter.
4. **No on-the-fly ML in this worker.** You normalize, enrich, and store. Classification is Contributor 3's job.
5. **Rate limit all external HTTP calls.** Both FIRMS and Overpass have rate limits. Add `time.sleep(1)` between chunks and respect `Retry-After` headers.
6. **The backfill script must be resumable.** It must check `data_ingestion_runs` before each chunk and skip already-completed windows.
