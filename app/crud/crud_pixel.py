from uuid import UUID
from sqlalchemy.orm import Session

from app.models import models
from app.api import schemas 

def get_pixel(db: Session, pixel_id: UUID) -> models.Pixel | None:
    return db.query(models.Pixel).filter(models.Pixel.id == pixel_id).first()

def get_pixels(db: Session, skip: int = 0, limit: int = 100) -> list[models.Pixel]:
    return db.query(models.Pixel).offset(skip).limit(limit).all()

def get_pixels_by_space(db: Session, space_id: UUID, skip: int = 0, limit: int = 100) -> list[models.Pixel]:
    return (
        db.query(models.Pixel)
        .filter(models.Pixel.space_id == space_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_pixel(db: Session, pixel_in: schemas.PixelCreate, space_id: UUID) -> models.Pixel:
    db_pixel = models.Pixel(**pixel_in.model_dump(), space_id=space_id)
    db.add(db_pixel)
    db.commit()
    db.refresh(db_pixel)
    return db_pixel

def update_pixel(db: Session, db_pixel: models.Pixel, pixel_in: schemas.PixelUpdate) -> models.Pixel:
    update_data = pixel_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_pixel, key, value)
    db.add(db_pixel)
    db.commit()
    db.refresh(db_pixel)
    return db_pixel

def delete_pixel(db: Session, pixel_id: UUID) -> models.Pixel | None:
    db_pixel = get_pixel(db, pixel_id)
    if db_pixel:
        db.delete(db_pixel)
        db.commit()
    return db_pixel
