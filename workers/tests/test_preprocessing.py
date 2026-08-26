from datetime import datetime, timezone

from workers.preprocessing.preprocess_worker import run_preprocess
from workers.preprocessing.quality_checks import (
    check_brightness_valid,
    check_frp_valid,
    check_timestamp_valid,
    check_within_india,
    ensure_h3_cell,
    run_quality_checks,
)
from workers.utils.db import InMemoryObservationStore
from workers.utils.india_boundary import get_india_geom

DELHI_OBS = {
    "id": "obs-1",
    "satellite": "N",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "h3_cell": None,
    "frp": 42.1,
    "bright_ti4": 365.2,
    "bright_ti5": 308.1,
    "timestamp_utc": datetime(2026, 8, 25, 3, 15, tzinfo=timezone.utc),
    "quality_flags": {"daynight": "N"},
}


def test_check_within_india_true_for_delhi():
    assert check_within_india(DELHI_OBS, get_india_geom()) is True


def test_check_within_india_false_for_karachi():
    karachi = {**DELHI_OBS, "latitude": 24.8607, "longitude": 67.0011}
    assert check_within_india(karachi, get_india_geom()) is False


def test_check_timestamp_valid_rejects_future():
    future = {**DELHI_OBS, "timestamp_utc": datetime(2099, 1, 1, tzinfo=timezone.utc)}
    assert check_timestamp_valid(future, now=datetime(2026, 8, 25, tzinfo=timezone.utc)) is False


def test_check_timestamp_valid_rejects_pre_2000():
    old = {**DELHI_OBS, "timestamp_utc": datetime(1999, 1, 1, tzinfo=timezone.utc)}
    assert check_timestamp_valid(old) is False


def test_check_timestamp_valid_accepts_reasonable_date():
    assert check_timestamp_valid(DELHI_OBS, now=datetime(2026, 8, 26, tzinfo=timezone.utc)) is True


def test_check_frp_valid_bounds():
    assert check_frp_valid(DELHI_OBS) is True
    assert check_frp_valid({**DELHI_OBS, "frp": 250_000}) is False
    assert check_frp_valid({**DELHI_OBS, "frp": -1}) is False
    assert check_frp_valid({**DELHI_OBS, "frp": None}) is True  # missing != invalid


def test_check_brightness_valid_bounds():
    assert check_brightness_valid(DELHI_OBS) is True
    assert check_brightness_valid({**DELHI_OBS, "bright_ti4": 550}) is False
    assert check_brightness_valid({**DELHI_OBS, "bright_ti5": 100}) is False


def test_ensure_h3_cell_computes_when_missing():
    cell = ensure_h3_cell(DELHI_OBS)
    assert cell
    # Already-set cell is returned unchanged, not recomputed.
    obs_with_cell = {**DELHI_OBS, "h3_cell": "deadbeef"}
    assert ensure_h3_cell(obs_with_cell) == "deadbeef"


def test_run_quality_checks_marks_invalid_without_deleting_observation():
    karachi = {**DELHI_OBS, "latitude": 24.8607, "longitude": 67.0011, "bright_ti4": 999}
    flags = run_quality_checks(karachi, get_india_geom())
    assert flags["within_india_boundary"] is False
    assert flags["brightness_valid"] is False
    # The check only returns flags — it never mutates or drops obs fields.
    assert karachi["latitude"] == 24.8607


def test_run_preprocess_updates_store_in_place():
    store = InMemoryObservationStore()
    store.insert({**DELHI_OBS})
    fields = run_preprocess("obs-1", store, india_geom=get_india_geom())
    assert fields["h3_cell"]
    assert fields["quality_flags"]["within_india_boundary"] is True
    updated = store.get("obs-1")
    assert updated["h3_cell"] == fields["h3_cell"]


def test_run_preprocess_returns_none_for_missing_observation():
    store = InMemoryObservationStore()
    assert run_preprocess("does-not-exist", store) is None
