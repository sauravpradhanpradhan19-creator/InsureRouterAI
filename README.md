# InsurRoute AI 🛡️

> AI-powered insurance claim router using **LangGraph** multi-agent pipeline, **Groq LLM**, **RAG** knowledge base, **FastAPI**, and **React**.

Built as a portfolio project demonstrating real-world agentic AI architecture.

---

## What It Does

A customer describes their insurance claim in plain text. The AI pipeline automatically:

1. **Validates** the input (IntakeValidator)
2. **Classifies** the claim type — health, motor, property, life, travel, liability (ClaimClassifier)
3. **Validates** coverage against company policy documents via RAG (PolicyValidator)
4. **Scores fraud risk** 1–5 with detected red flags (FraudScorer)
5. **Scores priority** 1–5 based on urgency (PriorityScorer)
6. **Routes** to the correct specialist department (DepartmentRouter)
7. **Composes** a structured customer response with documents required (ResponseComposer)

All in under 10 seconds. Every agent step is traced in LangSmith.

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq (Llama 3.1 8B / 70B) — free tier |
| Orchestration | LangGraph state machine |
| RAG | FAISS + HuggingFace sentence-transformers |
| Knowledge base | Multi-tenant per-company FAISS indexes |
| API | FastAPI + async SQLAlchemy |
| Database | SQLite (dev) → PostgreSQL (prod) |
| Observability | LangSmith agent tracing |
| Frontend | React + TypeScript + Tailwind CSS |
| Infrastructure | Docker Compose |

---

## Project Structure

```
insurance-claim-router/
├── backend/
│   ├── app/
│   │   ├── agents/nodes.py          # All 7 LangGraph agent nodes
│   │   ├── graph/
│   │   │   ├── pipeline.py          # LangGraph state machine
│   │   │   └── state.py             # ClaimState TypedDict
│   │   ├── rag/
│   │   │   ├── knowledge_base.py    # Multi-tenant FAISS manager
│   │   │   └── demo_seed.py         # Demo policy data seeder
│   │   ├── api/routes/
│   │   │   ├── claims.py            # POST /claims/submit
│   │   │   ├── admin.py             # GET /admin/metrics
│   │   │   └── health.py            # GET /health
│   │   ├── database/
│   │   │   ├── models.py            # SQLAlchemy ORM models
│   │   │   ├── connection.py        # Async engine + session
│   │   │   └── crud.py              # All DB operations
│   │   ├── config/settings.py       # Pydantic settings
│   │   └── main.py                  # FastAPI app + lifespan
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── SubmitClaim.tsx      # Claim submission + results
│       │   ├── AdminDashboard.tsx   # Metrics + claims table
│       │   └── KnowledgeBase.tsx    # PDF upload UI
│       ├── components/
│       │   ├── Layout.tsx           # Navigation
│       │   └── ui.tsx               # Reusable components
│       ├── lib/api.ts               # Axios API client
│       ├── store/index.ts           # Zustand global state
│       └── types/index.ts           # TypeScript types
├── kb/                              # FAISS vector stores (auto-generated)
├── docker/
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── docker-compose.yml
└── .env.example
```

---

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/yourusername/insurance-claim-router
cd insurance-claim-router
cp .env.example .env
```

### 2. Add your API keys to `.env`

```bash
# Get free key at https://console.groq.com
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx

# Get free key at https://smith.langchain.com (optional)
LANGCHAIN_API_KEY=ls_xxxxxxxxxxxxxxxxxxxx
LANGCHAIN_TRACING_V2=true
```

### 3. Run with Docker

```bash
docker compose up --build
```

That's it. Open:
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **LangSmith**: https://smith.langchain.com (traces appear automatically)

---

## Running Locally (without Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env        # fill in your keys
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## API Endpoints

### Submit a Claim
```http
POST /claims/submit
Content-Type: application/json

{
  "company_slug": "demo_hdfc",
  "description": "I was hospitalized for 3 days due to dengue fever. Bill is Rs 45,000.",
  "customer_name": "Rahul Sharma",
  "policy_number": "HDFC-2024-98765"
}
```

### Get Metrics
```http
GET /admin/metrics
```

### Upload Policy PDF
```http
POST /admin/ingest-pdf
Content-Type: multipart/form-data

company_slug=demo_hdfc
file=@policy.pdf
```

### Interactive Docs
```
http://localhost:8000/docs
```

---

## Multi-Tenant Knowledge Base

Each insurance company gets its own isolated FAISS vector store:

```
kb/
├── shared/          # IRDAI regulations (applies to all)
├── demo_hdfc/       # HDFC Ergo policies
└── demo_star/       # Star Health policies
```

**Demo data** is auto-seeded on startup with:
- HDFC Ergo Health Suraksha Plus policy
- HDFC Ergo Motor Package policy
- Star Health Comprehensive policy
- IRDAI claim regulations

**Add real policies**: Upload PDFs via the Knowledge Base page or `POST /admin/ingest-pdf`.

---

## LangGraph Pipeline

```
Patient Input
     ↓
IntakeValidator  ──(invalid)──→ ResponseComposer
     ↓ (valid)
ClaimClassifier
     ↓
PolicyValidator  ← RAG queries company KB
     ↓
FraudScorer
     ↓ (fraud=5)──────────────→ DepartmentRouter
     ↓ (fraud<5)
PriorityScorer
     ↓
DepartmentRouter  ← conditional routing by type + priority + fraud
     ↓
ResponseComposer
     ↓
JSON Response + DB log
```

---

## Sample Claims to Test

```
Health: "I was hospitalized for 5 days at Apollo Hospital due to typhoid. Total bill Rs 80,000. Policy no HDFC-2024-12345."

Motor: "My car was hit by another vehicle at a traffic signal yesterday. Front bumper and bonnet damaged. I have photos and witnesses."

Property: "Heavy rains caused flooding in my ground floor shop. Stock and equipment worth Rs 2 lakh destroyed."

Fraud (high risk): "I just bought this policy last week and my car was stolen immediately. Need urgent claim settlement."

Travel: "My flight was delayed by 8 hours and I missed my connecting flight. Stuck in Dubai airport with no accommodation."
```

---

## Deployment

For production deployment, update `.env`:
```bash
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/insurroute
ALLOWED_ORIGINS=https://yourdomain.com
```

Deploy to any cloud that supports Docker:
- **Railway** — `railway up`
- **Render** — connect GitHub repo
- **AWS ECS** — push to ECR, deploy task definition
- **DigitalOcean App Platform** — connect repo, auto-deploy

---

## License

MIT — free to use for personal projects and portfolios.
