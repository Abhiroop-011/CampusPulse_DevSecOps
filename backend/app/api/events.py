"""
Events CRUD API router — the core domain of CampusPulse.
Supports GET (list + detail), POST, PUT, DELETE, plus registration management.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Club, Event, EventStatus, Registration, RegistrationStatus
from app.schemas.schemas import (
    EventCreate, EventRead, EventUpdate, MessageResponse,
    RegistrationCreate, RegistrationRead,
)

router = APIRouter(prefix="/api/events", tags=["events"])


def _to_event_read(event: Event) -> EventRead:
    spots_remaining = max(0, event.capacity - event.registered_count)
    club_name = event.club.name if event.club else None
    return EventRead(
        id=event.id,
        club_id=event.club_id,
        title=event.title,
        description=event.description,
        location=event.location,
        event_date=event.event_date,
        capacity=event.capacity,
        registered_count=event.registered_count,
        category=event.category,
        status=event.status,
        created_at=event.created_at,
        club_name=club_name,
        spots_remaining=spots_remaining,
    )


# ---------------------------------------------------------------------------
# Events CRUD
# ---------------------------------------------------------------------------

@router.get("", response_model=List[EventRead], summary="List events with optional filters")
def list_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = None,
    club_id: Optional[int] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Event)
    if status:
        q = q.filter(Event.status == status.upper())
    if club_id:
        q = q.filter(Event.club_id == club_id)
    if category:
        q = q.filter(Event.category == category)
    events = q.order_by(Event.event_date.asc()).offset(skip).limit(limit).all()
    return [_to_event_read(e) for e in events]


@router.get("/{event_id}", response_model=EventRead, summary="Get an event by ID")
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return _to_event_read(event)


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED, summary="Create an event")
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    club = db.query(Club).filter(Club.id == payload.club_id).first()
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Club with id={payload.club_id} not found",
        )
    event = Event(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return _to_event_read(event)


@router.put("/{event_id}", response_model=EventRead, summary="Update an event")
def update_event(event_id: int, payload: EventUpdate, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    update_data = payload.model_dump(exclude_unset=True)
    # Prevent capacity being reduced below registered count
    if "capacity" in update_data and update_data["capacity"] < event.registered_count:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Capacity cannot be reduced below current registrations ({event.registered_count})",
        )
    for field, value in update_data.items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)
    return _to_event_read(event)


@router.delete("/{event_id}", response_model=MessageResponse, summary="Delete an event")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    db.delete(event)
    db.commit()
    return {"message": f"Event '{event.title}' deleted successfully"}


# ---------------------------------------------------------------------------
# Registrations (sub-resource under /api/events/{event_id}/registrations)
# ---------------------------------------------------------------------------

@router.post(
    "/{event_id}/registrations",
    response_model=RegistrationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a student for an event",
)
def register_for_event(event_id: int, payload: RegistrationCreate, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    if event.status != EventStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Registrations are only open for PUBLISHED events",
        )

    if event.registered_count >= event.capacity:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Event is at full capacity",
        )

    # Check for existing active registration
    existing = (
        db.query(Registration)
        .filter(
            Registration.event_id == event_id,
            Registration.student_email == payload.student_email.lower().strip(),
            Registration.status == RegistrationStatus.CONFIRMED,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This student is already registered for this event",
        )

    registration = Registration(
        event_id=event_id,
        student_name=payload.student_name,
        student_email=payload.student_email.lower().strip(),
        student_id=payload.student_id,
        status=RegistrationStatus.CONFIRMED,
    )
    db.add(registration)
    event.registered_count += 1
    db.commit()
    db.refresh(registration)
    return registration


@router.delete(
    "/{event_id}/registrations/{registration_id}",
    response_model=MessageResponse,
    summary="Cancel a registration",
)
def cancel_registration(event_id: int, registration_id: int, db: Session = Depends(get_db)):
    registration = (
        db.query(Registration)
        .filter(
            Registration.id == registration_id,
            Registration.event_id == event_id,
            Registration.status == RegistrationStatus.CONFIRMED,
        )
        .first()
    )
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active registration not found",
        )

    registration.status = RegistrationStatus.CANCELLED
    event = db.query(Event).filter(Event.id == event_id).first()
    if event and event.registered_count > 0:
        event.registered_count -= 1
    db.commit()
    return {"message": "Registration cancelled successfully"}


@router.get(
    "/{event_id}/registrations",
    response_model=List[RegistrationRead],
    summary="List registrations for an event",
)
def list_registrations(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    registrations = (
        db.query(Registration)
        .filter(
            Registration.event_id == event_id,
            Registration.status == RegistrationStatus.CONFIRMED,
        )
        .all()
    )
    return registrations
