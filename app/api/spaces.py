from typing import List, Any
from uuid import UUID 

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import User as UserModel, SpaceUserRole as ModelSpaceUserRole, SpaceUser as SpaceUserModel 
from app.api import schemas 
from app.core.security import get_current_active_user
from app.crud import crud_space, crud_user 

# Initializes the API router for space endpoints
router = APIRouter()

# Utility/check functions for space membership and roles
def check_space_membership(db: Session, space_id: UUID, user_id: UUID) -> schemas.SpaceUser | None:
    space_user = crud_space.get_space_user(db, space_id=space_id, user_id=user_id)
    if not space_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this space")
    return schemas.SpaceUser.model_validate(space_user) 

def check_space_admin_or_owner(db: Session, space_id: UUID, user_id: UUID) -> schemas.SpaceUser:
    space_user = check_space_membership(db, space_id, user_id)
    if space_user.role not in [ModelSpaceUserRole.ADMIN.value, ModelSpaceUserRole.OWNER.value]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires ADMIN or OWNER role")
    return space_user

def check_space_owner(db: Session, space_id: UUID, user_id: UUID) -> schemas.SpaceUser:
    space_user = check_space_membership(db, space_id, user_id)
    if space_user.role != ModelSpaceUserRole.OWNER.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires OWNER role")
    return space_user

# Space Endpoints
@router.post("/", response_model=schemas.Space, status_code=status.HTTP_201_CREATED)
def create_space_endpoint(
    space_in: schemas.SpaceCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    # Convert schema to dict for CRUD layer
    space_dict = space_in.model_dump()
    return crud_space.create_space_with_owner(db=db, space_in=space_dict, owner_id=current_user.id)

@router.get("/", response_model=List[schemas.Space])
def list_spaces_for_current_user_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
   
    return crud_space.get_spaces_by_user(db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/{space_id}", response_model=schemas.Space)
def read_space_endpoint(
    space_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    
    check_space_membership(db, space_id=space_id, user_id=current_user.id)
    db_space = crud_space.get_space(db, space_id=space_id)
    if not db_space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Space not found")
    return db_space

@router.put("/{space_id}", response_model=schemas.Space)
def update_space_endpoint(
    space_id: UUID,
    space_in: schemas.SpaceUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
   
    db_space = crud_space.get_space(db, space_id=space_id)
    if not db_space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Space not found")
    check_space_admin_or_owner(db, space_id=space_id, user_id=current_user.id)
    return crud_space.update_space(db=db, db_space=db_space, space_in=space_in)

@router.delete("/{space_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_space_endpoint(
    space_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> None:
   
    db_space = crud_space.get_space(db, space_id=space_id)
    if not db_space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Space not found")
    check_space_owner(db, space_id=space_id, user_id=current_user.id)
    
    if current_user.default_space_id == space_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete your default space. Please change your default space before deleting.")

    # Remove all users from the space to avoid foreign key constraint errors
    space_users = crud_space.get_space_users_with_roles(db, space_id=space_id)
    for su in space_users:
        db.delete(su)
    db.commit()

    crud_space.delete_space(db, space_id=space_id)
    return None

# User-in-Space Endpoints
@router.get("/{space_id}/users", response_model=List[schemas.User])
def list_users_in_space_endpoint(
    space_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
  
    check_space_membership(db, space_id=space_id, user_id=current_user.id)
    users = crud_space.get_users_in_space(db, space_id=space_id, skip=skip, limit=limit)
    return users

@router.post("/{space_id}/users", response_model=schemas.SpaceUser, status_code=status.HTTP_201_CREATED)
def add_user_to_space_endpoint(
    space_id: UUID,
    space_user_in: schemas.SpaceUserCreateBody,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
   
    check_space_admin_or_owner(db, space_id=space_id, user_id=current_user.id)
    
    target_user = crud_user.get_user(db, user_id=space_user_in.user_id)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found")
        
    existing_space_user = crud_space.get_space_user(db, space_id=space_id, user_id=space_user_in.user_id)
    if existing_space_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already in space")

    if space_user_in.role == ModelSpaceUserRole.OWNER.value:
        check_space_owner(db, space_id=space_id, user_id=current_user.id)
        
    return crud_space.add_user_to_space(
        db, space_id=space_id, user_id=space_user_in.user_id, role=ModelSpaceUserRole(space_user_in.role.value)
    )

@router.put("/{space_id}/users/{user_id}", response_model=schemas.SpaceUser)
def update_user_role_in_space_endpoint(
    space_id: UUID,
    user_id: UUID, 
    role_in: schemas.SpaceUserUpdateRoleBody,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
   
    current_user_membership = check_space_admin_or_owner(db, space_id=space_id, user_id=current_user.id)
    
    target_space_user = crud_space.get_space_user(db, space_id=space_id, user_id=user_id)
    if not target_space_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found in this space")

    new_role = ModelSpaceUserRole(role_in.role.value)
    
    if current_user.id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change your own role via this endpoint.")

    if new_role == ModelSpaceUserRole.OWNER and current_user_membership.role != ModelSpaceUserRole.OWNER.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only an OWNER can assign the OWNER role.")

    if current_user_membership.role == ModelSpaceUserRole.ADMIN.value:
        if ModelSpaceUserRole(target_space_user.role) in [ModelSpaceUserRole.ADMIN, ModelSpaceUserRole.OWNER]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ADMINs cannot change role of other ADMINs or OWNERs.")
        if new_role in [ModelSpaceUserRole.ADMIN, ModelSpaceUserRole.OWNER]:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ADMINs cannot promote users to ADMIN or OWNER.")
             
    return crud_space.update_user_role_in_space(db, space_id=space_id, user_id=user_id, new_role=new_role)

@router.delete("/{space_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user_from_space_endpoint(
    space_id: UUID,
    user_id: UUID, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> None:
   
    current_user_membership = check_space_admin_or_owner(db, space_id=space_id, user_id=current_user.id)
    
    target_space_user_model = crud_space.get_space_user(db, space_id=space_id, user_id=user_id)
    if not target_space_user_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found in this space")

    target_user_role = ModelSpaceUserRole(target_space_user_model.role)

    if current_user.id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove yourself from a space via this endpoint. Consider a 'leave space' feature.")

    if current_user_membership.role == ModelSpaceUserRole.ADMIN.value:
        if target_user_role in [ModelSpaceUserRole.ADMIN, ModelSpaceUserRole.OWNER]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ADMINs cannot remove other ADMINs or OWNERs.")
            
    if target_user_role == ModelSpaceUserRole.OWNER:
        owners_in_space = db.query(SpaceUserModel).filter(
            SpaceUserModel.space_id == space_id,
            SpaceUserModel.role == ModelSpaceUserRole.OWNER.value
        ).count()
        if owners_in_space <= 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove the last OWNER of the space.")
            
    crud_space.remove_user_from_space(db, space_id=space_id, user_id=user_id)
    return None
