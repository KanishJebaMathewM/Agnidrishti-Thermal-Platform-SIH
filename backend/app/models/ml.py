import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, ForeignKey, Boolean, Text, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_tag: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False) # e.g. xgb_v1.0
    feature_set_version: Mapped[Optional[str]] = mapped_column(String(50))
    training_data_version: Mapped[Optional[str]] = mapped_column(String(50))
    trained_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # metrics: precision, recall, f1, etc.
    metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    artifact_path: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)


class TrainingLabel(Base):
    __tablename__ = "training_labels"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    observation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("observations.id", ondelete="CASCADE"), nullable=False)
    
    label: Mapped[str] = mapped_column(String(50), nullable=False) # class name
    label_source: Mapped[Optional[str]] = mapped_column(String(100)) # e.g. "operator_feedback", "weak_rule_landuse"
    label_confidence: Mapped[Optional[float]] = mapped_column(Float)
    
    # UNVERIFIED, VERIFIED, DISPUTED
    verification_status: Mapped[str] = mapped_column(String(30), default="UNVERIFIED", nullable=False)
    labeled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
