import pytest
import pandas as pd
import numpy as np
from app.models.ml_model import DelinquencyModel

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "Age": [25, 35, 45, 55, 28, 40, 50, 33, 38, 48],
        "Income": [30000, 50000, 70000, 90000, 35000, 60000, 80000, 45000, 55000, 75000],
        "Credit_Score": [650, 700, 750, 800, 620, 680, 770, 660, 720, 780],
        "Missed_Payments": [1, 2, 0, 1, 3, 1, 0, 2, 1, 0],
        "Debt_to_Income_Ratio": [0.3, 0.4, 0.2, 0.35, 0.5, 0.25, 0.15, 0.45, 0.33, 0.22],
        "Delinquent": [1, 1, 0, 0, 1, 0, 0, 1, 0, 0],
    })

def test_model_initialization():
    model = DelinquencyModel()
    assert model.is_trained == False
    assert model.model is None

def test_model_training(sample_df):
    model = DelinquencyModel()
    metrics = model.train(sample_df)
    assert model.is_trained == True
    assert "train_accuracy" in metrics
    assert "test_accuracy" in metrics
    assert metrics["train_accuracy"] > 0

def test_model_prediction(sample_df):
    model = DelinquencyModel()
    model.train(sample_df)
    result = model.predict(45, 70000, 750, 0, 0.2)
    assert "is_delinquent" in result
    assert "risk_probability" in result
    assert "method" in result
    assert result["method"] == "ml_model"

def test_model_prediction_before_training():
    model = DelinquencyModel()
    result = model.predict(45, 70000, 750, 0, 0.2)
    assert result["method"] == "rule_based"

def test_batch_prediction(sample_df):
    model = DelinquencyModel()
    model.train(sample_df)
    results = model.predict_batch(sample_df)
    assert len(results) == len(sample_df)
    for r in results:
        assert "is_delinquent" in r
        assert "risk_probability" in r

def test_save_and_load(sample_df, tmp_path):
    model = DelinquencyModel(str(tmp_path / "test_model.pkl"))
    model.train(sample_df)
    model.save()
    
    new_model = DelinquencyModel(str(tmp_path / "test_model.pkl"))
    loaded = new_model.load()
    assert loaded == True
    assert new_model.is_trained == True
    
    result = new_model.predict(45, 70000, 750, 0, 0.2)
    assert "is_delinquent" in result

def test_feature_importance(sample_df):
    model = DelinquencyModel()
    model.train(sample_df)
    importance = model.get_feature_importance()
    expected_keys = {"Age", "Income", "Credit_Score", "Missed_Payments", "Debt_to_Income_Ratio"}
    assert set(importance.keys()) == expected_keys
    assert all(0 <= v <= 1 for v in importance.values())

def test_rule_based_fallback():
    model = DelinquencyModel()
    result = model._rule_based_prediction(550, 5, 0.5)
    assert result["is_delinquent"] == True
    
    result = model._rule_based_prediction(700, 0, 0.2)
    assert result["is_delinquent"] == False
