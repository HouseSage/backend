# Imports FastAPI, SQLAlchemy, app schemas, and CRUD utilities for link API endpoints
from typing import List, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api import schemas
from app.crud import crud_link, crud_domain 
from app.db.database import SessionLocal

# Dependency that provides a database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initializes the API router for link endpoints
router = APIRouter()

# Link Endpoints

@router.post("/", response_model=schemas.Link, status_code=status.HTTP_201_CREATED)
def create_link_endpoint(link: schemas.LinkCreate, db: Session = Depends(get_db)) -> Any:
   
    existing_link = crud_link.get_link_by_domain_and_short_code(
        db, short_code=link.short_code, domain_id=link.domain_id
    )
    if existing_link:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A link with this short_code and domain already exists.",
        )

    if link.domain_id:
        domain = crud_domain.get_domain(db, domain_name=link.domain_id)
        if not domain:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Domain with name '{link.domain_id}' not found.",
            )
            
    return crud_link.create_link(db=db, link=link)

@router.get("/", response_model=List[schemas.Link])
def read_links_endpoint(
    space_id: UUID | None = Query(None, description="Filter links by Space ID"),
    domain_id: str | None = Query(None, description="Filter links by Domain ID (domain name)"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> Any:
   
    if space_id:
        links = crud_link.get_links_by_space(db, space_id=space_id, skip=skip, limit=limit)
    elif domain_id:
        links = crud_link.get_links_by_domain(db, domain_id=domain_id, skip=skip, limit=limit)
    else:
        links = crud_link.get_all_links(db, skip=skip, limit=limit)
    return links

@router.get("/{link_id}", response_model=schemas.Link)
def read_link_endpoint(link_id: UUID, db: Session = Depends(get_db)) -> Any:
   
    db_link = crud_link.get_link(db, link_id=link_id)
    if db_link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
    return db_link

@router.put("/{link_id}", response_model=schemas.Link)
def update_link_endpoint(
    link_id: UUID, link_in: schemas.LinkUpdate, db: Session = Depends(get_db)
) -> Any:
  
    db_link = crud_link.get_link(db, link_id=link_id)
    if not db_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
        )
    updated_link = crud_link.update_link(db=db, db_link=db_link, link_in=link_in)
    return updated_link

@router.delete("/{link_id}", response_model=schemas.Link)
def delete_link_endpoint(link_id: UUID, db: Session = Depends(get_db)) -> Any:
    
    db_link = crud_link.get_link(db, link_id=link_id)
    if not db_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
        )
    deleted_link = crud_link.delete_link(db=db, link_id=link_id)
    return deleted_link
