import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()