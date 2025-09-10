#!/usr/bin/env python3
"""
scripts/load_all_data.py
Master script to load all e-commerce datasets into Neo4j
"""

import sys
import os
from pathlib import Path
import time
from datetime import datetime
import traceback

# Add parent directory to path to import enhanced_data_loader
sys.path.insert(0, str(Path(__file__).parent.parent))

from enhanced_data_loader import EnhancedDataLoader
from neo4j import GraphDatabase
from dotenv import load_dotenv
from colorama import init, Fore, Back, Style

# Initialize colorama for colored output
init()

# Load environment variables
load_dotenv()


class DataPipelineOrchestrator:
    """Orchestrates the complete data loading pipeline"""
    
    def __init__(self):
        self.start_time = None
        self.loader = None
        self.stats = {}
        
    def print_banner(self):
        """Print a nice banner"""
        print(f"""
{Fore.CYAN}{'='*70}
{Fore.YELLOW}🚀 E-COMMERCE DATA PIPELINE ORCHESTRATOR
{Fore.CYAN}{'='*70}{Style.RESET_ALL}

{Fore.GREEN}📊 This script will:
  1. Connect to Neo4j database
  2. Clear existing data (optional)
  3. Load all 7 e-commerce datasets
  4. Create relationships and indexes
  5. Calculate analytics and scores
  6. Verify data integrity{Style.RESET_ALL}
        """)
        
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        print(f"\n{Fore.CYAN}🔍 Checking prerequisites...{Style.RESET_ALL}")
        
        issues = []
        
        # Check environment variables
        if not os.getenv("NEO4J_URI"):
            issues.append("NEO4J_URI not set in .env file")
        if not os.getenv("NEO4J_USER"):
            issues.append("NEO4J_USER not set in .env file")
        if not os.getenv("NEO4J_PASSWORD"):
            issues.append("NEO4J_PASSWORD not set in .env file")
            
        # Check data directory
        data_dir = Path(__file__).parent.parent / "data"
        if not data_dir.exists():
            issues.append(f"Data directory not found: {data_dir}")
            
        # Check for at least one dataset
        required_dirs = [
            "1. Amazon Product Data (UCSD)",
            "2. E-Commerce Behavior Data (Multi-Category Store)",
            "3. E-Commerce Customer Behavior Dataset",
            "4. UCI Online Retail Dataset"
        ]
        
        found_datasets = []
        for dir_name in required_dirs:
            if (data_dir / dir_name).exists():
                found_datasets.append(dir_name)
                
        if not found_datasets:
            issues.append("No datasets found in data directory")
        else:
            print(f"{Fore.GREEN}  ✓ Found {len(found_datasets)} datasets{Style.RESET_ALL}")
            
        # Test Neo4j connection
        try:
            uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            user = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "password123")
            
            driver = GraphDatabase.driver(uri, auth=(user, password))
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                result.single()
            driver.close()
            print(f"{Fore.GREEN}  ✓ Neo4j connection successful{Style.RESET_ALL}")
        except Exception as e:
            issues.append(f"Cannot connect to Neo4j: {str(e)}")
            
        if issues:
            print(f"\n{Fore.RED}❌ Prerequisites not met:{Style.RESET_ALL}")
            for issue in issues:
                print(f"  • {issue}")
            print(f"\n{Fore.YELLOW}Please fix these issues and try again.{Style.RESET_ALL}")
            return False
            
        print(f"{Fore.GREEN}  ✓ All prerequisites met!{Style.RESET_ALL}")
        return True
        
    def ask_clear_database(self):
        """Ask user if they want to clear existing data"""
        print(f"\n{Fore.YELLOW}⚠️  Warning: This will clear all existing data in Neo4j!{Style.RESET_ALL}")
        response = input(f"{Fore.CYAN}Do you want to clear the database before loading? (yes/no): {Style.RESET_ALL}").lower()
        return response in ['yes', 'y']
        
    def run_pipeline(self, clear_db=True):
        """Run the complete data pipeline"""
        self.start_time = time.time()
        
        try:
            # Initialize loader
            print(f"\n{Fore.CYAN}🔌 Connecting to Neo4j...{Style.RESET_ALL}")
            self.loader = EnhancedDataLoader()
            
            # Clear database if requested
            if clear_db:
                print(f"\n{Fore.YELLOW}🗑️  Clearing existing data...{Style.RESET_ALL}")
                self.loader.clear_database()
                print(f"{Fore.GREEN}  ✓ Database cleared{Style.RESET_ALL}")
            
            # Create schema
            print(f"\n{Fore.CYAN}📋 Creating database schema...{Style.RESET_ALL}")
            self.loader.create_enhanced_schema()
            print(f"{Fore.GREEN}  ✓ Schema created{Style.RESET_ALL}")
            
            # Load datasets
            datasets = [
                ("UCI Retail Dataset", self.loader.load_uci_retail_fixed),
                ("Amazon Products", self.loader.load_amazon_products_enhanced),
                ("Customer Behavior", self.loader.load_customer_behavior_enriched),
                ("Sessions & Clickstream", self.loader.load_sessions_and_clickstream),
            ]
            
            for name, load_func in datasets:
                print(f"\n{Fore.CYAN}📦 Loading {name}...{Style.RESET_ALL}")
                try:
                    load_func()
                    print(f"{Fore.GREEN}  ✓ {name} loaded successfully{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.YELLOW}  ⚠ {name} partially loaded or skipped: {str(e)}{Style.RESET_ALL}")
            
            # Create relationships
            print(f"\n{Fore.CYAN}🔗 Creating product relationships...{Style.RESET_ALL}")
            self.loader.create_product_relationships()
            print(f"{Fore.GREEN}  ✓ Relationships created{Style.RESET_ALL}")
            
            # Update scores
            print(f"\n{Fore.CYAN}📊 Calculating product scores...{Style.RESET_ALL}")
            self.loader.update_product_scores()
            print(f"{Fore.GREEN}  ✓ Scores calculated{Style.RESET_ALL}")
            
            # Get statistics
            self.collect_statistics()
            
            # Show results
            self.show_results()
            
            return True
            
        except Exception as e:
            print(f"\n{Fore.RED}❌ Pipeline failed: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Stack trace:{Style.RESET_ALL}")
            traceback.print_exc()
            return False
            
        finally:
            if self.loader:
                self.loader.close()
                
    def collect_statistics(self):
        """Collect statistics about loaded data"""
        print(f"\n{Fore.CYAN}📈 Collecting statistics...{Style.RESET_ALL}")
        
        try:
            driver = GraphDatabase.driver(
                os.getenv("NEO4J_URI"),
                auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
            )
            
            with driver.session() as session:
                # Count nodes
                node_counts = session.run("""
                    MATCH (n)
                    RETURN labels(n)[0] as label, count(n) as count
                    ORDER BY count DESC
                """).data()
                
                self.stats['nodes'] = {item['label']: item['count'] for item in node_counts}
                
                # Count relationships
                rel_counts = session.run("""
                    MATCH ()-[r]->()
                    RETURN type(r) as type, count(r) as count
                    ORDER BY count DESC
                """).data()
                
                self.stats['relationships'] = {item['type']: item['count'] for item in rel_counts}
                
                # Get sample metrics
                metrics = session.run("""
                    MATCH (c:Customer)
                    OPTIONAL MATCH (c)-[r:PURCHASED]->()
                    WITH c, count(r) as purchases
                    RETURN 
                        count(c) as total_customers,
                        avg(purchases) as avg_purchases,
                        max(purchases) as max_purchases,
                        percentileDisc(purchases, 0.5) as median_purchases
                """).single()
                
                if metrics:
                    self.stats['metrics'] = dict(metrics)
                    
            driver.close()
            
        except Exception as e:
            print(f"{Fore.YELLOW}  ⚠ Could not collect all statistics: {str(e)}{Style.RESET_ALL}")
            
    def show_results(self):
        """Show final results and statistics"""
        elapsed_time = time.time() - self.start_time
        
        print(f"""
{Fore.CYAN}{'='*70}
{Fore.GREEN}✅ DATA PIPELINE COMPLETED SUCCESSFULLY!
{Fore.CYAN}{'='*70}{Style.RESET_ALL}

{Fore.YELLOW}📊 LOADED DATA SUMMARY:{Style.RESET_ALL}
""")
        
        # Show node counts
        if 'nodes' in self.stats:
            print(f"{Fore.CYAN}Nodes:{Style.RESET_ALL}")
            total_nodes = 0
            for label, count in self.stats['nodes'].items():
                print(f"  • {label}: {count:,}")
                total_nodes += count
            print(f"  {Fore.GREEN}Total: {total_nodes:,} nodes{Style.RESET_ALL}")
            
        # Show relationship counts
        if 'relationships' in self.stats:
            print(f"\n{Fore.CYAN}Relationships:{Style.RESET_ALL}")
            total_rels = 0
            for rel_type, count in self.stats['relationships'].items():
                print(f"  • {rel_type}: {count:,}")
                total_rels += count
            print(f"  {Fore.GREEN}Total: {total_rels:,} relationships{Style.RESET_ALL}")
            
        # Show metrics
        if 'metrics' in self.stats:
            print(f"\n{Fore.CYAN}Customer Metrics:{Style.RESET_ALL}")
            metrics = self.stats['metrics']
            if metrics.get('total_customers'):
                print(f"  • Total customers: {metrics['total_customers']:,}")
            if metrics.get('avg_purchases'):
                print(f"  • Avg purchases/customer: {metrics['avg_purchases']:.1f}")
            if metrics.get('median_purchases'):
                print(f"  • Median purchases: {metrics['median_purchases']}")
            if metrics.get('max_purchases'):
                print(f"  • Max purchases: {metrics['max_purchases']}")
                
        print(f"""
{Fore.CYAN}⏱️  Time elapsed: {elapsed_time:.2f} seconds{Style.RESET_ALL}

{Fore.GREEN}🎉 Next Steps:{Style.RESET_ALL}
  1. Start the backend: {Fore.YELLOW}cd backend && python run.py{Style.RESET_ALL}
  2. Start the frontend: {Fore.YELLOW}cd frontend && npm run dev{Style.RESET_ALL}
  3. Access the dashboard: {Fore.YELLOW}http://localhost:3000/dashboard{Style.RESET_ALL}
  4. Check the API docs: {Fore.YELLOW}http://localhost:8000/docs{Style.RESET_ALL}
  5. Explore Neo4j Browser: {Fore.YELLOW}http://localhost:7474{Style.RESET_ALL}

{Fore.CYAN}{'='*70}{Style.RESET_ALL}
        """)
        
    def run_verification(self):
        """Run data verification queries"""
        print(f"\n{Fore.CYAN}🔍 Running verification queries...{Style.RESET_ALL}")
        
        try:
            driver = GraphDatabase.driver(
                os.getenv("NEO4J_URI"),
                auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
            )
            
            with driver.session() as session:
                # Test queries
                queries = [
                    ("Products with reviews", """
                        MATCH (p:Product)<-[:ABOUT]-(r:Review)
                        RETURN count(DISTINCT p) as count
                    """),
                    ("Customers with purchases", """
                        MATCH (c:Customer)-[:PURCHASED]->()
                        RETURN count(DISTINCT c) as count
                    """),
                    ("Products with relationships", """
                        MATCH (p:Product)-[:FREQUENTLY_BOUGHT_WITH]-(p2:Product)
                        RETURN count(DISTINCT p) as count
                    """),
                ]
                
                for name, query in queries:
                    result = session.run(query).single()
                    if result and result['count'] > 0:
                        print(f"{Fore.GREEN}  ✓ {name}: {result['count']:,}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}  ⚠ {name}: 0{Style.RESET_ALL}")
                        
            driver.close()
            
        except Exception as e:
            print(f"{Fore.YELLOW}  ⚠ Verification incomplete: {str(e)}{Style.RESET_ALL}")


def main():
    """Main entry point"""
    orchestrator = DataPipelineOrchestrator()
    
    # Show banner
    orchestrator.print_banner()
    
    # Check prerequisites
    if not orchestrator.check_prerequisites():
        sys.exit(1)
        
    # Ask about clearing database
    clear_db = orchestrator.ask_clear_database()
    
    # Run pipeline
    print(f"\n{Fore.CYAN}🚀 Starting data pipeline...{Style.RESET_ALL}")
    success = orchestrator.run_pipeline(clear_db=clear_db)
    
    if success:
        # Run verification
        orchestrator.run_verification()
        sys.exit(0)
    else:
        print(f"\n{Fore.RED}Pipeline failed. Please check the errors above.{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠️  Pipeline interrupted by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error: {str(e)}{Style.RESET_ALL}")
        traceback.print_exc()
        sys.exit(1)