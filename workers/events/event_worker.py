"""
Event formation worker (AGNIDRISHTI_PLAN.md Phase 15-17).

Runs after an observation has been preprocessed, enriched, and classified.
Groups nearby, temporally-close observations into a single Event so one
physical episode does not become multiple alerts.

Algorithm (deterministic grouping — not ST-DBSCAN for the prototype):
1. Load the classified observation.
2. Look for an existing OPEN event that:
   - has a centroid within 10km of this observation
   - has last_seen within the last 12 hours
   - has the same classification (or is still NEW/ANALYZING)
3. If found: add observation to existing event, update centroid, update stats.
4. If not found: create a new event with status=NEW.

Event centroid update rule: weighted mean of all observation positions,
weighted by FRP (falls back to an unweighted mean if no observation in the
event has a usable FRP value).

Event status transitions:
  NEW -> ANALYZING (when first ML result attached)
  ANALYZING -> CANDIDATE (when confidence > 0.6 and at least 1 observation)
  CANDIDATE -> HUMAN_REVIEW (when severity >= HIGH)
  All other states transition via the human feedback API (Contributor 5).

Event severity (deterministic, AGNIDRISHTI_PLAN.md Phase 17):
  Score = classification_confidence*30 + anomaly_score*30
        + persistence_factor*20 (nights active / 14, capped at 1.0)
        + frp_intensity_factor*20 (current_frp / 500 MW, capped at 1.0)
  severity:
    score >= 80 -> CRITICAL
    score >= 60 -> HIGH
    score >= 40 -> REVIEW
    score >= 20 -> OBSERVE
    default    -> NORMAL

------------------------------------------------------------------------
No hard dependency on a live database or broker. The grouping/severity/
status logic below is pure and given the same observations in the same
order always produces the same events (no randomness anywhere).

`EventDataStore` is the integration seam for Contributor 1: implement it
against SQLAlchemy/PostGIS and pass an instance to `process_event(...)` (or
register it as the module default) — nothing in the pure logic functions
needs to change.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Protocol

try:
    from celery import shared_task
except ImportError:  # pragma: no cover - celery not installed in this environment
    def shared_task(*_args, **_kwargs):
        def _decorator(fn):
            return fn
        return _decorator

from ml.features.feature_builder import _coerce_timestamp

EARTH_RADIUS_KM = 6371.0088
MAX_DISTANCE_KM = 10.0
MAX_TIME_GAP_HOURS = 12
PERSISTENCE_CAP_NIGHTS = 14
FRP_INTENSITY_CAP_MW = 500.0
CANDIDATE_CONFIDENCE_THRESHOLD = 0.6

OPEN_STATUSES = ("NEW", "ANALYZING", "CANDIDATE", "HUMAN_REVIEW")


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two lat/lon points, in kilometers."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(min(1.0, math.sqrt(a)))


def weighted_centroid(observations: list[dict]) -> tuple[float, float]:
    """
    Weighted mean position of `observations`, weighted by FRP.

    Falls back to an unweighted mean if no observation has a usable
    (non-None, positive) FRP value.
    """
    weights = [o.get("frp") or 0 for o in observations]
    total_weight = sum(w for w in weights if w and w > 0)

    if total_weight <= 0:
        n = len(observations)
        lat = sum(o["latitude"] for o in observations) / n
        lon = sum(o["longitude"] for o in observations) / n
        return lat, lon

    lat = sum(o["latitude"] * (o.get("frp") or 0) for o in observations) / total_weight
    lon = sum(o["longitude"] * (o.get("frp") or 0) for o in observations) / total_weight
    return lat, lon


def compute_severity(
    classification_confidence: float | None,
    anomaly_score: float | None,
    persistence_nights: float,
    frp: float | None,
) -> tuple[float, str]:
    """
    Deterministic severity scoring. `classification_confidence` and
    `anomaly_score` are expected on a 0-1 scale.
    """
    confidence_pts = (classification_confidence or 0.0) * 30
    anomaly_pts = (anomaly_score or 0.0) * 30
    persistence_factor = min(persistence_nights / PERSISTENCE_CAP_NIGHTS, 1.0)
    persistence_pts = persistence_factor * 20
    frp_factor = min((frp or 0.0) / FRP_INTENSITY_CAP_MW, 1.0)
    frp_pts = frp_factor * 20

    score = confidence_pts + anomaly_pts + persistence_pts + frp_pts

    if score >= 80:
        severity = "CRITICAL"
    elif score >= 60:
        severity = "HIGH"
    elif score >= 40:
        severity = "REVIEW"
    elif score >= 20:
        severity = "OBSERVE"
    else:
        severity = "NORMAL"

    return score, severity


def _event_is_open(event: dict) -> bool:
    return event.get("status") in OPEN_STATUSES


def find_matching_event(
    observation: dict,
    open_events: list[dict],
    max_distance_km: float = MAX_DISTANCE_KM,
    max_time_hours: int = MAX_TIME_GAP_HOURS,
) -> dict | None:
    """
    Find the first open event this observation should join, or None to
    start a new event. Deterministic: `open_events` order is preserved, so
    the same input always yields the same match.
    """
    obs_ts = _coerce_timestamp(observation.get("timestamp_utc"))
    obs_classification = observation.get("classification")

    for event in open_events:
        if not _event_is_open(event):
            continue

        last_seen = _coerce_timestamp(event.get("last_seen"))
        if obs_ts and last_seen:
            gap_hours = abs((obs_ts - last_seen).total_seconds()) / 3600.0
            if gap_hours > max_time_hours:
                continue

        distance = haversine_km(
            observation["latitude"], observation["longitude"],
            event["centroid_lat"], event["centroid_lon"],
        )
        if distance > max_distance_km:
            continue

        same_classification = obs_classification is None or event.get("classification") in (
            None, obs_classification
        )
        still_forming = event.get("status") in ("NEW", "ANALYZING")
        if same_classification or still_forming:
            return event

    return None


def _persistence_nights(event: dict) -> float:
    """Approximate 'nights active' as whole days between first_seen and last_seen."""
    first_seen = _coerce_timestamp(event.get("first_seen"))
    last_seen = _coerce_timestamp(event.get("last_seen"))
    if not first_seen or not last_seen:
        return 0.0
    return max((last_seen - first_seen).total_seconds() / 86400.0, 0.0)


def _advance_status(event: dict) -> str:
    status = event.get("status", "NEW")

    if status == "NEW" and event.get("classification") is not None:
        status = "ANALYZING"

    if status == "ANALYZING" and (event.get("classification_confidence") or 0) > CANDIDATE_CONFIDENCE_THRESHOLD \
            and event.get("observation_count", 0) >= 1:
        status = "CANDIDATE"

    if status == "CANDIDATE" and event.get("severity") in ("HIGH", "CRITICAL"):
        status = "HUMAN_REVIEW"

    return status


def apply_observation_to_event(
    event: dict | None,
    observation: dict,
    classification: dict | None = None,
    anomaly: dict | None = None,
) -> dict:
    """
    Fold `observation` (with its optional classification/anomaly results)
    into `event`, or create a new event if `event` is None.

    Returns the updated event dict. Does not mutate the input `event`.
    """
    obs_ts = _coerce_timestamp(observation.get("timestamp_utc")) or datetime.now(timezone.utc)

    if event is None:
        event = {
            "id": None,  # assigned by the store on persist
            "first_seen": obs_ts.isoformat(),
            "last_seen": obs_ts.isoformat(),
            "observation_count": 0,
            "observations": [],
            "source_id": observation.get("source_id"),
            "status": "NEW",
            "classification": None,
            "classification_confidence": None,
            "anomaly_score": None,
            "anomaly_flag": False,
        }
    else:
        event = dict(event)
        event["observations"] = list(event.get("observations", []))

    event["observations"].append(observation)
    event["observation_count"] = len(event["observations"])

    last_seen = _coerce_timestamp(event.get("last_seen"))
    if not last_seen or obs_ts > last_seen:
        event["last_seen"] = obs_ts.isoformat()
    first_seen = _coerce_timestamp(event.get("first_seen"))
    if not first_seen or obs_ts < first_seen:
        event["first_seen"] = obs_ts.isoformat()

    centroid_lat, centroid_lon = weighted_centroid(event["observations"])
    event["centroid_lat"] = centroid_lat
    event["centroid_lon"] = centroid_lon

    # Event-level classification/anomaly reflect the most recent ML result
    # (the newest observation is the most informative about current state);
    # anomaly_score is the max seen across the event's lifetime so a past
    # spike is not silently forgotten once things calm down.
    if classification is not None:
        event["classification"] = classification.get("predicted_class")
        event["classification_confidence"] = classification.get("confidence")
        event["model_version"] = classification.get("model_version")

    if anomaly is not None:
        prior_score = event.get("anomaly_score") or 0.0
        event["anomaly_score"] = max(prior_score, anomaly.get("anomaly_score") or 0.0)
        event["anomaly_flag"] = bool(event.get("anomaly_flag")) or bool(anomaly.get("anomaly_flag"))

    persistence_nights = _persistence_nights(event)
    current_frp = observation.get("frp")
    score, severity = compute_severity(
        event.get("classification_confidence"),
        event.get("anomaly_score"),
        persistence_nights,
        current_frp,
    )
    event["severity_score"] = score
    event["severity"] = severity
    event["status"] = _advance_status(event)

    return event


def process_event_logic(
    observation: dict,
    open_events: list[dict],
    classification: dict | None = None,
    anomaly: dict | None = None,
) -> dict:
    """
    Pure event-formation step for a single observation.

    Returns the resulting event dict with an extra `_is_new` bool so the
    caller (store-backed wrapper) knows whether to insert or update.
    """
    matched = find_matching_event(observation, open_events)
    is_new = matched is None
    updated = apply_observation_to_event(matched, observation, classification, anomaly)
    updated["_is_new"] = is_new
    return updated


class EventDataStore(Protocol):
    """Integration seam: implement against real storage (Contributor 1)."""

    def get_observation(self, observation_id: str) -> dict | None: ...
    def get_inference_result(self, observation_id: str) -> dict | None: ...
    def find_open_events_near(self, latitude: float, longitude: float) -> list[dict]: ...
    def save_event(self, event: dict) -> dict: ...


class InMemoryEventStore:
    """
    Default in-process store used for tests, the replay/demo mode
    (AGNIDRISHTI_PLAN.md Phase 40), and local development without a
    database. Not for production use.
    """

    def __init__(self):
        self._observations: dict[str, dict] = {}
        self._inference_results: dict[str, dict] = {}
        self._events: list[dict] = []
        self._next_event_id = 1

    def add_observation(self, observation: dict, inference_result: dict | None = None) -> None:
        self._observations[observation["id"]] = observation
        if inference_result is not None:
            self._inference_results[observation["id"]] = inference_result

    def get_observation(self, observation_id: str) -> dict | None:
        return self._observations.get(observation_id)

    def get_inference_result(self, observation_id: str) -> dict | None:
        return self._inference_results.get(observation_id)

    def find_open_events_near(self, latitude: float, longitude: float) -> list[dict]:
        # A real implementation would use a PostGIS bounding-box/KNN query;
        # in-memory we just return all open events and let
        # `find_matching_event` apply the exact distance/time filter.
        return [e for e in self._events if _event_is_open(e)]

    def save_event(self, event: dict) -> dict:
        event = dict(event)
        is_new = event.pop("_is_new", False)
        if is_new or event.get("id") is None:
            event["id"] = f"EVT-{self._next_event_id:06d}"
            self._next_event_id += 1
            self._events.append(event)
        else:
            for i, existing in enumerate(self._events):
                if existing.get("id") == event["id"]:
                    self._events[i] = event
                    break
            else:
                self._events.append(event)
        return event


_default_store = InMemoryEventStore()


@shared_task(name="workers.events.process_event")
def process_event(observation_id: str, store: EventDataStore | None = None) -> dict | None:
    """
    Celery task: fold one observation into an event.

    Expects the observation's classification/anomaly result to already be
    attached (via `run_inference` in workers/inference/inference_worker.py,
    which triggers this task after saving its result).
    """
    store = store or _default_store
    observation = store.get_observation(observation_id)
    if observation is None:
        return None

    inference_result = store.get_inference_result(observation_id) or {}
    classification = {
        "predicted_class": inference_result.get("predicted_class"),
        "confidence": inference_result.get("confidence"),
        "model_version": inference_result.get("model_version"),
    } if inference_result.get("predicted_class") is not None else None
    anomaly = {
        "anomaly_score": inference_result.get("anomaly_score"),
        "anomaly_flag": inference_result.get("anomaly_flag"),
    } if "anomaly_score" in inference_result else None

    open_events = store.find_open_events_near(observation["latitude"], observation["longitude"])
    event = process_event_logic(observation, open_events, classification, anomaly)
    return store.save_event(event)
