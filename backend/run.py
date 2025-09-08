# backend/run.py
"""
Main entry point for running the FastAPI application
"""

import uvicorn
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings


def main():
    """
    Run the FastAPI application with Uvicorn
    """
    # Configure Uvicorn
    config = {
        "app": "app.main:app",
        "host": "0.0.0.0",
        "port": 8000,
        "reload": settings.debug,
        "log_level": settings.log_level.lower(),
        "access_log": True,
    }

    # Add SSL in production
    if settings.environment == "production":
        config.update({
            "ssl_keyfile": "/path/to/keyfile.key",
            "ssl_certfile": "/path/to/certfile.crt",
            "workers": 4
        })

    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     E-COMMERCE INTELLIGENCE PLATFORM                        ║
    ║     Advanced Recommendation Engine & Analytics              ║
    ║                                                              ║
    ║     Version: {settings.version}                                        ║
    ║     Environment: {settings.environment.upper()}                           ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝

    🚀 Starting server at http://localhost:8000
    📚 Documentation at http://localhost:8000/docs
    🔧 Alternative docs at http://localhost:8000/redoc

    Press CTRL+C to stop the server
    """)

    # Run the server
    uvicorn.run(**config)


if __name__ == "__main__":
    main()