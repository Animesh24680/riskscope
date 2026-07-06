<div align="center">
  <h1>RiskScope</h1>
  <p><strong>ML-Powered Credit Risk Assessment Platform</strong></p>
  <p>Predict financial delinquency with explainable AI — <br>real-time single predictions, batch CSV uploads, and interactive what-if analysis.</p>
</div>

---

## Features

- **Single Prediction** — Assess one customer's risk with instant SHAP explanation
- **Batch Upload** — Upload a CSV for bulk predictions with export
- **Dashboard** — Charts, stats, and prediction history with CSV export
- **What-If Analysis** — Adjust sliders to see how inputs change risk in real time
- **Model Registry** — Versioned models with metrics, rollback, and drift monitoring
- **Explainable AI** — SHAP-based feature contribution breakdown for every prediction
- **API Key Authentication** — Optional auth layer for production use
- **Dark / Light Theme** — Persistent theme toggle

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, FastAPI, Uvicorn |
| ML | scikit-learn (RandomForest), SHAP |
| Database | SQLAlchemy + SQLite (dev) / PostgreSQL (production) |
| Frontend | Vanilla JS, Vite, Chart.js |
| Infra | Render, Railway, GitHub Actions |

## Quick Start (No Docker)

```bash
# 1. Clone
git clone https://github.com/Animesh24680/riskscope.git
cd riskscope

# 2. Backend
cd backend
python -m venv .venv
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
cd ..

# 3. Frontend
npm install
cd frontend
npm install
cd ..

# 4. Build frontend & run
npm run build
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000** — the API and frontend are served together.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/predict` | Single customer risk prediction |
| POST | `/predict/batch` | Upload CSV for bulk predictions |
| GET | `/dashboard/stats` | Aggregate prediction statistics |
| GET | `/dashboard/history` | Paginated prediction history |
| GET | `/dashboard/history/export` | Download all predictions as CSV |
| POST | `/train` | Retrain model from data file |
| GET | `/train/status` | Model status + feature importance |
| GET | `/train/models` | List all registered model versions |
| POST | `/train/rollback/{id}` | Rollback to a specific model version |
| GET | `/drift` | PSI-based drift detection |
| GET | `/health` | Server health check |

Interactive docs at **http://127.0.0.1:8000/docs** (Swagger UI).

## Project Structure

```
riskscope/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Environment settings
│   │   ├── database.py          # SQLAlchemy models
│   │   ├── auth.py              # API key authentication
│   │   ├── models/
│   │   │   ├── ml_model.py      # RandomForest + scaler
│   │   │   └── schemas.py       # Pydantic request/response models
│   │   ├── routers/
│   │   │   ├── predict.py       # /predict endpoints
│   │   │   ├── train.py         # /train endpoints
│   │   │   ├── dashboard.py     # /dashboard endpoints
│   │   │   └── drift.py         # /drift endpoint
│   │   └── services/
│   │       ├── predictor.py     # Prediction orchestration
│   │       ├── trainer.py       # Training pipeline + MLflow
│   │       ├── explainer.py     # SHAP TreeExplainer
│   │       ├── drift.py         # PSI computation
│   │       └── model_registry.py# Versioned model storage
│   ├── alembic/                 # Database migrations
│   ├── data/raw/                # Training data (CSV)
│   ├── tests/                   # Pytest suite
│   └── requirements.txt
├── frontend/
│   ├── index.html               # SPA entry point
│   ├── css/style.css            # Dark/light theme
│   ├── js/
│   │   ├── app.js               # Pages: Predict, Batch, Dashboard, What-If, Models
│   │   ├── api.js               # API client
│   │   ├── components/toast.js  # Toast notifications
│   │   └── utils/export.js      # CSV export
│   ├── vite.config.js           # Vite config
│   └── package.json
├── .env                         # Environment variables
└── README.md
```

## Deployment (Render)

1. Push to GitHub
2. Go to [render.com](https://render.com) → New Web Service → connect your repo
3. Set:
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add env vars: `SECRET_KEY`, `DEBUG=false`
5. Deploy — your app is live at `https://riskscope.onrender.com`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./data/predictions.db` | Database connection string |
| `MODEL_PATH` | `models/latest_model.pkl` | Path to serialized model |
| `DATA_PATH` | `data/raw/delinquency_data.csv` | Training data file |
| `CORS_ORIGINS` | `["*"]` | Allowed origins |
| `API_KEYS` | `[]` | Comma-separated API keys (empty = no auth) |
| `SECRET_KEY` | — | Required in production |
| `DEBUG` | `false` | Enable debug mode |

## Testing

```bash
cd backend
python -m pytest tests/ -v --tb=short
```

## License

MIT
