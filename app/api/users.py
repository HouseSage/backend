from typing import List, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import schemas
from app.crud import crud_user
from app.db.database import SessionLocal
from app.core.security import get_current_active_user
from app.crud import crud_space

# Imports FastAPI, SQLAlchemy, app schemas, and CRUD utilities for user API endpoints

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(user: schemas.UserCreate, db: Session = Depends(get_db)) -> Any:
    
    db_user = crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    # Create the user
    new_user = crud_user.create_user(db=db, user=user)
    # Create a default space for the user
    from app.api.schemas import SpaceCreate
    space_in = SpaceCreate(name=f"{new_user.email.split('@')[0]}'s Space", description="Default space")
    default_space = crud_space.create_space_with_owner(db=db, space_in=space_in, owner_id=new_user.id)
    # Set the user's default_space_id
    new_user.default_space_id = default_space.id
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/", response_model=List[schemas.User])
def read_users_endpoint(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
) -> Any:
    
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/me", response_model=schemas.User)
def read_current_user_endpoint(current_user = Depends(get_current_active_user)):
    """
    Get the current authenticated user's information.
    """
    return current_user

@router.get("/{user_id}", response_model=schemas.User)
def read_user_endpoint(user_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)) -> Any:
    
    db_user = crud_user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=schemas.User)
def update_user_endpoint(
    user_id: UUID, user_in: schemas.UserUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)
) -> Any:
    
    db_user = crud_user.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if user_in.email:
        existing_user_with_email = crud_user.get_user_by_email(db, email=user_in.email)
        if existing_user_with_email and existing_user_with_email.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered by another user.",
            )
    updated_user = crud_user.update_user(db=db, db_user=db_user, user_in=user_in)
    return updated_user

@router.delete("/{user_id}", response_model=schemas.User)
def delete_user_endpoint(user_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)) -> Any:
    """
    Delete a user by ID.
    """
    db_user = crud_user.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    # Use the correct function name from crud_user
    deleted_user = crud_user.delete_user(db=db, user_id=user_id)
    if not deleted_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user",
        )
    return deleted_user
