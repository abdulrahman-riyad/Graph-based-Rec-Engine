"""
Main entry point for running the FastAPI application
"""

import uvicorn
import sys
import os

# Add the current directory to Python path to ensure proper imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings


def main():
    """
    Run the FastAPI application with Uvicorn
    """
    # Configure Uvicorn
    config = {
        "app": "app.main:app",
        "host": settings.host or "0.0.0.0",
        "port": settings.port or 8000,
        "reload": settings.debug,
        "log_level": settings.log_level.lower(),
        "access_log": True,
    }

    # Add SSL in production
    if settings.environment == "production":
        config.update({
            "ssl_keyfile": os.getenv("SSL_KEYFILE", "/path/to/keyfile.key"),
            "ssl_certfile": os.getenv("SSL_CERTFILE", "/path/to/certfile.crt"),
            "workers": int(os.getenv("UVICORN_WORKERS", 4))
        })

    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     E-COMMERCE INTELLIGENCE PLATFORM                        ║
    ║     Advanced Recommendation Engine & Analytics              ║
    ║                                                              ║
    ║     Version: {settings.version:16}                   ║
    ║     Environment: {settings.environment.upper():12}                   ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝

    🚀 Starting server at http://{config['host']}:{config['port']}
    📚 Documentation at http://{config['host']}:{config['port']}/docs
    🔧 Alternative docs at http://{config['host']}:{config['port']}/redoc
    🔗 Neo4j: {settings.neo4j_uri}

    Press CTRL+C to stop the server
    """)

    # Run the server
    uvicorn.run(**config)


if __name__ == "__main__":
    main()