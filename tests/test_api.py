"""
Tests for Space and Pixel API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from uuid import uuid4

from main import app
from app.models import models
from app.core.security import create_access_token

# Test client
client = TestClient(app)

def test_create_space_unauthorized():
    """Test creating a space without authentication."""
    response = client.post("/api/v1/spaces/", json={"name": "Test Space"})
    assert response.status_code == 401

def test_create_space_authorized(monkeypatch):
    """Test creating a space with authentication."""
    # Mock the database session
    mock_db = MagicMock()
    mock_commit = MagicMock()
    mock_db.commit.return_value = mock_commit
    
    # Create test data
    test_user_id = str(uuid4())
    test_space_id = str(uuid4())
    
    # Mock the space creation
    def mock_create_space(db, space_in, user_id):
        return models.Space(
            id=test_space_id,
            name=space_in.name,
            description=space_in.description,
            owner_id=user_id
        )
    
    # Patch the dependencies
    monkeypatch.setattr("app.crud.crud_space.create_space", mock_create_space)
    
    # Create access token
    token = create_access_token({"sub": test_user_id})
    
    # Make the request
    response = client.post(
        "/api/v1/spaces/",
        json={"name": "Test Space", "description": "Test Description"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    assert response.json()["name"] == "Test Space"
    assert response.json()["description"] == "Test Description"

def test_create_pixel_unauthorized():
    """Test creating a pixel without authentication."""
    response = client.post(
        "/api/v1/pixels/",
        json={"name": "Test Pixel", "code": "test", "type": "javascript", "space_id": str(uuid4())}
    )
    assert response.status_code == 401

@patch("app.api.pixels.crud_pixel.create_pixel")
def test_create_pixel_authorized(mock_create_pixel, monkeypatch):
    """Test creating a pixel with authentication."""
    # Setup test data
    test_user_id = str(uuid4())
    test_space_id = str(uuid4())
    test_pixel_id = str(uuid4())
    
    # Create a test pixel
    test_pixel = models.Pixel(
        id=test_pixel_id,
        name="Test Pixel",
        code="console.log('test')",
        type="javascript",
        space_id=test_space_id
    )
    
    # Mock the create_pixel function
    mock_create_pixel.return_value = test_pixel
    
    # Mock the space membership check
    def mock_ensure_space_admin(*args, **kwargs):
        return True
    
    monkeypatch.setattr("app.api.pixels.ensure_space_admin_or_owner", mock_ensure_space_admin)
    
    # Create access token
    token = create_access_token({"sub": test_user_id})
    
    # Make the request
    response = client.post(
        "/api/v1/pixels/",
        json={
            "name": "Test Pixel",
            "code": "console.log('test')",
            "type": "javascript",
            "space_id": test_space_id
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Pixel"
    assert data["code"] == "console.log('test')"
    assert data["type"] == "javascript"
    assert data["space_id"] == test_space_id

def test_get_pixels_unauthorized():
    """Test getting pixels without authentication."""
    response = client.get("/api/v1/pixels/?space_id=123")
    assert response.status_code == 401

@patch("app.api.pixels.crud_pixel.get_pixels_by_space")
def test_get_pixels_authorized(mock_get_pixels, monkeypatch):
    """Test getting pixels with authentication."""
    # Setup test data
    test_user_id = str(uuid4())
    test_space_id = str(uuid4())
    
    # Create test pixels
    test_pixels = [
        models.Pixel(
            id=str(uuid4()),
            name=f"Pixel {i}",
            code=f"console.log('test{i}')",
            type="javascript",
            space_id=test_space_id
        ) for i in range(3)
    ]
    
    # Mock the get_pixels_by_space function
    mock_get_pixels.return_value = test_pixels
    
    # Mock the space membership check
    def mock_ensure_space_membership(*args, **kwargs):
        return True
    
    monkeypatch.setattr("app.api.pixels.ensure_space_membership", mock_ensure_space_membership)
    
    # Create access token
    token = create_access_token({"sub": test_user_id})
    
    # Make the request
    response = client.get(
        f"/api/v1/pixels/?space_id={test_space_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["name"].startswith("Pixel ")
    assert "code" in data[0]
    assert "type" in data[0]
