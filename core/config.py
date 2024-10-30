from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    MONGODB_URI: str
    MONGODB_NAME: str
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")

    class Config:
        env_file = ".env"


settings = Settings()