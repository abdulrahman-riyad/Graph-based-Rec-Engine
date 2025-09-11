import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from ..database import db_manager
from ..models.schemas import CustomerSegmentResponse, ProductPerformance, BasketAnalysis, RevenueAnalytics

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Service for analytics and business intelligence
    """

    @staticmethod
    def get_customer_segments() -> List[CustomerSegmentResponse]:
        """
        Perform customer segmentation using RFM analysis
        """
        try:
            with db_manager.get_session() as session:
                query = """
                    MATCH (c:Customer)-[r:PURCHASED]->(p:Product)
                    WITH c,
                         count(r) as frequency,
                         max(r.purchase_date) as last_purchase,
                         sum(COALESCE(r.quantity, 1) * COALESCE(r.price, p.price, 0)) as monetary_value

                    // Calculate recency in days
                    WITH c, frequency, monetary_value,
                         duration.between(last_purchase, datetime()).days as recency_days
                    WHERE recency_days IS NOT NULL

                    // Assign segments based on RFM scores
                    WITH CASE
                        WHEN recency_days <= 30 AND frequency >= 10 AND monetary_value >= 500 
                            THEN 'Champions'
                        WHEN recency_days <= 60 AND frequency >= 5 AND monetary_value >= 200 
                            THEN 'Loyal Customers'
                        WHEN recency_days <= 90 AND frequency <= 2 
                            THEN 'New Customers'
                        WHEN recency_days > 90 AND recency_days <= 180 AND frequency >= 5 
                            THEN 'At Risk'
                        WHEN recency_days > 180 AND frequency >= 5 
                            THEN 'Cant Lose Them'
                        WHEN recency_days > 180 
                            THEN 'Lost'
                        ELSE 'Regular'
                    END as segment,
                    count(c) as customer_count,
                    avg(monetary_value) as avg_ltv,
                    avg(frequency) as avg_frequency

                    RETURN segment, customer_count, avg_ltv, avg_frequency
                    ORDER BY customer_count DESC
                """

                result = session.run(query)

                segments = []
                total_customers = 0

                # First pass to get total
                records = list(result)
                for record in records:
                    total_customers += record['customer_count']

                # Create segment objects
                for record in records:
                    segment = CustomerSegmentResponse(
                        segment_name=record['segment'],
                        customer_count=record['customer_count'],
                        avg_lifetime_value=round(record['avg_ltv'] or 0, 2),
                        avg_purchase_frequency=round(record['avg_frequency'] or 0, 2),
                        percentage=round(
                            (record['customer_count'] / total_customers * 100) if total_customers > 0 else 0, 2),
                        total_revenue=round((record['avg_ltv'] or 0) * (record['customer_count'] or 0), 2),
                        growth_rate=0.0  # This would be calculated in a real implementation
                    )
                    segments.append(segment)

                return segments

        except Exception as e:
            logger.error(f"Error getting customer segments: {e}")
            return []

    @staticmethod
    def get_revenue_analytics(start_date: datetime, end_date: datetime) -> RevenueAnalytics:
        """
        Get revenue analytics for a time period
        """
        try:
            with db_manager.get_session() as session:
                # Daily revenue breakdown
                daily_query = """
                    MATCH (c:Customer)-[r:PURCHASED]->(p:Product)
                    WHERE r.purchase_date >= $start_date 
                      AND r.purchase_date <= $end_date
                    WITH date(r.purchase_date) as purchase_date,
                         sum(COALESCE(r.quantity, 1) * COALESCE(r.price, p.price, 0)) as daily_revenue,
                         count(distinct c) as daily_customers,
                         count(r) as daily_orders
                    ORDER BY purchase_date
                    RETURN collect(purchase_date) as dates,
                           collect(daily_revenue) as revenues,
                           collect(daily_customers) as customers,
                           collect(daily_orders) as orders,
                           sum(daily_revenue) as total_revenue,
                           avg(daily_revenue) as avg_daily_revenue
                """

                daily_result = session.run(
                    daily_query,
                    start_date=start_date.isoformat(),
                    end_date=end_date.isoformat()
                ).single()

                # Category breakdown
                category_query = """
                    MATCH (c:Customer)-[r:PURCHASED]->(p:Product)
                    WHERE r.purchase_date >= $start_date 
                      AND r.purchase_date <= $end_date
                      AND p.category IS NOT NULL
                    WITH p.category as category,
                         sum(COALESCE(r.quantity, 1) * COALESCE(r.price, p.price, 0)) as category_revenue,
                         count(distinct c) as category_customers
                    ORDER BY category_revenue DESC
                    RETURN collect({
                        category: category,
                        revenue: category_revenue,
                        customers: category_customers
                    }) as category_breakdown
                """

                category_result = session.run(
                    category_query,
                    start_date=start_date.isoformat(),
                    end_date=end_date.isoformat()
                ).single()

                # Determine trend
                trend = 'stable'
                if daily_result and daily_result['revenues']:
                    revenues = daily_result['revenues']
                    if len(revenues) > 1:
                        first_half = sum(revenues[:len(revenues) // 2])
                        second_half = sum(revenues[len(revenues) // 2:])
                        if second_half > first_half * 1.1:
                            trend = 'increasing'
                        elif second_half < first_half * 0.9:
                            trend = 'decreasing'

                # Format daily breakdown
                daily_breakdown = []
                if daily_result and daily_result['dates']:
                    for i, date in enumerate(daily_result['dates']):
                        daily_breakdown.append({
                            'date': date.isoformat() if date else None,
                            'revenue': daily_result['revenues'][i] if i < len(daily_result['revenues']) else 0,
                            'customers': daily_result['customers'][i] if i < len(daily_result['customers']) else 0,
                            'orders': daily_result['orders'][i] if i < len(daily_result['orders']) else 0
                        })

                # Format category breakdown
                revenue_by_category = {}
                if category_result and category_result['category_breakdown']:
                    for item in category_result['category_breakdown']:
                        revenue_by_category[item['category']] = item['revenue']

                return RevenueAnalytics(
                    total_revenue=round(daily_result['total_revenue'] or 0, 2),
                    order_count=sum(daily_result['orders'] or [0]),
                    avg_order_value=round(daily_result['avg_daily_revenue'] or 0, 2),
                    growth_rate=0.0,  # This would be calculated in a real implementation
                    daily_revenue=daily_breakdown,
                    revenue_by_category=revenue_by_category,
                    revenue_by_segment=None,  # This would be calculated in a real implementation
                    forecast=None  # This would be calculated in a real implementation
                )

        except Exception as e:
            logger.error(f"Error getting revenue analytics: {e}")
            return RevenueAnalytics(
                total_revenue=0,
                order_count=0,
                avg_order_value=0,
                growth_rate=0,
                daily_revenue=[],
                revenue_by_category={},
                revenue_by_segment=None,
                forecast=None
            )

    @staticmethod
    def get_basket_analysis(min_support: float = 0.01, min_confidence: float = 0.1) -> List[BasketAnalysis]:
        """
        Perform market basket analysis
        """
        try:
            with db_manager.get_session() as session:
                query = """
                    // Find product pairs frequently bought together
                    MATCH (p1:Product)<-[:PURCHASED]-(c:Customer)-[:PURCHASED]->(p2:Product)
                    WHERE id(p1) < id(p2)  // Avoid duplicates
                    WITH p1, p2, count(distinct c) as support_count

                    // Get total customers for support calculation
                    MATCH (c:Customer)
                    WITH p1, p2, support_count, count(distinct c) as total_customers

                    // Calculate support
                    WITH p1, p2, 
                         support_count,
                         support_count * 1.0 / total_customers as support
                    WHERE support > $min_support

                    // Calculate confidence
                    MATCH (c1:Customer)-[:PURCHASED]->(p1)
                    WITH p1, p2, support_count, support, count(distinct c1) as p1_count

                    WITH p1.title as item1,
                         p2.title as item2,
                         support,
                         support_count * 1.0 / p1_count as confidence,
                         support_count,
                         support / ((p1_count * 1.0 / support_count) * 0.01) as lift
                    WHERE confidence > $min_confidence

                    RETURN item1, item2, support, confidence, lift, support_count
                    ORDER BY lift DESC
                    LIMIT 50
                """

                result = session.run(
                    query,
                    min_support=min_support,
                    min_confidence=min_confidence
                )

                rules = []
                for record in result:
                    rule = BasketAnalysis(
                        product_a=record['item1'] or 'Unknown',
                        product_b=record['item2'] or 'Unknown',
                        support=round(record['support'], 4),
                        confidence=round(record['confidence'], 4),
                        lift=round(record['lift'], 2),
                        frequency=record['support_count']
                    )
                    rules.append(rule)

                return rules

        except Exception as e:
            logger.error(f"Error performing basket analysis: {e}")
            return []

    @staticmethod
    def get_product_performance(product_sku: str) -> Optional[ProductPerformance]:
        """
        Get comprehensive performance metrics for a product
        """
        try:
            with db_manager.get_session() as session:
                # Get basic metrics
                metrics_query = """
                    MATCH (p:Product {sku: $sku})
                    OPTIONAL MATCH (p)<-[r:PURCHASED]-(c:Customer)
                    WITH p,
                         count(distinct c) as unique_customers,
                         count(r) as total_orders,
                         sum(COALESCE(r.quantity, 1)) as units_sold,
                         sum(COALESCE(r.quantity, 1) * COALESCE(r.price, p.price, 0)) as revenue
                    RETURN p as product,
                           unique_customers,
                           total_orders,
                           units_sold,
                           revenue
                """

                result = session.run(metrics_query, sku=product_sku).single()

                if not result or not result['product']:
                    return None

                product_data = result['product']

                # Determine trend (simplified)
                trend = 'stable'

                return ProductPerformance(
                    sku=product_data['sku'],
                    title=product_data.get('title', 'Unknown'),
                    category=product_data.get('category', 'Unknown'),
                    revenue=round(result['revenue'] or 0, 2),
                    units_sold=result['units_sold'] or 0,
                    conversion_rate=0.0,  # This would be calculated in a real implementation
                    avg_rating=0.0,  # This would be calculated in a real implementation
                    return_rate=0.0,  # This would be calculated in a real implementation
                    profit_margin=0.0,  # This would be calculated in a real implementation
                    trend=trend
                )

        except Exception as e:
            logger.error(f"Error getting product performance: {e}")
            return None