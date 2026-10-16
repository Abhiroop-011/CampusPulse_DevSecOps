"""
CampusPulse application configuration.
Reads all settings from environment variables (or .env file).
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+psycopg://campuspulse:campuspulse_dev_pass@localhost:5432/campuspulse_db"

    # Application
    environment: str = "development"
    log_level: str = "info"
    backend_port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Test database (SQLite in-memory, used only by pytest)
    test_database_url: str = "sqlite+aiosqlite:///:memory:"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
