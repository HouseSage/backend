from pydantic import BaseModel, UUID4, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum as PyEnum


# Space Schemas
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


# Pixel Schemas
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


# User Schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    default_space_id: Optional[UUID4] = None

class UserInDBBase(UserBase):
    id: UUID4
    default_space_id: Optional[UUID4] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class User(UserInDBBase):
    pass


# Domain Schemas
class DomainBase(BaseModel):
    domain: str
    is_active: Optional[bool] = True
    space_id: UUID4
    verified: Optional[bool] = False

class DomainCreate(DomainBase):
    pass

class DomainUpdate(BaseModel):
    is_active: Optional[bool] = None
    verified: Optional[bool] = None

class DomainInDBBase(DomainBase):
    created_at: datetime
    verification_token: Optional[str] = None

    class Config:
        orm_mode = True

class Domain(DomainInDBBase):
    pass


# Link Schemas
class LinkBase(BaseModel):
    space_id: UUID4
    domain_id: Optional[str] = None
    short_code: str
    is_active: Optional[bool] = True
    link_data: dict

class LinkCreate(LinkBase):
    pass

class LinkUpdate(BaseModel):
    is_active: Optional[bool] = None
    link_data: Optional[dict] = None

class LinkInDBBase(LinkBase):
    id: UUID4
    created_at: datetime

    class Config:
        orm_mode = True

class Link(LinkInDBBase):
    pass


# Event Schemas
class EventBase(BaseModel):
    link_id: UUID4
    type: str
    event_data: dict

class EventCreate(EventBase):
    pass

class EventInDBBase(EventBase):
    id: UUID4
    created_at: datetime

    class Config:
        orm_mode = True

class Event(EventInDBBase):
    pass


# SpaceUser Schemas
class PySpaceUserRole(str, PyEnum):
    OWNER = ModelSpaceUserRole.OWNER.value
    ADMIN = ModelSpaceUserRole.ADMIN.value
    MEMBER = ModelSpaceUserRole.MEMBER.value
    VIEWER = ModelSpaceUserRole.VIEWER.value

class SpaceUserCreateBody(BaseModel):
    user_id: UUID4
    role: PySpaceUserRole = PySpaceUserRole.MEMBER

class SpaceUserUpdateRoleBody(BaseModel):
    role: PySpaceUserRole

class SpaceUser(BaseModel):
    user_id: UUID4
    space_id: UUID4
    role: PySpaceUserRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)




