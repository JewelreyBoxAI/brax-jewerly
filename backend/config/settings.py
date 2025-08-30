from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    cors_allow_origins: List[str] = ["*"]

    postgres_url: str
    redis_url: str | None = None

    ghl_webhook_url: str | None = None
    ghl_api_key: str | None = None
    ghl_api_base: str = "https://services.leadconnectorhq.com"
    ghl_api_version: str = "2021-07-28"
    ghl_location_id: str | None = None
    ghl_pipeline_id: str | None = None
    ghl_stage_id: str | None = None

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()