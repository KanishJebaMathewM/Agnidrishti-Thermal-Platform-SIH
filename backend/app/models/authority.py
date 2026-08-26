import uuid
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlalchemy import String, DateTime, Date, ForeignKey, Boolean, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class Authority(Base):
    __tablename__ = "authorities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    district: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    
    # PLANT_EMERGENCY, FIRE_RESPONSE, FOREST_RESPONSE, POLLUTION_CONTROL, DISTRICT_EMERGENCY, SYSTEM_OPERATOR
    authority_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    department: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[Optional[str]] = mapped_column(String(100))
    official_email: Mapped[str] = mapped_column(String(200), nullable=False)
    official_phone: Mapped[Optional[str]] = mapped_column(String(20))
    portal_url: Mapped[Optional[str]] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    verified_on: Mapped[Optional[date]] = mapped_column(Date)
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    notifications = relationship("Notification", back_populates="authority")


class RoutingProfile(Base):
    __tablename__ = "routing_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. "industrial_fire_kerala"
    state: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    district: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    classification: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. "Industrial Incident"
    
    primary_authority_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("authorities.id", ondelete="RESTRICT"), nullable=False)
    secondary_authority_ids: Mapped[Optional[List[uuid.UUID]]] = mapped_column(ARRAY(UUID(as_uuid=True)))
    
    rules: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
