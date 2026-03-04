"""
Auth Endpoint Tests

Tests for registration, login, and profile management.
Each test starts with a clean database (see conftest.py).
"""


# =============================================================================
# REGISTRATION TESTS
# =============================================================================

class TestRegister:
    """Tests for POST /api/v1/auth/register"""

    def test_register_success(self, client):
        """New user can register with valid email and password."""
        response = client.post("/api/v1/auth/register", json={
            "email": "newuser@example.com",
            "password": "securepassword123"
        })
        
        assert response.status_code == 201
        data = response.json()
        
        # Should return a JWT token
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        # Should return user data (without password!)
        assert data["user"]["email"] == "newuser@example.com"
        assert "hashed_password" not in data["user"]

    def test_register_duplicate_email(self, client):
        """Cannot register with an email that's already taken."""
        # Register first user
        client.post("/api/v1/auth/register", json={
            "email": "taken@example.com",
            "password": "password123"
        })
        
        # Try to register with same email
        response = client.post("/api/v1/auth/register", json={
            "email": "taken@example.com",
            "password": "differentpassword"
        })
        
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    def test_register_invalid_email(self, client):
        """Cannot register with an invalid email format."""
        response = client.post("/api/v1/auth/register", json={
            "email": "not-an-email",
            "password": "password123"
        })
        
        assert response.status_code == 422  # Validation error

    def test_register_short_password(self, client):
        """Cannot register with a password shorter than 8 characters."""
        response = client.post("/api/v1/auth/register", json={
            "email": "user@example.com",
            "password": "short"
        })
        
        assert response.status_code == 422


# =============================================================================
# LOGIN TESTS
# =============================================================================

class TestLogin:
    """Tests for POST /api/v1/auth/login"""

    def test_login_success(self, client, registered_user):
        """Can log in with correct credentials."""
        response = client.post("/api/v1/auth/login", json={
            "email": registered_user["email"],
            "password": registered_user["password"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == registered_user["email"]

    def test_login_wrong_password(self, client, registered_user):
        """Cannot log in with wrong password."""
        response = client.post("/api/v1/auth/login", json={
            "email": registered_user["email"],
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_nonexistent_email(self, client):
        """Cannot log in with an email that doesn't exist."""
        response = client.post("/api/v1/auth/login", json={
            "email": "nobody@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]


# =============================================================================
# GET CURRENT USER TESTS
# =============================================================================

class TestGetMe:
    """Tests for GET /api/v1/auth/me"""

    def test_get_me_authenticated(self, client, auth_headers):
        """Authenticated user can get their own data."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "profile" in data

    def test_get_me_no_token(self, client):
        """Cannot access /me without a token."""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401

    def test_get_me_invalid_token(self, client):
        """Cannot access /me with an invalid token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer fake-token-here"}
        )
        
        assert response.status_code == 401


# =============================================================================
# PROFILE TESTS
# =============================================================================

class TestProfile:
    """Tests for GET/PUT /api/v1/auth/profile"""

    def test_get_empty_profile(self, client, auth_headers):
        """New user has an empty profile."""
        response = client.get("/api/v1/auth/profile", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["skin_type"] is None
        assert data["concerns"] == []
        assert data["favorite_ingredients"] == []

    def test_update_profile(self, client, auth_headers):
        """Can update skincare profile."""
        response = client.put("/api/v1/auth/profile", headers=auth_headers, json={
            "skin_type": "oily",
            "concerns": ["acne", "pores"],
            "favorite_ingredients": ["niacinamide", "salicylic_acid"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["skin_type"] == "oily"
        assert data["concerns"] == ["acne", "pores"]
        assert data["favorite_ingredients"] == ["niacinamide", "salicylic_acid"]

    def test_partial_profile_update(self, client, auth_headers):
        """Can update just one field without affecting others."""
        # First, set full profile
        client.put("/api/v1/auth/profile", headers=auth_headers, json={
            "skin_type": "oily",
            "concerns": ["acne"]
        })
        
        # Update only skin_type
        response = client.put("/api/v1/auth/profile", headers=auth_headers, json={
            "skin_type": "combination"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["skin_type"] == "combination"
        assert data["concerns"] == ["acne"]

    def test_profile_requires_auth(self, client):
        """Cannot access profile without authentication."""
        response = client.get("/api/v1/auth/profile")
        assert response.status_code == 401
        
        response = client.put("/api/v1/auth/profile", json={
            "skin_type": "oily"
        })
        assert response.status_code == 401