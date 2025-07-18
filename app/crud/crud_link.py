from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from app.models import models
from app.api import schemas

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


def get_link_by_short_code(db: Session, short_code: str) -> models.Link | None:
    """
    Retrieve a link by its short code (without domain).
    
    Args:
        db: Database session
        short_code: The short code of the link
        
    Returns:
        The Link object if found, None otherwise
    """
    return db.query(models.Link).filter(
        models.Link.short_code == short_code,
        models.Link.domain_id.is_(None)  # Only return links without a domain
    ).first()

# Returns a link by its short code and domain
def get_link_by_domain_and_short_code(
    db: Session, short_code: str, domain_id: str | None
) -> models.Link | None:
    """
    Retrieve a link by its short code and optional domain.
    
    Args:
        db: Database session
        short_code: The short code of the link
        domain_id: Optional domain ID. If None, only links without a domain are returned.
        
    Returns:
        The Link object if found, None otherwise
    """
    query = db.query(models.Link).filter(
        models.Link.short_code == short_code,
        models.Link.is_active == True  # Only return active links
    )
    
    if domain_id is None:
        query = query.filter(models.Link.domain_id.is_(None))
    else:
        query = query.filter(models.Link.domain_id == domain_id)
    
    return query.first()

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

# Creates a new link
def create_link(db: Session, link: schemas.LinkCreate) -> models.Link:
    """
    Create a new shortened link with the provided data.
    
    Args:
        db: Database session
        link: Link creation data
        
    Returns:
        The created Link object
    """
    # Prepare link data dictionary
    link_data = {
        "url": link.url,
        "title": link.title,
        "description": link.description,
        "tags": link.tags or [],
        "password": link.password,
        "created_at": datetime.utcnow().isoformat(),
        "clicks": 0,
        "is_active": link.is_active if link.is_active is not None else True
    }
    
    # Create the database record
    db_link = models.Link(
        space_id=link.space_id,
        domain_id=link.domain_id,
        short_code=link.short_code,
        is_active=link.is_active if link.is_active is not None else True,
        link_data=link_data
    )
    # Handle pixel association
    if getattr(link, 'pixel_ids', None):
        db_link.pixels = db.query(models.Pixel).filter(models.Pixel.id.in_(link.pixel_ids)).all()
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link

# Updates link details
def update_link(db: Session, db_link: models.Link, link_in: schemas.LinkUpdate) -> models.Link:
    """
    Update an existing link with new data.
    
    Args:
        db: Database session
        db_link: The link object to update
        link_in: New link data
        
    Returns:
        The updated Link object
    """
    update_data = link_in.model_dump(exclude_unset=True)
    
    # Update basic fields
    if "is_active" in update_data and update_data["is_active"] is not None:
        db_link.is_active = update_data["is_active"]
    
    # Update link data fields
    if "url" in update_data:
        db_link.link_data["url"] = update_data["url"]
    if "title" in update_data:
        db_link.link_data["title"] = update_data["title"]
    if "description" in update_data:
        db_link.link_data["description"] = update_data["description"]
    if "tags" in update_data:
        db_link.link_data["tags"] = update_data["tags"]
    if "password" in update_data:
        db_link.link_data["password"] = update_data["password"]
    
    # Update pixel association
    if 'pixel_ids' in update_data and update_data['pixel_ids'] is not None:
        db_link.pixels = db.query(models.Pixel).filter(models.Pixel.id.in_(update_data['pixel_ids'])).all()
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link

def increment_link_clicks(db: Session, link_id: UUID) -> models.Link:
    """
    Increment the click count for a link.
    
    Args:
        db: Database session
        link_id: ID of the link to update
        
    Returns:
        The updated Link object, or None if not found
    """
    db_link = get_link(db, link_id=link_id)
    if not db_link:
        return None
        
    # Initialize clicks if not exists
    if "clicks" not in db_link.link_data:
        db_link.link_data["clicks"] = 0
    
    # Increment click count
    db_link.link_data["clicks"] = db_link.link_data.get("clicks", 0) + 1
    
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link

# Deletes a link by its UUID
def delete_link(db: Session, link_id: UUID) -> models.Link | None:
  
    db_link = get_link(db, link_id=link_id)
    if db_link:
        db.delete(db_link)
        db.commit()
    return db_link
