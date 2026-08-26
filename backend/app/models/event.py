import uuid
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import Table, Column, String, DateTime, Float, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry

from app.models.base import Base

# Association table for many-to-many relationship between Event and Observation
event_observations = Table(
    "event_observations",
    Base.metadata,
    Column("event_id", UUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
    Column("observation_id", UUID(as_uuid=True), ForeignKey("observations.id", ondelete="CASCADE"), primary_key=True)
)

class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_seen: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_seen: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    centroid_lat: Mapped[float] = mapped_column(Float, nullable=False)
    centroid_lon: Mapped[float] = mapped_column(Float, nullable=False)
    
    # PostGIS Point centroid
    centroid: Mapped[Any] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        nullable=False
    )
    
    observation_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("thermal_sources.id", ondelete="SET NULL"),
        nullable=True
    )
    
    classification: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. "Industrial Incident", etc.
    classification_confidence: Mapped[Optional[float]] = mapped_column(Float)
    anomaly_score: Mapped[Optional[float]] = mapped_column(Float)
    anomaly_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # NORMAL, OBSERVE, REVIEW, HIGH, CRITICAL
    severity: Mapped[str] = mapped_column(String(20), default="NORMAL", nullable=False)
    
    # NEW, ANALYZING, CANDIDATE, HUMAN_REVIEW, CONFIRMED, FALSE_ALARM, RECLASSIFIED
    status: Mapped[str] = mapped_column(String(30), default="NEW", nullable=False)
    
    state: Mapped[Optional[str]] = mapped_column(String(100))
    district: Mapped[Optional[str]] = mapped_column(String(100))
    model_version: Mapped[Optional[str]] = mapped_column(String(50))
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    thermal_source = relationship("ThermalSource", back_populates="events")
    observations = relationship("Observation", secondary=event_observations, back_populates="events")
    notifications = relationship("Notification", back_populates="event", cascade="all, delete-orphan")
    feedbacks = relationship("OperatorFeedback", back_populates="event", cascade="all, delete-orphan")
