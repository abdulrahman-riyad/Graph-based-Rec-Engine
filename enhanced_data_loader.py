"""
enhanced_data_loader.py
Load all 7 datasets with proper relationships and enriched features
"""

import os
import pandas as pd
import numpy as np
import json
import jsonlines
from pathlib import Path
from neo4j import GraphDatabase
from dotenv import load_dotenv
from tqdm import tqdm
from datetime import datetime
from textblob import TextBlob
import warnings

warnings.filterwarnings('ignore')
load_dotenv()

class EnhancedDataLoader:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        self.data_root = Path("data")
        self.batch_size = 1000
        print("✅ Connected to Neo4j")

    def create_enhanced_schema(self):
        """Create comprehensive constraints and indexes"""
        print("📊 Creating enhanced schema...")

        queries = [
            # Customer constraints
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Customer) REQUIRE c.customer_id IS UNIQUE",
            "CREATE INDEX IF NOT EXISTS FOR (c:Customer) ON (c.country)",
            "CREATE INDEX IF NOT EXISTS FOR (c:Customer) ON (c.segment)",
            "CREATE INDEX IF NOT EXISTS FOR (c:Customer) ON (c.lifetime_value)",

            # Product constraints
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Product) REQUIRE p.sku IS UNIQUE",
            "CREATE INDEX IF NOT EXISTS FOR (p:Product) ON (p.category)",
            "CREATE INDEX IF NOT EXISTS FOR (p:Product) ON (p.brand)",
            "CREATE INDEX IF NOT EXISTS FOR (p:Product) ON (p.price)",
            "CREATE INDEX IF NOT EXISTS FOR (p:Product) ON (p.rating)",

            # Category constraints
            "CREATE CONSTRAINT IF NOT EXISTS FOR (cat:Category) REQUIRE cat.name IS UNIQUE",
            "CREATE INDEX IF NOT EXISTS FOR (cat:Category) ON (cat.level)",

            # Brand constraints
            "CREATE CONSTRAINT IF NOT EXISTS FOR (b:Brand) REQUIRE b.name IS UNIQUE",

            # Review constraints
            "CREATE CONSTRAINT IF NOT EXISTS FOR (r:Review) REQUIRE r.review_id IS UNIQUE",
            "CREATE INDEX IF NOT EXISTS FOR (r:Review) ON (r.rating)",
            "CREATE INDEX IF NOT EXISTS FOR (r:Review) ON (r.sentiment)",

            # Session constraints
            "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Session) REQUIRE s.session_id IS UNIQUE",
            "CREATE INDEX IF NOT EXISTS FOR (s:Session) ON (s.date)",
        ]

        with self.driver.session() as session:
            for query in queries:
                try:
                    session.run(query)
                except Exception as e:
                    pass
        print("✅ Schema created")

    def load_amazon_products_enhanced(self):
        """Load Amazon product metadata and reviews with NLP features"""
        print("\n📦 Loading Amazon Product Data (Enhanced)...")

        path = self.data_root / "1. Amazon Product Data (UCSD)"

        # Load metadata files
        meta_files = ['meta_Amazon_Fashion.jsonl', 'meta_Health_and_Personal_Care.jsonl']

        for meta_file in meta_files:
            file_path = path / meta_file
            if not file_path.exists():
                continue

            category_type = meta_file.replace('meta_', '').replace('.jsonl', '')
            print(f"  Loading {category_type} metadata...")

            with jsonlines.open(file_path) as reader:
                batch = []
                for item in tqdm(reader):
                    # Create product with enriched features
                    product = {
                        'sku': f'AMZN_{item.get("asin", "")}',
                        'title': item.get('title', ''),
                        'price': float(item.get('price', '0').replace('$', '').replace(',', '')) if item.get('price') else 0,
                        'brand': item.get('brand', 'Unknown'),
                        'category': category_type,
                        'features': ' '.join(item.get('feature', [])) if item.get('feature') else '',
                        'also_buy': item.get('also_buy', []),
                        'also_view': item.get('also_view', []),
                        'rank': item.get('rank', ''),
                        'main_cat': item.get('main_cat', category_type)
                    }
                    batch.append(product)

                    if len(batch) >= self.batch_size:
                        self._load_product_batch(batch)
                        batch = []

                if batch:
                    self._load_product_batch(batch)

        # Load review files with sentiment analysis
        review_files = ['Amazon_Fashion.jsonl', 'Health_and_Personal_Care.jsonl']

        for review_file in review_files:
            file_path = path / review_file
            if not file_path.exists():
                continue

            print(f"  Loading reviews from {review_file}...")

            with jsonlines.open(file_path) as reader:
                batch = []
                for i, review in enumerate(tqdm(reader)):
                    if i >= 10000:  # Limit for demo
                        break

                    # Perform sentiment analysis
                    review_text = review.get('reviewText', '')
                    sentiment = self._analyze_sentiment(review_text) if review_text else 0

                    review_data = {
                        'review_id': f'REV_{review.get("asin")}_{review.get("reviewerID")}',
                        'customer_id': f'AMZN_{review.get("reviewerID")}',
                        'product_sku': f'AMZN_{review.get("asin")}',
                        'rating': float(review.get('overall', 0)),
                        'review_text': review_text[:500],  # Truncate for storage
                        'sentiment': sentiment,
                        'helpful': review.get('helpful', [0, 0]),
                        'verified': review.get('verified', False),
                        'review_time': review.get('reviewTime', ''),
                        'unix_time': review.get('unixReviewTime', 0)
                    }
                    batch.append(review_data)

                    if len(batch) >= self.batch_size:
                        self._load_review_batch(batch)
                        batch = []

                if batch:
                    self._load_review_batch(batch)

    def load_customer_behavior_enriched(self):
        """Load customer behavior with segmentation"""
        print("\n📊 Loading Customer Behavior Dataset (Enriched)...")

        path = self.data_root / "3. E-Commerce Customer Behavior Dataset"
        csv_file = path / "E-commerce Customer Behavior - Sheet1.csv"

        if not csv_file.exists():
            print("  File not found")
            return

        df = pd.read_csv(csv_file)

        # Customer segmentation based on behavior
        if 'Customer_ID' in df.columns:
            # Calculate customer metrics
            customer_metrics = df.groupby('Customer_ID').agg({
                'Purchase_Amount': ['sum', 'mean', 'count'] if 'Purchase_Amount' in df.columns else {},
                'Page_Views': 'sum' if 'Page_Views' in df.columns else {},
                'Time_on_Site': 'mean' if 'Time_on_Site' in df.columns else {}
            }).reset_index()

            # Flatten column names
            customer_metrics.columns = ['_'.join(col).strip() for col in customer_metrics.columns.values]

            # Create customer segments
            if 'Purchase_Amount_sum' in customer_metrics.columns:
                customer_metrics['segment'] = pd.qcut(
                    customer_metrics['Purchase_Amount_sum'],
                    q=4,
                    labels=['Bronze', 'Silver', 'Gold', 'Platinum']
                )

            # Load to Neo4j
            print(f"  Loading {len(customer_metrics)} customer profiles...")

            with self.driver.session() as session:
                for batch_start in tqdm(range(0, len(customer_metrics), self.batch_size)):
                    batch = customer_metrics.iloc[batch_start:batch_start + self.batch_size]

                    query = """
                    UNWIND $batch as row
                    MERGE (c:Customer {customer_id: 'BEHAV_' + toString(row.Customer_ID_)})
                    SET c.lifetime_value = coalesce(row.Purchase_Amount_sum, 0),
                        c.avg_purchase = coalesce(row.Purchase_Amount_mean, 0),
                        c.purchase_count = coalesce(row.Purchase_Amount_count, 0),
                        c.segment = coalesce(row.segment, 'Unknown'),
                        c.total_page_views = coalesce(row.Page_Views_sum, 0),
                        c.avg_time_on_site = coalesce(row.Time_on_Site_mean, 0)
                    """

                    session.run(query, batch=batch.fillna(0).to_dict('records'))

    def load_sessions_and_clickstream(self):
        """Load session data with clickstream events"""
        print("\n🖱️ Loading Session & Clickstream Data...")

        path = self.data_root / "2. E-Commerce Behavior Data (Multi-Category Store)"
        csv_file = path / "2019-Oct.csv"

        if not csv_file.exists():
            print("  File not found")
            return

        # Read sample for clickstream
        df = pd.read_csv(csv_file, nrows=100000)

        # Create sessions
        sessions = df.groupby('user_session').agg({
            'user_id': 'first',
            'event_time': ['min', 'max'],
            'event_type': 'count'
        }).reset_index()

        print(f"  Loading {len(sessions)} sessions...")

        with self.driver.session() as session:
            # Create session nodes
            for batch_start in tqdm(range(0, len(sessions), self.batch_size)):
                batch = sessions.iloc[batch_start:batch_start + self.batch_size]

                query = """
                UNWIND $batch as row
                CREATE (s:Session {
                    session_id: row.user_session,
                    customer_id: 'CLICK_' + toString(row.user_id),
                    start_time: row.event_time_min,
                    end_time: row.event_time_max,
                    event_count: row.event_type
                })
                """

                # Flatten multi-level columns
                batch_dict = []
                for _, row in batch.iterrows():
                    batch_dict.append({
                        'user_session': row['user_session'],
                        'user_id': row[('user_id', 'first')],
                        'event_time_min': str(row[('event_time', 'min')]),
                        'event_time_max': str(row[('event_time', 'max')]),
                        'event_type': int(row[('event_type', 'count')])
                    })

                session.run(query, batch=batch_dict)

            # Create clickstream relationships
            print("  Creating clickstream paths...")

            # Group events by session
            for session_id in tqdm(df['user_session'].unique()[:100]):  # Limit for demo
                session_events = df[df['user_session'] == session_id].sort_values('event_time')

                if len(session_events) > 1:
                    query = """
                    MATCH (s:Session {session_id: $session_id})
                    UNWIND $events as event
                    MATCH (p:Product {sku: 'CLICK_' + toString(event.product_id)})
                    CREATE (s)-[r:EVENT {
                        type: event.event_type,
                        timestamp: event.event_time,
                        order: event.order
                    }]->(p)
                    """

                    events = []
                    for i, (_, row) in enumerate(session_events.iterrows()):
                        events.append({
                            'product_id': row['product_id'],
                            'event_type': row['event_type'],
                            'event_time': str(row['event_time']),
                            'order': i
                        })

                    try:
                        session.run(query, session_id=session_id, events=events)
                    except:
                        pass

    def create_product_relationships(self):
        """Create co-purchase and co-view relationships"""
        print("\n🔗 Creating Product Relationships...")

        with self.driver.session() as session:
            # Create ALSO_BOUGHT relationships
            print("  Creating co-purchase relationships...")

            query = """
            MATCH (p1:Product)<-[:PURCHASED]-(c:Customer)-[:PURCHASED]->(p2:Product)
            WHERE p1 <> p2
            WITH p1, p2, count(distinct c) as co_purchase_count
            WHERE co_purchase_count > 5
            MERGE (p1)-[r:ALSO_BOUGHT {weight: co_purchase_count}]->(p2)
            """

            session.run(query)

            # Create VIEWED_TOGETHER relationships from sessions
            print("  Creating co-view relationships...")

            query = """
            MATCH (s:Session)-[:EVENT {type: 'view'}]->(p1:Product)
            MATCH (s)-[:EVENT {type: 'view'}]->(p2:Product)
            WHERE p1 <> p2
            WITH p1, p2, count(distinct s) as co_view_count
            WHERE co_view_count > 3
            MERGE (p1)-[r:VIEWED_TOGETHER {weight: co_view_count}]->(p2)
            """

            session.run(query)

    def _load_product_batch(self, batch):
        """Helper to load product batch"""
        with self.driver.session() as session:
            query = """
            UNWIND $batch as row
            MERGE (p:Product {sku: row.sku})
            SET p.title = row.title,
                p.price = toFloat(row.price),
                p.brand = row.brand,
                p.category = row.category,
                p.features = row.features,
                p.main_cat = row.main_cat
            WITH p, row
            WHERE row.brand IS NOT NULL AND row.brand <> 'Unknown'
            MERGE (b:Brand {name: row.brand})
            MERGE (p)-[:MADE_BY]->(b)
            WITH p, row
            WHERE row.category IS NOT NULL
            MERGE (c:Category {name: row.category})
            MERGE (p)-[:BELONGS_TO]->(c)
            """

            session.run(query, batch=batch)

    def _load_review_batch(self, batch):
        """Helper to load review batch"""
        with self.driver.session() as session:
            query = """
            UNWIND $batch as row
            MERGE (c:Customer {customer_id: row.customer_id})
            MERGE (p:Product {sku: row.product_sku})
            CREATE (r:Review {
                review_id: row.review_id,
                rating: toFloat(row.rating),
                review_text: row.review_text,
                sentiment: toFloat(row.sentiment),
                verified: row.verified,
                review_time: row.review_time
            })
            CREATE (c)-[:WROTE]->(r)
            CREATE (r)-[:ABOUT]->(p)
            """

            session.run(query, batch=batch)

    def _analyze_sentiment(self, text):
        """Simple sentiment analysis"""
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except:
            return 0

    def update_product_scores(self):
        """Calculate and update product scores based on reviews and purchases"""
        print("\n📈 Calculating Product Scores...")

        with self.driver.session() as session:
            query = """
            MATCH (p:Product)
            OPTIONAL MATCH (p)<-[:ABOUT]-(r:Review)
            OPTIONAL MATCH (p)<-[pur:PURCHASED]-()
            WITH p, 
                 avg(r.rating) as avg_rating,
                 count(r) as review_count,
                 avg(r.sentiment) as avg_sentiment,
                 count(pur) as purchase_count
            SET p.rating = coalesce(avg_rating, 0),
                p.review_count = coalesce(review_count, 0),
                p.sentiment_score = coalesce(avg_sentiment, 0),
                p.popularity_score = coalesce(purchase_count, 0),
                p.overall_score = (
                    coalesce(avg_rating, 0) * 0.3 + 
                    coalesce(avg_sentiment + 1, 0) * 2.5 * 0.2 + 
                    log(coalesce(purchase_count, 1) + 1) * 0.5
                )
            """

            session.run(query)
            print("  ✅ Product scores updated")

    def show_enhanced_statistics(self):
        """Show comprehensive statistics"""
        print("\n📊 ENHANCED DATABASE STATISTICS")
        print("=" * 60)

        with self.driver.session() as session:
            stats = {}

            # Node counts
            node_types = ['Customer', 'Product', 'Review', 'Session', 'Category', 'Brand']
            for node_type in node_types:
                count = session.run(f"MATCH (n:{node_type}) RETURN count(n) as c").single()['c']
                stats[node_type] = count

            # Relationship counts
            rel_types = ['PURCHASED', 'WROTE', 'ALSO_BOUGHT', 'VIEWED_TOGETHER', 'EVENT']
            for rel_type in rel_types:
                count = session.run(f"MATCH ()-[r:{rel_type}]->() RETURN count(r) as c").single()['c']
                stats[rel_type] = count

            # Print stats
            print("\n📦 Nodes:")
            for node_type in node_types:
                if stats.get(node_type, 0) > 0:
                    print(f"   • {node_type}s: {stats[node_type]:,}")

            print("\n🔗 Relationships:")
            for rel_type in rel_types:
                if stats.get(rel_type, 0) > 0:
                    print(f"   • {rel_type}: {stats[rel_type]:,}")

            # Advanced metrics
            metrics = session.run("""
                MATCH (c:Customer)
                OPTIONAL MATCH (c)-[r:PURCHASED]->()
                WITH c, count(r) as purchases
                RETURN avg(purchases) as avg_purchases,
                       percentileDisc(purchases, 0.5) as median_purchases,
                       max(purchases) as max_purchases
            """).single()

            print("\n📈 Metrics:")
            print(f"   • Avg purchases/customer: {metrics['avg_purchases']:.1f}")
            print(f"   • Median purchases: {metrics['median_purchases']}")
            print(f"   • Max purchases: {metrics['max_purchases']}")

    def run_full_load(self):
        """Run complete enhanced data load"""
        print("=" * 60)
        print("ENHANCED DATA LOADER")
        print("=" * 60)

        # Clear and setup
        self.clear_database()
        self.create_enhanced_schema()

        # Load all datasets
        self.load_uci_retail_fixed()  # Use existing method
        self.load_amazon_products_enhanced()
        self.load_customer_behavior_enriched()
        self.load_sessions_and_clickstream()

        # Create relationships and scores
        self.create_product_relationships()
        self.update_product_scores()

        # Show results
        self.show_enhanced_statistics()

    def clear_database(self):
        """Clear existing data"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("✅ Database cleared")

    def load_uci_retail_fixed(self):
        """Your existing UCI retail loader - keep this"""
        # Keep your existing implementation
        pass

    def close(self):
        self.driver.close()

if __name__ == "__main__":
    loader = EnhancedDataLoader()
    loader.run_full_load()
    loader.close()
    print("\n✅ Enhanced data loading complete!")