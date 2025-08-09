#!/usr/bin/env python3
"""
ChatBot Plugin - Main Entry Point
"""

import uvicorn
from src.api.app import app
from src.core.config import settings

def main():
    """Main entry point for the application"""
    # Create necessary directories
    settings.create_directories()
    
    uvicorn.run(
        "src.api.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL
    )

if __name__ == "__main__":
    main()
