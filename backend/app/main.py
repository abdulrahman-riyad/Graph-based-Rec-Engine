# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime

from config import settings
from database import db_manager
from api.v1.endpoints import (
    health,
    recommendations,
    analytics,
    products,
    customers
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle - startup and shutdown events
    """
    # Startup
    print("🚀 Starting E-Commerce Intelligence Platform...")
    db_manager.connect()
    print("✅ Connected to Neo4j database")

    yield

    # Shutdown
    print("👋 Shutting down...")
    db_manager.close()
    print("✅ Database connection closed")


# Create FastAPI application
app = FastAPI(
    title="E-Commerce Intelligence Platform",
    description="Advanced recommendation engine and analytics for e-commerce",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(
    health.router,
    prefix="/api/v1/health",
    tags=["health"]
)

app.include_router(
    recommendations.router,
    prefix="/api/v1/recommendations",
    tags=["recommendations"]
)

app.include_router(
    analytics.router,
    prefix="/api/v1/analytics",
    tags=["analytics"]
)

app.include_router(
    products.router,
    prefix="/api/v1/products",
    tags=["products"]
)

app.include_router(
    customers.router,
    prefix="/api/v1/customers",
    tags=["customers"]
)


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint - API information
    """
    return {
        "name": "E-Commerce Intelligence Platform API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "redoc": "/redoc",
        "health": "/api/v1/health",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api")
async def api_info():
    """
    API version information
    """
    return {
        "v1": {
            "endpoints": [
                "/api/v1/health",
                "/api/v1/recommendations",
                "/api/v1/analytics",
                "/api/v1/products",
                "/api/v1/customers"
            ],
            "status": "active"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )