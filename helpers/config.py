from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    OPENAI_API_KEY: str


    class Config:
        env_file = ".env.app"

# Helper funcation to easily get the setting anywhere in my app
def get_settings():
    return Settings()