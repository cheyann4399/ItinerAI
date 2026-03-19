from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.models.base import get_db
from app.models.itinerary import Itinerary
from app.models.user import User
from app.schemas.itinerary import ItineraryCreate, ItineraryRead, ItineraryUpdate

router = APIRouter(prefix="/itineraries", tags=["itineraries"])


@router.post("", response_model=ItineraryRead, status_code=status.HTTP_201_CREATED)
def create_itinerary(
  payload: ItineraryCreate,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> Itinerary:
  itinerary = Itinerary(
    user_id=current_user.id,
    title=payload.title,
    description=payload.description,
    content=payload.content,
  )
  db.add(itinerary)
  db.commit()
  db.refresh(itinerary)
  return itinerary


@router.get("", response_model=list[ItineraryRead])
def list_itineraries(
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> list[Itinerary]:
  return (
    db.query(Itinerary)
    .filter(Itinerary.user_id == current_user.id)
    .order_by(Itinerary.created_at.desc())
    .all()
  )


@router.get("/{itinerary_id}", response_model=ItineraryRead)
def get_itinerary(
  itinerary_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> Itinerary:
  itinerary = (
    db.query(Itinerary)
    .filter(
      Itinerary.id == itinerary_id,
      Itinerary.user_id == current_user.id,
    )
    .first()
  )
  if not itinerary:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Itinerary not found",
    )
  return itinerary


@router.patch("/{itinerary_id}", response_model=ItineraryRead)
def update_itinerary(
  itinerary_id: int,
  payload: ItineraryUpdate,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> Itinerary:
  itinerary = (
    db.query(Itinerary)
    .filter(
      Itinerary.id == itinerary_id,
      Itinerary.user_id == current_user.id,
    )
    .first()
  )
  if not itinerary:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Itinerary not found",
    )
  if payload.title is not None:
    itinerary.title = payload.title
  if payload.description is not None:
    itinerary.description = payload.description
  if payload.content is not None:
    itinerary.content = payload.content
  itinerary.updated_at = datetime.now(timezone.utc)
  db.add(itinerary)
  db.commit()
  db.refresh(itinerary)
  return itinerary
