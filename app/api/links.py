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
    link: dict = Body(...),
    request: Request = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Create a new shortened link.
    Allows minimal payload: {"url": "https://..."} or {"space_id": ..., "url": ...}
    """
    try:
        required_fields = {"space_id", "short_code", "link_data"}
        if not required_fields.issubset(link.keys()):
            from app.models.models import User, Space
            from app.crud import crud_space
            from app.api.schemas import SpaceCreate
            
            user_obj = current_user if current_user else None
            
            # Use provided space_id or user's default
            space_id = link.get("space_id")
            if not space_id:
                if user_obj and user_obj.default_space_id:
                    space_id = str(user_obj.default_space_id)
                else:
                    # If no user or no default space, create or use a default public space
                    default_space = db.query(Space).filter(Space.name == "Default").first()
                    if not default_space:
                        # Create a default space
                        default_space = Space(
                            name="Default",
                            description="Default space for links without specific space"
                        )
                        db.add(default_space)
                        db.commit()
                        db.refresh(default_space)
                    space_id = str(default_space.id)
            
            # Generate short_code if missing
            import random, string
            short_code = link.get("short_code") or ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            # Wrap url in link_data if not present
            link_data = link.get("link_data") or {"url": link.get("url")}
            # Build the full payload
            link_payload = {
                "space_id": space_id,
                "short_code": short_code,
                "link_data": link_data,
                "url": link_data.get("url"),
                "is_active": link.get("is_active", True),
                "domain_id": link.get("domain_id"),
                "generate_qr": link.get("generate_qr", False),
                "password": link.get("password"),
                "title": link.get("title"),
                "description": link.get("description"),
                "tags": link.get("tags"),
            }
            link_obj = LinkCreate(**{k: v for k, v in link_payload.items() if v is not None})
            link_service = LinkService(db)
            db_link = link_service.create_link(link_data=link_obj, user_id=current_user.id)
            return db_link
        # Otherwise, use the existing logic
        link_obj = LinkCreate(**link)
        link_service = LinkService(db)
        db_link = link_service.create_link(link_data=link_obj, user_id=current_user.id)
        return db_link
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
        links = crud_link.get_all_links(db, skip=skip, limit=min(limit, 100))
        return links
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
    return db_link

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
            
        return updated_link
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
        return deleted_link
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the link.",
        ) from e
