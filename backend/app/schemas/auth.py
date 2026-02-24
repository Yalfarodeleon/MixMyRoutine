"""
Auth Schemas (Pydantic Models for Auth Endpoints)

WHAT IS THIS?
=============
These schemas define the shape of auth-related requests and responses.
They validate data coming in and structure data going out.

PATTERN:
========
- *Request schemas: What the client sends TO the API
- *Response schemas: What the API sends back TO the client

IMPORTANT:
==========
UserResponse does NOT include the password hash.
Password data is NEVER sent back to the client!
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class RegisterRequest(BaseModel):
    """
    Data needed to create a new account.
    
    EmailStr automatically validates email format:
        "user@example.com" → valid
        "not-an-email"     → rejected with clear error
    """
    email: EmailStr = Field(
        ...,
        description="User's email address",
        examples=["user@example.com"]
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Password (minimum 8 characters)",
        examples=["securepassword123"]
    )


class LoginRequest(BaseModel):
    """Data needed to log in."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class ProfileUpdateRequest(BaseModel):
    """
    Data for updating a user's skincare profile.
    All fields are optional — update only what you want.
    """
    skin_type: Optional[str] = Field(
        None,
        description="Skin type: dry, oily, combination, sensitive, normal"
    )
    concerns: Optional[list[str]] = Field(
        None,
        description="Skin concerns: acne, aging, dryness, etc."
    )
    favorite_ingredients: Optional[list[str]] = Field(
        None,
        description="List of favorite ingredient IDs"
    )


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class UserResponse(BaseModel):
    """
    User data returned to the client.
    
    NOTE: No password field! Never expose password hashes.
    
    model_config with from_attributes=True tells Pydantic:
    "You can create this from a SQLAlchemy model object"
    (SQLAlchemy uses attributes, not dict keys)
    """
    id: UUID
    email: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ProfileResponse(BaseModel):
    """User's skincare profile."""
    skin_type: Optional[str] = None
    concerns: list[str] = []
    favorite_ingredients: list[str] = []

    model_config = {"from_attributes": True}


class UserWithProfileResponse(BaseModel):
    """User data with their skincare profile attached."""
    id: UUID
    email: str
    is_active: bool
    created_at: datetime
    profile: Optional[ProfileResponse] = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """
    JWT token returned after successful login.
    
    WHY "Bearer"?
    The "Bearer" token type means:
    "Whoever bears (carries) this token gets access."
    It's sent in the Authorization header:
        Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
    """
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str