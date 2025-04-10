import os
from pydantic import BaseSettings
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Search Service API"
    PROJECT_DESCRIPTION: str = "Azure AI Search Service"
    VERSION: str = "1.0.0"
    
    # Azure Search configuration
    SEARCH_SERVICE_ENDPOINT: str = os.getenv("SEARCH_SERVICE_ENDPOINT", "")
    INDEX_NAME: str = os.getenv("INDEX_NAME", "")
    AZURE_TENANT_ID: str = os.getenv("AZURE_TENANT_ID", "")
    AZURE_CLIENT_ID: str = os.getenv("AZURE_CLIENT_ID", "")
    AZURE_CLIENT_SECRET: str = os.getenv("AZURE_CLIENT_SECRET", "")
    
    class Config:
        env_file = ".env"

settings = Settings() 