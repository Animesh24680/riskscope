# RiskScope — Walkthrough

## Prerequisites

- Python 3.11+
- Node.js 18+ (optional, for Railway CLI)
- Docker Desktop (optional, for containerized run)

---

## 1. Local Setup

```bash
# 1. Navigate to project root
cd riskscope

# 2. Create virtual environment
python -m venv .venv

# 3. Activate it
#   Windows (PowerShell):
.venv\Scripts\Activate.ps1
#   macOS / Linux:
source .venv/bin/activate

# 4. Install dependencies
cd backend
pip install -r requirements.txt
cd ..
```

## 2. Environment Variables

Copy `.env.example` to `.env` (or just use the existing `.env`):

```bash
# backend/.env
DATABASE_URL=sqlite:///./data/predictions.db
MODEL_PATH=models/latest_model.pkl
DATA_PATH=data/raw/delinquency_data.csv
CORS_ORIGINS=["*"]
DEBUG=true
API_KEYS=[]
SECRET_KEY=change-me-in-production
```

## 3. Run Locally (backend)

```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API is now available at **http://127.0.0.1:8000**

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/docs | Interactive API docs (Swagger UI) |
| http://127.0.0.1:8000/redoc | Alternative API docs (ReDoc) |
| http://127.0.0.1:8000/health | Health check |

## 4. Run Locally (frontend)

Open `frontend/index.html` directly in your browser, or serve it:

```bash
# Option A: Python simple server
python -m http.server 3000 -d frontend

# Option B: VS Code Live Server extension
right-click frontend/index.html → Open with Live Server

# Option C: NPM serve
npx serve frontend
```

The frontend will connect to `http://127.0.0.1:8000` by default (proxied via `API_BASE = ''` in `api.js`).

## 5. Run with Docker Compose

```bash
docker-compose up -d --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost |
| API docs | http://localhost/docs |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

Stop with:

```bash
docker-compose down
```

## 6. Run Tests

```bash
cd backend
python -m pytest tests/ -v --tb=short
```

Expected output: **18 passed**

## 7. API Endpoints

### POST /predict
Single customer prediction.

```json
{
  "age": 45,
  "income": 70000,
  "credit_score": 750,
  "missed_payments": 0,
  "debt_to_income_ratio": 0.2
}
```

Response includes risk level, probability, confidence, recommendation, and **SHAP explanation** showing why the prediction was made.

### POST /predict/batch
Upload a CSV file for bulk predictions.

Required columns: `Age, Income, Credit_Score, Missed_Payments, Debt_to_Income_Ratio`

### GET /dashboard/stats
Aggregate statistics (total predictions, high-risk count, percentage).

### GET /dashboard/history?limit=100&offset=0
Paginated prediction history.

### GET /dashboard/history/export
Download all history as CSV.

### POST /train
Retrain the model from the data file.

### GET /train/status
Check if model is trained + feature importance.

### GET /health
Server health check.

## 8. Deploy to Railway (Free)

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Link project
railway init

# 4. Add PostgreSQL plugin
railway add postgres

# 5. Set env vars
railway env set DATABASE_URL=postgresql://...
railway env set SECRET_KEY=<random-string>

# 6. Deploy
railway up
```

Or connect your GitHub repo directly at https://railway.app — Railway auto-detects the Dockerfile.

## 9. Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app + lifespan
│   ├── config.py            # Settings from .env
│   ├── database.py          # SQLAlchemy models (Prediction table)
│   ├── models/
│   │   ├── ml_model.py      # RandomForest + scaler + save/load
│   │   └── schemas.py       # Pydantic request/response schemas
│   ├── routers/
│   │   ├── predict.py       # /predict, /predict/batch
│   │   ├── train.py         # /train, /train/status
│   │   └── dashboard.py     # /dashboard/* endpoints
│   └── services/
│       ├── predictor.py     # Orchestrates prediction + DB logging
│       ├── trainer.py       # Training pipeline
│       └── explainer.py     # SHAP TreeExplainer
├── data/
│   └── raw/delinquency_data.csv
├── tests/                   # 18 tests
├── requirements.txt
└── Dockerfile

frontend/
├── index.html               # 4-page SPA
├── css/style.css            # Dark/light theme
└── js/
    ├── api.js               # API client
    ├── app.js               # Pages: Predict, Batch, Dashboard, What-If
    ├── components/toast.js  # Toast notifications
    └── utils/export.js      # CSV export

docker-compose.yml           # App + Nginx + PostgreSQL + Redis
nginx.conf                   # Reverse proxy config
.github/workflows/           # CI + Deploy
Makefile                     # Common commands
.walkthrough.md              # This file
```

## 10. Quick Reference

```bash
make install    # Install deps
make run        # Start server locally
make test       # Run tests
make docker-up  # Start Docker Compose
make clean      # Clean caches
```
