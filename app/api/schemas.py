import re
from pydantic import BaseModel, UUID4, EmailStr, Field, ConfigDict, field_validator, model_validator, constr
from pydantic_core import PydanticCustomError
from app.core.exceptions import ValidationException
from typing import Optional, List, Union, Dict, Any, Literal
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



class DomainInDBBase(DomainBase):
    created_at: datetime
    verification_token: Optional[str] = None

    class Config:
        orm_mode = True

class Domain(DomainInDBBase):
    pass


# Link Schemas - Generic Link System
class LinkDataBase(BaseModel):
    """Base schema for link data - all link types inherit from this."""
    track: bool = Field(True, description="Whether to track events for this link")
    password: Optional[str] = Field(None, description="Optional password protection")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration date")

class SimpleLinkData(LinkDataBase):
    """Data for simple redirect links."""
    type: Literal["simple"] = Field(default="simple", description="Link type")
    url: str = Field(..., description="The destination URL to redirect to")
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        if not v or not v.strip():
            raise ValueError("URL cannot be empty")
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError("URL must start with http:// or https://")
        return v.strip()

class RoundRobinLinkData(LinkDataBase):
    """Data for round-robin redirect links."""
    type: Literal["round_robin"] = Field(default="round_robin", description="Link type")
    urls: List[str] = Field(..., min_length=1, description="List of URLs to rotate through")
    
    @field_validator('urls')
    @classmethod
    def validate_urls(cls, v):
        if not v:
            raise ValueError("URLs list cannot be empty")
        for url in v:
            if not url or not url.strip():
                raise ValueError("URL cannot be empty")
            if not (url.startswith('http://') or url.startswith('https://')):
                raise ValueError("All URLs must start with http:// or https://")
        return v

class ComplexLinkData(LinkDataBase):
    """Data for complex redirect links with rules."""
    type: Literal["complex"] = Field(default="complex", description="Link type")
    rules: Dict[str, Any] = Field(..., description="Redirect rules (android -> urlA, iphone -> urlB, else -> urlC)")

class LinkCreate(BaseModel):
    """Schema for creating a new shortened link - Generic Link System."""
    # Core fields
    space_id: Optional[UUID4] = Field(None, description="Space ID (optional - use default if not provided)")
    domain_id: str = Field(default="3c47a249.test", description="Domain name (defaults to verified domain if not provided)")
    short_code: Optional[str] = Field(None, description="Custom short code (optional, auto-generated if not provided)")
    
    # Metadata fields
    title: Optional[str] = Field(None, max_length=200, description="Optional title for the link")
    description: Optional[str] = Field(None, max_length=500, description="Optional description")
    tags: Optional[List[str]] = Field(None, description="Optional tags for organization")
    pixel_ids: Optional[List[UUID4]] = Field(None, description="List of pixel IDs to associate with this link")
    
    # Generic data field - contains all redirect logic
    data: Optional[Union[SimpleLinkData, RoundRobinLinkData, ComplexLinkData]] = Field(
        None, 
        discriminator='type',
        description="Link data containing type-specific redirect logic"
    )
    
    # Backward compatibility field
    url: Optional[str] = Field(None, description="Legacy URL field for backward compatibility")
    
    @model_validator(mode='before')
    @classmethod
    def handle_backward_compatibility(cls, values):
        """Handle backward compatibility with old link format and set defaults."""
        if isinstance(values, dict):
            # If data field is missing but url field is present, convert to simple link format
            if 'data' not in values and 'url' in values:
                values['data'] = {
                    'type': 'simple',
                    'url': values['url']
                }
                
        return values
    
    @model_validator(mode='after')
    def validate_data_field(self):
        """Ensure data field is present after backward compatibility conversion."""
        if not self.data:
            raise ValueError("Link data is required")
        return self
    
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
        return sanitized  # This was missing!
    
    class Config:
        schema_extra = {
            "examples": {
                "simple": {
                    "summary": "Simple link",
                    "description": "Basic redirect link - matches your image example",
                    "value": {
                        "domain_id": "qill.me",
                        "short_code": "hello",
                        "title": "My Example Link",
                        "description": "This is an example link",
                        "data": {
                            "type": "simple",
                            "url": "https://example.com/very/long/url",
                            "track": True,
                            "password": None,
                            "expires_at": None
                        }
                    }
                },
                "password_protected": {
                    "summary": "Password protected link",
                    "description": "Simple link with password protection",
                    "value": {
                        "domain_id": "qill.me",
                        "short_code": "secret",
                        "title": "Protected Content",
                        "data": {
                            "type": "simple",
                            "url": "https://example.com/secret-content",
                            "track": True,
                            "password": "secret123",
                            "expires_at": "2024-12-31T23:59:59"
                        }
                    }
                },
                "round_robin": {
                    "summary": "Round robin link",
                    "description": "Link that rotates through multiple URLs",
                    "value": {
                        "domain_id": "qill.me",
                        "short_code": "rotate",
                        "title": "Load Balanced Link",
                        "data": {
                            "type": "round_robin",
                            "urls": [
                                "https://server1.example.com/app",
                                "https://server2.example.com/app",
                                "https://server3.example.com/app"
                            ],
                            "track": True
                        }
                    }
                },
                "complex_rules": {
                    "summary": "Complex redirect rules",
                    "description": "Link with device/geo-based redirect rules",
                    "value": {
                        "domain_id": "qill.me",
                        "short_code": "smart",
                        "title": "Smart Redirect",
                        "data": {
                            "type": "complex",
                            "rules": {
                                "android": "https://play.google.com/store/apps/details?id=com.example.app",
                                "iphone": "https://apps.apple.com/us/app/example-app/id123456789",
                                "else": "https://example.com/download"
                            },
                            "track": True
                        }
                    }
                }
            }
        }

class LinkUpdate(BaseModel):
    """Schema for updating a link - supports updating the generic data field."""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = Field(None, max_items=10)
    is_active: Optional[bool] = None
    data: Optional[Union[SimpleLinkData, RoundRobinLinkData, ComplexLinkData]] = Field(
        None,
        discriminator='type',
        description="Updated link data - if provided, replaces the existing data"
    )

class Link(BaseModel):
    """Schema for a link response - Generic Link System."""
    id: UUID4
    space_id: UUID4
    domain_id: Optional[str] = None  # Make optional for backward compatibility
    short_code: str
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    short_url: str = Field(..., description="The full short URL")
    is_active: bool = True
    created_at: datetime
    data: Dict[str, Any] = Field(..., description="Link data containing type-specific redirect logic")
    
    @classmethod
    def from_db_model(cls, db_link):
        """Convert database model to response schema."""
        from app.core.config import settings
        
        # Extract metadata from link_data (maintaining backward compatibility)
        link_data = db_link.link_data or {}
        title = link_data.get('title')
        description = link_data.get('description')
        tags = link_data.get('tags', [])
        
        # Build short URL
        if db_link.domain_id:
            short_url = f"https://{db_link.domain_id}/{db_link.short_code}"
        else:
            short_url = f"https://{settings.DEFAULT_DOMAIN}/{db_link.short_code}"
        
        # Extract the data field - this contains the type-specific redirect logic
        # For backward compatibility, if data doesn't have type, assume simple
        data = link_data.copy()
        if 'type' not in data and 'url' in data:
            # Convert old format to new format
            data = {
                'type': 'simple',
                'url': data.get('url'),
                'track': True,  # Default to tracking enabled
                'password': data.get('password'),
                'expires_at': data.get('expires_at')
            }
        
        return cls(
            id=db_link.id,
            space_id=db_link.space_id,
            domain_id=db_link.domain_id,
            short_code=db_link.short_code,
            title=title,
            description=description,
            tags=tags,
            short_url=short_url,
            is_active=db_link.is_active,
            created_at=db_link.created_at,
            data=data
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




