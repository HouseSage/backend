#!/usr/bin/env python3
"""
Link API Testing Examples
Generate curl commands for testing the Link API with various payloads.
"""

import json
from uuid import uuid4
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
TOKEN = "YOUR_JWT_TOKEN_HERE"  # Replace with actual token

def print_curl_command(method, endpoint, data=None, description=""):
    """Print a formatted curl command."""
    print(f"\n# {description}")
    print("-" * 60)
    
    cmd = f'curl -X {method} "{BASE_URL}{endpoint}" \\\n'
    cmd += f'  -H "Authorization: Bearer {TOKEN}" \\\n'
    
    if data:
        cmd += f'  -H "Content-Type: application/json" \\\n'
        cmd += f"  -d '{json.dumps(data, indent=2)}'"
    
    print(cmd)
    print()

def generate_test_examples():
    """Generate comprehensive test examples."""
    
    print("=" * 80)
    print("LINK API TESTING EXAMPLES")
    print("=" * 80)
    print(f"Base URL: {BASE_URL}")
    print(f"Replace '{TOKEN}' with your actual JWT token")
    print("=" * 80)
    
    # 1. Minimal request
    print_curl_command(
        "POST", "/api/v1/links/",
        {"url": "https://example.com/very/long/url/that/needs/shortening"},
        "1. MINIMAL REQUEST - Just URL (recommended starting point)"
    )
    
    # 2. With custom short code
    print_curl_command(
        "POST", "/api/v1/links/",
        {
            "url": "https://example.com/very/long/url",
            "short_code": "mylink"
        },
        "2. WITH CUSTOM SHORT CODE"
    )
    
    # 3. With title and description
    print_curl_command(
        "POST", "/api/v1/links/",
        {
            "url": "https://example.com/very/long/url",
            "title": "My Example Link",
            "description": "This is an example link for testing purposes"
        },
        "3. WITH TITLE AND DESCRIPTION"
    )
    
    # 4. With tags and organization
    print_curl_command(
        "POST", "/api/v1/links/",
        {
            "url": "https://example.com/blog/post/123",
            "title": "Blog Post: Getting Started",
            "description": "Introduction to our platform",
            "tags": ["blog", "tutorial", "getting-started"],
            "short_code": "blog-intro"
        },
        "4. WITH TAGS AND ORGANIZATION"
    )
    
    # 5. With password protection
    print_curl_command(
        "POST", "/api/v1/links/",
        {
            "url": "https://example.com/private/document",
            "title": "Private Document",
            "password": "secret123",
            "short_code": "private-doc"
        },
        "5. WITH PASSWORD PROTECTION"
    )
    
    # 6. With expiration date
    future_date = (datetime.now() + timedelta(days=30)).isoformat()
    print_curl_command(
        "POST", "/api/v1/links/",
        {
            "url": "https://example.com/limited-time-offer",
            "title": "Limited Time Offer",
            "expires_at": future_date,
            "short_code": "offer2024"
        },
        "6. WITH EXPIRATION DATE"
    )
    
    # 7. Advanced usage with all features
    space_id = str(uuid4())
    pixel_id_1 = str(uuid4())
    pixel_id_2 = str(uuid4())
    
    print_curl_command(
        "POST", "/api/v1/links/",
        {
            "url": "https://example.com/marketing/campaign/landing",
            "space_id": space_id,
            "domain_id": "short.ly",
            "short_code": "campaign2024",
            "title": "Marketing Campaign 2024",
            "description": "Main landing page for our 2024 marketing campaign",
            "tags": ["marketing", "campaign", "2024", "landing-page"],
            "password": "campaign_secret",
            "pixel_ids": [pixel_id_1, pixel_id_2],
            "expires_at": "2024-12-31T23:59:59"
        },
        "7. ADVANCED USAGE - All features (replace UUIDs with real ones)"
    )
    
    # 8. Get all links
    print_curl_command(
        "GET", "/api/v1/links/",
        description="8. GET ALL LINKS"
    )
    
    # 9. Get all links with pagination
    print_curl_command(
        "GET", "/api/v1/links/?skip=0&limit=10",
        description="9. GET LINKS WITH PAGINATION"
    )
    
    # 10. Get specific link
    link_id = str(uuid4())
    print_curl_command(
        "GET", f"/api/v1/links/{link_id}",
        description="10. GET SPECIFIC LINK (replace with actual link ID)"
    )
    
    # 11. Update link
    print_curl_command(
        "PUT", f"/api/v1/links/{link_id}",
        {
            "title": "Updated Title",
            "url": "https://updated-example.com"
        },
        "11. UPDATE LINK (replace with actual link ID)"
    )
    
    # 12. Deactivate link
    print_curl_command(
        "PUT", f"/api/v1/links/{link_id}",
        {"is_active": False},
        "12. DEACTIVATE LINK (replace with actual link ID)"
    )
    
    # 13. Delete link
    print_curl_command(
        "DELETE", f"/api/v1/links/{link_id}",
        description="13. DELETE LINK (replace with actual link ID)"
    )
    
    print("=" * 80)
    print("TESTING TIPS:")
    print("=" * 80)
    print("1. Start with the minimal request (#1) to test basic functionality")
    print("2. Get a JWT token first by authenticating with the auth endpoints")
    print("3. Replace 'YOUR_JWT_TOKEN_HERE' with your actual token")
    print("4. Replace UUID placeholders with real IDs from your database")
    print("5. Test validation by sending invalid data (empty URLs, bad short codes)")
    print("6. Use the GET endpoints to verify your created links")
    print("7. Check the response format matches the documented schema")
    print("=" * 80)

def generate_postman_collection():
    """Generate a basic Postman collection structure."""
    
    collection = {
        "info": {
            "name": "Link Shortener API",
            "description": "Comprehensive test collection for Link API",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "auth": {
            "type": "bearer",
            "bearer": [{"key": "token", "value": "{{jwt_token}}", "type": "string"}]
        },
        "variable": [
            {"key": "base_url", "value": "http://localhost:8000"},
            {"key": "jwt_token", "value": "YOUR_JWT_TOKEN_HERE"}
        ],
        "item": [
            {
                "name": "Create Link - Minimal",
                "request": {
                    "method": "POST",
                    "header": [{"key": "Content-Type", "value": "application/json"}],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({"url": "https://example.com/very/long/url"}, indent=2)
                    },
                    "url": "{{base_url}}/api/v1/links/"
                }
            },
            {
                "name": "Create Link - Advanced",
                "request": {
                    "method": "POST",
                    "header": [{"key": "Content-Type", "value": "application/json"}],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({
                            "url": "https://example.com/marketing/campaign",
                            "title": "Marketing Campaign 2024",
                            "description": "Main landing page",
                            "tags": ["marketing", "campaign"],
                            "short_code": "campaign2024"
                        }, indent=2)
                    },
                    "url": "{{base_url}}/api/v1/links/"
                }
            },
            {
                "name": "Get All Links",
                "request": {
                    "method": "GET",
                    "url": "{{base_url}}/api/v1/links/"
                }
            }
        ]
    }
    
    print("\n" + "=" * 80)
    print("POSTMAN COLLECTION (save as .json file)")
    print("=" * 80)
    print(json.dumps(collection, indent=2))

if __name__ == "__main__":
    generate_test_examples()
    
    # Uncomment to also generate Postman collection
    # generate_postman_collection()