"""
Source registry updater.

After an observation is preprocessed and enriched, this finds or creates a
thermal_source keyed by H3 cell and advances its lifecycle:

  NEW -> OBSERVED (after first observation stored)
  OBSERVED -> CANDIDATE (after N observations over M days)
  CANDIDATE -> MONITORED (after human confirmation via feedback API — not automatic)
  MONITORED -> ARCHIVED (after no observations for K days — swept, not per-observation)

Thresholds start at the spec's defaults; tune once real data volume is observed.
"""
from __future__ import annotations

import uuid
from datetime import timedelta
from typing import Protocol

NEW, OBSERVED, CANDIDATE, MONITORED, ARCHIVED = "NEW", "OBSERVED", "CANDIDATE", "MONITORED", "ARCHIVED"

N_OBSERVATIONS_FOR_CANDIDATE = 3
M_DAYS_WINDOW = 7
K_DAYS_INACTIVITY_ARCHIVE = 90


class SourceRegistryStore(Protocol):
    def find_by_h3(self, h3_cell: str) -> dict | None: ...
    def get(self, source_id: str) -> dict | None: ...
    def create(self, source: dict) -> str: ...
    def update(self, source_id: str, fields: dict) -> None: ...
    def all(self) -> list[dict]: ...


class InMemorySourceRegistryStore:
    def __init__(self):
        self._sources: dict[str, dict] = {}

    def find_by_h3(self, h3_cell: str) -> dict | None:
        for s in self._sources.values():
            if s["h3_cell"] == h3_cell:
                return dict(s)
        return None

    def get(self, source_id: str) -> dict | None:
        s = self._sources.get(source_id)
        return dict(s) if s else None

    def create(self, source: dict) -> str:
        source_id = source.get("id") or str(uuid.uuid4())
        self._sources[source_id] = {**source, "id": source_id}
        return source_id

    def update(self, source_id: str, fields: dict) -> None:
        if source_id in self._sources:
            self._sources[source_id].update(fields)

    def all(self) -> list[dict]:
        return [dict(s) for s in self._sources.values()]


def _apply_observation(source: dict, obs: dict) -> dict:
    timestamps = list(source.get("observation_timestamps") or []) + [obs["timestamp_utc"]]
    count = source.get("observation_count", 0) + 1
    frp = obs.get("frp")
    frp_sum = source.get("frp_sum", 0.0) + (frp or 0.0)
    frp_n = source.get("frp_n", 0) + (1 if frp is not None else 0)
    mean_frp = frp_sum / frp_n if frp_n else None

    status = source.get("status", NEW)
    if status == NEW:
        status = OBSERVED
    if status == OBSERVED:
        window_start = obs["timestamp_utc"] - timedelta(days=M_DAYS_WINDOW)
        recent = [t for t in timestamps if t >= window_start]
        if len(recent) >= N_OBSERVATIONS_FOR_CANDIDATE:
            status = CANDIDATE

    return {
        "observation_count": count,
        "observation_timestamps": timestamps,
        "last_seen": obs["timestamp_utc"],
        "frp_sum": frp_sum,
        "frp_n": frp_n,
        "mean_frp": mean_frp,
        "status": status,
    }


def update_source_registry_for_observation(obs: dict, store: SourceRegistryStore) -> dict:
    h3_cell = obs["h3_cell"]
    source = store.find_by_h3(h3_cell)
    if source is None:
        source_id = store.create(
            {
                "h3_cell": h3_cell,
                "status": NEW,
                "observation_count": 0,
                "observation_timestamps": [],
                "first_seen": obs["timestamp_utc"],
                "last_seen": obs["timestamp_utc"],
                "frp_sum": 0.0,
                "frp_n": 0,
                "mean_frp": None,
            }
        )
        source = store.get(source_id)

    fields = _apply_observation(source, obs)
    store.update(source["id"], fields)
    return {**source, **fields}


def confirm_source(source_id: str, store: SourceRegistryStore) -> dict | None:
    """Human confirmation via the feedback API: CANDIDATE -> MONITORED.
    No-op (returns the record unchanged) if the source isn't in CANDIDATE."""
    source = store.get(source_id)
    if source is None:
        return None
    if source["status"] == CANDIDATE:
        store.update(source_id, {"status": MONITORED})
        source = store.get(source_id)
    return source


def archive_stale_sources(store: SourceRegistryStore, now) -> list[str]:
    """Periodic sweep: MONITORED sources idle for K_DAYS_INACTIVITY_ARCHIVE -> ARCHIVED."""
    archived_ids = []
    for source in store.all():
        if source["status"] != MONITORED:
            continue
        last_seen = source["last_seen"]
        if (now - last_seen) >= timedelta(days=K_DAYS_INACTIVITY_ARCHIVE):
            store.update(source["id"], {"status": ARCHIVED})
            archived_ids.append(source["id"])
    return archived_ids


try:
    from celery import shared_task
except ImportError:  # pragma: no cover - celery not installed in this environment
    def shared_task(*_args, **_kwargs):
        def _decorator(fn):
            return fn
        return _decorator


@shared_task(name="workers.enrichment.update_source_registry")
def update_source_registry(observation_id: str, observation_store=None, registry_store: SourceRegistryStore | None = None):
    if observation_store is None:
        raise ValueError("update_source_registry requires an ObservationStore instance")
    obs = observation_store.get(observation_id)
    if obs is None:
        return None
    return update_source_registry_for_observation(obs, registry_store or InMemorySourceRegistryStore())
