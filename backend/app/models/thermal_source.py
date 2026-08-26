import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, DateTime, Float, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry

from app.models.base import Base

class ThermalSource(Base):
    __tablename__ = "thermal_sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    h3_cell: Mapped[str] = mapped_column(String(15), unique=True, index=True, nullable=False)
    representative_lat: Mapped[float] = mapped_column(Float, nullable=False)
    representative_lon: Mapped[float] = mapped_column(Float, nullable=False)
    state: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    district: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    
    # PostGIS Point
    geometry: Mapped[Any] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        nullable=False
    )
    
    first_seen: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_seen: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    observation_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    expected_class: Mapped[Optional[str]] = mapped_column(String(50))
    mean_frp: Mapped[Optional[float]] = mapped_column(Float)
    frp_std: Mapped[Optional[float]] = mapped_column(Float)
    median_frp: Mapped[Optional[float]] = mapped_column(Float)
    
    monthly_profile: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON) # e.g. {"1": 12.3, "2": 15.1, ...}
    seasonal_profile: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    typical_hours: Mapped[Optional[List[int]]] = mapped_column(JSON) # e.g. [18, 19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5]
    
    # NEW, OBSERVED, CANDIDATE, CONFIRMED, MONITORED, ARCHIVED
    status: Mapped[str] = mapped_column(String(30), default="NEW", nullable=False)
    classification_confidence: Mapped[Optional[float]] = mapped_column(Float)
    
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    observations = relationship("Observation", back_populates="thermal_source")
    events = relationship("Event", back_populates="thermal_source")
