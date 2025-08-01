from uuid import UUID
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models import models

# Returns an event by its UUID
def get_event(db: Session, event_id: UUID) -> models.Event | None:
   
    return db.query(models.Event).filter(models.Event.id == event_id).first()

# Returns all events for a given link, ordered by creation date (desc)
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

# Returns all events with pagination, ordered by creation date (desc)
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

# Returns the click count for a specific link
def get_link_click_count(db: Session, link_id: UUID) -> int:
    """
    Get the total number of click events for a specific link.
    
    Args:
        db: Database session
        link_id: The UUID of the link
        
    Returns:
        The total number of click events
    """
    return (
        db.query(models.Event)
        .filter(
            models.Event.link_id == link_id,
            models.Event.type == "CLICK"
        )
        .count()
    )

# Creates a new event
def create_event(db: Session, event: Dict[str, Any]) -> models.Event:
    
    db_event = models.Event(
        link_id=event.link_id,
        type=event.type,
        event_data=event.event_data
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event
