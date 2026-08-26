"""
SQLAlchemy Model for ISRO Bhuvan LULC AOI Cache.
Stores real retrieved land-use / land-cover classification from ISRO NRSC Bhuvan.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Float, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class BhuvanLulcCache(Base):
    __tablename__ = "bhuvan_lulc_cache"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    aoi_key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    h3_cell: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    
    lulc_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    lulc_class: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    raw_category: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    
    source: Mapped[str] = mapped_column(String(50), default="ISRO_BHUVAN")
    product: Mapped[str] = mapped_column(String(50), default="LULC AOI Wise")
    status: Mapped[str] = mapped_column(String(30), default="LIVE")
    response_metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    retrieved_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_verified: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
