from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
  )
  app_name: str = "ItinerAI"
  app_env: str = "local"
  app_debug: bool = True
  database_url: str = "postgresql+psycopg2://user:password@localhost:5432/itinerai"
  secret_key: str = "change-me-in-production"
  algorithm: str = "HS256"
  access_token_expire_minutes: int = 60 * 24 * 7
  # LLM / Kimi 相关配置（可选）
  kimi_api_key: str | None = None
  kimi_base_url: str | None = None
  kimi_model: str | None = "moonshot-v1-128k"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
  return Settings()

