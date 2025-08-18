from typing import List, Any
from uuid import UUID

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.api import schemas
from app.crud import crud_event, crud_link 
from app.db.database import SessionLocal
from app.core.exceptions import NotFoundException

# Imports FastAPI, SQLAlchemy, app schemas, and CRUD utilities for event API endpoints

# Dependency that provides a database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initializes the API router for event endpoints
router = APIRouter()

# Event Endpoints



@router.get("/", response_model=List[schemas.Event])
def read_events_endpoint(
    link_id: UUID | None = Query(None, description="Filter events by Link ID"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> Any:
    
    if link_id:
        events = crud_event.get_events_by_link(db, link_id=link_id, skip=skip, limit=limit)
    else:
        events = crud_event.get_all_events(db, skip=skip, limit=limit)
    return events

@router.get("/{event_id}", response_model=schemas.Event)
def read_event_endpoint(event_id: UUID, db: Session = Depends(get_db)) -> Any:
    
    db_event = crud_event.get_event(db, event_id=event_id)
    if db_event is None:
        raise NotFoundException("Event")
    return db_event
