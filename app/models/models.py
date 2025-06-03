from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, UniqueConstraint, Index, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr

from app.db.database import Base

def generate_uuid():
    return str(uuid.uuid4())


class SpaceUserRole(str, Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"

class EventType(str, Enum):
    CLICK = "CLICK"
    SCAN = "SCAN"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
   
    spaces = relationship(
        "Space",
        secondary="space_users",
        back_populates="users",
        viewonly=True
    )

class Space(Base):
    __tablename__ = "spaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
  
    links = relationship("Link", back_populates="space")
    pixels = relationship("Pixel", back_populates="space")
    domains = relationship("Domain", back_populates="space")
    users = relationship(
        "User",
        secondary="space_users",
        back_populates="spaces",
        viewonly=True
    )
    
   
    __table_args__ = (
        Index('ix_spaces_name', 'name'),
    )

class SpaceUser(Base):
    __tablename__ = "space_users"

    space_id = Column(UUID(as_uuid=True), ForeignKey("spaces.id"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    role = Column(String, default=SpaceUserRole.MEMBER.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    
  
    __table_args__ = (
        Index('ix_space_users_user_id', 'user_id'),
        Index('ix_space_users_space_id', 'space_id'),
    )

class Domain(Base):
    __tablename__ = "domains"

  
    domain = Column(String, primary_key=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    space_id = Column(UUID(as_uuid=True), ForeignKey("spaces.id"), nullable=False)
    verification_token = Column(String, nullable=True)
    verified = Column(Boolean, default=False)
    
   
    space = relationship("Space", back_populates="domains")
    links = relationship("Link", back_populates="domain")
    
   

class Link(Base):
    __tablename__ = "links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    space_id = Column(UUID(as_uuid=True), ForeignKey("spaces.id"), nullable=False)
    domain_id = Column(String, ForeignKey("domains.domain"), nullable=True)
    short_code = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
   
    link_data = Column(JSON, nullable=False, default=dict)
 
    events = relationship("Event", back_populates="link")
    
   
    __table_args__ = (
        UniqueConstraint('domain_id', 'short_code'),
        Index('ix_links_short_code', 'short_code'),
        Index('ix_links_created_at', 'created_at'),
        Index('ix_links_space_id', 'space_id'),
    )

class Pixel(Base):
    __tablename__ = "pixels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    space_id = Column(UUID(as_uuid=True), ForeignKey("spaces.id"), nullable=False)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)
    type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
   
    __table_args__ = (
        Index('ix_pixels_space_id', 'space_id'),
    )

class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    link_id = Column(UUID(as_uuid=True), ForeignKey("links.id"), nullable=False)
    type = Column(String, nullable=False)  # CLICK or SCAN
    created_at = Column(DateTime, default=datetime.utcnow)
    
   
    event_data = Column(JSON, nullable=False, default=dict)
    
   
    link = relationship("Link", back_populates="events")
    
  
    __table_args__ = (
        Index('ix_events_link_id', 'link_id'),
        Index('ix_events_created_at', 'created_at'),
        Index('ix_events_type', 'type'),
    )
