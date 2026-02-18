"""
Database Connection & Session Management

WHAT IS THIS?
=============
This file sets up the connection between the FastAPI app and PostgreSQL.
It uses SQLAlchemy, which is Python's most popular ORM (Object-Relational Mapper).

KEY CONCEPTS:
=============
1. ENGINE: The connection to the database (like opening a phone line)
2. SESSION: A conversation with the database (like a phone call)
3. BASE: The parent class for all of the database models

HOW SESSIONS WORK:
==================
Each API request gets its own session (via get_db dependency).
When the request finishes, the session is automatically closed.
This prevents connection leaks and ensures data consistency.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# =============================================================================
# DATABASE URL
# =============================================================================
# Format: postgresql://username:password@host:port/database_name
#
# We read this from an environment variable so it can change between
# development (localhost) and production (Docker) without code changes.
#
# os.getenv("KEY", "default") = Read env var, use default if not set

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://mixmyroutine:mixmyroutine_secret@localhost:5432/mixmyroutine"
)

# =============================================================================
# CREATE ENGINE
# =============================================================================
# The engine manages the actual database connection pool.
#
# pool_pre_ping=True: Test connections before using them.
#   This prevents errors from stale connections (e.g., if PostgreSQL
#   restarts while your app is running).

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# =============================================================================
# SESSION FACTORY
# =============================================================================
# sessionmaker creates a factory that produces new Session objects.
#
# autocommit=False: You must explicitly commit changes (safer)
# autoflush=False:  Don't auto-sync Python objects to DB (more control)
# bind=engine:      Use our engine for database connections

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# =============================================================================
# DECLARATIVE BASE
# =============================================================================
# Base is the parent class for all database models.
# Any class that inherits from Base becomes a database table.

Base = declarative_base()


# =============================================================================
# DEPENDENCY: get_db
# =============================================================================
# This is a FastAPI "dependency" - a function that runs before your endpoint.
#
# HOW IT WORKS:
# 1. FastAPI calls get_db() before your endpoint runs
# 2. It creates a new database session
# 3. "yield" gives that session to the endpoint
# 4. After the endpoint finishes (or crashes), the "finally" block runs
# 5. The session is closed, returning the connection to the pool
#
# USAGE IN ENDPOINTS:
#   @router.get("/users/me")
#   async def get_me(db: Session = Depends(get_db)):
#       user = db.query(User).filter(User.id == user_id).first()
#       return user

def get_db():
    """Provide a database session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()