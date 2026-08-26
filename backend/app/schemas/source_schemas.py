from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime

class SourceBase(BaseModel):
    h3_cell: str
    representative_lat: float
    representative_lon: float
    expected_class: Optional[str] = None
    mean_frp: Optional[float] = None
    frp_std: Optional[float] = None
    median_frp: Optional[float] = None
    monthly_profile: Optional[Dict[str, Any]] = None
    seasonal_profile: Optional[Dict[str, Any]] = None
    typical_hours: Optional[List[int]] = None
    status: str = "NEW"
    classification_confidence: Optional[float] = None

class SourceCreate(SourceBase):
    pass

class SourceSummary(BaseModel):
    id: str
    name: str
    type: str # Flare, Kiln, Power Plant, Refinery, Steel Mill
    lat: float
    lon: float
    placeName: str
    state: str
    expectedHours: str
    lastDeviationText: str
    lastDeviationPct: Optional[str] = None
    status: str # Registered | Flagged for Inspection

    model_config = ConfigDict(from_attributes=True)

class SourceDetail(SourceSummary):
    h3_cell: str
    observation_count: int
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    mean_frp: Optional[float] = None
    frp_std: Optional[float] = None
    median_frp: Optional[float] = None
    monthly_profile: Optional[Dict[str, Any]] = None
    seasonal_profile: Optional[Dict[str, Any]] = None
    typical_hours: Optional[List[int]] = None
    classification_confidence: Optional[float] = None
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)
