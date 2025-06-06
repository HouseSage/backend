from typing import List, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import User as UserModel, SpaceUserRole as ModelSpaceUserRole
from app.api import schemas
from app.core.security import get_current_active_user
from app.crud import crud_pixel, crud_space 

router = APIRouter()


def ensure_space_membership(db: Session, space_id: UUID, user_id: UUID) -> None:
   
    space = crud_space.get_space(db, space_id=space_id)
    if not space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Space with id {space_id} not found")
    
  
    space_user = crud_space.get_space_user(db, space_id=space_id, user_id=user_id)
    if not space_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a member of the specified space.",
        )

def ensure_space_admin_or_owner(db: Session, space_id: UUID, user_id: UUID) -> None:
  
    space = crud_space.get_space(db, space_id=space_id)
    if not space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Space with id {space_id} not found")

   
    space_user = crud_space.get_space_user(db, space_id=space_id, user_id=user_id)
    if not space_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a member of the specified space.",
        )
    if space_user.role not in [ModelSpaceUserRole.ADMIN.value, ModelSpaceUserRole.OWNER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User requires ADMIN or OWNER role in this space for this operation.",
        )

@router.post("/", response_model=schemas.Pixel, status_code=status.HTTP_201_CREATED)
def create_pixel_endpoint(
    pixel_in: schemas.PixelCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    
    ensure_space_admin_or_owner(db, space_id=pixel_in.space_id, user_id=current_user.id)
    
    return crud_pixel.create_pixel(db=db, pixel_in=pixel_in, space_id=pixel_in.space_id)

@router.get("/", response_model=List[schemas.Pixel])
def list_pixels_in_space_endpoint(
    space_id: UUID = Query(..., description="The ID of the space to list pixels from"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    
    ensure_space_membership(db, space_id=space_id, user_id=current_user.id)
    return crud_pixel.get_pixels_by_space(db, space_id=space_id, skip=skip, limit=limit)

@router.get("/{pixel_id}", response_model=schemas.Pixel)
def read_pixel_endpoint(
    pixel_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
   
    db_pixel = crud_pixel.get_pixel(db, pixel_id=pixel_id)
    if not db_pixel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pixel not found")
    
    ensure_space_membership(db, space_id=db_pixel.space_id, user_id=current_user.id)
    return db_pixel

@router.put("/{pixel_id}", response_model=schemas.Pixel)
def update_pixel_endpoint(
    pixel_id: UUID,
    pixel_in: schemas.PixelUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
  
    db_pixel = crud_pixel.get_pixel(db, pixel_id=pixel_id)
    if not db_pixel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pixel not found")
    
    ensure_space_admin_or_owner(db, space_id=db_pixel.space_id, user_id=current_user.id)
    return crud_pixel.update_pixel(db=db, db_pixel=db_pixel, pixel_in=pixel_in)

@router.delete("/{pixel_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pixel_endpoint(
    pixel_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> None:
   
    db_pixel = crud_pixel.get_pixel(db, pixel_id=pixel_id)
    if not db_pixel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pixel not found")
        
    ensure_space_admin_or_owner(db, space_id=db_pixel.space_id, user_id=current_user.id)
    
    crud_pixel.delete_pixel(db, pixel_id=pixel_id)
    return None
