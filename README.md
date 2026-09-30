# Fraud Rule Engine with Reviewer Console

A modular, high-throughput Fraud Detection Rule Engine and Analyst Reviewer Console built with Python (FastAPI, SQLAlchemy 2.0, Redis, Celery) and React (TypeScript, Vite).

---

## Project Structure

```text
fraud-rule-engine/
│
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application entrypoint & health check
│   │   ├── api/                     # REST API route modules
│   │   │   ├── __init__.py
│   │   │   ├── transactions.py      # Transaction ingestion endpoints
│   │   │   ├── fraud.py             # Fraud evaluation endpoints
│   │   │   ├── reviews.py           # Reviewer queue & decision endpoints
│   │   │   ├── dashboard.py         # Metrics & statistics endpoints
│   │   │   └── rules.py             # Rule configuration endpoints
│   │   ├── core/                    # Infrastructure & app configuration
│   │   │   ├── config.py            # Pydantic Settings
│   │   │   ├── database.py          # SQLAlchemy 2.0 Async engine & sessions
│   │   │   ├── redis.py             # Redis connection lifecycle
│   │   │   └── logging.py           # Structured log configuration
│   │   ├── models/                  # Database ORM models (empty placeholder)
│   │   ├── schemas/                 # Pydantic validation schemas (empty placeholder)
│   │   ├── rules/                   # Rule interface & registry
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # BaseFraudRule abstract interface
│   │   │   └── registry.py          # Dynamic Rule Registry
│   │   ├── engine/                  # Core Fraud Evaluation logic
│   │   │   ├── __init__.py
│   │   │   ├── fraud_engine.py      # FraudEngine orchestrator skeleton
│   │   │   ├── risk_scorer.py       # RiskScorer algorithm skeleton
│   │   │   └── result.py            # FraudEvaluationResult & FraudDecision models
│   │   ├── services/                # Business logic services
│   │   ├── repositories/            # Database access layer
│   │   ├── workers/                 # Background Celery task processing
│   │   │   ├── celery_app.py        # Celery application configuration
│   │   │   └── tasks.py             # Background task definitions
│   │   └── integrations/            # External integration service adapters
│   │       ├── aws_sns.py           # AWS SNS alert notification adapter
│   │       ├── aws_ses.py           # AWS SES email notification adapter
│   │       └── redis_client.py      # Redis cache & velocity helper service
│   ├── tests/                       # Pytest test suite
│   │   ├── unit/                    # Unit tests
│   │   └── integration/             # Integration tests
│   ├── alembic/                     # Database migrations
│   │   └── versions/
│   ├── requirements.txt             # Python dependencies
│   ├── Dockerfile                   # Backend Docker image specification
│   └── .env.example                 # Backend environment variable template
│
├── frontend/                        # React + TypeScript + Vite console UI
│   ├── src/
│   │   ├── components/              # UI components
│   │   ├── pages/                   # Console pages (DashboardPage)
│   │   ├── services/                # API client services
│   │   ├── hooks/                   # Custom React hooks
│   │   ├── types/                   # TypeScript interfaces
│   │   ├── App.tsx                  # Root application component
│   │   └── main.tsx                 # React entrypoint
│   ├── package.json                 # Frontend dependencies
│   ├── vite.config.ts               # Vite bundler configuration
│   └── Dockerfile                   # Frontend Docker image specification
│
├── docker-compose.yml               # Multi-container local orchestration
├── .gitignore                       # Version control exclusions
└── README.md                        # Documentation
```

---

## Major Directory Directory Overview

- **`backend/app/api/`**: API endpoints exposing transaction ingestion, fraud evaluation triggers, analyst manual overrides, rules management, and metrics.
- **`backend/app/core/`**: Application configuration, database connections (SQLAlchemy 2.0 async), Redis lifecycle, and logging.
- **`backend/app/rules/`**: Declarative base class (`BaseFraudRule`) and registry (`RuleRegistry`) for creating and managing custom fraud rules dynamically.
- **`backend/app/engine/`**: The main evaluation pipeline (`FraudEngine`) and risk aggregator (`RiskScorer`).
- **`backend/app/workers/`**: Celery worker instance and asynchronous tasks for velocity checks and background alert delivery.
- **`backend/app/integrations/`**: Separated adapter interfaces for AWS SNS (SMS/Alerts), AWS SES (Emails), and Redis (Caching/Counters).
- **`frontend/`**: Single Page Application built with React, TypeScript, and Vite providing an executive dashboard and reviewer queue console.

---

## How to Run the Project

### Prerequisites
- Python 3.12+
- Node.js 18+ / npm
- Docker & Docker Compose
- PostgreSQL 16 & Redis 7 (or running via Docker Compose)

---

### Method 1: Start Everything with Docker Compose (Recommended)

1. Clone or navigate to the project directory:
   ```bash
   cd fraud-rule-engine
   ```

2. Copy the environment variables:
   ```bash
   cp .env.example .env
   ```

3. Launch all services (Backend, Frontend, PostgreSQL, Redis, Celery Worker):
   ```bash
   docker-compose up --build
   ```

4. Access the services:
   - **Frontend Dashboard**: `http://localhost:3000`
   - **Backend OpenAPI Docs**: `http://localhost:8000/docs`
   - **Health Endpoint**: `http://localhost:8000/health`

---

### Method 2: Running Services Locally for Development

#### 1. Start Infrastructure Dependencies (Postgres & Redis)
```bash
docker-compose up postgres redis -d
```

#### 2. Start Backend Service
```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations (when models are added)
# alembic upgrade head

# Start Uvicorn development server
uvicorn app.main:app --reload --port 8000
```

#### 3. Start Celery Worker (In a separate terminal)
```bash
cd backend
source .venv/bin/activate
celery -A app.workers.celery_app worker --loglevel=info
```

#### 4. Start Frontend Service (In a separate terminal)
```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```
Access the application at `http://localhost:3000`.

---

### Running Tests
To run backend unit tests:
```bash
cd backend
pytest
```

---

## Next Implementation Steps

1. **Database Schema & ORM Models (`backend/app/models/`)**
   - Implement `Transaction`, `Rule`, `EvaluationLog`, and `ReviewQueue` models using SQLAlchemy 2.0.
   - Generate initial Alembic migration scripts.

2. **Concrete Fraud Rules (`backend/app/rules/`)**
   - Implement velocity rules (e.g. `HighFrequencyTransactionRule`).
   - Implement amount anomaly rules (e.g. `HighAmountRule`).
   - Implement geolocation / IP discrepancy rules.

3. **Risk Scoring Engine (`backend/app/engine/risk_scorer.py`)**
   - Implement weighted risk scoring logic, decision boundary thresholds (Approve, Review, Reject).

4. **Reviewer Workflow API & UI (`backend/app/api/reviews.py` & `frontend/src/pages/`)**
   - Create endpoints and UI tables for manual transaction reviews, analyst approvals, and manual overrides.

5. **AWS Integration Client Logic (`backend/app/integrations/`)**
   - Wire up `boto3` client calls for SNS and SES notifications when high-risk transactions are flagged.
#   A c e n t r a H e a l t h  
 