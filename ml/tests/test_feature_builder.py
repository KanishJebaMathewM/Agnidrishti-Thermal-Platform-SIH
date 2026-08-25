from datetime import datetime, timezone

from ml.features.feature_builder import FEATURE_SET_VERSION, build_feature_vector
from ml.features.feature_columns import FEATURE_COLUMNS_V1


def _known_observation():
    return {
        "id": "obs-001",
        "frp": 210.5,
        "bright_ti4": 340.0,
        "bright_ti5": 305.0,
        "confidence": "high",
        "timestamp_utc": datetime(2026, 4, 15, 22, 30, tzinfo=timezone.utc),  # 22:30 -> night, April -> Summer
        "source_id": "src-001",
    }


def _known_baseline():
    return {"mean_frp": 100.0, "frp_std": 20.0}


def _known_context():
    return {
        "nearest_industrial_dist_km": 1.2,
        "land_use_class": "INDUSTRIAL",
        "is_forest": False,
    }


def test_known_observation_produces_expected_feature_vector():
    features = build_feature_vector(_known_observation(), _known_baseline(), _known_context())

    assert features["frp"] == 210.5
    assert features["bright_ti4"] == 340.0
    assert features["bright_ti5"] == 305.0
    assert features["temp_diff_ti4_ti5"] == 35.0
    assert features["confidence_encoded"] == 2  # high
    assert features["hour_of_day"] == 22
    assert features["day_of_week"] == datetime(2026, 4, 15).weekday()
    assert features["month"] == 4
    assert features["is_night"] == 1
    assert features["season"] == 2  # Summer (Mar/Apr/May)
    assert features["has_baseline"] == 1
    assert features["frp_deviation"] == 110.5
    assert features["frp_zscore"] == 110.5 / 20.0
    assert features["nearest_industrial_dist_km"] == 1.2
    assert features["is_forest"] == 0
    assert features["land_use_encoded"] == 0  # INDUSTRIAL
    assert features["source_exists"] == 1


def test_missing_frp_produces_none_not_zero():
    observation = _known_observation()
    observation["frp"] = None

    features = build_feature_vector(observation, _known_baseline(), _known_context())

    assert features["frp"] is None
    assert features["frp"] != 0
    # Without FRP there is no deviation/zscore to compute, and no baseline attachment.
    assert features["frp_deviation"] is None
    assert features["frp_zscore"] is None
    assert features["has_baseline"] == 0


def test_feature_column_order_matches_canonical_list():
    features = build_feature_vector(_known_observation(), _known_baseline(), _known_context())
    ordered_values = [features[col] for col in FEATURE_COLUMNS_V1]

    # Every canonical column must be present and independently addressable
    # in exactly the order FEATURE_COLUMNS_V1 declares.
    assert len(ordered_values) == len(FEATURE_COLUMNS_V1)
    for col in FEATURE_COLUMNS_V1:
        assert col in features


def test_feature_set_version_present():
    features = build_feature_vector(_known_observation(), _known_baseline(), _known_context())
    assert features["_feature_set_version"] == FEATURE_SET_VERSION == "v1"
    assert features["_observation_id"] == "obs-001"


def test_missing_baseline_does_not_crash():
    features = build_feature_vector(_known_observation(), None, _known_context())
    assert features["has_baseline"] == 0
    assert features["frp_deviation"] is None
    assert features["frp_zscore"] is None


def test_missing_context_does_not_crash():
    features = build_feature_vector(_known_observation(), _known_baseline(), {})
    assert features["nearest_industrial_dist_km"] is None
    assert features["is_forest"] == 0
    assert features["land_use_encoded"] is None
