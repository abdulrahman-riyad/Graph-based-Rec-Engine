# backend/app/models/__init__.py
"""
Pydantic models for request/response schemas
"""

from schemas import (
    # Base models
    Product,
    Customer,
    Recommendation,

    # Request models
    RecommendationRequest,
    RevenueAnalyticsRequest,

    # Response models
    CustomerSegment,
    ProductPerformance,
    BasketAnalysis,
    HealthCheck,

    # Enums
    RecommendationAlgorithm,
    AnalyticsTimeframe
)

__all__ = [
    # Base models
    "Product",
    "Customer",
    "Recommendation",

    # Request models
    "RecommendationRequest",
    "RevenueAnalyticsRequest",

    # Response models
    "CustomerSegment",
    "ProductPerformance",
    "BasketAnalysis",
    "HealthCheck",

    # Enums
    "RecommendationAlgorithm",
    "AnalyticsTimeframe"
]