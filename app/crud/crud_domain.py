import secrets
from uuid import UUID
from sqlalchemy.orm import Session
from app.models import models
from app.api import schemas

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
def create_domain(db: Session, domain: schemas.DomainCreate) -> models.Domain:
  
    verification_token = generate_verification_token()
    db_domain = models.Domain(
        domain=domain.domain,
        is_active=domain.is_active if domain.is_active is not None else True,
        space_id=domain.space_id,
        verified=domain.verified if domain.verified is not None else False,
        verification_token=verification_token
    )
    db.add(db_domain)
    db.commit()
    db.refresh(db_domain)
    return db_domain

# Updates domain details (is_active, verified)
def update_domain(db: Session, db_domain: models.Domain, domain_in: schemas.DomainUpdate) -> models.Domain:
    
    update_data = domain_in.model_dump(exclude_unset=True)

    if "is_active" in update_data and update_data["is_active"] is not None:
        db_domain.is_active = update_data["is_active"]
    
    if "verified" in update_data and update_data["verified"] is not None:
        db_domain.verified = update_data["verified"]
        if db_domain.verified:
            db_domain.verification_token = None

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
