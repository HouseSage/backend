import secrets
from uuid import UUID
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models import models

# Generates a secure random verification token
def generate_verification_token(length: int = 32) -> str:
    
    return secrets.token_urlsafe(length)

# Returns a domain by its name
def get_domain(db: Session, domain_name: str) -> models.Domain | None:
   
    return db.query(models.Domain).filter(models.Domain.domain == domain_name).first()

# Returns all domains for a given space
def get_domains_by_space(db: Session, space_id: UUID, skip: int = 0, limit: int = 100) -> list[models.Domain]:
   
    return db.query(models.Domain).filter(models.Domain.space_id == space_id).offset(skip).limit(limit).all()

# Returns all domains with pagination
def get_all_domains(db: Session, skip: int = 0, limit: int = 100) -> list[models.Domain]:
   
    return db.query(models.Domain).offset(skip).limit(limit).all()

# Creates a new domain with a verification token
def create_domain(db: Session, domain: Dict[str, Any]) -> models.Domain:
    verification_token = generate_verification_token()
    db_domain = models.Domain(
        domain=domain.get('domain'),
        is_active=True,  # Always set by backend
        space_id=domain.get('space_id'),
        verified=False,  # Always set by backend
        verification_token=verification_token
    )
    db.add(db_domain)
    db.commit()
    db.refresh(db_domain)
    return db_domain



# Deletes a domain by its name
def delete_domain(db: Session, domain_name: str) -> models.Domain | None:
    
    db_domain = get_domain(db, domain_name=domain_name)
    if db_domain:
        db.delete(db_domain)
        db.commit()
    return db_domain
