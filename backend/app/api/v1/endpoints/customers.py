# backend/app/api/v1/endpoints/customers.py
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.schemas import Customer, Recommendation
from app.services.customers import CustomerService
from app.services.recommendations import RecommendationService

router = APIRouter()


@router.get("/", response_model=List[Customer])
async def get_customers(
        limit: int = Query(default=50, ge=1, le=100, description="Number of customers to return"),
        offset: int = Query(default=0, ge=0, description="Number of customers to skip"),
        segment: Optional[str] = Query(default=None, description="Filter by customer segment"),
        sort_by: Optional[str] = Query(default="lifetime_value", description="Sort field")
):
    """
    Get customers with pagination and filtering
    """
    try:
        return CustomerService.get_customers(limit, offset, segment)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str):
    """
    Get detailed information for a specific customer
    """
    try:
        customer = CustomerService.get_customer_by_id(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{customer_id}/recommendations", response_model=List[Recommendation])
async def get_customer_recommendations(
        customer_id: str,
        limit: int = Query(default=10, ge=1, le=50, description="Number of recommendations"),
        algorithm: str = Query(default="hybrid", description="Recommendation algorithm")
):
    """
    Get personalized recommendations for a specific customer
    """
    try:
        # Check if customer exists
        customer = CustomerService.get_customer_by_id(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        return RecommendationService.get_hybrid_recommendations(customer_id, limit)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{customer_id}/purchase-history")
async def get_customer_purchase_history(
        customer_id: str,
        limit: int = Query(default=20, ge=1, le=100),
        offset: int = Query(default=0, ge=0)
):
    """
    Get purchase history for a specific customer
    """
    try:
        from app.database import db_manager

        with db_manager.get_session() as session:
            # Check if customer exists
            exists = session.run("""
                MATCH (c:Customer {customer_id: $customer_id})
                RETURN c
            """, customer_id=customer_id).single()

            if not exists:
                raise HTTPException(status_code=404, detail="Customer not found")

            # Get purchase history
            result = session.run("""
                MATCH (c:Customer {customer_id: $customer_id})-[r:PURCHASED]->(p:Product)
                RETURN p.sku as product_sku,
                       p.title as product_title,
                       p.price as product_price,
                       p.category as category,
                       r.purchase_date as purchase_date,
                       COALESCE(r.quantity, 1) as quantity,
                       COALESCE(r.price, p.price) as purchase_price,
                       COALESCE(r.quantity, 1) * COALESCE(r.price, p.price, 0) as total_amount
                ORDER BY r.purchase_date DESC
                SKIP $offset
                LIMIT $limit
            """, customer_id=customer_id, offset=offset, limit=limit)

            purchases = [dict(record) for record in result]

            # Get total count
            count_result = session.run("""
                MATCH (c:Customer {customer_id: $customer_id})-[r:PURCHASED]->()
                RETURN count(r) as total
            """, customer_id=customer_id).single()

            return {
                'customer_id': customer_id,
                'purchases': purchases,
                'total': count_result['total'] if count_result else 0,
                'offset': offset,
                'limit': limit
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{customer_id}/analytics")
async def get_customer_analytics(customer_id: str):
    """
    Get detailed analytics for a specific customer
    """
    try:
        from app.database import db_manager

        with db_manager.get_session() as session:
            # Get comprehensive customer analytics
            result = session.run("""
                MATCH (c:Customer {customer_id: $customer_id})
                OPTIONAL MATCH (c)-[r:PURCHASED]->(p:Product)
                WITH c,
                     count(r) as total_purchases,
                     count(distinct p) as unique_products,
                     sum(COALESCE(r.quantity, 1)) as total_items,
                     sum(COALESCE(r.quantity, 1) * COALESCE(r.price, p.price, 0)) as lifetime_value,
                     avg(COALESCE(r.quantity, 1) * COALESCE(r.price, p.price, 0)) as avg_order_value,
                     min(r.purchase_date) as first_purchase,
                     max(r.purchase_date) as last_purchase,
                     collect(distinct p.category) as categories,
                     collect(distinct p.brand) as brands

                RETURN c.customer_id as customer_id,
                       c.country as country,
                       c.segment as segment,
                       total_purchases,
                       unique_products,
                       total_items,
                       lifetime_value,
                       avg_order_value,
                       first_purchase,
                       last_purchase,
                       categories[0..5] as top_categories,
                       brands[0..5] as top_brands,
                       CASE 
                           WHEN last_purchase IS NOT NULL 
                           THEN duration.between(last_purchase, datetime()).days
                           ELSE null 
                       END as days_since_last_purchase
            """, customer_id=customer_id).single()

            if not result:
                raise HTTPException(status_code=404, detail="Customer not found")

            analytics = dict(result)

            # Calculate additional metrics
            if analytics['days_since_last_purchase'] is not None:
                if analytics['days_since_last_purchase'] <= 30:
                    analytics['status'] = 'Active'
                elif analytics['days_since_last_purchase'] <= 90:
                    analytics['status'] = 'At Risk'
                else:
                    analytics['status'] = 'Churned'
            else:
                analytics['status'] = 'New'

            return analytics

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))