"""
Tests for the LinkService class.
"""
import pytest
from uuid import UUID, uuid4
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from app.models import models
from app.services.link_service import LinkService
from app.api.schemas import LinkCreate, LinkUpdate
from app.core.config import settings

# Test data
TEST_USER_ID = uuid4()
TEST_SPACE_ID = uuid4()
TEST_DOMAIN_ID = "example.com"
TEST_LINK_ID = uuid4()

def test_create_link_success():
    """Test creating a link with valid data."""
    # Setup
    db = MagicMock(spec=Session)
    link_service = LinkService(db)
    
    # Mock data
    link_data = LinkCreate(
        url="https://example.com",
        short_code="test123",
        title="Test Link",
        description="A test link",
        tags=["test", "example"],
        password="mypassword"
    )
    
    # Mock user with default space
    mock_user = models.User(
        id=TEST_USER_ID,
        email="test@example.com",
        default_space_id=TEST_SPACE_ID
    )
    
    # Mock database responses
    db.query.return_value.filter.return_value.first.side_effect = [
        mock_user,  # User lookup
        None  # No existing link
    ]
    db.query.return_value.get.return_value = None  # No domain check needed
    
    # Create a mock link to return
    mock_link = models.Link(
        id=TEST_LINK_ID,
        space_id=TEST_SPACE_ID,
        short_code=link_data.short_code,
        is_active=True,
        link_data={
            "url": link_data.url,
            "title": link_data.title,
            "description": link_data.description,
            "tags": link_data.tags,
            "password": link_data.password,
            "clicks": 0
        }
    )
    
    # Mock the add and commit
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock(return_value=mock_link)
    
    # Execute
    result = link_service.create_link(link_data, user_id=TEST_USER_ID)
    
    # Assert
    assert result.id == TEST_LINK_ID
    assert result.short_code == link_data.short_code
    assert result.link_data["url"] == link_data.url
    assert result.link_data["title"] == link_data.title
    assert result.link_data["description"] == link_data.description
    assert result.link_data["tags"] == link_data.tags
    assert "password" in result.link_data  # Password should be stored
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()

def test_create_link_duplicate_short_code():
    """Test creating a link with a duplicate short code."""
    # Setup
    db = MagicMock(spec=Session)
    link_service = LinkService(db)
    
    # Mock data
    link_data = LinkCreate(
        url="https://example.com",
        short_code="duplicate",
    )
    
    # Mock user with default space
    mock_user = models.User(
        id=TEST_USER_ID,
        email="test@example.com",
        default_space_id=TEST_SPACE_ID
    )
    
    # Mock existing link
    existing_link = models.Link(id=uuid4(), short_code="duplicate")
    db.query.return_value.filter.return_value.first.side_effect = [
        mock_user,  # User lookup
        existing_link  # Existing link found
    ]
    
    # Test that it raises ValueError
    with pytest.raises(ValueError) as excinfo:
        link_service.create_link(link_data, user_id=TEST_USER_ID)
    
    assert "already in use" in str(excinfo.value)

def test_create_link_no_default_space():
    """Test creating a link when user has no default space."""
    # Setup
    db = MagicMock(spec=Session)
    link_service = LinkService(db)
    
    # Mock data
    link_data = LinkCreate(
        url="https://example.com",
        short_code="test123",
    )
    
    # Mock user without default space
    mock_user = models.User(
        id=TEST_USER_ID,
        email="test@example.com",
        default_space_id=None
    )
    
    # Mock database responses
    db.query.return_value.filter.return_value.first.return_value = mock_user
    
    # Test that it raises ValueError
    with pytest.raises(ValueError) as excinfo:
        link_service.create_link(link_data, user_id=TEST_USER_ID)
    
    assert "has no default space" in str(excinfo.value)

def test_create_link_user_not_found():
    """Test creating a link when user is not found."""
    # Setup
    db = MagicMock(spec=Session)
    link_service = LinkService(db)
    
    # Mock data
    link_data = LinkCreate(
        url="https://example.com",
        short_code="test123",
    )
    
    # Mock database responses - user not found
    db.query.return_value.filter.return_value.first.return_value = None
    
    # Test that it raises ValueError
    with pytest.raises(ValueError) as excinfo:
        link_service.create_link(link_data, user_id=TEST_USER_ID)
    
    assert "User not found" in str(excinfo.value)

def test_create_link_with_explicit_space_id():
    """Test creating a link with explicit space_id (should not use default space)."""
    # Setup
    db = MagicMock(spec=Session)
    link_service = LinkService(db)
    
    # Mock data with explicit space_id
    explicit_space_id = uuid4()
    link_data = LinkCreate(
        url="https://example.com",
        short_code="test123",
        space_id=explicit_space_id
    )
    
    # Mock database responses
    db.query.return_value.filter.return_value.first.return_value = None  # No existing link
    db.query.return_value.get.return_value = None  # No domain check needed
    
    # Create a mock link to return
    mock_link = models.Link(
        id=TEST_LINK_ID,
        space_id=explicit_space_id,  # Should use the explicit space_id
        short_code=link_data.short_code,
        is_active=True,
        link_data={
            "url": link_data.url,
            "clicks": 0
        }
    )
    
    # Mock the add and commit
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock(return_value=mock_link)
    
    # Execute
    result = link_service.create_link(link_data, user_id=TEST_USER_ID)
    
    # Assert
    assert result.id == TEST_LINK_ID
    assert result.space_id == explicit_space_id  # Should use explicit space_id
    assert result.short_code == link_data.short_code
    assert result.link_data["url"] == link_data.url
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()

def test_get_link_info():
    """Test getting link information."""
    # Setup
    db = MagicMock(spec=Session)
    link_service = LinkService(db)
    
    # Create a test link
    test_link = models.Link(
        id=TEST_LINK_ID,
        space_id=TEST_SPACE_ID,
        short_code="test123",
        domain_id=TEST_DOMAIN_ID,
        is_active=True,
        link_data={
            "url": "https://example.com",
            "title": "Test Link",
            "description": "A test link",
            "tags": ["test"],
            "password": "hashed_password",
            "clicks": 10
        }
    )
    
    # Mock the get_link method
    with patch.object(link_service, 'get_link_by_short_code') as mock_get_link:
        mock_get_link.return_value = test_link
        
        # Execute
        result = link_service.get_link_info(TEST_LINK_ID)
        
        # Assert
        assert result["id"] == str(TEST_LINK_ID)
        assert result["short_code"] == "test123"
        assert result["domain"] == TEST_DOMAIN_ID
        assert result["original_url"] == "https://example.com"
        assert result["title"] == "Test Link"
        assert result["description"] == "A test link"
        assert result["tags"] == ["test"]
        assert result["is_active"] is True
        assert result["has_password"] is True
        assert result["click_count"] == 10
        assert "created_at" in result
        assert "updated_at" in result

def test_update_link_success():
    """Test updating a link with valid data."""
    # Setup
    db = MagicMock(spec=Session)
    link_service = LinkService(db)
    
    # Create a test link
    test_link = models.Link(
        id=TEST_LINK_ID,
        space_id=TEST_SPACE_ID,
        short_code="oldcode",
        is_active=True,
        link_data={
            "url": "https://example.com/old",
            "title": "Old Title"
        }
    )
    
    # Mock data for update
    update_data = LinkUpdate(
        short_code="newcode",
        title="New Title"
    )
    
    # Mock database responses
    db.query.return_value.filter.return_value.first.return_value = None  # No conflict with new short code
    db.query.return_value.get.return_value = test_link  # Return test link when queried by ID
    
    # Execute
    updated_link = link_service.update_link(TEST_LINK_ID, update_data)
    
    # Assert
    assert updated_link.short_code == "newcode"
    assert updated_link.link_data["title"] == "New Title"
    assert updated_link.link_data["url"] == "https://example.com/old"  # Should be unchanged
    db.commit.assert_called_once()

def test_get_link_by_short_code_simple():
    """Test getting a link by short code (click counting handled by event system)."""
    # Setup
    db = MagicMock(spec=Session)
    link_service = LinkService(db)
    
    # Create a test link
    test_link = models.Link(
        id=TEST_LINK_ID,
        space_id=TEST_SPACE_ID,
        short_code="test123",
        is_active=True,
        link_data={"url": "https://example.com"}
    )
    
    # Mock the query
    db.query.return_value.filter.return_value.first.return_value = test_link
    
    # Execute
    result = link_service.get_link_by_short_code("test123")
    
    # Assert - service layer only retrieves the link, doesn't modify it
    assert result is not None
    assert result.short_code == "test123"
    assert result.link_data["url"] == "https://example.com"
    # Click counting is handled by event system at API level, not service level
    db.commit.assert_not_called()  # Service layer shouldn't modify data
