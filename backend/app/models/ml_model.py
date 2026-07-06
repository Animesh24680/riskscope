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
        version_path = self.save()
        return {**metrics, "version_path": version_path}

    def predict(self, age: float, income: float, credit_score: float,
                missed_payments: int, debt_to_income_ratio: float) -> dict:
        if not self.is_trained:
            return self._rule_based_prediction(credit_score, missed_payments, debt_to_income_ratio, age, income)

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
            return [
                self._rule_based_prediction(
                    row["Credit_Score"], row["Missed_Payments"],
                    row["Debt_to_Income_Ratio"],
                    row.get("Age"), row.get("Income"),
                )
                for _, row in df.iterrows()
            ]

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

    def _rule_based_prediction(self, credit_score: float = 0, missed_payments: int = 0,
                               debt_to_income_ratio: float = 0, age: float | None = None,
                               income: float | None = None) -> dict:
        score = 0.0

        if credit_score < 580:
            score += 0.35
        elif credit_score < 620:
            score += 0.25
        elif credit_score < 670:
            score += 0.12

        if missed_payments >= 5:
            score += 0.30
        elif missed_payments >= 3:
            score += 0.20
        elif missed_payments >= 1:
            score += 0.08

        if debt_to_income_ratio > 0.5:
            score += 0.25
        elif debt_to_income_ratio > 0.4:
            score += 0.15
        elif debt_to_income_ratio > 0.3:
            score += 0.05

        if age is not None and age < 25:
            score += 0.05
        if income is not None and income < 30000:
            score += 0.05

        is_delinquent = score >= 0.35
        confidence = 0.6 + min(abs(score - 0.35) / 0.65 * 0.3, 0.35)

        if score >= 0.55:
            message = "High risk"
        elif score >= 0.35:
            message = "Medium risk"
        else:
            message = "Low risk"

        return {
            "is_delinquent": is_delinquent,
            "risk_probability": round(min(score, 0.95), 4),
            "confidence": round(min(confidence, 0.95), 4),
            "method": "rule_based",
            "rule_based_risk_tier": message,
        }

    def save(self) -> str:
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, "wb") as f:
            pickle.dump({"model": self.model, "scaler": self.scaler, "is_trained": self.is_trained}, f)
        return self.model_path

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
