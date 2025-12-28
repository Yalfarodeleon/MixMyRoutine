"""
Routine Builder Module

KBAI Concepts Implemented:
- Constraint Satisfaction: Building routines that respect all rules
- Planning: Sequencing products in correct order
- Diagnostic Reasoning: Identifying issues in existing routines

HCI Concepts:
- Error Prevention: Warn before adding conflicting products
- Clear Feedback: Explain why a routine does/doesn't work
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from app.core.knowledge.ingredients import (
    IngredientKnowledgeGraph,
    Ingredient,
    TimeOfDay,
    SkinProfile,
    SkinConcern,
    InteractionType
)


class RoutineTime(Enum):
    """Morning or evening routine."""
    AM = "morning"
    PM = "evening"


@dataclass
class RoutineStep:
    """A single step in a skincare routine."""
    order: int
    product_name: str
    ingredients: list[str]  # ingredient IDs
    wait_after: int = 0  # minutes to wait before next step
    notes: str = ""


@dataclass
class RoutineAnalysis:
    """Results of analyzing a routine."""
    is_valid: bool
    conflicts: list[dict]
    cautions: list[dict]
    synergies: list[dict]
    ordering_issues: list[str]
    missing_essentials: list[str]
    suggestions: list[str]


@dataclass
class Routine:
    """A complete skincare routine (AM or PM)."""
    time: RoutineTime
    steps: list[RoutineStep] = field(default_factory=list)
    
    def get_all_ingredients(self) -> list[str]:
        """Get flat list of all ingredient IDs in routine."""
        ingredients = []
        for step in self.steps:
            ingredients.extend(step.ingredients)
        return ingredients


class RoutineBuilder:
    """Builds and validates skincare routines.
    
    KBAI: This is essentially a constraint satisfaction problem.
    We need to find a valid arrangement of products that:
    1. Has no conflicts
    2. Is in correct order (thin→thick, water→oil)
    3. Respects time-of-day restrictions
    4. Includes wait times where needed
    """
    
    # Standard order for skincare products
    # Lower number = apply first
    STANDARD_ORDER = {
        "cleanser": 1,
        "toner": 2,
        "essence": 3,
        "serum_water": 4,  # water-based serums
        "serum_active": 5,  # actives like retinol, vitamin C
        "serum_oil": 6,  # oil-based serums
        "eye_cream": 7,
        "moisturizer": 8,
        "face_oil": 9,
        "sunscreen": 10,  # AM only, always last
        "sleeping_mask": 10,  # PM only, always last
    }
    
    def __init__(self, knowledge_graph: IngredientKnowledgeGraph):
        self.kg = knowledge_graph
    
    def analyze_routine(self, routine: Routine, profile: Optional[SkinProfile] = None) -> RoutineAnalysis:
        """Analyze a routine for conflicts, issues, and improvements.
        
        KBAI: Diagnostic reasoning - identify problems and their causes.
        """
        all_ingredients = routine.get_all_ingredients()
        
        # Check ingredient compatibility
        compatibility = self.kg.check_compatibility(all_ingredients)
        
        # Check ordering
        ordering_issues = self._check_ordering(routine)
        
        # Check for missing essentials
        missing = self._check_missing_essentials(routine, profile)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(routine, compatibility, profile)
        
        return RoutineAnalysis(
            is_valid=len(compatibility['conflicts']) == 0 and len(ordering_issues) == 0,
            conflicts=compatibility['conflicts'],
            cautions=compatibility['cautions'],
            synergies=compatibility['synergies'],
            ordering_issues=ordering_issues,
            missing_essentials=missing,
            suggestions=suggestions
        )
    
    def _check_ordering(self, routine: Routine) -> list[str]:
        """Check if products are in correct order."""
        issues = []
        
        for i, step in enumerate(routine.steps):
            for j, later_step in enumerate(routine.steps[i+1:], i+1):
                # Get application orders for ingredients
                step_order = self._get_step_order(step)
                later_order = self._get_step_order(later_step)
                
                if step_order > later_order:
                    issues.append(
                        f"'{step.product_name}' (step {i+1}) should come after "
                        f"'{later_step.product_name}' (step {j+1})"
                    )
        
        return issues
    
    def _get_step_order(self, step: RoutineStep) -> float:
        """Get the application order for a step based on its ingredients."""
        if not step.ingredients:
            return 5  # Default middle order
        
        orders = []
        for ing_id in step.ingredients:
            ingredient = self.kg.get_ingredient(ing_id)
            if ingredient:
                orders.append(ingredient.application_order)
        
        return min(orders) if orders else 5
    
    def _check_missing_essentials(self, routine: Routine, profile: Optional[SkinProfile]) -> list[str]:
        """Check for missing essential steps."""
        missing = []
        all_ingredients = routine.get_all_ingredients()
        
        # SPF is essential for AM routine
        if routine.time == RoutineTime.AM:
            has_spf = any(
                self.kg.get_ingredient(ing_id) and 
                self.kg.get_ingredient(ing_id).category.value == "sunscreen"
                for ing_id in all_ingredients
            )
            if not has_spf:
                missing.append("Sunscreen (SPF) - essential for morning routine")
        
        # Moisturizer is essential
        has_moisturizer = any(
            self.kg.get_ingredient(ing_id) and 
            self.kg.get_ingredient(ing_id).category.value in ["moisturizer", "ceramide"]
            for ing_id in all_ingredients
        )
        if not has_moisturizer:
            missing.append("Moisturizer - needed to maintain skin barrier")
        
        return missing
    
    def _generate_suggestions(
        self, 
        routine: Routine, 
        compatibility: dict,
        profile: Optional[SkinProfile]
    ) -> list[str]:
        """Generate improvement suggestions."""
        suggestions = []
        
        # Suggest wait times
        for wait_pair in compatibility.get('wait_times', []):
            suggestions.append(
                f"Wait 20-30 minutes between {wait_pair['ingredient_a']} "
                f"and {wait_pair['ingredient_b']}"
            )
        
        # Suggest alternatives for conflicts
        for conflict in compatibility.get('conflicts', []):
            suggestions.append(
                f"Consider removing one of: {conflict['ingredient_a']} or "
                f"{conflict['ingredient_b']}. {conflict.get('recommendation', '')}"
            )
        
        # Profile-based suggestions
        if profile:
            if SkinConcern.AGING in profile.concerns:
                all_ings = routine.get_all_ingredients()
                has_retinoid = any(
                    self.kg.get_ingredient(ing) and 
                    self.kg.get_ingredient(ing).category.value == "retinoid"
                    for ing in all_ings
                )
                if not has_retinoid and routine.time == RoutineTime.PM:
                    suggestions.append(
                        "Consider adding a retinoid for anti-aging (PM routine only)"
                    )
        
        return suggestions
    
    def build_routine(
        self,
        products: list[dict],  # [{"name": "...", "ingredients": [...]}]
        time: RoutineTime,
        profile: Optional[SkinProfile] = None
    ) -> tuple[Routine, RoutineAnalysis]:
        """Build an optimized routine from a list of products.
        
        KBAI: Planning - arrange products to satisfy all constraints.
        """
        # Sort products by application order
        sorted_products = sorted(
            products,
            key=lambda p: self._get_product_order(p['ingredients'])
        )
        
        # Build steps
        steps = []
        for i, product in enumerate(sorted_products):
            # Check if this product is appropriate for the time of day
            time_ok, time_note = self._check_time_appropriateness(
                product['ingredients'], time
            )
            
            # Calculate wait time needed after this step
            wait_time = self._calculate_wait_time(
                product['ingredients'],
                sorted_products[i+1]['ingredients'] if i+1 < len(sorted_products) else []
            )
            
            step = RoutineStep(
                order=i + 1,
                product_name=product['name'],
                ingredients=product['ingredients'],
                wait_after=wait_time,
                notes=time_note if not time_ok else ""
            )
            steps.append(step)
        
        routine = Routine(time=time, steps=steps)
        analysis = self.analyze_routine(routine, profile)
        
        return routine, analysis
    
    def _get_product_order(self, ingredient_ids: list[str]) -> float:
        """Get application order for a product based on its ingredients."""
        if not ingredient_ids:
            return 5
        
        orders = []
        for ing_id in ingredient_ids:
            ingredient = self.kg.get_ingredient(ing_id)
            if ingredient:
                orders.append(ingredient.application_order)
        
        return min(orders) if orders else 5
    
    def _check_time_appropriateness(
        self, 
        ingredient_ids: list[str], 
        time: RoutineTime
    ) -> tuple[bool, str]:
        """Check if ingredients are appropriate for time of day."""
        for ing_id in ingredient_ids:
            ingredient = self.kg.get_ingredient(ing_id)
            if not ingredient:
                continue
            
            if time == RoutineTime.AM:
                if ingredient.time_of_day == TimeOfDay.PM_ONLY:
                    return False, f"{ingredient.name} should only be used at night"
            else:  # PM
                if ingredient.time_of_day == TimeOfDay.AM_ONLY:
                    return False, f"{ingredient.name} should only be used in the morning"
        
        return True, ""
    
    def _calculate_wait_time(
        self, 
        current_ingredients: list[str],
        next_ingredients: list[str]
    ) -> int:
        """Calculate recommended wait time between products."""
        max_wait = 0
        
        for curr_id in current_ingredients:
            for next_id in next_ingredients:
                interaction = self.kg.get_interaction(curr_id, next_id)
                if interaction and interaction.wait_minutes:
                    max_wait = max(max_wait, interaction.wait_minutes)
        
        return max_wait
    
    def suggest_routine(
        self, 
        profile: SkinProfile, 
        time: RoutineTime,
        budget: str = "moderate"  # "minimal", "moderate", "comprehensive"
    ) -> list[dict]:
        """Suggest a routine based on skin profile.
        
        KBAI: Case-based reasoning - recommend based on profile matching.
        """
        suggestions = []
        
        # Always include basics
        suggestions.append({
            "step": "Cleanser",
            "why": "Removes dirt, oil, and products",
            "ingredients": ["cleanser"],
            "priority": "essential"
        })
        
        # Get recommended ingredients for concerns
        recommended = self.kg.get_recommended_ingredients(profile)
        
        # Filter by time of day
        time_appropriate = [
            ing for ing in recommended
            if (time == RoutineTime.AM and ing.time_of_day != TimeOfDay.PM_ONLY) or
               (time == RoutineTime.PM and ing.time_of_day != TimeOfDay.AM_ONLY)
        ]
        
        # Add treatments based on concerns
        added_categories = set()
        for ingredient in time_appropriate[:5]:  # Limit to avoid overcomplicating
            if ingredient.category not in added_categories:
                concerns_addressed = [
                    c.value for c in ingredient.addresses_concerns 
                    if c in profile.concerns
                ]
                suggestions.append({
                    "step": f"Treatment: {ingredient.name}",
                    "why": f"Addresses: {', '.join(concerns_addressed)}",
                    "ingredients": [ingredient.id],
                    "priority": "recommended"
                })
                added_categories.add(ingredient.category)
        
        # Always include moisturizer
        suggestions.append({
            "step": "Moisturizer",
            "why": "Maintains skin barrier and hydration",
            "ingredients": ["ceramides", "hyaluronic_acid"],
            "priority": "essential"
        })
        
        # SPF for morning
        if time == RoutineTime.AM:
            suggestions.append({
                "step": "Sunscreen (SPF 30+)",
                "why": "Protects from UV damage - the #1 anti-aging step",
                "ingredients": ["spf"],
                "priority": "essential"
            })
        
        return suggestions


class RoutineAnalyzer:
    """Analyzes existing routines and provides detailed feedback.
    
    KBAI: Diagnostic reasoning - like a doctor examining symptoms.
    """
    
    def __init__(self, knowledge_graph: IngredientKnowledgeGraph):
        self.kg = knowledge_graph
        self.builder = RoutineBuilder(knowledge_graph)
    
    def analyze_ingredient_list(self, ingredient_names: list[str]) -> dict:
        """Analyze a list of ingredients (e.g., from a product).
        
        Returns detailed breakdown of what's in the list.
        """
        found = []
        not_found = []
        
        for name in ingredient_names:
            ingredient = self.kg.get_ingredient(name)
            if ingredient:
                found.append({
                    "name": ingredient.name,
                    "id": ingredient.id,
                    "category": ingredient.category.value,
                    "concerns_addressed": [c.value for c in ingredient.addresses_concerns],
                    "caution_for": [s.value for s in ingredient.caution_skin_types]
                })
            else:
                not_found.append(name)
        
        # Check compatibility among found ingredients
        found_ids = [f["id"] for f in found]
        compatibility = self.kg.check_compatibility(found_ids)
        
        return {
            "identified_ingredients": found,
            "unrecognized": not_found,
            "compatibility": compatibility,
            "summary": self._generate_summary(found, compatibility)
        }
    
    def _generate_summary(self, found: list[dict], compatibility: dict) -> str:
        """Generate a human-readable summary."""
        lines = []
        
        if compatibility['conflicts']:
            lines.append(f"⚠️ Found {len(compatibility['conflicts'])} ingredient conflict(s)")
        
        if compatibility['synergies']:
            lines.append(f"✨ Found {len(compatibility['synergies'])} beneficial combination(s)")
        
        concerns = set()
        for ing in found:
            concerns.update(ing['concerns_addressed'])
        
        if concerns:
            lines.append(f"📋 This addresses: {', '.join(sorted(concerns))}")
        
        return "\n".join(lines) if lines else "No notable interactions found."
    
    def compare_products(self, product_a: list[str], product_b: list[str]) -> dict:
        """Compare two products to see if they can be used together."""
        all_ingredients = product_a + product_b
        compatibility = self.kg.check_compatibility(all_ingredients)
        
        return {
            "can_use_together": compatibility['is_compatible'],
            "conflicts": compatibility['conflicts'],
            "cautions": compatibility['cautions'],
            "synergies": compatibility['synergies'],
            "recommendation": self._generate_combination_advice(compatibility)
        }
    
    def _generate_combination_advice(self, compatibility: dict) -> str:
        """Generate advice for using products together."""
        if compatibility['conflicts']:
            return "These products should NOT be used together in the same routine."
        
        if compatibility['cautions']:
            return "These can be used together with caution. Consider using on alternate days if irritation occurs."
        
        if compatibility['synergies']:
            return "Great combination! These products complement each other well."
        
        return "No known interactions. Should be safe to use together."