"""Configuration et settings de l'application."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration de l'application."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # API France Travail (will fail at runtime if not provided)
    francetravail_client_id: str = ""
    francetravail_client_secret: str = ""

    # Base de données
    database_url: str = "sqlite:///./data/emploi_store.db"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False

    # Logging
    log_level: str = "INFO"

    @property
    def database_path(self) -> Path:
        """Retourne le chemin de la base de données."""
        if self.database_url.startswith("sqlite:///./"):
            return Path(self.database_url.replace("sqlite:///./", ""))
        return Path("./data/emploi_store.db")


@lru_cache
def get_settings() -> Settings:
    """Retourne une instance singleton des settings."""
    return Settings()
