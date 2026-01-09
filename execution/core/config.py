"""Configuration centralisée de l'application."""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Configuration de l'application avec validation Pydantic."""

    # Database
    postgres_host: str
    postgres_port: int = 5432
    postgres_db: str
    postgres_user: str
    postgres_password: str

    # LLM API
    anthropic_api_key: Optional[str] = None
    gemini_api_key: str

    # Telegram
    telegram_bot_token: str
    telegram_admin_users: list[int]  # Liste des user_id autorisés

    # Business Info (pour documents)
    company_name: str
    company_siret: str
    company_address: str
    company_tva_number: str
    company_logo_path: Optional[str] = None

    # Paths
    tmp_dir: str = ".tmp"
    templates_dir: str = "execution/templates"

    # Application
    app_name: str = "Admin Agent Pro"
    app_version: str = "0.1.0"
    debug: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Retourne une instance singleton des settings."""
    return Settings()
