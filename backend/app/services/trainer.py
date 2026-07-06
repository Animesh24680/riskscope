from app.models.ml_model import DelinquencyModel, FEATURES
from app.services.predictor import model, explainer
from app.services.explainer import SHAPExplainer
from app.services.model_registry import registry
from app.config import settings

def train_model(data_path: str = "data/raw/delinquency_data.csv") -> dict:
    try:
        df = model.load_data(data_path)
        metrics = model.train(df)

        version_path = metrics.pop("version_path", None)

        mlflow_run_id = None
        try:
            import mlflow
            mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
            with mlflow.start_run() as run:
                mlflow.log_params({
                    "n_estimators": metrics.get("n_estimators", 200),
                    "max_depth": metrics.get("max_depth", 10),
                    "model_type": "RandomForest",
                    "data_path": data_path,
                })
                mlflow.log_metrics({
                    "train_accuracy": metrics.get("train_accuracy", 0),
                    "test_accuracy": metrics.get("test_accuracy", 0),
                    "precision": metrics.get("precision", 0),
                    "recall": metrics.get("recall", 0),
                    "f1_score": metrics.get("f1_score", 0),
                    "roc_auc": metrics.get("roc_auc", 0),
                })
                if model.model is not None:
                    mlflow.sklearn.log_model(model.model, "model")
                mlflow_run_id = run.info.run_id
        except ImportError:
            pass
        except Exception:
            pass

        if version_path:
            registry.register(metrics, version_path)

        if model.is_trained and model.model is not None:
            global explainer
            explainer = SHAPExplainer(model.model, FEATURES)

        result = {"trained": True, **metrics}
        if mlflow_run_id:
            result["mlflow_run_id"] = mlflow_run_id
        return result
    except Exception as e:
        return {"trained": False, "error": str(e)}
