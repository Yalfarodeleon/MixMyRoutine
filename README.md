# Skincare Advisor

An intelligent skincare routine analyzer that checks ingredient compatibility, identifies potential conflicts, and helps build effective routines.

## What Makes This Different

Unlike simple ingredient checkers, this system:

- **Understands ingredient interactions** using a knowledge graph of chemical relationships
- **Explains its reasoning** — you see *why* ingredients conflict or synergize
- **Builds complete routines** respecting application order and timing
- **Adapts to your skin** using case-based reasoning from skin profiles
- **Answers questions naturally** through an AI-powered advisor agent

Built with principles from Knowledge-Based AI (semantic networks, constraint satisfaction, case-based reasoning) and Human-Computer Interaction (progressive disclosure, error prevention, clear feedback).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                          │
│                   (Streamlit Frontend)                       │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │   Product    │ │   Routine    │ │      Advisor         │ │
│  │   Checker    │ │   Builder    │ │       Chat           │ │
│  └──────────────┘ └──────────────┘ └──────────────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Reasoning Engine                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │  Conflict    │ │   Routine    │ │    Advisor           │ │
│  │  Detector    │ │   Sequencer  │ │    Agent             │ │
│  └──────────────┘ └──────────────┘ └──────────────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Knowledge Base                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │  Ingredient  │ │ Interaction  │ │     Skin Profile     │ │
│  │    Graph     │ │    Rules     │ │       Cases          │ │
│  └──────────────┘ └──────────────┘ └──────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/skincare-advisor.git
cd skincare-advisor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run src/ui/app.py
```

## Project Structure

```
skincare-advisor/
├── src/
│   ├── knowledge/      # Ingredient data & interaction rules
│   ├── routines/       # Routine building & analysis
│   ├── agent/          # AI-powered advisor
│   └── ui/             # Streamlit interface
├── tests/              # Unit and integration tests
├── data/               # Ingredient databases, skin profiles
└── docs/               # Design decisions & documentation
```

## Key Concepts Demonstrated

### From Knowledge-Based AI
- **Semantic Networks**: Ingredients connected by interaction relationships
- **Frames**: Ingredients represented with slots (pH, function, concerns)
- **Constraint Satisfaction**: Routine building respects hard rules
- **Case-Based Reasoning**: Recommend routines based on similar skin profiles
- **Diagnostic Reasoning**: Map skin concerns to ingredient recommendations

### From Human-Computer Interaction
- **Progressive Disclosure**: Show compatibility first, details on demand
- **Error Prevention**: Warn before adding conflicting products
- **Clear Feedback**: Visual indicators (✓ safe, ⚠ caution, ✗ conflict)
- **Recognition over Recall**: Searchable ingredient database
- **User Control**: Customize skin type, concerns, and preferences

## Tech Stack

- **Python 3.11+**
- **Streamlit** — Interactive UI
- **NetworkX** — Knowledge graph operations
- **Pydantic** — Data validation
- **OpenAI/Anthropic API** — Natural language advisor
- **pytest** — Testing

## License

MIT
