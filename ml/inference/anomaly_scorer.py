"""
Two-layer anomaly detection (AGNIDRISHTI_PLAN.md Phase 14).

Layer 1: statistical baseline deviation (frp_zscore) — interpretable,
         always runs, requires no trained model.
Layer 2: Isolation Forest — catches multivariate anomalies the simple
         z-score misses. Optional: falls back to Layer 1 only if no
         Isolation Forest model is supplied (e.g. cold start, before the
         first `ml/training/train_anomaly.py` run).

Anomaly detection answers "is this unusual?" — never "what is it?".
That question belongs to the classifier (ml/inference/classifier.py).
A known flare operating within its normal range must score LOW here even
if its absolute FRP is high.
"""
from __future__ import annotations

import numpy as np

from ml.features.feature_columns import FEATURE_COLUMNS_V1

Z_SCORE_ANOMALY_THRESHOLD = 3.0
# z-score magnitude past which the statistical component saturates at 1.0
Z_SCORE_SATURATION = 6.0
COMBINED_ANOMALY_FLAG_THRESHOLD = 0.5


def statistical_anomaly(frp_zscore: float | None) -> dict:
    """
    Layer 1: interpretable z-score deviation from the source's own baseline.

    frp_zscore > 3.0 -> anomalous (configurable threshold).
    """
    if frp_zscore is None:
        return {"available": False, "flag": False, "score_component": None}

    flag = abs(frp_zscore) > Z_SCORE_ANOMALY_THRESHOLD
    score_component = min(abs(frp_zscore) / Z_SCORE_SATURATION, 1.0)
    return {"available": True, "flag": flag, "score_component": score_component}


def isolation_forest_anomaly(
    feature_vector: dict,
    model,
    feature_columns: list[str] = FEATURE_COLUMNS_V1,
) -> dict:
    """
    Layer 2: multivariate anomaly score from a per-class Isolation Forest.

    `model` is one entry from the dict produced by
    `ml/training/train_anomaly.py::train_isolation_forests` (keyed by the
    observation's predicted/expected class). Pass None to skip this layer.
    """
    if model is None:
        return {"available": False, "score_component": None, "top_features": []}

    values = [feature_vector.get(c) for c in feature_columns]
    # IsolationForest cannot accept NaN; missing values are imputed with 0
    # for scoring purposes only (training already imputes with the
    # per-class median — 0 is a deliberately neutral stand-in at inference
    # time when a per-request median isn't available).
    x = np.array([[0.0 if v is None or (isinstance(v, float) and np.isnan(v)) else v for v in values]])

    # decision_function: higher = more normal, lower/negative = more anomalous.
    raw = float(model.decision_function(x)[0])
    # score_samples is roughly bounded in [-0.5, 0.5] for typical data; map
    # to an anomaly score in [0, 1] where 1 = most anomalous.
    score_component = float(np.clip(0.5 - raw, 0.0, 1.0))

    top_features = _top_contributing_features(x[0], feature_columns, model)
    return {"available": True, "score_component": score_component, "top_features": top_features}


def _top_contributing_features(x_row: np.ndarray, feature_columns: list[str], model, top_n: int = 3) -> list[str]:
    """
    Approximate feature attribution: how far each feature sits from the
    training data's mean, in units of that feature's training std. This is
    a simple, dependency-free stand-in for full SHAP attribution — good
    enough for a human-readable "why" explanation.
    """
    try:
        means = getattr(model, "_agnidrishti_feature_means", None)
        stds = getattr(model, "_agnidrishti_feature_stds", None)
        if means is None or stds is None:
            return []
        deviations = np.abs((x_row - means) / np.where(stds == 0, 1.0, stds))
        order = np.argsort(deviations)[::-1]
        return [feature_columns[i] for i in order[:top_n]]
    except Exception:
        return []


def compute_anomaly(
    feature_vector: dict,
    source_baseline: dict | None = None,
    isolation_forest_model=None,
    feature_columns: list[str] = FEATURE_COLUMNS_V1,
) -> dict:
    """
    Combined anomaly output.

    Returns:
    {
      "anomaly_score": float,      # 0.0-1.0
      "anomaly_flag": bool,
      "baseline_deviation": float | None,  # frp_zscore
      "anomaly_reason": str
    }
    """
    frp_zscore = feature_vector.get("frp_zscore")
    stat = statistical_anomaly(frp_zscore)
    iso = isolation_forest_anomaly(feature_vector, isolation_forest_model, feature_columns)

    components = [c for c in (stat["score_component"], iso["score_component"]) if c is not None]
    anomaly_score = float(np.mean(components)) if components else 0.0
    anomaly_flag = bool(stat["flag"]) or anomaly_score >= COMBINED_ANOMALY_FLAG_THRESHOLD

    reasons = []
    if stat["available"] and stat["flag"]:
        reasons.append(f"FRP deviates {frp_zscore:.1f} standard deviations from the source baseline")
    if iso["available"] and iso["score_component"] and iso["score_component"] >= COMBINED_ANOMALY_FLAG_THRESHOLD:
        top = ", ".join(iso["top_features"]) if iso["top_features"] else "multiple features"
        reasons.append(f"multivariate pattern is atypical for this source class (driven by: {top})")
    if not reasons:
        reasons.append("within expected range for this source/location" if source_baseline else
                        "no baseline available; anomaly assessment limited to raw feature plausibility")

    return {
        "anomaly_score": round(anomaly_score, 4),
        "anomaly_flag": anomaly_flag,
        "baseline_deviation": frp_zscore,
        "anomaly_reason": "; ".join(reasons),
    }
