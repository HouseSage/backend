"""
Simple tests for the Link API - demonstrating the simplified schema.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import datetime

from main import app
from app.models import models
from app.core.security import create_access_token

# Test client
client = TestClient(app)

def test_create_link_simple():
    """Test creating a link with minimal payload."""
    # Mock the database and service
    with patch("app.api.links.LinkService") as mock_service_class:
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        
        # Create test data
        test_user_id = str(uuid4())
        test_space_id = str(uuid4())
        test_link_id = str(uuid4())
        
        # Mock the created link
        mock_db_link = models.Link(
            id=test_link_id,
            space_id=test_space_id,
            short_code="abc123",
            is_active=True,
            created_at=datetime.utcnow(),
            link_data={"url": "https://example.com", "title": None}
        )
        mock_service.create_link.return_value = mock_db_link
        
        # Create access token
        token = create_access_token({"sub": test_user_id})
        
        # Test minimal payload
        response = client.post(
            "/api/v1/links/",
            json={"url": "https://example.com"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["url"] == "https://example.com"
        assert data["short_code"] == "abc123"
        assert "short_url" in data
        assert data["is_active"] is True

def test_create_link_with_custom_code():
    """Test creating a link with custom short code."""
    with patch("app.api.links.LinkService") as mock_service_class:
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        
        test_user_id = str(uuid4())
        test_space_id = str(uuid4())
        test_link_id = str(uuid4())
        
        mock_db_link = models.Link(
            id=test_link_id,
            space_id=test_space_id,
            short_code="mylink",
            is_active=True,
            created_at=datetime.utcnow(),
            link_data={"url": "https://example.com", "title": "My Link"}
        )
        mock_service.create_link.return_value = mock_db_link
        
        token = create_access_token({"sub": test_user_id})
        
        # Test with custom short code and title
        response = client.post(
            "/api/v1/links/",
            json={
                "url": "https://example.com",
                "short_code": "mylink",
                "title": "My Link"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["url"] == "https://example.com"
        assert data["short_code"] == "mylink"
        assert data["title"] == "My Link"

def test_create_link_invalid_url():
    """Test creating a link with invalid URL."""
    test_user_id = str(uuid4())
    token = create_access_token({"sub": test_user_id})
    
    # Test invalid URL
    response = client.post(
        "/api/v1/links/",
        json={"url": "not-a-valid-url"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 422  # Validation error

def test_create_link_unauthorized():
    """Test creating a link without authentication."""
    response = client.post(
        "/api/v1/links/",
        json={"url": "https://example.com"}
    )
    assert response.status_code == 401

def test_get_links():
    """Test getting list of links."""
    with patch("app.crud.crud_link.get_all_links") as mock_get_links:
        test_user_id = str(uuid4())
        test_space_id = str(uuid4())
        
        # Mock links
        mock_links = [
            models.Link(
                id=str(uuid4()),
                space_id=test_space_id,
                short_code=f"link{i}",
                is_active=True,
                created_at=datetime.utcnow(),
                link_data={"url": f"https://example{i}.com", "title": f"Link {i}"}
            ) for i in range(3)
        ]
        mock_get_links.return_value = mock_links
        
        token = create_access_token({"sub": test_user_id})
        
        response = client.get(
            "/api/v1/links/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["url"] == "https://example0.com"
        assert data[0]["title"] == "Link 0"

def test_update_link():
    """Test updating a link."""
    with patch("app.api.links.LinkService") as mock_service_class:
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        
        test_user_id = str(uuid4())
        test_link_id = str(uuid4())
        test_space_id = str(uuid4())
        
        # Mock updated link
        mock_updated_link = models.Link(
            id=test_link_id,
            space_id=test_space_id,
            short_code="abc123",
            is_active=True,
            created_at=datetime.utcnow(),
            link_data={"url": "https://updated.com", "title": "Updated Title"}
        )
        mock_service.update_link.return_value = mock_updated_link
        
        token = create_access_token({"sub": test_user_id})
        
        response = client.put(
            f"/api/v1/links/{test_link_id}",
            json={"url": "https://updated.com", "title": "Updated Title"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["url"] == "https://updated.com"
        assert data["title"] == "Updated Title"