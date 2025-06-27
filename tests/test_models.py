"""
Tests for Space and Pixel models.
"""
import pytest
from uuid import uuid4
from datetime import datetime, timedelta

from app.models import models
from app.core.exceptions import ValidationException

def test_space_creation():
    """Test creating a new space."""
    space = models.Space(
        id=uuid4(),
        name="Test Space",
        description="A test space"
    )
    
    assert space.name == "Test Space"
    assert space.description == "A test space"
    assert isinstance(space.created_at, datetime)
    assert space.created_at <= datetime.utcnow()

def test_space_validation():
    """Test space model validation."""
    # Test valid name
    space = models.Space(name="Valid Name 123")
    assert space.name == "Valid Name 123"
    
    # Test name with invalid characters
    with pytest.raises(ValueError):
        models.Space(name="Invalid; DROP TABLE users; --")

def test_pixel_creation(test_space):
    """Test creating a new pixel."""
    pixel = models.Pixel(
        id=uuid4(),
        space_id=test_space.id,
        name="Test Pixel",
        code="console.log('test')",
        type="javascript"
    )
    
    assert pixel.name == "Test Pixel"
    assert pixel.code == "console.log('test')"
    assert pixel.type == "javascript"
    assert pixel.space_id == test_space.id
    assert isinstance(pixel.created_at, datetime)

def test_pixel_validation():
    """Test pixel model validation."""
    # Test valid pixel data
    pixel = models.Pixel(
        space_id=uuid4(),
        name="Test Pixel",
        code="console.log('test')",
        type="javascript"
    )
    assert pixel.name == "Test Pixel"
    
    # Test invalid code with SQL injection attempt
    with pytest.raises(ValueError):
        models.Pixel(
            space_id=uuid4(),
            name="Test Pixel",
            code="console.log('test'); DROP TABLE users; --",
            type="javascript"
        )

def test_space_user_relationship(test_user, test_space):
    """Test space-user relationship."""
    # Create a space user relationship
    space_user = models.SpaceUser(
        space_id=test_space.id,
        user_id=test_user.id,
        role=models.SpaceUserRole.OWNER
    )
    
    # Test the relationship
    assert space_user.space_id == test_space.id
    assert space_user.user_id == test_user.id
    assert space_user.role == models.SpaceUserRole.OWNER

def test_pixel_space_relationship(test_space):
    """Test pixel-space relationship."""
    # Create a pixel
    pixel = models.Pixel(
        space_id=test_space.id,
        name="Test Pixel",
        code="console.log('test')",
        type="javascript"
    )
    
    # Test the relationship
    assert pixel.space_id == test_space.id
    # Note: If you've set up the relationship in the model, you could also test:
    # assert pixel.space == test_space
