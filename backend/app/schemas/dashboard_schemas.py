from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
from app.schemas.event_schemas import EventSummary

class ClassificationDistItem(BaseModel):
    name: str
    value: int
    pct: str
    color: str

class RiskLevelItem(BaseModel):
    name: str
    count: int
    pct: str
    color: str

class StateAnomalyItem(BaseModel):
    state: str
    anomalies: int
    total: int

class DashboardSummary(BaseModel):
    total_events_24h: int
    anomaly_events_24h: int
    critical_events: int
    active_sources: int
    classification_distribution: List[ClassificationDistItem]
    risk_level_summary: List[RiskLevelItem]
    state_anomaly_data: List[StateAnomalyItem]
    recent_events: List[EventSummary]

    model_config = ConfigDict(from_attributes=True)

class MapEvent(BaseModel):
    id: str
    lat: float
    lon: float
    classification: str
    severity: str
    confidence: float
    anomaly_flag: bool

    model_config = ConfigDict(from_attributes=True)

class MapEventsResponse(BaseModel):
    events: List[MapEvent]

class TrendPoint(BaseModel):
    date: str
    industrial: int
    flare: int
    agricultural: int
    forest: int
    unknown: int

    model_config = ConfigDict(from_attributes=True)

class TrendsResponse(BaseModel):
    points: List[TrendPoint]
