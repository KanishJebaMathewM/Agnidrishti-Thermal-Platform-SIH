"""
Celery task: fetch latest FIRMS NRT data and store new observations.

No hard dependency on a live broker or database. `run_firms_ingest` is the
store-agnostic core (takes an `ObservationStore`, defaults to in-memory); the
`@shared_task` wrapper is the Celery integration seam for Contributor 1.
"""
from __future__ import annotations

import logging
import os

try:
    from celery import shared_task
except ImportError:  # pragma: no cover - celery not installed in this environment
    def shared_task(*_args, **_kwargs):
        def _decorator(fn):
            return fn
        return _decorator

from workers.ingestion.firms_client import FIRMSClient
from workers.ingestion.firms_normalizer import normalize_firms_row
from workers.utils.db import InMemoryObservationStore, ObservationStore
from workers.utils.geo import is_within_india
from workers.utils.india_boundary import get_india_geom

logger = logging.getLogger(__name__)


def run_firms_ingest(
    client: FIRMSClient,
    store: ObservationStore | None = None,
    days: int = 1,
    india_geom=None,
) -> dict:
    """
    Deduplication key: (satellite, timestamp_utc, latitude, longitude).
    Skips rows that fail normalization or fall outside the India boundary.
    """
    store = store if store is not None else InMemoryObservationStore()
    india_geom = india_geom if india_geom is not None else get_india_geom()

    df = client.fetch_nrt(days=days)

    fetched = len(df)
    inserted = 0
    skipped_invalid = 0
    skipped_outside_india = 0
    skipped_duplicate = 0

    for _, row in df.iterrows():
        obs = normalize_firms_row(row)
        if obs is None:
            skipped_invalid += 1
            continue
        if not is_within_india(obs["latitude"], obs["longitude"], india_geom):
            skipped_outside_india += 1
            continue
        if store.insert(obs):
            inserted += 1
        else:
            skipped_duplicate += 1

    logger.info(
        "FIRMS ingest complete. fetched=%s inserted=%s invalid=%s outside_india=%s duplicate=%s",
        fetched, inserted, skipped_invalid, skipped_outside_india, skipped_duplicate,
    )
    return {
        "fetched": fetched,
        "inserted": inserted,
        "skipped_invalid": skipped_invalid,
        "skipped_outside_india": skipped_outside_india,
        "skipped_duplicate": skipped_duplicate,
    }


@shared_task(name="workers.ingestion.ingest_firms_snapshot", bind=True, max_retries=3)
def ingest_firms_snapshot(self, days: int = 1):
    """Celery task wrapper. Requires FIRMS_MAP_KEY and a real ObservationStore
    (Contributor 1's SQLAlchemyObservationStore) to be meaningful in production."""
    map_key = os.getenv("FIRMS_MAP_KEY", "")
    if not map_key:
        raise ValueError("FIRMS_MAP_KEY not configured")

    client = FIRMSClient(map_key=map_key)
    try:
        return run_firms_ingest(client, days=days)
    except Exception as exc:
        logger.error("FIRMS fetch failed: %s", exc)
        raise self.retry(exc=exc, countdown=60)
