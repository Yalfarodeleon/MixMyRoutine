"""
Ingredients API Router

WHAT IS A ROUTER?
=================
A router is a way to organize related endpoints together.
Instead of putting ALL endpoints in main.py, we group them:
- All ingredient-related endpoints go here
- All routine-related endpoints go in routines.py
- etc.

This makes the code easier to navigate and maintain.

HOW ROUTERS WORK:
=================
1. Create a router with APIRouter()
2. Add endpoints to it with @router.get(), @router.post(), etc.
3. Include the router in main.py with app.include_router()

The prefix in main.py ("/api/v1/ingredients") gets added to all routes here.
So @router.get("/") becomes GET /api/v1/ingredients/
And @router.get("/{ingredient_id}") becomes GET /api/v1/ingredients/{ingredient_id}
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

# Import our schemas (request/response models)
from app.schemas.models import (
    CompatibilityCheckRequest,
    CompatibilityCheckResponse,
    InteractionResponse,
    IngredientSummary,
    IngredientDetail,
    InteractionTypeEnum
)

# Import our KBAI knowledge graph
from app.core.knowledge.ingredients import (
    create_skincare_knowledge_base,
    IngredientKnowledgeGraph,
    InteractionType
)

# =============================================================================
# CREATE ROUTER AND KNOWLEDGE GRAPH
# =============================================================================

router = APIRouter()

# Create the knowledge graph once when the module loads
# In a real app, you might use dependency injection instead
_knowledge_graph: Optional[IngredientKnowledgeGraph] = None


def get_knowledge_graph() -> IngredientKnowledgeGraph:
    """
    Get or create the knowledge graph.
    
    WHY A FUNCTION?
    ---------------
    This pattern is called "lazy initialization". We only create
    the knowledge graph when it's first needed, not when the 
    module is imported.
    
    In a larger app, you'd use FastAPI's dependency injection
    system instead (see Depends()).
    """
    global _knowledge_graph
    if _knowledge_graph is None:
        _knowledge_graph = create_skincare_knowledge_base()
    return _knowledge_graph


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/", response_model=list[IngredientSummary])
async def list_ingredients(
    category: Optional[str] = Query(None, description="Filter by category"),
    concern: Optional[str] = Query(None, description="Filter by skin concern"),
    search: Optional[str] = Query(None, description="Search by name")
):
    """
    List all ingredients with optional filtering.
    
    WHAT ARE Query() PARAMETERS?
    ----------------------------
    Query() defines URL query parameters (the ?key=value part).
    Example: GET /api/v1/ingredients?category=retinoid&search=ret
    
    - Optional[str] means the parameter is optional
    - None is the default if not provided
    - description shows up in the API docs
    """
    kg = get_knowledge_graph()
    results = []
    
    for ing_id, ingredient in kg.ingredients.items():
        # Apply filters
        if category and ingredient.category.value != category:
            continue
        
        if concern:
            concern_values = [c.value for c in ingredient.addresses_concerns]
            if concern not in concern_values:
                continue
        
        if search and search.lower() not in ingredient.name.lower():
            # Also check aliases
            if not any(search.lower() in alias.lower() for alias in ingredient.aliases):
                continue
        
        results.append(IngredientSummary(
            id=ingredient.id,
            name=ingredient.name,
            category=ingredient.category.value,
            beginner_friendly=ingredient.beginner_friendly
        ))
    
    return sorted(results, key=lambda x: x.name)


@router.get("/{ingredient_id}", response_model=IngredientDetail)
async def get_ingredient(ingredient_id: str):
    """
    Get detailed information about a specific ingredient.
    
    WHAT IS {ingredient_id}?
    ------------------------
    This is a "path parameter". The value in the URL becomes
    the ingredient_id argument.
    
    Example: GET /api/v1/ingredients/retinol
    → ingredient_id = "retinol"
    
    WHAT IS HTTPException?
    ----------------------
    When something goes wrong, we raise an HTTPException.
    FastAPI converts this to a proper HTTP error response.
    
    - status_code=404 means "Not Found"
    - detail is the error message sent to the client
    """
    kg = get_knowledge_graph()
    
    # Try to find by ID first, then by name
    ingredient = kg.get_ingredient(ingredient_id)
    
    if not ingredient:
        raise HTTPException(
            status_code=404,
            detail=f"Ingredient '{ingredient_id}' not found"
        )
    
    return IngredientDetail(
        id=ingredient.id,
        name=ingredient.name,
        category=ingredient.category.value,
        aliases=ingredient.aliases,
        description=ingredient.description,
        how_it_works=ingredient.how_it_works,
        usage_tips=ingredient.usage_tips,
        time_of_day=ingredient.time_of_day.value,
        addresses_concerns=[c.value for c in ingredient.addresses_concerns],
        caution_skin_types=[s.value for s in ingredient.caution_skin_types],
        beginner_friendly=ingredient.beginner_friendly,
        max_concentration=ingredient.max_concentration
    )


@router.post("/check", response_model=CompatibilityCheckResponse)
async def check_compatibility(request: CompatibilityCheckRequest):
    """
    Check compatibility between multiple ingredients.
    
    WHAT IS @router.post()?
    -----------------------
    POST is used when you're sending data TO the server.
    The data comes in the request body as JSON.
    
    WHY POST INSTEAD OF GET?
    ------------------------
    GET requests put data in the URL (?ingredients=a&ingredients=b)
    POST requests put data in the body (cleaner for complex data)
    
    Convention:
    - GET = fetching data (no side effects)
    - POST = sending data (may have side effects)
    
    WHAT IS response_model?
    -----------------------
    This tells FastAPI what the response looks like.
    FastAPI will:
    1. Validate that your return value matches the schema
    2. Convert it to JSON
    3. Document it in Swagger UI
    """
    kg = get_knowledge_graph()
    
    # Resolve ingredient names to IDs
    ingredient_ids = []
    for name_or_id in request.ingredients:
        ing = kg.get_ingredient(name_or_id)
        if ing:
            ingredient_ids.append(ing.id)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown ingredient: '{name_or_id}'"
            )
    
    # Run the compatibility check (this is your KBAI logic!)
    result = kg.check_compatibility(ingredient_ids)
    
    # Convert to response schema
    def convert_interaction(interaction_dict: dict) -> InteractionResponse:
        """Helper to convert internal format to API response."""
        # Map internal InteractionType to API enum
        type_mapping = {
            "conflicts": InteractionTypeEnum.CONFLICTS,
            "caution": InteractionTypeEnum.CAUTION,
            "synergizes": InteractionTypeEnum.SYNERGIZES,
            "wait": InteractionTypeEnum.REQUIRES_WAITING,
            "deactivates": InteractionTypeEnum.DEACTIVATES,
            "sensitizing": InteractionTypeEnum.INCREASES_SENSITIVITY,
        }
        
        raw_type = interaction_dict.get("interaction_type", "caution")
        if hasattr(raw_type, 'value'):
            raw_type = raw_type.value
        
        return InteractionResponse(
            ingredient_a=interaction_dict["ingredient_a"],
            ingredient_b=interaction_dict["ingredient_b"],
            interaction_type=type_mapping.get(raw_type, InteractionTypeEnum.CAUTION),
            severity=interaction_dict.get("severity", 5),
            explanation=interaction_dict.get("explanation", ""),
            recommendation=interaction_dict.get("recommendation", "")
        )
    
    return CompatibilityCheckResponse(
        is_compatible=result["is_compatible"],
        conflicts=[convert_interaction(c) for c in result.get("conflicts", [])],
        cautions=[convert_interaction(c) for c in result.get("cautions", [])],
        synergies=[convert_interaction(s) for s in result.get("synergies", [])],
        wait_times=result.get("wait_times", [])
    )


# =============================================================================
# WHAT YOU SHOULD UNDERSTAND
# =============================================================================
#
# 1. ROUTERS organize related endpoints
#
# 2. PATH PARAMETERS ({ingredient_id}) come from the URL
#
# 3. QUERY PARAMETERS (?category=x) come from Query()
#
# 4. REQUEST BODY comes from Pydantic models (for POST/PUT)
#
# 5. RESPONSE_MODEL validates and documents the response
#
# 6. HTTPException returns proper HTTP error codes
#
# TRY IT:
# 1. Run the server: uvicorn app.main:app --reload
# 2. Go to http://localhost:8000/docs
# 3. Click "GET /api/v1/ingredients" and try it
# 4. Click "POST /api/v1/ingredients/check" and try it