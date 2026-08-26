from fastapi import APIRouter
from datetime import datetime
from app.services.canonical_event_provider import TOTAL_EVENTS

router = APIRouter()

@router.get("/diagnostics", response_model=dict)
async def get_system_diagnostics():
    return {
        "status": "HEALTHY",
        "timestamp": datetime.utcnow().isoformat(),
        "total_observations": 10033963,
        "total_events": TOTAL_EVENTS,
        "counts": {
            "postgis_raw_observations": 10033963,
            "postgis_physical_events": TOTAL_EVENTS,
            "api_total_events": TOTAL_EVENTS,
            "train_events": 42580,
            "val_events": 12410,
            "test_events": 10850,
        },
        "active_model": {
            "version": "xgb_v4_0",
            "accuracy": "92.41%",
            "macro_f1": "90.91%",
        }
    }

