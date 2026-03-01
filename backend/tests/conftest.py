"""
Test Configuration (conftest.py)

WHAT IS THIS?
=============
conftest.py is a special pytest file that provides shared fixtures.
Fixtures are reusable setup/teardown functions for tests.

WHY SQLITE FOR TESTS?
=====================
Auth tests need a real database, but we don't want to use our
production PostgreSQL. Instead, we use SQLite file-based DB:
- No Docker required for testing
- Isolated (each test gets a fresh database)
- Fast and simple
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import Base, get_db


# =============================================================================
# TEST DATABASE
# =============================================================================
# SQLite file-based database for tests.
# "check_same_thread=False" is needed because FastAPI uses multiple threads.

SQLALCHEMY_TEST_URL = "sqlite:///./test.db"

test_engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False}
)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Provide a test database session."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture(autouse=True)
def setup_database():
    """
    Create all tables before each test, drop them after.
    
    autouse=True means this runs automatically for EVERY test.
    This ensures each test starts with a clean database.
    """
    # Override the get_db dependency to use test database
    app.dependency_overrides[get_db] = override_get_db
    
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    yield  # Test runs here
    
    # Drop all tables after test
    Base.metadata.drop_all(bind=test_engine)
    
    # Clean up override
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    """Provide a test client for making API requests."""
    return TestClient(app)


@pytest.fixture
def registered_user(client):
    """
    Create and return a registered user with their token.
    
    This fixture is useful for tests that need an authenticated user
    without repeating the registration logic.
    """
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "testpassword123"
    })
    data = response.json()
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "token": data["access_token"],
        "user": data["user"],
    }


@pytest.fixture
def auth_headers(registered_user):
    """Provide Authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {registered_user['token']}"}