from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import datetime


class SpaceBase(BaseModel):
    name: str
    description: Optional[str] = None

class SpaceCreate(SpaceBase):
    pass

class SpaceUpdate(SpaceBase):
    name: Optional[str] = None

class SpaceInDBBase(SpaceBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Space(SpaceInDB):
    pass


class PixelBase(BaseModel):
    name: str
    code: str
    type: str

class PixelCreate(PixelBase):
    space_id: UUID4

class PixelUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    type: Optional[str] = None

class PixelInDB(PixelBase):
    id: UUID4
    space_id: UUID4
    created_at: datetime

    class Config:
        orm_mode = True

class Pixel(PixelInDB):
    pass
