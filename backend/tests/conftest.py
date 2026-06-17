import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db, Prediction, Base, engine, SessionLocal
import pandas as pd
import io

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def sample_csv():
    data = pd.DataFrame({
        "Age": [25, 35, 45, 55, 28],
        "Income": [30000, 50000, 70000, 90000, 35000],
        "Credit_Score": [650, 700, 750, 800, 620],
        "Missed_Payments": [1, 2, 0, 1, 3],
        "Debt_to_Income_Ratio": [0.3, 0.4, 0.2, 0.35, 0.5],
        "Delinquent": [1, 1, 0, 0, 1],
    })
    buffer = io.StringIO()
    data.to_csv(buffer, index=False)
    return buffer.getvalue()
