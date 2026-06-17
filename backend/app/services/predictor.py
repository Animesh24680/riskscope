from app.models.ml_model import DelinquencyModel, FEATURES
from app.services.explainer import SHAPExplainer
from app.database import SessionLocal, Prediction
from typing import Optional
import pandas as pd

model = DelinquencyModel()
explainer: Optional[SHAPExplainer] = None

def initialize_model(data_path: str) -> dict:
    global explainer
    loaded = model.load()
    if not loaded:
        try:
            df = model.load_data(data_path)
            metrics = model.train(df)
            if model.is_trained and model.model is not None:
                explainer = SHAPExplainer(model.model, FEATURES)
            return {"loaded": False, "trained": True, "metrics": metrics}
        except Exception as e:
            return {"loaded": False, "trained": False, "error": str(e)}
    else:
        if model.model is not None:
            explainer = SHAPExplainer(model.model, FEATURES)
        return {"loaded": True, "trained": True}

def predict(age: float, income: float, credit_score: float,
            missed_payments: int, debt_to_income_ratio: float) -> dict:
    result = model.predict(age, income, credit_score, missed_payments, debt_to_income_ratio)

    shap_explanation = None
    top_risk_factor = None
    if explainer is not None and result["method"] == "ml_model":
        input_df = pd.DataFrame([{
            "Age": age, "Income": income, "Credit_Score": credit_score,
            "Missed_Payments": missed_payments, "Debt_to_Income_Ratio": debt_to_income_ratio
        }])
        shap_explanation = explainer.explain(input_df)
        top_risk_factor = shap_explanation.get("top_factor")

    if result["is_delinquent"]:
        result["message"] = "High risk of financial delinquency detected."
        result["recommendation"] = "Recommended: Conduct further financial review"
    else:
        result["message"] = "Low risk of financial delinquency."
        result["recommendation"] = "Customer appears financially stable"

    result["shap_explanation"] = shap_explanation

    db = SessionLocal()
    try:
        record = Prediction(
            age=age, income=income, credit_score=credit_score,
            missed_payments=missed_payments, debt_to_income_ratio=debt_to_income_ratio,
            is_delinquent=result["is_delinquent"],
            risk_probability=result["risk_probability"],
            confidence=result.get("confidence", 0.0),
            top_risk_factor=top_risk_factor,
            method=result["method"],
        )
        db.add(record)
        db.commit()
    finally:
        db.close()

    return result

def predict_batch(filepath: str) -> list[dict]:
    df = pd.read_csv(filepath)
    required = {"Age", "Income", "Credit_Score", "Missed_Payments", "Debt_to_Income_Ratio"}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing required columns. Need: {required}")

    results = []
    db = SessionLocal()
    try:
        batch_results = model.predict_batch(df)
        for i, (_, row) in enumerate(df.iterrows()):
            res = batch_results[i]

            shap_explanation = None
            top_risk_factor = None
            if explainer is not None and res["method"] == "ml_model":
                input_df = pd.DataFrame([row[list(required)]])
                shap_explanation = explainer.explain(input_df)
                top_risk_factor = shap_explanation.get("top_factor")

            if res["is_delinquent"]:
                res["message"] = "High risk of financial delinquency detected."
                res["recommendation"] = "Recommended: Conduct further financial review"
            else:
                res["message"] = "Low risk of financial delinquency."
                res["recommendation"] = "Customer appears financially stable"
            res["shap_explanation"] = shap_explanation

            record = Prediction(
                age=float(row["Age"]), income=float(row["Income"]),
                credit_score=float(row["Credit_Score"]),
                missed_payments=int(row["Missed_Payments"]),
                debt_to_income_ratio=float(row["Debt_to_Income_Ratio"]),
                is_delinquent=res["is_delinquent"],
                risk_probability=res["risk_probability"],
                confidence=res.get("confidence", 0.0),
                top_risk_factor=top_risk_factor,
                method=res["method"],
            )
            db.add(record)
            results.append(res)
        db.commit()
    finally:
        db.close()

    return results
