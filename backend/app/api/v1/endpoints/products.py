# backend/app/api/v1/endpoints/products.py
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ....models.schemas import Product, Recommendation
from ....services.products import ProductService

router = APIRouter()


@router.get("/", response_model=List[Product])
async def get_products(
        limit: int = Query(default=50, ge=1, le=100, description="Number of products to return"),
        offset: int = Query(default=0, ge=0, description="Number of products to skip"),
        category: Optional[str] = Query(default=None, description="Filter by category"),
        min_price: Optional[float] = Query(default=None, ge=0, description="Minimum price filter"),
        max_price: Optional[float] = Query(default=None, ge=0, description="Maximum price filter"),
        sort_by: Optional[str] = Query(default="popularity", description="Sort field (popularity, price, rating)")
):
    """
    Get products with pagination and filtering
    """
    try:
        products = ProductService.get_products(limit, offset, category)

        # Apply additional filters if needed
        if min_price is not None or max_price is not None:
            products = [
                p for p in products
                if (min_price is None or (p.price and p.price >= min_price)) and
                   (max_price is None or (p.price and p.price <= max_price))
            ]

        return products

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{product_sku}", response_model=Product)
async def get_product(product_sku: str):
    """
    Get detailed information for a specific product
    """
    try:
        product = ProductService.get_product_by_sku(product_sku)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{product_sku}/similar", response_model=List[Product])
async def get_similar_products(
        product_sku: str,
        limit: int = Query(default=10, ge=1, le=50, description="Number of similar products to return")
):
    """
    Get products similar to the specified product
    """
    try:
        from ....database import db_manager

        with db_manager.get_session() as session:
            # First check if product exists
            exists = session.run("""
                MATCH (p:Product {sku: $sku})
                RETURN p
            """, sku=product_sku).single()

            if not exists:
                raise HTTPException(status_code=404, detail="Product not found")

            # Find similar products
            result = session.run("""
                MATCH (p:Product {sku: $sku})
                MATCH (similar:Product)
                WHERE similar <> p
                  AND (similar.category = p.category 
                       OR similar.brand = p.brand
                       OR abs(similar.price - p.price) / p.price < 0.3)
                WITH similar,
                     CASE 
                         WHEN similar.category = p.category THEN 3
                         ELSE 0
                     END +
                     CASE 
                         WHEN similar.brand = p.brand THEN 2
                         ELSE 0
                     END +
                     CASE 
                         WHEN abs(similar.price - p.price) / p.price < 0.1 THEN 2
                         WHEN abs(similar.price - p.price) / p.price < 0.3 THEN 1
                         ELSE 0
                     END as similarity_score
                WHERE similarity_score > 0
                RETURN similar
                ORDER BY similarity_score DESC, similar.popularity_score DESC
                LIMIT $limit
            """, sku=product_sku, limit=limit)

            products = []
            for record in result:
                p = record['similar']
                products.append(Product(
                    sku=p['sku'],
                    title=p.get('title'),
                    price=p.get('price'),
                    category=p.get('category'),
                    brand=p.get('brand'),
                    rating=p.get('rating'),
                    review_count=p.get('review_count'),
                    popularity_score=p.get('popularity_score'),
                    overall_score=p.get('overall_score')
                ))

            return products

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{product_sku}/reviews")
async def get_product_reviews(
        product_sku: str,
        limit: int = Query(default=20, ge=1, le=100),
        offset: int = Query(default=0, ge=0)
):
    """
    Get reviews for a specific product
    """
    try:
        from ....database import db_manager

        with db_manager.get_session() as session:
            result = session.run("""
                MATCH (p:Product {sku: $sku})<-[:ABOUT]-(r:Review)<-[:WROTE]-(c:Customer)
                RETURN r.review_id as review_id,
                       r.rating as rating,
                       r.review_text as text,
                       r.sentiment as sentiment,
                       r.verified as verified,
                       COALESCE(r.review_time, r.date) as review_date,
                       c.customer_id as customer_id
                ORDER BY r.review_time DESC
                SKIP $offset
                LIMIT $limit
            """, sku=product_sku, offset=offset, limit=limit)

            reviews = [dict(record) for record in result]

            if not reviews and offset == 0:
                # Check if product exists
                exists = session.run("""
                    MATCH (p:Product {sku: $sku})
                    RETURN p
                """, sku=product_sku).single()

                if not exists:
                    raise HTTPException(status_code=404, detail="Product not found")

            return {
                'product_sku': product_sku,
                'reviews': reviews,
                'total': len(reviews),
                'offset': offset,
                'limit': limit
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))