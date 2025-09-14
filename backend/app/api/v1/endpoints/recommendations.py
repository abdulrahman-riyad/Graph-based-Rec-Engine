# backend/app/api/v1/endpoints/recommendations.py
from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional
from ....models.schemas import RecommendationRequest, Recommendation
from ....services.recommendations import RecommendationService

router = APIRouter()


@router.post("/", response_model=List[Recommendation])
async def get_recommendations(request: RecommendationRequest):
    """
    Get personalized product recommendations for a customer

    - **customer_id**: The unique identifier of the customer
    - **algorithm**: The recommendation algorithm to use (hybrid, collaborative, content, graph)
    - **limit**: Maximum number of recommendations to return
    - **include_explanation**: Whether to include explanation for recommendations
    """
    try:
        recommendations = RecommendationService.get_hybrid_recommendations(
            request.customer_id,
            request.limit
        )

        if request.include_explanation and recommendations:
            for rec in recommendations[:5]:  # Add explanations for top 5
                rec.explanation = RecommendationService.get_recommendation_explanation(
                    request.customer_id,
                    rec.sku
                )

        return recommendations

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/popular", response_model=List[Recommendation])
async def get_popular_products(
        limit: int = Query(default=10, ge=1, le=100, description="Number of products to return"),
        category: Optional[str] = Query(default=None, description="Filter by category")
):
    """
    Get popular products across all customers
    """
    try:
        from ....database import db_manager

        with db_manager.get_session() as session:
            query = """
                MATCH (c:Customer)-[r:PURCHASED]->(p:Product)
                """

            if category:
                query += " WHERE p.category = $category"

            query += """
                WITH p, 
                     count(distinct c) as customer_count,
                     sum(COALESCE(r.quantity, 1)) as total_sold
                RETURN p.sku as sku,
                       p.title as title,
                       p.price as price,
                       p.category as category,
                       p.brand as brand,
                       p.rating as rating,
                       customer_count,
                       total_sold
                ORDER BY customer_count DESC, total_sold DESC
                LIMIT $limit
            """

            params = {"limit": limit}
            if category:
                params["category"] = category

            result = session.run(query, params)

            recommendations = []
            for i, record in enumerate(result):
                rec = Recommendation(
                    sku=record['sku'],
                    title=record.get('title') or record['sku'],
                    price=record.get('price'),
                    category=record.get('category'),
                    rating=record.get('rating'),
                    score=max(0.0, min(1.0, 1.0 - (i / max(1, limit)))),
                    confidence=0.95,
                    algorithm="popular"
                )
                recommendations.append(rec)

            return recommendations

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending", response_model=List[Recommendation])
async def get_trending_products(
        limit: int = Query(default=10, ge=1, le=100),
        days: int = Query(default=7, ge=1, le=30, description="Look back period in days")
):
    """
    Get trending products based on recent activity
    """
    try:
        from ....database import db_manager

        with db_manager.get_session() as session:
            result = session.run("""
                MATCH (c:Customer)-[r:PURCHASED]->(p:Product)
                WHERE COALESCE(r.purchase_date, r.date) > datetime() - duration({days: $days})
                WITH p,
                     count(distinct c) as recent_buyers,
                     sum(COALESCE(r.quantity, 1)) as recent_sales
                WHERE recent_buyers > 1
                RETURN p.sku as sku,
                       p.title as title,
                       p.price as price,
                       p.category as category,
                       p.brand as brand,
                       p.rating as rating,
                       recent_buyers,
                       recent_sales,
                       recent_buyers * 10 + recent_sales as trend_score
                ORDER BY trend_score DESC
                LIMIT $limit
            """, days=f"P{days}D", limit=limit)

            recommendations = []
            for i, record in enumerate(result):
                rec = Recommendation(
                    sku=record['sku'],
                    title=record.get('title') or record['sku'],
                    price=record.get('price'),
                    category=record.get('category'),
                    rating=record.get('rating'),
                    score=min(1.0, float(record['trend_score']) if record.get('trend_score') is not None else 0.0),
                    confidence=min((record.get('recent_buyers') or 0) / 10, 1.0),
                    algorithm="trending"
                )
                recommendations.append(rec)

            return recommendations

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cross-sell")
async def get_cross_sell_recommendations(
        product_sku: str = Body(..., embed=True),
        limit: int = Query(default=5, ge=1, le=20)
):
    """
    Get cross-sell recommendations for a specific product
    """
    try:
        from ....database import db_manager

        with db_manager.get_session() as session:
            result = session.run("""
                MATCH (p:Product {sku: $sku})<-[:PURCHASED]-(c:Customer)-[:PURCHASED]->(cross:Product)
                WHERE p <> cross
                WITH cross,
                     count(distinct c) as co_purchase_count,
                     avg(COALESCE(cross.rating, 0)) as avg_rating
                WHERE co_purchase_count > 1
                RETURN cross.sku as sku,
                       cross.title as title,
                       cross.price as price,
                       cross.category as category,
                       co_purchase_count,
                       avg_rating
                ORDER BY co_purchase_count DESC
                LIMIT $limit
            """, sku=product_sku, limit=limit)

            products = [dict(record) for record in result]

            if not products:
                raise HTTPException(status_code=404, detail="No cross-sell products found")

            return products

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))