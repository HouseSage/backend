from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint, Index, CHAR, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr

from app.db.database import Base


class SpaceUserRole(str, Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"

class RedirectType(str, Enum):
    DIRECT = "DIRECT"
    RANDOM = "RANDOM"
    GEO = "GEO"
    WEIGHTED = "WEIGHTED"

class EventType(str, Enum):
    CLICK = "CLICK"
    REDIRECT = "REDIRECT"
    SCAN = "SCAN"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    

    default_space = relationship("Space", uselist=False, back_populates="owner", foreign_keys="Space.owner_id")
    space_members = relationship("SpaceUser", back_populates="user")

class Space(Base):
    __tablename__ = "spaces"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True)
    
   
    owner = relationship("User", back_populates="default_space", foreign_keys=[owner_id])
    links = relationship("Link", back_populates="space")
    pixels = relationship("Pixel", back_populates="space")
    domains = relationship("Domain", back_populates="space")
    members = relationship("SpaceUser", back_populates="space")
    
   
    __table_args__ = (
        UniqueConstraint('owner_id', 'is_default'),
        Index('ix_spaces_name', 'name'),
    )

class SpaceUser(Base):
    __tablename__ = "space_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    space_id = Column(Integer, ForeignKey("spaces.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, default=SpaceUserRole.MEMBER.value)
    
  
    space = relationship("Space", back_populates="members")
    user = relationship("User", back_populates="space_members")
    
   
    __table_args__ = (
        UniqueConstraint('space_id', 'user_id'),
    )

class Domain(Base):
    __tablename__ = "domains"

    id = Column(Integer, primary_key=True, autoincrement=True)
    domain = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    space_id = Column(Integer, ForeignKey("spaces.id"), nullable=False)
    verification_token = Column(String, nullable=True)
    verified = Column(Boolean, default=False)
    
   
    space = relationship("Space", back_populates="domains")
    links = relationship("Link", back_populates="domain")
    
    
    __table_args__ = (
        Index('ix_domains_domain', 'domain'),
    )

class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    space_id = Column(Integer, ForeignKey("spaces.id"), nullable=False)
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=True)
    short_code = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    hasQR = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
   
    link_data = Column(JSON, nullable=False) 
    utm_data = Column(JSON, nullable=True)  
    redirect_rules = Column(JSON, nullable=True)  
    password_data = Column(JSON, nullable=True)  
    qr_data = Column(JSON, nullable=True)  
    
    
    space = relationship("Space", back_populates="links")
    domain = relationship("Domain", back_populates="links")
    events = relationship("Event", back_populates="link")
   
    __table_args__ = (
        UniqueConstraint('domain_id', 'short_code'),
        Index('ix_links_short_code', 'short_code'),
        Index('ix_links_created_at', 'created_at'),
    )

class Pixel(Base):
    __tablename__ = "pixels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    space_id = Column(Integer, ForeignKey("spaces.id"), nullable=False)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)
    type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
   
    space = relationship("Space", back_populates="pixels")
    
   
    __table_args__ = (
        Index('ix_pixels_code', 'code'),
    )

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    link_id = Column(Integer, ForeignKey("links.id"), nullable=False)
    type = Column(String, nullable=False)  
    country_code = Column(CHAR(2), nullable=True)
    city = Column(String, nullable=True)
    region = Column(String, nullable=True)
    referrer = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    device_type = Column(String, nullable=True)
    os = Column(String, nullable=True)
    browser = Column(String, nullable=True)
    session_id = Column(String, nullable=True)
    user_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    event_data = Column(JSON, nullable=True) 
    
   
    link = relationship("Link", back_populates="events")
    
    
    __table_args__ = (
        Index('ix_events_link_id', 'link_id'),
        Index('ix_events_created_at', 'created_at'),
        Index('ix_events_country_code', 'country_code'),
        Index('ix_events_device_type', 'device_type'),
        Index('ix_events_type', 'type'),
    )
