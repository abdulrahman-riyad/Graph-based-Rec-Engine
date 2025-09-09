# backend/app/models/schemas.py
"""
Complete Pydantic models for request/response schemas
All classes needed by endpoints are included here
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================
# Enums
# ============================================================

class RecommendationAlgorithm(str, Enum):
    HYBRID = "hybrid"
    COLLABORATIVE = "collaborative"
    CONTENT = "content"
    GRAPH = "graph"
    TRENDING = "trending"
    POPULAR = "popular"
    DIVERSITY = "diversity"


class AnalyticsTimeframe(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class CustomerSegmentEnum(str, Enum):
    CHAMPIONS = "Champions"
    LOYAL_CUSTOMERS = "Loyal Customers"
    POTENTIAL_LOYALISTS = "Potential Loyalists"
    NEW_CUSTOMERS = "New Customers"
    PROMISING = "Promising"
    NEED_ATTENTION = "Need Attention"
    ABOUT_TO_SLEEP = "About to Sleep"
    AT_RISK = "At Risk"
    CANT_LOSE_THEM = "Can't Lose Them"
    HIBERNATING = "Hibernating"
    LOST = "Lost"


# ============================================================
# Base Models
# ============================================================

class Product(BaseModel):
    """Product model"""
    sku: str
    title: str
    category: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None
    features: Optional[List[str]] = []
    rating: Optional[float] = Field(None, ge=0, le=5)
    review_count: Optional[int] = Field(None, ge=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Analytics fields
    view_count: Optional[int] = 0
    purchase_count: Optional[int] = 0
    revenue: Optional[float] = 0
    popularity_score: Optional[float] = 0
    trend: Optional[str] = "stable"  # up, down, stable

    class Config:
        json_schema_extra = {
            "example": {
                "sku": "PROD-001",
                "title": "Premium Wireless Headphones",
                "category": "Electronics",
                "brand": "AudioTech",
                "price": 199.99,
                "rating": 4.5,
                "review_count": 324
            }
        }


class Customer(BaseModel):
    """Customer model"""
    customer_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    segment: Optional[str] = None
    created_at: Optional[datetime] = None

    # Behavioral metrics
    lifetime_value: Optional[float] = Field(None, ge=0)
    purchase_count: Optional[int] = Field(None, ge=0)
    avg_order_value: Optional[float] = Field(None, ge=0)
    days_since_last_purchase: Optional[int] = None
    favorite_categories: Optional[List[str]] = []

    # RFM scores
    recency_score: Optional[int] = Field(None, ge=1, le=5)
    frequency_score: Optional[int] = Field(None, ge=1, le=5)
    monetary_score: Optional[int] = Field(None, ge=1, le=5)

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "CUST-12345",
                "email": "customer@example.com",
                "segment": "Loyal Customers",
                "lifetime_value": 2543.67,
                "purchase_count": 12
            }
        }


class Recommendation(BaseModel):
    """Recommendation model"""
    sku: str
    title: str
    category: Optional[str] = None
    price: Optional[float] = None
    score: float = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=1)
    algorithm: Optional[str] = None
    explanation: Optional[List[str]] = None

    # Additional product info
    rating: Optional[float] = None
    image_url: Optional[str] = None
    discount_percentage: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "sku": "PROD-002",
                "title": "Bluetooth Speaker",
                "category": "Electronics",
                "price": 79.99,
                "score": 0.92,
                "confidence": 0.85,
                "algorithm": "hybrid",
                "explanation": ["Frequently bought together", "Similar to your purchases"]
            }
        }


# ============================================================
# Request Models
# ============================================================

class RecommendationRequest(BaseModel):
    """Request model for recommendations"""
    customer_id: str
    algorithm: RecommendationAlgorithm = RecommendationAlgorithm.HYBRID
    limit: int = Field(10, ge=1, le=100)
    include_explanation: bool = False
    category_filter: Optional[str] = None
    price_range: Optional[Dict[str, float]] = None
    exclude_purchased: bool = True

    @validator('price_range')
    def validate_price_range(cls, v):
        if v and ('min' not in v or 'max' not in v):
            raise ValueError('price_range must contain min and max')
        if v and v['min'] > v['max']:
            raise ValueError('min price must be less than max price')
        return v


class RevenueAnalyticsRequest(BaseModel):
    """Request model for revenue analytics"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    timeframe: AnalyticsTimeframe = AnalyticsTimeframe.DAILY
    include_forecast: bool = False
    segment_by: Optional[str] = None  # category, brand, customer_segment


# ============================================================
# Response Models (THESE WERE MISSING!)
# ============================================================

class CustomerSegmentResponse(BaseModel):
    """Customer segment analytics response"""
    segment_name: str
    customer_count: int
    percentage: float
    avg_lifetime_value: float
    avg_purchase_frequency: float
    total_revenue: float
    growth_rate: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "segment_name": "Champions",
                "customer_count": 245,
                "percentage": 12.5,
                "avg_lifetime_value": 3456.78,
                "avg_purchase_frequency": 8.2,
                "total_revenue": 847411.10
            }
        }


class ProductPerformance(BaseModel):
    """Product performance analytics"""
    sku: str
    title: str
    category: str
    revenue: float
    units_sold: int
    conversion_rate: float
    avg_rating: float
    return_rate: Optional[float] = None
    profit_margin: Optional[float] = None
    trend: str  # up, down, stable

    class Config:
        json_schema_extra = {
            "example": {
                "sku": "PROD-001",
                "title": "Premium Headphones",
                "category": "Electronics",
                "revenue": 45678.90,
                "units_sold": 234,
                "conversion_rate": 0.045,
                "avg_rating": 4.5,
                "trend": "up"
            }
        }


class BasketAnalysis(BaseModel):
    """Market basket analysis results"""
    product_a: str
    product_b: str
    support: float
    confidence: float
    lift: float
    frequency: int

    class Config:
        json_schema_extra = {
            "example": {
                "product_a": "Laptop",
                "product_b": "Mouse",
                "support": 0.15,
                "confidence": 0.72,
                "lift": 2.4,
                "frequency": 156
            }
        }


class RevenueAnalytics(BaseModel):
    """Revenue analytics response"""
    total_revenue: float
    order_count: int
    avg_order_value: float
    growth_rate: float
    daily_revenue: Optional[List[Dict[str, Any]]] = None
    revenue_by_category: Optional[Dict[str, float]] = None
    revenue_by_segment: Optional[Dict[str, float]] = None
    forecast: Optional[List[Dict[str, Any]]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "total_revenue": 1234567.89,
                "order_count": 4567,
                "avg_order_value": 270.34,
                "growth_rate": 15.7,
                "daily_revenue": [
                    {"date": "2024-01-01", "revenue": 45678.90, "order_count": 123}
                ]
            }
        }


class DashboardSummary(BaseModel):
    """Dashboard summary statistics"""
    total_customers: int
    total_products: int
    total_purchases: int
    total_revenue: float

    # Time-based metrics
    revenue_30d: float
    revenue_growth_30d: float
    active_customers_30d: int
    new_customers_30d: int

    # Top performers
    top_products: Optional[List[Dict[str, Any]]] = None
    top_categories: Optional[List[Dict[str, Any]]] = None

    # System status
    database_status: str = "operational"
    last_update: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "total_customers": 10000,
                "total_products": 5000,
                "total_purchases": 100000,
                "total_revenue": 2500000.00,
                "revenue_30d": 250000.00,
                "revenue_growth_30d": 15.5,
                "active_customers_30d": 3000,
                "new_customers_30d": 500,
                "database_status": "operational",
                "last_update": "2024-01-01T12:00:00"
            }
        }


class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    database: str
    timestamp: datetime
    version: str
    node_count: Optional[int] = None
    relationship_count: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "database": "connected",
                "timestamp": "2024-01-01T12:00:00",
                "version": "1.0.0",
                "node_count": 1000000,
                "relationship_count": 5000000
            }
        }


# ============================================================
# Utility Models
# ============================================================

class PaginationParams(BaseModel):
    """Pagination parameters"""
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)
    sort_by: Optional[str] = None
    sort_order: str = Field("desc", regex="^(asc|desc)$")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class SuccessResponse(BaseModel):
    """Success response model"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# ============================================================
# Additional Response Models for Endpoints
# ============================================================

class CustomerAnalytics(BaseModel):
    """Customer analytics response"""
    customer_id: str
    total_spent: float
    order_count: int
    avg_order_value: float
    favorite_category: Optional[str] = None
    last_purchase_date: Optional[datetime] = None
    churn_probability: Optional[float] = None


class ProductRecommendationResponse(BaseModel):
    """Response for product recommendations endpoint"""
    customer_id: str
    algorithm_used: str
    recommendations: List[Recommendation]
    generated_at: datetime = Field(default_factory=datetime.now)


class SegmentationAnalysis(BaseModel):
    """Detailed segmentation analysis"""
    segments: List[CustomerSegmentResponse]
    total_customers: int
    analysis_date: datetime = Field(default_factory=datetime.now)
    insights: Optional[List[str]] = None