"""
Ingredient Interactions Module

This module implements KBAI concepts for reasoning about ingredient relationships:
- Semantic network of conflicts and synergies
- Rule-based reasoning for compatibility checking
- Explanation generation for why interactions matter
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import networkx as nx

from .ingredients import Ingredient, SeverityLevel, create_ingredient_database


class InteractionType(Enum):
    """Types of relationships between ingredients."""
    CONFLICTS = "conflicts"
    SYNERGIZES = "synergizes"
    NEUTRALIZES = "neutralizes"
    SENSITIZES = "sensitizes"


@dataclass
class Interaction:
    """Represents a relationship between two ingredients.
    
    KBAI Principle: This is an edge in our semantic network,
    with properties that enable reasoning about combinations.
    """
    ingredient_a: str
    ingredient_b: str
    interaction_type: InteractionType
    severity: SeverityLevel
    explanation: str
    detailed_explanation: str = ""
    recommendation: str = ""
    can_alternate: bool = False
    wait_time_hours: Optional[int] = None
    mechanism: str = ""


class InteractionGraph:
    """Semantic network of ingredient interactions.
    
    KBAI Principle: Semantic networks represent knowledge as nodes
    (ingredients) and edges (interactions), enabling reasoning about
    compatibility and explanation generation.
    """
    
    def __init__(self):
        self.graph = nx.Graph()
        self.interactions: dict[tuple[str, str], Interaction] = {}
        self.ingredients = create_ingredient_database()
        self._build_interaction_graph()
    
    def _interaction_key(self, id_a: str, id_b: str) -> tuple[str, str]:
        """Create consistent key for interaction lookup."""
        return tuple(sorted([id_a, id_b]))
    
    def add_interaction(self, interaction: Interaction) -> None:
        """Add an interaction to the graph."""
        key = self._interaction_key(interaction.ingredient_a, interaction.ingredient_b)
        self.interactions[key] = interaction
        self.graph.add_edge(
            interaction.ingredient_a,
            interaction.ingredient_b,
            interaction_type=interaction.interaction_type,
            severity=interaction.severity,
            interaction=interaction
        )
    
    def get_interaction(self, id_a: str, id_b: str) -> Optional[Interaction]:
        """Get the interaction between two ingredients, if any."""
        key = self._interaction_key(id_a, id_b)
        return self.interactions.get(key)
    
    def check_compatibility(self, ingredient_ids: list[str]) -> list[dict]:
        """Check all pairwise interactions in a list of ingredients.
        Returns list of issues found, sorted by severity.
        """
        issues = []
        for i, id_a in enumerate(ingredient_ids):
            for id_b in ingredient_ids[i+1:]:
                interaction = self.get_interaction(id_a, id_b)
                if interaction and interaction.interaction_type == InteractionType.CONFLICTS:
                    ing_a = self.ingredients.get(id_a)
                    ing_b = self.ingredients.get(id_b)
                    issues.append({
                        "ingredient_a": ing_a.name if ing_a else id_a,
                        "ingredient_b": ing_b.name if ing_b else id_b,
                        "severity": interaction.severity,
                        "explanation": interaction.explanation,
                        "recommendation": interaction.recommendation,
                        "can_alternate": interaction.can_alternate,
                        "wait_time_hours": interaction.wait_time_hours
                    })
        
        severity_order = {SeverityLevel.SEVERE: 0, SeverityLevel.HIGH: 1, 
                         SeverityLevel.MODERATE: 2, SeverityLevel.LOW: 3}
        issues.sort(key=lambda x: severity_order.get(x["severity"], 99))
        return issues
    
    def get_synergies(self, ingredient_ids: list[str]) -> list[dict]:
        """Find beneficial combinations in a list of ingredients."""
        synergies = []
        for i, id_a in enumerate(ingredient_ids):
            for id_b in ingredient_ids[i+1:]:
                interaction = self.get_interaction(id_a, id_b)
                if interaction and interaction.interaction_type == InteractionType.SYNERGIZES:
                    ing_a = self.ingredients.get(id_a)
                    ing_b = self.ingredients.get(id_b)
                    synergies.append({
                        "ingredient_a": ing_a.name if ing_a else id_a,
                        "ingredient_b": ing_b.name if ing_b else id_b,
                        "explanation": interaction.explanation,
                        "benefit": interaction.detailed_explanation
                    })
        return synergies
    
    def get_all_conflicts_for(self, ingredient_id: str) -> list[dict]:
        """Get all known conflicts for a specific ingredient."""
        conflicts = []
        for (id_a, id_b), interaction in self.interactions.items():
            if interaction.interaction_type != InteractionType.CONFLICTS:
                continue
            other_id = id_b if id_a == ingredient_id else (id_a if id_b == ingredient_id else None)
            if other_id:
                other_ing = self.ingredients.get(other_id)
                conflicts.append({
                    "conflicts_with": other_ing.name if other_ing else other_id,
                    "conflicts_with_id": other_id,
                    "severity": interaction.severity,
                    "explanation": interaction.explanation
                })
        return conflicts
    
    def explain_interaction(self, id_a: str, id_b: str) -> dict:
        """Generate a detailed explanation of the interaction.
        KBAI Principle: Explainable AI - help users understand the reasoning.
        """
        interaction = self.get_interaction(id_a, id_b)
        ing_a = self.ingredients.get(id_a)
        ing_b = self.ingredients.get(id_b)
        
        if not interaction:
            return {
                "status": "compatible",
                "summary": f"{ing_a.name if ing_a else id_a} and {ing_b.name if ing_b else id_b} can generally be used together.",
                "details": "No known negative interactions.",
                "recommendation": "Apply in order of thinnest to thickest consistency."
            }
        
        status_map = {
            InteractionType.CONFLICTS: "conflict",
            InteractionType.SYNERGIZES: "synergy",
            InteractionType.NEUTRALIZES: "neutralizes",
            InteractionType.SENSITIZES: "sensitizes"
        }
        return {
            "status": status_map.get(interaction.interaction_type, "unknown"),
            "severity": interaction.severity.value,
            "summary": interaction.explanation,
            "details": interaction.detailed_explanation,
            "mechanism": interaction.mechanism,
            "recommendation": interaction.recommendation,
            "can_alternate": interaction.can_alternate,
            "wait_time_hours": interaction.wait_time_hours
        }
    
    def _build_interaction_graph(self) -> None:
        """Build the interaction graph with known ingredient relationships."""
        
        # ===== RETINOID CONFLICTS =====
        self.add_interaction(Interaction(
            ingredient_a="retinol", ingredient_b="glycolic_acid",
            interaction_type=InteractionType.CONFLICTS,
            severity=SeverityLevel.HIGH,
            explanation="Both are potent exfoliants that can compromise the skin barrier when combined.",
            detailed_explanation="Retinol and glycolic acid both increase cell turnover. Using them together significantly increases irritation, dryness, and barrier damage risk.",
            mechanism="Both increase keratinocyte turnover; combined effect overwhelms skin's repair capacity",
            recommendation="Use glycolic acid in the morning, retinol at night. Or alternate nights.",
            can_alternate=True, wait_time_hours=12
        ))
        
        self.add_interaction(Interaction(
            ingredient_a="retinol", ingredient_b="lactic_acid",
            interaction_type=InteractionType.CONFLICTS,
            severity=SeverityLevel.MODERATE,
            explanation="Both exfoliate and can cause irritation when combined.",
            detailed_explanation="Lactic acid is gentler than glycolic but still an exfoliant. May be tolerable for experienced users.",
            recommendation="Alternate nights, or use lactic acid AM and retinol PM.",
            can_alternate=True, wait_time_hours=12
        ))
        
        self.add_interaction(Interaction(
            ingredient_a="retinol", ingredient_b="salicylic_acid",
            interaction_type=InteractionType.CONFLICTS,
            severity=SeverityLevel.MODERATE,
            explanation="Both can dry and irritate skin, especially when starting out.",
            detailed_explanation="Can be used together by experienced users, but beginners should separate them.",
            recommendation="Use salicylic acid AM, retinol PM. Or alternate nights.",
            can_alternate=True, wait_time_hours=8
        ))
        
        self.add_interaction(Interaction(
            ingredient_a="retinol", ingredient_b="benzoyl_peroxide",
            interaction_type=InteractionType.CONFLICTS,
            severity=SeverityLevel.HIGH,
            explanation="Benzoyl peroxide can deactivate retinol, making it less effective.",
            detailed_explanation="Benzoyl peroxide oxidizes retinol, reducing its effectiveness. Both are also drying.",
            mechanism="Oxidation of retinol molecule by benzoyl peroxide's free radicals",
            recommendation="Use benzoyl peroxide in the morning, retinol at night. Never layer directly.",
            can_alternate=True, wait_time_hours=12
        ))
        
        self.add_interaction(Interaction(
            ingredient_a="tretinoin", ingredient_b="glycolic_acid",
            interaction_type=InteractionType.CONFLICTS,
            severity=SeverityLevel.SEVERE,
            explanation="Combining prescription retinoid with AHA risks serious irritation.",
            detailed_explanation="Tretinoin is much more potent than OTC retinol. Combining with glycolic dramatically increases risk of severe irritation and barrier damage.",
            recommendation="Avoid combining. If you must use both, alternate weeks.",
            can_alternate=True
        ))
        
        self.add_interaction(Interaction(
            ingredient_a="tretinoin", ingredient_b="benzoyl_peroxide",
            interaction_type=InteractionType.CONFLICTS,
            severity=SeverityLevel.SEVERE,
            explanation="Benzoyl peroxide degrades tretinoin on contact.",
            detailed_explanation="Studies show benzoyl peroxide oxidizes and deactivates tretinoin. This wastes your prescription.",
            mechanism="Oxidative degradation of tretinoin molecule",
            recommendation="Apply BP in morning only. Never layer together.",
            can_alternate=True, wait_time_hours=12
        ))
        
        # ===== VITAMIN C INTERACTIONS =====
        self.add_interaction(Interaction(
            ingredient_a="ascorbic_acid", ingredient_b="niacinamide",
            interaction_type=InteractionType.CONFLICTS,
            severity=SeverityLevel.LOW,
            explanation="Old formulation issue - mostly debunked but some flushing possible.",
            detailed_explanation="The concern about vitamin C and niacinamide is largely outdated. Modern formulations are stable together. Some users experience mild flushing.",
            recommendation="Generally safe to use together. If flushing occurs, use vitamin C AM and niacinamide PM.",
            can_alternate=True, wait_time_hours=0
        ))
        
        self.add_interaction(Interaction(
            ingredient_a="ascorbic_acid", ingredient_b="retinol",
            interaction_type=InteractionType.CONFLICTS,
            severity=SeverityLevel.MODERATE,
            explanation="Different optimal pH ranges may reduce effectiveness of both.",
            detailed_explanation="Vitamin C works best at pH 2.5-3.5, retinol at pH 5-6. Using together may reduce effectiveness. Also increases irritation risk.",
            mechanism="pH incompatibility affects stability and absorption",
            recommendation="Vitamin C in the morning (with sunscreen), retinol at night.",
            can_alternate=True, wait_time_hours=12
        ))
        
        self.add_interaction(Interaction(
            ingredient_a="ascorbic_acid", ingredient_b="benzoyl_peroxide",
            interaction_type=InteractionType.CONFLICTS,
            severity=SeverityLevel.HIGH,
            explanation="Benzoyl peroxide oxidizes vitamin C, making it ineffective.",
            detailed_explanation="Vitamin C is easily oxidized. Benzoyl peroxide is an oxidizing agent. Using together wastes your vitamin C serum.",
            mechanism="Oxidative degradation of ascorbic acid",
            recommendation="Never use together. Vitamin C AM, benzoyl peroxide PM if needed.",
            can_alternate=True, wait_time_hours=12
        ))
        
        # ===== AHA + BHA INTERACTIONS =====
        self.add_interaction(Interaction(
            ingredient_a="glycolic_acid", ingredient_b="salicylic_acid",
            interaction_type=InteractionType.CONFLICTS,
            severity=SeverityLevel.MODERATE,
            explanation="Combining multiple exfoliants increases irritation risk.",
            detailed_explanation="Both are effective exfoliants. Using together can over-exfoliate, damaging the skin barrier. May be tolerable at low concentrations.",
            recommendation="Pick one per routine. Can alternate days if skin tolerates.",
            can_alternate=True
        ))
        
        # ===== SYNERGIES =====
        self.add_interaction(Interaction(
            ingredient_a="hyaluronic_acid", ingredient_b="niacinamide",
            interaction_type=InteractionType.SYNERGIZES,
            severity=SeverityLevel.LOW,
            explanation="Excellent pairing - hydration plus barrier support.",
            detailed_explanation="Hyaluronic acid provides hydration while niacinamide strengthens the skin barrier to keep that hydration in. Both are gentle and suitable for all skin types."
        ))
        
        self.add_interaction(Interaction(
            ingredient_a="hyaluronic_acid", ingredient_b="ceramides",
            interaction_type=InteractionType.SYNERGIZES,
            severity=SeverityLevel.LOW,
            explanation="Perfect combination for barrier repair and hydration.",
            detailed_explanation="HA draws moisture into skin, ceramides form a protective layer to prevent moisture loss. Ideal for dry or compromised skin."
        ))
        
        self.add_interaction(Interaction(
            ingredient_a="ascorbic_acid", ingredient_b="zinc_oxide",
            interaction_type=InteractionType.SYNERGIZES,
            severity=SeverityLevel.LOW,
            explanation="Vitamin C enhances sun protection when used with sunscreen.",
            detailed_explanation="Vitamin C provides antioxidant protection against UV-induced free radicals that sunscreen alone doesn't block. Always apply vitamin C before sunscreen."
        ))
        
        self.add_interaction(Interaction(
            ingredient_a="niacinamide", ingredient_b="salicylic_acid",
            interaction_type=InteractionType.SYNERGIZES,
            severity=SeverityLevel.LOW,
            explanation="Great combination for acne-prone skin.",
            detailed_explanation="Salicylic acid clears pores while niacinamide reduces inflammation and controls oil. Niacinamide also helps buffer any irritation from salicylic acid."
        ))
        
        self.add_interaction(Interaction(
            ingredient_a="retinol", ingredient_b="hyaluronic_acid",
            interaction_type=InteractionType.SYNERGIZES,
            severity=SeverityLevel.LOW,
            explanation="Hyaluronic acid helps buffer retinol irritation.",
            detailed_explanation="HA provides hydration that counteracts retinol's drying effects. Apply HA to damp skin, let absorb, then apply retinol."
        ))
        
        self.add_interaction(Interaction(
            ingredient_a="retinol", ingredient_b="ceramides",
            interaction_type=InteractionType.SYNERGIZES,
            severity=SeverityLevel.LOW,
            explanation="Ceramides help protect barrier during retinol use.",
            detailed_explanation="Retinol can compromise the skin barrier. Ceramides help maintain barrier function, reducing irritation and dryness. Apply ceramide moisturizer after retinol."
        ))
        
        self.add_interaction(Interaction(
            ingredient_a="azelaic_acid", ingredient_b="niacinamide",
            interaction_type=InteractionType.SYNERGIZES,
            severity=SeverityLevel.LOW,
            explanation="Gentle but effective combination for redness and pigmentation.",
            detailed_explanation="Both ingredients reduce redness and hyperpigmentation through different mechanisms. Safe to layer and suitable for sensitive skin."
        ))
