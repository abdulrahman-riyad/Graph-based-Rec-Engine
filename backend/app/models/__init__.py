"""
Pydantic models for request/response schemas
"""

from .schemas import (
    # Base models
    Product,
    Customer,
    Recommendation,

    # Request models
    RecommendationRequest,
    RevenueAnalyticsRequest,
    PaginationParams,

    # Response models
    CustomerSegmentResponse,
    CustomerSegmentEnum,
    ProductPerformance,
    BasketAnalysis,
    RevenueAnalytics,
    DashboardSummary,
    HealthCheck,
    ErrorResponse,
    SuccessResponse,

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
    "PaginationParams",

    # Response models
    "CustomerSegmentResponse",
    "CustomerSegmentEnum",
    "ProductPerformance",
    "BasketAnalysis",
    "RevenueAnalytics",
    "DashboardSummary",
    "HealthCheck",
    "ErrorResponse",
    "SuccessResponse",

    # Enums
    "RecommendationAlgorithm",
    "AnalyticsTimeframe"
]