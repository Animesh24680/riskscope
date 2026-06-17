import os
import uuid
import json
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.database import get_db, Prediction
from app.models.schemas import PredictionRequest, PredictionResponse, BatchPredictionResponse
from app.services.predictor import predict, predict_batch
from app.config import settings

router = APIRouter(prefix="/predict", tags=["prediction"])

@router.post("", response_model=PredictionResponse)
async def single_prediction(req: PredictionRequest):
    try:
        result = predict(
            age=req.age,
            income=req.income,
            credit_score=req.credit_score,
            missed_payments=req.missed_payments,
            debt_to_income_ratio=req.debt_to_income_ratio,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch", response_model=BatchPredictionResponse)
async def batch_prediction(file: UploadFile = File(...)):
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    temp_dir = "data/raw"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, f"batch_{uuid.uuid4().hex}.csv")

    try:
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)

        results = predict_batch(temp_path)
        return {"results": results, "count": len(results)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
