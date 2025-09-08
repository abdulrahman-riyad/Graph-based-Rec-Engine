# backend/app/api/v1/endpoints/analytics.py
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta

# Fix import paths
import sys
import os

# Get the backend directory (4 levels up from this file)
current_file = os.path.abspath(__file__)
endpoints_dir = os.path.dirname(current_file)  # endpoints
v1_dir = os.path.dirname(endpoints_dir)  # v1
api_dir = os.path.dirname(v1_dir)  # api
app_dir = os.path.dirname(api_dir)  # app
backend_dir = os.path.dirname(app_dir)  # backend

# Add to path if needed
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.models.schemas import (
    RevenueAnalyticsRequest,
    CustomerSegment,
    ProductPerformance,
    BasketAnalysis
)
from app.services.analytics import AnalyticsService

router = APIRouter()


@router.get("/customer-segments", response_model=List[CustomerSegment])
async def get_customer_segments():
    """
    Get customer segmentation using RFM analysis

    Returns segments like Champions, Loyal Customers, At Risk, etc.
    """
    try:
        return AnalyticsService.get_customer_segments()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/revenue")
async def get_revenue_analytics(request: RevenueAnalyticsRequest):
    """
    Get revenue analytics for a specified time period

    - **start_date**: Start date for analysis (defaults to 30 days ago)
    - **end_date**: End date for analysis (defaults to today)
    - **timeframe**: Granularity of data (daily, weekly, monthly)
    - **include_forecast**: Whether to include revenue forecast
    """
    try:
        start_date = request.start_date or datetime.now() - timedelta(days=30)
        end_date = request.end_date or datetime.now()

        return AnalyticsService.get_revenue_analytics(start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/basket-analysis", response_model=List[BasketAnalysis])
async def get_basket_analysis(
        min_support: float = Query(default=0.01, ge=0.001, le=1.0, description="Minimum support threshold"),
        min_confidence: float = Query(default=0.1, ge=0.01, le=1.0, description="Minimum confidence threshold"),
        limit: int = Query(default=20, ge=1, le=100, description="Maximum number of rules to return")
):
    """
    Get market basket analysis and association rules

    Identifies products frequently bought together
    """
    try:
        rules = AnalyticsService.get_basket_analysis(min_support, min_confidence)
        return rules[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/product/{product_sku}/performance")
async def get_product_performance(product_sku: str):
    """
    Get comprehensive performance metrics for a specific product
    """
    try:
        performance = AnalyticsService.get_product_performance(product_sku)
        if not performance:
            raise HTTPException(status_code=404, detail="Product not found")
        return performance
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard-summary")
async def get_dashboard_summary():
    """
    Get summary statistics for the main dashboard
    """
    try:
        from app.database import db_manager

        with db_manager.get_session() as session:
            # Get overall statistics
            stats = session.run("""
                MATCH (c:Customer)
                WITH count(c) as total_customers
                MATCH (p:Product)
                WITH total_customers, count(p) as total_products
                OPTIONAL MATCH ()-[r:PURCHASED]->()
                WITH total_customers, total_products, count(r) as total_purchases

                // Get 30-day metrics
                OPTIONAL MATCH (c:Customer)-[r2:PURCHASED]->(p:Product)
                WHERE r2.purchase_date > datetime() - duration('P30D')
                WITH total_customers, total_products, total_purchases,
                     count(distinct c) as active_customers,
                     sum(COALESCE(r2.quantity, 1) * COALESCE(r2.price, p.price, 0)) as revenue_30d

                RETURN total_customers, 
                       total_products, 
                       total_purchases,
                       active_customers,
                       revenue_30d
            """).single()

            # Get trend data
            trend = session.run("""
                MATCH (c:Customer)-[r:PURCHASED]->(p:Product)
                WHERE r.purchase_date > datetime() - duration('P7D')
                RETURN count(r) as recent_orders
            """).single()

            return {
                'total_customers': stats['total_customers'] if stats else 0,
                'total_products': stats['total_products'] if stats else 0,
                'total_purchases': stats['total_purchases'] if stats else 0,
                'active_customers_30d': stats['active_customers'] if stats else 0,
                'revenue_30d': round(stats['revenue_30d'], 2) if stats and stats['revenue_30d'] else 0,
                'recent_orders_7d': trend['recent_orders'] if trend else 0,
                'timestamp': datetime.now().isoformat()
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversion-funnel")
async def get_conversion_funnel(
        days: int = Query(default=30, ge=1, le=90, description="Look back period in days")
):
    """
    Get conversion funnel analytics
    """
    try:
        from app.database import db_manager

        with db_manager.get_session() as session:
            result = session.run("""
                // This would require session/event data
                // Simplified version
                MATCH (c:Customer)
                OPTIONAL MATCH (c)-[r:PURCHASED]->()
                WHERE r.purchase_date > datetime() - duration({days: $days})
                WITH count(distinct c) as total_customers,
                     count(distinct CASE WHEN r IS NOT NULL THEN c END) as purchasers

                RETURN total_customers,
                       purchasers,
                       CASE WHEN total_customers > 0 
                            THEN purchasers * 100.0 / total_customers 
                            ELSE 0 END as conversion_rate
            """, days=f"P{days}D").single()

            return {
                'total_customers': result['total_customers'] if result else 0,
                'purchasers': result['purchasers'] if result else 0,
                'conversion_rate': round(result['conversion_rate'], 2) if result else 0,
                'period_days': days
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))