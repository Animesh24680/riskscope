from fastapi import APIRouter, Query
from app.services.drift import detect_drift

router = APIRouter(prefix="/drift", tags=["drift"])


@router.get("")
async def drift_status(window: int = Query(default=100, ge=10, le=1000),
                       baseline: int = Query(default=500, ge=100, le=10000)):
    return detect_drift(window=window, baseline_size=baseline)
