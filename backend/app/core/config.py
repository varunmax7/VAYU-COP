from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "VAYU-COP"
    version: str = "0.1.0"
    environment: Literal["dev", "test", "prod"] = "dev"

    database_url: str = "sqlite:///./vayu.db"

    jwt_secret: str = "change-me"
    jwt_expire_min: int = 720
    jwt_algorithm: str = "HS256"

    weather_mode: Literal["auto", "live", "synthetic"] = "auto"
    map_tiles: Literal["auto", "online", "offline"] = "auto"

    llm_provider: Literal["none", "anthropic", "openai", "ollama"] = "none"
    llm_model: str = ""
    llm_api_key: str = ""
    ollama_url: str = "http://localhost:11434"

    sim_autostart: bool = False
    sim_speed: int = 10

    cors_origins: str = "http://localhost:5173"

    @field_validator("cors_origins")
    @classmethod
    def _normalise_cors(cls, v: str) -> str:
        return v.strip()

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
