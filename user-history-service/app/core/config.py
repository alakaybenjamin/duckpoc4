import os
from pydantic import BaseSettings
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "User & History Service"
    PROJECT_DESCRIPTION: str = "User Management and Search History"
    VERSION: str = "1.0.0"
    
    # Database configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/devsearch")
    
    class Config:
        env_file = ".env"

settings = Settings() 