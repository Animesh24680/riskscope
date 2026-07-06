from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import init_db, SessionLocal, Prediction
from app.routers import predict, train, dashboard, drift
from app.services.predictor import initialize_model
from app.auth import verify_api_key, get_rate_limit_key

limiter = Limiter(key_func=get_rate_limit_key)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    result = initialize_model(settings.data_path)
    print(f"Model initialization: {result}")
    yield

app = FastAPI(
    title="RiskScope API",
    description="ML-powered API to assess credit risk",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "X-API-Key", "Authorization"],
)

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path not in ("/health", "/", "/docs", "/openapi.json", "/redoc", "/train/models"):
        try:
            verify_api_key(request)
        except Exception as e:
            return JSONResponse(status_code=401, content={"detail": str(e)})
    return await call_next(request)

app.include_router(predict.router)
app.include_router(train.router)
app.include_router(dashboard.router)
app.include_router(drift.router)

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

@app.get("/health")
async def health():
    from app.services.predictor import model
    db = SessionLocal()
    try:
        total = db.query(Prediction).count()
    finally:
        db.close()
    return {
        "status": "ok",
        "model_trained": model.is_trained,
        "total_predictions": total,
    }

@app.get("/", include_in_schema=False)
async def serve_frontend():
    index = FRONTEND_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return JSONResponse(status_code=404, content={"detail": "Frontend not found"})

@app.get("/{path:path}", include_in_schema=False)
async def serve_static(path: str):
    file = FRONTEND_DIR / path
    if file.exists() and file.is_file():
        return FileResponse(str(file))
    return JSONResponse(status_code=404, content={"detail": "Not found"})

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )
