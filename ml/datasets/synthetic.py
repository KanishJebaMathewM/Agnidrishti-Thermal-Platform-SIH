"""
Synthetic observation generator.

There is no real ingested FIRMS/INSAT data yet (Contributor 2's ingestion
pipeline has not been built). This module produces a small, deterministic,
CLASS-SEPARABLE-BUT-NOISY synthetic dataset so the rest of the ML pipeline
(feature engineering, dataset building, classifier training, anomaly
detection, event formation, evaluation) can be built, exercised, and unit
tested end-to-end without depending on any other contributor's work.

This is explicitly demo/test data — it must never be presented as real
satellite observations. It exists purely to validate the pipeline mechanics
described in AGNIDRISHTI_PLAN.md (Phases 10-17) ahead of real data being
available. Once Contributor 2's ingestion pipeline and Contributor 1's
database are live, `ml/datasets/build_dataset.py` should be pointed at real
`observations` rows instead.

Each generated record is a dict with keys:
  observation   — dict matching the `observations` table shape
  baseline      — dict matching `source_baselines` shape, or None
  context       — geographic enrichment dict (state, district,
                   nearest_industrial_dist_km, land_use_class, is_forest, ...)
  label         — ground-truth class (one of CLASS_LABELS)
  label_source  — "SYNTHETIC_GROUND_TRUTH"
  label_confidence — 1.0
"""
from __future__ import annotations

import random
import uuid
from datetime import datetime, timezone

from ml.features.feature_columns import CLASS_LABELS

# India's rough bounding box, used only to produce plausible-looking lat/lon.
INDIA_LAT_RANGE = (8.0, 34.0)
INDIA_LON_RANGE = (68.0, 97.0)

# Weight each class evenly across the years so temporal train/val/test
# splits (2020-2024 / 2025 / 2026) all get a reasonable sample of every class.
DEFAULT_YEARS = list(range(2020, 2027))


def _rand_datetime(rng: random.Random, year: int, months: list[int] | None = None) -> datetime:
    month = rng.choice(months) if months else rng.randint(1, 12)
    day = rng.randint(1, 28)
    hour = rng.randint(0, 23)
    minute = rng.randint(0, 59)
    return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)


def _make_industrial_incident(rng: random.Random, year: int) -> dict:
    """High-intensity, abrupt deviation near industrial infrastructure."""
    frp = rng.uniform(300, 600)
    obs = {
        "id": str(uuid.uuid4()),
        "frp": round(frp, 1),
        "bright_ti4": round(rng.uniform(350, 400), 1),
        "bright_ti5": round(rng.uniform(295, 320), 1),
        "confidence": rng.choices(["high", "nominal"], weights=[0.7, 0.3])[0],
        "timestamp_utc": _rand_datetime(rng, year),
        "latitude": round(rng.uniform(*INDIA_LAT_RANGE), 4),
        "longitude": round(rng.uniform(*INDIA_LON_RANGE), 4),
        "source_id": str(uuid.uuid4()) if rng.random() < 0.4 else None,
    }
    # If tied to a known source, the current FRP is a large deviation from
    # a much lower historical baseline (sudden abnormal spike).
    baseline = None
    if obs["source_id"]:
        mean_frp = rng.uniform(80, 150)
        baseline = {"mean_frp": round(mean_frp, 1), "frp_std": round(mean_frp * 0.15, 1)}
    context = {
        "state": "Synthetic State",
        "district": "Synthetic District",
        "nearest_industrial_dist_km": round(rng.uniform(0.0, 1.5), 2),
        "land_use_class": "INDUSTRIAL",
        "is_forest": False,
        "nearest_settlement_dist_km": round(rng.uniform(0.5, 5.0), 2),
    }
    return {"observation": obs, "baseline": baseline, "context": context,
            "label": "Industrial Incident"}


def _make_persistent_flare(rng: random.Random, year: int) -> dict:
    """Stable, recurring flare/kiln — current FRP close to its own baseline."""
    mean_frp = rng.uniform(100, 220)
    frp = mean_frp + rng.uniform(-15, 15)
    obs = {
        "id": str(uuid.uuid4()),
        "frp": round(frp, 1),
        "bright_ti4": round(rng.uniform(320, 350), 1),
        "bright_ti5": round(rng.uniform(295, 312), 1),
        "confidence": rng.choices(["nominal", "high"], weights=[0.6, 0.4])[0],
        "timestamp_utc": _rand_datetime(rng, year),
        "latitude": round(rng.uniform(*INDIA_LAT_RANGE), 4),
        "longitude": round(rng.uniform(*INDIA_LON_RANGE), 4),
        "source_id": str(uuid.uuid4()),
    }
    baseline = {"mean_frp": round(mean_frp, 1), "frp_std": round(mean_frp * 0.1, 1)}
    context = {
        "state": "Synthetic State",
        "district": "Synthetic District",
        "nearest_industrial_dist_km": round(rng.uniform(0.0, 3.0), 2),
        "land_use_class": "INDUSTRIAL",
        "is_forest": False,
        "nearest_settlement_dist_km": round(rng.uniform(1.0, 8.0), 2),
    }
    return {"observation": obs, "baseline": baseline, "context": context,
            "label": "Persistent Flare/Kiln"}


def _make_agricultural_burn(rng: random.Random, year: int) -> dict:
    """Low-moderate FRP on farmland, concentrated in harvest-adjacent months."""
    frp = rng.uniform(20, 95)
    obs = {
        "id": str(uuid.uuid4()),
        "frp": round(frp, 1),
        "bright_ti4": round(rng.uniform(305, 330), 1),
        "bright_ti5": round(rng.uniform(292, 305), 1),
        "confidence": rng.choices(["low", "nominal"], weights=[0.5, 0.5])[0],
        "timestamp_utc": _rand_datetime(rng, year, months=[10, 11, 4, 5]),
        "latitude": round(rng.uniform(*INDIA_LAT_RANGE), 4),
        "longitude": round(rng.uniform(*INDIA_LON_RANGE), 4),
        "source_id": None,
    }
    context = {
        "state": "Synthetic State",
        "district": "Synthetic District",
        "nearest_industrial_dist_km": round(rng.uniform(5.0, 40.0), 2),
        "land_use_class": "AGRICULTURAL",
        "is_forest": False,
        "nearest_settlement_dist_km": round(rng.uniform(1.0, 10.0), 2),
    }
    return {"observation": obs, "baseline": None, "context": context,
            "label": "Agricultural Burn"}


def _make_forest_fire(rng: random.Random, year: int) -> dict:
    """Moderate-high FRP inside forest boundary, concentrated in dry months."""
    frp = rng.uniform(80, 300)
    obs = {
        "id": str(uuid.uuid4()),
        "frp": round(frp, 1),
        "bright_ti4": round(rng.uniform(315, 360), 1),
        "bright_ti5": round(rng.uniform(295, 310), 1),
        "confidence": rng.choices(["nominal", "high"], weights=[0.5, 0.5])[0],
        "timestamp_utc": _rand_datetime(rng, year, months=[3, 4, 5, 10, 11]),
        "latitude": round(rng.uniform(*INDIA_LAT_RANGE), 4),
        "longitude": round(rng.uniform(*INDIA_LON_RANGE), 4),
        "source_id": None,
    }
    context = {
        "state": "Synthetic State",
        "district": "Synthetic District",
        "nearest_industrial_dist_km": round(rng.uniform(10.0, 60.0), 2),
        "land_use_class": "FOREST",
        "is_forest": True,
        "nearest_settlement_dist_km": round(rng.uniform(5.0, 30.0), 2),
    }
    return {"observation": obs, "baseline": None, "context": context,
            "label": "Forest Fire"}


def _make_unknown(rng: random.Random, year: int) -> dict:
    """No consistent pattern — deliberately noisy/ambiguous."""
    obs = {
        "id": str(uuid.uuid4()),
        "frp": round(rng.uniform(10, 200), 1) if rng.random() > 0.1 else None,
        "bright_ti4": round(rng.uniform(295, 360), 1) if rng.random() > 0.2 else None,
        "bright_ti5": round(rng.uniform(290, 315), 1) if rng.random() > 0.2 else None,
        "confidence": rng.choice(["low", "nominal", "high"]),
        "timestamp_utc": _rand_datetime(rng, year),
        "latitude": round(rng.uniform(*INDIA_LAT_RANGE), 4),
        "longitude": round(rng.uniform(*INDIA_LON_RANGE), 4),
        "source_id": None,
    }
    context = {
        "state": "Synthetic State",
        "district": "Synthetic District",
        "nearest_industrial_dist_km": round(rng.uniform(0.0, 80.0), 2),
        "land_use_class": rng.choice(["BARREN", "WATER", None]),
        "is_forest": rng.random() < 0.1,
        "nearest_settlement_dist_km": round(rng.uniform(0.0, 40.0), 2),
    }
    return {"observation": obs, "baseline": None, "context": context, "label": "Unknown"}


_GENERATORS = {
    "Industrial Incident": _make_industrial_incident,
    "Persistent Flare/Kiln": _make_persistent_flare,
    "Agricultural Burn": _make_agricultural_burn,
    "Forest Fire": _make_forest_fire,
    "Unknown": _make_unknown,
}


def generate_synthetic_dataset(
    n_per_class: int = 200,
    years: list[int] | None = None,
    seed: int = 42,
) -> list[dict]:
    """
    Generate a deterministic synthetic dataset spanning `years`.

    Returns a list of records:
      {observation, baseline, context, label, label_source, label_confidence}
    """
    years = years or DEFAULT_YEARS
    rng = random.Random(seed)
    records = []
    for label in CLASS_LABELS:
        gen = _GENERATORS[label]
        for _ in range(n_per_class):
            year = rng.choice(years)
            record = gen(rng, year)
            record["label_source"] = "SYNTHETIC_GROUND_TRUTH"
            record["label_confidence"] = 1.0
            records.append(record)
    rng.shuffle(records)
    return records
