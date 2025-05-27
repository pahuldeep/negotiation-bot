import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "AI Negotiation API"
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", 6379))
    redis_password: str = os.getenv("REDIS_PASSWORD", "")
    ai_api_key: str = os.getenv("AI_API_KEY", "")
    session_ttl: int = 86400  # 24 hours

    class Config:
        env_file = ".env"

settings = Settings()
