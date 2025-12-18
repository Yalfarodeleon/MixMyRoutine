"""
Skincare Advisor UI

HCI Principles Applied:
- Progressive Disclosure: Show summary first, details on demand
- Error Prevention: Warn before conflicts, suggest alternatives
- Clear Feedback: Color-coded indicators, immediate responses
- Recognition over Recall: Search/select ingredients, don't require typing
- User Control: Let users customize profile, override suggestions
- Consistency: Same patterns throughout the interface
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from knowledge.ingredients import (
    IngredientKnowledgeGraph,
    create_skincare_knowledge_base,
    SkinProfile,
    SkinType,
    SkinConcern,
    InteractionType
)
from routines.builder import RoutineBuilder, RoutineAnalyzer, RoutineTime
from agent.advisor import SkincareAdvisor


# Page config
st.set_page_config(
    page_title="Skincare Advisor",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .status-safe { color: #10b981; }
    .status-caution { color: #f59e0b; }
    .status-conflict { color: #ef4444; }
    .status-synergy { color: #8b5cf6; }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if "knowledge_graph" not in st.session_state:
        st.session_state.knowledge_graph = create_skincare_knowledge_base()
    
    if "advisor" not in st.session_state:
        st.session_state.advisor = SkincareAdvisor(st.session_state.knowledge_graph)
    
    if "routine_builder" not in st.session_state:
        st.session_state.routine_builder = RoutineBuilder(st.session_state.knowledge_graph)
    
    if "analyzer" not in st.session_state:
        st.session_state.analyzer = RoutineAnalyzer(st.session_state.knowledge_graph)
    
    if "profile" not in st.session_state:
        st.session_state.profile = None
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "view" not in st.session_state:
        st.session_state.view = "checker"
    
    if "routine_products" not in st.session_state:
        st.session_state.routine_products = []


def render_sidebar():
    """Render sidebar with navigation and profile."""
    with st.sidebar:
        st.title("✨ Skincare Advisor")
        st.caption("Check ingredients, build routines, get advice")
        
        st.divider()
        
        # Navigation
        st.subheader("📍 Navigation")
        
        if st.button("🔍 Ingredient Checker", use_container_width=True):
            st.session_state.view = "checker"
        if st.button("📋 Routine Builder", use_container_width=True):
            st.session_state.view = "routine"
        if st.button("💬 Ask Advisor", use_container_width=True):
            st.session_state.view = "advisor"
        if st.button("📚 Ingredient Library", use_container_width=True):
            st.session_state.view = "library"
        
        st.divider()
        
        # Skin Profile (HCI: User control and personalization)
        st.subheader("👤 Your Skin Profile")
        
        skin_type = st.selectbox(
            "Skin Type",
            options=[t.value for t in SkinType],
            index=4,
            format_func=lambda x: x.title()
        )
        
        concerns = st.multiselect(
            "Concerns",
            options=[c.value for c in SkinConcern],
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        # Update profile
        st.session_state.profile = SkinProfile(
            skin_type=SkinType(skin_type),
            concerns=[SkinConcern(c) for c in concerns]
        )
        
        if concerns:
            st.caption(f"Profile: {skin_type.title()} skin with {len(concerns)} concern(s)")


def render_ingredient_checker():
    """Main ingredient compatibility checker view.
    
    HCI: Recognition over recall - users select from list
    HCI: Progressive disclosure - summary first, details in expanders
    """
    st.header("🔍 Ingredient Compatibility Checker")
    st.write("Check if ingredients can be safely used together")
    
    kg = st.session_state.knowledge_graph
    ingredient_options = sorted([ing.name for ing in kg.ingredients.values()])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Select Ingredients")
        selected_ingredients = st.multiselect(
            "Choose ingredients to check",
            options=ingredient_options,
            max_selections=10,
            help="Select 2 or more ingredients to check compatibility"
        )
    
    with col2:
        st.subheader("Or Paste Ingredient List")
        pasted_text = st.text_area(
            "Paste ingredients (one per line or comma-separated)",
            height=150,
            placeholder="Retinol\nNiacinamide\nHyaluronic Acid"
        )
        
        if pasted_text:
            if ',' in pasted_text:
                parsed = [i.strip() for i in pasted_text.split(',')]
            else:
                parsed = [i.strip() for i in pasted_text.split('\n')]
            
            matched, unmatched = [], []
            for item in parsed:
                if not item:
                    continue
                ing = kg.get_ingredient(item)
                if ing:
                    matched.append(ing.name)
                else:
                    found = kg.find_ingredient(item)
                    if found:
                        matched.append(found[0].name)
                    else:
                        unmatched.append(item)
            
            if matched:
                st.success(f"Recognized: {', '.join(matched)}")
            if unmatched:
                st.warning(f"Not recognized: {', '.join(unmatched)}")
            
            selected_ingredients = list(set(selected_ingredients + matched))
    
    if len(selected_ingredients) < 2:
        st.info("Select at least 2 ingredients to check compatibility")
        return
    
    # Check compatibility
    st.divider()
    st.subheader("📊 Compatibility Results")
    
    ingredient_ids = []
    for name in selected_ingredients:
        ing = kg.get_ingredient(name)
        if ing:
            ingredient_ids.append(ing.id)
    
    compatibility = kg.check_compatibility(ingredient_ids)
    
    # Overall status (HCI: Clear immediate feedback)
    if compatibility['is_compatible']:
        if compatibility['synergies']:
            st.success("✨ Great news! These ingredients are compatible and some work synergistically!")
        else:
            st.success("✅ These ingredients are compatible and can be used together!")
    else:
        st.error("⚠️ Warning: Some of these ingredients should NOT be used together!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if compatibility['conflicts']:
            st.markdown("### ❌ Conflicts")
            for conflict in compatibility['conflicts']:
                with st.expander(f"🚫 {conflict['ingredient_a']} + {conflict['ingredient_b']}", expanded=True):
                    st.write(f"**Why:** {conflict['explanation']}")
                    st.write(f"**Recommendation:** {conflict['recommendation']}")
        
        if compatibility['cautions']:
            st.markdown("### ⚠️ Use with Caution")
            for caution in compatibility['cautions']:
                with st.expander(f"⚡ {caution['ingredient_a']} + {caution['ingredient_b']}"):
                    st.write(f"**Why:** {caution['explanation']}")
                    st.write(f"**Recommendation:** {caution['recommendation']}")
    
    with col2:
        if compatibility['synergies']:
            st.markdown("### ✨ Great Combinations")
            for synergy in compatibility['synergies']:
                with st.expander(f"💜 {synergy['ingredient_a']} + {synergy['ingredient_b']}", expanded=True):
                    st.write(f"**Why:** {synergy['explanation']}")
                    if synergy.get('recommendation'):
                        st.write(f"**Tip:** {synergy['recommendation']}")
        
        if compatibility['wait_times']:
            st.markdown("### ⏱️ Timing Needed")
            for wait in compatibility['wait_times']:
                st.info(f"Wait {wait.get('wait_minutes', 20)} min between {wait['ingredient_a']} and {wait['ingredient_b']}")


def render_routine_builder():
    """Routine builder view.
    
    HCI: Error prevention - check conflicts before finalizing
    KBAI: Constraint satisfaction - respect all rules when building
    """
    st.header("📋 Routine Builder")
    st.write("Build your AM or PM routine with automatic compatibility checking")
    
    kg = st.session_state.knowledge_graph
    builder = st.session_state.routine_builder
    
    routine_time = st.radio(
        "Build routine for:",
        ["Morning (AM)", "Evening (PM)"],
        horizontal=True
    )
    time = RoutineTime.AM if "Morning" in routine_time else RoutineTime.PM
    
    st.divider()
    st.subheader("Add Products to Your Routine")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        product_name = st.text_input("Product name", placeholder="e.g., CeraVe Moisturizer")
    
    with col2:
        ingredient_options = sorted([ing.name for ing in kg.ingredients.values()])
        product_ingredients = st.multiselect(
            "Key ingredients",
            options=ingredient_options,
            key="product_ing_select"
        )
    
    if st.button("Add Product", type="primary"):
        if product_name and product_ingredients:
            ing_ids = []
            for name in product_ingredients:
                ing = kg.get_ingredient(name)
                if ing:
                    ing_ids.append(ing.id)
            
            st.session_state.routine_products.append({
                "name": product_name,
                "ingredients": ing_ids,
                "ingredient_names": product_ingredients
            })
            st.rerun()
        else:
            st.warning("Please enter a product name and select at least one ingredient")
    
    # Display current products
    if st.session_state.routine_products:
        st.divider()
        st.subheader("Your Products")
        
        for i, product in enumerate(st.session_state.routine_products):
            col1, col2, col3 = st.columns([3, 2, 1])
            col1.write(f"**{product['name']}**")
            col2.write(", ".join(product['ingredient_names']))
            if col3.button("Remove", key=f"remove_{i}"):
                st.session_state.routine_products.pop(i)
                st.rerun()
        
        st.divider()
        if st.button("🔍 Analyze Routine", type="primary"):
            routine, analysis = builder.build_routine(
                st.session_state.routine_products,
                time,
                st.session_state.profile
            )
            
            st.subheader("📊 Routine Analysis")
            
            if analysis.is_valid:
                st.success("✅ Your routine looks good!")
            else:
                st.error("⚠️ Issues found in your routine")
            
            st.markdown("### Recommended Order")
            for step in routine.steps:
                wait_note = f" ⏱️ (wait {step.wait_after} min)" if step.wait_after > 0 else ""
                note = f" ⚠️ {step.notes}" if step.notes else ""
                st.write(f"{step.order}. **{step.product_name}**{wait_note}{note}")
            
            if analysis.conflicts:
                st.markdown("### ❌ Conflicts Found")
                for conflict in analysis.conflicts:
                    st.error(f"**{conflict['ingredient_a']}** + **{conflict['ingredient_b']}**: {conflict['explanation']}")
            
            if analysis.missing_essentials:
                st.markdown("### 📌 Missing Essentials")
                for missing in analysis.missing_essentials:
                    st.info(missing)
            
            if analysis.suggestions:
                st.markdown("### 💡 Suggestions")
                for suggestion in analysis.suggestions:
                    st.write(f"• {suggestion}")
        
        if st.button("Clear All Products"):
            st.session_state.routine_products = []
            st.rerun()
    else:
        st.info("Add products to your routine to get started")


def render_advisor_chat():
    """AI Advisor chat interface.
    
    KBAI: Natural language understanding and knowledge retrieval
    HCI: Conversational interface, suggested follow-ups
    """
    st.header("💬 Skincare Advisor")
    st.write("Ask me anything about skincare ingredients and routines!")
    
    advisor = st.session_state.advisor
    
    with st.expander("💡 Example questions you can ask"):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Compatibility:**")
            st.write("• Can I use retinol with vitamin C?")
            st.write("• Is niacinamide safe with AHA?")
        with col2:
            st.write("**Advice:**")
            st.write("• What should I use for acne?")
            st.write("• What order should I apply products?")
    
    # Chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").markdown(msg["content"])
    
    # Input
    if prompt := st.chat_input("Ask about skincare..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        result = advisor.ask(prompt, st.session_state.profile)
        
        response = result.answer
        
        if result.confidence < 0.5:
            response += "\n\n*I'm not very confident about this answer. Consider consulting a dermatologist.*"
        
        if result.follow_up_questions:
            response += "\n\n**You might also want to know:**"
            for q in result.follow_up_questions[:3]:
                response += f"\n• {q}"
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.chat_message("assistant").markdown(response)
    
    if st.session_state.chat_history:
        if st.button("Clear conversation"):
            st.session_state.chat_history = []
            st.rerun()


def render_ingredient_library():
    """Browse all ingredients in the knowledge base.
    
    HCI: Recognition over recall - filterable, searchable
    """
    st.header("📚 Ingredient Library")
    st.write("Browse and learn about skincare ingredients")
    
    kg = st.session_state.knowledge_graph
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories = ["All"] + sorted(set(ing.category.value for ing in kg.ingredients.values()))
        category_filter = st.selectbox(
            "Filter by category",
            options=categories,
            format_func=lambda x: x.replace('_', ' ').title()
        )
    
    with col2:
        concern_options = ["All"] + [c.value for c in SkinConcern]
        concern_filter = st.selectbox(
            "Filter by concern",
            options=concern_options,
            format_func=lambda x: x.replace('_', ' ').title()
        )
    
    with col3:
        search = st.text_input("🔍 Search", placeholder="Type to search...")
    
    st.divider()
    
    # Display ingredients
    displayed = 0
    for ing_id, ingredient in sorted(kg.ingredients.items(), key=lambda x: x[1].name):
        # Apply filters
        if category_filter != "All" and ingredient.category.value != category_filter:
            continue
        
        if concern_filter != "All":
            concern = SkinConcern(concern_filter)
            if concern not in ingredient.addresses_concerns:
                continue
        
        if search and search.lower() not in ingredient.name.lower():
            if not any(search.lower() in alias.lower() for alias in ingredient.aliases):
                continue
        
        displayed += 1
        
        # Display ingredient card
        with st.expander(f"**{ingredient.name}** - {ingredient.category.value.replace('_', ' ').title()}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(ingredient.description)
                
                if ingredient.how_it_works:
                    st.write(f"**How it works:** {ingredient.how_it_works}")
                
                if ingredient.usage_tips:
                    st.write("**Usage tips:**")
                    for tip in ingredient.usage_tips:
                        st.write(f"• {tip}")
            
            with col2:
                st.write("**Quick Facts:**")
                
                concerns = [c.value.replace('_', ' ').title() for c in ingredient.addresses_concerns]
                if concerns:
                    st.write(f"✨ Good for: {', '.join(concerns)}")
                
                if ingredient.caution_skin_types:
                    cautions = [s.value.title() for s in ingredient.caution_skin_types]
                    st.write(f"⚠️ Caution for: {', '.join(cautions)} skin")
                
                time_display = {
                    "morning_only": "☀️ AM only",
                    "evening_only": "🌙 PM only",
                    "either": "☀️🌙 AM or PM",
                    "both": "☀️🌙 Use both"
                }
                st.write(f"⏰ {time_display.get(ingredient.time_of_day.value, 'Any time')}")
                
                if ingredient.beginner_friendly:
                    st.write("👍 Beginner friendly")
                else:
                    st.write("💪 For experienced users")
    
    if displayed == 0:
        st.info("No ingredients match your filters")


def main():
    """Main application entry point."""
    init_session_state()
    render_sidebar()
    
    view = st.session_state.view
    
    if view == "checker":
        render_ingredient_checker()
    elif view == "routine":
        render_routine_builder()
    elif view == "advisor":
        render_advisor_chat()
    elif view == "library":
        render_ingredient_library()
    else:
        render_ingredient_checker()


if __name__ == "__main__":
    main()
