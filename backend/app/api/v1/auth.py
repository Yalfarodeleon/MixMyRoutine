"""
Auth API Endpoints

  POST /api/v1/auth/register  → Create a new account
  POST /api/v1/auth/login     → Log in and get a JWT token
  GET  /api/v1/auth/me        → Get current user info (requires auth)
  PUT  /api/v1/auth/profile   → Update skincare profile (requires auth)
  GET  /api/v1/auth/profile   → Get skincare profile (requires auth)

AUTHENTICATION FLOW:
====================
1. User registers with email + password
2. User logs in → receives JWT token
3. User sends token in Authorization header for protected endpoints
4. Server decodes token to identify the user

DEPENDENCY INJECTION:
=====================
Notice how endpoints receive `db` and `current_user` as parameters.
FastAPI's Depends() system automatically:
- Creates a database session (get_db)
- Extracts and validates the JWT token (get_current_user)
- Passes the results to your function
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User, UserProfile
from app.core.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    ProfileUpdateRequest,
    TokenResponse,
    UserResponse,
    UserWithProfileResponse,
    ProfileResponse,
    MessageResponse,
)

# Create the router with a prefix tag for Swagger docs grouping
router = APIRouter()


# =============================================================================
# REGISTER
# =============================================================================

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new account",
)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    WHAT HAPPENS:
    1. Check if email is already taken
    2. Hash the password (NEVER store plain text!)
    3. Create the User record
    4. Create an empty UserProfile
    5. Generate a JWT token
    6. Return the token + user data
    
    The user is automatically logged in after registration
    (they get a token back immediately).
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists"
        )
    
    # Create user with hashed password
    user = User(
        email=request.email,
        hashed_password=hash_password(request.password)
    )
    db.add(user)
    db.flush()  # Assigns the user.id without committing yet
    
    # Create empty profile (user can fill it in later)
    profile = UserProfile(user_id=user.id)
    db.add(profile)
    
    # Commit both user and profile together (atomic operation)
    db.commit()
    db.refresh(user)  # Refresh to get the generated id, created_at, etc.
    
    # Generate JWT token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


# =============================================================================
# LOGIN
# =============================================================================

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in with email and password",
)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate a user and return a JWT token.
    
    SECURITY NOTE:
    We use the same error message for "user not found" and "wrong password"
    to prevent email enumeration attacks. An attacker can't figure out
    which emails are registered by trying to log in and reading errors.
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    
    # Verify password (same error for not found OR wrong password)
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # Generate JWT token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


# =============================================================================
# GET CURRENT USER
# =============================================================================

@router.get(
    "/me",
    response_model=UserWithProfileResponse,
    summary="Get current user info",
)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Return the currently authenticated user's data and profile.
    
    HOW THIS WORKS:
    1. Client sends: Authorization: Bearer <token>
    2. get_current_user decodes the token and fetches the user
    3. If valid, current_user is the User object from the database
    4. If invalid, FastAPI returns 401 before this function even runs
    """
    return UserWithProfileResponse.model_validate(current_user)


# =============================================================================
# UPDATE PROFILE
# =============================================================================

@router.put(
    "/profile",
    response_model=ProfileResponse,
    summary="Update skincare profile",
)
async def update_profile(
    request: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the current user's skincare profile.
    Only updates fields that are provided (not None).
    """
    profile = current_user.profile
    
    # Create profile if it doesn't exist yet
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    
    # Update only provided fields
    # exclude_unset=True means: only include fields the client actually sent
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    
    return ProfileResponse.model_validate(profile)


# =============================================================================
# GET PROFILE
# =============================================================================

@router.get(
    "/profile",
    response_model=ProfileResponse,
    summary="Get skincare profile",
)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get the current user's skincare profile."""
    if not current_user.profile:
        return ProfileResponse()
    
    return ProfileResponse.model_validate(current_user.profile)