"""
Pure quality-check functions over an observation dict (see
workers/ingestion/firms_normalizer.py for the shape). Each check returns a
flag, never deletes or mutates the record's substantive fields — invalid
observations are marked, not discarded, per AGNIDRISHTI_PLAN.md's rule that
missing/bad data must not be silently dropped or interpreted as "no fire."
"""
from __future__ import annotations

from datetime import datetime, timezone

from workers.utils.geo import is_within_india, lat_lon_to_h3

MIN_VALID_YEAR = 2000
FRP_MIN, FRP_MAX = 0.0, 200_000.0
BRIGHTNESS_MIN, BRIGHTNESS_MAX = 200.0, 500.0


def check_within_india(obs: dict, india_geom) -> bool:
    return is_within_india(obs["latitude"], obs["longitude"], india_geom)


def check_timestamp_valid(obs: dict, now: datetime | None = None) -> bool:
    ts = obs.get("timestamp_utc")
    if ts is None:
        return False
    now = now or datetime.now(timezone.utc)
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return MIN_VALID_YEAR <= ts.year and ts <= now


def check_frp_valid(obs: dict) -> bool:
    frp = obs.get("frp")
    if frp is None:
        return True  # missing is not invalid — just unknown
    return FRP_MIN <= frp <= FRP_MAX


def check_brightness_valid(obs: dict) -> bool:
    for key in ("bright_ti4", "bright_ti5"):
        val = obs.get(key)
        if val is not None and not (BRIGHTNESS_MIN <= val <= BRIGHTNESS_MAX):
            return False
    return True


def ensure_h3_cell(obs: dict) -> str:
    """Return the observation's H3 cell, computing it if missing."""
    if obs.get("h3_cell"):
        return obs["h3_cell"]
    return lat_lon_to_h3(obs["latitude"], obs["longitude"])


def run_quality_checks(obs: dict, india_geom) -> dict:
    """
    Run all quality checks and return the updated `quality_flags` dict to be
    merged into the observation's existing quality_flags. Does not raise and
    does not delete the observation — flags are informational.
    """
    existing = dict(obs.get("quality_flags") or {})
    existing.update(
        {
            "within_india_boundary": check_within_india(obs, india_geom),
            "timestamp_valid": check_timestamp_valid(obs),
            "frp_valid": check_frp_valid(obs),
            "brightness_valid": check_brightness_valid(obs),
        }
    )
    return existing
