from uuid import UUID
from sqlalchemy.orm import Session

from app.models import models
from app.api import schemas

def get_event(db: Session, event_id: UUID) -> models.Event | None:
   
    return db.query(models.Event).filter(models.Event.id == event_id).first()

def get_events_by_link(
    db: Session, link_id: UUID, skip: int = 0, limit: int = 1000
) -> list[models.Event]:
  
    return (
        db.query(models.Event)
        .filter(models.Event.link_id == link_id)
        .order_by(models.Event.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_all_events(
    db: Session, skip: int = 0, limit: int = 1000
) -> list[models.Event]:
    
    return (
        db.query(models.Event)
        .order_by(models.Event.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_event(db: Session, event: schemas.EventCreate) -> models.Event:
    
    db_event = models.Event(
        link_id=event.link_id,
        type=event.type,
        event_data=event.event_data
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event
