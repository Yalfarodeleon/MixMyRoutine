"""
Advisor API Endpoint with LLM Support

This endpoint uses Claude API for intelligent responses,
falling back to rule-based answers if no API key is set.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import os

from app.core.knowledge.ingredients import create_skincare_knowledge_base
from app.core.agent.advisor import SkincareAdvisor, QueryResult

router = APIRouter(prefix="/advisor", tags=["advisor"])

# Initialize knowledge base and advisor
kb = create_skincare_knowledge_base()
advisor = SkincareAdvisor(
    knowledge_graph=kb,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


class AdvisorQuestionRequest(BaseModel):
    """Request to ask the advisor a question."""
    question: str = Field(..., min_length=3, max_length=500, description="Your skincare question")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Can I use retinol with vitamin C?"
            }
        }


class AdvisorResponse(BaseModel):
    """Response from the advisor."""
    answer: str
    confidence: float = Field(..., ge=0, le=1)
    sources: list[str] = []
    follow_up_questions: list[str] = []
    llm_powered: bool = False  # Whether response used Claude API


@router.post("/ask", response_model=AdvisorResponse)
async def ask_advisor(request: AdvisorQuestionRequest):
    """
    Ask the skincare advisor a question.
    
    The advisor uses:
    1. Knowledge Graph with 26 ingredients and 41 interactions
    2. Claude API for natural, intelligent responses (if API key is set)
    
    Example questions:
    - "Can I use retinol with vitamin C?"
    - "What should I use for acne?"
    - "What is niacinamide?"
    - "What order should I apply my products?"
    """
    try:
        result: QueryResult = advisor.ask(request.question)
        
        return AdvisorResponse(
            answer=result.answer,
            confidence=result.confidence,
            sources=result.sources,
            follow_up_questions=result.follow_up_questions,
            llm_powered=advisor.client is not None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@router.get("/example-questions")
async def get_example_questions():
    """Get example questions to help users get started."""
    return {
        "compatibility": [
            "Can I use retinol with vitamin C?",
            "Can I mix niacinamide and vitamin C?",
            "Is it safe to use AHA with retinol?",
        ],
        "ingredient_info": [
            "What is niacinamide?",
            "What does retinol do?",
            "Tell me about hyaluronic acid",
        ],
        "concern_based": [
            "What should I use for acne?",
            "What ingredients help with aging?",
            "What's good for dry skin?",
        ],
        "routine": [
            "What order should I apply vitamin C and niacinamide?",
            "Should I use retinol in the morning or night?",
            "How do I layer my skincare?",
        ]
    }


@router.get("/status")
async def get_advisor_status():
    """Check if the advisor is using LLM or rule-based mode."""
    return {
        "llm_enabled": advisor.client is not None,
        "model": "claude-sonnet-4-20250514" if advisor.client else None,
        "knowledge_base": {
            "ingredients": len(kb.ingredients),
            "interactions": kb.graph.number_of_edges()
        }
    }