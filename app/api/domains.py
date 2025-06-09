from typing import List, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api import schemas
from app.crud import crud_domain
from app.db.database import SessionLocal

# Dependency that provides a database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initializes the API router for domain endpoints
router = APIRouter()

# Domain Endpoints

@router.post("/", response_model=schemas.Domain, status_code=status.HTTP_201_CREATED)
def create_domain_endpoint(domain: schemas.DomainCreate, db: Session = Depends(get_db)) -> Any:
  
    db_domain = crud_domain.get_domain(db, domain_name=domain.domain)
    if db_domain:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Domain already exists.",
        )
    return crud_domain.create_domain(db=db, domain=domain)

@router.get("/", response_model=List[schemas.Domain])
def read_domains_endpoint(
    space_id: UUID | None = Query(None, description="Filter domains by Space ID"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> Any:
   
    if space_id:
        domains = crud_domain.get_domains_by_space(db, space_id=space_id, skip=skip, limit=limit)
    else:
        domains = crud_domain.get_all_domains(db, skip=skip, limit=limit)
    return domains

@router.get("/{domain_name}", response_model=schemas.Domain)
def read_domain_endpoint(domain_name: str, db: Session = Depends(get_db)) -> Any:
    
    db_domain = crud_domain.get_domain(db, domain_name=domain_name)
    if db_domain is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain not found")
    return db_domain

@router.put("/{domain_name}", response_model=schemas.Domain)
def update_domain_endpoint(
    domain_name: str, domain_in: schemas.DomainUpdate, db: Session = Depends(get_db)
) -> Any:
   
    db_domain = crud_domain.get_domain(db, domain_name=domain_name)
    if not db_domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found",
        )
    updated_domain = crud_domain.update_domain(db=db, db_domain=db_domain, domain_in=domain_in)
    return updated_domain

@router.delete("/{domain_name}", response_model=schemas.Domain)
def delete_domain_endpoint(domain_name: str, db: Session = Depends(get_db)) -> Any:
   
    db_domain = crud_domain.get_domain(db, domain_name=domain_name)
    if not db_domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found",
        )
    deleted_domain = crud_domain.delete_domain(db=db, domain_name=domain_name)
    return deleted_domain
