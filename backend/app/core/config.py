import os
from enum import Enum
from typing import List, Optional

from pydantic import ConfigDict, field_validator
from pydantic_settings import BaseSettings


class Environment(str, Enum):
    """Application environment types"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class TradingMode(str, Enum):
    """Trading mode options"""

    DRY_RUN = "dry_run"
    DEMO = "demo"
    LIVE = "live"


class LogLevel(str, Enum):
    """Logging levels"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """Application settings with enterprise-grade configuration management"""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="forbid",  # Prevent unknown environment variables
    )

    # Environment Configuration
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = False
    TESTING: bool = False

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Crypto Trading Manager"
    VERSION: str = "1.0.0"

    # Server Configuration
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    WORKERS: int = 1

    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://localhost:3000",
        "https://localhost:5173",
    ]

    # Database Configuration
    DATABASE_URL: str = "sqlite:///./crypto_trading.db"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Security Configuration
    SECRET_KEY: str = (
        "your-secret-key-change-this-in-production-use-openssl-rand-hex-32"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ENCRYPTION_KEY: Optional[str] = None

    # API Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10

    # Bitvavo API Configuration
    BITVAVO_API_KEY: Optional[str] = None
    BITVAVO_API_SECRET: Optional[str] = None
    BITVAVO_REST_URL: str = "https://api.bitvavo.com/v2"
    BITVAVO_WS_URL: str = "wss://ws.bitvavo.com/v2/"
    BITVAVO_RATE_LIMIT: int = 1000  # requests per minute

    # Trading Configuration
    TRADING_MODE: TradingMode = TradingMode.DRY_RUN
    DRY_RUN_ENABLED: bool = True
    MAX_POSITION_SIZE: float = 1000.0  # USD
    DEFAULT_STOP_LOSS_PERCENTAGE: float = 0.02  # 2%
    DEFAULT_TAKE_PROFIT_PERCENTAGE: float = 0.05  # 5%

    # Logging Configuration
    LOG_LEVEL: LogLevel = LogLevel.INFO
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = None
    LOG_ROTATION: str = "1 day"
    LOG_RETENTION: str = "30 days"

    # Monitoring and Health Checks
    HEALTH_CHECK_INTERVAL: int = 30  # seconds
    METRICS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 9090

    # External Services
    REDIS_URL: Optional[str] = None
    SENTRY_DSN: Optional[str] = None

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate secret key strength"""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        if v == "your-secret-key-change-this-in-production-use-openssl-rand-hex-32":
            if os.getenv("ENVIRONMENT") == "production":
                raise ValueError("Default SECRET_KEY cannot be used in production")
        return v

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format"""
        if not v:
            raise ValueError("DATABASE_URL cannot be empty")
        return v

    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, v: List[str]) -> List[str]:
        """Validate CORS origins"""
        if not v:
            return ["*"]  # Allow all origins if none specified (dev only)
        return v

    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.ENVIRONMENT == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.ENVIRONMENT == Environment.PRODUCTION

    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode"""
        return self.ENVIRONMENT == Environment.TESTING or self.TESTING


# Create settings instance
settings = Settings()
