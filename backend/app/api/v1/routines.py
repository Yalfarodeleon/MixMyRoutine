"""
Routines API Router

This handles building and analyzing skincare routines.
The core logic uses Constraint Satisfaction to ensure:
- No conflicting ingredients
- Correct application order
- Proper wait times between products
"""

from fastapi import APIRouter, HTTPException
from typing import Optional

from app.schemas.models import (
    RoutineBuildRequest,
    RoutineResponse,
    RoutineStepResponse,
    InteractionResponse,
    InteractionTypeEnum,
    SkinConcernEnum
)

from app.core.knowledge.ingredients import (
    create_skincare_knowledge_base,
    IngredientKnowledgeGraph,
    SkinProfile,
    SkinType,
    SkinConcern
)
from app.core.routines.builder import RoutineBuilder, RoutineTime

router = APIRouter()

# Reuse the knowledge graph (in production, use proper dependency injection)
_knowledge_graph: Optional[IngredientKnowledgeGraph] = None
_routine_builder: Optional[RoutineBuilder] = None


def get_knowledge_graph() -> IngredientKnowledgeGraph:
    global _knowledge_graph
    if _knowledge_graph is None:
        _knowledge_graph = create_skincare_knowledge_base()
    return _knowledge_graph


def get_routine_builder() -> RoutineBuilder:
    global _routine_builder
    if _routine_builder is None:
        _routine_builder = RoutineBuilder(get_knowledge_graph())
    return _routine_builder


@router.post("/build", response_model=RoutineResponse)
async def build_routine(request: RoutineBuildRequest):
    """
    Build an optimized skincare routine.
    
    This endpoint:
    1. Takes your products and their ingredients
    2. Checks for conflicts between products
    3. Determines the optimal application order
    4. Adds wait times where needed
    5. Suggests missing essentials (like SPF for AM)
    
    KBAI CONCEPT: CONSTRAINT SATISFACTION
    -------------------------------------
    Building a routine is a Constraint Satisfaction Problem (CSP):
    - Variables: Which products to use
    - Constraints: 
        - No conflicts allowed
        - Must apply in correct order (thin → thick)
        - Time-of-day restrictions (retinol = PM only)
        - Wait times between certain ingredients
    
    The routine builder satisfies all these constraints to produce
    a valid routine.
    """
    builder = get_routine_builder()
    kg = get_knowledge_graph()
    
    # Convert request products to internal format
    products = []
    for product in request.products:
        # Validate ingredients exist
        valid_ingredients = []
        for ing_name in product.ingredients:
            ing = kg.get_ingredient(ing_name)
            if ing:
                valid_ingredients.append(ing.id)
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unknown ingredient '{ing_name}' in product '{product.name}'"
                )
        
        products.append({
            "name": product.name,
            "ingredients": valid_ingredients,
            "ingredient_names": product.ingredients
        })
    
    # Convert profile if provided
    profile = None
    if request.profile:
        profile = SkinProfile(
            skin_type=SkinType(request.profile.skin_type.value),
            concerns=[SkinConcern(c.value) for c in request.profile.concerns]
        )
    
    # Build the routine
    time = RoutineTime.AM if request.time.value == "am" else RoutineTime.PM
    routine, analysis = builder.build_routine(products, time, profile)
    
    # Convert interactions to response format
    def convert_interaction(interaction_dict: dict) -> InteractionResponse:
        type_mapping = {
            "conflicts": InteractionTypeEnum.CONFLICTS,
            "caution": InteractionTypeEnum.CAUTION,
            "synergizes": InteractionTypeEnum.SYNERGIZES,
        }
        raw_type = interaction_dict.get("interaction_type", "caution")
        if hasattr(raw_type, 'value'):
            raw_type = raw_type.value
        
        return InteractionResponse(
            ingredient_a=interaction_dict.get("ingredient_a", ""),
            ingredient_b=interaction_dict.get("ingredient_b", ""),
            interaction_type=type_mapping.get(raw_type, InteractionTypeEnum.CAUTION),
            severity=interaction_dict.get("severity", 5),
            explanation=interaction_dict.get("explanation", ""),
            recommendation=interaction_dict.get("recommendation", "")
        )
    
    # Build response
    steps = [
        RoutineStepResponse(
            order=step.order,
            product_name=step.product_name,
            ingredients=list(step.ingredients) if hasattr(step.ingredients, '__iter__') else [],
            wait_after=step.wait_after,
            notes=step.notes
        )
        for step in routine.steps
    ]
    
    return RoutineResponse(
        steps=steps,
        is_valid=analysis.is_valid,
        conflicts=[convert_interaction(c) for c in analysis.conflicts],
        cautions=[convert_interaction(c) for c in analysis.cautions],
        synergies=[convert_interaction(s) for s in analysis.synergies],
        missing_essentials=analysis.missing_essentials,
        suggestions=analysis.suggestions
    )


@router.post("/suggest")
async def suggest_routine(profile: Optional[dict] = None):
    """
    Get a suggested routine based on skin profile.
    
    KBAI CONCEPT: CASE-BASED REASONING
    ----------------------------------
    This uses case-based reasoning to suggest routines:
    1. Look at the user's skin type and concerns
    2. Find ingredients that address those concerns
    3. Avoid ingredients that are problematic for their skin type
    4. Build a routine from those ingredients
    
    It's like saying: "People with similar skin to you found these
    ingredients helpful."
    """
    # TODO: Implement case-based reasoning for routine suggestions
    return {
        "message": "Routine suggestion endpoint - coming soon",
        "hint": "This will use case-based reasoning to suggest routines based on your skin profile"
    }
