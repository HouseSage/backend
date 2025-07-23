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
    space_id: UUID4
    is_active: Optional[bool] = True
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

class DomainCreate(BaseModel):
    domain: constr(strip_whitespace=True, to_lower=True, min_length=1, max_length=253)
    space_id: UUID4

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

class DomainUpdate(BaseModel):
    domain: Optional[constr(strip_whitespace=True, to_lower=True, min_length=1, max_length=253)] = None

    @field_validator('domain')
    @classmethod
    def validate_domain(cls, v):
        if v is None:
            return v
        sanitized = sanitize_string(v)
        if not sanitized or not re.match(
            r'^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$',
            sanitized
        ):
            raise ValueError("Invalid domain format")
        return sanitized

class DomainInDBBase(DomainBase):
    created_at: datetime
    verification_token: Optional[str] = None

    class Config:
        orm_mode = True

class Domain(DomainInDBBase):
    pass


# Link Schemas
class LinkCreate(BaseModel):
    """Schema for creating a new shortened link - supports both minimal and advanced usage."""
    url: str = Field(..., description="The destination URL to redirect to")
    space_id: Optional[UUID4] = Field(None, description="Space ID (optional)")
    domain_id: Optional[str] = Field(None, description="Custom domain (optional)")
    short_code: Optional[str] = Field(None, description="Custom short code (optional, auto-generated if not provided)")
    title: Optional[str] = Field(None, max_length=200, description="Optional title for the link")
    description: Optional[str] = Field(None, max_length=500, description="Optional description")
    tags: Optional[List[str]] = Field(None, description="Optional tags for organization")
    password: Optional[str] = Field(None, description="Optional password protection")
    pixel_ids: Optional[List[UUID4]] = Field(None, description="List of pixel IDs to associate with this link")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration date")
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        if not v or not v.strip():
            raise ValueError("URL cannot be empty")
        # Basic URL validation
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError("URL must start with http:// or https://")
        return v.strip()
    
    @field_validator('short_code')
    @classmethod
    def validate_short_code(cls, v):
        if v is None:
            return v
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Short code can only contain letters, numbers, hyphens, and underscores")
        return v.lower()
    
    @field_validator('domain_id')
    @classmethod
    def validate_domain_id(cls, v):
        if v is None:
            return v
        sanitized = sanitize_string(v)
        if not sanitized:
            raise ValueError("Invalid characters in domain_id")
        return sanitized
    
    class Config:
        schema_extra = {
            "examples": {
                "minimal": {
                    "summary": "Minimal request",
                    "description": "Just the URL - everything else is optional",
                    "value": {
                        "url": "https://example.com/very/long/url"
                    }
                },
                "with_custom_code": {
                    "summary": "With custom short code",
                    "description": "URL with a custom short code",
                    "value": {
                        "url": "https://example.com/very/long/url",
                        "short_code": "mylink"
                    }
                },
                "with_title": {
                    "summary": "With title and description",
                    "description": "URL with metadata",
                    "value": {
                        "url": "https://example.com/very/long/url",
                        "title": "My Example Link",
                        "description": "This is an example link for testing"
                    }
                },
                "advanced": {
                    "summary": "Advanced usage",
                    "description": "Using custom domain, pixels, and other advanced features",
                    "value": {
                        "url": "https://example.com/very/long/url",
                        "space_id": "123e4567-e89b-12d3-a456-426614174000",
                        "domain_id": "short.ly",
                        "short_code": "campaign2024",
                        "title": "Marketing Campaign 2024",
                        "description": "Main landing page for our 2024 marketing campaign",
                        "tags": ["marketing", "campaign", "2024"],
                        "password": "secret123",
                        "pixel_ids": ["123e4567-e89b-12d3-a456-426614174001", "123e4567-e89b-12d3-a456-426614174002"]
                    }
                }
            }
        }

class LinkUpdate(BaseModel):
    """Schema for updating a link."""
    url: Optional[str] = None
    title: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        if v is None:
            return v
        if not v.strip():
            raise ValueError("URL cannot be empty")
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError("URL must start with http:// or https://")
        return v.strip()

class Link(BaseModel):
    """Schema for a link response - simplified for easy testing."""
    id: UUID4
    space_id: UUID4
    short_code: str
    url: str = Field(..., description="The original URL")
    title: Optional[str] = None
    short_url: str = Field(..., description="The full short URL")
    is_active: bool = True
    created_at: datetime
    
    @classmethod
    def from_db_model(cls, db_link):
        """Convert database model to response schema."""
        from app.core.config import settings
        
        # Extract URL and title from link_data
        url = db_link.link_data.get('url', '')
        title = db_link.link_data.get('title')
        
        # Build short URL
        if db_link.domain_id:
            short_url = f"https://{db_link.domain_id}/{db_link.short_code}"
        else:
            short_url = f"{settings.DEFAULT_DOMAIN}/{db_link.short_code}"
        
        return cls(
            id=db_link.id,
            space_id=db_link.space_id,
            short_code=db_link.short_code,
            url=url,
            title=title,
            short_url=short_url,
            is_active=db_link.is_active,
            created_at=db_link.created_at
        )
    
    class Config:
        from_attributes = True
        json_encoders = {
            'datetime': lambda v: v.isoformat() if v else None
        }


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




