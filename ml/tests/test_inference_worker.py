from datetime import datetime, timezone

import pytest

from ml.features.feature_columns import CLASS_LABELS
from ml.inference.classifier import ClassifierModel
from workers.inference import inference_worker
from workers.inference.inference_worker import (
    InMemoryInferenceStore,
    get_active_model,
    run_inference,
    run_inference_logic,
)


class FakeClassifier:
    """Stands in for a loaded ClassifierModel without needing a trained artifact."""

    def predict(self, feature_vector: dict) -> dict:
        return {
            "predicted_class": "Persistent Flare/Kiln",
            "class_probabilities": {c: (0.8 if c == "Persistent Flare/Kiln" else 0.05) for c in CLASS_LABELS},
            "confidence": 0.8,
            "model_version": "test_v0",
            "feature_set_version": "v1",
        }


def _sample_observation():
    return {
        "id": "obs-100",
        "frp": 180.0,
        "bright_ti4": 330.0,
        "bright_ti5": 305.0,
        "confidence": "nominal",
        "timestamp_utc": datetime(2026, 6, 1, 12, 0, tzinfo=timezone.utc),
        "latitude": 21.0,
        "longitude": 79.0,
        "source_id": "src-100",
    }


EXPECTED_RESULT_KEYS = {
    "observation_id",
    "predicted_class",
    "class_probabilities",
    "confidence",
    "model_version",
    "feature_set_version",
    "anomaly_score",
    "anomaly_flag",
    "baseline_deviation",
    "anomaly_reason",
}


def test_run_inference_logic_returns_expected_keys():
    result = run_inference_logic(
        _sample_observation(), baseline=None, context={}, classifier=FakeClassifier(), isolation_forest_models=None
    )
    assert EXPECTED_RESULT_KEYS.issubset(result.keys())
    assert result["predicted_class"] == "Persistent Flare/Kiln"
    assert result["observation_id"] == "obs-100"


def test_run_inference_logic_with_baseline_produces_anomaly_deviation():
    baseline = {"mean_frp": 40.0, "frp_std": 10.0}
    result = run_inference_logic(
        _sample_observation(), baseline=baseline, context={}, classifier=FakeClassifier(), isolation_forest_models=None
    )
    # frp=180, mean=40, std=10 -> zscore = 14.0, well past the anomaly threshold
    assert result["baseline_deviation"] == pytest.approx(14.0)
    assert result["anomaly_flag"] is True


class _CountingModelStore:
    def __init__(self, info: dict):
        self._info = info
        self.calls = 0

    def get_active_model_info(self):
        self.calls += 1
        return self._info


def test_model_cache_reused_on_second_call(monkeypatch):
    load_calls = []

    def fake_load(cls, model_path, metadata_path):
        load_calls.append((model_path, metadata_path))
        return FakeClassifier()

    monkeypatch.setattr(ClassifierModel, "load", classmethod(fake_load))
    inference_worker._model_cache.clear()

    store = _CountingModelStore(
        {"version_tag": "test_v_cache", "artifact_path": "dummy.joblib", "metadata_path": "dummy.json"}
    )

    model1 = get_active_model(store)
    model2 = get_active_model(store)

    assert model1 is model2
    assert len(load_calls) == 1
    # The store itself may be queried each time (cheap metadata lookup) —
    # what must not repeat is the expensive joblib deserialization.
    assert store.calls == 2


def test_run_inference_task_persists_result_and_triggers_event_formation(monkeypatch):
    inference_store = InMemoryInferenceStore()
    observation = _sample_observation()
    inference_store.add_observation(observation, baseline={"mean_frp": 150.0, "frp_std": 15.0})

    class _FixedModelStore:
        def get_active_model_info(self):
            return {"version_tag": "test_v_task", "artifact_path": "x", "metadata_path": "y"}

    monkeypatch.setattr(ClassifierModel, "load", classmethod(lambda cls, *a, **k: FakeClassifier()))
    inference_worker._model_cache.clear()

    triggered = {}

    def fake_trigger(observation_id):
        triggered["observation_id"] = observation_id

    monkeypatch.setattr(inference_worker, "_trigger_event_formation", fake_trigger)

    result = run_inference("obs-100", store=inference_store, model_store=_FixedModelStore())

    assert result["predicted_class"] == "Persistent Flare/Kiln"
    assert inference_store.get_inference_result("obs-100") == result
    assert triggered["observation_id"] == "obs-100"


def test_run_inference_missing_observation_returns_none():
    empty_store = InMemoryInferenceStore()

    class _FixedModelStore:
        def get_active_model_info(self):
            return {"version_tag": "test_v_missing", "artifact_path": "x", "metadata_path": "y"}

    result = run_inference("does-not-exist", store=empty_store, model_store=_FixedModelStore())
    assert result is None
