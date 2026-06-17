from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime

class PredictionRequest(BaseModel):
    age: float = Field(gt=0, lt=120, description="Customer age (1-119)")
    income: float = Field(gt=0, description="Annual income")
    credit_score: float = Field(ge=300, le=850, description="Credit score (300-850)")
    missed_payments: int = Field(ge=0, description="Number of missed payments")
    debt_to_income_ratio: float = Field(ge=0, le=1, description="Debt-to-income ratio (0-1)")

    @field_validator("age")
    @classmethod
    def age_must_be_reasonable(cls, v: float) -> float:
        if v < 18:
            raise ValueError("Age must be at least 18")
        return v

class PredictionResponse(BaseModel):
    is_delinquent: bool
    risk_probability: float
    confidence: float
    message: str
    recommendation: str
    method: str
    shap_explanation: Optional[dict] = None

class BatchPredictionResponse(BaseModel):
    results: list[PredictionResponse]
    count: int

class PredictionHistoryItem(BaseModel):
    id: int
    age: float
    income: float
    credit_score: float
    missed_payments: int
    debt_to_income_ratio: float
    is_delinquent: bool
    risk_probability: float
    top_risk_factor: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class StatsResponse(BaseModel):
    total_predictions: int
    high_risk_count: int
    high_risk_pct: float

class TrainResponse(BaseModel):
    trained: bool
    message: str
    train_accuracy: Optional[float] = None
    test_accuracy: Optional[float] = None

class HealthResponse(BaseModel):
    status: str
    model_trained: bool
    total_predictions: int
