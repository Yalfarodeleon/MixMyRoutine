"""
Backend Tests for MixMyRoutine

These tests verify that the core functionality works correctly.
They run automatically on GitHub Actions when you push code.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

# Create a test client
client = TestClient(app)


# =============================================================================
# HEALTH CHECK TESTS
# =============================================================================

def test_root_endpoint():
    """Test that the root endpoint returns welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    assert "MixMyRoutine" in response.json()["message"]


def test_health_check():
    """Test that health check endpoint works."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# =============================================================================
# INGREDIENTS API TESTS
# =============================================================================

def test_list_ingredients():
    """Test that we can list all ingredients."""
    response = client.get("/api/v1/ingredients")
    assert response.status_code == 200
    
    ingredients = response.json()
    assert isinstance(ingredients, list)
    assert len(ingredients) > 0  # Should have ingredients
    
    # Check structure of first ingredient
    first = ingredients[0]
    assert "id" in first
    assert "name" in first
    assert "category" in first


def test_get_single_ingredient():
    """Test that we can get a specific ingredient."""
    response = client.get("/api/v1/ingredients/retinol")
    assert response.status_code == 200
    
    ingredient = response.json()
    assert ingredient["id"] == "retinol"
    assert "name" in ingredient
    assert "description" in ingredient


def test_get_nonexistent_ingredient():
    """Test that missing ingredients return 404."""
    response = client.get("/api/v1/ingredients/fake_ingredient_xyz")
    assert response.status_code == 404


# =============================================================================
# COMPATIBILITY CHECK TESTS
# =============================================================================

def test_compatibility_check_compatible():
    """Test checking compatible ingredients."""
    response = client.post(
        "/api/v1/ingredients/check",
        json={"ingredients": ["niacinamide", "hyaluronic_acid"]}
    )
    assert response.status_code == 200
    
    result = response.json()
    assert "is_compatible" in result
    assert "conflicts" in result
    assert "cautions" in result
    assert "synergies" in result


def test_compatibility_check_with_caution():
    """Test checking ingredients that have cautions."""
    response = client.post(
        "/api/v1/ingredients/check",
        json={"ingredients": ["retinol", "vitamin_c"]}
    )
    assert response.status_code == 200
    
    result = response.json()
    # Retinol + Vitamin C should have cautions
    assert len(result["cautions"]) > 0 or len(result["conflicts"]) > 0


def test_compatibility_check_invalid_ingredient():
    """Test that invalid ingredients return error."""
    response = client.post(
        "/api/v1/ingredients/check",
        json={"ingredients": ["retinol", "fake_ingredient"]}
    )
    assert response.status_code == 400


def test_compatibility_check_too_few_ingredients():
    """Test that we need at least 2 ingredients."""
    response = client.post(
        "/api/v1/ingredients/check",
        json={"ingredients": ["retinol"]}
    )
    assert response.status_code == 422  # Validation error


# =============================================================================
# ADVISOR API TESTS
# =============================================================================

def test_advisor_ask():
    """Test that we can ask the advisor questions."""
    response = client.post(
        "/api/v1/advisor/ask",
        json={"question": "Can I use retinol with vitamin C?"}
    )
    assert response.status_code == 200
    
    result = response.json()
    assert "answer" in result
    assert "confidence" in result
    assert len(result["answer"]) > 0


def test_advisor_example_questions():
    """Test that we can get example questions."""
    response = client.get("/api/v1/advisor/example-questions")
    assert response.status_code == 200
    
    result = response.json()
    assert isinstance(result, dict)
    assert len(result) > 0


# =============================================================================
# KNOWLEDGE BASE TESTS
# =============================================================================

def test_knowledge_base_has_ingredients():
    """Test that the knowledge base is populated."""
    from app.core.knowledge.ingredients import create_skincare_knowledge_base
    
    kb = create_skincare_knowledge_base()
    
    # Should have ingredients
    assert len(kb.ingredients) >= 20
    
    # Check a known ingredient exists
    assert "retinol" in kb.ingredients
    assert "vitamin_c" in kb.ingredients
    assert "niacinamide" in kb.ingredients


def test_knowledge_base_has_interactions():
    """Test that the knowledge base has interaction rules."""
    from app.core.knowledge.ingredients import create_skincare_knowledge_base
    
    kb = create_skincare_knowledge_base()
    
    # Should have edges (interactions) in the graph
    assert kb.graph.number_of_edges() > 0