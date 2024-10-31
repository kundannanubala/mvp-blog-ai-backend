from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_URI: str
    MONGODB_NAME: str
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_CLOUD_REGION: str
    GOOGLE_APPLICATION_CREDENTIALS: str
    MODEL_NAME: str
    GEMINI_OUTPUT_TOKEN_LIMIT: int
    GOOGLE_API_KEY: str
    GROQ_API_KEY: str
    class Config:
        env_file = ".env"


settings = Settings()