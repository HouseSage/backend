from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Pixel, SpaceUser, SpaceUserRole, User
from app.api.schemas import Pixel, PixelCreate, PixelUpdate
from app.core.security import get_current_active_user

router = APIRouter()

@router.post("/", response_model=Pixel)
def create_pixel(
    pixel_in: PixelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    
    space_user = db.query(SpaceUser).filter(
        SpaceUser.space_id == pixel_in.space_id,
        SpaceUser.user_id == current_user.id,
        SpaceUser.role.in_([SpaceUserRole.ADMIN, SpaceUserRole.OWNER])
    ).first()
    
    if not space_user:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_pixel = Pixel(**pixel_in.dict())
    db.add(db_pixel)
    db.commit()
    db.refresh(db_pixel)
    return db_pixel

@router.get("/", response_model=List[Pixel])
def list_pixels(
    space_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    
    space_user = db.query(SpaceUser).filter(
        SpaceUser.space_id == space_id,
        SpaceUser.user_id == current_user.id
    ).first()
    
    if not space_user:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    pixels = db.query(Pixel).filter(
        Pixel.space_id == space_id
    ).offset(skip).limit(limit).all()
    
    return pixels

@router.get("/{pixel_id}", response_model=Pixel)
def read_pixel(
    pixel_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
   
    pixel = db.query(Pixel).filter(Pixel.id == pixel_id).first()
    if not pixel:
        raise HTTPException(status_code=404, detail="Pixel not found")
    
  
    space_user = db.query(SpaceUser).filter(
        SpaceUser.space_id == pixel.space_id,
        SpaceUser.user_id == current_user.id
    ).first()
    
    if not space_user:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    return pixel

@router.put("/{pixel_id}", response_model=Pixel)
def update_pixel(
    pixel_id: UUID,
    pixel_in: PixelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
   
    db_pixel = db.query(Pixel).filter(Pixel.id == pixel_id).first()
    if not db_pixel:
        raise HTTPException(status_code=404, detail="Pixel not found")
    
   
    space_user = db.query(SpaceUser).filter(
        SpaceUser.space_id == db_pixel.space_id,
        SpaceUser.user_id == current_user.id,
        SpaceUser.role.in_([SpaceUserRole.ADMIN, SpaceUserRole.OWNER])
    ).first()
    
    if not space_user:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_data = pixel_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_pixel, field, value)
    
    db.add(db_pixel)
    db.commit()
    db.refresh(db_pixel)
    return db_pixel

@router.delete("/{pixel_id}", response_model=Pixel)
def delete_pixel(
    pixel_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
  
    db_pixel = db.query(Pixel).filter(Pixel.id == pixel_id).first()
    if not db_pixel:
        raise HTTPException(status_code=404, detail="Pixel not found")
    
   
    space_user = db.query(SpaceUser).filter(
        SpaceUser.space_id == db_pixel.space_id,
        SpaceUser.user_id == current_user.id,
        SpaceUser.role.in_([SpaceUserRole.ADMIN, SpaceUserRole.OWNER])
    ).first()
    
    if not space_user:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(db_pixel)
    db.commit()
    return db_pixel
