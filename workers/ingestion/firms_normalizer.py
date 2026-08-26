"""
Normalize raw NASA FIRMS VIIRS CSV rows into the observation dict shape that
workers.utils.db.ObservationStore consumes.

VIIRS SNPP CSV columns: latitude, longitude, bright_ti4, bright_ti5, scan, track,
acq_date, acq_time, satellite, instrument, confidence, version, bright_t31, frp,
daynight, type
"""
import uuid
from datetime import datetime, timezone

import pandas as pd

from workers.ingestion.firms_client import PRODUCT_NRT
from workers.utils.geo import lat_lon_to_h3, point_to_wkt

INDIA_BBOX_BOUNDS = (6.0, 38.0, 65.0, 98.0)  # lat_min, lat_max, lon_min, lon_max


def normalize_firms_row(row: pd.Series) -> dict | None:
    """
    Convert a single FIRMS VIIRS row to a normalized observation dict.
    Returns None if the row is invalid. Does NOT do the India boundary
    point-in-polygon check — that's a separate step (bbox is rectangular,
    the real boundary is not) done by the caller against get_india_geom().
    """
    try:
        lat = float(row["latitude"])
        lon = float(row["longitude"])
    except (ValueError, KeyError, TypeError):
        return None

    lat_min, lat_max, lon_min, lon_max = INDIA_BBOX_BOUNDS
    if not (lat_min <= lat <= lat_max and lon_min <= lon <= lon_max):
        return None

    try:
        acq_date = str(row["acq_date"])  # YYYY-MM-DD
        acq_time = str(row.get("acq_time", "0000")).zfill(4)
        timestamp_str = f"{acq_date} {acq_time[:2]}:{acq_time[2:]}:00"
        timestamp_utc = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=timezone.utc
        )
    except (KeyError, ValueError):
        return None

    confidence = str(row.get("confidence", "nominal")).lower().strip()
    if confidence not in ("low", "nominal", "high"):
        confidence = "nominal"

    frp = _safe_float(row.get("frp"))
    bright_ti4 = _safe_float(row.get("bright_ti4"))
    bright_ti5 = _safe_float(row.get("bright_ti5"))

    # FRP sanity check — VIIRS physically cannot report > 200,000 MW
    if frp is not None and (frp < 0 or frp > 200_000):
        frp = None

    h3_cell = lat_lon_to_h3(lat, lon)
    geometry_wkt = point_to_wkt(lat, lon)

    return {
        "id": str(uuid.uuid4()),
        "source_type": "FIRMS_VIIRS",
        "source_product": str(row.get("version", PRODUCT_NRT)),
        "satellite": str(row.get("satellite", "SNPP")),
        "timestamp_utc": timestamp_utc,
        "latitude": lat,
        "longitude": lon,
        "geometry": geometry_wkt,
        "h3_cell": h3_cell,
        "frp": frp,
        "bright_ti4": bright_ti4,
        "bright_ti5": bright_ti5,
        "confidence": confidence,
        "quality_flags": {
            "daynight": str(row.get("daynight", "D")),
            "scan": _safe_float(row.get("scan")),
            "track": _safe_float(row.get("track")),
        },
        "thermal_features": None,
        "raw_record_ref": row.to_dict(),
        "source_id": None,
    }


def _safe_float(val) -> float | None:
    try:
        v = float(val)
        return None if pd.isna(v) else v
    except (ValueError, TypeError):
        return None
