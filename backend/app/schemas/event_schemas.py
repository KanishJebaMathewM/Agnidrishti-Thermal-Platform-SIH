from pydantic import BaseModel, ConfigDict, model_validator
from datetime import datetime, timezone
from typing import Optional

class EventSummary(BaseModel):
    id: str
    classification: str
    confidence: float
    lat: float
    lon: float
    placeName: str
    state: str
    timestamp: str
    timeAgo: str
    formattedTime: str
    persistenceText: str
    persistenceSubtext: str
    persistenceNights: int
    status: str # Suppressed | Escalated | Under Review
    frp: float
    brightnessTemp4: float
    brightnessTemp11: float
    flameTemp: float
    burnArea: float
    baseline: float
    current: float
    routedTo: str # Fire Services | CPCB | Forest Department | State Aggregation
    isAnomaly: bool

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def from_db_model(cls, data):
        if isinstance(data, dict):
            return data
        
        now = datetime.now(timezone.utc)
        first_seen = getattr(data, "first_seen", now) or now
        last_seen = getattr(data, "last_seen", now) or now
        if first_seen.tzinfo is None:
            first_seen = first_seen.replace(tzinfo=timezone.utc)
        if last_seen.tzinfo is None:
            last_seen = last_seen.replace(tzinfo=timezone.utc)
        
        diff = now - first_seen
        hours = int(diff.total_seconds() // 3600)
        if hours < 1:
            mins = int(diff.total_seconds() // 60)
            time_ago = f"{mins}m ago"
        else:
            time_ago = f"{hours}h ago"
            
        formatted_time = first_seen.strftime("%d %b, %I:%M %p").lower()
        
        days_diff = (last_seen - first_seen).days
        nights = max(1, days_diff)
        persistence_text = f"{nights} night" if nights == 1 else f"{nights} nights"
        persistence_subtext = "High" if nights > 5 else "Moderate" if nights > 2 else "Low"
        
        db_status = getattr(data, "status", "NEW")
        if db_status == "CONFIRMED":
            status = "Escalated"
        elif db_status in ("FALSE_ALARM", "Suppressed"):
            status = "Suppressed"
        else:
            status = "Under Review"
            
        classification = getattr(data, "classification", "Unknown")
        agency_map = {
            "Industrial Incident": "Fire Services",
            "Forest Fire": "Forest Department",
            "Agricultural Burn": "CPCB",
            "Persistent Flare/Kiln": "CPCB",
            "Unknown": "State Aggregation"
        }
        routed_to = agency_map.get(classification, "State Aggregation")
        
        district = getattr(data, "district", "")
        place_name = f"{district} Cluster Zone" if district else f"{getattr(data, 'state', 'India')} Zone"
        
        conf = getattr(data, "classification_confidence", 0.0) or 0.0
        if conf <= 1.0:
            conf = conf * 100
            
        payload = {
            "id": str(getattr(data, "id", "")),
            "classification": classification,
            "confidence": round(conf, 1),
            "lat": getattr(data, "centroid_lat", 0.0),
            "lon": getattr(data, "centroid_lon", 0.0),
            "placeName": place_name,
            "state": getattr(data, "state", "") or "Unknown",
            "timestamp": first_seen.isoformat() + "Z",
            "timeAgo": time_ago,
            "formattedTime": formatted_time,
            "persistenceText": persistence_text,
            "persistenceSubtext": persistence_subtext,
            "persistenceNights": nights,
            "status": status,
            "frp": getattr(data, "anomaly_score", 100.0) or 100.0, # using anomaly score / baseline diff context
            "brightnessTemp4": 330.0,
            "brightnessTemp11": 300.0,
            "flameTemp": 1000.0,
            "burnArea": 1.5,
            "baseline": 25.0,
            "current": getattr(data, "anomaly_score", 80.0) or 80.0,
            "routedTo": routed_to,
            "isAnomaly": getattr(data, "anomaly_flag", False),
        }
        for field in ("observation_count", "source_id", "district", "model_version", "created_at", "updated_at"):
            if hasattr(data, field):
                payload[field] = getattr(data, field)
        return payload

class EventDetail(EventSummary):
    observation_count: int
    source_id: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    model_version: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
