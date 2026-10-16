"""
Clubs CRUD API router.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Club, Event
from app.schemas.schemas import ClubCreate, ClubRead, ClubUpdate, MessageResponse

router = APIRouter(prefix="/api/clubs", tags=["clubs"])


def _to_club_read(club: Club, db: Session) -> ClubRead:
    event_count = db.query(func.count(Event.id)).filter(Event.club_id == club.id).scalar() or 0
    data = {
        "id": club.id,
        "name": club.name,
        "slug": club.slug,
        "description": club.description,
        "category": club.category,
        "lead_email": club.lead_email,
        "created_at": club.created_at,
        "event_count": event_count,
    }
    return ClubRead(**data)


@router.get("", response_model=List[ClubRead], summary="List all clubs")
def list_clubs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Club)
    if category:
        q = q.filter(Club.category == category.upper())
    clubs = q.offset(skip).limit(limit).all()
    return [_to_club_read(c, db) for c in clubs]


@router.get("/{club_id}", response_model=ClubRead, summary="Get a club by ID")
def get_club(club_id: int, db: Session = Depends(get_db)):
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club not found")
    return _to_club_read(club, db)


@router.post("", response_model=ClubRead, status_code=status.HTTP_201_CREATED, summary="Create a club")
def create_club(payload: ClubCreate, db: Session = Depends(get_db)):
    if db.query(Club).filter(Club.slug == payload.slug).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A club with slug '{payload.slug}' already exists",
        )
    club = Club(**payload.model_dump())
    db.add(club)
    db.commit()
    db.refresh(club)
    return _to_club_read(club, db)


@router.put("/{club_id}", response_model=ClubRead, summary="Update a club")
def update_club(club_id: int, payload: ClubUpdate, db: Session = Depends(get_db)):
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club not found")
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(club, field, value)
    db.commit()
    db.refresh(club)
    return _to_club_read(club, db)


@router.delete("/{club_id}", response_model=MessageResponse, summary="Delete a club")
def delete_club(club_id: int, db: Session = Depends(get_db)):
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club not found")
    db.delete(club)
    db.commit()
    return {"message": f"Club '{club.name}' deleted successfully"}
