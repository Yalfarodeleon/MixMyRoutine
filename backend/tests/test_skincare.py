"""
Tests for the Skincare Advisor

These tests demonstrate:
1. Knowledge graph stores ingredients correctly
2. Interaction detection works (conflicts, synergies)
3. Routine builder validates combinations
4. Advisor agent classifies and answers questions
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from knowledge.ingredients import (
    IngredientKnowledgeGraph,
    create_skincare_knowledge_base,
    SkinProfile,
    SkinType,
    SkinConcern,
    InteractionType
)
from routines.builder import RoutineBuilder, RoutineTime
from agent.advisor import SkincareAdvisor, QueryType


class TestKnowledgeGraph:
    """Tests for ingredient knowledge representation."""
    
    @pytest.fixture
    def kg(self):
        return create_skincare_knowledge_base()
    
    def test_has_ingredients(self, kg):
        """Knowledge base should have ingredients."""
        assert len(kg.ingredients) > 0
        assert "retinol" in kg.ingredients
    
    def test_get_by_name(self, kg):
        """Should find ingredients by name."""
        ing = kg.get_ingredient("Retinol")
        assert ing is not None
        assert ing.id == "retinol"
    
    def test_get_by_alias(self, kg):
        """Should find ingredients by alias."""
        ing = kg.get_ingredient("vitamin a")
        assert ing is not None
        assert ing.id == "retinol"
    
    def test_detects_conflict(self, kg):
        """Should detect retinol + glycolic acid conflict."""
        interaction = kg.get_interaction("retinol", "glycolic_acid")
        assert interaction is not None
        assert interaction.interaction_type == InteractionType.CONFLICTS
    
    def test_detects_synergy(self, kg):
        """Should detect beneficial combinations."""
        interaction = kg.get_interaction("niacinamide", "hyaluronic_acid")
        assert interaction is not None
        assert interaction.interaction_type == InteractionType.SYNERGIZES
    
    def test_compatibility_check(self, kg):
        """Should check multiple ingredients at once."""
        result = kg.check_compatibility(["retinol", "glycolic_acid"])
        assert not result['is_compatible']
        assert len(result['conflicts']) > 0


class TestRoutineBuilder:
    """Tests for routine building and validation."""
    
    @pytest.fixture
    def builder(self):
        kg = create_skincare_knowledge_base()
        return RoutineBuilder(kg)
    
    def test_detects_conflict_in_routine(self, builder):
        """Should flag conflicting products."""
        products = [
            {"name": "Retinol Serum", "ingredients": ["retinol"]},
            {"name": "Glycolic Toner", "ingredients": ["glycolic_acid"]}
        ]
        routine, analysis = builder.build_routine(products, RoutineTime.PM)
        assert not analysis.is_valid
    
    def test_approves_valid_routine(self, builder):
        """Should approve compatible products."""
        products = [
            {"name": "HA Serum", "ingredients": ["hyaluronic_acid"]},
            {"name": "Niacinamide", "ingredients": ["niacinamide"]}
        ]
        routine, analysis = builder.build_routine(products, RoutineTime.PM)
        assert analysis.is_valid
    
    def test_flags_missing_spf(self, builder):
        """Should flag missing SPF in morning routine."""
        products = [
            {"name": "Vitamin C", "ingredients": ["vitamin_c"]}
        ]
        routine, analysis = builder.build_routine(products, RoutineTime.AM)
        assert any("SPF" in m or "Sunscreen" in m for m in analysis.missing_essentials)


class TestAdvisor:
    """Tests for the AI advisor agent."""
    
    @pytest.fixture
    def advisor(self):
        kg = create_skincare_knowledge_base()
        return SkincareAdvisor(kg)
    
    def test_classifies_compatibility_question(self, advisor):
        """Should recognize compatibility questions."""
        result = advisor.ask("Can I use retinol with vitamin C?")
        assert result.query_type == QueryType.COMPATIBILITY
    
    def test_classifies_ingredient_question(self, advisor):
        """Should recognize ingredient info questions."""
        result = advisor.ask("What is niacinamide?")
        assert result.query_type == QueryType.INGREDIENT_INFO
    
    def test_answers_with_confidence(self, advisor):
        """Should provide confident answers for known questions."""
        result = advisor.ask("Can I use retinol with glycolic acid?")
        assert result.confidence > 0.5
        assert "conflict" in result.answer.lower() or "not" in result.answer.lower()
    
    def test_suggests_followups(self, advisor):
        """Should suggest follow-up questions."""
        result = advisor.ask("What is retinol?")
        assert len(result.follow_up_questions) > 0


class TestSkinProfile:
    """Tests for personalized recommendations."""
    
    @pytest.fixture
    def kg(self):
        return create_skincare_knowledge_base()
    
    def test_recommends_for_acne(self, kg):
        """Should recommend acne-fighting ingredients."""
        profile = SkinProfile(
            skin_type=SkinType.OILY,
            concerns=[SkinConcern.ACNE]
        )
        recommended = kg.get_recommended_ingredients(profile)
        ids = [ing.id for ing in recommended]
        assert "salicylic_acid" in ids or "benzoyl_peroxide" in ids
    
    def test_respects_sensitive_skin(self, kg):
        """Should avoid irritating ingredients for sensitive skin."""
        profile = SkinProfile(
            skin_type=SkinType.SENSITIVE,
            concerns=[SkinConcern.AGING]
        )
        recommended = kg.get_recommended_ingredients(profile)
        for ing in recommended:
            assert SkinType.SENSITIVE not in ing.caution_skin_types


# Run with: pytest tests/test_skincare.py -v
