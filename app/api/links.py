"""
Link API endpoints for creating, reading, updating, and deleting shortened links.
"""
from typing import List, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import base64

from app.api import schemas
from app.crud import crud_link, crud_domain
from app.db.database import SessionLocal
from app.services import LinkService
from app.core.qr_code import get_qr_url

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
    link: schemas.LinkCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: UUID | None = Depends(get_current_user)
) -> Any:
    """
    Create a new shortened link.
    
    - **url**: The destination URL to shorten (required)
    - **short_code**: Custom short code (optional, auto-generated if not provided)
    - **domain_id**: Custom domain ID (optional, uses default domain if not provided)
    - **title**: Title for the link (optional)
    - **description**: Description for the link (optional)
    - **tags**: List of tags for categorization (optional)
    - **password**: Password to protect the link (optional)
    """
    try:
        link_service = LinkService(db)
        db_link = link_service.create_link(link_data=link, user_id=current_user)
        return db_link
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
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
    current_user: UUID | None = Depends(get_current_user)
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
    current_user: UUID | None = Depends(get_current_user)
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
    current_user: UUID | None = Depends(get_current_user)
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
            user_id=current_user
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

@router.get(
    "/{link_id}/qr-code",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {"image/png": {}},
            "description": "QR code image",
async def get_link_qr_code(
    link_id: UUID,
    db: Session = Depends(get_db),
    current_user: UUID | None = Depends(get_current_user)
):
    """
    Get the URL for generating a QR code.
    The actual QR code generation should be handled in the frontend.
    
    - **link_id**: The UUID of the link
    
    Returns:
        A JSON object with the URL to be used for QR code generation
    """
    try:
        # Get the link
        db_link = crud_link.get_link(db, link_id=link_id)
        if not db_link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Link not found"
            )
        
        # Check if user has permission to view this link
        if db_link.user_id and db_link.user_id != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this link"
            )
        
        # Get the full URL
        base_url = f"{settings.DEFAULT_DOMAIN}/"
        if db_link.domain_id:
            base_url = f"https://{db_link.domain_id}/"
        short_url = f"{base_url}{db_link.short_code}"
        
        # Return the URL for QR code generation
        return get_qr_url(short_url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate QR code",
        ) from e


@router.delete("/{link_id}", response_model=schemas.Link)
def delete_link_endpoint(
    link_id: UUID,
    db: Session = Depends(get_db),
    current_user: UUID | None = Depends(get_current_user)
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
