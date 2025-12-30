# 🧴 MixMyRoutine

An intelligent skincare routine builder that uses **Knowledge-Based AI** to analyze ingredient compatibility, detect conflicts, and provide personalized recommendations.

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

**MixMyRoutine** solves that problem by:
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
```

### 2. Semantic Networks
Ingredients and their interactions form a **graph** where:
- **Nodes** = Ingredients
- **Edges** = Interactions (conflicts, synergies, etc.)

### 3. Constraint Satisfaction
Routine building is a **CSP** where:
- **Variables** = Products to apply
- **Constraints** = No conflicts, correct order, proper timing

### 4. Case-Based Reasoning
Recommendations based on similar skin profiles.

### 5. Diagnostic Reasoning
Maps symptoms (skin concerns) → solutions (ingredients).

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (optional)

### Option 1: Docker (Recommended)
```bash
git clone https://github.com/YOUR_USERNAME/mixmyroutine.git
cd mixmyroutine
docker-compose up --build
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

---

## API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger documentation.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/ingredients` | List all ingredients |
| `GET` | `/api/v1/ingredients/{id}` | Get ingredient details |
| `POST` | `/api/v1/ingredients/check` | Check compatibility |
| `POST` | `/api/v1/routines/build` | Build optimized routine |
| `POST` | `/api/v1/advisor/ask` | Ask a question |

---

## Project Structure

```
mixmyroutine/
├── backend/                    # Python FastAPI
│   ├── app/
│   │   ├── api/v1/            # REST endpoints
│   │   ├── core/              # KBAI business logic
│   │   ├── schemas/           # Pydantic models
│   │   └── main.py
│   └── requirements.txt
│
├── frontend/                   # React TypeScript
│   ├── src/
│   │   ├── pages/             # Page components
│   │   ├── hooks/             # React Query hooks
│   │   ├── services/          # API client
│   │   └── App.tsx
│   └── package.json
│
├── docker-compose.yml
└── README.md
```

---

## Knowledge Base Stats

| Metric | Count |
|--------|-------|
| Ingredients | 26 |
| Interaction Rules | 41 |
| Skin Concerns | 11 |
| Skin Types | 5 |

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- Georgia Tech CS 7637 Knowledge-Based AI course
- Skincare science: [LabMuffin](https://labmuffin.com/), [Paula's Choice](https://www.paulaschoice.com/ingredient-dictionary)

---

<p align="center">
  <strong>MixMyRoutine</strong> — Mix smarter, glow better ✨
</p>
