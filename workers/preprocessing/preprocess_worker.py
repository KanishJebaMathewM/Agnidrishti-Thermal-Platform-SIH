"""
Preprocessing worker. Triggered after new raw observations are inserted.

Runs the checks from quality_checks.py, backfills the H3 cell if missing, and
writes the merged quality_flags back onto the observation via the injected
ObservationStore. Never deletes or blanks out invalid observations.

Source matching (spec Step 6, item 7) is intentionally not done here — it's
handled by workers/enrichment/update_source_registry.py later in the same
pipeline, so there's one place that owns "is this a known source."
"""
from __future__ import annotations

import logging

try:
    from celery import shared_task
except ImportError:  # pragma: no cover - celery not installed in this environment
    def shared_task(*_args, **_kwargs):
        def _decorator(fn):
            return fn
        return _decorator

from workers.preprocessing.quality_checks import ensure_h3_cell, run_quality_checks
from workers.utils.db import InMemoryObservationStore, ObservationStore
from workers.utils.india_boundary import get_india_geom

logger = logging.getLogger(__name__)


def run_preprocess(observation_id: str, store: ObservationStore, india_geom=None) -> dict | None:
    """Quality-check and enrich a single observation by ID. Returns the updated
    fields, or None if the observation doesn't exist in the store."""
    obs = store.get(observation_id)
    if obs is None:
        logger.warning("preprocess: observation %s not found", observation_id)
        return None

    india_geom = india_geom if india_geom is not None else get_india_geom()

    fields = {
        "h3_cell": ensure_h3_cell(obs),
        "quality_flags": run_quality_checks(obs, india_geom),
    }
    store.update(observation_id, fields)
    return fields


@shared_task(name="workers.preprocessing.preprocess_observation")
def preprocess_observation(observation_id: str, store: ObservationStore | None = None):
    """Celery task wrapper. `store` defaults to a fresh in-memory store only
    for standalone invocation — production wiring should pass Contributor 1's
    SQLAlchemyObservationStore so the update actually persists."""
    return run_preprocess(observation_id, store or InMemoryObservationStore())
