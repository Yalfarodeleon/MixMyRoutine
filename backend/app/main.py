"""
FastAPI Main Application Entry Point

WHAT IS THIS FILE?
==================
This is where your FastAPI application is created and configured.
Think of it as the "main()" function for your API server.

WHAT IS FASTAPI?
================
FastAPI is a modern Python web framework for building APIs.
- It automatically generates documentation (Swagger UI)
- It validates incoming data using Pydantic
- It's very fast (hence the name)

HOW TO RUN THIS:
================
    cd backend
    uvicorn app.main:app --reload

This command means:
- uvicorn: The server that runs your app (like waitress for a restaurant)
- app.main:app: Look in app/main.py for a variable called "app"
- --reload: Restart automatically when you change code (dev only)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import our API routers (we'll create these next)
from app.api.v1 import ingredients, routines, advisor

# =============================================================================
# CREATE THE APP
# =============================================================================
# FastAPI() creates your application instance
# All the parameters here are for the auto-generated documentation

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
# Instead of putting ALL endpoints in main.py, we split them:
#   - ingredients.py → /api/v1/ingredients/*
#   - routines.py    → /api/v1/routines/*
#   - advisor.py     → /api/v1/advisor/*
#
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


# =============================================================================
# ROOT ENDPOINTS
# =============================================================================
# These are simple endpoints that don't need their own router file.

@app.get("/")
async def root():
    """
    Root endpoint - just confirms the API is running.
    
    WHAT IS @app.get("/")?
    ----------------------
    This is a "decorator" that tells FastAPI:
    "When someone makes a GET request to /, run this function"
    
    WHAT IS async def?
    ------------------
    async def means this function can run asynchronously.
    This is useful when you have slow operations (database, external APIs).
    For now, just know that FastAPI prefers async functions.
    """
    return {
        "message": "Welcome to the MixMyRoutine API",
        "tagline": "Mix smarter, glow better✨",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint - used by deployment platforms to verify the app is running.
    
    WHY HAVE A HEALTH CHECK?
    ------------------------
    When you deploy to platforms like Railway, Render, or Kubernetes,
    they periodically ping /health to make sure your app hasn't crashed.
    If it returns anything other than 200 OK, they restart your app.
    """
    return {"status": "healthy"}


# =============================================================================
# WHAT HAPPENS WHEN YOU RUN THIS?
# =============================================================================
# 
# 1. Python reads this file and creates the FastAPI app
# 2. uvicorn starts a web server and hands requests to your app
# 3. When a request comes in:
#    - FastAPI matches the URL to a route (e.g., GET /health)
#    - It runs the function for that route
#    - It converts the return value to JSON
#    - It sends the response back
#
# TRY IT:
# 1. Run: uvicorn app.main:app --reload
# 2. Open: http://localhost:8000 (see the root response)
# 3. Open: http://localhost:8000/docs (see Swagger UI)
# 4. Open: http://localhost:8000/health (see health check)