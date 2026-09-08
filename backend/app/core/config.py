"""App configuration, loaded from environment variables (see
deployment/docker-compose.yml for defaults)."""
import os


class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql://guardian:guardian@localhost:5432/edgehealth"
    )
    cors_origins: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    prediction_horizon_hours: float = float(os.getenv("PREDICTION_HORIZON_HOURS", "8"))


settings = Settings()
