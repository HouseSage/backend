"""
Link API endpoints for creating, reading, updating, and deleting shortened links.
"""
from typing import List, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Response, Body
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
    link: schemas.LinkCreate = Body(...),
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
        link_service = LinkService(db)
        db_link = link_service.create_link(link_data=link, user_id=current_user.id)
        return schemas.Link.from_db_model(db_link)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        print('Link creation error:', e)
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the link.",
        ) from e

@router.get("/", response_model=List[schemas.Link])
def read_links_endpoint(
    space_id: UUID | None = Query(None, description="Filter links by Space ID"),
    domain_id: str | None = Query(None, description="Filter links by Domain ID (domain name)"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Get a list of shortened links, optionally filtered by space or domain.
    
    - **space_id**: Filter links by space ID (optional)
    - **domain_id**: Filter links by domain ID (optional)
    - **skip**: Number of records to skip for pagination
    - **limit**: Maximum number of records to return (max 100)
    """
    try:
        link_service = LinkService(db)
        
        # For now, we'll just return all links
        # In a real app, you'd want to filter by the current user's permissions
        db_links = crud_link.get_all_links(db, skip=skip, limit=min(limit, 100))
        return [schemas.Link.from_db_model(link) for link in db_links]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving links.",
        ) from e

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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
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
        updated_link = link_service.update_link(
            link_id=link_id,
            update_data=link_in,
            user_id=current_user.id
        )
        
        if not updated_link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Link not found",
            )
            
        return schemas.Link.from_db_model(updated_link)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the link.",
        ) from e

@router.delete("/{link_id}", response_model=schemas.Link)
def delete_link_endpoint(
    link_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Delete a shortened link.
    
    - **link_id**: The UUID of the link to delete
    """
    db_link = crud_link.get_link(db, link_id=link_id)
    if not db_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
        )
    
    # In a real app, you'd check if the current user has permission to delete this link
    try:
        deleted_link = crud_link.delete_link(db=db, link_id=link_id)
        return schemas.Link.from_db_model(deleted_link)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the link.",
        ) from e
