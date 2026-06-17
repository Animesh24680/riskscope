from sqlalchemy import create_engine, Column, Integer, Float, Boolean, String, DateTime
from sqlalchemy.orm import declarative_base, Session, sessionmaker
from datetime import datetime, timezone
from app.config import settings

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    age = Column(Float, nullable=False)
    income = Column(Float, nullable=False)
    credit_score = Column(Float, nullable=False)
    missed_payments = Column(Integer, nullable=False)
    debt_to_income_ratio = Column(Float, nullable=False)
    is_delinquent = Column(Boolean, nullable=False)
    risk_probability = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    top_risk_factor = Column(String, nullable=True)
    method = Column(String, default="ml_model")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
