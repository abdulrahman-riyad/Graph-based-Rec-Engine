# backend/app/models/schemas.py
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class RecommendationAlgorithm(str, Enum):
    """Available recommendation algorithms"""
    hybrid = "hybrid"
    collaborative = "collaborative"
    content = "content"
    graph = "graph"
    trending = "trending"
    diversity = "diversity"


class AnalyticsTimeframe(str, Enum):
    """Analytics timeframe options"""
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    quarterly = "quarterly"
    yearly = "yearly"


# Base Models
class Product(BaseModel):
    """Product model"""
    model_config = ConfigDict(from_attributes=True)

    sku: str
    title: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    category: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    review_count: Optional[int] = Field(None, ge=0)
    popularity_score: Optional[float] = None
    overall_score: Optional[float] = None


class Customer(BaseModel):
    """Customer model"""
    model_config = ConfigDict(from_attributes=True)

    customer_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    country: Optional[str] = None
    segment: Optional[str] = None
    lifetime_value: Optional[float] = Field(None, ge=0)
    purchase_count: Optional[int] = Field(None, ge=0)
    avg_order_value: Optional[float] = Field(None, ge=0)
    last_purchase_date: Optional[datetime] = None
    churn_risk: Optional[str] = None
    created_at: Optional[datetime] = None


class Recommendation(Product):
    """Recommendation model extending Product"""
    score: float = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=1)
    explanation: Optional[List[str]] = None
    algorithm_used: Optional[str] = None


# Request Models
class RecommendationRequest(BaseModel):
    """Request model for recommendations"""
    customer_id: str
    algorithm: RecommendationAlgorithm = RecommendationAlgorithm.hybrid
    limit: int = Field(default=10, ge=1, le=100)
    include_explanation: bool = False
    filters: Optional[Dict[str, Any]] = None
    exclude_purchased: bool = True
    category_filter: Optional[str] = None
    price_range: Optional[Dict[str, float]] = None


class RevenueAnalyticsRequest(BaseModel):
    """Request model for revenue analytics"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    timeframe: AnalyticsTimeframe = AnalyticsTimeframe.daily
    include_forecast: bool = False
    compare_period: bool = False
    group_by: Optional[str] = None


# Response Models
class CustomerSegment(BaseModel):
    """Customer segment model"""
    segment_name: str
    customer_count: int
    avg_lifetime_value: float
    avg_purchase_frequency: float
    characteristics: Dict[str, Any]
    percentage: Optional[float] = None


class ProductPerformance(BaseModel):
    """Product performance metrics model"""
    product: Product
    revenue: float
    units_sold: int
    unique_customers: int
    conversion_rate: Optional[float] = None
    trend: str  # "increasing", "decreasing", "stable"
    trend_percentage: Optional[float] = None
    cross_sell_opportunities: List[Product]
    competitive_position: Dict[str, Any]


class BasketAnalysis(BaseModel):
    """Market basket analysis model"""
    item1: str
    item2: str
    support: float = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=1)
    lift: float = Field(..., ge=0)
    transaction_count: Optional[int] = None


class HealthCheck(BaseModel):
    """Health check response model"""
    status: str  # "healthy", "unhealthy", "degraded"
    database: str
    timestamp: datetime
    node_count: Optional[int] = None
    relationship_count: Optional[int] = None
    version: str = "1.0.0"
    uptime: Optional[float] = None


# Analytics Models
class DashboardSummary(BaseModel):
    """Dashboard summary statistics"""
    total_customers: int
    total_products: int
    total_purchases: int
    active_customers_30d: int
    revenue_30d: float
    recent_orders_7d: int
    conversion_rate: Optional[float] = None
    avg_order_value: Optional[float] = None
    timestamp: datetime


class RevenueAnalytics(BaseModel):
    """Revenue analytics response"""
    period: Dict[str, datetime]
    summary: Dict[str, float]
    daily_breakdown: Dict[str, List]
    category_breakdown: Optional[List[Dict]] = None
    trend: str
    forecast: Optional[Dict[str, Any]] = None


class CustomerAnalytics(BaseModel):
    """Customer analytics response"""
    customer_id: str
    lifetime_value: float
    total_purchases: int
    unique_products: int
    avg_order_value: float
    days_since_last_purchase: Optional[int] = None
    predicted_churn_probability: Optional[float] = None
    recommended_actions: Optional[List[str]] = None


# Pagination Models
class PaginationParams(BaseModel):
    """Pagination parameters"""
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    sort_by: Optional[str] = None
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: List[Any]
    total: int
    limit: int
    offset: int
    has_more: bool


# Error Models
class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)