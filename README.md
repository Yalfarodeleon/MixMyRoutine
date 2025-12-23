# 🧴 Skincare Ingredient Advisor

An intelligent skincare routine builder that uses principles of **Knowledge-Based AI** to analyze ingredient compatibility, detect conflicts, and provide personalized recommendations.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.100+-teal.svg)
![React](https://img.shields.io/badge/react-18+-61DAFB.svg)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [KBAI Concepts](#kbai-concepts)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Roadmap](#roadmap)
- [Contributing](#contributing)

---

## Overview

Many skincare enthusiasts struggle to know which ingredients can be safely combined. Mixing incompatible ingredients like **Retinol + AHAs** or **Benzoyl Peroxide + Vitamin C** can cause irritation, reduced effectiveness, or skin damage.

This application solves that problem by:
- ✅ Checking ingredient compatibility in real-time
- ✅ Explaining *why* certain combinations are problematic
- ✅ Building optimized routines with proper product ordering
- ✅ Providing personalized recommendations based on skin type and concerns

---

## Features

| Feature | Description |
|---------|-------------|
| **Ingredient Checker** | Select multiple ingredients and instantly see conflicts, cautions, and synergies |
| **Routine Builder** | Add products to AM/PM routines with automatic conflict detection and ordering |
| **AI Advisor** | Ask natural language questions like "Can I use retinol with vitamin C?" |
| **Ingredient Library** | Browse 26+ ingredients with detailed usage information |
| **Personalization** | Set your skin type and concerns for tailored recommendations |

---

## Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Python 3.11+** | Core language |
| **FastAPI** | REST API framework with automatic OpenAPI docs |
| **Pydantic** | Data validation and serialization |
| **NetworkX** | Graph data structure for ingredient relationships |
| **SQLAlchemy** | ORM for database operations |
| **SQLite** | Database (PostgreSQL for production) |
| **pytest** | Testing framework |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | UI library |
| **TypeScript** | Type-safe JavaScript |
| **Vite** | Build tool and dev server |
| **Tailwind CSS** | Utility-first styling |
| **React Query** | Server state management |
| **React Router** | Client-side routing |

### DevOps
| Technology | Purpose |
|------------|---------|
| **Docker** | Containerization |
| **docker-compose** | Multi-container orchestration |
| **GitHub Actions** | CI/CD pipeline |
| **Vercel / Railway** | Deployment (planned) |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                        │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (React + TypeScript)               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Checker   │  │   Routine   │  │   Advisor   │   ...        │
│  │    Page     │  │   Builder   │  │    Chat     │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                              │                                  │
│                    React Query (API Client)                     │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                           │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    API Layer (/api/v1/)                 │    │
│  │  • POST /ingredients/check                              │    │
│  │  • POST /routines/build                                 │    │
│  │  • POST /advisor/ask                                    │    │
│  │  • GET  /ingredients                                    │    │
│  └─────────────────────────────┬───────────────────────────┘    │
│                                │                                │
│  ┌─────────────────────────────▼───────────────────────────┐    │
│  │                    CORE (KBAI Logic)                    │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │    │
│  │  │  Knowledge   │  │   Routine    │  │   Advisor    │   │    │
│  │  │    Graph     │  │   Builder    │  │    Agent     │   │    │
│  │  │  (NetworkX)  │  │    (CSP)     │  │    (NLU)     │   │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │    │
│  └─────────────────────────────┬───────────────────────────┘    │
│                                │                                │
│  ┌─────────────────────────────▼───────────────────────────┐    │
│  │                    DATA Layer                           │    │
│  │           SQLite / PostgreSQL (SQLAlchemy)              │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## KBAI Concepts

This project demonstrates several Knowledge-Based AI principles:

### 1. Frame-Based Representation
Each ingredient is a **frame** with slots containing structured knowledge:
```python
@dataclass
class Ingredient:
    id: str
    name: str
    category: IngredientCategory
    optimal_ph: tuple[float, float]
    addresses_concerns: list[SkinConcern]
    # ... more slots
```

### 2. Semantic Networks
Ingredients and their interactions form a **graph** where:
- **Nodes** = Ingredients
- **Edges** = Interactions (conflicts, synergies, etc.)

```python
# Using NetworkX to represent relationships
self.graph.add_edge("retinol", "glycolic_acid", 
                    interaction_type=InteractionType.CONFLICTS)
```

### 3. Constraint Satisfaction
Routine building is a **CSP** where:
- **Variables** = Products to apply
- **Constraints** = No conflicts, correct order, proper timing

### 4. Case-Based Reasoning
Recommendations based on similar skin profiles:
- *"Users with oily, acne-prone skin often use salicylic acid + niacinamide"*

### 5. Diagnostic Reasoning
Maps symptoms (skin concerns) → solutions (ingredients):
- Acne → Salicylic Acid, Benzoyl Peroxide, Niacinamide
- Aging → Retinol, Vitamin C, Peptides

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (optional)

### Option 1: Docker (Recommended)
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/skincare-advisor.git
cd skincare-advisor

# Start all services
docker-compose up --build

# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Running Tests
```bash
# Backend tests
cd backend
pytest -v

# Frontend tests
cd frontend
npm test
```

---

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive Swagger documentation.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/ingredients` | List all ingredients |
| `GET` | `/api/v1/ingredients/{id}` | Get ingredient details |
| `POST` | `/api/v1/ingredients/check` | Check compatibility |
| `POST` | `/api/v1/routines/build` | Build optimized routine |
| `POST` | `/api/v1/advisor/ask` | Ask a question |

### Example Request
```bash
curl -X POST "http://localhost:8000/api/v1/ingredients/check" \
  -H "Content-Type: application/json" \
  -d '{"ingredients": ["retinol", "vitamin_c"]}'
```

### Example Response
```json
{
  "is_compatible": false,
  "conflicts": [],
  "cautions": [
    {
      "ingredient_a": "Retinol",
      "ingredient_b": "Vitamin C (L-Ascorbic Acid)",
      "severity": 6,
      "explanation": "pH incompatibility and increased irritation risk...",
      "recommendation": "Use vitamin C in AM and retinol in PM..."
    }
  ],
  "synergies": []
}
```

---

## Project Structure

```
skincare-advisor/
│
├── backend/                    # Python FastAPI
│   ├── app/
│   │   ├── api/                # REST endpoints
│   │   │   ├── v1/
│   │   │   │   ├── ingredients.py
│   │   │   │   ├── routines.py
│   │   │   │   └── advisor.py
│   │   │   └── deps.py         # Dependencies
│   │   ├── core/               # KBAI business logic
│   │   │   ├── knowledge/      # Knowledge graph
│   │   │   ├── routines/       # Routine builder
│   │   │   └── agent/          # NL advisor
│   │   ├── db/                 # Database models
│   │   ├── schemas/            # Pydantic models
│   │   └── main.py             # App entry point
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                   # React TypeScript
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Page components
│   │   ├── hooks/              # Custom React hooks
│   │   ├── services/           # API client
│   │   ├── types/              # TypeScript interfaces
│   │   └── App.tsx
│   ├── package.json
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── docs/                       # Documentation
├── .github/
│   └── workflows/              # CI/CD pipelines
│       └── ci.yml
│
├── docker-compose.yml
├── Makefile
└── README.md
```

---

## Roadmap

### Phase 1: Core Migration ✅
- [x] Knowledge graph with 26 ingredients
- [x] 41 interaction rules
- [x] Routine builder with constraint satisfaction
- [x] NL advisor agent

### Phase 2: API Layer (Current)
- [ ] FastAPI backend setup
- [ ] REST endpoints for all features
- [ ] Pydantic request/response schemas
- [ ] API tests with pytest

### Phase 3: Frontend
- [ ] React + TypeScript setup
- [ ] Ingredient checker page
- [ ] Routine builder page
- [ ] Advisor chat interface
- [ ] Responsive design with Tailwind

### Phase 4: Database
- [ ] SQLAlchemy models
- [ ] User accounts
- [ ] Saved routines
- [ ] Product database

### Phase 5: DevOps
- [ ] Docker containerization
- [ ] GitHub Actions CI/CD
- [ ] Production deployment
- [ ] Monitoring and logging

### Phase 6: Enhancements
- [ ] LLM integration for better NL responses
- [ ] Barcode scanning for products
- [ ] Community-submitted products
- [ ] Mobile app (React Native)

---

## Knowledge Base Stats

| Metric | Count |
|--------|-------|
| Ingredients | 26 |
| Interaction Rules | 41 |
| Skin Concerns | 11 |
| Skin Types | 5 |

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Georgia Tech CS 7637 Knowledge-Based AI course
- Skincare science resources: [LabMuffin](https://labmuffin.com/), [Paula's Choice](https://www.paulaschoice.com/ingredient-dictionary)
- UI inspiration: Glossier, The Ordinary, CeraVe

---
