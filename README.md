# 🧴 MixMyRoutine

An intelligent skincare routine builder that uses **Knowledge-Based AI** to analyze ingredient compatibility, detect conflicts, and provide personalized recommendations.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.100+-teal.svg)
![React](https://img.shields.io/badge/react-18+-61DAFB.svg)
![CI](https://github.com/Yalfarodeleon/mixmyroutine/actions/workflows/ci.yml/badge.svg)

---

## 🎬 Demo

### Ingredient Compatibility Checker
<!-- Future demo GIF here: Record checking retinol + vitamin C -->
![Ingredient Checker Demo](docs/images/checker-demo.gif)

### AI Skincare Advisor
<!-- Future demo GIF here: Record asking a question and getting response -->
![Advisor Demo](docs/images/advisor-demo.gif)

### Ingredient Library
<!-- Future demo GIF here: Record browsing ingredients -->
![Library Demo](docs/images/library-demo.gif)

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

---

## Overview

Many skincare enthusiasts struggle to know which ingredients can be safely combined. Mixing incompatible ingredients like **Retinol + AHAs** or **Benzoyl Peroxide + Vitamin C** can cause irritation, reduced effectiveness, or skin damage.

**MixMyRoutine** solves this by:
- ✅ Checking ingredient compatibility in real-time
- ✅ Explaining *why* certain combinations are problematic
- ✅ Building optimized routines with proper product ordering
- ✅ Answering skincare questions with AI-powered advice

---

## Features

| Feature | Description |
|---------|-------------|
| **Ingredient Checker** | Select multiple ingredients and instantly see conflicts, cautions, and synergies |
| **Routine Builder** | Add products to AM/PM routines with automatic conflict detection and ordering |
| **AI Advisor** | Ask natural language questions like "Can I use retinol with vitamin C?" |
| **Ingredient Library** | Browse 26 ingredients with detailed usage information |

---

## Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Python 3.11+** | Core language |
| **FastAPI** | REST API framework with automatic OpenAPI docs |
| **Pydantic** | Data validation and serialization |
| **NetworkX** | Graph data structure for semantic networks |
| **pytest** | Testing framework |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | UI library |
| **TypeScript** | Type-safe JavaScript |
| **Vite** | Build tool and dev server |
| **Tailwind CSS** | Utility-first styling |
| **React Query** | Server state management and caching |
| **React Router** | Client-side routing |

### DevOps
| Technology | Purpose |
|------------|---------|
| **Docker** | Containerization |
| **docker-compose** | Multi-container orchestration |
| **GitHub Actions** | CI/CD pipeline with automated testing |
| **nginx** | Production web server for frontend |

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
│  │  • POST /ingredients/check    • GET  /ingredients       │    │
│  │  • POST /routines/build       • POST /advisor/ask       │    │
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

This project demonstrates several **Knowledge-Based AI** principles from Georgia Tech's CS 7637:

### 1. Frame-Based Representation
Each ingredient is a **frame** with slots containing structured knowledge:
```python
@dataclass
class Ingredient:
    id: str
    name: str
    category: IngredientCategory
    description: str
    how_it_works: str
    addresses_concerns: list[SkinConcern]
    time_of_day: TimeOfDay
```

### 2. Semantic Networks
Ingredients and their interactions form a **graph** (using NetworkX):
- **Nodes** = Ingredients (26 total)
- **Edges** = Interactions with attributes (41 rules)
- **Edge attributes** = interaction type, severity, explanation

### 3. Constraint Satisfaction Problem (CSP)
Routine building is modeled as a CSP:
- **Variables** = Products to apply
- **Domains** = Time slots (AM/PM)
- **Constraints** = No conflicts, correct layering order, wait times

### 4. Natural Language Understanding
The advisor agent parses questions using:
- Pattern matching for query classification
- Alias resolution (50+ ingredient name variations)
- Knowledge retrieval for grounded responses

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (optional)

### Option 1: Docker (Recommended)
```bash
git clone https://github.com/Yalfarodeleon/mixmyroutine.git
cd mixmyroutine
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

---

## API Documentation

Interactive Swagger documentation available at `http://localhost:8000/docs`

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/ingredients` | List all ingredients with optional filtering |
| `GET` | `/api/v1/ingredients/{id}` | Get detailed ingredient information |
| `POST` | `/api/v1/ingredients/check` | Check compatibility between ingredients |
| `POST` | `/api/v1/routines/build` | Build optimized routine from products |
| `POST` | `/api/v1/advisor/ask` | Ask a natural language skincare question |
| `GET` | `/api/v1/advisor/status` | Check advisor status and knowledge base stats |

### Example Request
```bash
curl -X POST "http://localhost:8000/api/v1/ingredients/check" \
  -H "Content-Type: application/json" \
  -d '{"ingredients": ["retinol", "vitamin_c"]}'
```

---

## Project Structure

```
mixmyroutine/
├── backend/
│   ├── app/
│   │   ├── api/v1/              # REST endpoints
│   │   │   ├── ingredients.py   # Ingredient & compatibility endpoints
│   │   │   ├── routines.py      # Routine builder endpoint
│   │   │   └── advisor.py       # AI advisor endpoint
│   │   ├── core/                # KBAI business logic
│   │   │   ├── knowledge/       # Knowledge graph & ingredients
│   │   │   ├── routines/        # CSP-based routine builder
│   │   │   └── agent/           # NLU advisor agent
│   │   ├── schemas/             # Pydantic models
│   │   └── main.py              # FastAPI app entry point
│   ├── tests/                   # pytest test suite
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/               # React page components
│   │   ├── hooks/               # React Query custom hooks
│   │   ├── services/            # Axios API client
│   │   ├── types/               # TypeScript interfaces
│   │   └── App.tsx              # Main app with routing
│   ├── Dockerfile
│   └── package.json
│
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI pipeline
│
├── docker-compose.yml
├── Makefile
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
| Ingredient Aliases | 50+ |

---

## Roadmap

### Completed ✅
- [x] Knowledge graph with ingredients and interactions
- [x] RESTful API with FastAPI
- [x] React frontend with TypeScript
- [x] Ingredient compatibility checker
- [x] AI-powered skincare advisor
- [x] Routine builder with CSP
- [x] Docker containerization
- [x] CI/CD with GitHub Actions

### In Progress 🚧
- [ ] Landing page / homepage
- [ ] UI/UX improvements
- [ ] Response formatting enhancements

### Planned 📋
- [ ] User authentication
- [ ] Saved routines & profiles
- [ ] Database integration (PostgreSQL)
- [ ] Production deployment
- [ ] Mobile responsive design

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  <strong>MixMyRoutine</strong> — Mix smarter, glow better ✨
</p>