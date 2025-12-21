"""
Ingredient Knowledge Module

KBAI Concepts Implemented:
- Frames: Ingredients as structured knowledge with slots
- Semantic Networks: Ingredient relationships and interactions
- Classification: Ingredient categories and functions

This module contains real skincare science about ingredient
interactions, pH levels, and application guidelines.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import networkx as nx


class IngredientCategory(Enum):
    """Primary function categories for skincare ingredients."""
    RETINOID = "retinoid"
    AHA = "alpha_hydroxy_acid"
    BHA = "beta_hydroxy_acid"
    VITAMIN_C = "vitamin_c"
    NIACINAMIDE = "niacinamide"
    PEPTIDE = "peptide"
    HYALURONIC_ACID = "hyaluronic_acid"
    CERAMIDE = "ceramide"
    SPF = "sunscreen"
    MOISTURIZER = "moisturizer"
    CLEANSER = "cleanser"
    OIL = "facial_oil"
    ENZYME = "enzyme"
    BENZOYL_PEROXIDE = "benzoyl_peroxide"
    AZELAIC_ACID = "azelaic_acid"
    OTHER = "other"


class InteractionType(Enum):
    """Types of interactions between ingredients."""
    CONFLICTS = "conflicts"           # Should never be used together
    CAUTION = "caution"               # Can be used but with care
    SYNERGIZES = "synergizes"         # Works better together
    REQUIRES_WAITING = "wait"         # Need time between applications
    DEACTIVATES = "deactivates"       # One neutralizes the other
    INCREASES_SENSITIVITY = "sensitizing"  # Combined = more irritation risk


class SkinType(Enum):
    """Standard skin type classifications."""
    DRY = "dry"
    OILY = "oily"
    COMBINATION = "combination"
    SENSITIVE = "sensitive"
    NORMAL = "normal"


class SkinConcern(Enum):
    """Common skin concerns that ingredients can address."""
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


class TimeOfDay(Enum):
    """When an ingredient should be used."""
    AM_ONLY = "morning_only"
    PM_ONLY = "evening_only"
    AM_OR_PM = "either"
    AM_AND_PM = "both"


@dataclass
class Ingredient:
    """Frame-based representation of a skincare ingredient.
    
    KBAI: This is a frame with slots that capture everything
    we know about an ingredient's properties and behavior.
    """
    id: str
    name: str
    category: IngredientCategory
    
    # Also known as (for ingredient list parsing)
    aliases: list[str] = field(default_factory=list)
    
    # Chemical properties
    optimal_ph: Optional[tuple[float, float]] = None  # (min, max) pH range
    water_soluble: bool = True
    
    # Application guidelines
    time_of_day: TimeOfDay = TimeOfDay.AM_OR_PM
    application_order: int = 5  # 1=first (cleanser) to 10=last (SPF/occlusive)
    
    # What it helps with
    addresses_concerns: list[SkinConcern] = field(default_factory=list)
    
    # Who should be careful
    caution_skin_types: list[SkinType] = field(default_factory=list)
    
    # Usage notes
    description: str = ""
    how_it_works: str = ""
    usage_tips: list[str] = field(default_factory=list)
    
    # Strength/concentration notes
    beginner_friendly: bool = True
    max_concentration: Optional[str] = None  # e.g., "2% for beginners"
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if isinstance(other, Ingredient):
            return self.id == other.id
        return False


@dataclass
class Interaction:
    """Represents a relationship between two ingredients.
    
    KBAI: These are the edges in our semantic network,
    capturing how ingredients relate to each other.
    """
    ingredient_a: str  # ingredient ID
    ingredient_b: str  # ingredient ID
    interaction_type: InteractionType
    severity: int = 5  # 1-10, higher = more serious
    
    explanation: str = ""
    recommendation: str = ""
    
    # If they need wait time between applications
    wait_minutes: Optional[int] = None


@dataclass
class SkinProfile:
    """User's skin profile for personalized recommendations.
    
    KBAI: Used for case-based reasoning - match similar
    profiles to recommend similar routines.
    """
    skin_type: SkinType
    concerns: list[SkinConcern] = field(default_factory=list)
    sensitivities: list[str] = field(default_factory=list)  # specific ingredients to avoid
    age_range: Optional[str] = None  # "20s", "30s", etc.
    climate: Optional[str] = None  # "humid", "dry", "temperate"
    
    # Current routine info for case matching
    currently_using: list[str] = field(default_factory=list)
    goals: list[str] = field(default_factory=list)


class IngredientKnowledgeGraph:
    """Semantic network of ingredients and their interactions.
    
    KBAI: This is the core knowledge representation. Ingredients
    are nodes, interactions are edges. We can traverse the graph
    to reason about compatibility, find alternatives, etc.
    """
    
    def __init__(self):
        self.graph = nx.Graph()  # Undirected - interactions go both ways
        self.ingredients: dict[str, Ingredient] = {}
        self.interactions: list[Interaction] = []
        
        # Index for fast alias lookup
        self._alias_index: dict[str, str] = {}  # alias -> ingredient_id
    
    def add_ingredient(self, ingredient: Ingredient) -> None:
        """Add an ingredient to the knowledge graph."""
        self.ingredients[ingredient.id] = ingredient
        self.graph.add_node(ingredient.id, ingredient=ingredient)
        
        # Index aliases for lookup
        for alias in ingredient.aliases:
            self._alias_index[alias.lower()] = ingredient.id
        self._alias_index[ingredient.name.lower()] = ingredient.id
        self._alias_index[ingredient.id.lower()] = ingredient.id
    
    def add_interaction(self, interaction: Interaction) -> None:
        """Add an interaction between two ingredients."""
        self.interactions.append(interaction)
        
        # Add edge to graph with interaction data
        self.graph.add_edge(
            interaction.ingredient_a,
            interaction.ingredient_b,
            interaction=interaction,
            type=interaction.interaction_type.value
        )
    
    def get_ingredient(self, identifier: str) -> Optional[Ingredient]:
        """Get ingredient by ID, name, or alias."""
        # Direct ID lookup
        if identifier in self.ingredients:
            return self.ingredients[identifier]
        
        # Alias lookup
        ingredient_id = self._alias_index.get(identifier.lower())
        if ingredient_id:
            return self.ingredients.get(ingredient_id)
        
        return None
    
    def find_ingredient(self, search_term: str) -> list[Ingredient]:
        """Search for ingredients by partial name match."""
        search_lower = search_term.lower()
        matches = []
        
        for ingredient in self.ingredients.values():
            if search_lower in ingredient.name.lower():
                matches.append(ingredient)
                continue
            
            for alias in ingredient.aliases:
                if search_lower in alias.lower():
                    matches.append(ingredient)
                    break
        
        return matches
    
    def get_interaction(self, ingredient_a: str, ingredient_b: str) -> Optional[Interaction]:
        """Get the interaction between two ingredients, if any."""
        # Normalize to IDs
        id_a = self._alias_index.get(ingredient_a.lower(), ingredient_a)
        id_b = self._alias_index.get(ingredient_b.lower(), ingredient_b)
        
        if self.graph.has_edge(id_a, id_b):
            return self.graph[id_a][id_b].get('interaction')
        
        return None
    
    def get_all_interactions(self, ingredient_id: str) -> list[Interaction]:
        """Get all interactions for a specific ingredient."""
        if ingredient_id not in self.graph:
            return []
        
        interactions = []
        for neighbor in self.graph.neighbors(ingredient_id):
            edge_data = self.graph[ingredient_id][neighbor]
            if 'interaction' in edge_data:
                interactions.append(edge_data['interaction'])
        
        return interactions
    
    def check_compatibility(self, ingredient_ids: list[str]) -> dict:
        """Check compatibility of multiple ingredients.
        
        KBAI: This is constraint satisfaction - we're checking
        if a set of ingredients satisfies our compatibility rules.
        
        Returns dict with:
        - conflicts: list of conflicting pairs
        - cautions: list of pairs needing caution
        - synergies: list of pairs that work well together
        - wait_times: list of pairs needing time between
        """
        result = {
            'conflicts': [],
            'cautions': [],
            'synergies': [],
            'wait_times': [],
            'is_compatible': True
        }
        
        # Normalize IDs
        normalized_ids = []
        for ing_id in ingredient_ids:
            resolved = self._alias_index.get(ing_id.lower(), ing_id)
            if resolved in self.ingredients:
                normalized_ids.append(resolved)
        
        # Check all pairs
        for i, id_a in enumerate(normalized_ids):
            for id_b in normalized_ids[i+1:]:
                interaction = self.get_interaction(id_a, id_b)
                
                if interaction:
                    pair_info = {
                        'ingredient_a': self.ingredients[id_a].name,
                        'ingredient_b': self.ingredients[id_b].name,
                        'explanation': interaction.explanation,
                        'recommendation': interaction.recommendation,
                        'severity': interaction.severity
                    }
                    
                    if interaction.interaction_type == InteractionType.CONFLICTS:
                        result['conflicts'].append(pair_info)
                        result['is_compatible'] = False
                    elif interaction.interaction_type == InteractionType.CAUTION:
                        result['cautions'].append(pair_info)
                    elif interaction.interaction_type == InteractionType.SYNERGIZES:
                        result['synergies'].append(pair_info)
                    elif interaction.interaction_type == InteractionType.REQUIRES_WAITING:
                        pair_info['wait_minutes'] = interaction.wait_minutes
                        result['wait_times'].append(pair_info)
                    elif interaction.interaction_type == InteractionType.DEACTIVATES:
                        result['conflicts'].append(pair_info)
                        result['is_compatible'] = False
        
        return result
    
    def get_recommended_ingredients(self, profile: SkinProfile) -> list[Ingredient]:
        """Recommend ingredients based on skin profile.
        
        KBAI: Diagnostic reasoning - map concerns to solutions.
        """
        recommended = []
        
        for ingredient in self.ingredients.values():
            # Check if it addresses any of their concerns
            addresses_concern = any(
                concern in ingredient.addresses_concerns 
                for concern in profile.concerns
            )
            
            # Check if it's safe for their skin type
            safe_for_skin = profile.skin_type not in ingredient.caution_skin_types
            
            # Check if they're not sensitive to it
            not_sensitive = ingredient.id not in profile.sensitivities
            
            if addresses_concern and safe_for_skin and not_sensitive:
                recommended.append(ingredient)
        
        # Sort by how many concerns they address
        recommended.sort(
            key=lambda x: len(set(x.addresses_concerns) & set(profile.concerns)),
            reverse=True
        )
        
        return recommended
    
    def explain_interaction(self, ingredient_a: str, ingredient_b: str) -> str:
        """Generate a detailed explanation of how two ingredients interact.
        
        KBAI: Explainable AI - provide reasoning for our conclusions.
        """
        ing_a = self.get_ingredient(ingredient_a)
        ing_b = self.get_ingredient(ingredient_b)
        
        if not ing_a or not ing_b:
            return "One or both ingredients not found in database."
        
        interaction = self.get_interaction(ingredient_a, ingredient_b)
        
        if not interaction:
            # Check for implicit conflicts (e.g., pH incompatibility)
            explanation = self._check_implicit_conflicts(ing_a, ing_b)
            if explanation:
                return explanation
            return f"No known interaction between {ing_a.name} and {ing_b.name}. Generally safe to use together."
        
        # Build detailed explanation
        lines = []
        
        if interaction.interaction_type == InteractionType.CONFLICTS:
            lines.append(f"⚠️ CONFLICT: {ing_a.name} and {ing_b.name} should not be used together.")
        elif interaction.interaction_type == InteractionType.CAUTION:
            lines.append(f"⚡ CAUTION: {ing_a.name} and {ing_b.name} can be used together with care.")
        elif interaction.interaction_type == InteractionType.SYNERGIZES:
            lines.append(f"✨ SYNERGY: {ing_a.name} and {ing_b.name} work great together!")
        elif interaction.interaction_type == InteractionType.REQUIRES_WAITING:
            lines.append(f"⏱️ TIMING: Wait between applying {ing_a.name} and {ing_b.name}.")
        
        if interaction.explanation:
            lines.append(f"\nWhy: {interaction.explanation}")
        
        if interaction.recommendation:
            lines.append(f"\nRecommendation: {interaction.recommendation}")
        
        if interaction.wait_minutes:
            lines.append(f"\nWait time: {interaction.wait_minutes} minutes between applications.")
        
        return "\n".join(lines)
    
    def _check_implicit_conflicts(self, ing_a: Ingredient, ing_b: Ingredient) -> Optional[str]:
        """Check for conflicts based on properties even without explicit rules."""
        # pH incompatibility check
        if ing_a.optimal_ph and ing_b.optimal_ph:
            a_min, a_max = ing_a.optimal_ph
            b_min, b_max = ing_b.optimal_ph
            
            # If pH ranges don't overlap significantly
            if a_max < b_min - 1 or b_max < a_min - 1:
                return (
                    f"Potential pH conflict: {ing_a.name} works best at pH {a_min}-{a_max}, "
                    f"while {ing_b.name} needs pH {b_min}-{b_max}. "
                    f"Using together may reduce effectiveness of one or both."
                )
        
        return None
    
    def get_ingredients_by_concern(self, concern: SkinConcern) -> list[Ingredient]:
        """Get all ingredients that address a specific concern."""
        return [
            ing for ing in self.ingredients.values()
            if concern in ing.addresses_concerns
        ]
    
    def get_ingredients_by_category(self, category: IngredientCategory) -> list[Ingredient]:
        """Get all ingredients in a category."""
        return [
            ing for ing in self.ingredients.values()
            if ing.category == category
        ]


def create_skincare_knowledge_base() -> IngredientKnowledgeGraph:
    """Create a comprehensive skincare ingredient knowledge base.
    
    This contains real skincare science about common ingredients
    and their interactions.
    """
    kg = IngredientKnowledgeGraph()
    
    # ========== RETINOIDS ==========
    kg.add_ingredient(Ingredient(
        id="retinol",
        name="Retinol",
        category=IngredientCategory.RETINOID,
        aliases=["vitamin a", "retinyl palmitate", "retinaldehyde", "retinoic acid"],
        optimal_ph=(5.5, 6.5),
        water_soluble=False,
        time_of_day=TimeOfDay.PM_ONLY,
        application_order=6,
        addresses_concerns=[
            SkinConcern.AGING, SkinConcern.ACNE, SkinConcern.TEXTURE,
            SkinConcern.HYPERPIGMENTATION, SkinConcern.PORES
        ],
        caution_skin_types=[SkinType.SENSITIVE],
        description="Gold standard anti-aging ingredient that increases cell turnover.",
        how_it_works="Binds to retinoic acid receptors in skin cells, accelerating cell turnover and stimulating collagen production.",
        usage_tips=[
            "Start with low concentration (0.25-0.5%) 2-3x per week",
            "Always use SPF during the day",
            "Apply to dry skin to reduce irritation",
            "Expect purging for 4-6 weeks"
        ],
        beginner_friendly=False,
        max_concentration="Start at 0.25%, work up to 1%"
    ))
    
    # ========== AHAs ==========
    kg.add_ingredient(Ingredient(
        id="glycolic_acid",
        name="Glycolic Acid",
        category=IngredientCategory.AHA,
        aliases=["glycolic", "aha"],
        optimal_ph=(3.0, 4.0),
        water_soluble=True,
        time_of_day=TimeOfDay.PM_ONLY,
        application_order=4,
        addresses_concerns=[
            SkinConcern.TEXTURE, SkinConcern.DULLNESS, 
            SkinConcern.HYPERPIGMENTATION, SkinConcern.AGING
        ],
        caution_skin_types=[SkinType.SENSITIVE, SkinType.DRY],
        description="Smallest AHA molecule, penetrates deeply for effective exfoliation.",
        how_it_works="Dissolves bonds between dead skin cells, revealing fresher skin underneath.",
        usage_tips=[
            "Start with 5-10% concentration",
            "Use 2-3x per week initially",
            "Don't combine with other actives when starting"
        ],
        beginner_friendly=True,
        max_concentration="Up to 30% for peels (professional use)"
    ))
    
    kg.add_ingredient(Ingredient(
        id="lactic_acid",
        name="Lactic Acid",
        category=IngredientCategory.AHA,
        aliases=["lactic"],
        optimal_ph=(3.5, 4.5),
        water_soluble=True,
        time_of_day=TimeOfDay.PM_ONLY,
        application_order=4,
        addresses_concerns=[
            SkinConcern.TEXTURE, SkinConcern.DULLNESS, 
            SkinConcern.DRYNESS, SkinConcern.HYPERPIGMENTATION
        ],
        caution_skin_types=[SkinType.SENSITIVE],
        description="Gentler AHA that also provides hydration.",
        how_it_works="Larger molecule than glycolic, so it penetrates more slowly and gently. Also acts as a humectant.",
        usage_tips=[
            "Great for sensitive skin as a starting AHA",
            "Provides hydration while exfoliating"
        ],
        beginner_friendly=True
    ))
    
    # ========== BHAs ==========
    kg.add_ingredient(Ingredient(
        id="salicylic_acid",
        name="Salicylic Acid",
        category=IngredientCategory.BHA,
        aliases=["bha", "salicylic", "beta hydroxy acid"],
        optimal_ph=(3.0, 4.0),
        water_soluble=False,
        time_of_day=TimeOfDay.AM_OR_PM,
        application_order=4,
        addresses_concerns=[
            SkinConcern.ACNE, SkinConcern.PORES, 
            SkinConcern.OILINESS, SkinConcern.TEXTURE
        ],
        caution_skin_types=[SkinType.DRY],
        description="Oil-soluble acid that penetrates into pores to clear congestion.",
        how_it_works="Being oil-soluble, it can penetrate sebum-filled pores to exfoliate from within.",
        usage_tips=[
            "Excellent for blackheads and whiteheads",
            "Can be drying - always moisturize",
            "Safe to use daily for most people"
        ],
        beginner_friendly=True,
        max_concentration="2% OTC, higher needs prescription"
    ))
    
    # ========== VITAMIN C ==========
    kg.add_ingredient(Ingredient(
        id="vitamin_c",
        name="Vitamin C (L-Ascorbic Acid)",
        category=IngredientCategory.VITAMIN_C,
        aliases=["l-ascorbic acid", "ascorbic acid", "vit c", "laa"],
        optimal_ph=(2.5, 3.5),
        water_soluble=True,
        time_of_day=TimeOfDay.AM_ONLY,
        application_order=4,
        addresses_concerns=[
            SkinConcern.HYPERPIGMENTATION, SkinConcern.DULLNESS,
            SkinConcern.AGING, SkinConcern.DARK_CIRCLES
        ],
        caution_skin_types=[SkinType.SENSITIVE],
        description="Powerful antioxidant that brightens skin and boosts sun protection.",
        how_it_works="Neutralizes free radicals, inhibits melanin production, and is essential for collagen synthesis.",
        usage_tips=[
            "Use in the morning before sunscreen for antioxidant protection",
            "Store in a cool, dark place - it oxidizes easily",
            "If it turns brown/orange, it's gone bad"
        ],
        beginner_friendly=True,
        max_concentration="10-20% is effective; higher can irritate"
    ))
    
    kg.add_ingredient(Ingredient(
        id="vitamin_c_derivative",
        name="Vitamin C Derivatives",
        category=IngredientCategory.VITAMIN_C,
        aliases=[
            "sodium ascorbyl phosphate", "ascorbyl glucoside", 
            "magnesium ascorbyl phosphate", "ascorbyl tetraisopalmitate"
        ],
        optimal_ph=(5.0, 7.0),
        water_soluble=True,
        time_of_day=TimeOfDay.AM_OR_PM,
        application_order=4,
        addresses_concerns=[
            SkinConcern.HYPERPIGMENTATION, SkinConcern.DULLNESS, SkinConcern.AGING
        ],
        caution_skin_types=[],
        description="Stable forms of vitamin C, gentler but less potent than L-ascorbic acid.",
        how_it_works="Convert to ascorbic acid in the skin. More stable and less irritating.",
        usage_tips=[
            "Great for sensitive skin",
            "Can be used with niacinamide without issues"
        ],
        beginner_friendly=True
    ))
    
    # ========== NIACINAMIDE ==========
    kg.add_ingredient(Ingredient(
        id="niacinamide",
        name="Niacinamide",
        category=IngredientCategory.NIACINAMIDE,
        aliases=["vitamin b3", "nicotinamide"],
        optimal_ph=(5.0, 7.0),
        water_soluble=True,
        time_of_day=TimeOfDay.AM_AND_PM,
        application_order=4,
        addresses_concerns=[
            SkinConcern.PORES, SkinConcern.OILINESS, SkinConcern.REDNESS,
            SkinConcern.HYPERPIGMENTATION, SkinConcern.AGING
        ],
        caution_skin_types=[],
        description="Versatile ingredient that regulates oil, reduces pores, and brightens.",
        how_it_works="Supports skin barrier, regulates sebum production, and inhibits melanin transfer.",
        usage_tips=[
            "Works well with most ingredients",
            "Can cause flushing if used with pure vitamin C at high concentrations",
            "5% is effective for most benefits"
        ],
        beginner_friendly=True,
        max_concentration="10% max; 5% is usually sufficient"
    ))
    
    # ========== HYALURONIC ACID ==========
    kg.add_ingredient(Ingredient(
        id="hyaluronic_acid",
        name="Hyaluronic Acid",
        category=IngredientCategory.HYALURONIC_ACID,
        aliases=["ha", "sodium hyaluronate", "hyaluronan"],
        optimal_ph=(5.0, 7.0),
        water_soluble=True,
        time_of_day=TimeOfDay.AM_AND_PM,
        application_order=3,
        addresses_concerns=[
            SkinConcern.DRYNESS, SkinConcern.AGING, SkinConcern.DULLNESS
        ],
        caution_skin_types=[],
        description="Powerful humectant that holds up to 1000x its weight in water.",
        how_it_works="Draws moisture from the environment into the skin, plumping and hydrating.",
        usage_tips=[
            "Apply to damp skin for best results",
            "Follow with moisturizer to seal in hydration",
            "In dry climates, can draw moisture OUT of skin - always seal with moisturizer"
        ],
        beginner_friendly=True
    ))
    
    # ========== BENZOYL PEROXIDE ==========
    kg.add_ingredient(Ingredient(
        id="benzoyl_peroxide",
        name="Benzoyl Peroxide",
        category=IngredientCategory.BENZOYL_PEROXIDE,
        aliases=["bp", "bpo"],
        optimal_ph=(4.0, 6.0),
        water_soluble=True,
        time_of_day=TimeOfDay.AM_OR_PM,
        application_order=5,
        addresses_concerns=[SkinConcern.ACNE],
        caution_skin_types=[SkinType.SENSITIVE, SkinType.DRY],
        description="Antibacterial that kills acne-causing bacteria.",
        how_it_works="Releases oxygen into pores, killing P. acnes bacteria. Also mildly exfoliating.",
        usage_tips=[
            "2.5% is as effective as 10% with less irritation",
            "Bleaches fabrics - use white towels and pillowcases",
            "Can be very drying - start slow"
        ],
        beginner_friendly=True,
        max_concentration="2.5% recommended; 10% max OTC"
    ))
    
    # ========== AZELAIC ACID ==========
    kg.add_ingredient(Ingredient(
        id="azelaic_acid",
        name="Azelaic Acid",
        category=IngredientCategory.AZELAIC_ACID,
        aliases=["azelaic"],
        optimal_ph=(4.5, 5.5),
        water_soluble=True,
        time_of_day=TimeOfDay.AM_OR_PM,
        application_order=5,
        addresses_concerns=[
            SkinConcern.ACNE, SkinConcern.HYPERPIGMENTATION,
            SkinConcern.REDNESS, SkinConcern.TEXTURE
        ],
        caution_skin_types=[],
        description="Gentle multitasker safe for pregnancy and sensitive skin.",
        how_it_works="Antibacterial, anti-inflammatory, and inhibits melanin production.",
        usage_tips=[
            "Safe during pregnancy",
            "Great for rosacea",
            "Can be used with most other actives"
        ],
        beginner_friendly=True,
        max_concentration="10% OTC, 15-20% prescription"
    ))
    
    # ========== PEPTIDES ==========
    kg.add_ingredient(Ingredient(
        id="peptides",
        name="Peptides",
        category=IngredientCategory.PEPTIDE,
        aliases=["matrixyl", "argireline", "copper peptides", "palmitoyl"],
        optimal_ph=(5.0, 7.0),
        water_soluble=True,
        time_of_day=TimeOfDay.AM_AND_PM,
        application_order=5,
        addresses_concerns=[SkinConcern.AGING, SkinConcern.TEXTURE],
        caution_skin_types=[],
        description="Amino acid chains that signal skin to produce more collagen.",
        how_it_works="Act as messengers, telling skin cells to perform specific functions like collagen production.",
        usage_tips=[
            "Most effective with consistent long-term use",
            "Don't use with strong acids (deactivates them)"
        ],
        beginner_friendly=True
    ))
    
    # ========== CERAMIDES ==========
    kg.add_ingredient(Ingredient(
        id="ceramides",
        name="Ceramides",
        category=IngredientCategory.CERAMIDE,
        aliases=["ceramide np", "ceramide ap", "ceramide eop"],
        optimal_ph=(5.0, 7.0),
        water_soluble=False,
        time_of_day=TimeOfDay.AM_AND_PM,
        application_order=7,
        addresses_concerns=[
            SkinConcern.DRYNESS, SkinConcern.SENSITIVITY, SkinConcern.AGING
        ],
        caution_skin_types=[],
        description="Lipids that form the skin barrier, essential for healthy skin.",
        how_it_works="Replenish the skin's natural lipid barrier, preventing moisture loss.",
        usage_tips=[
            "Essential for anyone using actives",
            "Look for products with multiple ceramide types",
            "Works synergistically with cholesterol and fatty acids"
        ],
        beginner_friendly=True
    ))
    
    # ========== SPF ==========
    kg.add_ingredient(Ingredient(
        id="spf",
        name="Sunscreen (SPF)",
        category=IngredientCategory.SPF,
        aliases=["sunscreen", "sun protection", "sunblock"],
        water_soluble=False,
        time_of_day=TimeOfDay.AM_ONLY,
        application_order=10,
        addresses_concerns=[
            SkinConcern.AGING, SkinConcern.HYPERPIGMENTATION
        ],
        caution_skin_types=[],
        description="The most important anti-aging product. Prevents UV damage.",
        how_it_works="Physical blockers reflect UV; chemical filters absorb and convert UV to heat.",
        usage_tips=[
            "Apply as LAST step of skincare, before makeup",
            "Use 1/4 teaspoon for face",
            "Reapply every 2 hours when exposed to sun"
        ],
        beginner_friendly=True
    ))
    
    # ========== SQUALANE ==========
    kg.add_ingredient(Ingredient(
        id="squalane",
        name="Squalane",
        category=IngredientCategory.OIL,
        aliases=["squalene", "olive squalane", "sugarcane squalane"],
        water_soluble=False,
        time_of_day=TimeOfDay.AM_AND_PM,
        application_order=8,
        addresses_concerns=[
            SkinConcern.DRYNESS, SkinConcern.AGING, SkinConcern.SENSITIVITY
        ],
        caution_skin_types=[],
        description="Lightweight oil that mimics skin's natural sebum. Non-comedogenic.",
        how_it_works="Identical to squalene naturally produced by skin, so it absorbs easily and reinforces the lipid barrier.",
        usage_tips=[
            "Can be mixed with moisturizer or applied alone",
            "Great for sealing in hydration after water-based serums",
            "Safe for acne-prone skin despite being an oil"
        ],
        beginner_friendly=True
    ))
    
    # ========== TRANEXAMIC ACID ==========
    kg.add_ingredient(Ingredient(
        id="tranexamic_acid",
        name="Tranexamic Acid",
        category=IngredientCategory.OTHER,
        aliases=["txa", "tranexamic"],
        optimal_ph=(4.5, 6.5),
        water_soluble=True,
        time_of_day=TimeOfDay.AM_AND_PM,
        application_order=4,
        addresses_concerns=[
            SkinConcern.HYPERPIGMENTATION, SkinConcern.REDNESS, SkinConcern.DULLNESS
        ],
        caution_skin_types=[],
        description="Brightening ingredient that targets stubborn pigmentation and melasma.",
        how_it_works="Interrupts the pathway between UV exposure and melanin production. Also reduces redness.",
        usage_tips=[
            "Pairs well with vitamin C and niacinamide",
            "Safe for long-term use",
            "Particularly effective for melasma"
        ],
        beginner_friendly=True
    ))
    
    # ========== ALPHA ARBUTIN ==========
    kg.add_ingredient(Ingredient(
        id="alpha_arbutin",
        name="Alpha Arbutin",
        category=IngredientCategory.OTHER,
        aliases=["arbutin", "α-arbutin"],
        optimal_ph=(3.5, 6.5),
        water_soluble=True,
        time_of_day=TimeOfDay.AM_AND_PM,
        application_order=4,
        addresses_concerns=[
            SkinConcern.HYPERPIGMENTATION, SkinConcern.DULLNESS
        ],
        caution_skin_types=[],
        description="Gentle brightening agent derived from bearberry. Safer alternative to hydroquinone.",
        how_it_works="Inhibits tyrosinase enzyme, reducing melanin production without irritation.",
        usage_tips=[
            "Works best at 1-2% concentration",
            "Synergizes with vitamin C",
            "Results visible after 2-3 months of consistent use"
        ],
        beginner_friendly=True
    ))
    
    # ========== CENTELLA ASIATICA ==========
    kg.add_ingredient(Ingredient(
        id="centella",
        name="Centella Asiatica",
        category=IngredientCategory.OTHER,
        aliases=["cica", "tiger grass", "gotu kola", "madecassoside", "asiaticoside"],
        water_soluble=True,
        time_of_day=TimeOfDay.AM_AND_PM,
        application_order=5,
        addresses_concerns=[
            SkinConcern.SENSITIVITY, SkinConcern.REDNESS, SkinConcern.ACNE, SkinConcern.AGING
        ],
        caution_skin_types=[],
        description="Calming, healing ingredient popular in K-beauty. Great for damaged skin barrier.",
        how_it_works="Contains madecassoside and asiaticoside that promote collagen synthesis and wound healing.",
        usage_tips=[
            "Excellent for post-procedure recovery",
            "Pairs well with almost everything",
            "Look for products with multiple centella compounds"
        ],
        beginner_friendly=True
    ))
    
    # ========== BAKUCHIOL ==========
    kg.add_ingredient(Ingredient(
        id="bakuchiol",
        name="Bakuchiol",
        category=IngredientCategory.OTHER,
        aliases=["natural retinol alternative"],
        water_soluble=False,
        time_of_day=TimeOfDay.AM_AND_PM,
        application_order=6,
        addresses_concerns=[
            SkinConcern.AGING, SkinConcern.TEXTURE, SkinConcern.HYPERPIGMENTATION
        ],
        caution_skin_types=[],
        description="Plant-based retinol alternative. Same benefits without irritation or sun sensitivity.",
        how_it_works="Activates similar genes as retinol, stimulating collagen production and cell turnover.",
        usage_tips=[
            "Can be used during pregnancy (unlike retinol)",
            "Safe to use in AM without sun sensitivity",
            "Can be combined with retinol for enhanced effects"
        ],
        beginner_friendly=True
    ))
    
    # ========== TEA TREE OIL ==========
    kg.add_ingredient(Ingredient(
        id="tea_tree",
        name="Tea Tree Oil",
        category=IngredientCategory.OIL,
        aliases=["melaleuca", "tea tree", "melaleuca alternifolia"],
        water_soluble=False,
        time_of_day=TimeOfDay.PM_ONLY,
        application_order=5,
        addresses_concerns=[SkinConcern.ACNE, SkinConcern.OILINESS],
        caution_skin_types=[SkinType.SENSITIVE, SkinType.DRY],
        description="Natural antibacterial oil effective for acne spot treatment.",
        how_it_works="Contains terpinen-4-ol which has antimicrobial properties that kill acne-causing bacteria.",
        usage_tips=[
            "Never use undiluted - always at 5% or less concentration",
            "Best as spot treatment, not all-over",
            "Can be drying - follow with moisturizer"
        ],
        beginner_friendly=True,
        max_concentration="5% max for leave-on products"
    ))
    
    # ========== KOJIC ACID ==========
    kg.add_ingredient(Ingredient(
        id="kojic_acid",
        name="Kojic Acid",
        category=IngredientCategory.OTHER,
        aliases=["kojic"],
        optimal_ph=(4.5, 5.5),
        water_soluble=True,
        time_of_day=TimeOfDay.PM_ONLY,
        application_order=4,
        addresses_concerns=[SkinConcern.HYPERPIGMENTATION, SkinConcern.DULLNESS],
        caution_skin_types=[SkinType.SENSITIVE],
        description="Potent brightening agent derived from fungi. Effective for stubborn dark spots.",
        how_it_works="Inhibits tyrosinase enzyme and chelates copper required for melanin production.",
        usage_tips=[
            "Can cause irritation - introduce slowly",
            "Often combined with other brighteners for enhanced effect",
            "Unstable in light - use PM only and store properly"
        ],
        beginner_friendly=False,
        max_concentration="1-4% in most products"
    ))
    
    # ========== MANDELIC ACID ==========
    kg.add_ingredient(Ingredient(
        id="mandelic_acid",
        name="Mandelic Acid",
        category=IngredientCategory.AHA,
        aliases=["mandelic"],
        optimal_ph=(3.0, 4.0),
        water_soluble=True,
        time_of_day=TimeOfDay.PM_ONLY,
        application_order=4,
        addresses_concerns=[
            SkinConcern.TEXTURE, SkinConcern.ACNE, 
            SkinConcern.HYPERPIGMENTATION, SkinConcern.AGING
        ],
        caution_skin_types=[],
        description="Gentlest AHA due to large molecule size. Great for sensitive skin and darker skin tones.",
        how_it_works="Larger molecule penetrates slowly and evenly, reducing irritation risk while still exfoliating.",
        usage_tips=[
            "Best AHA for sensitive skin and beginners",
            "Safe for darker skin tones - lower risk of post-inflammatory hyperpigmentation",
            "Also has antibacterial properties for acne"
        ],
        beginner_friendly=True,
        max_concentration="Up to 10% for regular use"
    ))
    
    # ========== PHA (POLYHYDROXY ACIDS) ==========
    kg.add_ingredient(Ingredient(
        id="pha",
        name="PHAs (Polyhydroxy Acids)",
        category=IngredientCategory.AHA,
        aliases=["gluconolactone", "lactobionic acid", "polyhydroxy acid"],
        optimal_ph=(3.5, 4.5),
        water_soluble=True,
        time_of_day=TimeOfDay.AM_OR_PM,
        application_order=4,
        addresses_concerns=[
            SkinConcern.TEXTURE, SkinConcern.DRYNESS, 
            SkinConcern.SENSITIVITY, SkinConcern.AGING
        ],
        caution_skin_types=[],
        description="Gentlest exfoliating acids. Humectant properties make them hydrating while exfoliating.",
        how_it_works="Largest molecule size of all hydroxy acids. Exfoliate surface only while attracting moisture.",
        usage_tips=[
            "Can be used daily by most skin types",
            "Great alternative if AHAs/BHAs are too irritating",
            "Antioxidant properties provide additional benefits"
        ],
        beginner_friendly=True
    ))
    
    # ========== ZINC ==========
    kg.add_ingredient(Ingredient(
        id="zinc",
        name="Zinc",
        category=IngredientCategory.OTHER,
        aliases=["zinc oxide", "zinc pca", "zinc sulfate", "zinc gluconate"],
        water_soluble=True,
        time_of_day=TimeOfDay.AM_AND_PM,
        application_order=5,
        addresses_concerns=[
            SkinConcern.ACNE, SkinConcern.OILINESS, 
            SkinConcern.REDNESS, SkinConcern.SENSITIVITY
        ],
        caution_skin_types=[SkinType.DRY],
        description="Anti-inflammatory mineral that controls oil and soothes irritation.",
        how_it_works="Regulates sebum production, has antimicrobial properties, and supports wound healing.",
        usage_tips=[
            "Zinc oxide in sunscreen provides physical UV protection",
            "Zinc PCA specifically targets oil control",
            "Can be drying - pair with hydrating ingredients"
        ],
        beginner_friendly=True
    ))
    
    # ========== ROSEHIP OIL ==========
    kg.add_ingredient(Ingredient(
        id="rosehip_oil",
        name="Rosehip Oil",
        category=IngredientCategory.OIL,
        aliases=["rosehip seed oil", "rosa canina"],
        water_soluble=False,
        time_of_day=TimeOfDay.PM_ONLY,
        application_order=9,
        addresses_concerns=[
            SkinConcern.AGING, SkinConcern.HYPERPIGMENTATION, 
            SkinConcern.DRYNESS, SkinConcern.TEXTURE
        ],
        caution_skin_types=[SkinType.OILY],
        description="Nutrient-rich oil high in vitamin A and essential fatty acids.",
        how_it_works="Contains natural retinoids (trans-retinoic acid) and linoleic acid for regeneration.",
        usage_tips=[
            "Best used at night as final step",
            "Can oxidize - store in dark, cool place",
            "A little goes a long way - 2-3 drops is enough"
        ],
        beginner_friendly=True
    ))
    
    # ========== VITAMIN E ==========
    kg.add_ingredient(Ingredient(
        id="vitamin_e",
        name="Vitamin E",
        category=IngredientCategory.OTHER,
        aliases=["tocopherol", "tocopheryl acetate", "alpha-tocopherol"],
        water_soluble=False,
        time_of_day=TimeOfDay.AM_AND_PM,
        application_order=6,
        addresses_concerns=[
            SkinConcern.DRYNESS, SkinConcern.AGING, SkinConcern.SENSITIVITY
        ],
        caution_skin_types=[SkinType.OILY],
        description="Antioxidant that protects skin from free radicals and supports barrier function.",
        how_it_works="Neutralizes free radicals from UV and pollution. Enhances moisturizer effectiveness.",
        usage_tips=[
            "Works synergistically with vitamin C - stabilizes it",
            "Can be comedogenic for some - patch test first",
            "Often found in moisturizers and sunscreens"
        ],
        beginner_friendly=True
    ))
    
    # ========== ALLANTOIN ==========
    kg.add_ingredient(Ingredient(
        id="allantoin",
        name="Allantoin",
        category=IngredientCategory.OTHER,
        aliases=[],
        water_soluble=True,
        time_of_day=TimeOfDay.AM_AND_PM,
        application_order=5,
        addresses_concerns=[
            SkinConcern.SENSITIVITY, SkinConcern.DRYNESS, 
            SkinConcern.REDNESS, SkinConcern.TEXTURE
        ],
        caution_skin_types=[],
        description="Ultra-gentle soothing ingredient that promotes skin healing.",
        how_it_works="Stimulates cell proliferation and has keratolytic properties for gentle exfoliation.",
        usage_tips=[
            "Found in many sensitive skin products",
            "Safe for all skin types including babies",
            "Helps other ingredients penetrate better"
        ],
        beginner_friendly=True
    ))
    
    # ========== NEW INGREDIENT INTERACTIONS ==========
    
    # Tea tree interactions
    kg.add_interaction(Interaction(
        ingredient_a="tea_tree",
        ingredient_b="benzoyl_peroxide",
        interaction_type=InteractionType.CAUTION,
        severity=6,
        explanation="Both are antibacterial and drying. Using together may over-dry and irritate skin.",
        recommendation="Choose one or the other for acne treatment, not both."
    ))
    
    kg.add_interaction(Interaction(
        ingredient_a="tea_tree",
        ingredient_b="retinol",
        interaction_type=InteractionType.CAUTION,
        severity=5,
        explanation="Both can be irritating. Tea tree's essential oils may increase sensitivity.",
        recommendation="Use on alternating nights if combining."
    ))
    
    # Kojic acid interactions
    kg.add_interaction(Interaction(
        ingredient_a="kojic_acid",
        ingredient_b="vitamin_c",
        interaction_type=InteractionType.SYNERGIZES,
        severity=1,
        explanation="Both target pigmentation through different mechanisms. Enhanced brightening effect.",
        recommendation="Powerful combination for stubborn dark spots."
    ))
    
    kg.add_interaction(Interaction(
        ingredient_a="kojic_acid",
        ingredient_b="retinol",
        interaction_type=InteractionType.CAUTION,
        severity=6,
        explanation="Both can be irritating. Combining may compromise skin barrier.",
        recommendation="Use on alternate nights, not together."
    ))
    
    # Mandelic acid interactions
    kg.add_interaction(Interaction(
        ingredient_a="mandelic_acid",
        ingredient_b="retinol",
        interaction_type=InteractionType.CAUTION,
        severity=5,
        explanation="Both exfoliate but mandelic is gentler than other AHAs with retinol.",
        recommendation="More tolerable than glycolic + retinol, but still use caution. Alternate nights recommended."
    ))
    
    kg.add_interaction(Interaction(
        ingredient_a="mandelic_acid",
        ingredient_b="niacinamide",
        interaction_type=InteractionType.SYNERGIZES,
        severity=1,
        explanation="Niacinamide soothes while mandelic exfoliates gently.",
        recommendation="Great combination for acne-prone sensitive skin."
    ))
    
    # PHA interactions
    kg.add_interaction(Interaction(
        ingredient_a="pha",
        ingredient_b="retinol",
        interaction_type=InteractionType.SYNERGIZES,
        severity=2,
        explanation="PHAs are gentle enough to use with retinol and provide hydration.",
        recommendation="Safest hydroxy acid to combine with retinol."
    ))
    
    kg.add_interaction(Interaction(
        ingredient_a="pha",
        ingredient_b="vitamin_c",
        interaction_type=InteractionType.SYNERGIZES,
        severity=1,
        explanation="PHAs work at compatible pH and won't destabilize vitamin C.",
        recommendation="Can be layered together for brightening and exfoliation."
    ))
    
    # Vitamin E interactions
    kg.add_interaction(Interaction(
        ingredient_a="vitamin_e",
        ingredient_b="vitamin_c",
        interaction_type=InteractionType.SYNERGIZES,
        severity=1,
        explanation="Vitamin E stabilizes vitamin C and enhances its antioxidant effects by 4x.",
        recommendation="Look for products combining both, or layer them."
    ))
    
    kg.add_interaction(Interaction(
        ingredient_a="vitamin_e",
        ingredient_b="retinol",
        interaction_type=InteractionType.SYNERGIZES,
        severity=1,
        explanation="Vitamin E's antioxidant properties protect skin while retinol works.",
        recommendation="Apply vitamin E product after retinol to boost moisture and protection."
    ))
    
    # Rosehip oil interactions
    kg.add_interaction(Interaction(
        ingredient_a="rosehip_oil",
        ingredient_b="retinol",
        interaction_type=InteractionType.SYNERGIZES,
        severity=1,
        explanation="Rosehip contains natural vitamin A that complements retinol. Also moisturizes.",
        recommendation="Apply rosehip oil after retinol to buffer irritation."
    ))
    
    # Zinc interactions
    kg.add_interaction(Interaction(
        ingredient_a="zinc",
        ingredient_b="niacinamide",
        interaction_type=InteractionType.SYNERGIZES,
        severity=1,
        explanation="Both control oil and reduce inflammation. Common pairing in acne products.",
        recommendation="Excellent combination for oily, acne-prone skin."
    ))
    
    # Allantoin interactions
    kg.add_interaction(Interaction(
        ingredient_a="allantoin",
        ingredient_b="retinol",
        interaction_type=InteractionType.SYNERGIZES,
        severity=1,
        explanation="Allantoin soothes irritation from retinol while promoting healing.",
        recommendation="Great supporting ingredient in retinol formulations."
    ))
    
    # ========== NEW INTERACTIONS ==========
    
    # Squalane synergies
    kg.add_interaction(Interaction(
        ingredient_a="squalane",
        ingredient_b="retinol",
        interaction_type=InteractionType.SYNERGIZES,
        severity=1,
        explanation="Squalane buffers retinol's irritation while helping it penetrate. Great for sensitive skin using retinoids.",
        recommendation="Apply retinol first, then seal with squalane."
    ))
    
    kg.add_interaction(Interaction(
        ingredient_a="squalane",
        ingredient_b="hyaluronic_acid",
        interaction_type=InteractionType.SYNERGIZES,
        severity=1,
        explanation="HA pulls in moisture, squalane locks it in. Perfect hydration combo.",
        recommendation="Apply HA to damp skin, follow with squalane."
    ))
    
    # Tranexamic acid synergies
    kg.add_interaction(Interaction(
        ingredient_a="tranexamic_acid",
        ingredient_b="vitamin_c",
        interaction_type=InteractionType.SYNERGIZES,
        severity=1,
        explanation="Both target pigmentation through different mechanisms. Enhanced brightening.",
        recommendation="Excellent combination for hyperpigmentation. Layer vitamin C first."
    ))
    
    kg.add_interaction(Interaction(
        ingredient_a="tranexamic_acid",
        ingredient_b="niacinamide",
        interaction_type=InteractionType.SYNERGIZES,
        severity=1,
        explanation="Niacinamide inhibits melanosome transfer while TXA blocks melanin production.",
        recommendation="Powerful brightening duo. Can be used together daily."
    ))
    
    # Alpha arbutin synergies
    kg.add_interaction(Interaction(
        ingredient_a="alpha_arbutin",
        ingredient_b="vitamin_c",
        interaction_type=InteractionType.SYNERGIZES,
        severity=1,
        explanation="Target pigmentation via different pathways. Arbutin is gentle enough to pair with actives.",
        recommendation="Use together in AM routine for maximum brightening."
    ))
    
    # Centella interactions
    kg.add_interaction(Interaction(
        ingredient_a="centella",
        ingredient_b="retinol",
        interaction_type=InteractionType.SYNERGIZES,
        severity=1,
        explanation="Centella soothes irritation from retinol while promoting healing.",
        recommendation="Apply centella product after retinol to buffer irritation."
    ))
    
    # Bakuchiol interactions
    kg.add_interaction(Interaction(
        ingredient_a="bakuchiol",
        ingredient_b="retinol",
        interaction_type=InteractionType.SYNERGIZES,
        severity=1,
        explanation="Studies show combining them enhances anti-aging effects beyond either alone.",
        recommendation="Can be layered together for experienced users, or use bakuchiol in AM and retinol in PM."
    ))
    
    kg.add_interaction(Interaction(
        ingredient_a="bakuchiol",
        ingredient_b="vitamin_c",
        interaction_type=InteractionType.SYNERGIZES,
        severity=1,
        explanation="Unlike retinol, bakuchiol is stable with vitamin C and doesn't cause pH conflicts.",
        recommendation="Great daytime anti-aging combination."
    ))
    
    # ========== INTERACTIONS ==========
    
    # Retinol interactions
    kg.add_interaction(Interaction(
        ingredient_a="retinol",
        ingredient_b="glycolic_acid",
        interaction_type=InteractionType.CONFLICTS,
        severity=8,
        explanation="Both increase cell turnover and can severely irritate skin when combined. Risk of redness, peeling, and damaged skin barrier.",
        recommendation="Use on alternate nights. Example: retinol Mon/Wed/Fri, glycolic Tue/Sat."
    ))
    
    kg.add_interaction(Interaction(
        ingredient_a="retinol",
        ingredient_b="lactic_acid",
        interaction_type=InteractionType.CONFLICTS,
        severity=7,
        explanation="Both exfoliating agents that can cause irritation when combined.",
        recommendation="Use on alternate nights."
    ))
    
    kg.add_interaction(Interaction(
        ingredient_a="retinol",
        ingredient_b="salicylic_acid",
        interaction_type=InteractionType.CAUTION,
        severity=5,
        explanation="Can be used together by experienced users, but may cause dryness and irritation.",
        recommendation="If combining, use salicylic in AM and retinol in PM, or start very slowly."
    ))
    
    kg.add_interaction(Interaction(
        ingredient_a="retinol",
        ingredient_b="vitamin_c",
        interaction_type=InteractionType.REQUIRES_WAITING,
        severity=4,
        wait_minutes=30,
        explanation="Different optimal pH levels. Vitamin C needs acidic environment (pH 3), retinol works best at pH 5.5-6.",
        recommendation="Use vitamin C in AM, retinol in PM. Or wait 30 minutes between applications."
    ))
    
    kg.add_interaction(Interaction(
        ingredient_a="retinol",
        ingredient_b="benzoyl_peroxide",
        interaction_type=InteractionType.DEACTIVATES,
        severity=9,
        explanation="Benzoyl peroxide oxidizes and deactivates retinol, making both less effective.",
        recommendation="Never use together. Use BP in AM, retinol in PM, or on alternate days."
    ))
    
    kg.add_interaction(Interaction(
        ingredient_a="retinol",
        ingredient_b="niacinamide",
        interaction_type=InteractionType.SYNERGIZES,
        severity=1,
        explanation="Niacinamide helps reduce the irritation from retinol while both work on similar concerns.",
        recommendation="Great combination! Apply niacinamide first, then retinol."
    ))
    
    kg.add_interaction(Interaction(
        ingredient_a="retinol",
        ingredient_b="hyaluronic_acid",
        interaction_type=InteractionType.SYNERGIZES,
        severity=1,
        explanation="Hyaluronic acid provides hydration that counteracts retinol's drying effects.",
        recommendation="Apply hyaluronic acid to damp skin, follow with retinol."
    ))
    
    # Vitamin C interactions
    kg.add_interaction(Interaction(
        ingredient_a="vitamin_c",
        ingredient_b="niacinamide",
        interaction_type=InteractionType.CAUTION,
        severity=3,
        explanation="Old studies suggested they cancel out, but modern research shows this is largely a myth. However, high concentrations of both may cause flushing.",
        recommendation="Can use together. If you experience flushing, apply vitamin C in AM and niacinamide in PM."
    ))
    
    kg.add_interaction(Interaction(
        ingredient_a="vitamin_c",
        ingredient_b="spf",
        interaction_type=InteractionType.SYNERGIZES,
        severity=1,
        explanation="Vitamin C boosts sunscreen effectiveness by neutralizing free radicals that UV rays generate.",
        recommendation="Perfect morning combination! Vitamin C first, then sunscreen."
    ))
    
    kg.add_interaction(Interaction(
        ingredient_a="vitamin_c",
        ingredient_b="vitamin_c_derivative",
        interaction_type=InteractionType.CAUTION,
        severity=2,
        explanation="No need to use both - they serve the same purpose.",
        recommendation="Pick one. L-ascorbic acid is more potent; derivatives are gentler."
    ))
    
    # AHA/BHA interactions
    kg.add_interaction(Interaction(
        ingredient_a="glycolic_acid",
        ingredient_b="salicylic_acid",
        interaction_type=InteractionType.CAUTION,
        severity=6,
        explanation="Both are exfoliants. Using together increases irritation risk significantly.",
        recommendation="Use on different days, or choose one based on your primary concern (texture vs. acne)."
    ))
    
    kg.add_interaction(Interaction(
        ingredient_a="glycolic_acid",
        ingredient_b="lactic_acid",
        interaction_type=InteractionType.CAUTION,
        severity=5,
        explanation="Both are AHAs - using together is usually unnecessary and increases irritation.",
        recommendation="Choose one. Glycolic for deeper exfoliation, lactic for gentler + hydration."
    ))
    
    # Benzoyl Peroxide interactions
    kg.add_interaction(Interaction(
        ingredient_a="benzoyl_peroxide",
        ingredient_b="vitamin_c",
        interaction_type=InteractionType.DEACTIVATES,
        severity=8,
        explanation="Benzoyl peroxide oxidizes vitamin C, rendering both less effective.",
        recommendation="Use at different times of day. Vitamin C in AM, BP in PM."
    ))
    
    # Peptide interactions
    kg.add_interaction(Interaction(
        ingredient_a="peptides",
        ingredient_b="glycolic_acid",
        interaction_type=InteractionType.CAUTION,
        severity=5,
        explanation="Strong acids can break down peptide chains, reducing their effectiveness.",
        recommendation="Apply acid first, wait 20-30 minutes for pH to normalize, then apply peptides."
    ))
    
    kg.add_interaction(Interaction(
        ingredient_a="peptides",
        ingredient_b="vitamin_c",
        interaction_type=InteractionType.CAUTION,
        severity=4,
        explanation="The acidic pH of L-ascorbic acid can destabilize some peptides.",
        recommendation="Use at different times of day, or use vitamin C derivatives instead."
    ))
    
    # Beneficial combinations
    kg.add_interaction(Interaction(
        ingredient_a="hyaluronic_acid",
        ingredient_b="niacinamide",
        interaction_type=InteractionType.SYNERGIZES,
        severity=1,
        explanation="Both are hydrating and work at similar pH levels. Niacinamide strengthens barrier while HA hydrates.",
        recommendation="Excellent combination for all skin types."
    ))
    
    kg.add_interaction(Interaction(
        ingredient_a="hyaluronic_acid",
        ingredient_b="ceramides",
        interaction_type=InteractionType.SYNERGIZES,
        severity=1,
        explanation="HA pulls in moisture, ceramides lock it in. Perfect moisture-barrier support.",
        recommendation="Apply HA to damp skin, follow with ceramide moisturizer."
    ))
    
    kg.add_interaction(Interaction(
        ingredient_a="niacinamide",
        ingredient_b="salicylic_acid",
        interaction_type=InteractionType.SYNERGIZES,
        severity=1,
        explanation="Niacinamide calms and regulates oil while BHA clears pores. Great for acne.",
        recommendation="Can be layered or found together in products."
    ))
    
    kg.add_interaction(Interaction(
        ingredient_a="azelaic_acid",
        ingredient_b="niacinamide",
        interaction_type=InteractionType.SYNERGIZES,
        severity=1,
        explanation="Both target hyperpigmentation and work at compatible pH levels.",
        recommendation="Excellent combination for brightening and evening skin tone."
    ))
    
    return kg