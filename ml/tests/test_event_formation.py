from datetime import datetime, timedelta, timezone

import pytest

from workers.events.event_worker import (
    apply_observation_to_event,
    compute_severity,
    haversine_km,
    process_event_logic,
    weighted_centroid,
)

BASE_TS = datetime(2026, 8, 23, 10, 0, tzinfo=timezone.utc)


def _obs(id_, lat, lon, frp, minutes_after_base=0, classification=None):
    return {
        "id": id_,
        "latitude": lat,
        "longitude": lon,
        "frp": frp,
        "timestamp_utc": BASE_TS + timedelta(minutes=minutes_after_base),
        "classification": classification,
    }


def test_two_close_observations_join_the_same_event():
    obs1 = _obs("o1", 20.0000, 78.0000, 150.0, minutes_after_base=0)
    obs2 = _obs("o2", 20.0500, 78.0500, 160.0, minutes_after_base=60)  # ~7.6km, 1h later

    event1 = process_event_logic(obs1, open_events=[])
    assert event1["_is_new"] is True
    event1["id"] = "EVT-1"

    event2 = process_event_logic(obs2, open_events=[event1])
    assert event2["_is_new"] is False
    assert event2["observation_count"] == 2


def test_far_apart_observations_become_different_events():
    obs1 = _obs("o1", 20.0000, 78.0000, 150.0, minutes_after_base=0)
    # ~0.5 degree lat ~ 55km further north — comfortably over 50km away.
    obs2 = _obs("o2", 20.5000, 78.0000, 150.0, minutes_after_base=30)

    assert haversine_km(20.0000, 78.0000, 20.5000, 78.0000) > 50

    event1 = process_event_logic(obs1, open_events=[])
    event1["id"] = "EVT-1"

    event2 = process_event_logic(obs2, open_events=[event1])
    assert event2["_is_new"] is True


def test_observations_more_than_12h_apart_do_not_join():
    obs1 = _obs("o1", 20.0000, 78.0000, 150.0, minutes_after_base=0)
    obs2 = _obs("o2", 20.0100, 78.0100, 150.0, minutes_after_base=13 * 60)  # close, but 13h later

    event1 = process_event_logic(obs1, open_events=[])
    event1["id"] = "EVT-1"

    event2 = process_event_logic(obs2, open_events=[event1])
    assert event2["_is_new"] is True


def test_centroid_is_frp_weighted_mean_of_observation_positions():
    obs1 = _obs("o1", 10.0, 70.0, 100.0)
    obs2 = _obs("o2", 20.0, 80.0, 300.0)

    lat, lon = weighted_centroid([obs1, obs2])

    expected_lat = (10.0 * 100 + 20.0 * 300) / 400
    expected_lon = (70.0 * 100 + 80.0 * 300) / 400
    assert lat == pytest.approx(expected_lat)
    assert lon == pytest.approx(expected_lon)


def test_centroid_falls_back_to_unweighted_mean_without_frp():
    obs1 = _obs("o1", 10.0, 70.0, None)
    obs2 = _obs("o2", 20.0, 80.0, None)

    lat, lon = weighted_centroid([obs1, obs2])
    assert lat == pytest.approx(15.0)
    assert lon == pytest.approx(75.0)


@pytest.mark.parametrize(
    "confidence,anomaly_score,persistence_nights,frp,expected_severity",
    [
        (1.0, 1.0, 14, 500, "CRITICAL"),   # 30+30+20+20 = 100
        (0.9, 0.7, 7, 250, "HIGH"),        # 27+21+10+10 = 68
        (0.7, 0.5, 5, 200, "REVIEW"),      # 21+15+7.14+8 ~= 51.1 -> in [40, 60)
        (0.1, 0.1, 0, 0, "NORMAL"),        # near-zero score
    ],
)
def test_severity_thresholds(confidence, anomaly_score, persistence_nights, frp, expected_severity):
    score, severity = compute_severity(confidence, anomaly_score, persistence_nights, frp)
    assert severity == expected_severity


def test_severity_critical_at_exact_boundary():
    score, severity = compute_severity(1.0, 1.0, 14, 500)
    assert score == pytest.approx(100.0)
    assert severity == "CRITICAL"


def test_event_formation_is_deterministic_regardless_of_call_count():
    obs1 = _obs("o1", 20.0, 78.0, 150.0, minutes_after_base=0)
    obs2 = _obs("o2", 20.02, 78.02, 160.0, minutes_after_base=30)

    def run():
        e1 = process_event_logic(obs1, open_events=[])
        e1["id"] = "EVT-1"
        return process_event_logic(obs2, open_events=[e1])

    first = run()
    second = run()

    assert first["centroid_lat"] == second["centroid_lat"]
    assert first["centroid_lon"] == second["centroid_lon"]
    assert first["severity"] == second["severity"]
    assert first["observation_count"] == second["observation_count"] == 2


def test_apply_observation_to_event_advances_status_with_classification():
    obs = _obs("o1", 20.0, 78.0, 400.0)
    classification = {"predicted_class": "Industrial Incident", "confidence": 0.95, "model_version": "xgb_v1.0"}
    anomaly = {"anomaly_score": 0.9, "anomaly_flag": True}

    event = apply_observation_to_event(None, obs, classification=classification, anomaly=anomaly)

    assert event["classification"] == "Industrial Incident"
    assert event["status"] in ("ANALYZING", "CANDIDATE", "HUMAN_REVIEW")
    assert event["anomaly_score"] == 0.9
