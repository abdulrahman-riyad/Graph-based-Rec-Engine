# backend/app/services/products.py
from typing import List, Optional, Dict
import logging

# Fix imports
try:
    from app.database import db_manager
    from app.models.schemas import Product
except ImportError:
    import sys
    import os

    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from app.database import db_manager
    from app.models.schemas import Product

logger = logging.getLogger(__name__)


class ProductService:
    """
    Service for product-related operations
    """

    @staticmethod
    def get_products(
            limit: int = 50,
            offset: int = 0,
            category: Optional[str] = None,
            min_price: Optional[float] = None,
            max_price: Optional[float] = None,
            brand: Optional[str] = None,
            min_rating: Optional[float] = None
    ) -> List[Product]:
        """
        Get products with filtering and pagination
        """
        try:
            with db_manager.get_session() as session:
                # Build dynamic query
                query = "MATCH (p:Product) WHERE 1=1"
                params = {'limit': limit, 'offset': offset}

                # Add filters
                if category:
                    query += " AND p.category = $category"
                    params['category'] = category

                if brand:
                    query += " AND p.brand = $brand"
                    params['brand'] = brand

                if min_price is not None:
                    query += " AND p.price >= $min_price"
                    params['min_price'] = min_price

                if max_price is not None:
                    query += " AND p.price <= $max_price"
                    params['max_price'] = max_price

                if min_rating is not None:
                    query += " AND p.rating >= $min_rating"
                    params['min_rating'] = min_rating

                # Add sorting and pagination
                query += """
                    RETURN p
                    ORDER BY COALESCE(p.popularity_score, 0) DESC, p.rating DESC
                    SKIP $offset
                    LIMIT $limit
                """

                result = session.run(query, params)

                products = []
                for record in result:
                    p = record['p']
                    products.append(Product(
                        sku=p['sku'],
                        title=p.get('title'),
                        price=p.get('price'),
                        category=p.get('category'),
                        brand=p.get('brand'),
                        description=p.get('description'),
                        rating=p.get('rating'),
                        review_count=p.get('review_count'),
                        popularity_score=p.get('popularity_score'),
                        overall_score=p.get('overall_score')
                    ))

                return products

        except Exception as e:
            logger.error(f"Error getting products: {e}")
            return []

    @staticmethod
    def get_product_by_sku(sku: str) -> Optional[Product]:
        """
        Get a single product by SKU
        """
        try:
            with db_manager.get_session() as session:
                query = """
                    MATCH (p:Product {sku: $sku})
                    OPTIONAL MATCH (p)<-[r:PURCHASED]-(c:Customer)
                    WITH p, 
                         count(distinct c) as purchase_count,
                         avg(r.rating) as avg_customer_rating
                    RETURN p, purchase_count, avg_customer_rating
                """

                result = session.run(query, sku=sku).single()

                if not result or not result['p']:
                    return None

                p = result['p']
                product = Product(
                    sku=p['sku'],
                    title=p.get('title'),
                    price=p.get('price'),
                    category=p.get('category'),
                    brand=p.get('brand'),
                    description=p.get('description'),
                    rating=p.get('rating') or result.get('avg_customer_rating'),
                    review_count=p.get('review_count') or result.get('purchase_count', 0),
                    popularity_score=p.get('popularity_score'),
                    overall_score=p.get('overall_score')
                )

                return product

        except Exception as e:
            logger.error(f"Error getting product {sku}: {e}")
            return None

    @staticmethod
    def search_products(
            query_text: str,
            limit: int = 20
    ) -> List[Product]:
        """
        Search products by text
        """
        try:
            with db_manager.get_session() as session:
                # Simple text search - in production, use full-text search
                query = """
                    MATCH (p:Product)
                    WHERE toLower(p.title) CONTAINS toLower($search_text)
                       OR toLower(p.description) CONTAINS toLower($search_text)
                       OR toLower(p.category) CONTAINS toLower($search_text)
                       OR toLower(p.brand) CONTAINS toLower($search_text)
                    RETURN p
                    ORDER BY p.popularity_score DESC
                    LIMIT $limit
                """

                result = session.run(query, search_text=query_text, limit=limit)

                products = []
                for record in result:
                    p = record['p']
                    products.append(Product(
                        sku=p['sku'],
                        title=p.get('title'),
                        price=p.get('price'),
                        category=p.get('category'),
                        brand=p.get('brand'),
                        description=p.get('description'),
                        rating=p.get('rating'),
                        review_count=p.get('review_count'),
                        popularity_score=p.get('popularity_score'),
                        overall_score=p.get('overall_score')
                    ))

                return products

        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []

    @staticmethod
    def get_product_categories() -> List[Dict[str, any]]:
        """
        Get all product categories with counts
        """
        try:
            with db_manager.get_session() as session:
                query = """
                    MATCH (p:Product)
                    WHERE p.category IS NOT NULL
                    WITH p.category as category, count(p) as product_count
                    ORDER BY product_count DESC
                    RETURN category, product_count
                """

                result = session.run(query)

                categories = []
                for record in result:
                    categories.append({
                        'name': record['category'],
                        'product_count': record['product_count']
                    })

                return categories

        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return []

    @staticmethod
    def get_product_brands() -> List[Dict[str, any]]:
        """
        Get all product brands with counts
        """
        try:
            with db_manager.get_session() as session:
                query = """
                    MATCH (p:Product)
                    WHERE p.brand IS NOT NULL
                    WITH p.brand as brand, count(p) as product_count
                    ORDER BY product_count DESC
                    RETURN brand, product_count
                """

                result = session.run(query)

                brands = []
                for record in result:
                    brands.append({
                        'name': record['brand'],
                        'product_count': record['product_count']
                    })

                return brands

        except Exception as e:
            logger.error(f"Error getting brands: {e}")
            return []

    @staticmethod
    def update_product_score(sku: str) -> bool:
        """
        Update product popularity and overall scores
        """
        try:
            with db_manager.get_session() as session:
                query = """
                    MATCH (p:Product {sku: $sku})
                    OPTIONAL MATCH (p)<-[r:PURCHASED]-(c:Customer)
                    WITH p, 
                         count(distinct c) as purchase_count,
                         avg(COALESCE(r.rating, p.rating)) as avg_rating

                    // Update scores
                    SET p.popularity_score = purchase_count,
                        p.overall_score = (
                            COALESCE(avg_rating, 0) * 0.3 + 
                            log(purchase_count + 1) * 0.7
                        ),
                        p.last_updated = datetime()

                    RETURN p
                """

                result = session.run(query, sku=sku).single()
                return result is not None

        except Exception as e:
            logger.error(f"Error updating product score for {sku}: {e}")
            return False

    @staticmethod
    def get_trending_products(days: int = 7, limit: int = 10) -> List[Product]:
        """
        Get trending products based on recent activity
        """
        try:
            with db_manager.get_session() as session:
                query = """
                    MATCH (c:Customer)-[r:PURCHASED]->(p:Product)
                    WHERE r.purchase_date > datetime() - duration({days: $days})
                    WITH p,
                         count(distinct c) as recent_buyers,
                         sum(COALESCE(r.quantity, 1)) as recent_sales
                    WHERE recent_buyers > 1
                    RETURN p
                    ORDER BY recent_buyers DESC, recent_sales DESC
                    LIMIT $limit
                """

                result = session.run(query, days=f"P{days}D", limit=limit)

                products = []
                for record in result:
                    p = record['p']
                    products.append(Product(
                        sku=p['sku'],
                        title=p.get('title'),
                        price=p.get('price'),
                        category=p.get('category'),
                        brand=p.get('brand'),
                        description=p.get('description'),
                        rating=p.get('rating'),
                        review_count=p.get('review_count'),
                        popularity_score=p.get('popularity_score'),
                        overall_score=p.get('overall_score')
                    ))

                return products

        except Exception as e:
            logger.error(f"Error getting trending products: {e}")
            return []