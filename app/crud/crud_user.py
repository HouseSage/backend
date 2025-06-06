from uuid import UUID
from sqlalchemy.orm import Session
from app.models import models
from app.api import schemas 
from app.core.security import get_password_hash

def get_user(db: Session, user_id: UUID):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: models.User, user_in: schemas.UserUpdate):
    user_data = user_in.model_dump(exclude_unset=True)
    
    if "password" in user_data and user_data["password"]:
        hashed_password = get_password_hash(user_data["password"])
        db_user.password_hash = hashed_password
    
    if "email" in user_data and user_data["email"]:
        db_user.email = user_data["email"]
        
    if "default_space_id" in user_data:
        db_user.default_space_id = user_data["default_space_id"]
        
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: UUID):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user
