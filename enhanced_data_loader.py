"""
enhanced_data_loader.py
Complete implementation for loading all e-commerce datasets
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
import warnings

warnings.filterwarnings('ignore')
load_dotenv()

class EnhancedDataLoader:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password123")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        self.data_root = Path("data")
        self.batch_size = 500
        print("✅ Connected to Neo4j")

    def create_enhanced_schema(self):
        """Create comprehensive constraints and indexes"""
        print("📊 Creating enhanced schema...")

        queries = [
            # Customer constraints
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Customer) REQUIRE c.customer_id IS UNIQUE",
            "CREATE INDEX IF NOT EXISTS FOR (c:Customer) ON (c.country)",
            "CREATE INDEX IF NOT EXISTS FOR (c:Customer) ON (c.segment)",
            
            # Product constraints
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Product) REQUIRE p.sku IS UNIQUE",
            "CREATE INDEX IF NOT EXISTS FOR (p:Product) ON (p.category)",
            "CREATE INDEX IF NOT EXISTS FOR (p:Product) ON (p.brand)",
            "CREATE INDEX IF NOT EXISTS FOR (p:Product) ON (p.price)",
            
            # Category constraints
            "CREATE CONSTRAINT IF NOT EXISTS FOR (cat:Category) REQUIRE cat.name IS UNIQUE",
            
            # Brand constraints
            "CREATE CONSTRAINT IF NOT EXISTS FOR (b:Brand) REQUIRE b.name IS UNIQUE",
            
            # Session constraints
            "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Session) REQUIRE s.session_id IS UNIQUE",
        ]

        with self.driver.session() as session:
            for query in queries:
                try:
                    session.run(query)
                except Exception as e:
                    pass  # Constraint might already exist
        print("✅ Schema created")

    def load_uci_retail_fixed(self):
        """Load UCI Online Retail Dataset with proper handling"""
        print("\n📦 Loading UCI Online Retail Dataset...")
        
        path = self.data_root / "4. UCI Online Retail Dataset"
        excel_file = path / "Online Retail.xlsx"
        
        if not excel_file.exists():
            print("  ⚠ UCI Retail file not found, skipping...")
            return
            
        try:
            # Read the Excel file
            df = pd.read_excel(excel_file)
            print(f"  Loaded {len(df)} transactions")
            
            # Clean the data
            df = df.dropna(subset=['CustomerID', 'StockCode'])
            df['CustomerID'] = df['CustomerID'].astype(str).str.replace('.0', '', regex=False)
            df['UnitPrice'] = pd.to_numeric(df['UnitPrice'], errors='coerce').fillna(0)
            df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(1)
            
            # Create customers
            customers = df.groupby('CustomerID').agg({
                'Country': 'first',
                'InvoiceNo': 'count',
                'UnitPrice': lambda x: (x * df.loc[x.index, 'Quantity']).sum()
            }).reset_index()
            customers.columns = ['customer_id', 'country', 'purchase_count', 'total_spent']
            
            print(f"  Loading {len(customers)} customers...")
            
            # Load customers in batches
            with self.driver.session() as session:
                for i in tqdm(range(0, len(customers), self.batch_size)):
                    batch = customers.iloc[i:i+self.batch_size]
                    query = """
                    UNWIND $batch as row
                    MERGE (c:Customer {customer_id: 'UCI_' + row.customer_id})
                    SET c.country = row.country,
                        c.purchase_count = toInteger(row.purchase_count),
                        c.total_spent = toFloat(row.total_spent),
                        c.source = 'UCI_Retail'
                    """
                    session.run(query, batch=batch.to_dict('records'))
            
            # Create products
            products = df.groupby('StockCode').agg({
                'Description': 'first',
                'UnitPrice': 'mean',
                'Quantity': 'sum'
            }).reset_index()
            products.columns = ['sku', 'description', 'avg_price', 'total_quantity_sold']
            products = products.dropna(subset=['description'])
            
            print(f"  Loading {len(products)} products...")
            
            # Load products in batches
            with self.driver.session() as session:
                for i in tqdm(range(0, len(products), self.batch_size)):
                    batch = products.iloc[i:i+self.batch_size]
                    query = """
                    UNWIND $batch as row
                    MERGE (p:Product {sku: 'UCI_' + row.sku})
                    SET p.title = row.description,
                        p.price = toFloat(row.avg_price),
                        p.total_quantity_sold = toInteger(row.total_quantity_sold),
                        p.source = 'UCI_Retail'
                    """
                    session.run(query, batch=batch.to_dict('records'))
            
            # Create purchase relationships
            print(f"  Creating purchase relationships...")
            purchases = df[['CustomerID', 'StockCode', 'Quantity', 'UnitPrice', 'InvoiceDate']].copy()
            purchases['total_amount'] = purchases['Quantity'] * purchases['UnitPrice']
            
            # Load purchases in batches
            with self.driver.session() as session:
                for i in tqdm(range(0, min(len(purchases), 50000), self.batch_size)):  # Limit to 50k for demo
                    batch = purchases.iloc[i:i+self.batch_size]
                    query = """
                    UNWIND $batch as row
                    MATCH (c:Customer {customer_id: 'UCI_' + row.CustomerID})
                    MATCH (p:Product {sku: 'UCI_' + row.StockCode})
                    CREATE (c)-[r:PURCHASED {
                        quantity: toInteger(row.Quantity),
                        unit_price: toFloat(row.UnitPrice),
                        total_amount: toFloat(row.total_amount),
                        date: datetime(row.InvoiceDate)
                    }]->(p)
                    """
                    batch_dict = batch.to_dict('records')
                    for record in batch_dict:
                        record['InvoiceDate'] = str(record['InvoiceDate'])
                    session.run(query, batch=batch_dict)
            
            print(f"  ✅ UCI Retail data loaded successfully")
            
        except Exception as e:
            print(f"  ❌ Error loading UCI Retail: {str(e)}")

    def load_amazon_products_enhanced(self):
        """Load Amazon product metadata with proper error handling"""
        print("\n📦 Loading Amazon Product Data (Enhanced)...")
        
        path = self.data_root / "1. Amazon Product Data (UCSD)"
        
        # Load metadata files
        meta_files = ['meta_Amazon_Fashion.jsonl', 'meta_Health_and_Personal_Care.jsonl']
        
        for meta_file in meta_files:
            file_path = path / meta_file
            if not file_path.exists():
                print(f"  ⚠ {meta_file} not found, skipping...")
                continue
                
            category_type = meta_file.replace('meta_', '').replace('.jsonl', '').replace('_', ' ')
            print(f"  Loading {category_type} metadata...")
            
            products_loaded = 0
            batch = []
            
            try:
                with jsonlines.open(file_path) as reader:
                    for item in tqdm(reader, desc="Products"):
                        if products_loaded >= 5000:  # Limit for demo
                            break
                            
                        # Extract price safely
                        price = 0.0
                        if 'price' in item and item['price']:
                            price_str = str(item['price'])
                            # Remove currency symbols and convert
                            price_str = price_str.replace('$', '').replace(',', '').strip()
                            try:
                                price = float(price_str)
                            except:
                                price = 0.0
                        
                        # Create product
                        product = {
                            'sku': f'AMZN_{item.get("asin", "")}',
                            'title': item.get('title', 'Unknown Product')[:200],
                            'price': price,
                            'brand': item.get('brand', 'Unknown'),
                            'category': category_type,
                            'main_cat': item.get('main_cat', category_type)
                        }
                        
                        batch.append(product)
                        products_loaded += 1
                        
                        if len(batch) >= self.batch_size:
                            self._load_product_batch(batch)
                            batch = []
                    
                    if batch:
                        self._load_product_batch(batch)
                        
                print(f"  ✅ Loaded {products_loaded} {category_type} products")
                
            except Exception as e:
                print(f"  ❌ Error loading {meta_file}: {str(e)}")

    def load_customer_behavior_enriched(self):
        """Load customer behavior dataset"""
        print("\n📊 Loading Customer Behavior Dataset (Enriched)...")
        
        path = self.data_root / "3. E-Commerce Customer Behavior Dataset"
        csv_file = path / "E-commerce Customer Behavior - Sheet1.csv"
        
        if not csv_file.exists():
            print("  ⚠ Customer behavior file not found, skipping...")
            return
            
        try:
            df = pd.read_csv(csv_file)
            
            # Print columns to debug
            print(f"  Found columns: {', '.join(df.columns[:10])}")
            
            # Try different possible column names for customer ID
            customer_id_col = None
            for possible_name in ['Customer_ID', 'Customer ID', 'CustomerID', 'customer_id', 'User_ID', 'User ID']:
                if possible_name in df.columns:
                    customer_id_col = possible_name
                    break
                    
            if not customer_id_col:
                print(f"  ⚠ No customer ID column found. Available columns: {list(df.columns)}")
                return
                
            # Create customers with behavior metrics
            print(f"  Loading {len(df)} customer behavior records...")
            
            # Load in batches
            with self.driver.session() as session:
                for i in tqdm(range(0, len(df), self.batch_size)):
                    batch = df.iloc[i:i+self.batch_size]
                    
                    # Prepare batch data
                    batch_data = []
                    for _, row in batch.iterrows():
                        customer_data = {
                            'customer_id': f'BEHAV_{row[customer_id_col]}',
                            'source': 'Behavior_Dataset'
                        }
                        
                        # Add other fields if they exist
                        if 'Age' in df.columns and pd.notna(row.get('Age')):
                            customer_data['age'] = int(row['Age'])
                        if 'Gender' in df.columns:
                            customer_data['gender'] = str(row.get('Gender', 'Unknown'))
                        if 'Purchase_Amount' in df.columns and pd.notna(row.get('Purchase_Amount')):
                            customer_data['last_purchase_amount'] = float(row['Purchase_Amount'])
                        
                        batch_data.append(customer_data)
                    
                    query = """
                    UNWIND $batch as row
                    MERGE (c:Customer {customer_id: row.customer_id})
                    SET c += row
                    """
                    
                    session.run(query, batch=batch_data)
                    
            print(f"  ✅ Customer behavior data loaded successfully")
            
        except Exception as e:
            print(f"  ❌ Error loading customer behavior: {str(e)}")

    def load_sessions_and_clickstream(self):
        """Load session and clickstream data"""
        print("\n🖱️ Loading Session & Clickstream Data...")
        
        path = self.data_root / "2. E-Commerce Behavior Data (Multi-Category Store)"
        csv_file = path / "2019-Oct.csv"
        
        if not csv_file.exists():
            print("  ⚠ Clickstream file not found, skipping...")
            return
            
        try:
            # Read sample of data
            df = pd.read_csv(csv_file, nrows=100000)  # Limit for demo
            
            # Create sessions
            sessions = df.groupby('user_session').agg({
                'user_id': 'first',
                'event_time': ['min', 'max'],
                'event_type': 'count'
            }).reset_index()
            
            # Flatten columns
            sessions.columns = ['session_id', 'user_id', 'start_time', 'end_time', 'event_count']
            
            print(f"  Loading {len(sessions)} sessions...")
            
            # Load sessions
            with self.driver.session() as session:
                for i in tqdm(range(0, len(sessions), self.batch_size)):
                    batch = sessions.iloc[i:i+self.batch_size]
                    
                    query = """
                    UNWIND $batch as row
                    CREATE (s:Session {
                        session_id: row.session_id,
                        customer_id: 'CLICK_' + toString(row.user_id),
                        start_time: datetime(row.start_time),
                        end_time: datetime(row.end_time),
                        event_count: toInteger(row.event_count)
                    })
                    """
                    
                    batch_dict = batch.to_dict('records')
                    for record in batch_dict:
                        record['start_time'] = str(record['start_time'])
                        record['end_time'] = str(record['end_time'])
                    
                    session.run(query, batch=batch_dict)
            
            # Create clickstream products and events
            print("  Creating clickstream events...")
            
            # Get product events
            product_events = df[df['product_id'].notna()].copy()
            product_events = product_events.head(10000)  # Limit for demo
            
            # Create products from clickstream
            products = product_events.groupby('product_id').agg({
                'category_code': 'first',
                'brand': 'first',
                'price': 'mean'
            }).reset_index()
            
            with self.driver.session() as session:
                for i in tqdm(range(0, len(products), self.batch_size), desc="Products"):
                    batch = products.iloc[i:i+self.batch_size]
                    
                    query = """
                    UNWIND $batch as row
                    MERGE (p:Product {sku: 'CLICK_' + toString(row.product_id)})
                    SET p.category = coalesce(row.category_code, 'Unknown'),
                        p.brand = coalesce(row.brand, 'Unknown'),
                        p.price = toFloat(coalesce(row.price, 0)),
                        p.source = 'Clickstream'
                    """
                    
                    session.run(query, batch=batch.fillna('').to_dict('records'))
            
            print(f"  ✅ Session and clickstream data loaded successfully")
            
        except Exception as e:
            print(f"  ❌ Error loading sessions: {str(e)}")

    def create_product_relationships(self):
        """Create relationships between products"""
        print("\n🔗 Creating Product Relationships...")
        
        with self.driver.session() as session:
            # Create FREQUENTLY_BOUGHT_WITH relationships
            print("  Creating co-purchase relationships...")
            
            query = """
            MATCH (c:Customer)-[:PURCHASED]->(p1:Product)
            MATCH (c)-[:PURCHASED]->(p2:Product)
            WHERE p1.sku < p2.sku
            WITH p1, p2, count(c) as co_purchase_count
            WHERE co_purchase_count > 2
            MERGE (p1)-[r:FREQUENTLY_BOUGHT_WITH {weight: co_purchase_count}]->(p2)
            """
            
            result = session.run(query)
            print(f"  ✅ Created co-purchase relationships")

    def update_product_scores(self):
        """Calculate and update product scores"""
        print("\n📈 Calculating Product Scores...")
        
        with self.driver.session() as session:
            # Calculate popularity scores
            query = """
            MATCH (p:Product)<-[r:PURCHASED]-()
            WITH p, count(r) as purchase_count
            SET p.popularity_score = purchase_count
            RETURN count(p) as updated_count
            """
            
            result = session.run(query).single()
            if result:
                print(f"  ✅ Updated popularity scores for {result['updated_count']} products")

    def show_enhanced_statistics(self):
        """Show statistics about loaded data"""
        print("\n📊 Database Statistics:")
        
        with self.driver.session() as session:
            # Count nodes by label
            node_stats = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as label, count(n) as count
                ORDER BY count DESC
            """).data()
            
            print("\n🔵 Nodes:")
            for stat in node_stats:
                print(f"   • {stat['label']}: {stat['count']:,}")
            
            # Count relationships
            rel_stats = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(r) as count
                ORDER BY count DESC
            """).data()
            
            if rel_stats:
                print("\n🔗 Relationships:")
                for stat in rel_stats:
                    print(f"   • {stat['type']}: {stat['count']:,}")

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
                p.main_cat = row.main_cat
            WITH p, row
            WHERE row.brand IS NOT NULL AND row.brand <> 'Unknown' AND row.brand <> ''
            MERGE (b:Brand {name: row.brand})
            MERGE (p)-[:MADE_BY]->(b)
            WITH p, row
            WHERE row.category IS NOT NULL AND row.category <> ''
            MERGE (c:Category {name: row.category})
            MERGE (p)-[:BELONGS_TO]->(c)
            """
            
            session.run(query, batch=batch)

    def clear_database(self):
        """Clear existing data"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("✅ Database cleared")

    def run_full_load(self):
        """Run complete enhanced data load"""
        print("=" * 60)
        print("ENHANCED DATA LOADER")
        print("=" * 60)
        
        # Clear and setup
        self.clear_database()
        self.create_enhanced_schema()
        
        # Load all datasets
        self.load_uci_retail_fixed()
        self.load_amazon_products_enhanced()
        self.load_customer_behavior_enriched()
        self.load_sessions_and_clickstream()
        
        # Create relationships and scores
        self.create_product_relationships()
        self.update_product_scores()
        
        # Show results
        self.show_enhanced_statistics()

    def close(self):
        self.driver.close()

if __name__ == "__main__":
    loader = EnhancedDataLoader()
    loader.run_full_load()
    loader.close()
    print("\n✅ Enhanced data loading complete!")