"""
Persistence layer for the data pipeline.

Workers depend on the `ObservationStore` interface below rather than talking to
SQLAlchemy directly, so pipeline logic stays testable offline regardless of
which store backs it. `InMemoryObservationStore` is the default (tests, local
dev without a DB); `SQLAlchemyObservationStore` is the real implementation,
backed by Contributor 1's `observations` table.
"""
from __future__ import annotations

import os
from typing import Protocol


def _default_database_url() -> str:
    """
    Prefer an explicit DATABASE_URL. Otherwise assemble one from the same
    POSTGRES_* parts backend/app/config.py's Settings uses — this is what the
    worker Celery container actually gets from docker-compose.yml (it sets
    POSTGRES_HOST/PORT/DB/USER/PASSWORD, not DATABASE_URL directly), so both
    services resolve to the same database without extra compose wiring.
    """
    explicit = os.getenv("DATABASE_URL")
    if explicit:
        return explicit
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "agnidrishti")
    user = os.getenv("POSTGRES_USER", "agnidrishti")
    password = os.getenv("POSTGRES_PASSWORD", "changeme")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"


DATABASE_URL = _default_database_url()

_engine = None
_SessionLocal = None


def get_engine():
    """Lazily create the SQLAlchemy engine. Only imported/used by the real store."""
    global _engine
    if _engine is None:
        from sqlalchemy import create_engine

        _engine = create_engine(DATABASE_URL)
    return _engine


def get_session():
    global _SessionLocal
    if _SessionLocal is None:
        from sqlalchemy.orm import sessionmaker

        _SessionLocal = sessionmaker(bind=get_engine())
    return _SessionLocal()


class ObservationStore(Protocol):
    """Storage abstraction for normalized FIRMS observations."""

    def insert(self, obs: dict) -> bool:
        """Insert an observation. Returns False (no-op) if it's a duplicate."""
        ...

    def exists(self, satellite: str, timestamp_utc, latitude: float, longitude: float) -> bool:
        ...

    def get(self, observation_id: str) -> dict | None:
        ...

    def update(self, observation_id: str, fields: dict) -> None:
        ...

    def all(self) -> list[dict]:
        ...


def _dedup_key(obs: dict) -> tuple:
    return (obs["satellite"], obs["timestamp_utc"], obs["latitude"], obs["longitude"])


class InMemoryObservationStore:
    """Default store used in tests and local development. Not persisted across runs."""

    def __init__(self):
        self._by_id: dict[str, dict] = {}
        self._keys: set[tuple] = set()

    def insert(self, obs: dict) -> bool:
        key = _dedup_key(obs)
        if key in self._keys:
            return False
        self._keys.add(key)
        self._by_id[obs["id"]] = dict(obs)
        return True

    def exists(self, satellite: str, timestamp_utc, latitude: float, longitude: float) -> bool:
        return (satellite, timestamp_utc, latitude, longitude) in self._keys

    def get(self, observation_id: str) -> dict | None:
        return self._by_id.get(observation_id)

    def update(self, observation_id: str, fields: dict) -> None:
        if observation_id in self._by_id:
            self._by_id[observation_id].update(fields)

    def all(self) -> list[dict]:
        return list(self._by_id.values())


class SQLAlchemyObservationStore:
    """
    Real store backed by the `observations` table (Contributor 1's schema).
    Requires DATABASE_URL to point at a live Postgres+PostGIS instance with the
    unique constraint on (satellite, timestamp_utc, latitude, longitude).
    """

    def __init__(self, session=None):
        self._session = session or get_session()

    def insert(self, obs: dict) -> bool:
        from sqlalchemy import text

        result = self._session.execute(
            text(
                """
                INSERT INTO observations
                  (id, source_type, source_product, satellite, timestamp_utc,
                   latitude, longitude, geometry, h3_cell, frp, bright_ti4,
                   bright_ti5, confidence, quality_flags, raw_record_ref)
                VALUES
                  (:id, :source_type, :source_product, :satellite, :timestamp_utc,
                   :latitude, :longitude, ST_GeomFromText(:geometry),
                   :h3_cell, :frp, :bright_ti4, :bright_ti5,
                   :confidence, :quality_flags::jsonb, :raw_record_ref::jsonb)
                ON CONFLICT (satellite, timestamp_utc, latitude, longitude) DO NOTHING
                """
            ),
            {
                **obs,
                "quality_flags": str(obs.get("quality_flags")),
                "raw_record_ref": str(obs.get("raw_record_ref")),
            },
        )
        return result.rowcount > 0

    def exists(self, satellite: str, timestamp_utc, latitude: float, longitude: float) -> bool:
        from sqlalchemy import text

        row = self._session.execute(
            text(
                "SELECT 1 FROM observations WHERE satellite=:s AND timestamp_utc=:t "
                "AND latitude=:la AND longitude=:lo"
            ),
            {"s": satellite, "t": timestamp_utc, "la": latitude, "lo": longitude},
        ).first()
        return row is not None

    def get(self, observation_id: str) -> dict | None:
        from sqlalchemy import text

        row = self._session.execute(
            text("SELECT * FROM observations WHERE id=:id"), {"id": observation_id}
        ).mappings().first()
        return dict(row) if row else None

    def update(self, observation_id: str, fields: dict) -> None:
        from sqlalchemy import text

        set_clause = ", ".join(f"{k} = :{k}" for k in fields)
        self._session.execute(
            text(f"UPDATE observations SET {set_clause} WHERE id = :id"),
            {**fields, "id": observation_id},
        )

    def all(self) -> list[dict]:
        from sqlalchemy import text

        rows = self._session.execute(text("SELECT * FROM observations")).mappings().all()
        return [dict(r) for r in rows]
