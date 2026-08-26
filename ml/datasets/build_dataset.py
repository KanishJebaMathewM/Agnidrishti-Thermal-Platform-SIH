"""
Build the labeled training dataset from the observations table.

Label strategy (in priority order):
1. Use human-verified labels from operator_feedback table (highest quality)
2. Use training_labels table (weak labels persisted from a previous run)
3. Generate weak labels from rules if no label exists

Weak labeling rules (these are heuristics, not ground truth):
- If source.expected_class is set and classification_confidence > 0.8 -> use it
- If observation is in a known forest boundary and month in (3,4,5,10,11) -> "Forest Fire" (weak)
- If observation is within 2km of a known industrial facility -> "Persistent Flare/Kiln" (weak)
- If observation is on agricultural land and month in (10,11,4,5) -> "Agricultural Burn" (weak)
- Otherwise -> "Unknown"

IMPORTANT: Every label carries label_source and label_confidence.
Do not force uncertain records into a class. "Unknown" is a valid class.

Temporal split (from AGNIDRISHTI_PLAN.md, Phase 12):
  TRAIN:      2020-2024
  VALIDATION: 2025
  TEST:       2026

This module has no hard dependency on a live database. It operates on plain
observation/source/context/label dicts (the same shapes
`ml/features/feature_builder.py` consumes) so it can run against:
  - real rows once Contributor 1's DB + Contributor 2's ingestion exist, or
  - the synthetic dataset in `ml/datasets/synthetic.py` for pipeline testing.

Integration point for Contributor 1/2: replace `records` (a list of
{observation, baseline, context, source, human_label, weak_label_row} dicts)
with a query against `observations` joined to `thermal_sources`,
`source_baselines`, geographic enrichment, `operator_feedback`, and
`training_labels`. The labeling/feature logic below does not change.
"""
from __future__ import annotations


import pandas as pd

from ml.features.feature_builder import build_feature_vector, _coerce_timestamp
from ml.features.feature_columns import FEATURE_COLUMNS_V1

FOREST_SEASON_MONTHS = (3, 4, 5, 10, 11)
AGRICULTURAL_SEASON_MONTHS = (10, 11, 4, 5)
INDUSTRIAL_PROXIMITY_KM = 2.0
SOURCE_REGISTRY_CONFIDENCE_THRESHOLD = 0.8

LABEL_SOURCE_HUMAN = "OPERATOR_FEEDBACK"
LABEL_SOURCE_TRAINING_LABEL = "TRAINING_LABELS_TABLE"
LABEL_SOURCE_REGISTRY = "SOURCE_REGISTRY_RULE"
LABEL_SOURCE_FOREST_RULE = "FOREST_SEASONAL_RULE"
LABEL_SOURCE_INDUSTRIAL_RULE = "INDUSTRIAL_PROXIMITY_RULE"
LABEL_SOURCE_AGRI_RULE = "AGRICULTURAL_SEASONAL_RULE"
LABEL_SOURCE_DEFAULT_UNKNOWN = "DEFAULT_UNKNOWN"


def _month_of(observation: dict) -> int | None:
    ts = _coerce_timestamp(observation.get("timestamp_utc"))
    return ts.month if ts else None


def label_observation(
    observation: dict,
    source: dict | None = None,
    context: dict | None = None,
    human_label: dict | None = None,
    weak_label_row: dict | None = None,
) -> dict:
    """
    Resolve the label for a single observation using the priority-ordered
    strategy documented above.

    Returns:
        {label, label_source, label_confidence, verification_status}
    """
    context = context or {}

    # 1. Human-verified label (highest quality)
    if human_label and human_label.get("human_label"):
        return {
            "label": human_label["human_label"],
            "label_source": LABEL_SOURCE_HUMAN,
            "label_confidence": 1.0,
            "verification_status": "VERIFIED",
        }

    # 2. Previously stored weak/rule label
    if weak_label_row and weak_label_row.get("label"):
        return {
            "label": weak_label_row["label"],
            "label_source": weak_label_row.get("label_source", LABEL_SOURCE_TRAINING_LABEL),
            "label_confidence": weak_label_row.get("label_confidence", 0.5),
            "verification_status": weak_label_row.get("verification_status", "UNVERIFIED"),
        }

    # 3. Weak labeling rules
    month = _month_of(observation)

    if source and source.get("expected_class"):
        confidence = source.get("classification_confidence") or 0.0
        if confidence > SOURCE_REGISTRY_CONFIDENCE_THRESHOLD:
            return {
                "label": source["expected_class"],
                "label_source": LABEL_SOURCE_REGISTRY,
                "label_confidence": confidence,
                "verification_status": "UNVERIFIED",
            }

    if context.get("is_forest") and month in FOREST_SEASON_MONTHS:
        return {
            "label": "Forest Fire",
            "label_source": LABEL_SOURCE_FOREST_RULE,
            "label_confidence": 0.5,
            "verification_status": "UNVERIFIED",
        }

    industrial_dist = context.get("nearest_industrial_dist_km")
    if industrial_dist is not None and industrial_dist <= INDUSTRIAL_PROXIMITY_KM:
        return {
            "label": "Persistent Flare/Kiln",
            "label_source": LABEL_SOURCE_INDUSTRIAL_RULE,
            "label_confidence": 0.5,
            "verification_status": "UNVERIFIED",
        }

    if context.get("land_use_class") == "AGRICULTURAL" and month in AGRICULTURAL_SEASON_MONTHS:
        return {
            "label": "Agricultural Burn",
            "label_source": LABEL_SOURCE_AGRI_RULE,
            "label_confidence": 0.5,
            "verification_status": "UNVERIFIED",
        }

    # Do not force an uncertain record into a confident class.
    return {
        "label": "Unknown",
        "label_source": LABEL_SOURCE_DEFAULT_UNKNOWN,
        "label_confidence": 0.3,
        "verification_status": "UNVERIFIED",
    }


def build_training_dataset(records: list[dict]) -> pd.DataFrame:
    """
    Build a flat, model-ready DataFrame from a list of raw records.

    Each record is a dict with keys:
      observation      (required) — raw observation dict
      baseline         (optional) — source_baselines row or None
      context          (optional) — geographic enrichment dict
      source           (optional) — thermal_sources row (for weak labeling)
      human_label      (optional) — operator_feedback row
      weak_label_row   (optional) — previously stored training_labels row
      label            (optional) — pre-resolved ground truth (used by the
                                     synthetic generator; if present it is
                                     trusted as-is instead of re-deriving it)
      label_source, label_confidence — accompany a pre-resolved `label`

    Returns a DataFrame with FEATURE_COLUMNS_V1 + label metadata + `year`
    (derived from timestamp_utc, used for the temporal split).
    """
    rows = []
    for record in records:
        observation = record["observation"]
        baseline = record.get("baseline")
        context = record.get("context") or {}

        if record.get("label"):
            label_info = {
                "label": record["label"],
                "label_source": record.get("label_source", "PROVIDED"),
                "label_confidence": record.get("label_confidence", 1.0),
                "verification_status": record.get("verification_status", "UNVERIFIED"),
            }
        else:
            label_info = label_observation(
                observation,
                source=record.get("source"),
                context=context,
                human_label=record.get("human_label"),
                weak_label_row=record.get("weak_label_row"),
            )

        features = build_feature_vector(observation, baseline, context)
        ts = _coerce_timestamp(observation.get("timestamp_utc"))

        row = {col: features.get(col) for col in FEATURE_COLUMNS_V1}
        row["observation_id"] = features["_observation_id"]
        row["feature_set_version"] = features["_feature_set_version"]
        row["year"] = ts.year if ts else None
        row.update(label_info)
        rows.append(row)

    df = pd.DataFrame(rows)
    if not df.empty:
        # Enforce a stable dtype for label so unknown/absent classes still compare cleanly.
        df["label"] = df["label"].astype("category")
    return df


def temporal_split(
    df: pd.DataFrame,
    train_years: tuple[int, int] = (2020, 2024),
    val_year: int = 2025,
    test_year: int = 2026,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split a dataset built by `build_training_dataset` by year.

    Never mixes time periods across splits (AGNIDRISHTI_PLAN.md Phase 12).
    """
    train_df = df[(df["year"] >= train_years[0]) & (df["year"] <= train_years[1])].copy()
    val_df = df[df["year"] == val_year].copy()
    test_df = df[df["year"] == test_year].copy()
    return train_df, val_df, test_df
