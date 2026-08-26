import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    authority_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("authorities.id", ondelete="CASCADE"), nullable=False)
    
    # EMAIL, PHONE, PORTAL
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # READY, PRESENTED, ACTION_TAKEN
    status: Mapped[str] = mapped_column(String(30), default="READY", nullable=False)
    
    alert_content: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    presented_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    action_taken_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    operator_id: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    event = relationship("Event", back_populates="notifications")
    authority = relationship("Authority", back_populates="notifications")


class OperatorFeedback(Base):
    __tablename__ = "operator_feedback"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    
    model_prediction: Mapped[Optional[str]] = mapped_column(String(50))
    model_confidence: Mapped[Optional[float]] = mapped_column(Float)
    human_label: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. "Industrial Incident" etc.
    reviewer: Mapped[str] = mapped_column(String(100), nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    event = relationship("Event", back_populates="feedbacks")
