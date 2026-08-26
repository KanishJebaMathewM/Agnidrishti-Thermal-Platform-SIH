"""
Backend Service for ISRO Bhuvan LULC AOI Integration.
Provides cached, authenticated access to official Bhuvan land-cover context.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from app.config import settings
from workers.ingestion.bhuvan_provider import BhuvanProvider

logger = logging.getLogger("agnidrishti.bhuvan_service")

# Global singleton provider instance
_bhuvan_provider: Optional[BhuvanProvider] = None


def get_bhuvan_provider() -> BhuvanProvider:
    global _bhuvan_provider
    if _bhuvan_provider is None:
        _bhuvan_provider = BhuvanProvider(token=settings.bhuvan_api_token)
    return _bhuvan_provider


def resolve_event_lulc(lat: float, lon: float, state: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve official ISRO Bhuvan LULC context for coordinates.
    
    Returns structured provenance metadata. Never falls back to fake land-use.
    """
    provider = get_bhuvan_provider()
    return provider.query_lulc_at_point(lat, lon, state=state)


def get_bhuvan_service_status() -> Dict[str, Any]:
    """Check Bhuvan service configuration and readiness status."""
    provider = get_bhuvan_provider()
    has_token = provider.has_valid_token()
    
    return {
        "name": "ISRO Bhuvan LULC",
        "source": "ISRO / NRSC Bhuvan",
        "product": "LULC AOI Wise",
        "token_configured": has_token,
        "status": "Active" if has_token else "Configuration Required",
        "description": "National Land Use / Land Cover 50K thematic layer and Area-of-Interest statistical services.",
        "coverage": "All-India Thematic Coverage (1:50,000 / 1:250,000)",
        "icon": "layers",
    }
