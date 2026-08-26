from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

class ObservationBase(BaseModel):
    source_type: str
    source_product: Optional[str] = None
    satellite: Optional[str] = None
    timestamp_utc: datetime
    latitude: float
    longitude: float
    h3_cell: Optional[str] = None
    frp: Optional[float] = None
    bright_ti4: Optional[float] = None
    bright_ti5: Optional[float] = None
    confidence: Optional[str] = None
    quality_flags: Optional[Dict[str, Any]] = None
    thermal_features: Optional[Dict[str, Any]] = None

class ObservationCreate(ObservationBase):
    raw_record_ref: Optional[Dict[str, Any]] = None
    source_id: Optional[uuid.UUID] = None

class ObservationDetail(ObservationBase):
    id: uuid.UUID
    ingested_at: datetime
    source_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)
