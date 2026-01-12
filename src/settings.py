"""Settings and environment configuration"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Hashdive API
    hashdive_api_key: str = Field(default="", alias="HASHDIVE_API_KEY")
    hashdive_api_url: str = Field(
        default="https://api.hashdive.io",
        alias="HASHDIVE_API_URL"
    )
    
    # Email Configuration
    smtp_host: str = Field(default="smtp.gmail.com", alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_user: str = Field(default="", alias="SMTP_USER")
    smtp_password: str = Field(default="", alias="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(default=True, alias="SMTP_USE_TLS")
    from_email: str = Field(default="", alias="FROM_EMAIL")
    to_emails: List[str] = Field(default_factory=list, alias="TO_EMAILS")
    
    # Trade Tracking
    trade_db_path: str = Field(default="data/trades.db", alias="TRADE_DB_PATH")
    min_trade_size_usd: float = Field(default=100.0, alias="MIN_TRADE_SIZE_USD")
    
    # Alert Settings
    batch_alerts: bool = Field(default=False, alias="BATCH_ALERTS")
    batch_window_seconds: int = Field(default=300, alias="BATCH_WINDOW_SECONDS")
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
        @staticmethod
        def parse_env_var(field_name: str, raw_val: str):
            """Parse environment variables, especially for lists"""
            if field_name == 'TO_EMAILS':
                # Parse comma-separated emails
                return [email.strip() for email in raw_val.split(',') if email.strip()]
            return raw_val


# Global settings instance
settings = Settings()
