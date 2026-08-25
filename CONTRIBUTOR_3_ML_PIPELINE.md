# CONTRIBUTOR 3 — ML Pipeline (Classification, Anomaly Detection, Event Formation)

> **Branch name to create:** `feat/ml-pipeline`
> **Your domain:** `ml/`, `workers/inference/`, `workers/events/`
> **Do NOT touch:** `frontend/`, `backend/app/api/`, `workers/ingestion/`, `workers/preprocessing/`, `db/migrations/`
> **Push rule:** Always push to `feat/ml-pipeline`. Never push to `main`.

---

## Who you are

You are building the intelligence layer of AGNIDRISHTI.
You own everything from feature engineering to classification, anomaly detection,
spatio-temporal event formation, and the inference worker that ties it all together.

Your output is the `events` table — every thermal anomaly the system surfaces to
human operators flows through your code.

---

## Repository context

**AGNIDRISHTI** classifies satellite thermal observations into:
```
1. Industrial Incident
2. Persistent Flare/Kiln
3. Agricultural Burn
4. Forest Fire
5. Unknown
```

It then determines whether a known source is behaving abnormally (anomaly detection).
Multiple observations near the same location in time get aggregated into a single Event.

Stack: Python, XGBoost, scikit-learn, Pandas, GeoPandas, H3, Celery.

Read `AGNIDRISHTI_PLAN.md` sections 15–22 (Phases 10–17) before starting.
Architecture decisions there are frozen.

The critical rule:
> **Online inference != training.**
> Every new observation runs through the deployed model.
> Training is periodic and independent.

---

## Step 0 — First actions

```
git checkout -b feat/ml-pipeline
```

Read:
- `AGNIDRISHTI_PLAN.md` sections 10 through 22 (Phases 10–17, 22, 26, 27)
- `src/data/mockData.ts` — specifically `ThermalEvent`, the `classification` field,
  `confidence`, `anomaly_score`, `isAnomaly`, `frp`, `baseline`, `current`
- `backend/app/models/event.py` — the event schema you must write to
- `backend/app/models/observation.py` — the observation schema you read from
- `data/samples/sample_firms_india.csv` — sample data for testing

---

## Step 1 — ML Python requirements

Create `ml/requirements.txt`:

```
xgboost==2.1.2
scikit-learn==1.5.2
pandas==2.2.3
numpy==2.1.2
geopandas==1.0.1
shapely==2.0.6
h3==3.7.7
joblib==1.4.2
matplotlib==3.9.2
seaborn==0.13.2
pytest==8.3.3
sqlalchemy==2.0.36
psycopg[binary]==3.2.3
```

---

## Step 2 — Feature engineering

Create `ml/features/feature_builder.py`.

This is the most important file you write. Every ML prediction depends on it.

### Input

A normalized observation dict (from the `observations` table) plus enrichment context.

### Output

A flat Python dict / Pandas Series — the feature vector for that observation.

```python
"""
Feature builder for AGNIDRISHTI classification and anomaly detection.

Feature set version: v1
This version tag must be stored alongside every model trained on these features.
If you add or remove features, increment to v2.

Feature groups:
  A. Thermal     — raw satellite measurements
  B. Temporal    — time-of-day, seasonality, recency
  C. Historical  — deviation from the known source baseline
  D. Geographic  — proximity to industrial/forest/agricultural context
  E. Source state — whether a known source exists at this location
"""

FEATURE_SET_VERSION = "v1"

def build_feature_vector(observation: dict, baseline: dict | None, context: dict) -> dict:
    """
    Build the feature vector for a single observation.

    Args:
        observation: row from observations table (normalized)
        baseline: row from source_baselines for this source/location, or None
        context: geographic enrichment dict with keys:
                 state, district, nearest_industrial_dist_km,
                 nearest_industrial_type, land_use_class,
                 is_forest, nearest_settlement_dist_km

    Returns:
        dict with all feature keys. Missing values are represented as None
        (they will be handled by XGBoost's missing-value support).
    """

    # --- A. Thermal features ---
    frp = observation.get("frp")
    bright_ti4 = observation.get("bright_ti4")
    bright_ti5 = observation.get("bright_ti5")

    # Brightness temperature difference — key discriminator
    # Industrial fires: high ti4 relative to ti5
    # Agricultural: moderate difference
    temp_diff_ti4_ti5 = None
    if bright_ti4 is not None and bright_ti5 is not None:
        temp_diff_ti4_ti5 = bright_ti4 - bright_ti5

    # Confidence encoding: low=0, nominal=1, high=2
    confidence_map = {"low": 0, "nominal": 1, "high": 2}
    confidence_encoded = confidence_map.get(str(observation.get("confidence", "nominal")).lower(), 1)

    # --- B. Temporal features ---
    ts = observation.get("timestamp_utc")
    hour_of_day = ts.hour if ts else None
    day_of_week = ts.weekday() if ts else None  # 0=Monday
    month = ts.month if ts else None
    is_night = 1 if hour_of_day is not None and (hour_of_day < 6 or hour_of_day >= 18) else 0

    # Season encoding (India): 1=Winter, 2=Summer, 3=Monsoon, 4=Post-monsoon
    season = None
    if month is not None:
        if month in (12, 1, 2): season = 1
        elif month in (3, 4, 5): season = 2
        elif month in (6, 7, 8, 9): season = 3
        else: season = 4

    # --- C. Historical / baseline features ---
    frp_deviation = None
    frp_zscore = None
    has_baseline = 0

    if baseline and frp is not None:
        has_baseline = 1
        mean_frp = baseline.get("mean_frp")
        std_frp = baseline.get("frp_std")
        if mean_frp is not None and mean_frp > 0:
            frp_deviation = frp - mean_frp
            if std_frp and std_frp > 0:
                frp_zscore = frp_deviation / std_frp

    # --- D. Geographic features ---
    nearest_industrial_dist = context.get("nearest_industrial_dist_km")
    is_forest = int(context.get("is_forest", False))
    land_use_encoded = _encode_land_use(context.get("land_use_class"))

    # --- E. Source state features ---
    source_exists = 1 if observation.get("source_id") else 0

    return {
        # Thermal
        "frp": frp,
        "bright_ti4": bright_ti4,
        "bright_ti5": bright_ti5,
        "temp_diff_ti4_ti5": temp_diff_ti4_ti5,
        "confidence_encoded": confidence_encoded,
        # Temporal
        "hour_of_day": hour_of_day,
        "day_of_week": day_of_week,
        "month": month,
        "is_night": is_night,
        "season": season,
        # Historical
        "has_baseline": has_baseline,
        "frp_deviation": frp_deviation,
        "frp_zscore": frp_zscore,
        # Geographic
        "nearest_industrial_dist_km": nearest_industrial_dist,
        "is_forest": is_forest,
        "land_use_encoded": land_use_encoded,
        # Source
        "source_exists": source_exists,
        # Metadata (not used as features but carried through)
        "_feature_set_version": FEATURE_SET_VERSION,
        "_observation_id": str(observation.get("id", "")),
    }

def _encode_land_use(land_use_class: str | None) -> int | None:
    """Ordinal encode land use class."""
    mapping = {
        "INDUSTRIAL": 0,
        "AGRICULTURAL": 1,
        "FOREST": 2,
        "SETTLEMENT": 3,
        "WATER": 4,
        "BARREN": 5,
    }
    if land_use_class is None:
        return None
    return mapping.get(str(land_use_class).upper(), 99)
```

### Feature columns list

Create `ml/features/feature_columns.py`:

```python
# Canonical ordered list of feature columns for model input.
# The model must always see features in this exact order.
# NEVER reorder this list. Append new features at the end with a version bump.

FEATURE_COLUMNS_V1 = [
    "frp",
    "bright_ti4",
    "bright_ti5",
    "temp_diff_ti4_ti5",
    "confidence_encoded",
    "hour_of_day",
    "day_of_week",
    "month",
    "is_night",
    "season",
    "has_baseline",
    "frp_deviation",
    "frp_zscore",
    "nearest_industrial_dist_km",
    "is_forest",
    "land_use_encoded",
    "source_exists",
]

CLASS_LABELS = [
    "Industrial Incident",
    "Persistent Flare/Kiln",
    "Agricultural Burn",
    "Forest Fire",
    "Unknown",
]

CLASS_TO_IDX = {c: i for i, c in enumerate(CLASS_LABELS)}
IDX_TO_CLASS = {i: c for i, c in enumerate(CLASS_LABELS)}
```

---

## Step 3 — Training dataset builder

Create `ml/datasets/build_dataset.py`:

```python
"""
Build the labeled training dataset from the observations table.

Label strategy (in priority order):
1. Use human-verified labels from operator_feedback table (highest quality)
2. Use training_labels table (weak labels from rules below)
3. Generate weak labels from rules if no label exists

Weak labeling rules (these are heuristics, not ground truth):
- If source.expected_class is set and confidence > 0.8 → use it
- If observation is in a known forest boundary and month in (3,4,5,10,11) → "Forest Fire" (weak)
- If observation is within 2km of a known industrial facility → "Persistent Flare/Kiln" (weak)
- If observation is on agricultural land and month in (10,11,4,5) → "Agricultural Burn" (weak)
- Otherwise → "Unknown"

IMPORTANT: Store label_source and label_confidence for every label.
Do not force uncertain records into a class. "Unknown" is a valid class.

Temporal split (from AGNIDRISHTI_PLAN.md):
  TRAIN:      2020–2024
  VALIDATION: 2025
  TEST:       2026
"""
```

---

## Step 4 — XGBoost classifier training

Create `ml/training/train_classifier.py`:

```python
"""
Train the XGBoost multiclass classifier.

Classes (5):
  0: Industrial Incident
  1: Persistent Flare/Kiln
  2: Agricultural Burn
  3: Forest Fire
  4: Unknown

Training steps:
1. Load dataset from ml/datasets/ (built by build_dataset.py)
2. Split into train/val/test by year (see temporal split above)
3. Build feature matrix using feature_columns.py FEATURE_COLUMNS_V1
4. Handle missing values — XGBoost supports NaN natively, use that
5. Handle class imbalance — use scale_pos_weight or sample_weight
6. Train baseline model with minimal tuning first
7. Evaluate on validation set
8. Save model artifact to ml/models/xgb_v1.joblib
9. Save model metadata to ml/models/xgb_v1_metadata.json

Model metadata must include:
{
  "version_tag": "xgb_v1.0",
  "feature_set_version": "v1",
  "feature_columns": [...],
  "class_labels": [...],
  "training_data_version": "dataset_2026_08",
  "trained_at": "2026-08-25T00:00:00Z",
  "metrics": {
    "val_accuracy": 0.0,
    "val_precision_macro": 0.0,
    "val_recall_macro": 0.0,
    "val_f1_macro": 0.0,
    "per_class": {}
  }
}

Do NOT tune hyperparameters until you have a working baseline.
Start with XGBoost defaults and max_depth=6, n_estimators=200.
"""
import xgboost as xgb
import joblib
import json
```

---

## Step 5 — Anomaly detection

Create `ml/training/train_anomaly.py` and `ml/inference/anomaly_scorer.py`.

### Two-layer anomaly detection (from AGNIDRISHTI_PLAN.md):

**Layer 1: Statistical baseline deviation**

```python
"""
For each observation with a known source:
  frp_zscore = (current_frp - source_mean_frp) / source_frp_std

If frp_zscore > 3.0 → flag as anomalous (configurable threshold)

This is interpretable and always runs, even without a trained Isolation Forest.
"""
```

**Layer 2: Isolation Forest**

```python
"""
Train an Isolation Forest on the historical feature vectors of known sources.
Use contamination=0.05 (5% expected anomaly rate — adjust after data inspection).

This catches multivariate anomalies that the simple z-score misses.

Output: anomaly_score (float 0–1, higher = more anomalous)
        anomaly_flag (bool)
        anomaly_reason_features (list of top contributing feature names)
"""
from sklearn.ensemble import IsolationForest

# Important: train Isolation Forest separately per source class
# (a flare behaving like a flare is normal; a flare behaving like an incident is not)
```

**Combined anomaly output:**

```python
def compute_anomaly(observation_features: dict, source_baseline: dict | None) -> dict:
    """
    Returns:
    {
      "anomaly_score": float,      # 0.0–1.0
      "anomaly_flag": bool,
      "baseline_deviation": float | None,  # frp_zscore
      "anomaly_reason": str        # human-readable reason
    }
    """
```

---

## Step 6 — Spatio-temporal event formation

Create `workers/events/event_worker.py` (replace stub):

```python
"""
Event formation worker.

This runs after an observation has been preprocessed, enriched, and classified.

Inputs: observation_id

Algorithm (deterministic grouping — not ST-DBSCAN for the prototype):
1. Load the classified observation
2. Look for an existing OPEN event that:
   - has a centroid within 10km of this observation
   - has last_seen within the last 12 hours
   - has the same classification (or is still NEW/ANALYZING)
3. If found: add observation to existing event, update centroid, update stats
4. If not found: create a new event with status=NEW

Event centroid update rule:
  new_centroid = weighted mean of all observation positions (weight by FRP)

Event status transitions:
  NEW → ANALYZING (when first ML result attached)
  ANALYZING → CANDIDATE (when confidence > 0.6 and at least 1 observation)
  CANDIDATE → HUMAN_REVIEW (when severity >= HIGH)
  All other states transition via human feedback API

Event severity calculation (deterministic, from AGNIDRISHTI_PLAN.md Phase 17):
  Score = 0
  + classification_confidence * 30   (max 30 pts)
  + anomaly_score * 30               (max 30 pts)
  + persistence_factor * 20          (max 20 pts)  # nights active / 14
  + frp_intensity_factor * 20        (max 20 pts)  # current_frp / 500 MW

  severity:
    score >= 80 → CRITICAL
    score >= 60 → HIGH
    score >= 40 → REVIEW
    score >= 20 → OBSERVE
    default    → NORMAL
"""
from celery import shared_task

@shared_task(name="workers.events.process_event")
def process_event(observation_id: str):
    pass  # implement full logic
```

---

## Step 7 — Inference worker

Create `workers/inference/inference_worker.py`:

```python
"""
Online inference worker.

This is the online path (see AGNIDRISHTI_PLAN.md):
  New observation (preprocessed + enriched)
       ↓
  Build feature vector
       ↓
  XGBoost classification
       ↓
  Anomaly detection
       ↓
  Store results
       ↓
  Trigger event formation

This worker does NOT retrain the model.
It loads the active model artifact once at startup and reuses it for all predictions.

Model loading:
  1. Query model_versions table for the active model (is_active=True)
  2. Load the artifact from ml/models/ using joblib
  3. Cache in memory (worker-level singleton)
  4. On /model/reload API call: reload from disk
"""
from celery import shared_task
import joblib
import logging

logger = logging.getLogger(__name__)

_model_cache = {}

def get_active_model():
    """Load and cache the active XGBoost model."""
    # Query DB for active model version
    # Load artifact with joblib
    # Return (model, metadata)
    pass

@shared_task(name="workers.inference.run_inference")
def run_inference(observation_id: str):
    """
    Run classification and anomaly detection on a single observation.

    Steps:
    1. Load observation + context from DB
    2. Load source baseline (or None if new source)
    3. Build feature vector
    4. Run XGBoost.predict_proba → class_probabilities, predicted_class
    5. Run anomaly scorer → anomaly_score, anomaly_flag
    6. Store results on the observation record
    7. Trigger process_event.delay(observation_id)
    """
    pass
```

---

## Step 8 — Model evaluation

Create `ml/evaluation/evaluate.py`:

```python
"""
Evaluation script.

Run after training to produce a comprehensive evaluation report.

Must compute:
1. Confusion matrix (5×5)
2. Per-class precision, recall, F1
3. Overall accuracy
4. Macro-averaged metrics
5. Feature importance plot (XGBoost built-in)
6. Calibration curve for confidence scores

Save outputs to ml/evaluation/reports/

The data in src/data/mockData.ts shows example expected metrics:
  precision: 0.91, recall: 0.88, f1: 0.89, accuracy: 0.89
  (these are the targets the UI is already showing as placeholders)

Also compare against a simple baseline:
  "always predict the majority class"
  "predict Industrial if within 2km of industrial facility, else Unknown"
The XGBoost model must outperform both baselines.
"""
```

---

## Step 9 — Baseline engine

Create `ml/training/build_baselines.py`:

```python
"""
Historical baseline builder.

For each thermal source in the thermal_sources table,
compute baseline statistics across its historical observations:

  mean_frp          — mean Fire Radiative Power
  frp_std           — standard deviation
  median_frp        — median FRP
  typical_hours     — histogram of active hours (0–23)
  monthly_profile   — mean FRP per month
  seasonal_profile  — mean FRP per season

Store results in the source_baselines table (one row per source).

Run this:
- Once after initial FIRMS backfill
- Periodically (monthly) to incorporate new verified data

The baseline is what anomaly detection compares against.
An empty baseline means anomaly detection falls back to z-score only.

Script:
  python scripts/build_baselines.py
"""
```

Create `scripts/build_baselines.py` wrapper that calls this module.

---

## Step 10 — ML tests

Create `ml/tests/`:

- `test_feature_builder.py`
  - test that a known observation produces the expected feature vector
  - test that missing FRP produces `frp=None` (not 0)
  - test that feature column order matches FEATURE_COLUMNS_V1
  - test that `_feature_set_version` is present in output

- `test_anomaly_scorer.py`
  - test that frp_zscore > 3.0 → anomaly_flag=True
  - test that frp_zscore < 1.0 → anomaly_flag=False
  - test that missing baseline → anomaly_score based on zscore only

- `test_event_formation.py`
  - test that two observations < 10km apart and < 12h apart → same event
  - test that two observations > 50km apart → different events
  - test that event severity=CRITICAL when score >= 80
  - test that event centroid is weighted mean of observation positions

- `test_inference_worker.py`
  - test that run_inference with sample observation returns expected keys
  - test that model cache is reused on second call

---

## Step 11 — Push

```
git add .
git commit -m "feat: ML pipeline — feature engineering, XGBoost classifier, anomaly detection, event formation"
git push -u origin feat/ml-pipeline
```

---

## Files you will create or modify

```
ml/
  requirements.txt                           (new)
  features/
    feature_builder.py                       (new)
    feature_columns.py                       (new)
  training/
    train_classifier.py                      (new)
    train_anomaly.py                         (new)
    build_baselines.py                       (new)
  datasets/
    build_dataset.py                         (new)
  evaluation/
    evaluate.py                              (new)
    reports/                                 (generated outputs go here)
  inference/
    classifier.py                            (new — thin wrapper around joblib model)
    anomaly_scorer.py                        (new)
  models/                                    (trained artifacts go here — gitignored)
  tests/
    test_feature_builder.py                  (new)
    test_anomaly_scorer.py                   (new)
    test_event_formation.py                  (new)
    test_inference_worker.py                 (new)
workers/
  inference/
    inference_worker.py                      (REPLACE stub)
  events/
    event_worker.py                          (REPLACE stub)
scripts/
  build_baselines.py                         (new)
  evaluate_model.py                          (new)
```

---

## Key rules for this contributor

1. **Feature set versioning is non-negotiable.** Every trained model artifact must be tagged with `feature_set_version`. If you change features, bump the version. Never silently change features under an existing version tag.
2. **XGBoost handles NaN natively.** Do NOT impute missing feature values with 0 or mean. Pass NaN and let XGBoost use its built-in missing value support.
3. **Anomaly != classification.** The anomaly score answers "is this unusual?" — not "what is it?". A known flare operating within its normal range should have a low anomaly score even if it has a high FRP.
4. **Temporal split, not random split.** Train=2020–2024, Val=2025, Test=2026. Never mix time periods across splits.
5. **The model is loaded once per worker.** Use a module-level cache. Do not deserialize the joblib file on every task call.
6. **Event formation is deterministic.** Do not introduce randomness in event grouping. Given the same set of observations in the same order, the same events must be produced.
