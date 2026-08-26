"""
Train Isolation Forest models for multivariate anomaly detection
(Layer 2 — see ml/inference/anomaly_scorer.py for Layer 1 + combined output).

Trained separately PER CLASS: a flare behaving like a flare is normal;
a flare behaving like an industrial incident is not. One global model would
blur that distinction (AGNIDRISHTI_PLAN.md Phase 14.2).

contamination=0.05 (5% expected anomaly rate) is a starting point — revisit
once real labeled abnormal/normal sets exist (Phase 50).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

from ml.features.feature_columns import FEATURE_COLUMNS_V1

DEFAULT_MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
CONTAMINATION = 0.05
MIN_SAMPLES_PER_CLASS = 20


def train_isolation_forests(
    df: pd.DataFrame,
    feature_columns: list[str] = FEATURE_COLUMNS_V1,
    contamination: float = CONTAMINATION,
    min_samples: int = MIN_SAMPLES_PER_CLASS,
) -> dict:
    """
    Fit one IsolationForest per class label present in `df`.

    Classes with fewer than `min_samples` rows are skipped — too little
    data to fit a meaningful per-class model; those observations fall back
    to the statistical (z-score) layer only at inference time.
    """
    models: dict[str, IsolationForest] = {}
    for label, group in df.groupby("label", observed=True):
        if len(group) < min_samples:
            continue

        X_raw = group[feature_columns].apply(pd.to_numeric, errors="coerce")
        medians = X_raw.median(numeric_only=True)
        X = X_raw.fillna(medians).to_numpy(dtype=float)

        model = IsolationForest(contamination=contamination, random_state=42)
        model.fit(X)

        # Stash per-feature mean/std on the fitted model so
        # ml/inference/anomaly_scorer.py can produce a lightweight
        # "top contributing features" explanation without a second pass
        # over the training data at inference time.
        model._agnidrishti_feature_means = X.mean(axis=0)
        model._agnidrishti_feature_stds = X.std(axis=0)

        models[str(label)] = model
    return models


def save_isolation_forests(models: dict, model_dir: Path = DEFAULT_MODEL_DIR) -> Path:
    model_dir.mkdir(parents=True, exist_ok=True)
    path = model_dir / "isolation_forest_v1.joblib"
    joblib.dump(models, path)
    return path


def main():
    parser = argparse.ArgumentParser(description="Train per-class Isolation Forest anomaly models.")
    parser.add_argument("--n-per-class", type=int, default=200)
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR)
    args = parser.parse_args()

    from ml.datasets.build_dataset import build_training_dataset, temporal_split
    from ml.datasets.synthetic import generate_synthetic_dataset

    records = generate_synthetic_dataset(n_per_class=args.n_per_class)
    df = build_training_dataset(records)
    train_df, _, _ = temporal_split(df)

    models = train_isolation_forests(train_df)
    path = save_isolation_forests(models, model_dir=args.model_dir)
    print(f"Trained Isolation Forest models for classes: {list(models.keys())}")
    print(f"Saved to {path}")


if __name__ == "__main__":
    main()
