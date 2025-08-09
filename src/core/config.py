"""
Configuration management for the ChatBot SaaS application
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    
    # Admin Configuration
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "admin-secret-key-12345")
    
    # Database Configuration
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./chroma")
    DATA_DIR: str = os.getenv("DATA_DIR", "./data")
    
    # File Storage
    TEMP_DIR: str = os.getenv("TEMP_DIR", "./tmp")
    STATIC_DIR: str = os.getenv("STATIC_DIR", "./static")
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # Client Management
    DEFAULT_PLAN: str = os.getenv("DEFAULT_PLAN", "free")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB default
    
    # RAG Configuration
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Security
    API_KEY_PREFIX: str = os.getenv("API_KEY_PREFIX", "cb_")
    CLIENT_ID_PREFIX: str = os.getenv("CLIENT_ID_PREFIX", "client_")
    
    # Logging
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    @classmethod
    def get_cors_origins(cls) -> List[str]:
        """Get CORS origins, handling wildcard"""
        if "*" in cls.ALLOWED_ORIGINS:
            return ["*"]
        return cls.ALLOWED_ORIGINS
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories"""
        directories = [
            cls.CHROMA_DB_PATH,
            cls.DATA_DIR,
            cls.TEMP_DIR,
            cls.STATIC_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

# Global settings instance
settings = Settings()
