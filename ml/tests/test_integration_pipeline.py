"""
End-to-end integration test for Contributor 3's slice of the pipeline:

  observation -> feature vector -> XGBoost classification -> anomaly score
             -> event formation -> event with severity/status

This is the part of AGNIDRISHTI_PLAN.md's "online inference" path that
belongs to this domain (ml/, workers/inference/, workers/events/). It
stops short of ingestion, the API layer, and the frontend — those belong
to Contributors 1, 2, 4, and 5.

Uses a real (freshly trained, on synthetic data) model artifact rather than
a fake classifier, so this test also exercises the joblib save/load round
trip and the LocalModelRegistry discovery mechanism exactly as a worker
process would use them.
"""
from datetime import datetime, timezone

import pytest

from ml.datasets.build_dataset import build_training_dataset, temporal_split
from ml.datasets.synthetic import generate_synthetic_dataset
from ml.training.train_classifier import save_model, train_classifier
from workers.events.event_worker import InMemoryEventStore, process_event
from workers.inference.inference_worker import (
    InMemoryInferenceStore,
    LocalModelRegistry,
    run_inference,
)


@pytest.fixture(scope="module")
def trained_model_dir(tmp_path_factory):
    model_dir = tmp_path_factory.mktemp("integration_models")
    records = generate_synthetic_dataset(n_per_class=120)
    df = build_training_dataset(records)
    train_df, val_df, _ = temporal_split(df)
    model, metrics = train_classifier(train_df, val_df)
    save_model(model, metrics, model_dir=model_dir, version_tag="xgb_integration.0")
    return model_dir


def test_observation_flows_end_to_end_into_a_scored_event(trained_model_dir):
    model_store = LocalModelRegistry(model_dir=trained_model_dir)
    inference_store = InMemoryInferenceStore()
    event_store = InMemoryEventStore()

    observation = {
        "id": "obs-e2e-1",
        "frp": 480.0,
        "bright_ti4": 385.0,
        "bright_ti5": 302.0,
        "confidence": "high",
        "timestamp_utc": datetime(2026, 5, 1, 21, 0, tzinfo=timezone.utc),
        "latitude": 22.5,
        "longitude": 82.0,
        "source_id": "src-e2e-1",
    }
    baseline = {"mean_frp": 90.0, "frp_std": 15.0}
    inference_store.add_observation(observation, baseline=baseline)

    inference_result = run_inference("obs-e2e-1", store=inference_store, model_store=model_store)
    assert inference_result is not None
    assert inference_result["predicted_class"] in {
        "Industrial Incident", "Persistent Flare/Kiln", "Agricultural Burn", "Forest Fire", "Unknown",
    }
    # Huge deviation from baseline (480 vs 90 mean, std 15) must register as anomalous.
    assert inference_result["anomaly_flag"] is True

    event_store.add_observation(observation, inference_result)
    event = process_event("obs-e2e-1", store=event_store)

    assert event is not None
    assert event["observation_count"] == 1
    assert event["classification"] == inference_result["predicted_class"]
    assert event["severity"] in {"NORMAL", "OBSERVE", "REVIEW", "HIGH", "CRITICAL"}
    assert event["status"] in {"NEW", "ANALYZING", "CANDIDATE", "HUMAN_REVIEW"}
    assert event["centroid_lat"] == pytest.approx(22.5)
    assert event["centroid_lon"] == pytest.approx(82.0)


def test_two_nearby_observations_produce_one_event_not_two(trained_model_dir):
    model_store = LocalModelRegistry(model_dir=trained_model_dir)
    inference_store = InMemoryInferenceStore()
    event_store = InMemoryEventStore()

    obs1 = {
        "id": "obs-e2e-2a",
        "frp": 150.0,
        "bright_ti4": 330.0,
        "bright_ti5": 300.0,
        "confidence": "nominal",
        "timestamp_utc": datetime(2026, 5, 2, 10, 0, tzinfo=timezone.utc),
        "latitude": 19.0,
        "longitude": 74.0,
        "source_id": None,
    }
    obs2 = {**obs1, "id": "obs-e2e-2b", "latitude": 19.02, "longitude": 74.02,
            "timestamp_utc": datetime(2026, 5, 2, 11, 0, tzinfo=timezone.utc)}

    for obs in (obs1, obs2):
        inference_store.add_observation(obs)
        result = run_inference(obs["id"], store=inference_store, model_store=model_store)
        event_store.add_observation(obs, result)
        process_event(obs["id"], store=event_store)

    assert len(event_store._events) == 1
    assert event_store._events[0]["observation_count"] == 2
