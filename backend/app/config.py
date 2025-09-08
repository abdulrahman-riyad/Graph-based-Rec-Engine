# backend/app/config.py
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # Application
    project_name: str = "E-Commerce Intelligence Platform"
    version: str = "1.0.0"
    api_v1_prefix: str = "/api/v1"

    # Neo4j Database
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "password")

    # CORS
    backend_cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]

    # Redis Cache (optional)
    redis_url: Optional[str] = os.getenv("REDIS_URL", None)
    cache_ttl: int = 3600  # Cache time-to-live in seconds

    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    access_token_expire_minutes: int = 30

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = environment == "development"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()