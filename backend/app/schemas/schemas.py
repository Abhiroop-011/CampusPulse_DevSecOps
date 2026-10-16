"""
Pydantic v2 schemas for CampusPulse API request/response bodies.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.models import ClubCategory, EventStatus, RegistrationStatus


# ---------------------------------------------------------------------------
# Club Schemas
# ---------------------------------------------------------------------------

class ClubBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    slug: str = Field(..., min_length=2, max_length=120, pattern=r"^[a-z0-9-]+$")
    description: Optional[str] = None
    category: ClubCategory = ClubCategory.SOCIAL
    lead_email: Optional[str] = None


class ClubCreate(ClubBase):
    pass


class ClubUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=120)
    description: Optional[str] = None
    category: Optional[ClubCategory] = None
    lead_email: Optional[str] = None


class ClubRead(ClubBase):
    id: int
    created_at: datetime
    event_count: Optional[int] = 0

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Event Schemas
# ---------------------------------------------------------------------------

class EventBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=255)
    event_date: datetime
    capacity: int = Field(default=50, ge=1, le=5000)
    category: Optional[str] = Field(None, max_length=50)
    status: EventStatus = EventStatus.DRAFT


class EventCreate(EventBase):
    club_id: int


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=255)
    event_date: Optional[datetime] = None
    capacity: Optional[int] = Field(None, ge=1, le=5000)
    category: Optional[str] = Field(None, max_length=50)
    status: Optional[EventStatus] = None

    @field_validator("capacity")
    @classmethod
    def capacity_must_be_positive(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 1:
            raise ValueError("Capacity must be at least 1")
        return v


class EventRead(EventBase):
    id: int
    club_id: int
    registered_count: int
    created_at: datetime
    club_name: Optional[str] = None
    spots_remaining: Optional[int] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Registration Schemas
# ---------------------------------------------------------------------------

class RegistrationCreate(BaseModel):
    student_name: str = Field(..., min_length=2, max_length=200)
    student_email: str = Field(..., min_length=5, max_length=255)
    student_id: Optional[str] = Field(None, max_length=50)

    @field_validator("student_email")
    @classmethod
    def email_must_be_valid(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("A valid email address is required")
        return v.lower().strip()


class RegistrationRead(BaseModel):
    id: int
    event_id: int
    student_name: str
    student_email: str
    student_id: Optional[str]
    status: RegistrationStatus
    registered_at: datetime

    model_config = {"from_attributes": True}


class RegistrationCancel(BaseModel):
    student_email: str


# ---------------------------------------------------------------------------
# Stats Schema
# ---------------------------------------------------------------------------

class PlatformStats(BaseModel):
    total_events: int
    published_events: int
    total_clubs: int
    total_registrations: int
    average_capacity_utilization: float


# ---------------------------------------------------------------------------
# Generic Responses
# ---------------------------------------------------------------------------

class MessageResponse(BaseModel):
    message: str

class HealthResponse(BaseModel):
    status: str

class ReadyResponse(BaseModel):
    status: str
    database: str
