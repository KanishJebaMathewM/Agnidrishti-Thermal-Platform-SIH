"""
Track each ingestion run so the backfill script can resume interrupted runs and
the dashboard can show data freshness.

Schema mirrors the future `data_ingestion_runs` table:
  id UUID
  source_type VARCHAR  -- FIRMS_VIIRS, INSAT
  run_start TIMESTAMPTZ
  run_end TIMESTAMPTZ
  status VARCHAR  -- RUNNING, SUCCESS, FAILED
  records_fetched INT
  records_inserted INT
  error_message TEXT
  parameters JSONB  -- date range, product, etc.

Like ObservationStore, this is store-agnostic: `InMemoryIngestionRunStore` (default,
used in tests) and `JSONFileIngestionRunStore` (used by scripts/backfill_firms.py so
resumability survives a process restart, without needing Contributor 1's Postgres).
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Protocol


class IngestionRunStore(Protocol):
    def create(self, run: dict) -> str: ...
    def update(self, run_id: str, fields: dict) -> None: ...
    def find_successful(self, source_type: str, parameters: dict) -> dict | None: ...
    def all(self) -> list[dict]: ...


class InMemoryIngestionRunStore:
    def __init__(self):
        self._runs: dict[str, dict] = {}

    def create(self, run: dict) -> str:
        run_id = run.get("id") or str(uuid.uuid4())
        self._runs[run_id] = {**run, "id": run_id}
        return run_id

    def update(self, run_id: str, fields: dict) -> None:
        if run_id in self._runs:
            self._runs[run_id].update(fields)

    def find_successful(self, source_type: str, parameters: dict) -> dict | None:
        for run in self._runs.values():
            if (
                run.get("source_type") == source_type
                and run.get("status") == "SUCCESS"
                and run.get("parameters") == parameters
            ):
                return run
        return None

    def all(self) -> list[dict]:
        return list(self._runs.values())


class JSONFileIngestionRunStore:
    """Persists runs to a JSON file so `scripts/backfill_firms.py` can resume
    across process restarts without a live database."""

    def __init__(self, path: str):
        self.path = path
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self._write({})

    def _read(self) -> dict:
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: dict) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def create(self, run: dict) -> str:
        data = self._read()
        run_id = run.get("id") or str(uuid.uuid4())
        data[run_id] = {**run, "id": run_id}
        self._write(data)
        return run_id

    def update(self, run_id: str, fields: dict) -> None:
        data = self._read()
        if run_id in data:
            data[run_id].update(fields)
            self._write(data)

    def find_successful(self, source_type: str, parameters: dict) -> dict | None:
        data = self._read()
        for run in data.values():
            if (
                run.get("source_type") == source_type
                and run.get("status") == "SUCCESS"
                and run.get("parameters") == parameters
            ):
                return run
        return None

    def all(self) -> list[dict]:
        return list(self._read().values())


class IngestionRunTracker:
    def __init__(self, store: IngestionRunStore | None = None):
        self.store = store or InMemoryIngestionRunStore()

    def start_run(self, source_type: str, parameters: dict) -> str:
        return self.store.create(
            {
                "source_type": source_type,
                "run_start": datetime.now(timezone.utc),
                "run_end": None,
                "status": "RUNNING",
                "records_fetched": 0,
                "records_inserted": 0,
                "error_message": None,
                "parameters": parameters,
            }
        )

    def complete_run(self, run_id: str, records_fetched: int, records_inserted: int) -> None:
        self.store.update(
            run_id,
            {
                "run_end": datetime.now(timezone.utc),
                "status": "SUCCESS",
                "records_fetched": records_fetched,
                "records_inserted": records_inserted,
            },
        )

    def fail_run(self, run_id: str, error_message: str) -> None:
        self.store.update(
            run_id,
            {
                "run_end": datetime.now(timezone.utc),
                "status": "FAILED",
                "error_message": error_message,
            },
        )

    def is_chunk_done(self, source_type: str, parameters: dict) -> bool:
        return self.store.find_successful(source_type, parameters) is not None
