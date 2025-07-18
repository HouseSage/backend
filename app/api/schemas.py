import re
from pydantic import BaseModel, UUID4, EmailStr, Field, ConfigDict, field_validator, constr
from pydantic_core import PydanticCustomError
from app.core.exceptions import ValidationException
from typing import Optional, List
from datetime import datetime
from enum import Enum as PyEnum
from uuid import UUID

from app.core.config import settings
from app.models.models import SpaceUserRole


# Space Schemas
def sanitize_string(value: str) -> str:
    """Sanitize string to prevent SQL injection and XSS attacks."""
    if not value:
        return value
    # Remove SQL comment sequences
    value = re.sub(r'--|#|/\*.*?\*/', '', value)
    # Remove potentially dangerous characters
    value = re.sub(r'[;\'"`]', '', value)
    # Remove leading/trailing whitespace
    return value.strip()

class SpaceBase(BaseModel):
    name: constr(strip_whitespace=True, min_length=1, max_length=100)
    description: Optional[constr(max_length=500)] = None
    
    @field_validator('name', 'description')
    @classmethod
    def validate_string_fields(cls, value):
        if value is None:
            return value
        sanitized = sanitize_string(value)
        if not sanitized and value:  # If we removed everything but the original wasn't empty
            raise ValidationException("Invalid characters in input")
        return sanitized

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

class Space(SpaceInDBBase):
    pass


# Pixel Schemas
class PixelBase(BaseModel):
    name: constr(strip_whitespace=True, min_length=1, max_length=100)
    code: constr(strip_whitespace=True, min_length=1, max_length=5000)
    type: constr(strip_whitespace=True, min_length=1, max_length=50)
    
    @field_validator('name', 'code', 'type')
    @classmethod
    def validate_pixel_fields(cls, value):
        sanitized = sanitize_string(value)
        if not sanitized:
            raise ValidationException("Invalid characters in input")
        return sanitized

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
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        # EmailStr already does basic validation, but we can add additional checks
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', v):
            raise ValueError("Invalid email format")
        return v.lower()  # Normalize email to lowercase

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
    domain: constr(strip_whitespace=True, to_lower=True, min_length=1, max_length=253)
    is_active: Optional[bool] = True
    space_id: UUID4
    verified: Optional[bool] = False
    
    @field_validator('domain')
    @classmethod
    def validate_domain(cls, v):
        sanitized = sanitize_string(v)
        if not sanitized or not re.match(
            r'^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$',
            sanitized
        ):
            raise ValueError("Invalid domain format")
        return sanitized

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
    domain_id: Optional[constr(max_length=253)] = None
    short_code: constr(
        strip_whitespace=True,
        min_length=1,
        max_length=100,
        pattern=r'^[a-zA-Z0-9_-]+$',
        to_lower=True  # Convert to lowercase for consistency
    )
    is_active: Optional[bool] = True
    link_data: dict
    
    @field_validator('short_code')
    @classmethod
    def validate_short_code(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValidationException(
                "Invalid short code format",
                details={"short_code": "Can only contain letters, numbers, hyphens, and underscores"}
            )
        return v.lower()  # Ensure consistent case

    @field_validator('domain_id')
    @classmethod
    def validate_domain_id(cls, v):
        if v is None:
            return v
        sanitized = sanitize_string(v)
        if not sanitized:
            raise ValueError("Invalid characters in domain_id")
        return sanitized

class LinkCreate(LinkBase):
    """Schema for creating a new shortened link."""
    url: str  # The destination URL to redirect to
    password: Optional[str] = None  # Optional password for the link
    title: Optional[str] = None  # Optional title for the link
    description: Optional[str] = None  # Optional description
    tags: Optional[List[str]] = None  # Optional tags for organization
    generate_qr: bool = False  # Whether to generate a QR code for this link
    pixel_ids: Optional[List[UUID]] = None  # List of pixel IDs to associate
    
    class Config:
        schema_extra = {
            "example": {
                "space_id": "123e4567-e89b-12d3-a456-426614174000",
                "domain_id": "example.com",
                "short_code": "mylink",
                "is_active": True,
                "url": "https://example.com/long/url/to/be/shortened",
                "password": "optional-password",
                "title": "My Short Link",
                "description": "A description of where this link points to",
                "tags": ["marketing", "social"],
                "generate_qr": False,
                "pixel_ids": ["123e4567-e89b-12d3-a456-426614174001", "123e4567-e89b-12d3-a456-426614174002"]
            }
        }

class LinkUpdate(BaseModel):
    is_active: Optional[bool] = None
    link_data: Optional[dict] = None
    pixel_ids: Optional[List[UUID]] = None

class LinkInDBBase(LinkBase):
    id: UUID4
    created_at: datetime
    pixel_ids: Optional[List[UUID]] = None

    class Config:
        orm_mode = True

class Link(LinkInDBBase):
    """Schema for a link response, including the QR code if available."""
    qr_code: Optional[str] = Field(
        None, 
        description="Base64-encoded QR code image (PNG) if available"
    )
    short_url: Optional[str] = Field(
        None,
        description="The full short URL that redirects to the original URL"
    )
    original_url: Optional[str] = Field(
        None,
        description="The original URL that this short link points to"
    )
    title: Optional[str] = Field(
        None,
        description="Optional title for the link"
    )
    description: Optional[str] = Field(
        None,
        description="Optional description for the link"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="List of tags for categorizing the link"
    )
    click_count: int = Field(
        0,
        description="Number of times this link has been clicked"
    )
    has_password: bool = Field(
        False,
        description="Whether the link is password protected"
    )
    pixels: Optional[List["Pixel"]] = None
    
    class Config:
        orm_mode = True
        json_encoders = {
            'datetime': lambda v: v.isoformat() if v else None
        }
        
    @classmethod
    def from_orm(cls, obj):
        """Override to handle custom field mapping from ORM."""
        # Get the base ORM data
        data = super().from_orm(obj)
        
        # Add link_data fields to the root of the response
        if hasattr(obj, 'link_data') and obj.link_data:
            data.original_url = obj.link_data.get('url')
            data.title = obj.link_data.get('title')
            data.description = obj.link_data.get('description')
            data.tags = obj.link_data.get('tags', [])
            data.click_count = obj.link_data.get('clicks', 0)
            data.has_password = bool(obj.link_data.get('password'))
            
            # Only include QR code if it exists
            if 'qr_code' in obj.link_data:
                data.qr_code = obj.link_data['qr_code']
        
        # Set the short URL
        if hasattr(obj, 'domain_id') and obj.domain_id:
            data.short_url = f"https://{obj.domain_id}/{obj.short_code}"
        else:
            data.short_url = f"{settings.DEFAULT_DOMAIN}/{obj.short_code}"
            
        return data


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
    OWNER = SpaceUserRole.OWNER.value
    ADMIN = SpaceUserRole.ADMIN.value
    MEMBER = SpaceUserRole.MEMBER.value
    VIEWER = SpaceUserRole.VIEWER.value

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




