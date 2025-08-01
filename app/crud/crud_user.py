from uuid import UUID
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models import models
from app.core.security import get_password_hash

# Returns a user by their UUID
def get_user(db: Session, user_id: UUID):
    return db.query(models.User).filter(models.User.id == user_id).first()

# Returns a user by their email address
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# Returns a list of users with pagination
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

# Creates a new user with hashed password
def create_user(db: Session, user: Dict[str, Any]):
    hashed_password = get_password_hash(user.get('password'))
    db_user = models.User(
        email=user.get('email'),
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Updates user details (email, password, default space)
def update_user(db: Session, db_user: models.User, user_in: Dict[str, Any]):
    user_data = user_in  # user_in is already a dict
    
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

# Deletes a user by their UUID
def delete_user(db: Session, user_id: UUID):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user
