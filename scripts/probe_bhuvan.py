import os
import sys
import json
import urllib.request
import urllib.parse
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("BHUVAN_API_TOKEN", "")

print(f"Loaded BHUVAN_API_TOKEN: length={len(token)} (Starts with: {token[:4]}...)")

# Test standard thematic API endpoints on bhuvan-app1
endpoints = [
    # API endpoints for LULC AOI Wise
    ("https://bhuvan-app1.nrsc.gov.in/api/thematic/get_aoi_stats.php", {"token": token, "theme": "lulc", "lat": 28.6139, "lon": 77.2090}),
    ("https://bhuvan-app1.nrsc.gov.in/thematic/get_aoi_stats.php", {"token": token, "theme": "lulc", "lat": 28.6139, "lon": 77.2090}),
    ("https://bhuvan-app1.nrsc.gov.in/thematic/thematic/get_aoi_stats.php", {"token": token, "theme": "lulc", "lat": 28.6139, "lon": 77.2090}),
    ("https://bhuvan-app1.nrsc.gov.in/thematic/getAOIStatistics.php", {"token": token, "theme": "lulc", "lat": 28.6139, "lon": 77.2090}),
    ("https://bhuvan-app1.nrsc.gov.in/thematic/lulc_aoi.php", {"token": token, "lat": 28.6139, "lon": 77.2090}),
    ("https://bhuvan-app1.nrsc.gov.in/api/thematic/lulc_aoi", {"token": token, "lat": 28.6139, "lon": 77.2090}),
    # WMS FeatureInfo on official Bhuvan WMS
    ("https://bhuvan-vec2.nrsc.gov.in/bhuvan/wms?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetFeatureInfo&LAYERS=lulc:IN_LULC250k_1819&QUERY_LAYERS=lulc:IN_LULC250k_1819&BBOX=77.0,28.0,78.0,29.0&WIDTH=100&HEIGHT=100&X=50&Y=50&INFO_FORMAT=application/json", None),
]

for url, params in endpoints:
    full_url = url
    if params:
        full_url = f"{url}?{urllib.parse.urlencode(params)}"
    
    print(f"\nProbing: {url}")
    try:
        req = urllib.request.Request(
            full_url,
            headers={
                "User-Agent": "AGNIDRISHTI/1.0 (ISRO Bhuvan Client)",
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            }
        )
        with urllib.request.urlopen(req, timeout=5) as res:
            body = res.read().decode("utf-8", errors="ignore")
            print(f"  -> Status {res.status}, Size {len(body)} B: {body[:300]}")
    except urllib.error.HTTPError as e:
        print(f"  -> HTTPError {e.code}: {e.reason}")
    except Exception as e:
        print(f"  -> {type(e).__name__}: {e}")
