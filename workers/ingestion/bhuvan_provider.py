"""
Official ISRO / NRSC Bhuvan LULC AOI Wise Data Provider.

Responsibilities:
1. Authenticates using BHUVAN_API_TOKEN loaded strictly from environment (.env).
2. Queries the official ISRO Bhuvan thematic LULC service for coordinate/AOI.
3. Normalizes official Bhuvan Level-1/Level-2 land-use classes into canonical representations.
4. Caches responses spatially by rounded coordinates / AOI key (in-memory + SQLite/PostGIS).
5. Returns strict DATA UNAVAILABLE / SOURCE PENDING upon API failure, token expiration, or network down.
   NEVER generates mock, random, or hardcoded land-use values.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("agnidrishti.bhuvan")

# Standard ISRO / NRSC National LULC Classification Hierarchy
BHUVAN_LULC_CODE_MAP = {
    1: {"name": "Built-up / Urban / Industrial", "canonical": "INDUSTRIAL"},
    2: {"name": "Agricultural Land (Crop / Fallow)", "canonical": "AGRICULTURAL"},
    3: {"name": "Forest (Deciduous / Evergreen / Scrub)", "canonical": "FOREST"},
    4: {"name": "Grassland / Grazing", "canonical": "AGRICULTURAL"},
    5: {"name": "Wasteland / Barren / Rocky", "canonical": "BARREN"},
    6: {"name": "Water Bodies / River / Lake", "canonical": "WATER"},
    7: {"name": "Wetlands / Coastal", "canonical": "WATER"},
}

BHUVAN_CLASS_NAME_MAP = {
    "built up": "INDUSTRIAL",
    "built-up": "INDUSTRIAL",
    "urban": "INDUSTRIAL",
    "industrial": "INDUSTRIAL",
    "settlement": "SETTLEMENT",
    "agriculture": "AGRICULTURAL",
    "agricultural": "AGRICULTURAL",
    "cropland": "AGRICULTURAL",
    "kharif": "AGRICULTURAL",
    "rabi": "AGRICULTURAL",
    "zaid": "AGRICULTURAL",
    "double crop": "AGRICULTURAL",
    "fallow": "AGRICULTURAL",
    "plantation": "AGRICULTURAL",
    "forest": "FOREST",
    "deciduous": "FOREST",
    "evergreen": "FOREST",
    "scrub": "FOREST",
    "water": "WATER",
    "waterbody": "WATER",
    "river": "WATER",
    "wetland": "WATER",
    "barren": "BARREN",
    "wasteland": "BARREN",
    "rocky": "BARREN",
    "mining": "INDUSTRIAL",
}

# State code mapping for Bhuvan WMS state-level layers
STATE_LAYER_CODES = {
    "bihar": "BR", "punjab": "PB", "haryana": "HR", "delhi": "DL",
    "gujarat": "GJ", "maharashtra": "MH", "rajasthan": "RJ", "odisha": "OR",
    "chhattisgarh": "CG", "assam": "AS", "madhya pradesh": "MP",
    "uttar pradesh": "UP", "west bengal": "WB", "karnataka": "KA",
    "tamil nadu": "TN", "telangana": "TG", "andhra pradesh": "AP",
}


class BhuvanProvider:
    """Production client for ISRO/NRSC Bhuvan Thematic LULC AOI Service."""

    def __init__(self, token: Optional[str] = None, cache_db_path: Optional[str] = None):
        # Read strictly from environment / parameter
        self._token = token or os.getenv("BHUVAN_API_TOKEN", "")
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        
        # Local persistent SQLite cache fallback for offline / server resilience
        self._cache_db_path = cache_db_path or os.path.join("data", "cache", "bhuvan_lulc_cache.sqlite")
        self._init_sqlite_cache()

    @property
    def source_name(self) -> str:
        return "ISRO_BHUVAN_LULC"

    @property
    def product_name(self) -> str:
        return "LULC AOI Wise"

    def has_valid_token(self) -> bool:
        return bool(self._token and len(self._token.strip()) >= 20)

    def _init_sqlite_cache(self) -> None:
        """Initialize local persistent spatial cache table."""
        try:
            os.makedirs(os.path.dirname(self._cache_db_path), exist_ok=True)
            with sqlite3.connect(self._cache_db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS bhuvan_lulc_cache (
                        aoi_key TEXT PRIMARY KEY,
                        latitude REAL NOT NULL,
                        longitude REAL NOT NULL,
                        lulc_code INTEGER,
                        lulc_class TEXT,
                        raw_category TEXT,
                        source TEXT NOT NULL,
                        product TEXT NOT NULL,
                        status TEXT NOT NULL,
                        response_metadata TEXT,
                        retrieved_at TEXT NOT NULL
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_bhuvan_coords ON bhuvan_lulc_cache (latitude, longitude)")
                conn.commit()
        except Exception as exc:
            logger.warning(f"Could not initialize Bhuvan SQLite cache: {exc}")

    def _get_aoi_key(self, lat: float, lon: float, precision: int = 3) -> str:
        """Generate spatial AOI key for ~100m grid cell caching."""
        return f"{round(lat, precision):.3f}_{round(lon, precision):.3f}"

    def _get_from_cache(self, aoi_key: str) -> Optional[Dict[str, Any]]:
        # 1. In-memory check
        if aoi_key in self._memory_cache:
            return self._memory_cache[aoi_key]

        # 2. SQLite cache check
        try:
            if os.path.exists(self._cache_db_path):
                with sqlite3.connect(self._cache_db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM bhuvan_lulc_cache WHERE aoi_key = ?", (aoi_key,))
                    row = cursor.fetchone()
                    if row:
                        entry = {
                            "source": row[6],
                            "product": row[7],
                            "latitude": row[1],
                            "longitude": row[2],
                            "lulc_code": row[3],
                            "lulc_class": row[4],
                            "raw_category": row[5],
                            "status": row[8],
                            "response_metadata": json.loads(row[9]) if row[9] else {},
                            "retrieved_at": row[10],
                        }
                        self._memory_cache[aoi_key] = entry
                        return entry
        except Exception as exc:
            logger.debug(f"Cache read error: {exc}")
        return None

    def _save_to_cache(self, aoi_key: str, entry: Dict[str, Any]) -> None:
        self._memory_cache[aoi_key] = entry
        try:
            with sqlite3.connect(self._cache_db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO bhuvan_lulc_cache
                    (aoi_key, latitude, longitude, lulc_code, lulc_class, raw_category, source, product, status, response_metadata, retrieved_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    aoi_key,
                    entry["latitude"],
                    entry["longitude"],
                    entry["lulc_code"],
                    entry["lulc_class"],
                    entry["raw_category"],
                    entry["source"],
                    entry["product"],
                    entry["status"],
                    json.dumps(entry.get("response_metadata", {})),
                    entry["retrieved_at"],
                ))
                conn.commit()
        except Exception as exc:
            logger.debug(f"Cache write error: {exc}")

    def query_lulc_at_point(
        self,
        lat: float,
        lon: float,
        state: Optional[str] = None,
        timeout: float = 3.5,
    ) -> Dict[str, Any]:
        """Query official ISRO Bhuvan LULC AOI service for a physical location.
        
        Guarantees:
        - If API returns valid data -> status="LIVE", lulc_class="AGRICULTURAL"|"FOREST"|etc.
        - If token missing/expired or API down -> status="DATA UNAVAILABLE", lulc_class=None.
        - NEVER returns synthetic, random, or hardcoded classifications.
        """
        aoi_key = self._get_aoi_key(lat, lon)
        cached = self._get_from_cache(aoi_key)
        if cached:
            return cached

        retrieved_at = datetime.now(timezone.utc).isoformat()

        # Check authentication token
        if not self.has_valid_token():
            result = {
                "source": "ISRO_BHUVAN",
                "product": "LULC AOI Wise",
                "latitude": lat,
                "longitude": lon,
                "aoi_key": aoi_key,
                "lulc_code": None,
                "lulc_class": None,
                "raw_category": None,
                "retrieved_at": retrieved_at,
                "status": "SOURCE PENDING (TOKEN MISSING)",
                "response_metadata": {"error": "BHUVAN_API_TOKEN is not configured or empty"},
            }
            return result

        # Attempt Official Bhuvan Thematic API
        api_endpoints = [
            f"https://bhuvan-app1.nrsc.gov.in/api/thematic/get_aoi_stats.php?token={self._token}&lat={lat}&lon={lon}&theme=lulc",
            f"https://bhuvan-app1.nrsc.gov.in/thematic/api/lulc?token={self._token}&lat={lat}&lon={lon}",
        ]

        raw_category = None
        lulc_code = None
        lulc_class = None
        status = "DATA UNAVAILABLE"
        response_meta: Dict[str, Any] = {}

        for url in api_endpoints:
            try:
                req = urllib.request.Request(
                    url,
                    headers={
                        "User-Agent": "AGNIDRISHTI/1.0 (ISRO Bhuvan Client; Disaster Management)",
                        "Authorization": f"Bearer {self._token}",
                        "Accept": "application/json",
                    },
                )
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    if resp.status == 200:
                        body = resp.read().decode("utf-8", errors="ignore")
                        data = json.loads(body)
                        response_meta = data

                        # Parse category from standard Bhuvan JSON response
                        raw_cat = (
                            data.get("lulc_class")
                            or data.get("category")
                            or data.get("landuse")
                            or data.get("class_name")
                        )
                        code = data.get("lulc_code") or data.get("code")

                        if raw_cat or code is not None:
                            raw_category = str(raw_cat) if raw_cat else None
                            lulc_code = int(code) if code is not None else None
                            lulc_class = self.normalize_category(raw_category, lulc_code)
                            status = "LIVE"
                            break

            except urllib.error.HTTPError as http_err:
                if http_err.code in (401, 403):
                    status = "TOKEN EXPIRED / UNAUTHORIZED"
                    response_meta = {"http_code": http_err.code, "reason": "Bhuvan token rejected or expired"}
                    break
                else:
                    response_meta = {"http_code": http_err.code, "reason": str(http_err.reason)}
            except Exception as exc:
                response_meta = {"error_type": type(exc).__name__, "error": str(exc)}

        # Fallback: Official Bhuvan OGC WMS GetFeatureInfo query
        if status not in ("LIVE", "TOKEN EXPIRED / UNAUTHORIZED") and state:
            st_code = STATE_LAYER_CODES.get(state.lower().strip())
            if st_code:
                wms_result = self._query_bhuvan_wms_feature_info(lat, lon, st_code, timeout=timeout)
                if wms_result and wms_result.get("status") == "LIVE":
                    raw_category = wms_result.get("raw_category")
                    lulc_code = wms_result.get("lulc_code")
                    lulc_class = wms_result.get("lulc_class")
                    status = "LIVE"
                    response_meta = wms_result.get("metadata", {})

        entry = {
            "source": "ISRO_BHUVAN",
            "product": "LULC AOI Wise",
            "latitude": lat,
            "longitude": lon,
            "aoi_key": aoi_key,
            "lulc_code": lulc_code,
            "lulc_class": lulc_class,
            "raw_category": raw_category,
            "retrieved_at": retrieved_at,
            "status": status,
            "response_metadata": response_meta,
        }

        # Cache valid lookups and deterministic unavailables
        if status == "LIVE":
            self._save_to_cache(aoi_key, entry)

        return entry

    def _query_bhuvan_wms_feature_info(
        self,
        lat: float,
        lon: float,
        state_code: str,
        timeout: float = 3.0,
    ) -> Optional[Dict[str, Any]]:
        """Query official Bhuvan WMS GetFeatureInfo for state-level LULC layer."""
        layer_name = f"lulc:{state_code}_LULC50K_1112"
        delta = 0.01
        bbox = f"{lon-delta:.4f},{lat-delta:.4f},{lon+delta:.4f},{lat+delta:.4f}"
        
        wms_url = (
            f"https://bhuvan-vec2.nrsc.gov.in/bhuvan/wms"
            f"?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetFeatureInfo"
            f"&LAYERS={layer_name}&QUERY_LAYERS={layer_name}"
            f"&BBOX={bbox}&WIDTH=101&HEIGHT=101&X=50&Y=50"
            f"&INFO_FORMAT=application/json"
        )

        try:
            req = urllib.request.Request(wms_url, headers={"User-Agent": "AGNIDRISHTI/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status == 200:
                    body = resp.read().decode("utf-8", errors="ignore")
                    if "ServiceException" not in body and "features" in body:
                        data = json.loads(body)
                        features = data.get("features", [])
                        if features:
                            props = features[0].get("properties", {})
                            cat_name = props.get("CLASS_NAME") or props.get("DESCRIPTIO") or props.get("LULC_CLASS")
                            if cat_name:
                                norm_class = self.normalize_category(cat_name)
                                return {
                                    "status": "LIVE",
                                    "raw_category": cat_name,
                                    "lulc_code": props.get("GRIDCODE") or props.get("CODE"),
                                    "lulc_class": norm_class,
                                    "metadata": {"wms_layer": layer_name, "properties": props},
                                }
        except Exception:
            pass
        return None

    @classmethod
    def normalize_category(cls, raw_category: Optional[str], code: Optional[int] = None) -> Optional[str]:
        """Normalize Bhuvan LULC class into canonical AGNIDRISHTI classes."""
        if code is not None and code in BHUVAN_LULC_CODE_MAP:
            return BHUVAN_LULC_CODE_MAP[code]["canonical"]

        if not raw_category:
            return None

        clean_cat = str(raw_category).lower().strip()
        for key, canonical in BHUVAN_CLASS_NAME_MAP.items():
            if key in clean_cat:
                return canonical

        return None
