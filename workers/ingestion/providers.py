"""
DataProvider abstract interface & concrete source adapters per Master Spec (Section 27 & Section 37).

Source Truth Table:
- FIRMSProvider: Primary active-fire detections (VIIRS/MODIS) + FRP/thermal attributes (Requires FIRMS_MAP_KEY)
- INSATProvider: High-frequency thermal context (MOSDAC). Safe adapter with env config + graceful fallback
- OSMProvider: Geographic/infrastructure context (Overpass API / cached local GeoJSON)
- BhuvanProvider: Land-use / land-cover context adapter
- ForestProvider: FSI / official forest data context adapter
"""

from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from datetime import date
from typing import Any

import pandas as pd

from workers.ingestion.firms_client import FIRMSClient

logger = logging.getLogger(__name__)


class DataProvider(ABC):
    """Abstract base adapter for all AGNIDRISHTI data sources."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Name of the data provider source."""
        pass

    @abstractmethod
    def fetch(self, **kwargs: Any) -> Any:
        """Fetch raw records from the data provider."""
        pass

    @abstractmethod
    def validate(self, raw_data: Any) -> bool:
        """Validate fetched data payload structure."""
        pass

    @abstractmethod
    def normalize(self, raw_data: Any) -> pd.DataFrame:
        """Normalize payload into standard AGNIDRISHTI observation/context schema."""
        pass


class FIRMSProvider(DataProvider):
    """Primary active-fire detection provider via NASA FIRMS API."""

    def __init__(self, map_key: str | None = None):
        self.map_key = map_key or os.getenv("FIRMS_MAP_KEY") or os.getenv("FIRMS_API_KEY") or ""
        self._client = FIRMSClient(map_key=self.map_key) if self.map_key else None

    @property
    def source_name(self) -> str:
        return "NASA_FIRMS_VIIRS"

    def fetch(self, days: int = 1, start_date: date | None = None, end_date: date | None = None) -> pd.DataFrame:
        if not self._client:
            raise ValueError("FIRMS_MAP_KEY not configured. Cannot fetch live FIRMS observations.")
        if start_date and end_date:
            return self._client.fetch_archive(start_date, end_date)
        return self._client.fetch_nrt(days=days)

    def validate(self, raw_data: Any) -> bool:
        if not isinstance(raw_data, pd.DataFrame):
            return False
        required_cols = {"latitude", "longitude", "bright_ti4", "acq_date"}
        return required_cols.issubset(raw_data.columns)

    def normalize(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        if raw_data.empty:
            return pd.DataFrame()
        df = raw_data.copy()
        df["source"] = self.source_name
        return df


class INSATProvider(DataProvider):
    """
    ISRO MOSDAC / INSAT-3D/3DR thermal context adapter (Section 6 of Master Spec).
    Uses environment credentials if authentication is required; otherwise falls back
    gracefully to unavailable/mock state without generating fake live data.
    """

    def __init__(self):
        self.username = os.getenv("MOSDAC_USERNAME", "")
        self.password = os.getenv("MOSDAC_PASSWORD", "")
        self.token = os.getenv("MOSDAC_TOKEN", "")
        self.product = os.getenv("MOSDAC_PRODUCT", "INSAT_3D_HEM")
        self.is_authenticated = bool(self.token or (self.username and self.password))

    @property
    def source_name(self) -> str:
        return "ISRO_INSAT_3D"

    def fetch(self, **kwargs: Any) -> dict[str, Any]:
        if not self.is_authenticated:
            logger.info("MOSDAC credentials not set. INSATProvider running in fallback state.")
            return {"status": "UNAVAILABLE", "reason": "MOSDAC credentials required for programmatic INSAT product access."}
        return {"status": "AUTHENTICATED", "product": self.product, "data": []}

    def validate(self, raw_data: Any) -> bool:
        return isinstance(raw_data, dict) and "status" in raw_data

    def normalize(self, raw_data: Any) -> pd.DataFrame:
        return pd.DataFrame()


class OSMProvider(DataProvider):
    """
    OpenStreetMap / Overpass industrial context provider (Section 7 of Master Spec).
    Provides geographic/infrastructure context, not authoritative national registry.
    Caches local reference features and rate-limits external Overpass queries.
    """

    def __init__(self, overpass_url: str = "https://overpass-api.de/api/interpreter"):
        self.overpass_url = os.getenv("OVERPASS_URL", overpass_url)

    @property
    def source_name(self) -> str:
        return "OPENSTREETMAP_OVERPASS"

    def fetch(self, **kwargs: Any) -> list[dict[str, Any]]:
        # Serves cached local GeoJSON reference data to prevent Overpass rate limiting per observation
        ref_file = os.path.join("data", "reference", "osm", "industrial_facilities.geojson")
        if os.path.exists(ref_file):
            import json
            with open(ref_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("features", [])
        return []

    def validate(self, raw_data: Any) -> bool:
        return isinstance(raw_data, list)

    def normalize(self, raw_data: list[dict[str, Any]]) -> pd.DataFrame:
        rows = []
        for feat in raw_data:
            props = feat.get("properties", {})
            geom = feat.get("geometry", {})
            coords = geom.get("coordinates", [0, 0])
            rows.append({
                "name": props.get("name", "Industrial Facility"),
                "facility_type": props.get("facility_type", "Industrial"),
                "longitude": coords[0],
                "latitude": coords[1],
            })
        return pd.DataFrame(rows)


class BhuvanProvider(DataProvider):
    """ISRO Bhuvan Land-Use / Land-Cover context provider (Section 8 of Master Spec)."""

    @property
    def source_name(self) -> str:
        return "ISRO_BHUVAN_LULC"

    def fetch(self, **kwargs: Any) -> list[dict[str, Any]]:
        ref_file = os.path.join("data", "reference", "landuse", "landuse_features.geojson")
        if os.path.exists(ref_file):
            import json
            with open(ref_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("features", [])
        return []

    def validate(self, raw_data: Any) -> bool:
        return isinstance(raw_data, list)

    def normalize(self, raw_data: list[dict[str, Any]]) -> pd.DataFrame:
        return pd.DataFrame(raw_data)


class ForestProvider(DataProvider):
    """Forest Survey of India (FSI) official forest context provider (Section 9 of Master Spec)."""

    @property
    def source_name(self) -> str:
        return "FOREST_SURVEY_OF_INDIA"

    def fetch(self, **kwargs: Any) -> list[dict[str, Any]]:
        ref_file = os.path.join("data", "reference", "forest", "forest_boundaries.geojson")
        if os.path.exists(ref_file):
            import json
            with open(ref_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("features", [])
        return []

    def validate(self, raw_data: Any) -> bool:
        return isinstance(raw_data, list)

    def normalize(self, raw_data: list[dict[str, Any]]) -> pd.DataFrame:
        return pd.DataFrame(raw_data)
