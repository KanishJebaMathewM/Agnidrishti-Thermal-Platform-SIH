import h3
from shapely.geometry import Point

INDIA_H3_RESOLUTION = 7  # approx 5km cells — benchmark this


def lat_lon_to_h3(lat: float, lon: float, resolution: int = INDIA_H3_RESOLUTION) -> str:
    """Convert lat/lon to H3 cell index.

    Note: h3 v4 renamed `geo_to_h3` -> `latlng_to_cell` (the spec's original
    snippet used the v3 name, which no longer exists in h3==4.5.0).
    """
    return h3.latlng_to_cell(lat, lon, resolution)


def is_within_india(lat: float, lon: float, india_geom) -> bool:
    """Check whether a point is inside India's boundary polygon."""
    point = Point(lon, lat)
    return india_geom.contains(point)


def point_to_wkt(lat: float, lon: float) -> str:
    return f"SRID=4326;POINT({lon} {lat})"
