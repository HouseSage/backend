"""
Comprehensive tests for the Link API - demonstrating both minimal and advanced usage.
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

# Test data constants
TEST_USER_ID = str(uuid4())
TEST_SPACE_ID = str(uuid4())
TEST_PIXEL_ID_1 = str(uuid4())
TEST_PIXEL_ID_2 = str(uuid4())
TEST_DOMAIN = "short.ly"

def get_test_token():
    """Helper to get test JWT token."""
    return create_access_token({"sub": TEST_USER_ID})

def create_mock_link(link_id=None, space_id=None, short_code="abc123", url="https://example.com", 
                    title=None, domain_id=None, link_data=None):
    """Helper to create mock link objects."""
    if link_data is None:
        link_data = {
            "url": url,
            "title": title,
            "description": None,
            "tags": [],
            "password": None,
            "expires_at": None,
            "created_at": datetime.utcnow().isoformat(),
            "clicks": 0
        }
    
    return models.Link(
        id=link_id or str(uuid4()),
        space_id=space_id or TEST_SPACE_ID,
        domain_id=domain_id,
        short_code=short_code,
        is_active=True,
        created_at=datetime.utcnow(),
        link_data=link_data
    )

class TestLinkCreation:
    """Test cases for link creation with various payloads."""
    
    def test_minimal_request(self):
        """Test 1: Minimal request - just URL."""
        with patch("app.api.links.LinkService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_db_link = create_mock_link()
            mock_service.create_link.return_value = mock_db_link
            
            response = client.post(
                "/api/v1/links/",
                json={"url": "https://example.com/very/long/url"},
                headers={"Authorization": f"Bearer {get_test_token()}"}
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["url"] == "https://example.com/very/long/url"
            assert "short_code" in data
            assert "short_url" in data
            assert data["is_active"] is True
    
    def test_with_custom_short_code(self):
        """Test 2: With custom short code."""
        with patch("app.api.links.LinkService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_db_link = create_mock_link(short_code="mylink")
            mock_service.create_link.return_value = mock_db_link
            
            response = client.post(
                "/api/v1/links/",
                json={
                    "url": "https://example.com/very/long/url",
                    "short_code": "mylink"
                },
                headers={"Authorization": f"Bearer {get_test_token()}"}
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["short_code"] == "mylink"
            assert data["url"] == "https://example.com/very/long/url"
    
    def test_with_title_and_description(self):
        """Test 3: With title and description."""
        with patch("app.api.links.LinkService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            link_data = {
                "url": "https://example.com/very/long/url",
                "title": "My Example Link",
                "description": "This is an example link for testing",
                "tags": [],
                "password": None,
                "expires_at": None,
                "created_at": datetime.utcnow().isoformat(),
                "clicks": 0
            }
            mock_db_link = create_mock_link(
                title="My Example Link",
                link_data=link_data
            )
            mock_service.create_link.return_value = mock_db_link
            
            response = client.post(
                "/api/v1/links/",
                json={
                    "url": "https://example.com/very/long/url",
                    "title": "My Example Link",
                    "description": "This is an example link for testing"
                },
                headers={"Authorization": f"Bearer {get_test_token()}"}
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "My Example Link"
            assert data["url"] == "https://example.com/very/long/url"
    
    def test_advanced_usage_with_all_features(self):
        """Test 4: Advanced usage with custom domain, pixels, tags, etc."""
        with patch("app.api.links.LinkService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            link_data = {
                "url": "https://example.com/marketing/campaign",
                "title": "Marketing Campaign 2024",
                "description": "Main landing page for our 2024 marketing campaign",
                "tags": ["marketing", "campaign", "2024"],
                "password": "secret123",
                "expires_at": "2024-12-31T23:59:59",
                "created_at": datetime.utcnow().isoformat(),
                "clicks": 0
            }
            mock_db_link = create_mock_link(
                short_code="campaign2024",
                domain_id=TEST_DOMAIN,
                title="Marketing Campaign 2024",
                link_data=link_data
            )
            mock_service.create_link.return_value = mock_db_link
            
            response = client.post(
                "/api/v1/links/",
                json={
                    "url": "https://example.com/marketing/campaign",
                    "space_id": TEST_SPACE_ID,
                    "domain_id": TEST_DOMAIN,
                    "short_code": "campaign2024",
                    "title": "Marketing Campaign 2024",
                    "description": "Main landing page for our 2024 marketing campaign",
                    "tags": ["marketing", "campaign", "2024"],
                    "password": "secret123",
                    "pixel_ids": [TEST_PIXEL_ID_1, TEST_PIXEL_ID_2],
                    "expires_at": "2024-12-31T23:59:59"
                },
                headers={"Authorization": f"Bearer {get_test_token()}"}
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["short_code"] == "campaign2024"
            assert data["title"] == "Marketing Campaign 2024"
            assert data["url"] == "https://example.com/marketing/campaign"
            # Note: short_url should use custom domain
            assert TEST_DOMAIN in data["short_url"]

class TestLinkValidation:
    """Test cases for link validation."""
    
    def test_invalid_url_format(self):
        """Test validation of invalid URL format."""
        response = client.post(
            "/api/v1/links/",
            json={"url": "not-a-valid-url"},
            headers={"Authorization": f"Bearer {get_test_token()}"}
        )
        assert response.status_code == 422  # Validation error
    
    def test_empty_url(self):
        """Test validation of empty URL."""
        response = client.post(
            "/api/v1/links/",
            json={"url": ""},
            headers={"Authorization": f"Bearer {get_test_token()}"}
        )
        assert response.status_code == 422  # Validation error
    
    def test_invalid_short_code_characters(self):
        """Test validation of invalid short code characters."""
        response = client.post(
            "/api/v1/links/",
            json={
                "url": "https://example.com",
                "short_code": "invalid@code!"
            },
            headers={"Authorization": f"Bearer {get_test_token()}"}
        )
        assert response.status_code == 422  # Validation error
    
    def test_duplicate_short_code(self):
        """Test handling of duplicate short codes."""
        with patch("app.api.links.LinkService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            # Mock service to raise ValueError for duplicate short code
            mock_service.create_link.side_effect = ValueError("Short code 'duplicate' is already in use")
            
            response = client.post(
                "/api/v1/links/",
                json={
                    "url": "https://example.com",
                    "short_code": "duplicate"
                },
                headers={"Authorization": f"Bearer {get_test_token()}"}
            )
            
            assert response.status_code == 400
            assert "already in use" in response.json()["detail"]

class TestLinkOperations:
    """Test cases for other link operations."""
    
    def test_get_links_list(self):
        """Test getting list of links."""
        with patch("app.crud.crud_link.get_all_links") as mock_get_links:
            mock_links = [
                create_mock_link(short_code=f"link{i}", url=f"https://example{i}.com")
                for i in range(3)
            ]
            mock_get_links.return_value = mock_links
            
            response = client.get(
                "/api/v1/links/",
                headers={"Authorization": f"Bearer {get_test_token()}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 3
            assert data[0]["short_code"] == "link0"
            assert data[1]["short_code"] == "link1"
            assert data[2]["short_code"] == "link2"
    
    def test_get_single_link(self):
        """Test getting a single link by ID."""
        with patch("app.crud.crud_link.get_link") as mock_get_link:
            test_link_id = str(uuid4())
            mock_link = create_mock_link(
                link_id=test_link_id,
                short_code="testlink",
                title="Test Link"
            )
            mock_get_link.return_value = mock_link
            
            response = client.get(
                f"/api/v1/links/{test_link_id}",
                headers={"Authorization": f"Bearer {get_test_token()}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == test_link_id
            assert data["short_code"] == "testlink"
            assert data["title"] == "Test Link"
    
    def test_update_link(self):
        """Test updating a link."""
        with patch("app.api.links.LinkService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            test_link_id = str(uuid4())
            updated_link_data = {
                "url": "https://updated.com",
                "title": "Updated Title",
                "description": None,
                "tags": [],
                "password": None,
                "expires_at": None,
                "created_at": datetime.utcnow().isoformat(),
                "clicks": 0
            }
            mock_updated_link = create_mock_link(
                link_id=test_link_id,
                url="https://updated.com",
                title="Updated Title",
                link_data=updated_link_data
            )
            mock_service.update_link.return_value = mock_updated_link
            
            response = client.put(
                f"/api/v1/links/{test_link_id}",
                json={
                    "url": "https://updated.com",
                    "title": "Updated Title"
                },
                headers={"Authorization": f"Bearer {get_test_token()}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["url"] == "https://updated.com"
            assert data["title"] == "Updated Title"
    
    def test_delete_link(self):
        """Test deleting a link."""
        with patch("app.crud.crud_link.get_link") as mock_get_link, \
             patch("app.crud.crud_link.delete_link") as mock_delete_link:
            
            test_link_id = str(uuid4())
            mock_link = create_mock_link(link_id=test_link_id)
            mock_get_link.return_value = mock_link
            mock_delete_link.return_value = mock_link
            
            response = client.delete(
                f"/api/v1/links/{test_link_id}",
                headers={"Authorization": f"Bearer {get_test_token()}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == test_link_id

class TestAuthentication:
    """Test cases for authentication requirements."""
    
    def test_create_link_without_auth(self):
        """Test that creating a link requires authentication."""
        response = client.post(
            "/api/v1/links/",
            json={"url": "https://example.com"}
        )
        assert response.status_code == 401
    
    def test_get_links_without_auth(self):
        """Test that getting links requires authentication."""
        response = client.get("/api/v1/links/")
        assert response.status_code == 401
    
    def test_update_link_without_auth(self):
        """Test that updating a link requires authentication."""
        test_link_id = str(uuid4())
        response = client.put(
            f"/api/v1/links/{test_link_id}",
            json={"title": "New Title"}
        )
        assert response.status_code == 401
    
    def test_delete_link_without_auth(self):
        """Test that deleting a link requires authentication."""
        test_link_id = str(uuid4())
        response = client.delete(f"/api/v1/links/{test_link_id}")
        assert response.status_code == 401

# Practical test examples you can run manually
class TestManualExamples:
    """
    These are example payloads you can use for manual testing.
    Copy these JSON payloads and use them with curl or Postman.
    """
    
    @pytest.mark.skip(reason="Manual testing examples")
    def test_manual_examples(self):
        """
        Manual testing examples - use these with curl or Postman:
        
        # 1. Minimal request
        curl -X POST "http://localhost:8000/api/v1/links/" \
          -H "Authorization: Bearer YOUR_TOKEN_HERE" \
          -H "Content-Type: application/json" \
          -d '{"url": "https://example.com/very/long/url"}'
        
        # 2. With custom short code
        curl -X POST "http://localhost:8000/api/v1/links/" \
          -H "Authorization: Bearer YOUR_TOKEN_HERE" \
          -H "Content-Type: application/json" \
          -d '{"url": "https://example.com/very/long/url", "short_code": "mylink"}'
        
        # 3. With title and description
        curl -X POST "http://localhost:8000/api/v1/links/" \
          -H "Authorization: Bearer YOUR_TOKEN_HERE" \
          -H "Content-Type: application/json" \
          -d '{
            "url": "https://example.com/very/long/url",
            "title": "My Example Link",
            "description": "This is an example link for testing"
          }'
        
        # 4. Advanced usage (replace UUIDs with real ones)
        curl -X POST "http://localhost:8000/api/v1/links/" \
          -H "Authorization: Bearer YOUR_TOKEN_HERE" \
          -H "Content-Type: application/json" \
          -d '{
            "url": "https://example.com/marketing/campaign",
            "space_id": "123e4567-e89b-12d3-a456-426614174000",
            "domain_id": "short.ly",
            "short_code": "campaign2024",
            "title": "Marketing Campaign 2024",
            "description": "Main landing page for our 2024 marketing campaign",
            "tags": ["marketing", "campaign", "2024"],
            "password": "secret123",
            "pixel_ids": [
              "123e4567-e89b-12d3-a456-426614174001",
              "123e4567-e89b-12d3-a456-426614174002"
            ],
            "expires_at": "2024-12-31T23:59:59"
          }'
        
        # 5. Get all links
        curl -X GET "http://localhost:8000/api/v1/links/" \
          -H "Authorization: Bearer YOUR_TOKEN_HERE"
        
        # 6. Get specific link
        curl -X GET "http://localhost:8000/api/v1/links/LINK_ID_HERE" \
          -H "Authorization: Bearer YOUR_TOKEN_HERE"
        
        # 7. Update link
        curl -X PUT "http://localhost:8000/api/v1/links/LINK_ID_HERE" \
          -H "Authorization: Bearer YOUR_TOKEN_HERE" \
          -H "Content-Type: application/json" \
          -d '{"title": "Updated Title", "url": "https://updated.com"}'
        
        # 8. Delete link
        curl -X DELETE "http://localhost:8000/api/v1/links/LINK_ID_HERE" \
          -H "Authorization: Bearer YOUR_TOKEN_HERE"
        """
        pass

if __name__ == "__main__":
    # Run specific test classes
    pytest.main([__file__ + "::TestLinkCreation", "-v"])