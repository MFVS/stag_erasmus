"""Konfigurace aplikace z .env souboru."""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App settings."""

    stag_user: str
    stag_password: SecretStr

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # retrun auth tuple
    def get_auth(self) -> tuple:
        """Return auth tuple."""
        return (self.stag_user, self.stag_password.get_secret_value())


settings = Settings()
