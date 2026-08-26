"""
Geographic enrichment.

Production target (AGNIDRISHTI_PLAN.md): PostGIS point-in-polygon /
nearest-neighbor queries against `admin_boundaries`, `industrial_facilities`,
`landuse_features`, `forest_boundaries` tables owned by Contributor 1 — those
tables don't exist yet. Until they do, this module does the same lookups with
GeoPandas spatial joins against the small dev-scale reference layers in
data/reference/{admin,osm,landuse,forest}/ (see scripts/bootstrap.py for how
the real GADM/OSM/Forest-Survey data replaces them).

Critical rule from AGNIDRISHTI_PLAN.md:
  "Missing data must not be interpreted as a negative fire observation."
  If a geography lookup fails or the point falls outside every reference
  polygon we have, the field is set to None — never guessed or defaulted.
"""
from __future__ import annotations

import math
import os
from functools import lru_cache

REFERENCE_BASE = os.path.join(os.path.dirname(__file__), "../../data/reference")

# Facilities farther than this from a point are not considered "nearby" —
# beyond this, "no facility found" is the honest answer rather than a guess.
NEAREST_FACILITY_MAX_KM = 50.0


@lru_cache(maxsize=1)
def _load_layers():
    import geopandas as gpd

    admin = gpd.read_file(os.path.join(REFERENCE_BASE, "admin", "india_states.geojson"))
    landuse = gpd.read_file(os.path.join(REFERENCE_BASE, "landuse", "landuse_features.geojson"))
    forest = gpd.read_file(os.path.join(REFERENCE_BASE, "forest", "forest_boundaries.geojson"))
    industrial = gpd.read_file(os.path.join(REFERENCE_BASE, "osm", "industrial_facilities.geojson"))
    return admin, landuse, forest, industrial


def _point_in_polygon_lookup(lat: float, lon: float, gdf, value_column: str) -> str | None:
    from shapely.geometry import Point

    point = Point(lon, lat)
    matches = gdf[gdf.contains(point)]
    if matches.empty:
        return None
    return matches.iloc[0][value_column]


def _haversine_km(lat1, lon1, lat2, lon2) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _nearest_facility(lat: float, lon: float, industrial_gdf):
    """Nearest facility within NEAREST_FACILITY_MAX_KM, by haversine distance.

    Production note: with the real `industrial_facilities` PostGIS table this
    becomes a single `ORDER BY geometry <-> point LIMIT 1` KNN query, not a
    Python loop — looping here is fine only because the dev fixture has a
    handful of rows.
    """
    best = None
    best_dist = None
    for _, row in industrial_gdf.iterrows():
        facility_lon, facility_lat = row.geometry.x, row.geometry.y
        dist = _haversine_km(lat, lon, facility_lat, facility_lon)
        if best_dist is None or dist < best_dist:
            best_dist, best = dist, row
    if best is None or best_dist > NEAREST_FACILITY_MAX_KM:
        return None, None, None
    return best["name"], best["facility_type"], round(best_dist, 2)


def enrich_geography_context(lat: float, lon: float) -> dict:
    """Returns geographic context for a point. Any field the reference data
    can't confidently determine is None — never guessed."""
    try:
        admin, landuse, forest, industrial = _load_layers()
    except Exception:
        # Reference data unreadable — everything is genuinely unknown.
        return {
            "state": None,
            "landuse_class": None,
            "is_forest": None,
            "nearest_facility_name": None,
            "nearest_facility_type": None,
            "nearest_facility_km": None,
        }

    state = _point_in_polygon_lookup(lat, lon, admin, "state")
    landuse_class = _point_in_polygon_lookup(lat, lon, landuse, "class")
    forest_match = _point_in_polygon_lookup(lat, lon, forest, "name")
    facility_name, facility_type, facility_km = _nearest_facility(lat, lon, industrial)

    return {
        "state": state,
        "landuse_class": landuse_class,
        "is_forest": forest_match is not None,
        "nearest_facility_name": facility_name,
        "nearest_facility_type": facility_type,
        "nearest_facility_km": facility_km,
    }


try:
    from celery import shared_task
except ImportError:  # pragma: no cover - celery not installed in this environment
    def shared_task(*_args, **_kwargs):
        def _decorator(fn):
            return fn
        return _decorator


@shared_task(name="workers.enrichment.enrich_geography")
def enrich_geography(observation_id: str, store=None):
    """Celery task wrapper: enrich the observation in `store` with geographic
    context and write it back. `store` must be an ObservationStore instance."""
    if store is None:
        raise ValueError("enrich_geography requires an ObservationStore instance")
    obs = store.get(observation_id)
    if obs is None:
        return None
    context = enrich_geography_context(obs["latitude"], obs["longitude"])
    store.update(observation_id, {"thermal_features": {**(obs.get("thermal_features") or {}), **context}})
    return context
