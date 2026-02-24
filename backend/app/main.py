"""
FastAPI Main Application Entry Point

WHAT IS THIS FILE?
==================
This is where your FastAPI application is created and configured.
Think of it as the "main()" function for your API server.

HOW TO RUN THIS:
================
    cd backend
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import our API routers
from app.api.v1 import ingredients, routines, advisor, auth

# Import database setup
from app.db.database import engine, Base
from app.db import models  # noqa: F401 - Import so SQLAlchemy knows about our models

# =============================================================================
# CREATE THE APP
# =============================================================================

app = FastAPI(
    title="MixMyRoutine API",
    description="""
    An intelligent skincare API that uses Knowledge-Based AI to:
    
    * **Check ingredient compatibility** - Find conflicts and synergies
    * **Build optimized routines** - Get proper product ordering
    * **Answer skincare questions** - Natural language advisor
    
    ## KBAI Concepts Used
    
    - Frame-based knowledge representation
    - Semantic networks (ingredient graphs)
    - Constraint satisfaction (routine building)
    - Case-based reasoning (recommendations)
    """,
    version="1.0.0",
    docs_url="/docs",        # Swagger UI at /docs
    redoc_url="/redoc",      # Alternative docs at /redoc
)


# =============================================================================
# CORS MIDDLEWARE
# =============================================================================
# CORS = Cross-Origin Resource Sharing
# 
# WHY DO WE NEED THIS?
# When your React frontend (localhost:3000) tries to call your 
# FastAPI backend (localhost:8000), the browser blocks it by default.
# This is a security feature called "Same-Origin Policy".
#
# CORS middleware tells the browser: "It's okay, let requests from
# these origins through."

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # React dev server
        "http://localhost:5173",      # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,           # Allow cookies
    allow_methods=["*"],              # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],              # Allow all headers
)


# =============================================================================
# INCLUDE ROUTERS
# =============================================================================
# Routers let you organize your endpoints into separate files.
# The "prefix" adds a path prefix to all routes in that router.
# The "tags" group endpoints together in the documentation.

app.include_router(
    ingredients.router,
    prefix="/api/v1/ingredients",
    tags=["Ingredients"]
)

app.include_router(
    routines.router,
    prefix="/api/v1/routines",
    tags=["Routines"]
)

app.include_router(
    advisor.router,
    prefix="/api/v1/advisor",
    tags=["Advisor"]
)

app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Auth"]
)


# =============================================================================
# DATABASE STARTUP
# =============================================================================
# Create all database tables when the app starts.
# Base.metadata.create_all() checks which tables exist and creates missing ones.
#
# NOTE: In production, you'd use Alembic migrations instead of create_all().
# create_all() is fine for development and portfolio projects.

@app.on_event("startup")
async def startup():
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)


# =============================================================================
# ROOT ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint - confirms the API is running."""
    return {
        "message": "Welcome to the MixMyRoutine API",
        "tagline": "Mix smarter, glow better✨",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint - used by deployment platforms."""
    return {"status": "healthy"}