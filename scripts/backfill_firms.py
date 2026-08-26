"""
Run this script once to backfill FIRMS data from a start date to present.

Usage:
  python scripts/backfill_firms.py --start 2020-01-01 --end 2026-08-25

Chunks the date range into 10-day windows and ingests each chunk. Expect this
to take a while for multi-year ranges. Progress is tracked via
workers/ingestion/ingestion_tracker.py (JSON-file-backed, see
data/processed/ingestion_runs.json) so an interrupted run can be resumed —
each chunk is skipped if a SUCCESS run already exists for that exact
(source_type, parameters) combination.
"""
import argparse
import os
import sys
import time
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from workers.ingestion.firms_client import FIRMSClient
from workers.ingestion.firms_normalizer import normalize_firms_row
from workers.ingestion.ingestion_tracker import IngestionRunTracker, JSONFileIngestionRunStore
from workers.utils.db import InMemoryObservationStore, ObservationStore
from workers.utils.geo import is_within_india
from workers.utils.india_boundary import get_india_geom

SOURCE_TYPE = "FIRMS_VIIRS"
DEFAULT_TRACKER_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "processed", "ingestion_runs.json"
)


def chunk_ranges(start: date, end: date, chunk_days: int = 10):
    current = start
    while current <= end:
        chunk_end = min(current + timedelta(days=chunk_days - 1), end)
        yield current, chunk_end
        current = chunk_end + timedelta(days=1)


def backfill(
    client: FIRMSClient,
    start: date,
    end: date,
    store: ObservationStore,
    tracker: IngestionRunTracker,
    india_geom=None,
) -> dict:
    india_geom = india_geom if india_geom is not None else get_india_geom()
    total_fetched = total_inserted = total_skipped = 0

    for chunk_start, chunk_end in chunk_ranges(start, end):
        parameters = {"start": chunk_start.isoformat(), "end": chunk_end.isoformat()}
        if tracker.is_chunk_done(SOURCE_TYPE, parameters):
            print(f"[skip] {chunk_start} - {chunk_end} already completed")
            continue

        run_id = tracker.start_run(SOURCE_TYPE, parameters)
        try:
            df = client.fetch_archive_chunk(chunk_start, chunk_end)
            fetched = len(df)
            inserted = 0
            for _, row in df.iterrows():
                obs = normalize_firms_row(row)
                if obs is None:
                    continue
                if not is_within_india(obs["latitude"], obs["longitude"], india_geom):
                    continue
                if store.insert(obs):
                    inserted += 1
            tracker.complete_run(run_id, records_fetched=fetched, records_inserted=inserted)
            total_fetched += fetched
            total_inserted += inserted
            print(f"[ok] {chunk_start} - {chunk_end}: fetched={fetched} inserted={inserted}")
        except Exception as e:
            tracker.fail_run(run_id, str(e))
            total_skipped += 1
            print(f"[fail] {chunk_start} - {chunk_end}: {e}")

        time.sleep(1)  # rate limiting between chunks

    return {
        "total_fetched": total_fetched,
        "total_inserted": total_inserted,
        "chunks_failed": total_skipped,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", required=True, help="YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="YYYY-MM-DD")
    parser.add_argument("--tracker-path", default=DEFAULT_TRACKER_PATH)
    args = parser.parse_args()

    map_key = os.getenv("FIRMS_MAP_KEY", "")
    if not map_key:
        raise SystemExit("FIRMS_MAP_KEY not configured — set it in the environment or .env")

    start = datetime.strptime(args.start, "%Y-%m-%d").date()
    end = datetime.strptime(args.end, "%Y-%m-%d").date()

    client = FIRMSClient(map_key=map_key)
    store = InMemoryObservationStore()  # swap for Contributor 1's SQLAlchemyObservationStore
    tracker = IngestionRunTracker(JSONFileIngestionRunStore(args.tracker_path))

    summary = backfill(client, start, end, store, tracker)
    print(f"Backfill complete: {summary}")


if __name__ == "__main__":
    main()
