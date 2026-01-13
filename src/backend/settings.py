"""Backend settings and environment configuration"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    database_url: str = Field(
        default="sqlite:///./src/data/tracker.db",
        alias="DATABASE_URL"
    )
    
    # Hashdive API
    hashdive_api_key: str = Field(default="", alias="HASHDIVE_API_KEY")
    hashdive_api_url: str = Field(
        default="https://api.hashdive.io",
        alias="HASHDIVE_API_URL"
    )
    
    # Email Configuration
    email_host: str = Field(default="smtp.gmail.com", alias="EMAIL_HOST")
    email_port: int = Field(default=587, alias="EMAIL_PORT")
    email_username: str = Field(default="", alias="EMAIL_USERNAME")
    email_password: str = Field(default="", alias="EMAIL_PASSWORD")
    email_use_tls: bool = Field(default=True, alias="EMAIL_USE_TLS")
    email_from: str = Field(default="", alias="EMAIL_FROM")
    email_to: str = Field(default="", alias="EMAIL_TO")
    
    # Poller Configuration
    poll_interval_seconds: int = Field(default=60, alias="POLL_INTERVAL_SECONDS")
    initial_lookback_days: int = Field(default=7, alias="INITIAL_LOOKBACK_DAYS")
    
    # Alert Settings
    min_trade_size_usd: float = Field(default=100.0, alias="MIN_TRADE_SIZE_USD")
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # Frontend Configuration (added this field)
    api_base_url: str = Field(default="http://localhost:8080", alias="API_BASE_URL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Added this to ignore extra fields


# Global settings instance
settings = Settings()
