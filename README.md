# Fraud Rule Engine with Reviewer Console

A modular, high-throughput Fraud Detection Rule Engine and Analyst Reviewer Console built with Python (FastAPI, SQLAlchemy 2.0, Redis, Celery) and React (TypeScript, Vite).

---

## Project Structure

```text
fraud-rule-engine/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1/                         # Versioned API routes
│   │   │       ├── __init__.py
│   │   │       ├── transactions.py
│   │   │       ├── fraud.py
│   │   │       ├── reviews.py
│   │   │       ├── dashboard.py
│   │   │       └── rules.py
│   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── redis.py
│   │   │   ├── logging.py
│   │   │   └── security.py                  # Authentication, JWT, and access control
│   │
│   │   ├── models/
│   │   │   ├── __init__.py                  # SQLAlchemy 2.0 model registry
│   │   │   ├── transaction.py
│   │   │   ├── fraud_evaluation.py
│   │   │   ├── rule_result.py
│   │   │   ├── review.py
│   │   │   ├── fraud_rule.py
│   │   │   └── audit_log.py
│   │
│   │   ├── schemas/
│   │   │   ├── __init__.py                  # Pydantic v2 validation models
│   │   │   ├── transaction.py
│   │   │   ├── fraud.py
│   │   │   ├── review.py
│   │   │   ├── dashboard.py
│   │   │   └── rule.py
│   │
│   │   ├── rules/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── registry.py
│   │   │   ├── r1_velocity_spike.py         # R1: High Velocity Spike
│   │   │   ├── r2_device_anomaly.py         # R2: Device Fingerprint Anomaly
│   │   │   ├── r3_billing_region.py         # R3: Billing Region Mismatch
│   │   │   ├── r4_disposable_email.py       # R4: Disposable / High-Risk Email Domain
│   │   │   ├── r5_chargeback_link.py        # R5: Prior Chargeback / Closed Case Link
│   │   │   ├── r6_customer_dispute.py       # R6: Customer Dispute / Unauthorized Claim
│   │   │   ├── r7_pending_evidence.py       # R7: Pending Evidence Verification Guard
│   │   │   ├── r8_customer_legitimacy.py     # R8: Customer Confirmed Legitimacy
│   │   │   ├── r9_high_exposure.py          # R9: High Transaction Exposure (> $2,500)
│   │   │   └── r10_cumulative_threshold.py  # R10: Cumulative Fraud Score Threshold
│   │
│   │   ├── engine/
│   │   │   ├── __init__.py
│   │   │   ├── fraud_engine.py
│   │   │   ├── risk_scorer.py
│   │   │   └── result.py
│   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── transaction_service.py
│   │   │   ├── fraud_service.py
│   │   │   ├── review_service.py
│   │   │   ├── dashboard_service.py
│   │   │   └── notification_service.py
│   │
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── transaction_repository.py
│   │   │   ├── fraud_repository.py
│   │   │   ├── review_repository.py
│   │   │   ├── rule_repository.py
│   │   │   └── audit_repository.py
│   │
│   │   ├── workers/
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py
│   │   │   └── tasks.py
│   │
│   │   └── integrations/
│   │       ├── __init__.py
│   │       ├── aws_sns.py
│   │       ├── aws_ses.py
│   │       └── redis_client.py
│   │
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── rules/
│   │   │   │   └── test_rules.py            # Comprehensive R1-R10 test suite
│   │   │   ├── engine/
│   │   │   │   └── test_engine.py
│   │   │   ├── test_health.py
│   │   │   ├── test_security.py
│   │   │   └── test_models_schemas.py
│   │   └── integration/
│   │       └── test_tigergraph.py
│   │
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── types/
│   │   ├── lib/                            # UI utility helpers
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## Major Directory & Module Overview

- **`backend/app/api/v1/`**: Versioned API endpoints:
  - `transactions.py`: Ingestion, filtering, and transaction lookups.
  - `fraud.py`: Real-time fraud evaluation and evaluation execution history.
  - `reviews.py`: Review queue listings, case details, and manual analyst verdicts.
  - `dashboard.py`: Consolidated executive metrics, KPI stats, and alert feeds.
  - `rules.py`: Dynamic rule registration, weight adjustments, and configuration.
- **`backend/app/core/`**: Infrastructure configuration, SQLAlchemy 2.0 async engine, Redis connection lifecycle, logging, and `security.py` (PBKDF2 password hashing, JWT creation/verification, role enforcement).
- **`backend/app/models/`**: SQLAlchemy 2.0 ORM models (`Transaction`, `FraudRule`, `FraudEvaluation`, `RuleResultModel`, `Review`, `AuditLog`).
- **`backend/app/schemas/`**: Pydantic v2 validation models and DTOs.
- **`backend/app/rules/`**: Declarative base rule interface, dynamic `RuleRegistry`, and canonical fraud detection algorithms:
  - `r1_velocity_spike.py` (**R1**): Detects rapid consecutive transactions or bursts (>= 5 in 10m).
  - `r2_device_anomaly.py` (**R2**): Flags anonymized VPN, proxy, TOR, or device fingerprint tampering.
  - `r3_billing_region.py` (**R3**): Flags billing country vs origin/IP geographical discrepancies.
  - `r4_disposable_email.py` (**R4**): Identifies temporary, burner, or high-risk disposable email domains.
  - `r5_chargeback_link.py` (**R5**): Links entities to historical chargebacks or past confirmed fraud cases.
  - `r6_customer_dispute.py` (**R6**): Flags active customer disputes, stolen card declarations, or unauthorized claims.
  - `r7_pending_evidence.py` (**R7**): Guards against auto-clearing when evidence verification is pending (forces `VERIFICATION_PENDING` / `NEEDS_REVIEW`).
  - `r8_customer_legitimacy.py` (**R8**): Cardholder confirmation clearing guard (forces `CLEARED` / `APPROVED` with risk credit).
  - `r9_high_exposure.py` (**R9**): Flags high transaction or cumulative exposure exceeding $2,500 USD ceiling.
  - `r10_cumulative_threshold.py` (**R10**): Cumulative fraud score threshold evaluation and policy binding.
- **`backend/app/engine/`**: Core evaluation orchestrator (`FraudEngine`), weighted decision boundaries (`RiskScorer`), and result types (`FraudDecision`).
- **`backend/app/repositories/`**: Decoupled database data access layer for all domain entities.
- **`backend/app/services/`**: Business logic orchestration connecting database repositories, rules engine, reviewer workflows, and external notifications.
- **`backend/app/workers/`**: Celery worker instance and asynchronous tasks for velocity checks and background alert delivery.
- **`backend/app/integrations/`**: Separated adapter interfaces for AWS SNS (SMS/Alerts), AWS SES (Emails), Redis (Counters/Sliding window), and TigerGraph.
- **`frontend/`**: React + TypeScript + Vite single page application with modern UI components and analyst reviewer tools.

---

## How to Run the Project

### Prerequisites
- Python 3.12+
- Node.js 18+ / npm
- Docker & Docker Compose
- PostgreSQL 16 & Redis 7 (or running via Docker Compose)

---

### Method 1: Start Everything with Docker Compose (Recommended)

1. Navigate to the project directory:
   ```bash
   cd fraud-rule-engine
   ```

2. Copy the environment variables:
   ```bash
   cp .env.example .env
   ```

3. Launch all services:
   ```bash
   docker compose up --build
   ```

4. Service Endpoints:
   - **Frontend UI Console**: `http://localhost:3000`
   - **Backend API Docs**: `http://localhost:8000/docs`
   - **API Base URL**: `http://localhost:8000/api/v1`
   - **Health Check**: `http://localhost:8000/health`

---

### Method 2: Run Services Locally for Development

#### 1. Start External Infrastructure (PostgreSQL & Redis)
```bash
docker compose up -d postgres redis
```

#### 2. Start Backend Service
```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start FastAPI development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 3. Start Celery Worker (In a separate terminal)
```bash
cd backend
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
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
To run the automated test suite:
```bash
cd backend
pytest
```
All unit and integration tests are configured via `backend/pytest.ini` with native asyncio support.