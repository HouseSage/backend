from typing import List, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import schemas
from app.crud import crud_user
from app.db.database import SessionLocal

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
    return crud_user.create_user(db=db, user=user)

@router.get("/", response_model=List[schemas.User])
def read_users_endpoint(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> Any:
    
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=schemas.User)
def read_user_endpoint(user_id: UUID, db: Session = Depends(get_db)) -> Any:
    
    db_user = crud_user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=schemas.User)
def update_user_endpoint(
    user_id: UUID, user_in: schemas.UserUpdate, db: Session = Depends(get_db)
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
def delete_user_endpoint(user_id: UUID, db: Session = Depends(get_db)) -> Any:
   
    db_user = crud_user.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    deleted_user_response = crud_user.delete_user(db=db, user_id=user_id)
    return deleted_user_response
