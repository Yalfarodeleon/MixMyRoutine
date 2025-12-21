"""
Skincare Advisor UI

Design Aesthetic: Clean, bright, medical/clinical feel
Inspired by: Glossier, The Ordinary, CeraVe, Paula's Choice

HCI Principles:
- Progressive Disclosure: Summary first, details on demand
- Error Prevention: Warn before conflicts
- Clear Feedback: Color-coded status indicators
- Recognition over Recall: Searchable dropdowns
- User Control: Customizable profile
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
    page_icon="🧴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============== CUSTOM CSS - BRIGHT MEDICAL THEME ==============
st.markdown("""
<style>
    /* Import clean font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles - Light theme */
    .stApp {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafb 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Headers */
    h1 {
        color: #1a1a2e !important;
        font-weight: 600 !important;
        letter-spacing: -0.5px;
    }
    
    h2, h3 {
        color: #2d3748 !important;
        font-weight: 500 !important;
    }
    
    /* Sidebar styling - Light */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #fefefe 0%, #f7f8fa 100%);
        border-right: 1px solid #e8edf2;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #4a5568;
    }
    
    /* Status badges */
    .status-safe {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        color: #065f46;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-weight: 500;
        font-size: 0.9rem;
        display: inline-block;
        border: 1px solid #6ee7b7;
    }
    
    .status-caution {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        color: #92400e;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-weight: 500;
        font-size: 0.9rem;
        display: inline-block;
        border: 1px solid #fcd34d;
    }
    
    .status-conflict {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        color: #991b1b;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-weight: 500;
        font-size: 0.9rem;
        display: inline-block;
        border: 1px solid #fca5a5;
    }
    
    .status-synergy {
        background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%);
        color: #5b21b6;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-weight: 500;
        font-size: 0.9rem;
        display: inline-block;
        border: 1px solid #c4b5fd;
    }
    
    /* Info boxes */
    .info-box {
        background: #f0f9ff;
        border-left: 4px solid #0ea5e9;
        padding: 1rem 1.25rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        color: #0c4a6e;
    }
    
    .warning-box {
        background: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 1rem 1.25rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        color: #78350f;
    }
    
    .success-box {
        background: #f0fdf4;
        border-left: 4px solid #22c55e;
        padding: 1rem 1.25rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        color: #14532d;
    }
    
    .error-box {
        background: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 1rem 1.25rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        color: #7f1d1d;
    }
    
    /* Primary buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Secondary buttons */
    .stButton > button[kind="secondary"] {
        background: white;
        color: #4a5568;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #f7fafc;
        border-color: #cbd5e0;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        background: white;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: #f8fafc;
        border-radius: 8px;
        font-weight: 500;
        color: #2d3748;
    }
    
    /* Dividers */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        margin: 1.5rem 0;
    }
    
    /* Chat messages */
    [data-testid="stChatMessage"] {
        background: white;
        border-radius: 12px;
        border: 1px solid #f0f0f0;
    }
    
    /* Logo/Title styling */
    .app-title {
        font-size: 1.75rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .app-subtitle {
        color: #6b7280;
        font-size: 0.9rem;
        margin-top: -0.5rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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
        # Logo/Title
        st.markdown('<p class="app-title">🧴 Skincare Advisor</p>', unsafe_allow_html=True)
        st.markdown('<p class="app-subtitle">Smart ingredient analysis</p>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        st.markdown("#### Navigation")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 Checker", use_container_width=True, 
                        type="primary" if st.session_state.view == "checker" else "secondary"):
                st.session_state.view = "checker"
                st.rerun()
        with col2:
            if st.button("📋 Routine", use_container_width=True,
                        type="primary" if st.session_state.view == "routine" else "secondary"):
                st.session_state.view = "routine"
                st.rerun()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💬 Advisor", use_container_width=True,
                        type="primary" if st.session_state.view == "advisor" else "secondary"):
                st.session_state.view = "advisor"
                st.rerun()
        with col2:
            if st.button("📚 Library", use_container_width=True,
                        type="primary" if st.session_state.view == "library" else "secondary"):
                st.session_state.view = "library"
                st.rerun()
        
        st.markdown("---")
        
        # Skin Profile
        st.markdown("#### Your Skin Profile")
        
        skin_type = st.selectbox(
            "Skin Type",
            options=[t.value for t in SkinType],
            index=4,
            format_func=lambda x: x.title()
        )
        
        concerns = st.multiselect(
            "Concerns",
            options=[c.value for c in SkinConcern],
            format_func=lambda x: x.replace('_', ' ').title(),
            placeholder="Select your concerns..."
        )
        
        # Update profile
        st.session_state.profile = SkinProfile(
            skin_type=SkinType(skin_type),
            concerns=[SkinConcern(c) for c in concerns]
        )
        
        if concerns:
            st.markdown(f"""
            <div style="background: #f0fdf4; padding: 0.75rem; border-radius: 8px; margin-top: 0.5rem;">
                <span style="color: #166534; font-size: 0.85rem;">
                    ✓ {skin_type.title()} skin • {len(concerns)} concern(s)
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #9ca3af; font-size: 0.75rem;">
            Built with KBAI + HCI principles<br>
            26 ingredients • 41 interactions
        </div>
        """, unsafe_allow_html=True)


def render_ingredient_checker():
    """Main ingredient compatibility checker view."""
    st.markdown("## 🔍 Ingredient Compatibility Checker")
    st.markdown("Check if your skincare ingredients can be safely used together")
    
    st.markdown("---")
    
    kg = st.session_state.knowledge_graph
    ingredient_options = sorted([ing.name for ing in kg.ingredients.values()])
    
    # Two column layout
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("#### Select Ingredients")
        selected_ingredients = st.multiselect(
            "Choose ingredients",
            options=ingredient_options,
            max_selections=10,
            help="Select 2 or more ingredients to check compatibility",
            label_visibility="collapsed",
            placeholder="Search ingredients..."
        )
    
    with col2:
        st.markdown("#### Or Paste Ingredient List")
        pasted_text = st.text_area(
            "Paste ingredients",
            height=120,
            placeholder="Retinol\nNiacinamide\nHyaluronic Acid",
            label_visibility="collapsed"
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
                st.markdown(f"""
                <div class="success-box">
                    ✓ Recognized: {', '.join(matched)}
                </div>
                """, unsafe_allow_html=True)
            if unmatched:
                st.markdown(f"""
                <div class="warning-box">
                    ? Not found: {', '.join(unmatched)}
                </div>
                """, unsafe_allow_html=True)
            
            selected_ingredients = list(set(selected_ingredients + matched))
    
    # Show selected count
    if selected_ingredients:
        st.markdown(f"**{len(selected_ingredients)} ingredients selected:** {', '.join(selected_ingredients)}")
    
    if len(selected_ingredients) < 2:
        st.markdown("""
        <div class="info-box">
            👆 Select at least 2 ingredients to check their compatibility
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Check compatibility
    st.markdown("---")
    st.markdown("### 📊 Analysis Results")
    
    ingredient_ids = []
    for name in selected_ingredients:
        ing = kg.get_ingredient(name)
        if ing:
            ingredient_ids.append(ing.id)
    
    compatibility = kg.check_compatibility(ingredient_ids)
    
    # Overall status banner
    if compatibility['is_compatible']:
        if compatibility['synergies']:
            st.markdown("""
            <div class="success-box" style="text-align: center; padding: 1.5rem;">
                <span style="font-size: 1.5rem;">✨</span><br>
                <strong style="font-size: 1.1rem;">Great combination!</strong><br>
                These ingredients are compatible and some work synergistically together.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="success-box" style="text-align: center; padding: 1.5rem;">
                <span style="font-size: 1.5rem;">✓</span><br>
                <strong style="font-size: 1.1rem;">All clear!</strong><br>
                These ingredients can be safely used together.
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="error-box" style="text-align: center; padding: 1.5rem;">
            <span style="font-size: 1.5rem;">⚠️</span><br>
            <strong style="font-size: 1.1rem;">Conflicts detected</strong><br>
            Some ingredients should NOT be used together. See details below.
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed results in columns
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        # Conflicts
        if compatibility['conflicts']:
            st.markdown("#### ❌ Conflicts")
            for conflict in compatibility['conflicts']:
                with st.expander(f"🚫 {conflict['ingredient_a']} + {conflict['ingredient_b']}", expanded=True):
                    st.markdown(f"**Why:** {conflict['explanation']}")
                    st.markdown(f"**What to do:** {conflict['recommendation']}")
        
        # Cautions
        if compatibility['cautions']:
            st.markdown("#### ⚠️ Use with Caution")
            for caution in compatibility['cautions']:
                with st.expander(f"⚡ {caution['ingredient_a']} + {caution['ingredient_b']}"):
                    st.markdown(f"**Why:** {caution['explanation']}")
                    st.markdown(f"**Tip:** {caution['recommendation']}")
    
    with col2:
        # Synergies
        if compatibility['synergies']:
            st.markdown("#### ✨ Great Combinations")
            for synergy in compatibility['synergies']:
                with st.expander(f"💜 {synergy['ingredient_a']} + {synergy['ingredient_b']}", expanded=True):
                    st.markdown(f"**Why:** {synergy['explanation']}")
                    if synergy.get('recommendation'):
                        st.markdown(f"**Tip:** {synergy['recommendation']}")
        
        # Wait times
        if compatibility['wait_times']:
            st.markdown("#### ⏱️ Timing Required")
            for wait in compatibility['wait_times']:
                st.markdown(f"""
                <div class="info-box">
                    Wait <strong>{wait.get('wait_minutes', 20)} minutes</strong> between 
                    {wait['ingredient_a']} and {wait['ingredient_b']}
                </div>
                """, unsafe_allow_html=True)


def render_routine_builder():
    """Routine builder view."""
    st.markdown("## 📋 Routine Builder")
    st.markdown("Build your skincare routine with automatic compatibility checking")
    
    st.markdown("---")
    
    kg = st.session_state.knowledge_graph
    builder = st.session_state.routine_builder
    
    # Time selection
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        routine_time = st.radio(
            "Build routine for:",
            ["☀️ Morning (AM)", "🌙 Evening (PM)"],
            horizontal=True,
            label_visibility="collapsed"
        )
    time = RoutineTime.AM if "Morning" in routine_time else RoutineTime.PM
    
    st.markdown("---")
    
    # Product entry
    st.markdown("#### Add Products")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        product_name = st.text_input(
            "Product name",
            placeholder="e.g., CeraVe PM Moisturizer",
            label_visibility="collapsed"
        )
    
    with col2:
        ingredient_options = sorted([ing.name for ing in kg.ingredients.values()])
        product_ingredients = st.multiselect(
            "Key ingredients",
            options=ingredient_options,
            key="product_ing_select",
            placeholder="Select key ingredients...",
            label_visibility="collapsed"
        )
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add", type="primary", use_container_width=True):
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
        st.markdown("---")
        st.markdown("#### Your Products")
        
        for i, product in enumerate(st.session_state.routine_products):
            col1, col2, col3 = st.columns([3, 3, 1])
            with col1:
                st.markdown(f"**{product['name']}**")
            with col2:
                st.markdown(f"<span style='color: #6b7280; font-size: 0.9rem;'>{', '.join(product['ingredient_names'])}</span>", unsafe_allow_html=True)
            with col3:
                if st.button("🗑️", key=f"remove_{i}", help="Remove product"):
                    st.session_state.routine_products.pop(i)
                    st.rerun()
        
        st.markdown("---")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔍 Analyze Routine", type="primary", use_container_width=True):
                routine, analysis = builder.build_routine(
                    st.session_state.routine_products,
                    time,
                    st.session_state.profile
                )
                
                st.markdown("### 📊 Routine Analysis")
                
                if analysis.is_valid:
                    st.markdown("""
                    <div class="success-box">
                        ✓ <strong>Your routine looks good!</strong> No conflicts detected.
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="error-box">
                        ⚠️ <strong>Issues found</strong> — see details below
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("#### Recommended Order")
                for step in routine.steps:
                    wait_note = f" ⏱️ *wait {step.wait_after} min*" if step.wait_after > 0 else ""
                    note = f" ⚠️ *{step.notes}*" if step.notes else ""
                    st.markdown(f"**{step.order}.** {step.product_name}{wait_note}{note}")
                
                if analysis.conflicts:
                    st.markdown("#### ❌ Conflicts Found")
                    for conflict in analysis.conflicts:
                        st.markdown(f"""
                        <div class="error-box">
                            <strong>{conflict['ingredient_a']} + {conflict['ingredient_b']}</strong><br>
                            {conflict['explanation']}
                        </div>
                        """, unsafe_allow_html=True)
                
                if analysis.missing_essentials:
                    st.markdown("#### 📌 Missing Essentials")
                    for missing in analysis.missing_essentials:
                        st.markdown(f"""
                        <div class="warning-box">{missing}</div>
                        """, unsafe_allow_html=True)
                
                if analysis.suggestions:
                    st.markdown("#### 💡 Suggestions")
                    for suggestion in analysis.suggestions:
                        st.markdown(f"• {suggestion}")
        
        with col2:
            if st.button("🗑️ Clear All", use_container_width=True):
                st.session_state.routine_products = []
                st.rerun()
    else:
        st.markdown("""
        <div class="info-box">
            👆 Add products to your routine to get started
        </div>
        """, unsafe_allow_html=True)


def render_advisor_chat():
    """AI Advisor chat interface."""
    st.markdown("## 💬 Skincare Advisor")
    st.markdown("Ask me anything about ingredients, routines, and skincare")
    
    st.markdown("---")
    
    advisor = st.session_state.advisor
    
    # Example questions
    with st.expander("💡 Example questions", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **Compatibility**
            - Can I use retinol with vitamin C?
            - Is niacinamide safe with AHA?
            - Can I mix benzoyl peroxide and salicylic acid?
            """)
        with col2:
            st.markdown("""
            **Recommendations**
            - What should I use for acne?
            - What order should I apply products?
            - What's good for hyperpigmentation?
            """)
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.chat_message("user", avatar="👤").write(msg["content"])
            else:
                st.chat_message("assistant", avatar="🧴").markdown(msg["content"])
    
    # Input
    if prompt := st.chat_input("Ask about skincare..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with chat_container:
            st.chat_message("user", avatar="👤").write(prompt)
        
        result = advisor.ask(prompt, st.session_state.profile)
        
        response = result.answer
        
        if result.confidence < 0.5:
            response += "\n\n---\n*I'm not fully confident about this answer. Consider consulting a dermatologist.*"
        
        if result.follow_up_questions:
            response += "\n\n**Related questions:**"
            for q in result.follow_up_questions[:3]:
                response += f"\n• {q}"
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        with chat_container:
            st.chat_message("assistant", avatar="🧴").markdown(response)
    
    # Clear button
    if st.session_state.chat_history:
        st.markdown("---")
        if st.button("🗑️ Clear conversation"):
            st.session_state.chat_history = []
            st.rerun()


def render_ingredient_library():
    """Browse all ingredients in the knowledge base."""
    st.markdown("## 📚 Ingredient Library")
    st.markdown("Browse and learn about skincare ingredients")
    
    st.markdown("---")
    
    kg = st.session_state.knowledge_graph
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories = ["All"] + sorted(set(ing.category.value for ing in kg.ingredients.values()))
        category_filter = st.selectbox(
            "Category",
            options=categories,
            format_func=lambda x: x.replace('_', ' ').title()
        )
    
    with col2:
        concern_options = ["All"] + [c.value for c in SkinConcern]
        concern_filter = st.selectbox(
            "Concern",
            options=concern_options,
            format_func=lambda x: x.replace('_', ' ').title()
        )
    
    with col3:
        search = st.text_input("🔍 Search", placeholder="Type to search...")
    
    st.markdown("---")
    
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
        
        # Ingredient card
        with st.expander(f"**{ingredient.name}** — {ingredient.category.value.replace('_', ' ').title()}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"*{ingredient.description}*")
                
                if ingredient.how_it_works:
                    st.markdown(f"**How it works:** {ingredient.how_it_works}")
                
                if ingredient.usage_tips:
                    st.markdown("**Tips:**")
                    for tip in ingredient.usage_tips:
                        st.markdown(f"- {tip}")
            
            with col2:
                # Tags
                concerns = [c.value.replace('_', ' ').title() for c in ingredient.addresses_concerns]
                if concerns:
                    st.markdown(f"✨ **Good for:** {', '.join(concerns)}")
                
                if ingredient.caution_skin_types:
                    cautions = [s.value.title() for s in ingredient.caution_skin_types]
                    st.markdown(f"⚠️ **Caution:** {', '.join(cautions)} skin")
                
                time_display = {
                    "morning_only": "☀️ AM only",
                    "evening_only": "🌙 PM only",
                    "either": "☀️🌙 AM or PM",
                    "both": "☀️🌙 Both AM & PM"
                }
                st.markdown(f"⏰ {time_display.get(ingredient.time_of_day.value, 'Any time')}")
                
                if ingredient.beginner_friendly:
                    st.markdown("👍 Beginner friendly")
                else:
                    st.markdown("💪 Advanced users")
    
    if displayed == 0:
        st.markdown("""
        <div class="info-box">
            No ingredients match your filters. Try adjusting your search.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"*Showing {displayed} ingredient(s)*")


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