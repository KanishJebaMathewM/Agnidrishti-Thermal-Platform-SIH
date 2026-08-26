"""
NASA FIRMS active-fire CSV API client.

API docs: https://firms.modaps.eosdis.nasa.gov/api/area/
Requires a free MAP_KEY. Area format is a bounding box: west,south,east,north.
"""
import time
from datetime import date, timedelta
from io import StringIO

import httpx
import pandas as pd

FIRMS_BASE_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"
INDIA_BBOX = "65.0,6.0,98.0,38.0"

# VIIRS SNPP NRT (Near Real-Time) product
PRODUCT_NRT = "VIIRS_SNPP_NRT"
# VIIRS SNPP Standard product (archived)
PRODUCT_STANDARD = "VIIRS_SNPP_SP"


class FIRMSClient:
    def __init__(self, map_key: str, client: httpx.Client | None = None):
        self.map_key = map_key
        # Accepting an injected httpx.Client lets tests substitute a MockTransport
        # instead of hitting the real FIRMS API.
        self.client = client or httpx.Client(timeout=60.0)

    def fetch_nrt(self, days: int = 1) -> pd.DataFrame:
        """Fetch NRT data for last N days over India bounding box (days: 1-10)."""
        url = f"{FIRMS_BASE_URL}/{self.map_key}/{PRODUCT_NRT}/{INDIA_BBOX}/{days}"
        return self._fetch_csv(url)

    def fetch_archive_chunk(self, start_date: date, end_date: date) -> pd.DataFrame:
        """Fetch one archive chunk (must be <=5 days) in a single request."""
        days = min((end_date - start_date).days + 1, 5)
        url_std = f"{FIRMS_BASE_URL}/{self.map_key}/{PRODUCT_STANDARD}/{INDIA_BBOX}/{days}/{start_date.isoformat()}"
        df = self._fetch_csv(url_std)
        # Fall back to NRT date endpoint if standard archive is empty
        if df.empty:
            url_nrt = f"{FIRMS_BASE_URL}/{self.map_key}/{PRODUCT_NRT}/{INDIA_BBOX}/{days}/{start_date.isoformat()}"
            df = self._fetch_csv(url_nrt)
        # Fall back to NRT relative days window if still empty
        if df.empty and (date.today() - end_date).days <= 10:
            df = self.fetch_nrt(days=min(days, 5))
        return df

    def fetch_archive(self, start_date: date, end_date: date) -> pd.DataFrame:
        """Fetch archived data for a date range, chunked into <=10-day windows."""
        frames = []
        current = start_date
        while current <= end_date:
            chunk_end = min(current + timedelta(days=9), end_date)
            try:
                frames.append(self.fetch_archive_chunk(current, chunk_end))
            except Exception as e:
                print(f"Warning: failed chunk {current} - {chunk_end}: {e}")
            current = chunk_end + timedelta(days=1)
            if current <= end_date:
                time.sleep(1)  # rate limiting between chunks
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    def _fetch_csv(self, url: str) -> pd.DataFrame:
        resp = self.client.get(url)
        resp.raise_for_status()
        return pd.read_csv(StringIO(resp.text))
