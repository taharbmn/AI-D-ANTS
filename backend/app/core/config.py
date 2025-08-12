import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application Database (for local development)
    DATABASE_URL: str

    # Docker Database (for container communication)
    DOCKER_DATABASE_URL: Optional[str] = None

    # PostgreSQL specific variables (used by Docker Compose)
    POSTGRES_DB: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None

    # Security Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Application Configuration
    DEBUG: bool = True
    ALLOWED_HOSTS: str = "http://localhost:3000,http://127.0.0.1:3000"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        # Allow extra fields to avoid validation errors
        extra = "allow"

settings = Settings()
