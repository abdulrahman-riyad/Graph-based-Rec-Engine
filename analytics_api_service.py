"""
analytics_api_service.py
Complete analytics engine and API service for e-commerce insights
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from scipy import stats

load_dotenv()

app = FastAPI(title="E-Commerce Analytics & Recommendation API", version="1.0.0")

# Enable CORS for Shopify integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
class DatabaseConnection:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        self.driver.close()

db = DatabaseConnection()

# Pydantic models
class RecommendationRequest(BaseModel):
    customer_id: str
    algorithm: Optional[str] = "hybrid"
    limit: Optional[int] = 10
    include_explanation: Optional[bool] = False

class SessionEvent(BaseModel):
    event_type: str
    product_sku: str
    timestamp: datetime

class AnalyticsRequest(BaseModel):
    metric_type: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    granularity: Optional[str] = "daily"

class ProductAnalytics(BaseModel):
    product_sku: str
    include_forecast: Optional[bool] = False

# Analytics Engine
class AnalyticsEngine:
    def __init__(self, driver):
        self.driver = driver

    def customer_segmentation(self) -> Dict:
        """Advanced customer segmentation using RFM analysis"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (c:Customer)-[r:PURCHASED]->(p:Product)
                WITH c,
                     count(r) as frequency,
                     max(r.purchase_date) as last_purchase,
                     sum(r.quantity * r.price) as monetary_value
                
                WITH c, frequency, last_purchase, monetary_value,
                     duration.between(last_purchase, datetime()).days as recency_days
                
                // Calculate RFM scores
                WITH c,
                     CASE 
                         WHEN recency_days <= 30 THEN 5
                         WHEN recency_days <= 60 THEN 4
                         WHEN recency_days <= 90 THEN 3
                         WHEN recency_days <= 180 THEN 2
                         ELSE 1
                     END as recency_score,
                     CASE
                         WHEN frequency >= 50 THEN 5
                         WHEN frequency >= 20 THEN 4
                         WHEN frequency >= 10 THEN 3
                         WHEN frequency >= 5 THEN 2
                         ELSE 1
                     END as frequency_score,
                     CASE
                         WHEN monetary_value >= 1000 THEN 5
                         WHEN monetary_value >= 500 THEN 4
                         WHEN monetary_value >= 200 THEN 3
                         WHEN monetary_value >= 100 THEN 2
                         ELSE 1
                     END as monetary_score
                
                // Segment customers
                WITH 
                    CASE
                        WHEN recency_score >= 4 AND frequency_score >= 4 AND monetary_score >= 4 THEN 'Champions'
                        WHEN recency_score >= 3 AND frequency_score >= 3 AND monetary_score >= 3 THEN 'Loyal Customers'
                        WHEN recency_score >= 3 AND frequency_score <= 2 THEN 'New Customers'
                        WHEN recency_score <= 2 AND frequency_score >= 3 THEN 'At Risk'
                        WHEN recency_score <= 2 AND frequency_score <= 2 AND monetary_score >= 3 THEN 'Cant Lose Them'
                        ELSE 'Need Attention'
                    END as segment,
                    count(c) as customer_count
                
                RETURN segment, customer_count
                ORDER BY customer_count DESC
            """)

            segments = {record['segment']: record['customer_count'] for record in result}

            return {
                'segments': segments,
                'total_customers': sum(segments.values()),
                'timestamp': datetime.now().isoformat()
            }

    def product_performance_metrics(self, product_sku: str) -> Dict:
        """Comprehensive product performance analytics"""
        with self.driver.session() as session:
            # Basic metrics
            basic_metrics = session.run("""
                MATCH (p:Product {sku: $sku})
                OPTIONAL MATCH (p)<-[r:PURCHASED]-(c:Customer)
                OPTIONAL MATCH (p)<-[:ABOUT]-(rev:Review)
                
                WITH p,
                     count(distinct c) as unique_customers,
                     count(r) as total_purchases,
                     sum(r.quantity) as units_sold,
                     avg(r.quantity) as avg_quantity_per_order,
                     sum(r.quantity * r.price) as total_revenue,
                     avg(rev.rating) as avg_rating,
                     count(rev) as review_count,
                     avg(rev.sentiment) as avg_sentiment
                
                RETURN p.title as product_name,
                       p.price as current_price,
                       p.category as category,
                       p.brand as brand,
                       unique_customers,
                       total_purchases,
                       units_sold,
                       avg_quantity_per_order,
                       total_revenue,
                       avg_rating,
                       review_count,
                       avg_sentiment
            """, sku=product_sku).single()

            if not basic_metrics:
                return {'error': 'Product not found'}

            # Trend analysis
            trend = session.run("""
                MATCH (p:Product {sku: $sku})<-[r:PURCHASED]-(c:Customer)
                WHERE r.purchase_date > datetime() - duration('P90D')
                WITH date(r.purchase_date) as purchase_date,
                     count(r) as daily_purchases,
                     sum(r.quantity) as daily_units
                ORDER BY purchase_date
                RETURN collect(purchase_date) as dates,
                       collect(daily_purchases) as purchases,
                       collect(daily_units) as units
            """, sku=product_sku).single()

            # Cross-sell opportunities
            cross_sell = session.run("""
                MATCH (p:Product {sku: $sku})<-[:PURCHASED]-(c:Customer)-[:PURCHASED]->(other:Product)
                WHERE p <> other
                WITH other, count(distinct c) as co_purchase_count
                ORDER BY co_purchase_count DESC
                LIMIT 5
                RETURN collect({
                    sku: other.sku,
                    title: other.title,
                    co_purchases: co_purchase_count
                }) as cross_sell_products
            """, sku=product_sku).single()

            # Competitive analysis
            competitive = session.run("""
                MATCH (p:Product {sku: $sku})
                MATCH (competitor:Product)
                WHERE p <> competitor
                  AND p.category = competitor.category
                  AND abs(p.price - competitor.price) / p.price < 0.3
                
                WITH competitor,
                     abs(p.price - competitor.price) as price_diff,
                     competitor.rating - p.rating as rating_diff
                ORDER BY competitor.overall_score DESC
                LIMIT 5
                
                RETURN collect({
                    sku: competitor.sku,
                    title: competitor.title,
                    price: competitor.price,
                    rating: competitor.rating,
                    price_difference: price_diff,
                    rating_advantage: rating_diff
                }) as competitors
            """, sku=product_sku).single()

            return {
                'basic_metrics': dict(basic_metrics),
                'trend_data': dict(trend) if trend else None,
                'cross_sell_opportunities': cross_sell['cross_sell_products'] if cross_sell else [],
                'competitive_analysis': competitive['competitors'] if competitive else [],
                'timestamp': datetime.now().isoformat()
            }

    def revenue_analytics(self, start_date: datetime, end_date: datetime) -> Dict:
        """Revenue analytics with forecasting"""
        with self.driver.session() as session:
            # Daily revenue
            daily_revenue = session.run("""
                MATCH (c:Customer)-[r:PURCHASED]->(p:Product)
                WHERE r.purchase_date >= $start_date AND r.purchase_date <= $end_date
                WITH date(r.purchase_date) as purchase_date,
                     sum(r.quantity * r.price) as daily_revenue,
                     count(distinct c) as daily_customers,
                     count(r) as daily_orders
                ORDER BY purchase_date
                RETURN collect(purchase_date) as dates,
                       collect(daily_revenue) as revenues,
                       collect(daily_customers) as customers,
                       collect(daily_orders) as orders,
                       sum(daily_revenue) as total_revenue,
                       avg(daily_revenue) as avg_daily_revenue
            """, start_date=start_date, end_date=end_date).single()

            # Category breakdown
            category_revenue = session.run("""
                MATCH (c:Customer)-[r:PURCHASED]->(p:Product)
                WHERE r.purchase_date >= $start_date AND r.purchase_date <= $end_date
                WITH p.category as category,
                     sum(r.quantity * r.price) as category_revenue,
                     count(distinct c) as category_customers
                ORDER BY category_revenue DESC
                RETURN collect({
                    category: category,
                    revenue: category_revenue,
                    customers: category_customers
                }) as category_breakdown
            """, start_date=start_date, end_date=end_date).single()

            # Customer cohort analysis
            cohort_analysis = session.run("""
                MATCH (c:Customer)-[r:PURCHASED]->(p:Product)
                WHERE r.purchase_date >= $start_date AND r.purchase_date <= $end_date
                WITH c, min(r.purchase_date) as first_purchase
                WITH date(first_purchase) as cohort_date, count(distinct c) as cohort_size
                ORDER BY cohort_date
                RETURN collect({
                    cohort: cohort_date,
                    size: cohort_size
                }) as cohorts
            """, start_date=start_date, end_date=end_date).single()

            # Simple linear regression forecast
            if daily_revenue and daily_revenue['revenues']:
                revenues = daily_revenue['revenues']
                x = np.arange(len(revenues))
                y = np.array(revenues)

                # Linear regression
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

                # Forecast next 7 days
                forecast_days = 7
                forecast_x = np.arange(len(revenues), len(revenues) + forecast_days)
                forecast_y = slope * forecast_x + intercept

                forecast = {
                    'forecasted_revenues': forecast_y.tolist(),
                    'trend': 'increasing' if slope > 0 else 'decreasing',
                    'confidence': abs(r_value)
                }
            else:
                forecast = None

            return {
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'summary': {
                    'total_revenue': daily_revenue['total_revenue'] if daily_revenue else 0,
                    'avg_daily_revenue': daily_revenue['avg_daily_revenue'] if daily_revenue else 0
                },
                'daily_breakdown': {
                    'dates': daily_revenue['dates'] if daily_revenue else [],
                    'revenues': daily_revenue['revenues'] if daily_revenue else [],
                    'customers': daily_revenue['customers'] if daily_revenue else [],
                    'orders': daily_revenue['orders'] if daily_revenue else []
                },
                'category_breakdown': category_revenue['category_breakdown'] if category_revenue else [],
                'cohort_analysis': cohort_analysis['cohorts'] if cohort_analysis else [],
                'forecast': forecast,
                'timestamp': datetime.now().isoformat()
            }

    def basket_analysis(self) -> Dict:
        """Market basket analysis for association rules"""
        with self.driver.session() as session:
            result = session.run("""
                // Find product pairs frequently bought together
                MATCH (p1:Product)<-[:PURCHASED]-(c:Customer)-[:PURCHASED]->(p2:Product)
                WHERE id(p1) < id(p2)  // Avoid duplicates
                WITH p1, p2, count(distinct c) as support_count
                
                // Calculate total transactions
                MATCH (c:Customer)
                WITH p1, p2, support_count, count(distinct c) as total_customers
                
                // Calculate support
                WITH p1, p2, 
                     support_count,
                     support_count * 1.0 / total_customers as support
                WHERE support > 0.01  // Minimum support threshold
                
                // Calculate confidence and lift
                MATCH (c1:Customer)-[:PURCHASED]->(p1)
                WITH p1, p2, support_count, support, count(distinct c1) as p1_count
                
                MATCH (c2:Customer)-[:PURCHASED]->(p2)
                WITH p1, p2, support_count, support, p1_count, count(distinct c2) as p2_count
                
                WITH p1.title as item1,
                     p2.title as item2,
                     support,
                     support_count * 1.0 / p1_count as confidence,
                     support / ((p1_count * 1.0 / p2_count) * (p2_count * 1.0 / p1_count)) as lift
                WHERE confidence > 0.1  // Minimum confidence threshold
                
                RETURN item1, item2, support, confidence, lift
                ORDER BY lift DESC
                LIMIT 20
            """)

            rules = [dict(record) for record in result]

            return {
                'association_rules': rules,
                'rule_count': len(rules),
                'timestamp': datetime.now().isoformat()
            }

    def customer_lifetime_value(self, customer_id: str) -> Dict:
        """Calculate customer lifetime value and predictions"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (c:Customer {customer_id: $customer_id})-[r:PURCHASED]->(p:Product)
                WITH c,
                     count(r) as total_purchases,
                     sum(r.quantity * r.price) as total_spent,
                     avg(r.quantity * r.price) as avg_order_value,
                     min(r.purchase_date) as first_purchase,
                     max(r.purchase_date) as last_purchase,
                     collect(r.purchase_date) as purchase_dates
                
                WITH c, total_purchases, total_spent, avg_order_value,
                     first_purchase, last_purchase, purchase_dates,
                     duration.between(first_purchase, last_purchase).months as customer_months
                
                // Calculate purchase frequency
                WITH c, total_purchases, total_spent, avg_order_value,
                     first_purchase, last_purchase,
                     CASE 
                         WHEN customer_months > 0 THEN total_purchases * 1.0 / customer_months
                         ELSE total_purchases
                     END as purchase_frequency
                
                // Predict future value (simple model)
                WITH c, total_purchases, total_spent, avg_order_value,
                     purchase_frequency,
                     avg_order_value * purchase_frequency * 12 as predicted_annual_value,
                     duration.between(last_purchase, datetime()).days as days_since_last_purchase
                
                // Churn risk
                WITH c, total_purchases, total_spent, avg_order_value,
                     predicted_annual_value, days_since_last_purchase,
                     CASE
                         WHEN days_since_last_purchase <= 30 THEN 'Active'
                         WHEN days_since_last_purchase <= 90 THEN 'At Risk'
                         WHEN days_since_last_purchase <= 180 THEN 'Churning'
                         ELSE 'Churned'
                     END as status
                
                RETURN c.customer_id as customer_id,
                       total_purchases,
                       total_spent,
                       avg_order_value,
                       predicted_annual_value,
                       status,
                       days_since_last_purchase
            """, customer_id=customer_id).single()

            if not result:
                return {'error': 'Customer not found'}

            return dict(result)

analytics = AnalyticsEngine(db.driver)

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "E-Commerce Analytics & Recommendation API",
        "version": "1.0.0",
        "endpoints": [
            "/recommendations",
            "/analytics/customer-segments",
            "/analytics/product/{product_sku}",
            "/analytics/revenue",
            "/analytics/basket",
            "/analytics/customer-ltv/{customer_id}"
        ]
    }

@app.post("/recommendations")
async def get_recommendations(request: RecommendationRequest):
    """Get personalized recommendations for a customer"""
    try:
        # Import recommendation engine
        from advanced_recommendations import AdvancedRecommendationEngine

        engine = AdvancedRecommendationEngine()

        if request.algorithm == "hybrid":
            recommendations = engine.hybrid_recommendations(
                request.customer_id,
                request.limit
            )
        elif request.algorithm == "collaborative":
            recommendations = engine._collaborative_filtering(
                request.customer_id,
                request.limit
            )
        elif request.algorithm == "content":
            recommendations = engine._content_based_filtering(
                request.customer_id,
                request.limit
            )
        elif request.algorithm == "graph":
            recommendations = engine._graph_based_recommendations(
                request.customer_id,
                request.limit
            )
        elif request.algorithm == "diversity":
            recommendations = engine.diversity_aware_recommendations(
                request.customer_id,
                request.limit
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid algorithm")

        # Add explanations if requested
        if request.include_explanation and recommendations:
            for rec in recommendations[:3]:  # Explain top 3
                explanation = engine.get_recommendation_explanation(
                    request.customer_id,
                    rec['sku']
                )
                rec['explanation'] = explanation

        engine.close()

        return {
            "customer_id": request.customer_id,
            "algorithm": request.algorithm,
            "recommendations": recommendations,
            "count": len(recommendations)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/customer-segments")
async def get_customer_segments():
    """Get customer segmentation analysis"""
    try:
        return analytics.customer_segmentation()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/product/{product_sku}")
async def get_product_analytics(product_sku: str):
    """Get comprehensive product performance metrics"""
    try:
        return analytics.product_performance_metrics(product_sku)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analytics/revenue")
async def get_revenue_analytics(request: AnalyticsRequest):
    """Get revenue analytics with forecasting"""
    try:
        start_date = request.start_date or datetime.now() - timedelta(days=30)
        end_date = request.end_date or datetime.now()

        return analytics.revenue_analytics(start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/basket")
async def get_basket_analysis():
    """Get market basket analysis and association rules"""
    try:
        return analytics.basket_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/customer-ltv/{customer_id}")
async def get_customer_ltv(customer_id: str):
    """Get customer lifetime value analysis"""
    try:
        return analytics.customer_lifetime_value(customer_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/real-time/session-recommendations")
async def get_session_recommendations(events: List[SessionEvent]):
    """Get real-time recommendations based on current session"""
    try:
        from advanced_recommendations import AdvancedRecommendationEngine

        engine = AdvancedRecommendationEngine()

        # Convert to dict format
        session_events = [
            {
                'event_type': event.event_type,
                'product_sku': event.product_sku,
                'timestamp': event.timestamp
            }
            for event in events
        ]

        recommendations = engine.real_time_recommendations(session_events)
        engine.close()

        return {
            "session_events": len(session_events),
            "recommendations": recommendations
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Shopify webhook endpoints
@app.post("/shopify/order-created")
async def shopify_order_webhook(order_data: Dict[str, Any]):
    """Handle Shopify order creation webhook"""
    # Process new order data and update graph
    # This would integrate with Shopify's webhook system
    return {"status": "processed"}

@app.post("/shopify/customer-updated")
async def shopify_customer_webhook(customer_data: Dict[str, Any]):
    """Handle Shopify customer update webhook"""
    # Update customer node in graph
    return {"status": "processed"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)