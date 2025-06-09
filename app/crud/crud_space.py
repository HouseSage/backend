from uuid import UUID
from sqlalchemy.orm import Session

from app.models import models
from app.api import schemas
from app.models.models import SpaceUserRole


# Returns a space by its UUID
def get_space(db: Session, space_id: UUID) -> models.Space | None:
    return db.query(models.Space).filter(models.Space.id == space_id).first()

# Returns all spaces a user is a member of
def get_spaces_by_user(db: Session, user_id: UUID, skip: int = 0, limit: int = 100) -> list[models.Space]:
   
    return (
        db.query(models.Space)
        .join(models.SpaceUser, models.Space.id == models.SpaceUser.space_id)
        .filter(models.SpaceUser.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

# Creates a new space and assigns the owner
def create_space_with_owner(db: Session, space_in: schemas.SpaceCreate, owner_id: UUID) -> models.Space:
    
    db_space = models.Space(name=space_in.name, description=space_in.description)
    db.add(db_space)
    db.commit()

    add_user_to_space(db, space_id=db_space.id, user_id=owner_id, role=SpaceUserRole.OWNER)
    
    user = db.query(models.User).filter(models.User.id == owner_id).first()
    if user and not user.default_space_id:
        user.default_space_id = db_space.id
        db.add(user)
        db.commit() 

    db.refresh(db_space)
    return db_space

# Updates space details
def update_space(db: Session, db_space: models.Space, space_in: schemas.SpaceUpdate) -> models.Space:
    update_data = space_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_space, key, value)
    db.add(db_space)
    db.commit()
    db.refresh(db_space)
    return db_space

# Deletes a space by its UUID
def delete_space(db: Session, space_id: UUID) -> models.Space | None:
   
    db_space = get_space(db, space_id)
    if db_space:
        db.delete(db_space)
        db.commit()
    return db_space


# Adds a user to a space with a specific role
def add_user_to_space(
    db: Session, space_id: UUID, user_id: UUID, role: SpaceUserRole = SpaceUserRole.MEMBER
) -> models.SpaceUser:
    db_space_user = models.SpaceUser(space_id=space_id, user_id=user_id, role=role.value)
    db.add(db_space_user)
    db.commit()
    db.refresh(db_space_user)
    return db_space_user

# Returns the SpaceUser association for a user and space
def get_space_user(db: Session, space_id: UUID, user_id: UUID) -> models.SpaceUser | None:
    return (
        db.query(models.SpaceUser)
        .filter(models.SpaceUser.space_id == space_id, models.SpaceUser.user_id == user_id)
        .first()
    )

# Returns all users in a space
def get_users_in_space(db: Session, space_id: UUID, skip: int = 0, limit: int = 100) -> list[models.User]:
    
    return (
        db.query(models.User)
        .join(models.SpaceUser, models.User.id == models.SpaceUser.user_id)
        .filter(models.SpaceUser.space_id == space_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    
# Returns all SpaceUser associations for a space
def get_space_users_with_roles(db: Session, space_id: UUID, skip: int = 0, limit: int = 100) -> list[models.SpaceUser]:
    
    return (
        db.query(models.SpaceUser)
        .filter(models.SpaceUser.space_id == space_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

# Updates a user's role in a space
def update_user_role_in_space(
    db: Session, space_id: UUID, user_id: UUID, new_role: SpaceUserRole
) -> models.SpaceUser | None:
    db_space_user = get_space_user(db, space_id, user_id)
    if db_space_user:
        db_space_user.role = new_role.value
        db.add(db_space_user)
        db.commit()
        db.refresh(db_space_user)
    return db_space_user

# Removes a user from a space
def remove_user_from_space(db: Session, space_id: UUID, user_id: UUID) -> models.SpaceUser | None:
    db_space_user = get_space_user(db, space_id, user_id)
    if db_space_user:
        db.delete(db_space_user)
        db.commit()
    return db_space_user
