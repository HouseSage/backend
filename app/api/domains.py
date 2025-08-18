from typing import List, Any
from uuid import UUID

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.api import schemas
from app.crud import crud_domain
from app.db.database import SessionLocal
from app.core.security import get_current_active_user
from app.models.models import User as UserModel
from app.core.exceptions import ConflictException

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
def create_domain_endpoint(
    domain_in: schemas.DomainCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_active_user)
) -> Any:
    # Check if domain already exists
    db_domain = crud_domain.get_domain(db, domain_name=domain_in.domain)
    if db_domain:
        raise ConflictException("Domain already exists")
    
    # Verify user has access to the space
    from app.api.spaces import check_space_membership
    check_space_membership(db, space_id=domain_in.space_id, user_id=current_user.id)
    
    # Convert schema to dict for CRUD layer
    domain_dict = domain_in.model_dump()
    return crud_domain.create_domain(db=db, domain=domain_dict)

@router.get("/", response_model=List[schemas.Domain])
def read_domains_endpoint(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
    space_id: UUID = Query(None, description="Optional space ID to filter domains")
) -> Any:
    if space_id:
        # Verify user has access to the space
        from app.api.spaces import check_space_membership
        check_space_membership(db, space_id=space_id, user_id=current_user.id)
        domains = crud_domain.get_domains_by_space(db, space_id=space_id, skip=skip, limit=limit)
    else:
        # Only return domains for spaces the user has access to
        from app.crud import crud_space
        user_spaces = crud_space.get_spaces_by_user(db, user_id=current_user.id)
        space_ids = [space.id for space in user_spaces]
        domains = []
        for space_id in space_ids:
            space_domains = crud_domain.get_domains_by_space(db, space_id=space_id, skip=skip, limit=limit)
            domains.extend(space_domains)
    return domains

@router.get("/{domain_name}", response_model=schemas.Domain)
def read_domain_endpoint(
    domain_name: str, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
) -> Any:
    db_domain = crud_domain.get_domain(db, domain_name=domain_name)
    if db_domain is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain not found")
    
    # Verify user has admin/owner access to the space that owns this domain
    from app.api.spaces import check_space_admin_or_owner
    check_space_admin_or_owner(db, space_id=db_domain.space_id, user_id=current_user.id)
    
    return db_domain



@router.delete("/{domain_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_domain_endpoint(
    domain_name: str, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
) -> None:
    db_domain = crud_domain.get_domain(db, domain_name=domain_name)
    if not db_domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found",
        )
    
    # Verify user has admin/owner access to the space that owns this domain
    from app.api.spaces import check_space_admin_or_owner
    check_space_admin_or_owner(db, space_id=db_domain.space_id, user_id=current_user.id)
    
    crud_domain.delete_domain(db=db, domain_name=domain_name)
    return None
