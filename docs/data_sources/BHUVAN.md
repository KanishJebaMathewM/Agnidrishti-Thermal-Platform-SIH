# ISRO Bhuvan Land Use / Land Cover (LULC) Integration

## 1. Overview & Provenance

* **Official Source**: National Remote Sensing Centre (NRSC) / Indian Space Research Organisation (ISRO)
* **Thematic Product**: LULC AOI Wise (1:50,000 & 1:250,000 scale)
* **Geoportal URL**: `https://bhuvan-app1.nrsc.gov.in/thematic/`
* **OGC WMS Service**: `https://bhuvan-vec2.nrsc.gov.in/bhuvan/wms`
* **Role in AGNIDRISHTI**: Contextual geospatial enrichment for physical thermal anomaly events detected from NASA FIRMS VIIRS/MODIS. Enriches thermal observations with authoritative land-use/land-cover classification to assist XGBoost anomaly classification and industrial routing.

---

## 2. Authentication & Token Management

* **Environment Variable**: `BHUVAN_API_TOKEN` (configured strictly in `.env`).
* **Security Policy**: The token is **NEVER** hardcoded in source code or committed to version control.
* **Token Lifetime**: Bhuvan API tokens typically expire within **24 hours (1 day)**.
* **Token Renewal Runbook**:
  1. Log in to the [ISRO Bhuvan API Portal](https://bhuvan-app1.nrsc.gov.in/).
  2. Navigate to **Developer Dashboard → Thematic Services → LULC AOI Wise**.
  3. Generate or copy the active Access Token.
  4. Update `BHUVAN_API_TOKEN=<new_token>` in `.env`.
  5. Restart the backend service (`uvicorn backend.app.main:app`).

---

## 3. Official Request Format

### A. Thematic REST AOI Endpoint
* **Base URL**: `https://bhuvan-app1.nrsc.gov.in/api/thematic/get_aoi_stats.php`
* **HTTP Method**: `GET`
* **Headers**:
  * `Authorization: Bearer <BHUVAN_API_TOKEN>`
  * `User-Agent: AGNIDRISHTI/1.0 (ISRO Bhuvan Client)`
  * `Accept: application/json`
* **Query Parameters**:
  * `token`: Active Bhuvan access token
  * `lat`: Decimal latitude (e.g. `28.6139`)
  * `lon`: Decimal longitude (e.g. `77.2090`)
  * `theme`: `lulc`

### B. OGC WMS GetFeatureInfo Fallback
* **Base URL**: `https://bhuvan-vec2.nrsc.gov.in/bhuvan/wms`
* **Query Parameters**:
  * `SERVICE=WMS&VERSION=1.1.1&REQUEST=GetFeatureInfo`
  * `LAYERS=lulc:<STATE_CODE>_LULC50K_1112`
  * `QUERY_LAYERS=lulc:<STATE_CODE>_LULC50K_1112`
  * `BBOX=<min_lon>,<min_lat>,<max_lon>,<max_lat>`
  * `WIDTH=101&HEIGHT=101&X=50&Y=50`
  * `INFO_FORMAT=application/json`

---

## 4. Response Schema & Normalized LULC Classes

### Provider Response Structure
```json
{
  "source": "ISRO_BHUVAN",
  "product": "LULC AOI Wise",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "aoi_key": "28.614_77.209",
  "lulc_code": 2,
  "lulc_class": "AGRICULTURAL",
  "raw_category": "Agricultural Land (Crop / Fallow)",
  "retrieved_at": "2026-08-26T17:00:00Z",
  "status": "LIVE",
  "response_metadata": { ... }
}
```

### Classification Code Mapping

| ISRO Level-1 Code | Bhuvan Category Name | AGNIDRISHTI Canonical Class | ML Feature Encoding |
|:---:|:---|:---|:---:|
| `1` | Built-up / Urban / Industrial / Mining | `INDUSTRIAL` | `0` |
| `2` | Agricultural Land (Kharif / Rabi / Zaid / Fallow) | `AGRICULTURAL` | `1` |
| `3` | Forest (Deciduous / Evergreen / Scrub) | `FOREST` | `2` |
| `4` | Grassland / Grazing Land | `AGRICULTURAL` | `1` |
| `5` | Wasteland / Barren / Rocky | `BARREN` | `5` |
| `6` | Water Bodies (River / Lake / Reservoir) | `WATER` | `4` |
| `7` | Wetlands / Mangroves / Coastal | `WATER` | `4` |
| `None` | Unknown / Unresolved / API Offline | `None` (`NULL`) | `None` (`NULL`) |

---

## 5. Spatial Caching Architecture

To prevent redundant API requests and adhere to NRSC rate limits:
1. **Spatial AOI Key**: Quantized to 3 decimal places (~100m ground resolution grid): `f"{round(lat, 3):.3f}_{round(lon, 3):.3f}"`.
2. **In-Memory Cache**: Fast in-process hash map for instant lookups during real-time event classification.
3. **Persistent SQLite/PostGIS Storage**: `bhuvan_lulc_cache` table stores verified land-use context permanently with query timestamp and raw provenance metadata.

---

## 6. Strict Real-Data & Failure Policy

* **Zero Synthetic Fallbacks**: If the Bhuvan API is unreachable, if the token is expired, or if a location is outside thematic coverage:
  * Status returns `DATA UNAVAILABLE` or `SOURCE PENDING (TOKEN MISSING)`.
  * `lulc_class` returns `None` (`NULL`).
  * `_encode_land_use(None)` returns `None` (`NULL`).
* **No Hardcoded Categories**: The system **NEVER** defaults an unresolved fire to `"Agricultural"` or `"Forest"`. An unknown land-use is explicitly treated as missing context.
