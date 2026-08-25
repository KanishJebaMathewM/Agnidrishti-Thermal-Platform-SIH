from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
import uuid
from datetime import date, datetime

class AuthorityBase(BaseModel):
    state: str
    district: str
    authority_type: str # PLANT_EMERGENCY, FIRE_RESPONSE, etc.
    department: str
    role: Optional[str] = None
    official_email: str
    official_phone: Optional[str] = None
    portal_url: Optional[str] = None
    active: bool = True
    verified_on: Optional[date] = None
    source_url: Optional[str] = None

class AuthorityCreate(AuthorityBase):
    pass

class AuthorityUpdate(BaseModel):
    state: Optional[str] = None
    district: Optional[str] = None
    authority_type: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    official_email: Optional[str] = None
    official_phone: Optional[str] = None
    portal_url: Optional[str] = None
    active: Optional[bool] = None
    verified_on: Optional[date] = None
    source_url: Optional[str] = None

class AuthorityDetail(AuthorityBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RoutingResult(BaseModel):
    state: str
    district: str
    routing_profile: Optional[str] = None
    primary_authority: Optional[AuthorityDetail] = None
    secondary_authorities: List[AuthorityDetail] = []

    model_config = ConfigDict(from_attributes=True)
class RoutingProfileBase(BaseModel):
    name: str
    state: str
    district: str
    classification: str
    primary_authority_id: uuid.UUID
    secondary_authority_ids: Optional[List[uuid.UUID]] = None
    rules: Optional[Dict[str, Any]] = None

class RoutingProfileDetail(RoutingProfileBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
