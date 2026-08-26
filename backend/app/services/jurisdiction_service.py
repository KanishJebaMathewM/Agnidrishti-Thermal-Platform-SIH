"""Deterministic PostGIS jurisdiction lookup for Indian events."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text

UNKNOWN_JURISDICTION = {
    "state_id": "UNKNOWN",
    "state_name": "Unknown / Offshore",
    "district_id": "UNKNOWN",
    "district_name": "Unknown",
    "country": "India",
}


class InvalidCoordinates(ValueError):
    """Raised when coordinates cannot represent a valid geographic point."""


def _validate_coordinates(lat: float, lon: float) -> tuple[float, float]:
    if isinstance(lat, bool) or isinstance(lon, bool):
        raise InvalidCoordinates("latitude and longitude must be numeric")
    try:
        latitude = float(lat)
        longitude = float(lon)
    except (TypeError, ValueError) as exc:
        raise InvalidCoordinates("latitude and longitude must be numeric") from exc
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise InvalidCoordinates("latitude or longitude is outside valid bounds")
    return latitude, longitude


async def resolve_jurisdiction(db: Any, lat: float, lon: float) -> dict[str, str]:
    """Resolve a point using PostGIS, returning a stable unknown fallback."""
    latitude, longitude = _validate_coordinates(lat, lon)
    query = text(
        """
        SELECT state_id, state_name, district_id, district_name
        FROM admin_boundaries
        WHERE ST_Contains(
            geometry,
            ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)
        )
        ORDER BY CASE level WHEN 'DISTRICT' THEN 0 WHEN 'STATE' THEN 1 ELSE 2 END
        LIMIT 1
        """
    )
    result = await db.execute(query, {"lat": latitude, "lon": longitude})
    row = result.fetchone()
    if row is None:
        return dict(UNKNOWN_JURISDICTION)

    def value(name: str) -> str:
        if hasattr(row, name):
            return str(getattr(row, name))
        return str(row._mapping[name])

    return {
        "state_id": value("state_id"),
        "state_name": value("state_name"),
        "district_id": value("district_id"),
        "district_name": value("district_name"),
        "country": "India",
    }
