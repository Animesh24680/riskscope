import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from typing import Optional

FEATURES = ["Age", "Income", "Credit_Score", "Missed_Payments", "Debt_to_Income_Ratio"]
TARGET = "Delinquent"

class DelinquencyModel:
    def __init__(self, model_path: str = "models/latest_model.pkl"):
        self.model: Optional[RandomForestClassifier] = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_path = model_path
        self.train_accuracy: Optional[float] = None
        self.test_accuracy: Optional[float] = None

    def load_data(self, filepath: str) -> pd.DataFrame:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Data file not found: {filepath}")
        df = pd.read_csv(filepath)
        df.dropna(inplace=True)
        return df

    def train(self, df: pd.DataFrame) -> dict:
        required = FEATURES + [TARGET]
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        X = df[FEATURES]
        y = df[TARGET]

        X_scaled = self.scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )

        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            class_weight="balanced",
            n_jobs=-1
        )
        self.model.fit(X_train, y_train)

        y_train_pred = self.model.predict(X_train)
        y_test_pred = self.model.predict(X_test)
        y_test_proba = self.model.predict_proba(X_test)[:, 1]

        self.train_accuracy = accuracy_score(y_train, y_train_pred)
        self.test_accuracy = accuracy_score(y_test, y_test_pred)

        metrics = {
            "train_accuracy": round(self.train_accuracy, 4),
            "test_accuracy": round(self.test_accuracy, 4),
            "precision": round(precision_score(y_test, y_test_pred, zero_division=0), 4),
            "recall": round(recall_score(y_test, y_test_pred, zero_division=0), 4),
            "f1_score": round(f1_score(y_test, y_test_pred, zero_division=0), 4),
            "roc_auc": round(roc_auc_score(y_test, y_test_proba), 4),
            "n_estimators": 200,
            "max_depth": 10,
        }

        self.is_trained = True
        self.save()
        return metrics

    def predict(self, age: float, income: float, credit_score: float,
                missed_payments: int, debt_to_income_ratio: float) -> dict:
        if not self.is_trained:
            return self._rule_based_prediction(credit_score, missed_payments, debt_to_income_ratio)

        input_data = np.array([[age, income, credit_score, missed_payments, debt_to_income_ratio]])
        input_scaled = self.scaler.transform(input_data)

        prediction = self.model.predict(input_scaled)[0]
        proba = self.model.predict_proba(input_scaled)[0]

        return {
            "is_delinquent": bool(prediction),
            "risk_probability": round(float(proba[1]), 4),
            "confidence": round(float(np.max(proba)), 4),
            "method": "ml_model",
        }

    def predict_batch(self, df: pd.DataFrame) -> list[dict]:
        if not self.is_trained:
            return [self._rule_based_prediction(
                row["Credit_Score"], row["Missed_Payments"], row["Debt_to_Income_Ratio"]
            ) for _, row in df.iterrows()]

        X = df[FEATURES]
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        probas = self.model.predict_proba(X_scaled)

        results = []
        for pred, proba in zip(predictions, probas):
            results.append({
                "is_delinquent": bool(pred),
                "risk_probability": round(float(proba[1]), 4),
                "confidence": round(float(np.max(proba)), 4),
                "method": "ml_model",
            })
        return results

    def get_feature_importance(self) -> dict[str, float]:
        if not self.is_trained or self.model is None:
            return {}
        importances = self.model.feature_importances_
        return dict(zip(FEATURES, [round(v, 4) for v in importances]))

    def _rule_based_prediction(self, credit_score: float, missed_payments: int,
                                debt_to_income_ratio: float) -> dict:
        risk_factors = 0
        if credit_score < 600:
            risk_factors += 1
        if missed_payments > 2:
            risk_factors += 1
        if debt_to_income_ratio > 0.4:
            risk_factors += 1
        is_delinquent = risk_factors >= 2
        return {
            "is_delinquent": is_delinquent,
            "risk_probability": round(risk_factors / 3, 4),
            "confidence": 0.7,
            "method": "rule_based",
        }

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, "wb") as f:
            pickle.dump({"model": self.model, "scaler": self.scaler, "is_trained": self.is_trained}, f)

    def load(self) -> bool:
        if not os.path.exists(self.model_path):
            return False
        try:
            with open(self.model_path, "rb") as f:
                data = pickle.load(f)
            self.model = data["model"]
            self.scaler = data["scaler"]
            self.is_trained = data["is_trained"]
            return True
        except Exception:
            return False
