from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "آوانگار"
    transcriber_mode: Literal["auto", "whisper", "demo"] = "auto"
    whisper_model: str = "small"
    whisper_device: str = "auto"
    whisper_compute_type: str = "default"
    max_upload_mb: int = 100
    job_ttl_minutes: int = 60
    low_confidence_threshold: float = 0.55
    temp_dir: Path = Path("/tmp/ava-negar")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.temp_dir.mkdir(parents=True, exist_ok=True)
    return settings

