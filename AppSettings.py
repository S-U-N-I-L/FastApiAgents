import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi import FastAPI, Depends


# 1. Define the Settings class
class Settings(BaseSettings):
    app_name: str
    database_url: str
    debug: bool

    # Dynamic file loading based on APP_ENV variable
    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('APP_ENV', 'local')}"
    )


# 2. Cache settings so they load only once
@lru_cache()
def get_settings():
    return Settings()
