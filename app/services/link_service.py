"""
Service layer for link-related operations.
Handles business logic for link creation, updates, and management.
"""
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import base64

from sqlalchemy.orm import Session

from app.models import models
from app.crud import crud_link, crud_domain
from app.core.short_code import generate_short_code, is_valid_short_code, generate_unique_short_code
from app.core.link_utils import LinkEncoder
# QR code generation is now handled in the frontend
from app.core.config import settings
from app.api.schemas import LinkCreate, LinkUpdate

class LinkService:
    """Service for handling link-related operations."""
    
    def __init__(self, db: Session):
        """Initialize the service with a database session."""
        self.db = db
    
    def create_link(self, link_data: LinkCreate, user_id: UUID = None) -> models.Link:
        """
        Create a new shortened link.
        
        Args:
            link_data: Data for the new link
            user_id: Optional user ID creating the link
            
        Returns:
            The created Link object
            
        Raises:
            ValueError: If the short code is invalid or already in use
        """
        # Validate short code if provided
        if link_data.short_code and not is_valid_short_code(link_data.short_code):
            raise ValueError(
                f"Short code contains invalid characters. "
                f"Use only letters and numbers (A-Z, a-z, 0-9)."
            )
        
        # Check if short code is already in use
        existing_link = crud_link.get_link_by_domain_and_short_code(
            self.db, link_data.short_code, link_data.domain_id
        )
        if existing_link:
            raise ValueError(f"Short code '{link_data.short_code}' is already in use")
        
        # If no short code provided, generate one
        if not link_data.short_code:
            link_data.short_code = generate_unique_short_code(
                self.db, length=settings.SHORT_CODE_LENGTH
            )
            if not link_data.short_code:
                raise ValueError("Failed to generate a unique short code. Please try again.")
        
        # If domain is provided, verify it exists and is verified
        if link_data.domain_id:
            domain = crud_domain.get_domain(self.db, link_data.domain_id)
            if not domain:
                raise ValueError(f"Domain '{link_data.domain_id}' not found")
            if not domain.verified:
                raise ValueError(f"Domain '{link_data.domain_id}' is not verified")
        
        # Create the link
        db_link = crud_link.create_link(self.db, link_data)
        
        # Generate QR code if requested
        if link_data.generate_qr:
            try:
                # Get the full short URL
                base_url = f"{settings.DEFAULT_DOMAIN}/"
                if link_data.domain_id:
                    base_url = f"https://{link_data.domain_id}/"
                short_url = f"{base_url}{db_link.short_code}"
                
                # Store the short URL for QR code generation in the frontend
                link_data = db_link.link_data or {}
                link_data['qr_code_url'] = short_url
                
                # Update the link with QR code data
                update_data = LinkUpdate(link_data=link_data)
                db_link = crud_link.update_link(
                    self.db, 
                    db_link=db_link, 
                    link_in=update_data
                )
            except Exception as e:
                # Log the error but don't fail the request
                print(f"Failed to generate QR code: {str(e)}")
        
        return db_link
    
    def update_link(
        self, 
        link_id: UUID, 
        update_data: LinkUpdate,
        user_id: UUID = None
    ) -> Optional[models.Link]:
        """
        Update an existing link.
        
        Args:
            link_id: ID of the link to update
            update_data: Data to update
            user_id: Optional user ID making the update
            
        Returns:
            The updated Link object, or None if not found
            
        Raises:
            ValueError: If the update would make the link invalid
        """
        db_link = crud_link.get_link(self.db, link_id=link_id)
        if not db_link:
            return None
        
        # If updating short code, validate it
        if update_data.short_code and update_data.short_code != db_link.short_code:
            if not is_valid_short_code(update_data.short_code):
                raise ValueError(
                    "Short code contains invalid characters. "
                    "Use only letters and numbers (A-Z, a-z, 0-9)."
                )
            
            # Check if new short code is already in use
            existing = crud_link.get_link_by_domain_and_short_code(
                self.db, update_data.short_code, db_link.domain_id
            )
            if existing and existing.id != link_id:
                raise ValueError(f"Short code '{update_data.short_code}' is already in use")
        
        # Update the link
        return crud_link.update_link(self.db, db_link=db_link, link_in=update_data)
    
    def get_link_by_short_code(
        self, 
        short_code: str, 
        domain: str = None,
        increment_clicks: bool = False
    ) -> Optional[models.Link]:
        """
        Get a link by its short code and optional domain.
        
        Args:
            short_code: The short code of the link
            domain: Optional domain name
            increment_clicks: Whether to increment the click count
            
        Returns:
            The Link object if found, None otherwise
        """
        db_link = crud_link.get_link_by_domain_and_short_code(
            self.db, short_code, domain
        )
        
        if db_link and increment_clicks:
            db_link = crud_link.increment_link_clicks(self.db, db_link.id)
            
        return db_link
    
    def get_link_info(self, link_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a link.
        
        Args:
            link_id: ID of the link
            
        Returns:
            Dictionary with link information, or None if not found
        """
        db_link = crud_link.get_link(self.db, link_id=link_id)
        if not db_link:
            return None
            
        # Get click statistics
        click_count = db_link.link_data.get("clicks", 0)
        
        # Get QR code if it exists
        qr_code = None
        if 'qr_code' in db_link.link_data:
            qr_code = db_link.link_data['qr_code']
        
        # Get the full short URL for QR code generation if needed
        short_url = None
        if db_link.domain_id:
            short_url = f"https://{db_link.domain_id}/{db_link.short_code}"
        else:
            short_url = f"{settings.DEFAULT_DOMAIN}/{db_link.short_code}"
        
        return {
            "id": str(db_link.id),
            "short_code": db_link.short_code,
            "domain": db_link.domain_id,
            "original_url": db_link.link_data.get("url"),
            "title": db_link.link_data.get("title"),
            "description": db_link.link_data.get("description"),
            "tags": db_link.link_data.get("tags", []),
            "is_active": db_link.is_active,
            "has_password": bool(db_link.link_data.get("password")),
            "click_count": click_count,
            "created_at": db_link.created_at.isoformat(),
            "updated_at": db_link.updated_at.isoformat() if db_link.updated_at else None,
            "qr_code": qr_code,
            "short_url": short_url
        }
