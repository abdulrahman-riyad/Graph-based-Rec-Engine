"""
advanced_recommendations.py
Advanced recommendation engine with multiple algorithms
"""

import os
import numpy as np
from neo4j import GraphDatabase
from dotenv import load_dotenv
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import pandas as pd

load_dotenv()

class AdvancedRecommendationEngine:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def hybrid_recommendations(self, customer_id: str, limit: int = 10) -> List[Dict]:
        """
        Hybrid recommendation combining multiple algorithms with weighted scoring
        """
        print(f"\n🎯 HYBRID RECOMMENDATIONS for {customer_id}")
        print("=" * 60)

        # Get recommendations from different algorithms
        collab = self._collaborative_filtering(customer_id, limit * 2)
        content = self._content_based_filtering(customer_id, limit * 2)
        graph = self._graph_based_recommendations(customer_id, limit * 2)
        trending = self._trending_products(limit)
        personalized_trending = self._personalized_trending(customer_id, limit)

        # Combine and score
        product_scores = {}

        # Weight each algorithm
        weights = {
            'collaborative': 0.35,
            'content': 0.25,
            'graph': 0.20,
            'trending': 0.10,
            'personalized_trending': 0.10
        }

        # Add collaborative filtering scores
        for i, product in enumerate(collab):
            sku = product['sku']
            score = (len(collab) - i) / len(collab) * weights['collaborative']
            product_scores[sku] = product_scores.get(sku, 0) + score

        # Add content-based scores
        for i, product in enumerate(content):
            sku = product['sku']
            score = (len(content) - i) / len(content) * weights['content']
            product_scores[sku] = product_scores.get(sku, 0) + score

        # Add graph-based scores
        for i, product in enumerate(graph):
            sku = product['sku']
            score = (len(graph) - i) / len(graph) * weights['graph']
            product_scores[sku] = product_scores.get(sku, 0) + score

        # Add trending scores
        for i, product in enumerate(trending):
            sku = product['sku']
            score = (len(trending) - i) / len(trending) * weights['trending']
            product_scores[sku] = product_scores.get(sku, 0) + score

        # Add personalized trending scores
        for i, product in enumerate(personalized_trending):
            sku = product['sku']
            score = (len(personalized_trending) - i) / len(personalized_trending) * weights['personalized_trending']
            product_scores[sku] = product_scores.get(sku, 0) + score

        # Sort by final score
        sorted_products = sorted(product_scores.items(), key=lambda x: x[1], reverse=True)[:limit]

        # Get product details
        recommendations = []
        with self.driver.session() as session:
            for sku, score in sorted_products:
                result = session.run("""
                    MATCH (p:Product {sku: $sku})
                    RETURN p.sku as sku,
                           p.title as title,
                           p.price as price,
                           p.rating as rating,
                           p.category as category,
                           p.brand as brand,
                           p.overall_score as overall_score
                """, sku=sku).single()

                if result:
                    recommendations.append({
                        **dict(result),
                        'hybrid_score': score,
                        'confidence': min(score * 2, 1.0)  # Normalize to 0-1
                    })

        return recommendations

    def _collaborative_filtering(self, customer_id: str, limit: int) -> List[Dict]:
        """Enhanced collaborative filtering with similarity scoring"""
        with self.driver.session() as session:
            result = session.run("""
                // Find similar customers using Jaccard similarity
                MATCH (target:Customer {customer_id: $customer_id})-[:PURCHASED]->(p:Product)
                WITH target, collect(id(p)) as targetProducts
                
                MATCH (other:Customer)-[:PURCHASED]->(p:Product)
                WHERE other <> target
                WITH target, targetProducts, other, collect(id(p)) as otherProducts
                
                // Calculate Jaccard similarity
                WITH target, other,
                     targetProducts, otherProducts,
                     size([x IN targetProducts WHERE x IN otherProducts]) as intersection,
                     size(targetProducts + [x IN otherProducts WHERE NOT x IN targetProducts]) as union
                WHERE union > 0
                WITH target, other, (intersection * 1.0) / union as similarity
                WHERE similarity > 0.1
                
                // Get recommendations from similar users
                MATCH (other)-[r:PURCHASED]->(rec:Product)
                WHERE NOT EXISTS((target)-[:PURCHASED]->(rec))
                
                RETURN rec.sku as sku,
                       rec.title as title,
                       rec.price as price,
                       rec.rating as rating,
                       sum(similarity) as similarity_score,
                       count(distinct other) as recommenders
                ORDER BY similarity_score DESC
                LIMIT $limit
            """, customer_id=customer_id, limit=limit)

            return [dict(record) for record in result]

    def _content_based_filtering(self, customer_id: str, limit: int) -> List[Dict]:
        """Content-based filtering using product features"""
        with self.driver.session() as session:
            result = session.run("""
                // Get customer's preferred categories and brands
                MATCH (c:Customer {customer_id: $customer_id})-[:PURCHASED]->(p:Product)
                WITH c,
                     collect(distinct p.category) as categories,
                     collect(distinct p.brand) as brands,
                     avg(p.price) as avg_price,
                     stdev(p.price) as price_stdev
                
                // Find similar products
                MATCH (rec:Product)
                WHERE NOT EXISTS((c)-[:PURCHASED]->(rec))
                  AND (rec.category IN categories OR rec.brand IN brands)
                  AND rec.price >= avg_price - 2 * price_stdev
                  AND rec.price <= avg_price + 2 * price_stdev
                
                // Score based on feature similarity
                WITH rec,
                     CASE WHEN rec.category IN categories THEN 0.4 ELSE 0 END +
                     CASE WHEN rec.brand IN brands THEN 0.3 ELSE 0 END +
                     CASE WHEN rec.rating > 4 THEN 0.3 ELSE 0 END as content_score
                
                RETURN rec.sku as sku,
                       rec.title as title,
                       rec.price as price,
                       rec.rating as rating,
                       content_score
                ORDER BY content_score DESC
                LIMIT $limit
            """, customer_id=customer_id, limit=limit)

            return [dict(record) for record in result]

    def _graph_based_recommendations(self, customer_id: str, limit: int) -> List[Dict]:
        """Graph-based recommendations using PageRank and community detection"""
        with self.driver.session() as session:
            # Use graph algorithms for recommendations
            result = session.run("""
                // Get products through graph traversal
                MATCH path = (c:Customer {customer_id: $customer_id})-[:PURCHASED]->(p1:Product)
                             -[:ALSO_BOUGHT|VIEWED_TOGETHER*1..2]-(p2:Product)
                WHERE NOT EXISTS((c)-[:PURCHASED]->(p2))
                  AND p1 <> p2
                
                WITH p2, 
                     count(distinct path) as path_count,
                     min(length(path)) as min_distance,
                     avg(p2.overall_score) as product_score
                
                RETURN p2.sku as sku,
                       p2.title as title,
                       p2.price as price,
                       p2.rating as rating,
                       path_count * (1.0 / min_distance) * product_score as graph_score
                ORDER BY graph_score DESC
                LIMIT $limit
            """, customer_id=customer_id, limit=limit)

            return [dict(record) for record in result]

    def _trending_products(self, limit: int) -> List[Dict]:
        """Get trending products based on recent activity"""
        with self.driver.session() as session:
            # Calculate trend score based on recent purchases
            result = session.run("""
                MATCH (c:Customer)-[r:PURCHASED]->(p:Product)
                WHERE r.purchase_date > datetime() - duration('P30D')
                
                WITH p,
                     count(distinct c) as recent_buyers,
                     avg(r.quantity) as avg_quantity,
                     p.overall_score as product_score
                
                RETURN p.sku as sku,
                       p.title as title,
                       p.price as price,
                       p.rating as rating,
                       recent_buyers * avg_quantity * product_score as trend_score
                ORDER BY trend_score DESC
                LIMIT $limit
            """, limit=limit)

            return [dict(record) for record in result]

    def _personalized_trending(self, customer_id: str, limit: int) -> List[Dict]:
        """Trending products in customer's preferred categories"""
        with self.driver.session() as session:
            result = session.run("""
                // Get customer preferences
                MATCH (c:Customer {customer_id: $customer_id})-[:PURCHASED]->(p:Product)
                WITH c, collect(distinct p.category) as preferred_categories
                
                // Find trending in those categories
                MATCH (other:Customer)-[r:PURCHASED]->(trending:Product)
                WHERE trending.category IN preferred_categories
                  AND NOT EXISTS((c)-[:PURCHASED]->(trending))
                  AND r.purchase_date > datetime() - duration('P14D')
                
                WITH trending,
                     count(distinct other) as recent_buyers,
                     avg(trending.rating) as avg_rating
                
                RETURN trending.sku as sku,
                       trending.title as title,
                       trending.price as price,
                       trending.rating as rating,
                       recent_buyers * avg_rating as personalized_trend_score
                ORDER BY personalized_trend_score DESC
                LIMIT $limit
            """, customer_id=customer_id, limit=limit)

            return [dict(record) for record in result]

    def sequential_pattern_mining(self, customer_id: str, limit: int = 5) -> List[Dict]:
        """
        Mine sequential patterns from customer sessions
        """
        with self.driver.session() as session:
            result = session.run("""
                // Find sequences that led to purchases
                MATCH (c:Customer {customer_id: $customer_id})-[:PURCHASED]->(last:Product)
                MATCH (other:Customer)-[:PURCHASED]->(last)
                WHERE other <> c
                
                // Find what other customers bought next
                MATCH (other)-[r2:PURCHASED]->(next:Product)
                WHERE r2.purchase_date > r1.purchase_date
                  AND NOT EXISTS((c)-[:PURCHASED]->(next))
                
                WITH next, count(distinct other) as sequence_count
                WHERE sequence_count > 2
                
                RETURN next.sku as sku,
                       next.title as title,
                       next.price as price,
                       sequence_count as pattern_strength
                ORDER BY pattern_strength DESC
                LIMIT $limit
            """, customer_id=customer_id, limit=limit)

            return [dict(record) for record in result]

    def cross_sell_recommendations(self, product_sku: str, limit: int = 5) -> List[Dict]:
        """
        Cross-sell recommendations for a specific product
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Product {sku: $sku})<-[:PURCHASED]-(c:Customer)-[:PURCHASED]->(cross:Product)
                WHERE p <> cross
                
                WITH cross,
                     count(distinct c) as co_purchase_count,
                     avg(cross.rating) as avg_rating
                
                RETURN cross.sku as sku,
                       cross.title as title,
                       cross.price as price,
                       cross.category as category,
                       co_purchase_count,
                       avg_rating
                ORDER BY co_purchase_count DESC
                LIMIT $limit
            """, sku=product_sku, limit=limit)

            return [dict(record) for record in result]

    def get_recommendation_explanation(self, customer_id: str, product_sku: str) -> Dict:
        """
        Explain why a product was recommended
        """
        with self.driver.session() as session:
            # Check different recommendation reasons
            explanations = []

            # Similar users bought it
            similar_users = session.run("""
                MATCH (c:Customer {customer_id: $customer_id})-[:PURCHASED]->(p1:Product)
                MATCH (p1)<-[:PURCHASED]-(other:Customer)-[:PURCHASED]->(rec:Product {sku: $sku})
                WHERE other <> c
                RETURN count(distinct other) as count
            """, customer_id=customer_id, sku=product_sku).single()

            if similar_users and similar_users['count'] > 0:
                explanations.append(f"{similar_users['count']} similar customers bought this")

            # Frequently bought together
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

            # Category match
            category_match = session.run("""
                MATCH (c:Customer {customer_id: $customer_id})-[:PURCHASED]->(p:Product)
                MATCH (rec:Product {sku: $sku})
                WHERE p.category = rec.category
                RETURN count(distinct p) as count, rec.category as category
            """, customer_id=customer_id, sku=product_sku).single()

            if category_match and category_match['count'] > 0:
                explanations.append(f"Matches your interest in {category_match['category']}")

            return {
                'product_sku': product_sku,
                'reasons': explanations,
                'confidence': len(explanations) / 3.0
            }

    def real_time_recommendations(self, session_events: List[Dict]) -> List[Dict]:
        """
        Real-time recommendations based on current session behavior
        """
        # Extract product views from session
        viewed_products = [e['product_sku'] for e in session_events if e['event_type'] == 'view']

        if not viewed_products:
            return []

        with self.driver.session() as session:
            result = session.run("""
                UNWIND $viewed as sku
                MATCH (p:Product {sku: sku})
                
                // Find related products
                MATCH (p)-[:ALSO_BOUGHT|VIEWED_TOGETHER]-(rec:Product)
                WHERE NOT rec.sku IN $viewed
                
                WITH rec, count(*) as relation_count
                
                RETURN rec.sku as sku,
                       rec.title as title,
                       rec.price as price,
                       rec.category as category,
                       relation_count
                ORDER BY relation_count DESC
                LIMIT 5
            """, viewed=viewed_products)

            return [dict(record) for record in result]

    def diversity_aware_recommendations(self, customer_id: str, limit: int = 10) -> List[Dict]:
        """
        Ensure diversity in recommendations across categories and price ranges
        """
        # Get initial recommendations
        initial_recs = self.hybrid_recommendations(customer_id, limit * 3)

        # Ensure diversity
        diverse_recs = []
        seen_categories = set()
        seen_brands = set()
        price_ranges = {'low': 0, 'medium': 0, 'high': 0}

        for rec in initial_recs:
            # Determine price range
            price = rec.get('price', 0)
            if price < 20:
                price_range = 'low'
            elif price < 50:
                price_range = 'medium'
            else:
                price_range = 'high'

            # Check diversity criteria
            category = rec.get('category', '')
            brand = rec.get('brand', '')

            # Add if it increases diversity
            if (category not in seen_categories or
                brand not in seen_brands or
                price_ranges[price_range] < 2):

                diverse_recs.append(rec)
                seen_categories.add(category)
                seen_brands.add(brand)
                price_ranges[price_range] += 1

                if len(diverse_recs) >= limit:
                    break

        return diverse_recs

    def close(self):
        self.driver.close()

def demo_advanced_recommendations():
    """Demo the advanced recommendation features"""
    engine = AdvancedRecommendationEngine()

    # Get a sample customer
    with engine.driver.session() as session:
        result = session.run("""
            MATCH (c:Customer)-[:PURCHASED]->()
            WITH c, count(*) as purchases
            WHERE purchases > 10 AND purchases < 100
            RETURN c.customer_id as customer_id
            ORDER BY rand()
            LIMIT 1
        """).single()

        if result:
            customer_id = result['customer_id']

            print(f"\n🎯 Advanced Recommendations Demo for Customer: {customer_id}")
            print("=" * 70)

            # Get hybrid recommendations
            hybrid_recs = engine.hybrid_recommendations(customer_id, 10)

            print("\n📊 HYBRID RECOMMENDATIONS (Multiple Algorithms)")
            print("-" * 70)

            for i, rec in enumerate(hybrid_recs, 1):
                title = rec.get('title', rec['sku'])[:50]
                print(f"{i:2}. {title:<50} ${rec.get('price', 0):>7.2f}  "
                      f"Rating: {rec.get('rating', 0):.1f}  "
                      f"Confidence: {rec['confidence']:.0%}")

            # Get explanation for top recommendation
            if hybrid_recs:
                top_rec = hybrid_recs[0]
                explanation = engine.get_recommendation_explanation(customer_id, top_rec['sku'])

                print("\n💡 WHY WE RECOMMENDED THE TOP ITEM:")
                print("-" * 70)
                for reason in explanation['reasons']:
                    print(f"  • {reason}")

            # Show diversity-aware recommendations
            diverse_recs = engine.diversity_aware_recommendations(customer_id, 10)

            print("\n🎨 DIVERSITY-AWARE RECOMMENDATIONS")
            print("-" * 70)

            categories = set()
            for rec in diverse_recs:
                categories.add(rec.get('category', 'Unknown'))

            print(f"Categories covered: {', '.join(categories)}")

            # Demo cross-sell
            if hybrid_recs:
                product_sku = hybrid_recs[0]['sku']
                cross_sell = engine.cross_sell_recommendations(product_sku, 5)

                print(f"\n🛍️ CROSS-SELL for {hybrid_recs[0].get('title', product_sku)[:40]}")
                print("-" * 70)

                for i, item in enumerate(cross_sell, 1):
                    title = item.get('title', item['sku'])[:50]
                    print(f"{i}. {title:<50} (bought together {item['co_purchase_count']} times)")

    engine.close()
    print("\n✅ Advanced recommendation demo complete!")

if __name__ == "__main__":
    demo_advanced_recommendations()