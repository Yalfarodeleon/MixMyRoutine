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

    