from typing import Any, Dict, List, Optional, Union
from pydantic_settings import BaseSettings

# App configuration using Pydantic BaseSettings
class Settings(BaseSettings):
    PROJECT_NAME: str = "Quill"
    API_V1_STR: str = "/api/v1"
    
   
    USE_SQLITE: bool = True
    DATABASE_URL: Optional[str] = None
    
   
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "quill"
    POSTGRES_PORT: str = "5432"
    
    
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    model_config = {
        "case_sensitive": True,
        "extra": "allow",
    }
    
    # Initializes settings and sets DATABASE_URL if not provided
    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.DATABASE_URL is None:
            if self.USE_SQLITE:
                self.DATABASE_URL = "sqlite:///./quill.db"
            else:
                self.DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
