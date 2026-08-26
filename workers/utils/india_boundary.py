"""
Load the India boundary polygon once at import time.

The boundary GeoJSON file lives at:
  data/reference/boundaries/india_boundary.geojson

It is a Natural Earth 110m admin-0 country polygon (public domain), extracted
by scripts/bootstrap.py's india_boundary step. It is a country-level polygon
suitable for the FIRMS-bbox-then-boundary-clip check — not authoritative for
state/district-level enrichment (that uses data/reference/admin/).
"""

import os

_india_geom = None


def get_india_geom():
    global _india_geom
    if _india_geom is None:
        import geopandas as gpd
        from shapely.ops import unary_union

        path = os.path.join(
            os.path.dirname(__file__), "../../data/reference/boundaries/india_boundary.geojson"
        )
        gdf = gpd.read_file(path)
        _india_geom = unary_union(gdf.geometry)
    return _india_geom
