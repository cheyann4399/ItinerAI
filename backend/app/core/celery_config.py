from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class CelerySettings(BaseSettings):
  model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
  )

  celery_broker_url: str = "redis://localhost:6379/0"
  celery_result_backend: str = "redis://localhost:6379/1"
  celery_task_default_queue: str = "default"


@lru_cache(maxsize=1)
def get_celery_settings() -> CelerySettings:
  return CelerySettings()

