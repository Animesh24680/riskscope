from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str = "sqlite:///./data/predictions.db"
    redis_url: str = "redis://localhost:6379"
    model_path: str = "models/latest_model.pkl"
    mlflow_tracking_uri: str = "mlruns"
    api_rate_limit: int = 100
    cors_origins: list[str] = ["*"]
    debug: bool = False
    api_keys: list[str] = []
    data_path: str = "data/raw/delinquency_data.csv"
    secret_key: str = "change-me-in-production"

settings = Settings()
