from app.models.ml_model import DelinquencyModel, FEATURES
from app.services.predictor import model, explainer
from app.services.explainer import SHAPExplainer
from app.config import settings

def train_model(data_path: str = "data/raw/delinquency_data.csv") -> dict:
    try:
        df = model.load_data(data_path)
        metrics = model.train(df)
        if model.is_trained and model.model is not None:
            global explainer
            explainer = SHAPExplainer(model.model, FEATURES)
        return {"trained": True, **metrics}
    except Exception as e:
        return {"trained": False, "error": str(e)}
