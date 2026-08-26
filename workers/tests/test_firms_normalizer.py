import pandas as pd
import pytest

from workers.ingestion.firms_normalizer import normalize_firms_row

VALID_ROW = {
    "latitude": "28.6139",
    "longitude": "77.2090",
    "bright_ti4": "365.2",
    "bright_ti5": "308.1",
    "scan": "0.39",
    "track": "0.36",
    "acq_date": "2026-08-25",
    "acq_time": "0315",
    "satellite": "N",
    "instrument": "VIIRS",
    "confidence": "nominal",
    "version": "2.0NRT",
    "bright_t31": "300.4",
    "frp": "42.1",
    "daynight": "N",
    "type": "0",
}


def _row(overrides=None):
    data = {**VALID_ROW, **(overrides or {})}
    return pd.Series(data)


def test_valid_row_produces_correct_dict():
    obs = normalize_firms_row(_row())
    assert obs is not None
    assert obs["latitude"] == pytest.approx(28.6139)
    assert obs["longitude"] == pytest.approx(77.2090)
    assert obs["source_type"] == "FIRMS_VIIRS"
    assert obs["satellite"] == "N"
    assert obs["confidence"] == "nominal"
    assert obs["frp"] == pytest.approx(42.1)
    assert obs["bright_ti4"] == pytest.approx(365.2)
    assert obs["h3_cell"]
    assert obs["geometry"] == "SRID=4326;POINT(77.209 28.6139)"
    assert obs["quality_flags"]["daynight"] == "N"
    assert obs["raw_record_ref"]["satellite"] == "N"
    assert obs["timestamp_utc"].year == 2026
    assert obs["timestamp_utc"].hour == 3
    assert obs["timestamp_utc"].minute == 15


def test_invalid_coordinates_returns_none():
    assert normalize_firms_row(_row({"latitude": "not-a-number"})) is None
    assert normalize_firms_row(_row({"longitude": None})) is None


def test_missing_coordinate_column_returns_none():
    row = pd.Series({k: v for k, v in VALID_ROW.items() if k != "latitude"})
    assert normalize_firms_row(row) is None


def test_out_of_india_bbox_coordinates_skipped():
    # Well outside the 6-38 lat / 65-98 lon rectangle used by the India FIRMS query.
    assert normalize_firms_row(_row({"latitude": "51.5", "longitude": "-0.13"})) is None


def test_nan_frp_becomes_none():
    obs = normalize_firms_row(_row({"frp": float("nan")}))
    assert obs is not None
    assert obs["frp"] is None


def test_missing_frp_becomes_none():
    row_data = {k: v for k, v in VALID_ROW.items() if k != "frp"}
    obs = normalize_firms_row(pd.Series(row_data))
    assert obs is not None
    assert obs["frp"] is None


def test_frp_above_physical_max_becomes_none():
    obs = normalize_firms_row(_row({"frp": "250000"}))
    assert obs is not None
    assert obs["frp"] is None


def test_frp_negative_becomes_none():
    obs = normalize_firms_row(_row({"frp": "-5"}))
    assert obs is not None
    assert obs["frp"] is None


def test_invalid_confidence_defaults_to_nominal():
    obs = normalize_firms_row(_row({"confidence": "garbage"}))
    assert obs is not None
    assert obs["confidence"] == "nominal"


def test_invalid_date_returns_none():
    assert normalize_firms_row(_row({"acq_date": "not-a-date"})) is None


def test_each_row_gets_a_unique_id():
    obs1 = normalize_firms_row(_row())
    obs2 = normalize_firms_row(_row())
    assert obs1["id"] != obs2["id"]
