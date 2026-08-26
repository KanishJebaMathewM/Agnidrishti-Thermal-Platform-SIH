import pandas as pd
import pytest

from workers.ingestion.firms_worker import run_firms_ingest
from workers.utils.db import InMemoryObservationStore
from workers.utils.india_boundary import get_india_geom

DELHI = {"latitude": 28.6139, "longitude": 77.2090}
CHENNAI = {"latitude": 13.0827, "longitude": 80.2707}
COMMON_FIELDS = {
    "bright_ti4": 365.2,
    "bright_ti5": 308.1,
    "scan": 0.39,
    "track": 0.36,
    "acq_date": "2026-08-25",
    "acq_time": "0315",
    "satellite": "N",
    "instrument": "VIIRS",
    "confidence": "nominal",
    "version": "2.0NRT",
    "bright_t31": 300.4,
    "frp": 42.1,
    "daynight": "N",
    "type": 0,
}


class FakeFIRMSClient:
    """Stands in for FIRMSClient so tests never hit the real FIRMS API."""

    def __init__(self, df: pd.DataFrame):
        self._df = df

    def fetch_nrt(self, days: int = 1) -> pd.DataFrame:
        return self._df


@pytest.fixture(scope="module")
def india_geom():
    return get_india_geom()


def test_duplicate_rows_inserted_once(india_geom):
    rows = [
        {**COMMON_FIELDS, **DELHI},
        {**COMMON_FIELDS, **DELHI},  # exact duplicate: same satellite/time/lat/lon
        {**COMMON_FIELDS, **CHENNAI},
    ]
    df = pd.DataFrame(rows)
    store = InMemoryObservationStore()

    result = run_firms_ingest(FakeFIRMSClient(df), store=store, india_geom=india_geom)

    assert result["fetched"] == 3
    assert result["inserted"] == 2
    assert result["skipped_duplicate"] == 1
    assert len(store.all()) == 2


def test_running_ingest_twice_does_not_double_insert(india_geom):
    df = pd.DataFrame([{**COMMON_FIELDS, **DELHI}])
    store = InMemoryObservationStore()

    run_firms_ingest(FakeFIRMSClient(df), store=store, india_geom=india_geom)
    second_result = run_firms_ingest(FakeFIRMSClient(df), store=store, india_geom=india_geom)

    assert second_result["inserted"] == 0
    assert second_result["skipped_duplicate"] == 1
    assert len(store.all()) == 1


def test_out_of_india_rows_are_skipped_not_inserted(india_geom):
    # Karachi: inside the rectangular FIRMS bbox, outside the real India polygon.
    karachi = {**COMMON_FIELDS, "latitude": 24.8607, "longitude": 67.0011}
    df = pd.DataFrame([karachi])
    store = InMemoryObservationStore()

    result = run_firms_ingest(FakeFIRMSClient(df), store=store, india_geom=india_geom)

    assert result["inserted"] == 0
    assert result["skipped_outside_india"] == 1
    assert len(store.all()) == 0


def test_invalid_rows_are_skipped(india_geom):
    bad_row = {**COMMON_FIELDS, "latitude": "not-a-number", "longitude": 77.0}
    df = pd.DataFrame([bad_row])
    store = InMemoryObservationStore()

    result = run_firms_ingest(FakeFIRMSClient(df), store=store, india_geom=india_geom)

    assert result["inserted"] == 0
    assert result["skipped_invalid"] == 1
