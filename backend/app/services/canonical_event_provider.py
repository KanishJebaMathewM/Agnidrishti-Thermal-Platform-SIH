"""
Canonical Event Provider — Fast, paginated, lazy event generation.

Generates event data on-demand for the requested page/filters only,
never building the full 65,840-event corpus in memory at once.
Backed by deterministic index arithmetic so results are stable and reproducible.
"""

from __future__ import annotations

import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

TOTAL_EVENTS = 65840
TRAIN_END = 42580       # 2020-2024
VAL_END = 42580 + 12410  # 2025

INDIAN_STATES = [
    "Punjab", "Haryana", "Odisha", "Chhattisgarh", "Assam", "Maharashtra",
    "Madhya Pradesh", "Uttar Pradesh", "Rajasthan", "Gujarat", "Karnataka",
    "Tamil Nadu", "Delhi", "West Bengal", "Jharkhand", "Telangana", "Andhra Pradesh",
    "Uttarakhand", "Himachal Pradesh", "Bihar"
]

DISTRICTS = {
    "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda", "Firozpur"],
    "Haryana": ["Karnal", "Kurukshetra", "Ambala", "Hisar", "Panipat", "Kaithal"],
    "Odisha": ["Mayurbhanj", "Sundargarh", "Kendrapara", "Sambalpur", "Koraput"],
    "Chhattisgarh": ["Bastar", "Durg", "Raipur", "Korba", "Bilaspur"],
    "Assam": ["Kamrup", "Dibrugarh", "Golaghat", "Jorhat", "Nagaon"],
    "Maharashtra": ["Chandrapur", "Gadchiroli", "Nagpur", "Pune", "Nashik", "Thane"],
    "Madhya Pradesh": ["Balaghat", "Chhindwara", "Hoshangabad", "Indore", "Bhopal"],
    "Uttar Pradesh": ["Mathura", "Agra", "Varanasi", "Gorakhpur", "Lucknow", "Jhansi"],
    "Delhi": ["New Delhi", "North Delhi", "South Delhi", "West Delhi"],
}

CLASSIFICATIONS = [
    ("Agricultural Burn", 94.1),
    ("Industrial Incident", 95.4),
    ("Forest Fire", 88.5),
    ("Persistent Flare/Kiln", 85.5),
    ("Unknown", 91.0),
]

SATS = ["N20", "SV", "J2"]


def _make_event(idx: int) -> Dict[str, Any]:
    """Generate a single deterministic event dict by index. O(1) per call."""
    if idx < TRAIN_END:
        year = 2020 + (idx % 5)
    elif idx < VAL_END:
        year = 2025
    else:
        year = 2026

    month = 1 + (idx % 12)
    day = 1 + (idx % 28)
    hour = (idx * 3 + 1) % 24
    minute = (idx * 7) % 60
    sec = (idx * 11) % 60
    ts = f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{sec:02d}Z"

    state = INDIAN_STATES[idx % len(INDIAN_STATES)]
    dlist = DISTRICTS.get(state, ["Central District"])
    district = dlist[idx % len(dlist)]

    lat = round(10.0 + (idx % 2200) * 0.01, 4)
    lon = round(70.0 + (idx % 2200) * 0.01, 4)

    cls_name, base_conf = CLASSIFICATIONS[idx % len(CLASSIFICATIONS)]
    conf = round(base_conf - (idx % 15) * 0.5, 1)

    sat = SATS[idx % 3]
    frp = round(12.5 + (idx % 180) * 1.85, 1)
    ti4 = round(325.0 + (idx % 85) * 0.8, 1)
    ti5 = round(290.0 + (idx % 35) * 0.6, 1)

    is_anomaly = (cls_name == "Industrial Incident") or (frp > 180.0) or ((idx % 7) == 0)
    status = "CONFIRMED" if is_anomaly and (idx % 2 == 0) else ("FALSE_ALARM" if (idx % 5 == 0) else "NEW")
    severity = "CRITICAL" if (frp > 220.0 or cls_name == "Industrial Incident") else ("HIGH" if is_anomaly else "NORMAL")
    obs_count = 1 + (idx % 14)

    return {
        "id": f"evt-nasa-{year}-{idx:06d}",
        "centroid_lat": lat,
        "centroid_lon": lon,
        "h3_cell": f"88{idx % 9999:04x}8281fffff",
        "state": state,
        "district": district,
        "placeName": f"{district}, {state}",
        "classification": cls_name,
        "classification_confidence": round(conf / 100.0, 3),
        "confidence": conf,
        "anomaly_score": round(0.92 if is_anomaly else 0.15, 2),
        "anomaly_flag": is_anomaly,
        "isAnomaly": is_anomaly,
        "severity": severity,
        "status": status,
        "first_seen": ts,
        "last_seen": ts,
        "timestamp": ts,
        "observation_count": obs_count,
        "max_frp": frp,
        "mean_frp": frp,
        "frp": frp,
        "bright_ti4": ti4,
        "bright_ti5": ti5,
        "brightnessTemp4": ti4,
        "brightnessTemp11": ti5,
        "satellite": sat,
        "instrument": "VIIRS",
        "year": year,
    }


def _matches_filters(
    idx: int,
    state: Optional[str],
    classification: Optional[str],
    status: Optional[str],
    anomaly_only: bool,
    bbox_parsed: Optional[tuple],
    from_dt: Optional[datetime],
    to_dt: Optional[datetime],
) -> bool:
    """Check if event at `idx` passes all filters without building a full dict."""
    # Quick state check
    if state and state.lower() != "all":
        s = INDIAN_STATES[idx % len(INDIAN_STATES)]
        if state.lower() not in s.lower():
            return False

    # Classification
    if classification and classification.lower() != "all":
        cls_name = CLASSIFICATIONS[idx % len(CLASSIFICATIONS)][0]
        if cls_name.lower() != classification.lower():
            return False

    # Status
    if status and status.lower() != "all":
        cls_name = CLASSIFICATIONS[idx % len(CLASSIFICATIONS)][0]
        frp = round(12.5 + (idx % 180) * 1.85, 1)
        is_anomaly = (cls_name == "Industrial Incident") or (frp > 180.0) or ((idx % 7) == 0)
        evt_status = "CONFIRMED" if is_anomaly and (idx % 2 == 0) else ("FALSE_ALARM" if (idx % 5 == 0) else "NEW")
        if status == "Escalated" and evt_status != "CONFIRMED":
            return False
        elif status == "Suppressed" and evt_status != "FALSE_ALARM":
            return False
        elif status == "Under Review" and evt_status != "NEW":
            return False
        elif status not in ["Escalated", "Suppressed", "Under Review"] and evt_status != status:
            return False

    # Anomaly only
    if anomaly_only:
        cls_name = CLASSIFICATIONS[idx % len(CLASSIFICATIONS)][0]
        frp = round(12.5 + (idx % 180) * 1.85, 1)
        is_anomaly = (cls_name == "Industrial Incident") or (frp > 180.0) or ((idx % 7) == 0)
        if not is_anomaly:
            return False

    # Bbox
    if bbox_parsed:
        min_lon, min_lat, max_lon, max_lat = bbox_parsed
        lat = round(10.0 + (idx % 2200) * 0.01, 4)
        lon = round(70.0 + (idx % 2200) * 0.01, 4)
        if lon < min_lon or lon > max_lon or lat < min_lat or lat > max_lat:
            return False

    # Date
    if from_dt or to_dt:
        if idx < TRAIN_END:
            year = 2020 + (idx % 5)
        elif idx < VAL_END:
            year = 2025
        else:
            year = 2026
        month = 1 + (idx % 12)
        day = 1 + (idx % 28)
        hour = (idx * 3 + 1) % 24
        minute = (idx * 7) % 60
        sec = (idx * 11) % 60
        e_dt = datetime(year, month, day, hour, minute, sec)
        if from_dt and e_dt < from_dt:
            return False
        if to_dt and e_dt > to_dt:
            return False

    return True


def query_canonical_events(
    page: int = 1,
    limit: int = 50,
    state: Optional[str] = None,
    classification: Optional[str] = None,
    status: Optional[str] = None,
    anomaly_only: bool = False,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    bbox: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], int]:
    """Paginated query — only materializes the dicts for the requested page."""

    bbox_parsed = None
    if bbox:
        try:
            parts = [float(x.strip()) for x in bbox.split(",")]
            if len(parts) == 4:
                bbox_parsed = tuple(parts)
        except Exception:
            pass

    from_dt = from_date.replace(tzinfo=None) if from_date else None
    to_dt = to_date.replace(tzinfo=None) if to_date else None

    # Count matching events and collect indices for the requested page
    skip = (page - 1) * limit
    matched = 0
    page_indices: List[int] = []

    for idx in range(TOTAL_EVENTS):
        if _matches_filters(idx, state, classification, status, anomaly_only, bbox_parsed, from_dt, to_dt):
            if matched >= skip and len(page_indices) < limit:
                page_indices.append(idx)
            matched += 1

    # Only build full dicts for the page
    items = [_make_event(i) for i in page_indices]
    return items, matched


def get_event_by_id(event_id: str) -> Optional[Dict[str, Any]]:
    """Look up a single event by its deterministic ID. O(1)."""
    # ID format: evt-nasa-{year}-{idx:06d}
    try:
        parts = event_id.split("-")
        idx = int(parts[-1])
        if 0 <= idx < TOTAL_EVENTS:
            evt = _make_event(idx)
            if evt["id"] == event_id:
                return evt
    except (ValueError, IndexError):
        pass

    # Fallback linear scan for non-standard IDs (rare)
    for idx in range(min(1000, TOTAL_EVENTS)):
        evt = _make_event(idx)
        if evt["id"] == event_id:
            return evt
    return None
