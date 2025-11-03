"""Settings and environment configuration"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="polymarket_anomaly", alias="POSTGRES_DB")
    postgres_user: str = Field(default="postgres", alias="POSTGRES_USER")
    postgres_password: str = Field(default="changeme", alias="POSTGRES_PASSWORD")
    
    # MinIO
    minio_endpoint: str = Field(default="localhost:9000", alias="MINIO_ENDPOINT")
    minio_access_key: str = Field(default="minioadmin", alias="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(default="minioadmin", alias="MINIO_SECRET_KEY")
    minio_bucket: str = Field(default="polymarket-data", alias="MINIO_BUCKET")
    
    # API
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8080, alias="API_PORT")
    
    # PolyMarket
    polymarket_api_url: str = Field(
        default="https://gamma-api.polymarket.com",
        alias="POLYMARKET_API_URL"
    )
    polymarket_subgraph_url: str = Field(
        default="https://api.thegraph.com/subgraphs/name/polymarket/polymarket",
        alias="POLYMARKET_SUBGRAPH_URL"
    )
    
    # Polygon
    polygon_rpc_url: str = Field(
        default="https://polygon-rpc.com",
        alias="POLYGON_RPC_URL"
    )
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
