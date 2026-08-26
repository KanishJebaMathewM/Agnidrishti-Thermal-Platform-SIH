from datetime import datetime, timezone

from ml.datasets.build_dataset import (
    build_training_dataset,
    label_observation,
    temporal_split,
)
from ml.features.feature_columns import FEATURE_COLUMNS_V1


def _obs(month, day=15, **overrides):
    base = {
        "id": "obs-1",
        "frp": 50.0,
        "timestamp_utc": datetime(2023, month, day, 10, 0, tzinfo=timezone.utc),
        "source_id": None,
    }
    base.update(overrides)
    return base


def test_human_label_takes_priority_over_everything():
    label = label_observation(
        _obs(1),
        source={"expected_class": "Forest Fire", "classification_confidence": 0.99},
        context={"is_forest": True},
        human_label={"human_label": "Industrial Incident"},
        weak_label_row={"label": "Agricultural Burn"},
    )
    assert label["label"] == "Industrial Incident"
    assert label["label_source"] == "OPERATOR_FEEDBACK"
    assert label["label_confidence"] == 1.0
    assert label["verification_status"] == "VERIFIED"


def test_training_labels_row_used_when_no_human_label():
    label = label_observation(
        _obs(1),
        weak_label_row={"label": "Agricultural Burn", "label_source": "TRAINING_LABELS_TABLE", "label_confidence": 0.6},
    )
    assert label["label"] == "Agricultural Burn"
    assert label["label_source"] == "TRAINING_LABELS_TABLE"


def test_high_confidence_source_registry_rule():
    label = label_observation(
        _obs(1),
        source={"expected_class": "Persistent Flare/Kiln", "classification_confidence": 0.95},
        context={},
    )
    assert label["label"] == "Persistent Flare/Kiln"
    assert label["label_source"] == "SOURCE_REGISTRY_RULE"


def test_low_confidence_source_registry_does_not_apply():
    label = label_observation(
        _obs(1),
        source={"expected_class": "Persistent Flare/Kiln", "classification_confidence": 0.5},
        context={},
    )
    assert label["label"] != "Persistent Flare/Kiln"


def test_forest_seasonal_rule():
    label = label_observation(_obs(month=4), context={"is_forest": True})
    assert label["label"] == "Forest Fire"
    assert label["label_source"] == "FOREST_SEASONAL_RULE"


def test_forest_rule_does_not_apply_outside_season():
    label = label_observation(_obs(month=7), context={"is_forest": True})
    assert label["label"] != "Forest Fire"


def test_industrial_proximity_rule():
    label = label_observation(_obs(month=1), context={"nearest_industrial_dist_km": 1.5})
    assert label["label"] == "Persistent Flare/Kiln"
    assert label["label_source"] == "INDUSTRIAL_PROXIMITY_RULE"


def test_agricultural_seasonal_rule():
    label = label_observation(_obs(month=11), context={"land_use_class": "AGRICULTURAL"})
    assert label["label"] == "Agricultural Burn"
    assert label["label_source"] == "AGRICULTURAL_SEASONAL_RULE"


def test_default_unknown_when_no_rule_matches():
    label = label_observation(_obs(month=7), context={})
    assert label["label"] == "Unknown"
    assert label["label_source"] == "DEFAULT_UNKNOWN"


def test_build_training_dataset_produces_feature_columns_and_year():
    records = [
        {"observation": _obs(month=4), "context": {"is_forest": True}},
        {"observation": _obs(month=1, id="obs-2"), "context": {"nearest_industrial_dist_km": 0.5}},
    ]
    df = build_training_dataset(records)

    for col in FEATURE_COLUMNS_V1:
        assert col in df.columns
    assert "label" in df.columns
    assert "label_source" in df.columns
    assert "year" in df.columns
    assert list(df["year"]) == [2023, 2023]


def test_temporal_split_never_mixes_years():
    records = []
    for year in (2021, 2025, 2026):
        obs = {
            "id": f"obs-{year}",
            "frp": 50.0,
            "timestamp_utc": datetime(year, 3, 1, tzinfo=timezone.utc),
            "source_id": None,
        }
        records.append({"observation": obs, "context": {}})

    df = build_training_dataset(records)
    train_df, val_df, test_df = temporal_split(df)

    assert set(train_df["year"]) <= {2020, 2021, 2022, 2023, 2024}
    assert set(val_df["year"]) <= {2025}
    assert set(test_df["year"]) <= {2026}
    assert len(train_df) + len(val_df) + len(test_df) == 3
