# backend/app/services/customers.py
from typing import List, Optional, Dict
from datetime import datetime
import logging

# Fix imports
try:
    from app.database import db_manager
    from app.models.schemas import Customer
except ImportError:
    import sys
    import os

    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from app.database import db_manager
    from app.models.schemas import Customer

logger = logging.getLogger(__name__)


class CustomerService:
    """
    Service for customer-related operations
    """

    @staticmethod
    def get_customers(
            limit: int = 50,
            offset: int = 0,
            segment: Optional[str] = None,
            country: Optional[str] = None,
            min_ltv: Optional[float] = None,
            sort_by: str = 'lifetime_value'
    ) -> List[Customer]:
        """
        Get customers with filtering and pagination
        """
        try:
            with db_manager.get_session() as session:
                # Build dynamic query
                query = """
                    MATCH (c:Customer)
                    OPTIONAL MATCH (c)-[r:PURCHASED]->(p:Product)
                    WITH c,
                         count(r) as purchase_count,
                         sum(COALESCE(r.quantity, 1) * COALESCE(r.price, p.price, 0)) as lifetime_value,
                         avg(COALESCE(r.quantity, 1) * COALESCE(r.price, p.price, 0)) as avg_order_value,
                         max(r.purchase_date) as last_purchase
                    WHERE 1=1
                """

                params = {'limit': limit, 'offset': offset}

                # Add filters
                if segment:
                    query += " AND c.segment = $segment"
                    params['segment'] = segment

                if country:
                    query += " AND c.country = $country"
                    params['country'] = country

                if min_ltv is not None:
                    query += " AND lifetime_value >= $min_ltv"
                    params['min_ltv'] = min_ltv

                # Add sorting
                sort_field = {
                    'lifetime_value': 'lifetime_value',
                    'purchase_count': 'purchase_count',
                    'last_purchase': 'last_purchase',
                    'customer_id': 'c.customer_id'
                }.get(sort_by, 'lifetime_value')

                query += f"""
                    RETURN c.customer_id as customer_id,
                           c.email as email,
                           c.name as name,
                           c.country as country,
                           c.segment as segment,
                           c.created_at as created_at,
                           lifetime_value,
                           purchase_count,
                           avg_order_value,
                           last_purchase
                    ORDER BY {sort_field} DESC
                    SKIP $offset
                    LIMIT $limit
                """

                result = session.run(query, params)

                customers = []
                for record in result:
                    # Calculate churn risk
                    churn_risk = CustomerService._calculate_churn_risk(record['last_purchase'])

                    customers.append(Customer(
                        customer_id=record['customer_id'],
                        email=record['email'],
                        name=record['name'],
                        country=record['country'],
                        segment=record['segment'],
                        lifetime_value=round(record['lifetime_value'] or 0, 2),
                        purchase_count=record['purchase_count'] or 0,
                        avg_order_value=round(record['avg_order_value'] or 0, 2),
                        last_purchase_date=record['last_purchase'],
                        churn_risk=churn_risk,
                        created_at=record['created_at']
                    ))

                return customers

        except Exception as e:
            logger.error(f"Error getting customers: {e}")
            return []

    @staticmethod
    def get_customer_by_id(customer_id: str) -> Optional[Customer]:
        """
        Get a single customer by ID
        """
        try:
            with db_manager.get_session() as session:
                query = """
                    MATCH (c:Customer {customer_id: $customer_id})
                    OPTIONAL MATCH (c)-[r:PURCHASED]->(p:Product)
                    WITH c,
                         count(r) as purchase_count,
                         sum(COALESCE(r.quantity, 1) * COALESCE(r.price, p.price, 0)) as lifetime_value,
                         avg(COALESCE(r.quantity, 1) * COALESCE(r.price, p.price, 0)) as avg_order_value,
                         max(r.purchase_date) as last_purchase,
                         min(r.purchase_date) as first_purchase
                    RETURN c.customer_id as customer_id,
                           c.email as email,
                           c.name as name,
                           c.country as country,
                           c.segment as segment,
                           c.created_at as created_at,
                           lifetime_value,
                           purchase_count,
                           avg_order_value,
                           last_purchase,
                           first_purchase
                """

                result = session.run(query, customer_id=customer_id).single()

                if not result:
                    return None

                # Calculate churn risk
                churn_risk = CustomerService._calculate_churn_risk(result['last_purchase'])

                return Customer(
                    customer_id=result['customer_id'],
                    email=result['email'],
                    name=result['name'],
                    country=result['country'],
                    segment=result['segment'] or CustomerService._calculate_segment(
                        result['purchase_count'],
                        result['lifetime_value'],
                        result['last_purchase']
                    ),
                    lifetime_value=round(result['lifetime_value'] or 0, 2),
                    purchase_count=result['purchase_count'] or 0,
                    avg_order_value=round(result['avg_order_value'] or 0, 2),
                    last_purchase_date=result['last_purchase'],
                    churn_risk=churn_risk,
                    created_at=result['created_at']
                )

        except Exception as e:
            logger.error(f"Error getting customer {customer_id}: {e}")
            return None

    @staticmethod
    def _calculate_churn_risk(last_purchase_date) -> str:
        """
        Calculate customer churn risk based on last purchase date
        """
        if not last_purchase_date:
            return 'New'

        try:
            # Handle both string and datetime formats
            if isinstance(last_purchase_date, str):
                last_purchase = datetime.fromisoformat(last_purchase_date.replace('Z', '+00:00'))
            else:
                last_purchase = last_purchase_date

            days_since = (datetime.now() - last_purchase).days

            if days_since <= 30:
                return 'Active'
            elif days_since <= 60:
                return 'Low'
            elif days_since <= 90:
                return 'Medium'
            elif days_since <= 180:
                return 'High'
            else:
                return 'Churned'
        except:
            return 'Unknown'

    @staticmethod
    def _calculate_segment(purchase_count: int, lifetime_value: float, last_purchase) -> str:
        """
        Calculate customer segment based on behavior
        """
        if not purchase_count:
            return 'New'

        # Calculate days since last purchase
        days_since = 0
        if last_purchase:
            try:
                if isinstance(last_purchase, str):
                    last_purchase = datetime.fromisoformat(last_purchase.replace('Z', '+00:00'))
                days_since = (datetime.now() - last_purchase).days
            except:
                pass

        # Segment logic
        if days_since <= 30 and purchase_count >= 10 and lifetime_value >= 500:
            return 'Champions'
        elif days_since <= 60 and purchase_count >= 5 and lifetime_value >= 200:
            return 'Loyal Customers'
        elif purchase_count <= 2:
            return 'New Customers'
        elif days_since > 90 and purchase_count >= 5:
            return 'At Risk'
        elif days_since > 180:
            return 'Lost'
        else:
            return 'Regular'

    @staticmethod
    def update_customer_segment(customer_id: str) -> bool:
        """
        Update customer segment based on current metrics
        """
        try:
            with db_manager.get_session() as session:
                query = """
                    MATCH (c:Customer {customer_id: $customer_id})
                    OPTIONAL MATCH (c)-[r:PURCHASED]->(p:Product)
                    WITH c,
                         count(r) as frequency,
                         max(r.purchase_date) as last_purchase,
                         sum(COALESCE(r.quantity, 1) * COALESCE(r.price, p.price, 0)) as monetary_value

                    WITH c, frequency, monetary_value,
                         CASE 
                             WHEN last_purchase IS NULL THEN 999
                             ELSE duration.between(last_purchase, datetime()).days
                         END as recency_days

                    SET c.segment = CASE
                        WHEN recency_days <= 30 AND frequency >= 10 AND monetary_value >= 500 
                            THEN 'Champions'
                        WHEN recency_days <= 60 AND frequency >= 5 AND monetary_value >= 200 
                            THEN 'Loyal Customers'
                        WHEN recency_days <= 90 AND frequency <= 2 
                            THEN 'New Customers'
                        WHEN recency_days > 90 AND recency_days <= 180 AND frequency >= 5 
                            THEN 'At Risk'
                        WHEN recency_days > 180 
                            THEN 'Lost'
                        ELSE 'Regular'
                    END,
                    c.segment_updated = datetime()

                    RETURN c
                """

                result = session.run(query, customer_id=customer_id).single()
                return result is not None

        except Exception as e:
            logger.error(f"Error updating customer segment for {customer_id}: {e}")
            return False

    @staticmethod
    def get_customer_metrics(customer_id: str) -> Dict:
        """
        Get detailed metrics for a customer
        """
        try:
            with db_manager.get_session() as session:
                query = """
                    MATCH (c:Customer {customer_id: $customer_id})
                    OPTIONAL MATCH (c)-[r:PURCHASED]->(p:Product)

                    WITH c, r, p
                    ORDER BY r.purchase_date DESC

                    WITH c,
                         count(r) as total_purchases,
                         count(distinct p) as unique_products,
                         sum(COALESCE(r.quantity, 1)) as total_items,
                         sum(COALESCE(r.quantity, 1) * COALESCE(r.price, p.price, 0)) as lifetime_value,
                         avg(COALESCE(r.quantity, 1) * COALESCE(r.price, p.price, 0)) as avg_order_value,
                         min(r.purchase_date) as first_purchase,
                         max(r.purchase_date) as last_purchase,
                         collect(distinct p.category)[0..5] as top_categories,
                         collect(distinct p.brand)[0..5] as top_brands

                    RETURN c.customer_id as customer_id,
                           total_purchases,
                           unique_products,
                           total_items,
                           lifetime_value,
                           avg_order_value,
                           first_purchase,
                           last_purchase,
                           top_categories,
                           top_brands
                """

                result = session.run(query, customer_id=customer_id).single()

                if not result:
                    return {}

                metrics = dict(result)

                # Calculate additional metrics
                if metrics['first_purchase'] and metrics['last_purchase']:
                    try:
                        first = datetime.fromisoformat(str(metrics['first_purchase']).replace('Z', '+00:00'))
                        last = datetime.fromisoformat(str(metrics['last_purchase']).replace('Z', '+00:00'))
                        metrics['customer_lifetime_days'] = (last - first).days
                        metrics['days_since_last_purchase'] = (datetime.now() - last).days
                    except:
                        pass

                # Purchase frequency
                if metrics['customer_lifetime_days'] and metrics['customer_lifetime_days'] > 0:
                    metrics['purchase_frequency'] = metrics['total_purchases'] / (
                                metrics['customer_lifetime_days'] / 30)

                return metrics

        except Exception as e:
            logger.error(f"Error getting customer metrics for {customer_id}: {e}")
            return {}

    @staticmethod
    def search_customers(
            query_text: str,
            limit: int = 20
    ) -> List[Customer]:
        """
        Search customers by text
        """
        try:
            with db_manager.get_session() as session:
                query = """
                    MATCH (c:Customer)
                    WHERE toLower(c.customer_id) CONTAINS toLower($search_text)
                       OR toLower(c.email) CONTAINS toLower($search_text)
                       OR toLower(c.name) CONTAINS toLower($search_text)
                       OR toLower(c.country) CONTAINS toLower($search_text)
                    OPTIONAL MATCH (c)-[r:PURCHASED]->()
                    WITH c,
                         count(r) as purchase_count,
                         sum(COALESCE(r.quantity, 1) * COALESCE(r.price, 0)) as lifetime_value
                    RETURN c.customer_id as customer_id,
                           c.email as email,
                           c.name as name,
                           c.country as country,
                           c.segment as segment,
                           lifetime_value,
                           purchase_count
                    ORDER BY lifetime_value DESC
                    LIMIT $limit
                """

                result = session.run(query, search_text=query_text, limit=limit)

                customers = []
                for record in result:
                    customers.append(Customer(
                        customer_id=record['customer_id'],
                        email=record['email'],
                        name=record['name'],
                        country=record['country'],
                        segment=record['segment'],
                        lifetime_value=round(record['lifetime_value'] or 0, 2),
                        purchase_count=record['purchase_count'] or 0,
                        avg_order_value=0,
                        churn_risk='Unknown'
                    ))

                return customers

        except Exception as e:
            logger.error(f"Error searching customers: {e}")
            return []