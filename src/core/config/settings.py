import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # Server Configuration
    HOST: str = os.getenv("HOST", "localhost")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Admin Configuration
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "admin-secret-key-12345")
    
    # Database Configuration
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "./data/chatbot_saas.db")
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./chroma")
    DATA_DIR: str = os.getenv("DATA_DIR", "./data")
    
    # File Storage Configuration
    TEMP_DIR: str = os.getenv("TEMP_DIR", "./tmp")
    STATIC_DIR: str = os.getenv("STATIC_DIR", "./static")
    
    # CORS Configuration
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    
    # Client Management Configuration
    DEFAULT_PLAN_TYPE: str = os.getenv("DEFAULT_PLAN_TYPE", "FREE")
    DEFAULT_CLIENT_STATUS: str = os.getenv("DEFAULT_CLIENT_STATUS", "ACTIVE")
    
    # RAG Configuration
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # Security Configuration
    CLIENT_ID_PREFIX: str = os.getenv("CLIENT_ID_PREFIX", "client_")
    API_KEY_PREFIX: str = os.getenv("API_KEY_PREFIX", "sk_")
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "mistral")
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "30"))
    OLLAMA_MAX_TOKENS: int = int(os.getenv("OLLAMA_MAX_TOKENS", "2048"))
    OLLAMA_TEMPERATURE: float = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
    
    @classmethod
    def get_cors_origins(cls) -> List[str]:
        """Parse CORS origins from environment variable"""
        if cls.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in cls.CORS_ORIGINS.split(",")]
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        directories = [
            cls.DATA_DIR,
            cls.TEMP_DIR,
            cls.STATIC_DIR,
            os.path.dirname(cls.CHROMA_DB_PATH),
            os.path.dirname(cls.DATABASE_PATH)
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

# Create global settings instance
settings = Settings()
