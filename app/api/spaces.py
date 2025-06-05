from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Space, SpaceUser, SpaceUserRole, User
from app.api.schemas import Space, SpaceCreate, SpaceUpdate
from app.core.security import get_current_active_user

router = APIRouter()

@router.post("/", response_model=Space)
def create_space(
    space_in: SpaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new space"""
    db_space = Space(**space_in.dict())
    db.add(db_space)
    db.commit()
    db.refresh(db_space)
    
  
    space_user = SpaceUser(
        space_id=db_space.id,
        user_id=current_user.id,
        role=SpaceUserRole.OWNER
    )
    db.add(space_user)
    
   
    if not current_user.default_space_id:
        current_user.default_space_id = db_space.id
    
    db.commit()
    return db_space

@router.get("/", response_model=List[Space])
def list_spaces(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
   
    spaces = db.query(Space).join(SpaceUser).filter(SpaceUser.user_id == current_user.id).offset(skip).limit(limit).all()
    return spaces

@router.get("/{space_id}", response_model=Space)
def read_space(
    space_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
   
    space = db.query(Space).filter(Space.id == space_id).first()
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
        
 
    space_user = db.query(SpaceUser).filter(
        SpaceUser.space_id == space_id,
        SpaceUser.user_id == current_user.id
    ).first()
    
    if not space_user:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    return space

@router.put("/{space_id}", response_model=Space)
def update_space(
    space_id: UUID,
    space_in: SpaceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a space"""
    db_space = db.query(Space).filter(Space.id == space_id).first()
    if not db_space:
        raise HTTPException(status_code=404, detail="Space not found")
    
  
    space_user = db.query(SpaceUser).filter(
        SpaceUser.space_id == space_id,
        SpaceUser.user_id == current_user.id,
        SpaceUser.role.in_([SpaceUserRole.ADMIN, SpaceUserRole.OWNER])
    ).first()
    
    if not space_user:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_data = space_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_space, field, value)
    
    db.add(db_space)
    db.commit()
    db.refresh(db_space)
    return db_space

@router.delete("/{space_id}", response_model=Space)
def delete_space(
    space_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a space"""
    db_space = db.query(Space).filter(Space.id == space_id).first()
    if not db_space:
        raise HTTPException(status_code=404, detail="Space not found")
    
   
    space_user = db.query(SpaceUser).filter(
        SpaceUser.space_id == space_id,
        SpaceUser.user_id == current_user.id,
        SpaceUser.role == SpaceUserRole.OWNER
    ).first()
    
    if not space_user:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
   
    db.delete(db_space)
    db.commit()
    return db_space
