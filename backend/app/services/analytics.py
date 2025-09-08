# backend/app/services/analytics.py
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

# Fix imports
try:
    from app.database import db_manager
    from app.models.schemas import CustomerSegment, ProductPerformance, BasketAnalysis
except ImportError:
    import sys
    import os

    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from app.database import db_manager
    from app.models.schemas import CustomerSegment, ProductPerformance, BasketAnalysis

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Service for analytics and business intelligence
    """

    @staticmethod
    def get_customer_segments() -> List[CustomerSegment]:
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
                    segment = CustomerSegment(
                        segment_name=record['segment'],
                        customer_count=record['customer_count'],
                        avg_lifetime_value=round(record['avg_ltv'] or 0, 2),
                        avg_purchase_frequency=round(record['avg_frequency'] or 0, 2),
                        percentage=round(
                            (record['customer_count'] / total_customers * 100) if total_customers > 0 else 0, 2),
                        characteristics=AnalyticsService._get_segment_characteristics(record['segment'])
                    )
                    segments.append(segment)

                return segments

        except Exception as e:
            logger.error(f"Error getting customer segments: {e}")
            return []

    @staticmethod
    def _get_segment_characteristics(segment_name: str) -> Dict[str, any]:
        """
        Get characteristics and recommendations for each segment
        """
        characteristics = {
            'Champions': {
                'description': 'Best customers - recent, frequent, high-value purchases',
                'strategy': 'Reward loyalty, early access to new products',
                'risk_level': 'Low',
                'potential': 'High'
            },
            'Loyal Customers': {
                'description': 'Consistent purchasers with good value',
                'strategy': 'Upsell higher value products, ask for reviews',
                'risk_level': 'Low',
                'potential': 'Medium-High'
            },
            'New Customers': {
                'description': 'Recently acquired customers',
                'strategy': 'Provide onboarding support, build relationship',
                'risk_level': 'Medium',
                'potential': 'High'
            },
            'At Risk': {
                'description': 'Previously good customers showing signs of churn',
                'strategy': 'Reconnection campaigns, special offers',
                'risk_level': 'High',
                'potential': 'Medium'
            },
            'Cant Lose Them': {
                'description': 'High-value customers who haven\'t purchased recently',
                'strategy': 'Win-back campaigns, personalized offers',
                'risk_level': 'Very High',
                'potential': 'High'
            },
            'Lost': {
                'description': 'Haven\'t purchased in a long time',
                'strategy': 'Reactivation campaigns, surveys',
                'risk_level': 'Lost',
                'potential': 'Low'
            },
            'Regular': {
                'description': 'Average purchase behavior',
                'strategy': 'General marketing, increase frequency',
                'risk_level': 'Medium',
                'potential': 'Medium'
            }
        }

        return characteristics.get(segment_name, {
            'description': 'Standard customer segment',
            'strategy': 'Standard marketing approach',
            'risk_level': 'Medium',
            'potential': 'Medium'
        })

    @staticmethod
    def get_revenue_analytics(start_date: datetime, end_date: datetime) -> Dict:
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

                return {
                    'period': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    },
                    'summary': {
                        'total_revenue': round(daily_result['total_revenue'] or 0, 2),
                        'avg_daily_revenue': round(daily_result['avg_daily_revenue'] or 0, 2),
                        'trend': trend
                    },
                    'daily_breakdown': {
                        'dates': [d.isoformat() if d else None for d in (daily_result['dates'] or [])],
                        'revenues': daily_result['revenues'] or [],
                        'customers': daily_result['customers'] or [],
                        'orders': daily_result['orders'] or []
                    },
                    'category_breakdown': category_result['category_breakdown'] if category_result else []
                }

        except Exception as e:
            logger.error(f"Error getting revenue analytics: {e}")
            return {
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'summary': {
                    'total_revenue': 0,
                    'avg_daily_revenue': 0,
                    'trend': 'unknown'
                },
                'daily_breakdown': {
                    'dates': [],
                    'revenues': [],
                    'customers': [],
                    'orders': []
                },
                'category_breakdown': []
            }

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
                        item1=record['item1'] or 'Unknown',
                        item2=record['item2'] or 'Unknown',
                        support=round(record['support'], 4),
                        confidence=round(record['confidence'], 4),
                        lift=round(record['lift'], 2),
                        transaction_count=record['support_count']
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

                # Get cross-sell opportunities
                cross_sell_query = """
                    MATCH (p:Product {sku: $sku})<-[:PURCHASED]-(c:Customer)-[:PURCHASED]->(other:Product)
                    WHERE p <> other
                    WITH other, count(distinct c) as co_purchase_count
                    ORDER BY co_purchase_count DESC
                    LIMIT 5
                    RETURN collect(other) as cross_sell_products
                """

                cross_sell_result = session.run(cross_sell_query, sku=product_sku).single()

                # Determine trend (simplified)
                trend = 'stable'
                # In production, you would calculate actual trend from time-series data

                product_data = result['product']

                # Create Product object from data
                from app.models.schemas import Product
                product = Product(
                    sku=product_data['sku'],
                    title=product_data.get('title'),
                    price=product_data.get('price'),
                    category=product_data.get('category'),
                    brand=product_data.get('brand'),
                    rating=product_data.get('rating')
                )

                # Create cross-sell product list
                cross_sell_products = []
                if cross_sell_result and cross_sell_result['cross_sell_products']:
                    for p in cross_sell_result['cross_sell_products'][:5]:
                        cross_sell_products.append(Product(
                            sku=p['sku'],
                            title=p.get('title'),
                            price=p.get('price'),
                            category=p.get('category'),
                            brand=p.get('brand')
                        ))

                return ProductPerformance(
                    product=product,
                    revenue=round(result['revenue'] or 0, 2),
                    units_sold=result['units_sold'] or 0,
                    unique_customers=result['unique_customers'] or 0,
                    trend=trend,
                    cross_sell_opportunities=cross_sell_products,
                    competitive_position={'market_share': 0.1}  # Placeholder
                )

        except Exception as e:
            logger.error(f"Error getting product performance: {e}")
            return None