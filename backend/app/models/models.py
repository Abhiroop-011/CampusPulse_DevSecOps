"""
CampusPulse SQLAlchemy ORM Models.

Tables:
  - clubs         : campus clubs / organizations
  - events        : events hosted by clubs
  - registrations : student event registrations
"""
import enum
from datetime import datetime

from sqlalchemy import (
    Column, DateTime, Enum, ForeignKey, Integer,
    String, Text, UniqueConstraint, func,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class ClubCategory(str, enum.Enum):
    TECH = "TECH"
    ARTS = "ARTS"
    SPORTS = "SPORTS"
    ACADEMIC = "ACADEMIC"
    SOCIAL = "SOCIAL"
    CULTURAL = "CULTURAL"


class EventStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class RegistrationStatus(str, enum.Enum):
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


# ---------------------------------------------------------------------------
# Club
# ---------------------------------------------------------------------------

class Club(Base):
    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    slug = Column(String(120), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    category = Column(Enum(ClubCategory), nullable=False, default=ClubCategory.SOCIAL)
    lead_email = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    events = relationship("Event", back_populates="club", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Club id={self.id} name={self.name!r}>"


# ---------------------------------------------------------------------------
# Event
# ---------------------------------------------------------------------------

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    club_id = Column(Integer, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    event_date = Column(DateTime(timezone=True), nullable=False)
    capacity = Column(Integer, nullable=False, default=50)
    registered_count = Column(Integer, nullable=False, default=0)
    category = Column(String(50), nullable=True)
    status = Column(Enum(EventStatus), nullable=False, default=EventStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    club = relationship("Club", back_populates="events")
    registrations = relationship(
        "Registration", back_populates="event", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Event id={self.id} title={self.title!r}>"


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(
        Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    student_name = Column(String(200), nullable=False)
    student_email = Column(String(255), nullable=False)
    student_id = Column(String(50), nullable=True)
    status = Column(
        Enum(RegistrationStatus), nullable=False, default=RegistrationStatus.CONFIRMED
    )
    registered_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    event = relationship("Event", back_populates="registrations")

    # Prevent duplicate active registrations for the same student + event
    __table_args__ = (
        UniqueConstraint("event_id", "student_email", name="uq_registration_event_student"),
    )

    def __repr__(self) -> str:
        return f"<Registration id={self.id} event_id={self.event_id} email={self.student_email!r}>"
