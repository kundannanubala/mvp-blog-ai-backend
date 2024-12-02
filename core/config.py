from pydantic_settings import BaseSettings
import os
import certifi

class Settings(BaseSettings):
    """
    Configuration settings for the application.

    This class uses Pydantic's BaseSettings to automatically load environment variables
    and provides structured access to various configuration parameters required by the application.

    Attributes:
        MONGODB_URI (str): The URI for connecting to the MongoDB database.
        MONGODB_NAME (str): The name of the MongoDB database.
        GOOGLE_API_KEY (str): The API key for accessing Google services.
        GROQ_API_KEY (str): The API key for accessing GROQ services.
        GOOGLE_CLOUD_PROJECT (str): The Google Cloud project identifier.
        GOOGLE_CLOUD_REGION (str): The Google Cloud region.
        GOOGLE_APPLICATION_CREDENTIALS (str): The path to the Google Cloud application credentials file.
        ASTRA_DB_APPLICATION_TOKEN (str): The application token for AstraDB.
        ASTRA_DB_API_ENDPOINT (str): The API endpoint for AstraDB.
        COLLECTION_NAME (str): The name of the collection in AstraDB.
    """
    MONGODB_URI: str
    MONGODB_NAME: str
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")

    # Google Cloud Settings
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT")
    GOOGLE_CLOUD_REGION: str = os.getenv("GOOGLE_CLOUD_REGION")
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    # AstraDB Settings
    ASTRA_DB_APPLICATION_TOKEN: str = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
    ASTRA_DB_API_ENDPOINT: str = os.getenv("ASTRA_DB_API_ENDPOINT")
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME")

    @property
    def mongodb_settings(self):
        """
        MongoDB connection options.

        Returns:
            dict: A dictionary containing MongoDB connection options such as TLS settings and write concerns.
        """
        return {
            "tls": True,  # Enable TLS for secure connections
            "tlsCAFile": certifi.where(),  # Use the certifi package to locate the CA file
            "retryWrites": True,  # Enable retryable writes for MongoDB
            "w": "majority",  # Set write concern to majority
        }

    def __init__(self, **kwargs):
        """
        Initialize the Settings class and set up environment variables.

        Args:
            **kwargs: Arbitrary keyword arguments passed to the BaseSettings initializer.
        """
        super().__init__(**kwargs)
        # Set the environment variable for Google application credentials
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
            self.GOOGLE_APPLICATION_CREDENTIALS
        )

    class Config:
        """
        Configuration for the Settings class.

        Attributes:
            env_file (str): The path to the environment file containing configuration variables.
        """
        env_file = ".env"

# Instantiate the settings object to access configuration throughout the application
settings = Settings()
