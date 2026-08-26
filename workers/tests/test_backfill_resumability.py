from datetime import date

import pandas as pd

from scripts.backfill_firms import backfill, chunk_ranges
from workers.ingestion.ingestion_tracker import IngestionRunTracker, JSONFileIngestionRunStore
from workers.utils.db import InMemoryObservationStore
from workers.utils.india_boundary import get_india_geom

DELHI_ROW = {
    "latitude": 28.6139,
    "longitude": 77.2090,
    "acq_date": "2026-01-01",
    "acq_time": "0300",
    "satellite": "N",
    "confidence": "nominal",
    "frp": 40.0,
}


class FakeClient:
    """Counts calls so tests can prove a resumed run skips completed chunks."""

    def __init__(self, rows_per_chunk):
        self.rows_per_chunk = rows_per_chunk
        self.calls = []

    def fetch_archive_chunk(self, start, end):
        self.calls.append((start, end))
        return pd.DataFrame(self.rows_per_chunk)


def test_chunk_ranges_splits_into_10_day_windows():
    chunks = list(chunk_ranges(date(2026, 1, 1), date(2026, 1, 25)))
    assert chunks[0] == (date(2026, 1, 1), date(2026, 1, 10))
    assert chunks[1] == (date(2026, 1, 11), date(2026, 1, 20))
    assert chunks[2] == (date(2026, 1, 21), date(2026, 1, 25))


def test_backfill_persists_progress_and_resumes(tmp_path):
    tracker_path = str(tmp_path / "ingestion_runs.json")
    india_geom = get_india_geom()

    client = FakeClient([DELHI_ROW])
    store = InMemoryObservationStore()
    tracker = IngestionRunTracker(JSONFileIngestionRunStore(tracker_path))

    summary = backfill(client, date(2026, 1, 1), date(2026, 1, 10), store, tracker, india_geom)
    assert summary["total_inserted"] == 1
    assert len(client.calls) == 1

    # Simulate a fresh process picking up the same tracker file — the chunk
    # already marked SUCCESS must be skipped, not re-fetched.
    resumed_tracker = IngestionRunTracker(JSONFileIngestionRunStore(tracker_path))
    resumed_client = FakeClient([DELHI_ROW])
    resumed_store = InMemoryObservationStore()

    resumed_summary = backfill(
        resumed_client, date(2026, 1, 1), date(2026, 1, 10), resumed_store, resumed_tracker, india_geom
    )
    assert resumed_summary["total_fetched"] == 0
    assert len(resumed_client.calls) == 0  # skipped entirely — no HTTP call made
    assert len(resumed_store.all()) == 0


def test_backfill_resumes_partway_through_a_multi_chunk_range(tmp_path):
    tracker_path = str(tmp_path / "ingestion_runs.json")
    india_geom = get_india_geom()

    # First run only completes the first of two chunks (simulating a crash).
    tracker = IngestionRunTracker(JSONFileIngestionRunStore(tracker_path))
    tracker.complete_run(
        tracker.start_run("FIRMS_VIIRS", {"start": "2026-01-01", "end": "2026-01-10"}),
        records_fetched=1,
        records_inserted=1,
    )

    client = FakeClient([DELHI_ROW])
    store = InMemoryObservationStore()
    summary = backfill(client, date(2026, 1, 1), date(2026, 1, 20), store, tracker, india_geom)

    # Only the second chunk (11-20) should have triggered a fetch.
    assert len(client.calls) == 1
    assert client.calls[0] == (date(2026, 1, 11), date(2026, 1, 20))
    assert summary["total_inserted"] == 1
