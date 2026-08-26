"""
End-to-end smoke tests for the offline training/evaluation path, run
against the synthetic dataset (ml/datasets/synthetic.py) since no real
FIRMS/INSAT data exists yet. These are slower than the unit tests above
but validate that the pieces actually fit together: dataset -> temporal
split -> XGBoost training -> serialization -> reload -> prediction -> beats
the required naive baselines -> anomaly model trains per class.
"""
import json

import pytest

from ml.datasets.build_dataset import build_training_dataset, temporal_split
from ml.datasets.synthetic import generate_synthetic_dataset
from ml.evaluation.evaluate import evaluate_model
from ml.features.feature_columns import CLASS_LABELS
from ml.inference.classifier import ClassifierModel
from ml.training.build_baselines import compute_source_baseline
from ml.training.train_anomaly import train_isolation_forests
from ml.training.train_classifier import save_model, train_classifier


@pytest.fixture(scope="module")
def dataset():
    records = generate_synthetic_dataset(n_per_class=150)
    df = build_training_dataset(records)
    return temporal_split(df)


def test_temporal_split_is_non_empty_and_covers_all_classes(dataset):
    train_df, val_df, test_df = dataset
    assert len(train_df) > 0
    assert len(val_df) > 0
    assert len(test_df) > 0
    assert set(train_df["label"].astype(str)) == set(CLASS_LABELS)


def test_classifier_trains_and_beats_naive_baselines(dataset, tmp_path):
    train_df, val_df, test_df = dataset

    model, val_metrics = train_classifier(train_df, val_df)
    assert 0.0 <= val_metrics["val_accuracy"] <= 1.0
    assert set(val_metrics["per_class"].keys()) == set(CLASS_LABELS)

    report = evaluate_model(model, train_df, test_df, output_dir=tmp_path, model_version="test")

    assert report["outperforms_majority_baseline"]
    assert report["outperforms_proximity_baseline"]
    assert report["model"]["accuracy"] > 0.5
    assert (tmp_path / "evaluation_report.json").exists()


def test_model_round_trips_through_joblib_and_predicts(dataset, tmp_path):
    train_df, val_df, _ = dataset
    model, metrics = train_classifier(train_df, val_df)

    model_path, metadata_path = save_model(model, metrics, model_dir=tmp_path, version_tag="xgb_test.0")
    assert model_path.exists()
    assert metadata_path.exists()

    metadata = json.loads(metadata_path.read_text())
    assert metadata["feature_set_version"] == "v1"
    assert metadata["class_labels"] == CLASS_LABELS
    assert metadata["is_active"] is True

    wrapper = ClassifierModel.load(model_path, metadata_path)
    prediction = wrapper.predict({col: None for col in metadata["feature_columns"]})
    assert prediction["predicted_class"] in CLASS_LABELS
    assert 0.0 <= prediction["confidence"] <= 1.0
    assert abs(sum(prediction["class_probabilities"].values()) - 1.0) < 1e-6


def test_isolation_forest_trains_per_class(dataset):
    train_df, _, _ = dataset
    models = train_isolation_forests(train_df, min_samples=20)
    assert set(models.keys()) <= set(CLASS_LABELS)
    assert len(models) > 0
    for model in models.values():
        assert hasattr(model, "decision_function")


def test_prediction_is_reproducible_across_runs(dataset):
    """AGNIDRISHTI_PLAN.md Phase 39: prediction reproducibility is a required ML test."""
    train_df, val_df, test_df = dataset

    model_a, _ = train_classifier(train_df, val_df)
    model_b, _ = train_classifier(train_df, val_df)

    from ml.training.train_classifier import _to_matrix

    X_test = _to_matrix(test_df)
    probs_a = model_a.predict_proba(X_test)
    probs_b = model_b.predict_proba(X_test)
    assert (probs_a == probs_b).all()


def test_baseline_engine_runs_on_synthetic_source_observations():
    records = generate_synthetic_dataset(n_per_class=20)
    flare_records = [r for r in records if r["label"] == "Persistent Flare/Kiln" and r["observation"].get("source_id")]
    assert flare_records, "synthetic generator should produce at least one sourced flare"

    observations = [r["observation"] for r in flare_records]
    baseline = compute_source_baseline(observations)
    assert baseline["mean_frp"] is not None
    assert baseline["observation_count"] == len(observations)
