"""
Train the XGBoost multiclass classifier.

Classes (5):
  0: Industrial Incident
  1: Persistent Flare/Kiln
  2: Agricultural Burn
  3: Forest Fire
  4: Unknown

Training steps:
1. Load dataset (built by ml/datasets/build_dataset.py)
2. Split into train/val/test by year (temporal split, AGNIDRISHTI_PLAN.md Phase 12)
3. Build feature matrix using ml/features/feature_columns.py FEATURE_COLUMNS_V1
4. Handle missing values — XGBoost supports NaN natively, we pass NaN through
5. Handle class imbalance — inverse-frequency sample weighting
6. Train baseline model with minimal tuning first (defaults + max_depth=6, n_estimators=200)
7. Evaluate on validation set
8. Save model artifact to ml/models/xgb_v1.joblib
9. Save model metadata to ml/models/xgb_v1_metadata.json

Do NOT tune hyperparameters until a working baseline exists.

Online inference != training (AGNIDRISHTI_PLAN.md). This script is the
OFFLINE path only. It is never invoked by the online inference worker.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.utils.class_weight import compute_sample_weight

from ml.datasets.build_dataset import build_training_dataset, temporal_split
from ml.features.feature_columns import CLASS_LABELS, CLASS_TO_IDX, FEATURE_COLUMNS_V1

DEFAULT_MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
DEFAULT_VERSION_TAG = "xgb_v1.0"
DEFAULT_FEATURE_SET_VERSION = "v1"


def _to_matrix(df: pd.DataFrame, feature_columns: list[str] = FEATURE_COLUMNS_V1) -> np.ndarray:
    """Coerce feature columns to a numeric matrix; None/NaN pass through for XGBoost."""
    return df[feature_columns].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)


def _per_class_metrics(y_true: np.ndarray, y_pred: np.ndarray, labels: list[int]) -> dict:
    precisions = precision_score(y_true, y_pred, labels=labels, average=None, zero_division=0)
    recalls = recall_score(y_true, y_pred, labels=labels, average=None, zero_division=0)
    f1s = f1_score(y_true, y_pred, labels=labels, average=None, zero_division=0)
    return {
        CLASS_LABELS[idx]: {
            "precision": float(precisions[i]),
            "recall": float(recalls[i]),
            "f1": float(f1s[i]),
        }
        for i, idx in enumerate(labels)
    }


def train_classifier(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    max_depth: int = 6,
    n_estimators: int = 200,
    feature_columns: list[str] = FEATURE_COLUMNS_V1,
) -> tuple[xgb.XGBClassifier, dict]:
    """
    Train the baseline XGBoost classifier and evaluate on `val_df`.

    Returns (fitted_model, metrics_dict).
    """
    X_train = _to_matrix(train_df, feature_columns)
    y_train = train_df["label"].astype(str).map(CLASS_TO_IDX).to_numpy()

    X_val = _to_matrix(val_df, feature_columns)
    y_val = val_df["label"].astype(str).map(CLASS_TO_IDX).to_numpy()

    sample_weight = compute_sample_weight(class_weight="balanced", y=y_train)

    model = xgb.XGBClassifier(
        objective="multi:softprob",
        num_class=len(CLASS_LABELS),
        max_depth=max_depth,
        n_estimators=n_estimators,
        eval_metric="mlogloss",
        missing=np.nan,
        random_state=42,
    )
    model.fit(X_train, y_train, sample_weight=sample_weight)

    y_pred = model.predict(X_val)
    labels = list(range(len(CLASS_LABELS)))

    metrics = {
        "val_accuracy": float(accuracy_score(y_val, y_pred)),
        "val_precision_macro": float(precision_score(y_val, y_pred, average="macro", zero_division=0)),
        "val_recall_macro": float(recall_score(y_val, y_pred, average="macro", zero_division=0)),
        "val_f1_macro": float(f1_score(y_val, y_pred, average="macro", zero_division=0)),
        "per_class": _per_class_metrics(y_val, y_pred, labels),
        "confusion_matrix": confusion_matrix(y_val, y_pred, labels=labels).tolist(),
    }
    return model, metrics


def save_model(
    model: xgb.XGBClassifier,
    metrics: dict,
    model_dir: Path = DEFAULT_MODEL_DIR,
    version_tag: str = DEFAULT_VERSION_TAG,
    training_data_version: str = "dataset_synthetic_v1",
    feature_columns: list[str] = FEATURE_COLUMNS_V1,
) -> tuple[Path, Path]:
    model_dir.mkdir(parents=True, exist_ok=True)
    slug = version_tag.replace(".", "_")
    model_path = model_dir / f"{slug}.joblib"
    metadata_path = model_dir / f"{slug}_metadata.json"

    joblib.dump(model, model_path)

    metadata = {
        "version_tag": version_tag,
        "feature_set_version": DEFAULT_FEATURE_SET_VERSION,
        "feature_columns": feature_columns,
        "class_labels": CLASS_LABELS,
        "training_data_version": training_data_version,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
        "artifact_path": str(model_path),
        "is_active": True,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2))
    return model_path, metadata_path


def main():
    parser = argparse.ArgumentParser(description="Train the AGNIDRISHTI XGBoost classifier.")
    parser.add_argument("--n-per-class", type=int, default=200,
                         help="Synthetic samples per class (used only when no real dataset is wired in).")
    parser.add_argument("--version-tag", default=DEFAULT_VERSION_TAG)
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR)
    args = parser.parse_args()

    # Integration point: once Contributor 1's DB + Contributor 2's ingestion
    # are live, replace this with a query-backed `records` list instead of
    # the synthetic generator.
    from ml.datasets.synthetic import generate_synthetic_dataset

    records = generate_synthetic_dataset(n_per_class=args.n_per_class)
    df = build_training_dataset(records)
    train_df, val_df, test_df = temporal_split(df)

    print(f"train={len(train_df)} val={len(val_df)} test={len(test_df)}")

    model, metrics = train_classifier(train_df, val_df)
    model_path, metadata_path = save_model(model, metrics, model_dir=args.model_dir, version_tag=args.version_tag)

    print(f"Saved model to {model_path}")
    print(f"Saved metadata to {metadata_path}")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
