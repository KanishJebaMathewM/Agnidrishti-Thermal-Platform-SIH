"""
Dedicated Jurisdiction Spatial Join Unit Test Suite (Item 4 of Next Phase Directives).

Verifies point-in-polygon spatial joins across multi-state geographic coordinates in India:
- Delhi (UT) / New Delhi
- Gujarat / Jamnagar
- Punjab / Ludhiana
- Odisha / Khordha
- Karnataka / Bengaluru Urban
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
from workers.enrichment.enrich_geography import enrich_geography_context


@pytest.mark.parametrize(
    "lat, lon, expected_state, expected_district",
    [
        (28.6139, 77.2090, "Delhi", "New Delhi"),
        (22.4707, 70.0577, "Gujarat", "Jamnagar"),
        (30.9010, 75.8573, "Punjab", "Ludhiana"),
        (20.1825, 85.6174, "Odisha", "Khordha"),
        (12.9716, 77.5946, "Karnataka", "Bengaluru Urban"),
    ],
)
def test_jurisdiction_multi_state_spatial_join(lat, lon, expected_state, expected_district):
    res = enrich_geography_context(lat, lon)
    assert res.get("state") == expected_state, f"Expected state {expected_state} for ({lat}, {lon}), got {res.get('state')}"
