"""
Skincare Advisor Agent

KBAI Concepts:
- Natural Language Understanding: Parse user questions
- Knowledge Retrieval: Find relevant information
- Explanation Generation: Provide reasoning for answers

This agent can answer questions about ingredients, routines,
and skincare concerns using the knowledge base and optionally
an LLM for natural language generation.
"""

from dataclasses import dataclass
from typing import Optional, Callable
from enum import Enum
import re

from knowledge.ingredients import (
    IngredientKnowledgeGraph,
    SkinProfile,
    SkinType,
    SkinConcern,
    InteractionType
)
from routines.builder import RoutineBuilder, RoutineTime


class QueryType(Enum):
    """Types of questions the agent can handle."""
    COMPATIBILITY = "compatibility"  # "Can I use X with Y?"
    INGREDIENT_INFO = "ingredient_info"  # "What is retinol?"
    ROUTINE_HELP = "routine_help"  # "What order should I apply?"
    CONCERN_ADVICE = "concern_advice"  # "What should I use for acne?"
    GENERAL = "general"  # Anything else


@dataclass
class QueryResult:
    """Result of processing a user query."""
    query_type: QueryType
    answer: str
    confidence: float  # 0-1, how confident we are in the answer
    sources: list[str]  # What knowledge was used
    follow_up_questions: list[str]  # Suggested follow-ups


class SkincareAdvisor:
    """AI-powered skincare advisor agent.
    
    This agent uses the knowledge graph to answer questions.
    It can work standalone (rule-based) or with an LLM for
    more natural responses.
    """
    
    def __init__(
        self, 
        knowledge_graph: IngredientKnowledgeGraph,
        llm_handler: Optional[Callable] = None
    ):
        self.kg = knowledge_graph
        self.routine_builder = RoutineBuilder(knowledge_graph)
        self.llm_handler = llm_handler  # Optional LLM for natural responses
        
        # Pattern matching for query classification
        self._compatibility_patterns = [
            r"can i use (.+) with (.+)",
            r"can i mix (.+) and (.+)",
            r"is (.+) compatible with (.+)",
            r"(.+) and (.+) together",
            r"combine (.+) and (.+)",
            r"layer (.+) with (.+)",
        ]
        
        self._ingredient_patterns = [
            r"what is (.+)",
            r"tell me about (.+)",
            r"how does (.+) work",
            r"benefits of (.+)",
            r"what does (.+) do",
        ]
        
        self._concern_patterns = [
            r"what should i use for (.+)",
            r"help with (.+)",
            r"how to treat (.+)",
            r"best for (.+)",
            r"recommend.* for (.+)",
        ]
        
        self._order_patterns = [
            r"what order",
            r"how to layer",
            r"which first",
            r"sequence",
            r"routine order",
        ]
    
    def ask(self, question: str, profile: Optional[SkinProfile] = None) -> QueryResult:
        """Process a natural language question.
        
        KBAI: This is the main reasoning loop - classify, retrieve, respond.
        """
        question_lower = question.lower().strip()
        
        # Classify the query
        query_type, extracted = self._classify_query(question_lower)
        
        # Route to appropriate handler
        if query_type == QueryType.COMPATIBILITY:
            return self._handle_compatibility(extracted, question)
        elif query_type == QueryType.INGREDIENT_INFO:
            return self._handle_ingredient_info(extracted, question)
        elif query_type == QueryType.CONCERN_ADVICE:
            return self._handle_concern_advice(extracted, profile, question)
        elif query_type == QueryType.ROUTINE_HELP:
            return self._handle_routine_help(extracted, profile, question)
        else:
            return self._handle_general(question, profile)
    
    def _classify_query(self, question: str) -> tuple[QueryType, list[str]]:
        """Classify the type of question and extract key terms."""
        
        # Check compatibility patterns
        for pattern in self._compatibility_patterns:
            match = re.search(pattern, question)
            if match:
                return QueryType.COMPATIBILITY, list(match.groups())
        
        # Check ingredient info patterns
        for pattern in self._ingredient_patterns:
            match = re.search(pattern, question)
            if match:
                return QueryType.INGREDIENT_INFO, list(match.groups())
        
        # Check concern patterns
        for pattern in self._concern_patterns:
            match = re.search(pattern, question)
            if match:
                return QueryType.CONCERN_ADVICE, list(match.groups())
        
        # Check order patterns
        for pattern in self._order_patterns:
            if re.search(pattern, question):
                return QueryType.ROUTINE_HELP, []
        
        return QueryType.GENERAL, []
    
    def _handle_compatibility(self, extracted: list[str], original_question: str) -> QueryResult:
        """Handle 'Can I use X with Y?' questions."""
        if len(extracted) < 2:
            return QueryResult(
                query_type=QueryType.COMPATIBILITY,
                answer="I need two ingredients to check compatibility. Try asking 'Can I use retinol with vitamin C?'",
                confidence=0.5,
                sources=[],
                follow_up_questions=["Can I use retinol with niacinamide?"]
            )
        
        ing_a_name, ing_b_name = extracted[0].strip(), extracted[1].strip()
        
        # Look up ingredients
        ing_a = self.kg.get_ingredient(ing_a_name)
        ing_b = self.kg.get_ingredient(ing_b_name)
        
        if not ing_a:
            # Try fuzzy search
            matches = self.kg.find_ingredient(ing_a_name)
            if matches:
                ing_a = matches[0]
        
        if not ing_b:
            matches = self.kg.find_ingredient(ing_b_name)
            if matches:
                ing_b = matches[0]
        
        if not ing_a or not ing_b:
            missing = ing_a_name if not ing_a else ing_b_name
            return QueryResult(
                query_type=QueryType.COMPATIBILITY,
                answer=f"I don't have information about '{missing}' in my database. Could you check the spelling or try another name?",
                confidence=0.3,
                sources=[],
                follow_up_questions=[f"What is {missing}?"]
            )
        
        # Get the interaction
        explanation = self.kg.explain_interaction(ing_a.id, ing_b.id)
        
        # Get compatibility check for more details
        compatibility = self.kg.check_compatibility([ing_a.id, ing_b.id])
        
        # Build comprehensive answer
        answer_parts = [explanation]
        
        if compatibility['synergies']:
            answer_parts.append("\n\n✨ These ingredients actually work well together!")
        
        sources = [f"Ingredient: {ing_a.name}", f"Ingredient: {ing_b.name}"]
        
        follow_ups = []
        if compatibility['conflicts'] or compatibility['cautions']:
            follow_ups.append(f"What can I use instead of {ing_a.name}?")
        follow_ups.append(f"What order should I apply {ing_a.name} and {ing_b.name}?")
        
        return QueryResult(
            query_type=QueryType.COMPATIBILITY,
            answer="\n".join(answer_parts),
            confidence=0.9,
            sources=sources,
            follow_up_questions=follow_ups
        )
    
    def _handle_ingredient_info(self, extracted: list[str], original_question: str) -> QueryResult:
        """Handle 'What is X?' questions about ingredients."""
        if not extracted:
            return QueryResult(
                query_type=QueryType.INGREDIENT_INFO,
                answer="What ingredient would you like to know about?",
                confidence=0.5,
                sources=[],
                follow_up_questions=["What is retinol?", "Tell me about niacinamide"]
            )
        
        ing_name = extracted[0].strip().rstrip('?')
        ingredient = self.kg.get_ingredient(ing_name)
        
        if not ingredient:
            matches = self.kg.find_ingredient(ing_name)
            if matches:
                ingredient = matches[0]
        
        if not ingredient:
            return QueryResult(
                query_type=QueryType.INGREDIENT_INFO,
                answer=f"I don't have detailed information about '{ing_name}'. It might be a less common ingredient or known by another name.",
                confidence=0.3,
                sources=[],
                follow_up_questions=["What ingredients help with acne?"]
            )
        
        # Build detailed response
        lines = [
            f"## {ingredient.name}",
            f"\n**Category:** {ingredient.category.value.replace('_', ' ').title()}",
            f"\n**What it does:** {ingredient.description}",
        ]
        
        if ingredient.how_it_works:
            lines.append(f"\n**How it works:** {ingredient.how_it_works}")
        
        concerns = [c.value.replace('_', ' ').title() for c in ingredient.addresses_concerns]
        if concerns:
            lines.append(f"\n**Good for:** {', '.join(concerns)}")
        
        if ingredient.caution_skin_types:
            cautions = [s.value.title() for s in ingredient.caution_skin_types]
            lines.append(f"\n**Use with caution if you have:** {', '.join(cautions)} skin")
        
        if ingredient.usage_tips:
            lines.append("\n**Tips:**")
            for tip in ingredient.usage_tips:
                lines.append(f"• {tip}")
        
        if ingredient.time_of_day.value != "either":
            time_str = ingredient.time_of_day.value.replace('_', ' ')
            lines.append(f"\n**Best used:** {time_str}")
        
        # Get interactions for follow-up suggestions
        interactions = self.kg.get_all_interactions(ingredient.id)
        follow_ups = [f"Can I use {ingredient.name} with retinol?"]
        
        if interactions:
            for interaction in interactions[:2]:
                other = interaction.ingredient_b if interaction.ingredient_a == ingredient.id else interaction.ingredient_a
                other_ing = self.kg.get_ingredient(other)
                if other_ing:
                    follow_ups.append(f"Can I use {ingredient.name} with {other_ing.name}?")
        
        return QueryResult(
            query_type=QueryType.INGREDIENT_INFO,
            answer="\n".join(lines),
            confidence=0.95,
            sources=[f"Ingredient database: {ingredient.name}"],
            follow_up_questions=follow_ups[:3]
        )
    
    def _handle_concern_advice(
        self, 
        extracted: list[str], 
        profile: Optional[SkinProfile],
        original_question: str
    ) -> QueryResult:
        """Handle 'What should I use for X?' questions."""
        if not extracted:
            return QueryResult(
                query_type=QueryType.CONCERN_ADVICE,
                answer="What skin concern would you like help with?",
                confidence=0.5,
                sources=[],
                follow_up_questions=[
                    "What should I use for acne?",
                    "Help with anti-aging",
                    "Best for hyperpigmentation"
                ]
            )
        
        concern_text = extracted[0].strip().rstrip('?')
        
        # Map common terms to concerns
        concern_mapping = {
            "acne": SkinConcern.ACNE,
            "pimples": SkinConcern.ACNE,
            "breakouts": SkinConcern.ACNE,
            "aging": SkinConcern.AGING,
            "anti-aging": SkinConcern.AGING,
            "wrinkles": SkinConcern.AGING,
            "fine lines": SkinConcern.AGING,
            "dark spots": SkinConcern.HYPERPIGMENTATION,
            "hyperpigmentation": SkinConcern.HYPERPIGMENTATION,
            "pigmentation": SkinConcern.HYPERPIGMENTATION,
            "uneven skin tone": SkinConcern.HYPERPIGMENTATION,
            "dry skin": SkinConcern.DRYNESS,
            "dryness": SkinConcern.DRYNESS,
            "dehydration": SkinConcern.DRYNESS,
            "oily skin": SkinConcern.OILINESS,
            "oiliness": SkinConcern.OILINESS,
            "shine": SkinConcern.OILINESS,
            "sensitivity": SkinConcern.SENSITIVITY,
            "sensitive skin": SkinConcern.SENSITIVITY,
            "redness": SkinConcern.REDNESS,
            "dull skin": SkinConcern.DULLNESS,
            "dullness": SkinConcern.DULLNESS,
            "texture": SkinConcern.TEXTURE,
            "rough skin": SkinConcern.TEXTURE,
            "pores": SkinConcern.PORES,
            "large pores": SkinConcern.PORES,
        }
        
        concern = None
        for term, mapped_concern in concern_mapping.items():
            if term in concern_text.lower():
                concern = mapped_concern
                break
        
        if not concern:
            return QueryResult(
                query_type=QueryType.CONCERN_ADVICE,
                answer=f"I'm not sure what '{concern_text}' refers to. Try asking about specific concerns like acne, aging, dark spots, dryness, or oiliness.",
                confidence=0.4,
                sources=[],
                follow_up_questions=[
                    "What should I use for acne?",
                    "Best ingredients for aging?"
                ]
            )
        
        # Get recommended ingredients
        ingredients = self.kg.get_ingredients_by_concern(concern)
        
        if not ingredients:
            return QueryResult(
                query_type=QueryType.CONCERN_ADVICE,
                answer=f"I don't have specific recommendations for {concern.value} yet.",
                confidence=0.3,
                sources=[],
                follow_up_questions=[]
            )
        
        # Build response
        lines = [f"## Recommended ingredients for {concern.value.replace('_', ' ')}:\n"]
        
        for ing in ingredients[:5]:  # Top 5
            lines.append(f"**{ing.name}** - {ing.description}")
            if ing.usage_tips:
                lines.append(f"  _Tip: {ing.usage_tips[0]}_")
            lines.append("")
        
        # Add cautions if profile provided
        if profile and profile.skin_type in [SkinType.SENSITIVE, SkinType.DRY]:
            lines.append(f"\n⚠️ Since you have {profile.skin_type.value} skin, start with gentler options and patch test first.")
        
        follow_ups = [
            f"Can I use {ingredients[0].name} with {ingredients[1].name}?" if len(ingredients) > 1 else "",
            f"What is {ingredients[0].name}?",
            "Build me a routine"
        ]
        
        return QueryResult(
            query_type=QueryType.CONCERN_ADVICE,
            answer="\n".join(lines),
            confidence=0.85,
            sources=[f"Concern: {concern.value}"],
            follow_up_questions=[q for q in follow_ups if q]
        )
    
    def _handle_routine_help(
        self, 
        extracted: list[str],
        profile: Optional[SkinProfile],
        original_question: str
    ) -> QueryResult:
        """Handle routine ordering and building questions."""
        lines = [
            "## Standard Skincare Routine Order\n",
            "**Morning (AM):**",
            "1. Cleanser (or just water)",
            "2. Toner (optional)",
            "3. Vitamin C serum",
            "4. Other treatments/serums (water-based)",
            "5. Eye cream",
            "6. Moisturizer",
            "7. Sunscreen (SPF 30+) ← ESSENTIAL\n",
            "**Evening (PM):**",
            "1. Oil cleanser / Makeup remover",
            "2. Water-based cleanser",
            "3. Toner (optional)",
            "4. Exfoliant (AHA/BHA) - not daily",
            "5. Treatments (retinol, etc.)",
            "6. Serums (thinnest to thickest)",
            "7. Eye cream",
            "8. Moisturizer",
            "9. Face oil (optional)",
            "10. Sleeping mask (optional)\n",
            "**Key Rules:**",
            "• Thin → Thick consistency",
            "• Water-based → Oil-based",
            "• Actives on dry skin to reduce irritation",
            "• Wait 1-2 minutes between layers",
        ]
        
        return QueryResult(
            query_type=QueryType.ROUTINE_HELP,
            answer="\n".join(lines),
            confidence=0.95,
            sources=["General skincare guidelines"],
            follow_up_questions=[
                "Can I use vitamin C and niacinamide together?",
                "What order for retinol and hyaluronic acid?",
                "What should I use for my skin concerns?"
            ]
        )
    
    def _handle_general(self, question: str, profile: Optional[SkinProfile]) -> QueryResult:
        """Handle general questions that don't fit other categories."""
        # Try to find any ingredients mentioned
        found_ingredients = []
        for ing_id, ingredient in self.kg.ingredients.items():
            if ingredient.name.lower() in question.lower():
                found_ingredients.append(ingredient)
            else:
                for alias in ingredient.aliases:
                    if alias.lower() in question.lower():
                        found_ingredients.append(ingredient)
                        break
        
        if found_ingredients:
            # Provide info about found ingredients
            if len(found_ingredients) == 1:
                return self._handle_ingredient_info([found_ingredients[0].name], question)
            elif len(found_ingredients) >= 2:
                return self._handle_compatibility(
                    [found_ingredients[0].name, found_ingredients[1].name], 
                    question
                )
        
        # Default helpful response
        return QueryResult(
            query_type=QueryType.GENERAL,
            answer=(
                "I'm not sure I understood that question. I can help you with:\n\n"
                "• **Ingredient compatibility** - 'Can I use retinol with AHA?'\n"
                "• **Ingredient information** - 'What is niacinamide?'\n"
                "• **Concern-based advice** - 'What should I use for acne?'\n"
                "• **Routine help** - 'What order should I apply products?'\n\n"
                "Try asking one of these types of questions!"
            ),
            confidence=0.3,
            sources=[],
            follow_up_questions=[
                "Can I use vitamin C with niacinamide?",
                "What should I use for aging?",
                "What order should I apply my products?"
            ]
        )
