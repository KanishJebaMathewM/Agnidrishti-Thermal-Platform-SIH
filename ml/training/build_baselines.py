"""
Historical baseline builder (AGNIDRISHTI_PLAN.md Phase 9).

For each thermal source, compute baseline statistics across its historical
observations. This is what anomaly detection compares new observations
against (see ml/inference/anomaly_scorer.py). A source with no baseline
yet falls back to anomaly detection running on the z-score layer alone
once a baseline exists, or skipping the deviation-based layer entirely
until then.

Run this:
- Once after initial FIRMS backfill
- Periodically (monthly) to incorporate new verified data

This module has no hard dependency on a live database — it operates on
plain observation dicts. `scripts/build_baselines.py` is the thin CLI
wrapper; wiring it to real `thermal_sources`/`observations` rows and
persisting the result to the `source_baselines` table is Contributor 1's
integration point (see the loader/saver hooks in the script).
"""
from __future__ import annotations

from datetime import datetime, timezone

from ml.features.feature_builder import _coerce_timestamp

SEASON_OF_MONTH = {
    12: 1, 1: 1, 2: 1,   # Winter
    3: 2, 4: 2, 5: 2,    # Summer
    6: 3, 7: 3, 8: 3, 9: 3,  # Monsoon
    10: 4, 11: 4,        # Post-monsoon
}


def compute_source_baseline(observations: list[dict]) -> dict:
    """
    Compute baseline statistics for a single source from its historical
    observations.

    Args:
        observations: list of dicts, each with at least `timestamp_utc` and
                       optionally `frp`.

    Returns:
        dict matching the `source_baselines` shape:
        mean_frp, frp_std, median_frp, typical_hours, monthly_profile,
        seasonal_profile, observation_count, first_seen, last_seen
    """
    frp_values = [o["frp"] for o in observations if o.get("frp") is not None]
    timestamps = [_coerce_timestamp(o.get("timestamp_utc")) for o in observations]
    timestamps = [t for t in timestamps if t is not None]

    mean_frp = _mean(frp_values)
    frp_std = _std(frp_values, mean_frp)
    median_frp = _median(frp_values)

    typical_hours = {h: 0 for h in range(24)}
    monthly_sums: dict[int, list[float]] = {m: [] for m in range(1, 13)}
    seasonal_sums: dict[int, list[float]] = {s: [] for s in range(1, 5)}

    for obs, ts in zip(observations, timestamps):
        typical_hours[ts.hour] += 1
        frp = obs.get("frp")
        if frp is not None:
            monthly_sums[ts.month].append(frp)
            seasonal_sums[SEASON_OF_MONTH[ts.month]].append(frp)

    monthly_profile = {m: _mean(v) for m, v in monthly_sums.items() if v}
    seasonal_profile = {s: _mean(v) for s, v in seasonal_sums.items() if v}

    return {
        "mean_frp": mean_frp,
        "frp_std": frp_std,
        "median_frp": median_frp,
        "typical_hours": typical_hours,
        "monthly_profile": monthly_profile,
        "seasonal_profile": seasonal_profile,
        "observation_count": len(observations),
        "first_seen": min(timestamps).isoformat() if timestamps else None,
        "last_seen": max(timestamps).isoformat() if timestamps else None,
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }


def build_all_baselines(observations_by_source: dict[str, list[dict]]) -> dict[str, dict]:
    """Compute baselines for every source in `observations_by_source`."""
    return {
        source_id: compute_source_baseline(obs_list)
        for source_id, obs_list in observations_by_source.items()
        if obs_list
    }


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    s = sorted(values)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2


def _std(values: list[float], mean: float | None) -> float | None:
    if not values or mean is None or len(values) < 2:
        return None
    variance = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    return variance ** 0.5
