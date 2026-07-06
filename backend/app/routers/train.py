from fastapi import APIRouter, HTTPException
from app.models.schemas import TrainResponse
from app.services.trainer import train_model
from app.services.model_registry import registry
from app.config import settings

router = APIRouter(prefix="/train", tags=["training"])

@router.post("", response_model=TrainResponse)
async def train():
    try:
        result = train_model(settings.data_path)
        if not result.get("trained"):
            raise HTTPException(status_code=500, detail=result.get("error", "Training failed"))
        return TrainResponse(
            trained=True,
            message="Model trained successfully",
            train_accuracy=result.get("train_accuracy"),
            test_accuracy=result.get("test_accuracy"),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", response_model=dict)
async def training_status():
    from app.services.predictor import model
    return {
        "is_trained": model.is_trained,
        "feature_importance": model.get_feature_importance() if model.is_trained else None,
    }

@router.get("/models")
async def list_models():
    return {"models": registry.list_models(), "summary": registry.summary()}

@router.post("/rollback/{version_id}")
async def rollback_model(version_id: str):
    success = registry.set_active(version_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Model version {version_id} not found")
    from app.services.predictor import initialize_model
    result = initialize_model(settings.data_path)
    if not result.get("trained") and not result.get("loaded"):
        raise HTTPException(status_code=500, detail="Failed to load rolled-back model")
    return {"message": f"Rolled back to {version_id}", "version_id": version_id}
