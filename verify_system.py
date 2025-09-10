#!/usr/bin/env python3
"""
verify_system.py
Verify that all components are working correctly
"""

import os
import sys
from pathlib import Path
from neo4j import GraphDatabase
from dotenv import load_dotenv
import requests
import time
from colorama import init, Fore, Style

init()
load_dotenv()

def check_neo4j_data():
    """Check Neo4j database contents"""
    print(f"\n{Fore.CYAN}=== NEO4J DATABASE CHECK ==={Style.RESET_ALL}")
    
    try:
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password123")
        
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        with driver.session() as session:
            # Count nodes
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as label, count(n) as count
                ORDER BY count DESC
            """)
            
            nodes = result.data()
            
            print(f"\n{Fore.GREEN}Nodes in database:{Style.RESET_ALL}")
            total_nodes = 0
            for node in nodes:
                print(f"  • {node['label']}: {node['count']:,}")
                total_nodes += node['count']
            print(f"  {Fore.YELLOW}Total: {total_nodes:,} nodes{Style.RESET_ALL}")
            
            # Count relationships
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(r) as count
                ORDER BY count DESC
                LIMIT 10
            """)
            
            relationships = result.data()
            
            if relationships:
                print(f"\n{Fore.GREEN}Relationships in database:{Style.RESET_ALL}")
                total_rels = 0
                for rel in relationships:
                    print(f"  • {rel['type']}: {rel['count']:,}")
                    total_rels += rel['count']
                print(f"  {Fore.YELLOW}Total: {total_rels:,} relationships{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.YELLOW}No relationships found{Style.RESET_ALL}")
            
            # Sample queries
            print(f"\n{Fore.GREEN}Sample queries:{Style.RESET_ALL}")
            
            # Customers with purchases
            result = session.run("""
                MATCH (c:Customer)-[:PURCHASED]->()
                RETURN count(DISTINCT c) as count
            """).single()
            
            if result and result['count'] > 0:
                print(f"  ✓ Customers with purchases: {result['count']:,}")
            else:
                print(f"  ⚠ No purchase relationships found")
            
            # Products with prices
            result = session.run("""
                MATCH (p:Product)
                WHERE p.price > 0
                RETURN count(p) as count
            """).single()
            
            if result:
                print(f"  ✓ Products with prices: {result['count']:,}")
                
        driver.close()
        return True
        
    except Exception as e:
        print(f"{Fore.RED}  ✗ Neo4j error: {str(e)}{Style.RESET_ALL}")
        return False

def check_backend():
    """Check if backend is running"""
    print(f"\n{Fore.CYAN}=== BACKEND API CHECK ==={Style.RESET_ALL}")
    
    try:
        # Check health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        
        if response.status_code == 200:
            print(f"{Fore.GREEN}  ✓ Backend is running{Style.RESET_ALL}")
            print(f"  Response: {response.json()}")
            
            # Test some endpoints
            endpoints = [
                "/api/v1/analytics/dashboard-summary",
                "/api/v1/products?limit=5",
                "/api/v1/customers?limit=5"
            ]
            
            print(f"\n{Fore.GREEN}Testing endpoints:{Style.RESET_ALL}")
            for endpoint in endpoints:
                try:
                    response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        print(f"  ✓ {endpoint}: OK")
                        if isinstance(data, list):
                            print(f"    Returned {len(data)} items")
                        elif isinstance(data, dict):
                            print(f"    Keys: {', '.join(list(data.keys())[:5])}")
                    else:
                        print(f"  ⚠ {endpoint}: Status {response.status_code}")
                except Exception as e:
                    print(f"  ✗ {endpoint}: Error - {str(e)}")
                    
            return True
        else:
            print(f"{Fore.YELLOW}  ⚠ Backend returned status {response.status_code}{Style.RESET_ALL}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}  ✗ Backend is not running{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}To start the backend:{Style.RESET_ALL}")
        print(f"  Option 1: python start_backend.py")
        print(f"  Option 2: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        print(f"  Option 3 (Windows): run_backend_windows.bat")
        return False
    except Exception as e:
        print(f"{Fore.RED}  ✗ Error checking backend: {str(e)}{Style.RESET_ALL}")
        return False

def check_frontend():
    """Check if frontend is accessible"""
    print(f"\n{Fore.CYAN}=== FRONTEND CHECK ==={Style.RESET_ALL}")
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        
        if response.status_code in [200, 301, 302, 304]:
            print(f"{Fore.GREEN}  ✓ Frontend is running{Style.RESET_ALL}")
            print(f"  Dashboard: http://localhost:3000/dashboard")
            return True
        else:
            print(f"{Fore.YELLOW}  ⚠ Frontend returned status {response.status_code}{Style.RESET_ALL}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"{Fore.YELLOW}  ⚠ Frontend is not running{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}To start the frontend:{Style.RESET_ALL}")
        print(f"  cd frontend && npm run dev")
        return False
    except Exception as e:
        print(f"{Fore.RED}  ✗ Error checking frontend: {str(e)}{Style.RESET_ALL}")
        return False

def main():
    print(f"""
{Fore.CYAN}{'='*60}
{Fore.YELLOW}E-COMMERCE SYSTEM VERIFICATION
{Fore.CYAN}{'='*60}{Style.RESET_ALL}
""")
    
    # Check Neo4j
    neo4j_ok = check_neo4j_data()
    
    # Check Backend
    backend_ok = check_backend()
    
    # Check Frontend
    frontend_ok = check_frontend()
    
    # Summary
    print(f"""
{Fore.CYAN}{'='*60}
{Fore.YELLOW}SUMMARY
{Fore.CYAN}{'='*60}{Style.RESET_ALL}

System Status:
  Neo4j Database: {Fore.GREEN if neo4j_ok else Fore.RED}{'✓ Running' if neo4j_ok else '✗ Issues detected'}{Style.RESET_ALL}
  Backend API: {Fore.GREEN if backend_ok else Fore.RED}{'✓ Running' if backend_ok else '✗ Not running'}{Style.RESET_ALL}
  Frontend: {Fore.GREEN if frontend_ok else Fore.YELLOW}{'✓ Running' if frontend_ok else '⚠ Not running'}{Style.RESET_ALL}
""")
    
    if neo4j_ok and backend_ok:
        print(f"{Fore.GREEN}✅ Core system is operational!{Style.RESET_ALL}")
        print(f"\nYou can access:")
        print(f"  • Dashboard: {Fore.CYAN}http://localhost:3000/dashboard{Style.RESET_ALL}")
        print(f"  • API Docs: {Fore.CYAN}http://localhost:8000/docs{Style.RESET_ALL}")
        print(f"  • Neo4j Browser: {Fore.CYAN}http://localhost:7474{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠ Some components need attention{Style.RESET_ALL}")
        
        if not neo4j_ok:
            print(f"\n{Fore.YELLOW}Neo4j issues detected. Try running:{Style.RESET_ALL}")
            print(f"  python enhanced_data_loader.py")
            
        if not backend_ok:
            print(f"\n{Fore.YELLOW}Backend not running. Try:{Style.RESET_ALL}")
            print(f"  python start_backend.py")

if __name__ == "__main__":
    main()