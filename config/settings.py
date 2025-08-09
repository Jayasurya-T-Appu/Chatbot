"""
Configuration settings for ChatBot Plugin
"""

import os
from typing import Dict, Any

# API Configuration
API_TITLE = "RAG Chatbot API"
API_VERSION = "1.0.0"
API_HOST = "0.0.0.0"
API_PORT = 8000

# CORS Configuration
CORS_ORIGINS = ["*"]
CORS_CREDENTIALS = True
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]

# File Upload Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = [".pdf", ".txt", ".doc", ".docx"]
TEMP_DIR = "./tmp"

# ChromaDB Configuration
CHROMA_PATH = "./chroma"

# Ollama Configuration
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "mistral"
OLLAMA_TIMEOUT = 15

# API Keys (in production, use environment variables)
API_KEYS: Dict[str, str] = {
    'demo-api-key': 'demo-client',
    'test-api-key': 'test_client'
}

# Widget Configuration
WIDGET_DEFAULT_CONFIG: Dict[str, Any] = {
    'theme': 'light',
    'position': 'bottom-right',
    'title': 'Chat with us',
    'placeholder': 'Type your message...',
    'welcomeMessage': 'Hello! How can I help you today?',
    'primaryColor': '#007bff',
    'fontSize': '14px',
    'zIndex': 9999
}

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Performance Configuration
BATCH_SIZE = 32
MAX_CHUNK_SIZE = 1000
MIN_CHUNK_SIZE = 100
