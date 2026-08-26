import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry

from app.models.base import Base

class Observation(Base):
    __tablename__ = "observations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. "FIRMS_VIIRS", "INSAT"
    source_product: Mapped[Optional[str]] = mapped_column(String(50))
    satellite: Mapped[Optional[str]] = mapped_column(String(50))
    timestamp_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    
    # PostGIS Point column (SRID 4326 - WGS 84)
    geometry: Mapped[Any] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        nullable=False
    )
    
    h3_cell: Mapped[Optional[str]] = mapped_column(String(15), index=True)
    frp: Mapped[Optional[float]] = mapped_column(Float)
    bright_ti4: Mapped[Optional[float]] = mapped_column(Float)
    bright_ti5: Mapped[Optional[float]] = mapped_column(Float)
    confidence: Mapped[Optional[str]] = mapped_column(String(10)) # 'low', 'nominal', 'high'
    
    quality_flags: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    thermal_features: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    raw_record_ref: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow,
        nullable=False
    )
    
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("thermal_sources.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relationships
    thermal_source = relationship("ThermalSource", back_populates="observations")
    events = relationship("Event", secondary="event_observations", back_populates="observations")
