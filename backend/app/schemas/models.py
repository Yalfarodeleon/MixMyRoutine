"""
Pydantic Schemas for API Request/Response Validation

WHAT IS PYDANTIC?
=================
Pydantic is a data validation library. It lets you define the 
"shape" of your data, and automatically validates that incoming
data matches that shape.

WHY USE SCHEMAS?
================
1. VALIDATION: If someone sends bad data, they get a clear error
2. DOCUMENTATION: FastAPI uses these to generate API docs
3. TYPE HINTS: Your IDE knows what data you're working with
4. SERIALIZATION: Converts Python objects to JSON automatically

HOW IT WORKS:
=============
1. You define a class that inherits from BaseModel
2. You add attributes with type hints
3. Pydantic validates data against those types

Example:
    class User(BaseModel):
        name: str
        age: int
    
    # This works:
    user = User(name="Alice", age=30)
    
    # This raises an error (age must be int):
    user = User(name="Bob", age="thirty")
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================
# We recreate the enums here for the API layer.
# This keeps the API schemas independent from the core logic.

class SkinTypeEnum(str, Enum):
    """Skin types for user profile."""
    DRY = "dry"
    OILY = "oily"
    COMBINATION = "combination"
    SENSITIVE = "sensitive"
    NORMAL = "normal"


class SkinConcernEnum(str, Enum):
    """Skin concerns for recommendations."""
    ACNE = "acne"
    AGING = "aging"
    HYPERPIGMENTATION = "hyperpigmentation"
    DRYNESS = "dryness"
    OILINESS = "oiliness"
    SENSITIVITY = "sensitivity"
    DULLNESS = "dullness"
    TEXTURE = "texture"
    REDNESS = "redness"
    DARK_CIRCLES = "dark_circles"
    PORES = "pores"


class InteractionTypeEnum(str, Enum):
    """Types of ingredient interactions."""
    CONFLICTS = "conflicts"
    CAUTION = "caution"
    SYNERGIZES = "synergizes"
    REQUIRES_WAITING = "wait"
    DEACTIVATES = "deactivates"
    INCREASES_SENSITIVITY = "sensitizing"


class RoutineTimeEnum(str, Enum):
    """Time of day for routine."""
    AM = "am"
    PM = "pm"


# =============================================================================
# REQUEST SCHEMAS (What the client sends TO the API)
# =============================================================================

class CompatibilityCheckRequest(BaseModel):
    """
    Request body for checking ingredient compatibility.
    
    WHAT IS Field()?
    ----------------
    Field() lets you add extra validation and documentation:
    - min_length: Minimum number of items in list
    - description: Shows up in API docs
    - example: Shows as example in Swagger UI
    """
    ingredients: list[str] = Field(
        ...,  # ... means "required"
        min_length=2,
        description="List of ingredient IDs or names to check",
        example=["retinol", "vitamin_c"]
    )

    class Config:
        # This adds an example to the API docs
        json_schema_extra = {
            "example": {
                "ingredients": ["retinol", "vitamin_c", "niacinamide"]
            }
        }


class SkinProfileRequest(BaseModel):
    """User's skin profile for personalized recommendations."""
    skin_type: SkinTypeEnum = Field(
        default=SkinTypeEnum.NORMAL,
        description="Your skin type"
    )
    concerns: list[SkinConcernEnum] = Field(
        default=[],
        description="Your skin concerns"
    )


class ProductRequest(BaseModel):
    """A product with its key ingredients."""
    name: str = Field(..., description="Product name", example="CeraVe PM Moisturizer")
    ingredients: list[str] = Field(
        ...,
        min_length=1,
        description="Key ingredient IDs in this product",
        example=["niacinamide", "hyaluronic_acid", "ceramides"]
    )


class RoutineBuildRequest(BaseModel):
    """Request to build an optimized routine."""
    products: list[ProductRequest] = Field(
        ...,
        min_length=1,
        description="Products to include in routine"
    )
    time: RoutineTimeEnum = Field(
        default=RoutineTimeEnum.PM,
        description="Morning (AM) or evening (PM) routine"
    )
    profile: Optional[SkinProfileRequest] = Field(
        default=None,
        description="Optional skin profile for personalized suggestions"
    )


class AdvisorQuestionRequest(BaseModel):
    """Question for the skincare advisor."""
    question: str = Field(
        ...,
        min_length=3,
        description="Your skincare question",
        example="Can I use retinol with vitamin C?"
    )
    profile: Optional[SkinProfileRequest] = Field(
        default=None,
        description="Optional skin profile for personalized answers"
    )


# =============================================================================
# RESPONSE SCHEMAS (What the API sends back TO the client)
# =============================================================================

class InteractionResponse(BaseModel):
    """Details about an interaction between two ingredients."""
    ingredient_a: str
    ingredient_b: str
    interaction_type: InteractionTypeEnum
    severity: int = Field(..., ge=1, le=10, description="Severity from 1-10")
    explanation: str
    recommendation: str


class CompatibilityCheckResponse(BaseModel):
    """Response from compatibility check."""
    is_compatible: bool = Field(
        ...,
        description="True if no conflicts found"
    )
    conflicts: list[InteractionResponse] = Field(
        default=[],
        description="Ingredients that should NOT be used together"
    )
    cautions: list[InteractionResponse] = Field(
        default=[],
        description="Ingredients that CAN be used but with care"
    )
    synergies: list[InteractionResponse] = Field(
        default=[],
        description="Ingredients that work BETTER together"
    )
    wait_times: list[dict] = Field(
        default=[],
        description="Ingredients that need waiting time between applications"
    )


class IngredientSummary(BaseModel):
    """Brief ingredient info for lists."""
    id: str
    name: str
    category: str
    beginner_friendly: bool


class IngredientDetail(BaseModel):
    """Full ingredient details."""
    id: str
    name: str
    category: str
    aliases: list[str] = []
    description: str
    how_it_works: Optional[str] = None
    usage_tips: list[str] = []
    time_of_day: str
    addresses_concerns: list[str] = []
    caution_skin_types: list[str] = []
    beginner_friendly: bool
    max_concentration: Optional[str] = None


class RoutineStepResponse(BaseModel):
    """A single step in a routine."""
    order: int
    product_name: str
    ingredients: list[str]
    wait_after: int = Field(default=0, description="Minutes to wait before next step")
    notes: Optional[str] = None


class RoutineResponse(BaseModel):
    """A complete routine with analysis."""
    steps: list[RoutineStepResponse]
    is_valid: bool
    conflicts: list[InteractionResponse] = []
    cautions: list[InteractionResponse] = []
    synergies: list[InteractionResponse] = []
    missing_essentials: list[str] = []
    suggestions: list[str] = []


class AdvisorResponse(BaseModel):
    """Response from the skincare advisor."""
    answer: str
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    query_type: str
    sources: list[str] = Field(default=[], description="Knowledge sources used")
    follow_up_questions: list[str] = Field(
        default=[],
        description="Suggested follow-up questions"
    )


# =============================================================================
# WHY SEPARATE REQUEST AND RESPONSE SCHEMAS?
# =============================================================================
#
# You might wonder: why have CompatibilityCheckRequest AND 
# CompatibilityCheckResponse? Why not just one schema?
#
# ANSWER: They serve different purposes:
#
# REQUEST schemas define what the CLIENT sends:
#   - Often simpler (just IDs, not full objects)
#   - May have different validation (required fields)
#
# RESPONSE schemas define what the SERVER returns:
#   - Usually more detailed (full objects, not just IDs)
#   - Include computed fields (is_compatible)
#
# This separation is called "DTOs" (Data Transfer Objects) in other languages.