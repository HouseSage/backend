from typing import Any, Dict, List, Optional, Union
from pydantic_settings import BaseSettings

# App configuration using Pydantic BaseSettings
class Settings(BaseSettings):
    # Application settings
    PROJECT_NAME: str = "Quill"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Database settings
    USE_SQLITE: bool = True
    DATABASE_URL: Optional[str] = None
    
    # PostgreSQL settings (used if USE_SQLITE is False)
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "quill"
    POSTGRES_PORT: str = "5432"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Authentication settings
    SECRET_KEY: str = "your-secret-key-here"  # Change this in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Link shortener settings
    DEFAULT_DOMAIN: str = "qill.me"  # Default domain for shortened links
    SHORT_CODE_LENGTH: int = 6  # Default length of generated short codes
    MAX_SHORT_CODE_LENGTH: int = 20  # Maximum allowed length for custom short codes
    ALLOW_CUSTOM_DOMAINS: bool = True  # Whether to allow custom domains
    REQUIRE_ACCOUNT_FOR_CREATION: bool = True  # Whether to require an account to create links
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100  # Max requests per minute per IP
    
    # Analytics and tracking
    TRACK_CLICKS: bool = True
    STORE_IP_ADDRESS: bool = True
    STORE_USER_AGENT: bool = True
    STORE_REFERRER: bool = True
    
    # Cache settings
    USE_REDIS: bool = False
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 300  # 5 minutes
    
    # Frontend URLs (for password reset, etc.)
    FRONTEND_BASE_URL: str = "http://localhost:3000"
    
    # Email settings (for notifications, etc.)
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@qill.me"
    
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
