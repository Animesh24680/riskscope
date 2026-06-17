from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model_trained" in data

def test_single_prediction():
    payload = {
        "age": 45,
        "income": 70000,
        "credit_score": 750,
        "missed_payments": 0,
        "debt_to_income_ratio": 0.2,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "is_delinquent" in data
    assert "risk_probability" in data
    assert "message" in data
    assert "recommendation" in data

def test_prediction_validation():
    payload = {"age": -1, "income": 0, "credit_score": 200, "missed_payments": -1, "debt_to_income_ratio": 1.5}
    response = client.post("/predict", json=payload)
    assert response.status_code == 422

def test_batch_prediction(sample_csv):
    response = client.post("/predict/batch", files={"file": ("test.csv", sample_csv, "text/csv")})
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 5
    assert len(data["results"]) == 5

def test_batch_invalid_file():
    response = client.post("/predict/batch", files={"file": ("test.txt", b"not csv", "text/plain")})
    assert response.status_code == 400

def test_batch_missing_columns():
    bad_csv = "Name,Age\nJohn,30\n"
    response = client.post("/predict/batch", files={"file": ("bad.csv", bad_csv, "text/csv")})
    assert response.status_code == 400

def test_dashboard_stats():
    response = client.get("/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_predictions" in data
    assert "high_risk_count" in data

def test_dashboard_history():
    response = client.get("/dashboard/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_dashboard_history_pagination():
    response = client.get("/dashboard/history?limit=5&offset=0")
    assert response.status_code == 200

def test_training_status():
    response = client.get("/train/status")
    assert response.status_code == 200
    data = response.json()
    assert "is_trained" in data
