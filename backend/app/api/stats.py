"""
Platform-wide statistics endpoint.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Club, Event, EventStatus, Registration, RegistrationStatus
from app.schemas.schemas import PlatformStats

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("", response_model=PlatformStats, summary="Platform statistics dashboard")
def get_stats(db: Session = Depends(get_db)):
    total_events = db.query(func.count(Event.id)).scalar() or 0
    published_events = (
        db.query(func.count(Event.id))
        .filter(Event.status == EventStatus.PUBLISHED)
        .scalar() or 0
    )
    total_clubs = db.query(func.count(Club.id)).scalar() or 0
    total_registrations = (
        db.query(func.count(Registration.id))
        .filter(Registration.status == RegistrationStatus.CONFIRMED)
        .scalar() or 0
    )

    # Average capacity utilization across all PUBLISHED events
    events_with_capacity = (
        db.query(Event.capacity, Event.registered_count)
        .filter(Event.status == EventStatus.PUBLISHED, Event.capacity > 0)
        .all()
    )
    if events_with_capacity:
        utilization = sum(
            r.registered_count / r.capacity for r in events_with_capacity
        ) / len(events_with_capacity) * 100
    else:
        utilization = 0.0

    return PlatformStats(
        total_events=total_events,
        published_events=published_events,
        total_clubs=total_clubs,
        total_registrations=total_registrations,
        average_capacity_utilization=round(utilization, 1),
    )
