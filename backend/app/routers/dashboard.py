from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db, Prediction
from app.models.schemas import PredictionHistoryItem, StatsResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/history", response_model=list[PredictionHistoryItem])
async def get_history(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    records = (
        db.query(Prediction)
        .order_by(Prediction.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return records

@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    total = db.query(Prediction).count()
    high_risk_count = db.query(Prediction).filter(Prediction.is_delinquent == True).count()
    high_risk_pct = round(high_risk_count / total * 100, 1) if total else 0.0
    return StatsResponse(
        total_predictions=total,
        high_risk_count=high_risk_count,
        high_risk_pct=high_risk_pct,
    )

@router.get("/history/export")
async def export_history(db: Session = Depends(get_db)):
    records = db.query(Prediction).order_by(Prediction.created_at.desc()).all()
    import csv
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Age", "Income", "Credit_Score", "Missed_Payments",
        "Debt_to_Income_Ratio", "Is_Delinquent", "Risk_Probability",
        "Confidence", "Top_Risk_Factor", "Method", "Created_At"
    ])
    for r in records:
        writer.writerow([
            r.id, r.age, r.income, r.credit_score, r.missed_payments,
            r.debt_to_income_ratio, r.is_delinquent, r.risk_probability,
            r.confidence, r.top_risk_factor, r.method, r.created_at.isoformat()
        ])
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=predictions_export.csv"}
    )
