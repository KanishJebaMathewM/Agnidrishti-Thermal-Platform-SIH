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
from __future__ import annotations

from datetime import datetime, date

FEATURE_SET_VERSION = "v1"


def _coerce_timestamp(ts):
    """Accept a datetime/date or an ISO-8601 string; return a datetime or None."""
    if ts is None:
        return None
    if isinstance(ts, datetime):
        return ts
    if isinstance(ts, date):
        return datetime(ts.year, ts.month, ts.day)
    if isinstance(ts, str):
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


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
    context = context or {}

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
    ts = _coerce_timestamp(observation.get("timestamp_utc"))
    hour_of_day = ts.hour if ts else None
    day_of_week = ts.weekday() if ts else None  # 0=Monday
    month = ts.month if ts else None
    is_night = 1 if hour_of_day is not None and (hour_of_day < 6 or hour_of_day >= 18) else 0

    # Season encoding (India): 1=Winter, 2=Summer, 3=Monsoon, 4=Post-monsoon
    season = None
    if month is not None:
        if month in (12, 1, 2):
            season = 1
        elif month in (3, 4, 5):
            season = 2
        elif month in (6, 7, 8, 9):
            season = 3
        else:
            season = 4

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
    is_forest = int(bool(context.get("is_forest", False)))
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
