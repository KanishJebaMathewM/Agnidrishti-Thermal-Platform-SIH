"""
Comprehensive Automated Acceptance Test for Frontend Canonical Data Migration.
Verifies all 7 frontend screens against live FastAPI / canonical data sources.
"""

import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

API_BASE = "http://127.0.0.1:8000"

def fetch_json(endpoint: str):
    url = f"{API_BASE}{endpoint}"
    req = urllib.request.Request(url, headers={"User-Agent": "AGNIDRISHTI-Acceptance-Test/1.0"})
    with urllib.request.urlopen(req, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))

def run_acceptance_audit():
    print("=" * 85)
    print("AGNIDRISHTI — FRONTEND CANONICAL DATA MIGRATION AUDIT & ACCEPTANCE")
    print("=" * 85)

    results = {}

    # 1. MAP DATA AUDIT
    print("\n[1] Auditing Map Data & Coordinates (/dashboard/map)...")
    try:
        map_res = fetch_json("/dashboard/map?limit=100")
        events = map_res.get("events", [])
        total = map_res.get("total_available", 0)
        print(f"  • Retrieved {len(events)} visible map events (Total Available: {total})")
        assert len(events) > 0, "Map must return active events"
        
        # Verify coordinates of first 5 events are inside India
        for e in events[:5]:
            lat = float(e["lat"])
            lon = float(e["lon"])
            assert 6.0 <= lat <= 38.0, f"Latitude outside India: {lat}"
            assert 68.0 <= lon <= 98.0, f"Longitude outside India: {lon}"
            assert e["classification"] in [
                "Industrial Incident", "Persistent Flare/Kiln", "Agricultural Burn", "Forest Fire", "Unknown"
            ], f"Invalid classification: {e['classification']}"
        print("  • Sample Coordinates: Verified inside Indian Subcontinent [6°-38°N, 68°-98°E]")
        print("  --> MAP DATA: [PASS]")
        results["MAP DATA"] = "PASS"
    except Exception as exc:
        print(f"  --> MAP DATA: [FAIL] ({exc})")
        results["MAP DATA"] = f"FAIL ({exc})"

    # 2. REGISTRY DATA AUDIT
    print("\n[2] Auditing Source Registry Data (/sources)...")
    try:
        sources_res = fetch_json("/sources?limit=50")
        sources = sources_res.get("items", [])
        total_sources = sources_res.get("total", 0)
        print(f"  • Retrieved {len(sources)} registered sources (Total Catalog: {total_sources})")
        assert len(sources) >= 5, "Registry must contain canonical industrial facilities"
        
        # Verify real facility names
        facility_names = [s["name"] for s in sources]
        print(f"  • Sample Facilities: {facility_names[:3]}")
        assert any("Jamnagar" in n for n in facility_names), "Jamnagar must be in registry"
        assert any("Korba" in n for n in facility_names), "Korba must be in registry"
        assert any("Rourkela" in n for n in facility_names), "Rourkela must be in registry"
        print("  --> REGISTRY DATA: [PASS]")
        results["REGISTRY DATA"] = "PASS"
    except Exception as exc:
        print(f"  --> REGISTRY DATA: [FAIL] ({exc})")
        results["REGISTRY DATA"] = f"FAIL ({exc})"

    # 3. TRENDS DATA AUDIT
    print("\n[3] Auditing Trends & Time Series Data (/dashboard/trends)...")
    try:
        trends_res = fetch_json("/dashboard/trends")
        summary = trends_res.get("summary", {})
        yearly = trends_res.get("yearly", [])
        monthly = trends_res.get("monthly_2026", [])
        
        total_events = summary.get("total_events", 0)
        total_obs = summary.get("total_observations", 0)
        print(f"  • Canonical Events in Summary: {total_events:,}")
        print(f"  • Canonical Observations:     {total_obs:,}")
        assert total_events == 65840, f"Expected 65,840 events, got {total_events}"
        assert total_obs == 10033963, f"Expected 10,033,963 obs, got {total_obs}"
        assert len(yearly) == 7, "Yearly breakdown must cover 2020-2026"
        assert len(monthly) >= 8, "Monthly 2026 series must be populated"
        print("  --> TRENDS DATA: [PASS]")
        results["TRENDS DATA"] = "PASS"
    except Exception as exc:
        print(f"  --> TRENDS DATA: [FAIL] ({exc})")
        results["TRENDS DATA"] = f"FAIL ({exc})"

    # 4. MODEL METADATA AUDIT
    print("\n[4] Auditing Active Production Model (/model/current)...")
    try:
        model_res = fetch_json("/model/current")
        version = model_res.get("version_tag")
        status = model_res.get("status")
        metrics = model_res.get("metrics", {})
        acc = metrics.get("accuracy", 0)
        f1 = metrics.get("macro_f1", 0)
        
        print(f"  • Active Model Version: {version}")
        print(f"  • Model Status:         {status}")
        print(f"  • Benchmark Accuracy:   {acc*100:.2f}%")
        print(f"  • Benchmark Macro F1:   {f1*100:.2f}%")
        
        assert version == "xgb_v4_0", f"Expected xgb_v4_0, got {version}"
        assert acc >= 0.92, f"Expected >= 92% accuracy, got {acc}"
        assert f1 >= 0.90, f"Expected >= 90% macro F1, got {f1}"
        assert len(model_res.get("feature_importance", [])) >= 5, "Feature importance must be populated"
        print("  --> MODEL DATA: [PASS]")
        results["MODEL DATA"] = "PASS"
    except Exception as exc:
        print(f"  --> MODEL DATA: [FAIL] ({exc})")
        results["MODEL DATA"] = f"FAIL ({exc})"

    # 5. EVENT DETAIL & PAGINATION AUDIT
    print("\n[5] Auditing Events Table & Event Details (/events)...")
    try:
        events_res = fetch_json("/events?limit=50&page=1")
        items = events_res.get("items", [])
        total_events_page = events_res.get("total", 0)
        print(f"  • Events on Page 1:     {len(items)} (Total: {total_events_page:,})")
        assert len(items) == 50, "Page limit 50 must return 50 items"
        assert total_events_page == 65840, f"Expected 65,840 events, got {total_events_page}"
        
        # Test specific verified real event: evt-nasa-2026-065839
        sample_evt = fetch_json("/events/evt-nasa-2026-065839")
        print(f"  • Verified Event ID:    {sample_evt.get('id')}")
        print(f"  • Location:             {sample_evt.get('placeName')} ({sample_evt.get('lat')}, {sample_evt.get('lon')})")
        assert sample_evt.get("lat") == 30.9010, "Ludhiana lat mismatch"
        assert sample_evt.get("lon") == 75.8573, "Ludhiana lon mismatch"
        print("  --> EVENT DATA: [PASS]")
        results["EVENT DATA"] = "PASS"
    except Exception as exc:
        print(f"  --> EVENT DATA: [FAIL] ({exc})")
        results["EVENT DATA"] = f"FAIL ({exc})"

    # 6. LIVE MODE INTEGRITY AUDIT
    print("\n[6] Auditing Live Operational Health (/health & /system/diagnostics)...")
    try:
        health = fetch_json("/health")
        diag = fetch_json("/system/diagnostics")
        print(f"  • Health Status:        {health.get('status')}")
        print(f"  • Active Model Tag:     {diag.get('active_model')}")
        print(f"  • Canonical Obs Count:  {diag.get('total_observations'):,}")
        print(f"  • Canonical Event Count:{diag.get('total_events'):,}")
        assert health.get("status") == "healthy"
        assert diag.get("total_observations") == 10033963
        assert diag.get("total_events") == 65840
        print("  --> LIVE MODE: [PASS]")
        results["LIVE MODE"] = "PASS"
    except Exception as exc:
        print(f"  --> LIVE MODE: [FAIL] ({exc})")
        results["LIVE MODE"] = f"FAIL ({exc})"

    # Summary
    print("\n" + "=" * 85)
    print("FRONTEND DATA CONTRACT TEST RESULTS")
    print("=" * 85)
    for k, v in results.items():
        print(f"{k:20s} {v}")
    print("=" * 85)

if __name__ == "__main__":
    run_acceptance_audit()
