import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DEBUG: bool = True
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
