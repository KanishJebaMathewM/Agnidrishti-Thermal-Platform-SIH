import uuid
from typing import Optional, Dict, Any
from sqlalchemy import String, BigInteger, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geometry

from app.models.base import Base

class AdminBoundary(Base):
    __tablename__ = "admin_boundaries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    level: Mapped[str] = mapped_column(String(20), nullable=False) # COUNTRY, STATE, DISTRICT
    state_id: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    state_name: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    district_id: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    district_name: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    
    # PostGIS MultiPolygon geometry (SRID 4326)
    geometry: Mapped[Any] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326, spatial_index=True),
        nullable=False
    )


class IndustrialFacility(Base):
    __tablename__ = "industrial_facilities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[Optional[str]] = mapped_column(Text)
    facility_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. "Refinery", "Kiln"
    
    # PostGIS Point
    geometry: Mapped[Any] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        nullable=False
    )
    
    osm_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    state: Mapped[Optional[str]] = mapped_column(String(100))
    district: Mapped[Optional[str]] = mapped_column(String(100))
    tags: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)


class LanduseFeature(Base):
    __tablename__ = "landuse_features"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    landuse_class: Mapped[str] = mapped_column(String(50), name="class", nullable=False) # FOREST, AGRICULTURAL, etc.
    
    # PostGIS MultiPolygon
    geometry: Mapped[Any] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326, spatial_index=True),
        nullable=False
    )
    
    source: Mapped[Optional[str]] = mapped_column(String(50)) # BHUVAN, OSM


class ForestBoundary(Base):
    __tablename__ = "forest_boundaries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    
    # PostGIS MultiPolygon
    geometry: Mapped[Any] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326, spatial_index=True),
        nullable=False
    )
    
    source: Mapped[Optional[str]] = mapped_column(String(50)) # FSI
