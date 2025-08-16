from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True
    )
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Crypto Trading Manager"
    
    # Database
    DATABASE_URL: str = "sqlite:///./crypto_trading.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Bitvavo API
    BITVAVO_API_KEY: Optional[str] = None
    BITVAVO_API_SECRET: Optional[str] = None
    BITVAVO_REST_URL: str = "https://api.bitvavo.com/v2"
    BITVAVO_WS_URL: str = "wss://ws.bitvavo.com/v2/"
    
    # Trading Mode Configuration
    TRADING_MODE: str = "dry_run"  # Options: "dry_run", "demo", "live"
    DRY_RUN_ENABLED: bool = True
    
    # Application settings
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

# Create settings instance
settings = Settings()
