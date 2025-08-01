from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import Dict, Any

from app.models import models

# Returns a link by its UUID
def get_link(db: Session, link_id: UUID) -> models.Link | None:
    """
    Retrieve a link by its UUID.
    
    Args:
        db: Database session
        link_id: The UUID of the link to retrieve
        
    Returns:
        The Link object if found, None otherwise
    """
    return db.query(models.Link).filter(models.Link.id == link_id).first()




# Returns a link by its short code and domain
def get_link_by_domain_and_short_code(
    db: Session, short_code: str, domain_id: str
) -> models.Link | None:
    """
    Retrieve a link by its short code and domain.
    
    Args:
        db: Database session
        short_code: The short code of the link
        domain_id: Domain ID (required - all links must have a domain)
        
    Returns:
        The Link object if found, None otherwise
    """
    return db.query(models.Link).filter(
        models.Link.short_code == short_code,
        models.Link.domain_id == domain_id,
        models.Link.is_active == True  # Only return active links
    ).first()

# Returns all links for a given space
def get_links_by_space(
    db: Session, space_id: UUID, skip: int = 0, limit: int = 100
) -> list[models.Link]:
    
    return db.query(models.Link).filter(models.Link.space_id == space_id).offset(skip).limit(limit).all()

# Returns all links for a given domain
def get_links_by_domain(
    db: Session, domain_id: str, skip: int = 0, limit: int = 100
) -> list[models.Link]:
    
    return db.query(models.Link).filter(models.Link.domain_id == domain_id).offset(skip).limit(limit).all()

# Returns all links with pagination
def get_all_links(db: Session, skip: int = 0, limit: int = 100) -> list[models.Link]:
   
    return db.query(models.Link).offset(skip).limit(limit).all()

# Returns filtered links with pagination
def get_links_filtered(
    db: Session,
    space_id: UUID | None = None,
    domain_id: str | None = None,
    is_active: bool | None = None,
    skip: int = 0,
    limit: int = 100
) -> list[models.Link]:
    """
    Get links with optional filtering by space_id, domain_id, and is_active status.
    
    Args:
        db: Database session
        space_id: Filter by space ID (optional)
        domain_id: Filter by domain ID (optional)
        is_active: Filter by active status (optional)
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        
    Returns:
        List of Link objects matching the filters
    """
    query = db.query(models.Link)
    
    # Apply filters
    if space_id is not None:
        query = query.filter(models.Link.space_id == space_id)
    
    if domain_id is not None:
        query = query.filter(models.Link.domain_id == domain_id)
        
    if is_active is not None:
        query = query.filter(models.Link.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()

# Creates a new link
def create_link(db: Session, link: Dict[str, Any], space_id: UUID) -> models.Link:
    """
    Create a new shortened link with the provided data - Generic Link System.
    
    Args:
        db: Database session
        link: Link creation data dict (contains generic data field)
        space_id: Space ID for the link
        
    Returns:
        The created Link object
    """
    # Ensure domain_id is provided (should be guaranteed by schema, but double-check)
    domain_id = link.get('domain_id')
    if not domain_id:
        raise ValueError("domain_id is required for all links")
    
    # Prepare link data dictionary - store metadata + data field directly
    # No more divergence between API schema and database storage
    data_field = link.get('data', {})
    link_data = {
        "title": link.get('title'),
        "description": link.get('description'),
        "tags": link.get('tags', []),
        "created_at": datetime.utcnow().isoformat(),
        # Store the generic data field directly - contains type, URL(s), rules, etc.
        **data_field  # Flatten the data object into link_data
    }
    
    # Create the database record
    db_link = models.Link(
        space_id=space_id,
        domain_id=domain_id,  # Now required
        short_code=link.get('short_code'),
        is_active=True,
        link_data=link_data
    )
    
    # Handle pixel association if provided
    pixel_ids = link.get('pixel_ids', [])
    if pixel_ids:
        db_link.pixels = db.query(models.Pixel).filter(models.Pixel.id.in_(pixel_ids)).all()
    
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link

# Updates link details
def update_link(db: Session, db_link: models.Link, link_in: Dict[str, Any]) -> models.Link:
    """
    Update an existing link with new data - Generic Link System.
    
    Args:
        db: Database session
        db_link: The link object to update
        link_in: New link data dict (may include new data field)
        
    Returns:
        The updated Link object
    """
    update_data = link_in  # link_in is already a dict
    
    # Update basic fields
    if "is_active" in update_data and update_data["is_active"] is not None:
        db_link.is_active = update_data["is_active"]
    
    # Update metadata fields in link_data
    json_updated = False
    if "title" in update_data:
        db_link.link_data["title"] = update_data["title"]
        json_updated = True
    if "description" in update_data:
        db_link.link_data["description"] = update_data["description"]
        json_updated = True
    if "tags" in update_data:
        db_link.link_data["tags"] = update_data["tags"]
        json_updated = True
    
    # Update the generic data field if provided
    if "data" in update_data and update_data["data"] is not None:
        # Replace the entire data section with new data
        new_data = update_data["data"]
        if isinstance(new_data, dict):
            # Update all data fields
            for key, value in new_data.items():
                db_link.link_data[key] = value
        else:
            # It's a Pydantic model, dump it
            for key, value in new_data.model_dump().items():
                db_link.link_data[key] = value
        json_updated = True
    
    # Mark the JSON field as modified if we changed it
    if json_updated:
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(db_link, "link_data")
    
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link

# Click counting is handled by the event system - see app/api/events.py
# Individual click events are stored in the events table for accurate tracking
# To get click counts, query the events table: COUNT(*) WHERE event_type='click' AND link_id=?

# Deletes a link by its UUID
def delete_link(db: Session, link_id: UUID) -> models.Link | None:
  
    db_link = get_link(db, link_id=link_id)
    if db_link:
        db.delete(db_link)
        db.commit()
    return db_link
