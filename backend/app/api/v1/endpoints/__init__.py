# backend/app/api/v1/endpoints/__init__.py
"""
API v1 endpoints
"""

from . import health
from . import recommendations
from . import analytics
from . import products
from . import customers

__all__ = [
    "health",
    "recommendations",
    "analytics",
    "products",
    "customers"
]