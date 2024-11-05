from pydantic_settings import BaseSettings
import os



class Settings(BaseSettings):
    MONGODB_URI: str
    MONGODB_NAME: str
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")

    # Google Cloud Settings
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT")
    GOOGLE_CLOUD_REGION: str = os.getenv("GOOGLE_CLOUD_REGION") 
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set Google credentials environment variable
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.GOOGLE_APPLICATION_CREDENTIALS

    class Config:
        env_file = ".env"


settings = Settings()