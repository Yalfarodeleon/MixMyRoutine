"""
Security Utilities: JWT Tokens & Password Hashing

HOW AUTH WORKS (THE BIG PICTURE):
=================================

  1. REGISTER:
     User sends email + password
     → We hash the password with bcrypt
     → Store email + hash in database
     
  2. LOGIN:
     User sends email + password
     → We find the user by email
     → We verify password against stored hash
     → If correct, we create a JWT token and return it
     
  3. AUTHENTICATED REQUESTS:
     User sends request with JWT in Authorization header
     → We decode the JWT to get the user_id
     → We look up the user in the database
     → If valid, we allow the request

WHY JWT (JSON Web Tokens)?
==========================
- Stateless: The server doesn't need to store sessions
- Scalable: Works with multiple server instances
- Self-contained: The token carries the user's identity
- Industry standard: Used by most modern APIs

A JWT looks like: xxxxx.yyyyy.zzzzz (three parts separated by dots)
- Header:  Algorithm used (e.g., HS256)
- Payload: Data (e.g., user_id, expiration time)
- Signature: Proves the token wasn't tampered with
"""

import os
import uuid as uuid_module
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User


# =============================================================================
# CONFIGURATION
# =============================================================================

# SECRET_KEY: Used to sign JWT tokens. In production, use a long random string
# stored in environment variables. NEVER commit real secrets to git!
SECRET_KEY = os.getenv("SECRET_KEY", "insecure-local-dev-key-only")

# ALGORITHM: HS256 = HMAC with SHA-256. Industry standard for JWT signing.
ALGORITHM = "HS256"

# Token expires after 30 minutes. User must re-login after this.
# Short expiration = more secure (less time for stolen tokens to be used)
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# =============================================================================
# PASSWORD HASHING
# =============================================================================
# CryptContext handles password hashing with bcrypt.
#
# WHY BCRYPT?
# - Intentionally slow (prevents brute-force attacks)
# - Adds a random "salt" (same password → different hash each time)
# - Industry standard for password storage
#
# WHAT IS HASHING?
# Hashing is a ONE-WAY function:
#   "password123" → "$2b$12$LJ3m4x..." (can't reverse this!)
# To check a login, we hash the attempt and compare hashes.

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain-text password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if a plain-text password matches a stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


# =============================================================================
# JWT TOKEN CREATION
# =============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    The "sub" (subject) claim is a JWT standard for "who this token is for".
    We store the user's UUID as a string in this field.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# =============================================================================
# TOKEN VERIFICATION & USER EXTRACTION
# =============================================================================

# OAuth2PasswordBearer tells FastAPI where to find the token.
# tokenUrl="api/v1/auth/login" = The endpoint where users get tokens.
# This also adds a "lock" icon in Swagger UI for testing auth.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Extract and validate the current user from a JWT token.
    
    This is a FastAPI DEPENDENCY — inject it into any endpoint that
    requires authentication:
    
        @router.get("/protected")
        async def protected_route(user: User = Depends(get_current_user)):
            return {"message": f"Hello {user.email}"}
    
    HOW IT WORKS:
    1. FastAPI extracts the token from the Authorization header
    2. We decode the JWT and extract the user_id ("sub" claim)
    3. We convert the string to a UUID object (needed for SQLite in tests)
    4. We look up the user in the database
    5. If anything fails, we return 401 Unauthorized
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract the user ID from the "sub" claim
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Convert string to UUID object for SQLAlchemy compatibility
        # PostgreSQL handles both strings and UUID objects fine,
        # but SQLite (used in tests) needs a proper UUID object.
        user_uuid = uuid_module.UUID(user_id)
            
    except (JWTError, ValueError):
        # JWTError = token is invalid, expired, or tampered with
        # ValueError = someone put a non-UUID string in the "sub" field
        raise credentials_exception
    
    # Look up the user in the database
    user = db.query(User).filter(User.id == user_uuid).first()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    return user