from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import models
from app.api import schemas

def get_link(db: Session, link_id: UUID) -> models.Link | None:
    
    return db.query(models.Link).filter(models.Link.id == link_id).first()

def get_link_by_domain_and_short_code(
    db: Session, short_code: str, domain_id: str | None
) -> models.Link | None:
    
    if domain_id is None:
        return db.query(models.Link).filter(
            and_(models.Link.short_code == short_code, models.Link.domain_id.is_(None))
        ).first()
    else:
        return db.query(models.Link).filter(
            and_(models.Link.short_code == short_code, models.Link.domain_id == domain_id)
        ).first()

def get_links_by_space(
    db: Session, space_id: UUID, skip: int = 0, limit: int = 100
) -> list[models.Link]:
    
    return db.query(models.Link).filter(models.Link.space_id == space_id).offset(skip).limit(limit).all()

def get_links_by_domain(
    db: Session, domain_id: str, skip: int = 0, limit: int = 100
) -> list[models.Link]:
    
    return db.query(models.Link).filter(models.Link.domain_id == domain_id).offset(skip).limit(limit).all()

def get_all_links(db: Session, skip: int = 0, limit: int = 100) -> list[models.Link]:
   
    return db.query(models.Link).offset(skip).limit(limit).all()

def create_link(db: Session, link: schemas.LinkCreate) -> models.Link:
    
    db_link = models.Link(
        space_id=link.space_id,
        domain_id=link.domain_id,  
        short_code=link.short_code,
        is_active=link.is_active if link.is_active is not None else True,
        link_data=link.link_data  
    )
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link

def update_link(db: Session, db_link: models.Link, link_in: schemas.LinkUpdate) -> models.Link:

    update_data = link_in.model_dump(exclude_unset=True)

    if "is_active" in update_data and update_data["is_active"] is not None:
        db_link.is_active = update_data["is_active"]
    
    if "link_data" in update_data and update_data["link_data"] is not None:
        db_link.link_data = update_data["link_data"]
        
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link

def delete_link(db: Session, link_id: UUID) -> models.Link | None:
  
    db_link = get_link(db, link_id=link_id)
    if db_link:
        db.delete(db_link)
        db.commit()
    return db_link
