"""
MixMyRoutine Skincare Advisor

KBAI Concepts Demonstrated:
- Knowledge Retrieval: Fetch relevant info from semantic network
- Natural Language Understanding: Parse and classify questions  
- Context-Augmented Generation: Ground LLM responses in knowledge base
- Explanation Generation: Provide reasoning for recommendations

This advisor combines:
1. Rule-based ingredient matching (fast, reliable)
2. Knowledge graph lookups (accurate data)
3. Claude LLM integration (natural responses)
"""

import os
from dataclasses import dataclass
from typing import Optional
from enum import Enum

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Note: anthropic package not installed. LLM features disabled.")

from app.core.knowledge.ingredients import (
    IngredientKnowledgeGraph,
    SkinProfile,
    SkinType,
    SkinConcern,
    InteractionType
)
from app.core.routines.builder import RoutineBuilder


class QueryType(Enum):
    """Types of questions the agent can handle."""
    COMPATIBILITY = "compatibility"
    INGREDIENT_INFO = "ingredient_info"
    ROUTINE_HELP = "routine_help"
    CONCERN_ADVICE = "concern_advice"
    GENERAL = "general"


@dataclass
class QueryResult:
    """Result of processing a user query."""
    query_type: QueryType
    answer: str
    confidence: float
    sources: list[str]
    follow_up_questions: list[str]


class SkincareAdvisor:
    """
    AI-powered skincare advisor combining KBAI + LLM.
    
    Architecture:
    ┌─────────────────────────────────────────────────┐
    │                 User Question                    │
    └─────────────────────┬───────────────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────────────┐
    │           Extract Ingredients                    │
    │     (pattern matching + alias lookup)           │
    └─────────────────────┬───────────────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────────────┐
    │         Retrieve Knowledge Context              │
    │    (knowledge graph + interaction rules)        │
    └─────────────────────┬───────────────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────────────┐
    │           Generate Response                      │
    │  (Claude LLM if available, else rule-based)     │
    └─────────────────────────────────────────────────┘
    """
    
    def __init__(
        self, 
        knowledge_graph: IngredientKnowledgeGraph,
        api_key: Optional[str] = None
    ):
        self.kg = knowledge_graph
        self.routine_builder = RoutineBuilder(knowledge_graph)
        
        # Initialize Claude client
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        
        if self.api_key and ANTHROPIC_AVAILABLE:
            try:
                self.client = Anthropic(api_key=self.api_key)
                print("✅ Claude API initialized successfully")
            except Exception as e:
                print(f"⚠️ Could not initialize Claude: {e}")
        else:
            print("ℹ️ Running in rule-based mode (no API key)")
        
        # Comprehensive ingredient aliases for better NLU
        self._ingredient_aliases = {
            # Vitamin C variations
            "vitamin c": "vitamin_c",
            "vit c": "vitamin_c",
            "vitc": "vitamin_c",
            "ascorbic acid": "vitamin_c",
            "l-ascorbic acid": "vitamin_c",
            "l ascorbic acid": "vitamin_c",
            "ascorbic": "vitamin_c",
            
            # Retinoids
            "retinol": "retinol",
            "retinoid": "retinol",
            "retin-a": "retinol",
            "retin a": "retinol",
            "tretinoin": "retinol",
            "retinal": "retinol",
            "retinaldehyde": "retinol",
            
            # AHAs
            "aha": "glycolic_acid",
            "ahas": "glycolic_acid",
            "alpha hydroxy acid": "glycolic_acid",
            "alpha hydroxy": "glycolic_acid",
            "glycolic acid": "glycolic_acid",
            "glycolic": "glycolic_acid",
            "lactic acid": "lactic_acid",
            "lactic": "lactic_acid",
            "mandelic acid": "mandelic_acid",
            "mandelic": "mandelic_acid",
            
            # BHAs
            "bha": "salicylic_acid",
            "bhas": "salicylic_acid",
            "beta hydroxy acid": "salicylic_acid",
            "beta hydroxy": "salicylic_acid",
            "salicylic acid": "salicylic_acid",
            "salicylic": "salicylic_acid",
            
            # Other common ingredients
            "hyaluronic acid": "hyaluronic_acid",
            "hyaluronic": "hyaluronic_acid",
            "ha": "hyaluronic_acid",
            "niacinamide": "niacinamide",
            "niacin": "niacinamide",
            "vitamin b3": "niacinamide",
            "vit b3": "niacinamide",
            "benzoyl peroxide": "benzoyl_peroxide",
            "benzoyl": "benzoyl_peroxide",
            "bp": "benzoyl_peroxide",
            "azelaic acid": "azelaic_acid",
            "azelaic": "azelaic_acid",
            "vitamin e": "vitamin_e",
            "vit e": "vitamin_e",
            "tocopherol": "vitamin_e",
            "ceramides": "ceramides",
            "ceramide": "ceramides",
            "peptides": "peptides",
            "peptide": "peptides",
            "squalane": "squalane",
            "zinc": "zinc",
            "zinc oxide": "zinc",
            "centella": "centella_asiatica",
            "cica": "centella_asiatica",
            "centella asiatica": "centella_asiatica",
            "arbutin": "arbutin",
            "alpha arbutin": "arbutin",
            "kojic acid": "kojic_acid",
            "kojic": "kojic_acid",
            "tranexamic acid": "tranexamic_acid",
            "tranexamic": "tranexamic_acid",
            "ferulic acid": "ferulic_acid",
            "ferulic": "ferulic_acid",
            "panthenol": "panthenol",
            "vitamin b5": "panthenol",
            "pro vitamin b5": "panthenol",
            "allantoin": "allantoin",
            "bakuchiol": "bakuchiol",
        }
    
    def _extract_ingredients(self, text: str) -> list[str]:
        """
        Extract ingredient IDs from text using multiple strategies.
        
        KBAI: This is our NLU component - converting natural language
        to structured knowledge graph queries.
        """
        text_lower = text.lower()
        found = set()
        
        # Strategy 1: Check for known aliases (longest match first)
        sorted_aliases = sorted(self._ingredient_aliases.keys(), key=len, reverse=True)
        for alias in sorted_aliases:
            if alias in text_lower:
                ing_id = self._ingredient_aliases[alias]
                if ing_id not in found:
                    found.add(ing_id)
                    # Remove matched text to avoid double-matching
                    text_lower = text_lower.replace(alias, " ")
        
        # Strategy 2: Check ingredient names directly from knowledge base
        for ing_id, ingredient in self.kg.ingredients.items():
            name_lower = ingredient.name.lower()
            if name_lower in text_lower and ing_id not in found:
                found.add(ing_id)
        
        # Strategy 3: Check ingredient IDs (underscore format)
        for ing_id in self.kg.ingredients.keys():
            # Convert "vitamin_c" to check for "vitamin c" or "vitamin-c"
            variations = [
                ing_id,
                ing_id.replace("_", " "),
                ing_id.replace("_", "-"),
            ]
            for var in variations:
                if var in text_lower and ing_id not in found:
                    found.add(ing_id)
                    break
        
        return list(found)
    
    def _build_knowledge_context(self, ingredients: list[str]) -> str:
        """
        Build context from knowledge graph for LLM grounding.
        
        KBAI: This is knowledge retrieval - fetching relevant frames
        from our semantic network to augment the LLM's response.
        """
        if not ingredients:
            return ""
        
        context_parts = []
        
        # Get ingredient details
        for ing_id in ingredients:
            ing = self.kg.get_ingredient(ing_id)
            if ing:
                concerns = ", ".join(c.value for c in ing.addresses_concerns) if ing.addresses_concerns else "General skincare"
                context_parts.append(f"""
### {ing.name}
- **Category**: {ing.category.value}
- **Description**: {ing.description}
- **How it works**: {ing.how_it_works or 'N/A'}
- **Best for**: {concerns}
- **Best time**: {ing.time_of_day.value}
- **Beginner friendly**: {'Yes' if ing.beginner_friendly else 'No - start slowly'}
""")
        
        # Get interactions between ingredients
        if len(ingredients) >= 2:
            context_parts.append("\n## Interactions")
            
            for i, ing_a in enumerate(ingredients):
                for ing_b in ingredients[i+1:]:
                    # Get interaction explanation
                    explanation = self.kg.explain_interaction(ing_a, ing_b)
                    
                    # Get detailed compatibility
                    compat = self.kg.check_compatibility([ing_a, ing_b])
                    
                    ing_a_name = self.kg.get_ingredient(ing_a).name if self.kg.get_ingredient(ing_a) else ing_a
                    ing_b_name = self.kg.get_ingredient(ing_b).name if self.kg.get_ingredient(ing_b) else ing_b
                    
                    context_parts.append(f"\n### {ing_a_name} + {ing_b_name}")
                    
                    if explanation:
                        context_parts.append(explanation)
                    
                    if compat.get('conflicts'):
                        context_parts.append("⚠️ **CONFLICT**: These should NOT be used together in the same routine!")
                        for c in compat['conflicts']:
                            if isinstance(c, dict) and c.get('explanation'):
                                context_parts.append(f"- {c['explanation']}")
                    
                    if compat.get('cautions'):
                        context_parts.append("⚡ **CAUTION**: Use carefully")
                        for c in compat['cautions']:
                            if isinstance(c, dict):
                                context_parts.append(f"- {c.get('explanation', '')}")
                                if c.get('recommendation'):
                                    context_parts.append(f"- **Recommendation**: {c['recommendation']}")
                    
                    if compat.get('synergies'):
                        context_parts.append("✨ **SYNERGY**: These work great together!")
                        for s in compat['synergies']:
                            if isinstance(s, dict) and s.get('explanation'):
                                context_parts.append(f"- {s['explanation']}")
                    
                    if not any([compat.get('conflicts'), compat.get('cautions'), compat.get('synergies')]):
                        context_parts.append("✅ No known interactions - generally safe to use together")
        
        return "\n".join(context_parts)
    
    def _get_concern_context(self, question: str) -> str:
        """Get ingredient recommendations for skin concerns mentioned."""
        concern_keywords = {
            "acne": SkinConcern.ACNE,
            "pimple": SkinConcern.ACNE,
            "breakout": SkinConcern.ACNE,
            "aging": SkinConcern.AGING,
            "anti-aging": SkinConcern.AGING,
            "wrinkle": SkinConcern.AGING,
            "fine line": SkinConcern.AGING,
            "dark spot": SkinConcern.HYPERPIGMENTATION,
            "hyperpigmentation": SkinConcern.HYPERPIGMENTATION,
            "pigmentation": SkinConcern.HYPERPIGMENTATION,
            "sun spot": SkinConcern.HYPERPIGMENTATION,
            "melasma": SkinConcern.HYPERPIGMENTATION,
            "dry": SkinConcern.DRYNESS,
            "dryness": SkinConcern.DRYNESS,
            "dehydrat": SkinConcern.DRYNESS,
            "oily": SkinConcern.OILINESS,
            "oiliness": SkinConcern.OILINESS,
            "sebum": SkinConcern.OILINESS,
            "sensitive": SkinConcern.SENSITIVITY,
            "sensitivity": SkinConcern.SENSITIVITY,
            "irritat": SkinConcern.SENSITIVITY,
            "redness": SkinConcern.REDNESS,
            "rosacea": SkinConcern.REDNESS,
            "dull": SkinConcern.DULLNESS,
            "glow": SkinConcern.DULLNESS,
            "bright": SkinConcern.DULLNESS,
            "texture": SkinConcern.TEXTURE,
            "rough": SkinConcern.TEXTURE,
            "pore": SkinConcern.PORES,
        }
        
        question_lower = question.lower()
        matched_concerns = set()
        
        for keyword, concern in concern_keywords.items():
            if keyword in question_lower:
                matched_concerns.add(concern)
        
        if not matched_concerns:
            return ""
        
        context_parts = ["\n## Recommended Ingredients for Your Concerns"]
        
        for concern in matched_concerns:
            recommendations = []
            for ing_id, ingredient in self.kg.ingredients.items():
                if concern in ingredient.addresses_concerns:
                    recommendations.append(f"- **{ingredient.name}**: {ingredient.description[:80]}...")
            
            if recommendations:
                context_parts.append(f"\n### For {concern.value}:")
                context_parts.extend(recommendations[:5])
        
        return "\n".join(context_parts)
    
    def ask(self, question: str, profile: Optional[SkinProfile] = None) -> QueryResult:
        """
        Main entry point - process a user question.
        
        KBAI Pipeline:
        1. Extract ingredients (NLU)
        2. Retrieve knowledge (Knowledge Retrieval)
        3. Generate response (LLM or Rule-based)
        """
        # Step 1: Extract ingredients from question
        ingredients = self._extract_ingredients(question)
        
        # Step 2: Build knowledge context
        knowledge_context = self._build_knowledge_context(ingredients)
        concern_context = self._get_concern_context(question)
        
        full_context = knowledge_context + concern_context
        
        # Step 3: Generate response
        if self.client:
            return self._generate_llm_response(question, full_context, ingredients, profile)
        else:
            return self._generate_rule_response(question, full_context, ingredients)
    
    def _generate_llm_response(
        self,
        question: str,
        context: str,
        ingredients: list[str],
        profile: Optional[SkinProfile]
    ) -> QueryResult:
        """Generate response using Claude API."""
        
        system_prompt = """You are MixMyRoutine's skincare advisor - a friendly, knowledgeable expert.

RULES:
1. Base your answers on the Knowledge Base provided - don't invent interactions
2. Be conversational and helpful, not robotic
3. Keep responses concise (2-3 paragraphs max)
4. Include specific, actionable advice
5. If the knowledge base doesn't cover something, say so honestly
6. Always prioritize skin safety - recommend patch testing for new products

FORMAT:
- Use clear paragraphs
- Include AM/PM recommendations when relevant
- End with a practical tip or next step"""

        profile_info = ""
        if profile:
            concerns = ", ".join(c.value for c in profile.concerns) if profile.concerns else "none specified"
            profile_info = f"\n\nUser's skin: {profile.skin_type.value} type with concerns: {concerns}"

        user_message = f"""Question: {question}

---
KNOWLEDGE BASE:
{context if context else "No specific ingredients detected in the question."}
{profile_info}
---

Provide a helpful response based on the knowledge base above."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            
            answer = response.content[0].text
            
            return QueryResult(
                query_type=self._classify_query(question),
                answer=answer,
                confidence=0.9 if context else 0.7,
                sources=[f"Knowledge base: {ing}" for ing in ingredients],
                follow_up_questions=self._get_follow_ups(question, ingredients)
            )
            
        except Exception as e:
            print(f"LLM Error: {e}")
            return self._generate_rule_response(question, context, ingredients)
    
    def _generate_rule_response(
        self,
        question: str,
        context: str,
        ingredients: list[str]
    ) -> QueryResult:
        """Generate response using rules when LLM is unavailable."""
        
        if not ingredients and not context:
            return QueryResult(
                query_type=QueryType.GENERAL,
                answer="""I'd be happy to help with your skincare question! 

To give you the best advice, try asking about specific ingredients. For example:
• "Can I use retinol with vitamin C?"
• "What is niacinamide good for?"  
• "What should I use for acne?"

I have information on 26 ingredients and 41 interaction rules in my knowledge base.""",
                confidence=0.5,
                sources=[],
                follow_up_questions=[
                    "Can I use retinol with niacinamide?",
                    "What ingredients help with acne?",
                    "What's a good anti-aging routine?"
                ]
            )
        
        # Build response from context
        if len(ingredients) >= 2:
            # Compatibility question
            compat = self.kg.check_compatibility(ingredients)
            
            ing_names = []
            for ing_id in ingredients:
                ing = self.kg.get_ingredient(ing_id)
                if ing:
                    ing_names.append(ing.name)
            
            if compat.get('conflicts'):
                answer = f"⚠️ **I'd be careful with this combination.**\n\n{context}\n\nConsider using these ingredients at different times (one in AM, one in PM) or on alternating days."
            elif compat.get('cautions'):
                answer = f"⚡ **These can be used together, but with some caution.**\n\n{context}\n\n**Tip**: Start slowly and monitor how your skin reacts."
            elif compat.get('synergies'):
                answer = f"✨ **Great news - these ingredients work well together!**\n\n{context}"
            else:
                answer = f"✅ **These ingredients are generally safe to use together.**\n\n{context}"
        else:
            # Single ingredient or concern question
            answer = f"Here's what I know:\n\n{context}"
        
        return QueryResult(
            query_type=self._classify_query(question),
            answer=answer,
            confidence=0.8 if ingredients else 0.6,
            sources=[f"Knowledge base: {ing}" for ing in ingredients],
            follow_up_questions=self._get_follow_ups(question, ingredients)
        )
    
    def _classify_query(self, question: str) -> QueryType:
        """Classify the type of question."""
        q = question.lower()
        
        if any(phrase in q for phrase in ["can i use", "can i mix", "together", "combine", "with"]):
            return QueryType.COMPATIBILITY
        elif any(phrase in q for phrase in ["what is", "tell me about", "how does", "what does"]):
            return QueryType.INGREDIENT_INFO
        elif any(phrase in q for phrase in ["what order", "routine", "layer", "sequence", "first"]):
            return QueryType.ROUTINE_HELP
        elif any(phrase in q for phrase in ["for acne", "for aging", "for dry", "recommend", "should i use for", "help with"]):
            return QueryType.CONCERN_ADVICE
        return QueryType.GENERAL
    
    def _get_follow_ups(self, question: str, ingredients: list[str]) -> list[str]:
        """Generate contextual follow-up questions."""
        follow_ups = []
        
        if ingredients:
            for ing_id in ingredients[:2]:
                ing = self.kg.get_ingredient(ing_id)
                if ing:
                    follow_ups.append(f"When is the best time to use {ing.name}?")
            
            if len(ingredients) == 1:
                ing = self.kg.get_ingredient(ingredients[0])
                if ing:
                    follow_ups.append(f"What ingredients pair well with {ing.name}?")
        
        # Add general follow-ups if we don't have enough
        general = [
            "What's a good routine for beginners?",
            "How do I layer my products correctly?",
            "What ingredients should I avoid mixing?"
        ]
        
        while len(follow_ups) < 3:
            for g in general:
                if g not in follow_ups:
                    follow_ups.append(g)
                    break
            else:
                break
        
        return follow_ups[:3]