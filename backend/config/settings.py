import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@hostname/dbname?sslmode=require"
    
    # LLM
    GROQ_API_KEY: str = ""
    CEREBRAS_API_KEY: str = ""
    DEFAULT_MODEL: str = "llama-3.3-70b-versatile"
    TEMPERATURE: float = 0.2
    
    # File handling
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: str = "xlsx,xls,csv"
    UPLOAD_DIR: str = "data/uploads"
    EXPORT_DIR: str = "data/exports"
    
    # App
    PROJECT_NAME: str = "Exodus Engine"
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        extra="ignore"
    )

    def get_allowed_extensions_list(self) -> List[str]:
        return [ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(",")]

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.EXPORT_DIR, exist_ok=True)
