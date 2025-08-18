"""
Link API endpoints for creating, reading, updating, and deleting shortened links.
"""
from typing import List, Any
from uuid import UUID

from fastapi import APIRouter, Depends, status, Query, Request, Response, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import base64
import traceback
from datetime import datetime

from app.api import schemas
from app.crud import crud_link, crud_domain
from app.db.database import SessionLocal
from app.services import LinkService
from app.api.schemas import LinkCreate
from app.core.config import settings
from app.core.security import get_current_active_user
from app.core.exceptions import BadRequestException, NotFoundException, ForbiddenException

# Dependency that provides a database session for each request
def get_db():
    """Get a database session for the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to get the current user (placeholder for auth)
def get_current_user() -> UUID | None:
    """Get the current user ID (placeholder for actual auth)."""
    # TODO: Implement actual authentication
    return None

# Initialize the API router for link endpoints
router = APIRouter()

@router.post("/", response_model=schemas.Link, status_code=status.HTTP_201_CREATED)
def create_link_endpoint(
    link_in: schemas.LinkCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Create a new shortened link.
    
    Simple payload: {"url": "https://example.com"}
    With custom code: {"url": "https://example.com", "short_code": "mylink"}
    With title: {"url": "https://example.com", "title": "My Link"}
    """
    try:
        print(f"DEBUG: Received validated link_in = {link_in}")
        
        # Convert validated schema to dict for service layer
        link_dict = link_in.model_dump()
        print(f"DEBUG: link_dict = {link_dict}")
        
        link_service = LinkService(db)
        db_link = link_service.create_link(link_data=link_dict, user_id=current_user.id)
        return schemas.Link.from_db_model(db_link)
    except ValueError as e:
        raise BadRequestException(str(e))
    except Exception as e:
        print('Link creation error:', e)
        traceback.print_exc()
        raise BadRequestException("An error occurred while creating the link") from e

@router.get("/", response_model=List[schemas.Link])
def read_links_endpoint(
    space_id: UUID | None = Query(None, description="Filter links by Space ID"),
    domain_id: str | None = Query(None, description="Filter links by Domain ID (domain name)"),
    is_active: bool | None = Query(True, description="Filter links by active status (defaults to true)"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Get a list of shortened links, optionally filtered by space, domain, or active status.
    By default, only active links are returned.
    
    - **space_id**: Filter links by space ID (optional)
    - **domain_id**: Filter links by domain ID (optional)
    - **is_active**: Filter links by active status (defaults to true, set to false to see inactive links)
    - **skip**: Number of records to skip for pagination
    - **limit**: Maximum number of records to return (max 100)
    """
    try:
        link_service = LinkService(db)
        
        # Use the new filtered query function with is_active defaulting to True
        db_links = crud_link.get_links_filtered(
            db=db,
            space_id=space_id,
            domain_id=domain_id,
            is_active=is_active,
            skip=skip,
            limit=min(limit, 100)
        )
        return [schemas.Link.from_db_model(link) for link in db_links]
    except Exception as e:
        raise BadRequestException("An error occurred while retrieving links") from e

@router.get("/{link_id}", response_model=schemas.Link)
def read_link_endpoint(
    link_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Get detailed information about a specific shortened link.
    
    - **link_id**: The UUID of the link to retrieve
    """
    db_link = crud_link.get_link(db, link_id=link_id)
    if db_link is None:
        raise NotFoundException("Link")
    
    # In a real app, you'd check if the current user has permission to view this link
    return schemas.Link.from_db_model(db_link)

@router.put("/{link_id}", response_model=schemas.Link)
def update_link_endpoint(
    link_id: UUID,
    link_in: schemas.LinkUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Update an existing shortened link.
    
    - **link_id**: The UUID of the link to update
    - **All other fields**: Fields to update (all optional)
    """
    try:
        link_service = LinkService(db)
        
        # Convert Pydantic model to dict for service layer
        update_dict = link_in.model_dump(exclude_unset=True)
        
        updated_link = link_service.update_link(
            link_id=link_id,
            update_data=update_dict,
            user_id=current_user.id
        )
        
        if not updated_link:
            raise NotFoundException("Link")
            
        return schemas.Link.from_db_model(updated_link)
    except PermissionError as e:
        raise ForbiddenException(str(e))
    except ValueError as e:
        raise BadRequestException(str(e))
    except Exception as e:
        raise BadRequestException("An error occurred while updating the link") from e

@router.delete("/{link_id}", response_model=schemas.Link)
def delete_link_endpoint(
    link_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Delete a shortened link with authorization checks.
    
    - **link_id**: The UUID of the link to delete
    """
    try:
        link_service = LinkService(db)
        deleted_link = link_service.delete_link(
            link_id=link_id,
            user_id=current_user.id
        )
        
        if not deleted_link:
            raise NotFoundException("Link")
            
        return schemas.Link.from_db_model(deleted_link)
    except PermissionError as e:
        raise ForbiddenException(str(e))
    except Exception as e:
        raise BadRequestException("An error occurred while deleting the link") from e
