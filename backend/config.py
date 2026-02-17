"""
Configuration module for eKYC application.
Loads environment variables and provides application settings.
"""
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    # SQLite for development - no need for PostgreSQL server
    DATABASE_URL: str = "sqlite:///./ekyc_db.sqlite"
    # PostgreSQL (requires running server): DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/ekyc_db"
    
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    
    # Application
    APP_NAME: str = "Avanza Solutions eKYC"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"
    

    
    # Security
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    MAX_FILE_SIZE_MB: int = 10
    
    # Computer Vision
    FACE_MATCH_THRESHOLD: float = 0.6
    LIVENESS_CONFIDENCE_THRESHOLD: float = 0.7
    OCR_LANGUAGES: str = "en,ur"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    AUDIT_LOG_PATH: str = "./logs/audit.log"

    # LLM Settings
    GROQ_API_KEY: str = "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"
    GROQ_API_URL: str = "https://api.groq.com/openai/v1/chat/completions"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string into list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def ocr_languages_list(self) -> List[str]:
        """Parse OCR_LANGUAGES string into list."""
        return [lang.strip() for lang in self.OCR_LANGUAGES.split(",")]


# Global settings instance
settings = Settings()
