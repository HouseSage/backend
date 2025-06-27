"""
Pytest configuration and fixtures for testing the application.
"""
import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from uuid import uuid4

from app.models import models
from app.db.database import Base, engine, SessionLocal

# Test configuration
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def db_engine():
    """Fixture for database engine with test database."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield engine
    # Drop all tables after tests complete
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(db_engine):
    """Fixture for database session with automatic rollback after each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def mock_db():
    """Fixture for a mocked database session."""
    return MagicMock(spec=Session)

@pytest.fixture
def test_user():
    """Fixture for a test user."""
    return models.User(
        id=uuid4(),
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
    )

@pytest.fixture
def test_space(test_user):
    """Fixture for a test space."""
    return models.Space(
        id=uuid4(),
        name="Test Space",
        owner_id=test_user.id,
        is_active=True,
    )

@pytest.fixture
def test_domain():
    """Fixture for a test domain."""
    return models.Domain(
        domain="example.com",
        is_active=True,
        is_verified=True,
    )

@pytest.fixture
def test_link(test_space, test_domain):
    """Fixture for a test link."""
    return models.Link(
        id=uuid4(),
        space_id=test_space.id,
        domain_id=test_domain.domain,
        short_code="test123",
        is_active=True,
        link_data={
            "url": "https://example.com",
            "title": "Test Link",
            "description": "A test link",
            "tags": ["test"],
            "clicks": 0
        }
    )
