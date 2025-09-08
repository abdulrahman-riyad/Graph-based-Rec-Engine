# backend/app/services/recommendations.py
from typing import List, Dict, Optional
import logging

# Fix imports - use relative or absolute based on your setup
try:
    from app.database import db_manager
    from app.models.schemas import Recommendation
except ImportError:
    # If running from backend directory
    import sys
    import os

    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from app.database import db_manager
    from app.models.schemas import Recommendation

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Service for generating product recommendations
    """

    @staticmethod
    def get_hybrid_recommendations(customer_id: str, limit: int = 10) -> List[Recommendation]:
        """
        Generate hybrid recommendations combining multiple algorithms
        """
        try:
            # Get recommendations from different algorithms
            collab = RecommendationService._collaborative_filtering(customer_id, limit * 2)
            content = RecommendationService._content_based_filtering(customer_id, limit * 2)
            graph = RecommendationService._graph_based_recommendations(customer_id, limit * 2)

            # Combine and score
            product_scores = {}

            # Weight configuration
            weights = {
                'collaborative': 0.4,
                'content': 0.3,
                'graph': 0.3
            }

            # Process collaborative filtering results
            for i, product in enumerate(collab):
                sku = product['sku']
                score = (len(collab) - i) / len(collab) * weights['collaborative']
                product_scores[sku] = product_scores.get(sku, {})
                product_scores[sku]['score'] = product_scores[sku].get('score', 0) + score
                product_scores[sku].update(product)

            # Process content-based results
            for i, product in enumerate(content):
                sku = product['sku']
                score = (len(content) - i) / len(content) * weights['content']
                product_scores[sku] = product_scores.get(sku, {})
                product_scores[sku]['score'] = product_scores[sku].get('score', 0) + score
                product_scores[sku].update(product)

            # Process graph-based results
            for i, product in enumerate(graph):
                sku = product['sku']
                score = (len(graph) - i) / len(graph) * weights['graph']
                product_scores[sku] = product_scores.get(sku, {})
                product_scores[sku]['score'] = product_scores[sku].get('score', 0) + score
                product_scores[sku].update(product)

            # Sort by final score
            sorted_products = sorted(
                product_scores.items(),
                key=lambda x: x[1].get('score', 0),
                reverse=True
            )[:limit]

            # Convert to Recommendation objects
            recommendations = []
            for sku, data in sorted_products:
                rec = Recommendation(
                    sku=sku,
                    title=data.get('title'),
                    price=data.get('price'),
                    category=data.get('category'),
                    brand=data.get('brand'),
                    rating=data.get('rating'),
                    score=min(data.get('score', 0), 1.0),
                    confidence=min(data.get('score', 0) * 2, 1.0),
                    algorithm_used='hybrid'
                )
                recommendations.append(rec)

            return recommendations

        except Exception as e:
            logger.error(f"Error generating hybrid recommendations: {e}")
            return []

    @staticmethod
    def _collaborative_filtering(customer_id: str, limit: int) -> List[Dict]:
        """
        Collaborative filtering based on similar customers
        """
        try:
            with db_manager.get_session() as session:
                query = """
                    // Find products purchased by target customer
                    MATCH (target:Customer {customer_id: $customer_id})-[:PURCHASED]->(p:Product)
                    WITH target, collect(id(p)) as targetProducts

                    // Find similar customers
                    MATCH (other:Customer)-[:PURCHASED]->(p:Product)
                    WHERE other <> target AND id(p) IN targetProducts
                    WITH target, other, targetProducts, collect(id(p)) as commonProducts

                    // Calculate similarity
                    WITH target, other, 
                         size(commonProducts) * 1.0 / size(targetProducts) as similarity
                    WHERE similarity > 0.1

                    // Get recommendations from similar customers
                    MATCH (other)-[:PURCHASED]->(rec:Product)
                    WHERE NOT EXISTS((target)-[:PURCHASED]->(rec))

                    RETURN rec.sku as sku,
                           rec.title as title,
                           rec.price as price,
                           rec.category as category,
                           rec.brand as brand,
                           rec.rating as rating,
                           sum(similarity) as score,
                           count(distinct other) as recommenders
                    ORDER BY score DESC
                    LIMIT $limit
                """

                result = session.run(query, customer_id=customer_id, limit=limit)
                return [dict(record) for record in result]

        except Exception as e:
            logger.error(f"Collaborative filtering error: {e}")
            return []

    @staticmethod
    def _content_based_filtering(customer_id: str, limit: int) -> List[Dict]:
        """
        Content-based filtering based on product features
        """
        try:
            with db_manager.get_session() as session:
                query = """
                    // Get customer preferences
                    MATCH (c:Customer {customer_id: $customer_id})-[:PURCHASED]->(p:Product)
                    WITH c,
                         collect(distinct p.category) as categories,
                         collect(distinct p.brand) as brands,
                         avg(p.price) as avg_price,
                         stdev(p.price) as price_std

                    // Find similar products
                    MATCH (rec:Product)
                    WHERE NOT EXISTS((c)-[:PURCHASED]->(rec))
                      AND (rec.category IN categories OR rec.brand IN brands)
                      AND rec.price >= avg_price - 2 * COALESCE(price_std, 10)
                      AND rec.price <= avg_price + 2 * COALESCE(price_std, 10)

                    // Calculate content score
                    WITH rec,
                         CASE WHEN rec.category IN categories THEN 0.5 ELSE 0 END +
                         CASE WHEN rec.brand IN brands THEN 0.3 ELSE 0 END +
                         CASE WHEN rec.rating > 4 THEN 0.2 ELSE 0 END as content_score
                    WHERE content_score > 0

                    RETURN rec.sku as sku,
                           rec.title as title,
                           rec.price as price,
                           rec.category as category,
                           rec.brand as brand,
                           rec.rating as rating,
                           content_score as score
                    ORDER BY content_score DESC
                    LIMIT $limit
                """

                result = session.run(query, customer_id=customer_id, limit=limit)
                return [dict(record) for record in result]

        except Exception as e:
            logger.error(f"Content-based filtering error: {e}")
            return []

    @staticmethod
    def _graph_based_recommendations(customer_id: str, limit: int) -> List[Dict]:
        """
        Graph-based recommendations using product relationships
        """
        try:
            with db_manager.get_session() as session:
                query = """
                    // Get customer's purchased products
                    MATCH (c:Customer {customer_id: $customer_id})-[:PURCHASED]->(p:Product)

                    // Find products frequently bought together
                    MATCH (p)<-[:PURCHASED]-(other:Customer)-[:PURCHASED]->(rec:Product)
                    WHERE NOT EXISTS((c)-[:PURCHASED]->(rec)) 
                      AND p <> rec

                    WITH rec, count(distinct other) as co_purchasers
                    WHERE co_purchasers > 1

                    RETURN rec.sku as sku,
                           rec.title as title,
                           rec.price as price,
                           rec.category as category,
                           rec.brand as brand,
                           rec.rating as rating,
                           co_purchasers as score
                    ORDER BY co_purchasers DESC
                    LIMIT $limit
                """

                result = session.run(query, customer_id=customer_id, limit=limit)
                return [dict(record) for record in result]

        except Exception as e:
            logger.error(f"Graph-based recommendations error: {e}")
            return []

    @staticmethod
    def get_recommendation_explanation(customer_id: str, product_sku: str) -> List[str]:
        """
        Generate explanation for why a product was recommended
        """
        explanations = []

        try:
            with db_manager.get_session() as session:
                # Check if similar customers bought it
                similar_customers = session.run("""
                    MATCH (c:Customer {customer_id: $customer_id})-[:PURCHASED]->(p1:Product)
                    MATCH (p1)<-[:PURCHASED]-(other:Customer)-[:PURCHASED]->(rec:Product {sku: $sku})
                    WHERE other <> c
                    RETURN count(distinct other) as count
                """, customer_id=customer_id, sku=product_sku).single()

                if similar_customers and similar_customers['count'] > 0:
                    explanations.append(f"{similar_customers['count']} customers with similar taste bought this")

                # Check category match
                category_match = session.run("""
                    MATCH (c:Customer {customer_id: $customer_id})-[:PURCHASED]->(p:Product)
                    MATCH (rec:Product {sku: $sku})
                    WHERE p.category = rec.category
                    RETURN count(distinct p) as count, rec.category as category
                """, customer_id=customer_id, sku=product_sku).single()

                if category_match and category_match['count'] > 0:
                    explanations.append(f"Matches your interest in {category_match['category']}")

                # Check frequently bought together
                bought_together = session.run("""
                    MATCH (c:Customer {customer_id: $customer_id})-[:PURCHASED]->(p:Product)
                    MATCH (p)<-[:PURCHASED]-(other:Customer)-[:PURCHASED]->(rec:Product {sku: $sku})
                    WHERE other <> c
                    RETURN p.title as product, count(distinct other) as count
                    ORDER BY count DESC
                    LIMIT 1
                """, customer_id=customer_id, sku=product_sku).single()

                if bought_together and bought_together['count'] > 0:
                    explanations.append(f"Frequently bought with {bought_together['product']}")

        except Exception as e:
            logger.error(f"Error generating explanation: {e}")

        return explanations if explanations else ["Based on your purchase history and preferences"]