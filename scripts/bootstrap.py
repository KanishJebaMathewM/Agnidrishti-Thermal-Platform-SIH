"""
One-time setup script for the data pipeline. Run before anything else that
needs real reference geodata.

What it does:
1. Downloads a India country boundary (Natural Earth 110m admin-0 countries,
   public domain) and saves it to data/reference/boundaries/india_boundary.geojson.
2. Fetches Indian industrial facility points from the OSM Overpass API and
   saves them to data/reference/osm/industrial_facilities.geojson.
3. Runs Alembic migrations to initialize the database, if Contributor 1's
   Alembic setup exists yet (skipped with a clear message otherwise — the
   `backend/` scaffold is empty in this environment as of 2026-08-26).

This repo already ships small hand-placed dev fixtures at those same paths
(see workers/enrichment/enrich_geography.py) so the pipeline is testable
offline without running this script. Running this script for real REPLACES
those fixtures with the genuine sourced data — pass --force to overwrite
without prompting.

Usage:
  python scripts/bootstrap.py [--force] [--skip-boundary] [--skip-osm] [--skip-db]
"""
import argparse
import json
import os
import subprocess
import sys

import httpx

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
BOUNDARIES_DIR = os.path.join(BASE_DIR, "data", "reference", "boundaries")
OSM_DIR = os.path.join(BASE_DIR, "data", "reference", "osm")

# Natural Earth 110m admin-0 countries — small enough (~800KB) to fetch reliably.
# The full-resolution "datasets/geo-countries" file (~24MB) times out on slow links;
# 110m resolution is more than sufficient for the bbox-then-boundary FIRMS clip.
NE110_URL = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/"
    "geojson/ne_110m_admin_0_countries.geojson"
)

OSM_OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_QUERY = """
[out:json][timeout:300];
area["ISO3166-1"="IN"]->.india;
(
  node["industrial"](area.india);
  way["industrial"](area.india);
  node["power"="plant"](area.india);
  way["power"="plant"](area.india);
  node["man_made"="petroleum_well"](area.india);
  node["man_made"="flare"](area.india);
);
out center;
"""


def bootstrap_india_boundary(force: bool) -> None:
    import geopandas as gpd
    from shapely.ops import unary_union

    out_path = os.path.join(BOUNDARIES_DIR, "india_boundary.geojson")
    if os.path.exists(out_path) and not force:
        print(f"[skip] {out_path} already exists (use --force to refetch)")
        return

    print(f"Downloading {NE110_URL} ...")
    resp = httpx.get(NE110_URL, timeout=60.0, follow_redirects=True)
    resp.raise_for_status()
    countries = json.loads(resp.text)

    gdf = gpd.GeoDataFrame.from_features(countries["features"])
    india = gdf[gdf.get("ADMIN") == "India"]
    if india.empty:
        # Column naming varies across Natural Earth releases — fall back to a scan.
        name_cols = [c for c in gdf.columns if "name" in c.lower() or c == "ADMIN"]
        mask = gdf[name_cols].apply(lambda r: r.astype(str).str.contains("India").any(), axis=1)
        india = gdf[mask]
    if india.empty:
        raise RuntimeError("Could not locate an India feature in the downloaded countries file")

    india = india[["geometry"]].copy()
    india["name"] = "India"
    india["iso_a2"] = "IN"
    india = india.set_crs("EPSG:4326", allow_override=True)

    os.makedirs(BOUNDARIES_DIR, exist_ok=True)
    india.to_file(out_path, driver="GeoJSON")
    print(f"[ok] wrote {out_path}")


def bootstrap_osm_industrial(force: bool) -> None:
    out_path = os.path.join(OSM_DIR, "industrial_facilities.geojson")
    if os.path.exists(out_path) and not force:
        print(f"[skip] {out_path} already exists (use --force to refetch)")
        return

    print("Querying OSM Overpass API for Indian industrial facilities ...")
    resp = httpx.post(OSM_OVERPASS_URL, data={"data": OVERPASS_QUERY}, timeout=310.0)
    resp.raise_for_status()
    elements = resp.json().get("elements", [])

    features = []
    for el in elements:
        lat = el.get("lat") or (el.get("center") or {}).get("lat")
        lon = el.get("lon") or (el.get("center") or {}).get("lon")
        if lat is None or lon is None:
            continue
        tags = el.get("tags", {})
        facility_type = (
            "Power Plant" if tags.get("power") == "plant"
            else "Refinery" if "refinery" in tags.get("industrial", "").lower()
            else tags.get("industrial") or tags.get("man_made") or "Industrial"
        )
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "name": tags.get("name") or f"OSM {el.get('type')} {el.get('id')}",
                    "facility_type": facility_type,
                },
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
            }
        )

    os.makedirs(OSM_DIR, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": features}, f, indent=2)
    print(f"[ok] wrote {out_path} ({len(features)} facilities)")


def run_migrations() -> None:
    alembic_ini = os.path.join(BASE_DIR, "backend", "alembic.ini")
    if not os.path.exists(alembic_ini):
        print(
            "[skip] backend/alembic.ini not found — Contributor 1's DB/migration "
            "layer isn't set up in this environment yet. Run `alembic upgrade head` "
            "from backend/ once it exists."
        )
        return
    subprocess.run(["alembic", "-c", alembic_ini, "upgrade", "head"], check=True)
    print("[ok] database migrated to head")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Overwrite existing reference files")
    parser.add_argument("--skip-boundary", action="store_true")
    parser.add_argument("--skip-osm", action="store_true")
    parser.add_argument("--skip-db", action="store_true")
    args = parser.parse_args()

    if not args.skip_boundary:
        bootstrap_india_boundary(args.force)
    if not args.skip_osm:
        bootstrap_osm_industrial(args.force)
    if not args.skip_db:
        run_migrations()


if __name__ == "__main__":
    sys.exit(main())
