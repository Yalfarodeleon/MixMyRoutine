"""
Advisor API Router

This handles natural language questions about skincare.
The core logic uses pattern matching and knowledge retrieval.
"""

from fastapi import APIRouter
from typing import Optional

from app.schemas.models import (
    AdvisorQuestionRequest,
    AdvisorResponse,
    SkinProfileRequest
)

from app.core.knowledge.ingredients import (
    create_skincare_knowledge_base,
    IngredientKnowledgeGraph,
    SkinProfile,
    SkinType,
    SkinConcern
)
from app.core.agent.advisor import SkincareAdvisor

router = APIRouter()

# Module-level instances (use dependency injection in production)
_knowledge_graph: Optional[IngredientKnowledgeGraph] = None
_advisor: Optional[SkincareAdvisor] = None


def get_knowledge_graph() -> IngredientKnowledgeGraph:
    global _knowledge_graph
    if _knowledge_graph is None:
        _knowledge_graph = create_skincare_knowledge_base()
    return _knowledge_graph


def get_advisor() -> SkincareAdvisor:
    global _advisor
    if _advisor is None:
        _advisor = SkincareAdvisor(get_knowledge_graph())
    return _advisor


@router.post("/ask", response_model=AdvisorResponse)
async def ask_advisor(request: AdvisorQuestionRequest):
    """
    Ask a skincare question in natural language.
    
    Examples:
    - "Can I use retinol with vitamin C?"
    - "What should I use for acne?"
    - "What order should I apply my products?"
    - "Is niacinamide good for oily skin?"
    
    KBAI CONCEPTS USED:
    -------------------
    
    1. NATURAL LANGUAGE UNDERSTANDING
       The advisor classifies questions into types:
       - Compatibility questions ("Can I use X with Y?")
       - Ingredient info questions ("What is X?")
       - Concern-based questions ("What should I use for acne?")
       - Routine questions ("What order should I apply?")
    
    2. KNOWLEDGE RETRIEVAL
       Based on the question type, it retrieves relevant knowledge:
       - Compatibility → Look up interaction between ingredients
       - Ingredient info → Retrieve ingredient frame
       - Concern-based → Map concern to recommended ingredients
    
    3. DIAGNOSTIC REASONING
       For concern-based questions, it maps:
       Symptom (acne) → Cause (excess sebum, bacteria) → Solution (salicylic acid, niacinamide)
    """
    advisor = get_advisor()
    
    # Convert profile if provided
    profile = None
    if request.profile:
        profile = SkinProfile(
            skin_type=SkinType(request.profile.skin_type.value),
            concerns=[SkinConcern(c.value) for c in request.profile.concerns]
        )
    
    # Ask the advisor (this is your KBAI logic!)
    result = advisor.ask(request.question, profile)
    
    return AdvisorResponse(
        answer=result.answer,
        confidence=result.confidence,
        query_type=result.query_type.value if hasattr(result.query_type, 'value') else str(result.query_type),
        sources=result.sources,
        follow_up_questions=result.follow_up_questions
    )


@router.get("/example-questions")
async def get_example_questions():
    """
    Get example questions to help users understand what they can ask.
    
    This is a UX feature - helping users discover the system's capabilities.
    """
    return {
        "compatibility": [
            "Can I use retinol with vitamin C?",
            "Is niacinamide safe with AHA?",
            "Can I mix benzoyl peroxide and salicylic acid?",
            "What happens if I use glycolic acid with retinol?"
        ],
        "ingredient_info": [
            "What is retinol?",
            "How does niacinamide work?",
            "Tell me about hyaluronic acid",
            "What does vitamin C do for skin?"
        ],
        "recommendations": [
            "What should I use for acne?",
            "What's good for anti-aging?",
            "What ingredients help with hyperpigmentation?",
            "What's best for dry skin?"
        ],
        "routine": [
            "What order should I apply my products?",
            "Should I use vitamin C in the morning or night?",
            "How long should I wait between products?"
        ]
    }
