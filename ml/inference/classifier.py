"""
Thin wrapper around the joblib-serialized XGBoost classifier.

This is deliberately the only place that knows how to turn a feature dict
into a model prediction. `workers/inference/inference_worker.py` loads one
of these once per worker process and reuses it for every task — it must
never deserialize the joblib artifact on a per-call basis.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np


class ClassifierModel:
    """A loaded XGBoost model paired with the metadata it was trained with."""

    def __init__(self, model, metadata: dict):
        self.model = model
        self.metadata = metadata
        self.feature_columns: list[str] = metadata["feature_columns"]
        self.class_labels: list[str] = metadata["class_labels"]

    @classmethod
    def load(cls, model_path: str | Path, metadata_path: str | Path) -> "ClassifierModel":
        import joblib

        model = joblib.load(model_path)
        metadata = json.loads(Path(metadata_path).read_text())
        return cls(model, metadata)

    def predict(self, feature_vector: dict) -> dict:
        """
        Run classification on a single feature vector.

        Returns:
            {
              "predicted_class": str,
              "class_probabilities": {label: float, ...},
              "confidence": float,               # probability of predicted_class
              "model_version": str,
              "feature_set_version": str,
            }
        """
        row = [_to_float_or_nan(feature_vector.get(col)) for col in self.feature_columns]
        x = np.array([row], dtype=float)

        probabilities = self.model.predict_proba(x)[0]
        idx = int(np.argmax(probabilities))

        return {
            "predicted_class": self.class_labels[idx],
            "class_probabilities": {
                label: float(p) for label, p in zip(self.class_labels, probabilities)
            },
            "confidence": float(probabilities[idx]),
            "model_version": self.metadata.get("version_tag"),
            "feature_set_version": self.metadata.get("feature_set_version"),
        }


def _to_float_or_nan(value) -> float:
    if value is None:
        return np.nan
    try:
        return float(value)
    except (TypeError, ValueError):
        return np.nan
