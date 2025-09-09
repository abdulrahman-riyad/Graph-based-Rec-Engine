# backend/app/services/__init__.py
"""
Service layer for business logic
"""

from .recommendations import RecommendationService
from .analytics import AnalyticsService
from .products import ProductService
from .customers import CustomerService

# Import advanced if available
try:
    from .advanced_recommendations import AdvancedRecommendationEngine
    __all__ = [
        "RecommendationService",
        "AnalyticsService",
        "ProductService",
        "CustomerService",
        "AdvancedRecommendationEngine"
    ]
except ImportError:
    __all__ = [
        "RecommendationService",
        "AnalyticsService",
        "ProductService",
        "CustomerService"
    ]