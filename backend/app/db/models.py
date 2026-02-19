"""
Database Models (SQLAlchemy ORM)

WHAT IS AN ORM?
===============
ORM = Object-Relational Mapper. It lets you work with database tables
as Python classes. Instead of writing SQL, you write Python:

    SQL:    SELECT * FROM user WHERE email = 'alice@test.com';
    ORM:    db.query(User).filter(User.email == 'alice@test.com').first()

HOW IT MAPS:
===========
    Python Class     ->  Database Table
    Class Attribute  ->  Column
    Class Instance   ->  Row
"""


import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.database import Base


# =============================================================================
# USER MODEL
# =============================================================================
# This creates a "users" table in PostgreSQL.
#
# Each Column() call defines a column in the table:
#   Column(Type, constraints...)
#
# WHY UUID FOR IDS?
# Sequential IDs (1, 2, 3) leak information (e.g., "only 50 users?").
# UUIDs are random and don't reveal ordering or count.

class User(Base):
    """
    Represents a registered user.

    TABLE: users
    COLUMNS: id, email, hashed_password, created_at, updated_at, is_active
    """
    __tablename__ = "users"

    # Primary key - UUID generated automatically
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # Email - must be unique (no two users with same email)
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True  # Index = faster lookup by email
    )

    # Hashed password - NEVER store plain text passwords!
    hashed_password = Column(String(255), nullable=False)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Soft delete flag (deactivate instead of deleting)
    is_active = Column(Boolean, default=True, nullable=False)

    # ---------------------------------------------------------------------------
    # RELATIONSHIP: User has one Profile
    # ---------------------------------------------------------------------------
    # This creates a virtual link between User and UserProfile.
    # It doesn't add a column - it lets you do: user.profile
    #
    # back_populates: Creates a two-way link (profile.user works too)
    # uselist=False:  One-to-one relationship (not one-to-many)
    # cascade:        If user is deleted, delete their profile too

    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email}"
    

# =============================================================================
# USER PROFILE MODEL
# =============================================================================
# Stores the user's skincare profile (skin type, concerns, favorites).
# Seperated from User to keep auth data and profile clean.

class UserProfile(Base):
    """
    Stores a user's skincare preferences.

    TABLE: user_profiles

    WHY SEPERATE FROM USER?
    Single Resposibility: User table handles auth (email, password).
    Profile table handles skincare data. This is cleaner and lets you
    update profile data without touching auth data.
    """
    __tablename__ = "user_profiles"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Foreign key linking this profile to a user
    # ForeignKey("users.id") means this column references users.id
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,    # One profile per user
        nullable=False
    )

    # Skincare data
    skin_type = Column(String(50), nullable=True)

    #JSON type - stores a list of strings as JSON
    # e.g., ["acne", "dryness", "aging"]
    concerns = Column(JSON, default=list)

    # Favorite ingredient IDs
    # e.g., ["niacinamide", "hyaluronic_acid", "vitamin_c"]
    favorite_ingredients = Column(JSON, default=list)

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Back-reference to user
    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile user_id={self.user_id} skin_type={self.skin_type}>"