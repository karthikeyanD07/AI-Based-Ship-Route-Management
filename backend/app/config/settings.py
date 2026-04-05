"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Server Configuration
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:8000"
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/ship_route_db"
    DATABASE_ECHO: bool = False
    
    # Redis Configuration (optional, for distributed state)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API Keys
    OPENWEATHER_API_KEY: str = ""
    MARINE_TRAFFIC_API_KEY: str = ""
    
    # Security
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Application Settings
    MAX_SHIPS_DISPLAY: int = 500
    SHIP_UPDATE_INTERVAL: int = 3
    CSV_DATA_FILE: str = "final_ship_routes.csv"
    
    # WebSocket Settings
    MAX_WEBSOCKET_CONNECTIONS: int = 1000
    
    # Cache Settings
    CACHE_MAX_SIZE: int = 1000
    CACHE_DEFAULT_TTL: int = 300
    
    # Circuit Breaker Settings
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: int = 60
    
    # Database Retry Settings
    DB_RETRY_MAX_ATTEMPTS: int = 3
    DB_RETRY_INITIAL_DELAY: float = 1.0
    DB_RETRY_MAX_DELAY: float = 60.0
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
