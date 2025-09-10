#!/usr/bin/env python3
"""
run_complete_pipeline.py
Complete pipeline runner - starts everything in correct order
"""

import subprocess
import time
import sys
import os
from pathlib import Path
import requests
from colorama import init, Fore, Style

init()

class PipelineRunner:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.processes = []
        
    def print_banner(self):
        print(f"""
{Fore.CYAN}{'='*70}
{Fore.YELLOW}🚀 E-COMMERCE INTELLIGENCE PLATFORM - COMPLETE PIPELINE
{Fore.CYAN}{'='*70}{Style.RESET_ALL}
        """)
        
    def check_neo4j(self):
        """Check if Neo4j is running"""
        print(f"\n{Fore.CYAN}1. Checking Neo4j...{Style.RESET_ALL}")
        
        try:
            from neo4j import GraphDatabase
            uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            user = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "password123")
            
            driver = GraphDatabase.driver(uri, auth=(user, password))
            with driver.session() as session:
                result = session.run("RETURN 1")
                result.single()
            driver.close()
            
            print(f"{Fore.GREEN}   ✓ Neo4j is running{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}   ✗ Neo4j is not running{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}   Please start Neo4j first:{Style.RESET_ALL}")
            print(f"   Option 1: docker-compose up -d neo4j")
            print(f"   Option 2: Start Neo4j Desktop")
            return False
            
    def load_data(self):
        """Load data into Neo4j"""
        print(f"\n{Fore.CYAN}2. Loading data into Neo4j...{Style.RESET_ALL}")
        
        response = input(f"{Fore.YELLOW}   Do you want to reload all data? (yes/no): {Style.RESET_ALL}").lower()
        if response in ['yes', 'y']:
            print(f"{Fore.CYAN}   Running data loader...{Style.RESET_ALL}")
            
            # Run the enhanced data loader
            try:
                subprocess.run([sys.executable, "enhanced_data_loader.py"], check=True)
                print(f"{Fore.GREEN}   ✓ Data loaded successfully{Style.RESET_ALL}")
                return True
            except subprocess.CalledProcessError as e:
                print(f"{Fore.RED}   ✗ Data loading failed: {e}{Style.RESET_ALL}")
                return False
        else:
            print(f"{Fore.YELLOW}   Skipping data load{Style.RESET_ALL}")
            return True
            
    def start_backend(self):
        """Start the backend server"""
        print(f"\n{Fore.CYAN}3. Starting backend server...{Style.RESET_ALL}")
        
        # Check if backend is already running
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print(f"{Fore.GREEN}   ✓ Backend is already running{Style.RESET_ALL}")
                return True
        except:
            pass
            
        # Start backend
        print(f"{Fore.YELLOW}   Starting backend on port 8000...{Style.RESET_ALL}")
        
        backend_process = subprocess.Popen(
            [sys.executable, "start_backend.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        self.processes.append(backend_process)
        
        # Wait for backend to start
        for i in range(30):
            try:
                response = requests.get("http://localhost:8000/health", timeout=1)
                if response.status_code == 200:
                    print(f"{Fore.GREEN}   ✓ Backend started successfully{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}   API Docs: http://localhost:8000/docs{Style.RESET_ALL}")
                    return True
            except:
                time.sleep(1)
                
        print(f"{Fore.RED}   ✗ Backend failed to start{Style.RESET_ALL}")
        return False
        
    def test_endpoints(self):
        """Test backend endpoints"""
        print(f"\n{Fore.CYAN}4. Testing backend endpoints...{Style.RESET_ALL}")
        
        try:
            subprocess.run([sys.executable, "scripts/test_endpoints.py"], check=True)
            return True
        except:
            print(f"{Fore.YELLOW}   Some endpoints may not be working{Style.RESET_ALL}")
            return True
            
    def start_frontend(self):
        """Start the frontend"""
        print(f"\n{Fore.CYAN}5. Starting frontend...{Style.RESET_ALL}")
        
        frontend_dir = self.root_dir / "frontend"
        
        # Check if node_modules exists
        if not (frontend_dir / "node_modules").exists():
            print(f"{Fore.YELLOW}   Installing frontend dependencies...{Style.RESET_ALL}")
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
            
        print(f"{Fore.YELLOW}   Starting frontend on port 3000...{Style.RESET_ALL}")
        
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        self.processes.append(frontend_process)
        
        print(f"{Fore.GREEN}   ✓ Frontend starting...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   Dashboard: http://localhost:3000/dashboard{Style.RESET_ALL}")
        
        return True
        
    def show_summary(self):
        """Show summary and next steps"""
        print(f"""
{Fore.CYAN}{'='*70}
{Fore.GREEN}✅ SYSTEM READY!
{Fore.CYAN}{'='*70}{Style.RESET_ALL}

{Fore.YELLOW}🎯 Access Points:{Style.RESET_ALL}
   • Dashboard: {Fore.CYAN}http://localhost:3000/dashboard{Style.RESET_ALL}
   • API Docs: {Fore.CYAN}http://localhost:8000/docs{Style.RESET_ALL}
   • Neo4j Browser: {Fore.CYAN}http://localhost:7474{Style.RESET_ALL}

{Fore.YELLOW}📊 Available Features:{Style.RESET_ALL}
   • Real-time Analytics Dashboard
   • Product Recommendations
   • Customer Segmentation
   • Revenue Analytics
   • Basket Analysis

{Fore.YELLOW}🛠️ Troubleshooting:{Style.RESET_ALL}
   • If frontend shows dummy data, refresh the page
   • Check console for any API errors
   • Verify Neo4j has data: MATCH (n) RETURN count(n)

{Fore.RED}Press CTRL+C to stop all services{Style.RESET_ALL}
        """)
        
    def cleanup(self):
        """Clean up processes on exit"""
        print(f"\n{Fore.YELLOW}Stopping services...{Style.RESET_ALL}")
        for process in self.processes:
            process.terminate()
        print(f"{Fore.GREEN}✓ All services stopped{Style.RESET_ALL}")
        
    def run(self):
        """Run the complete pipeline"""
        self.print_banner()
        
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        try:
            # Step 1: Check Neo4j
            if not self.check_neo4j():
                sys.exit(1)
                
            # Step 2: Load data
            if not self.load_data():
                response = input(f"{Fore.YELLOW}Continue anyway? (yes/no): {Style.RESET_ALL}")
                if response.lower() not in ['yes', 'y']:
                    sys.exit(1)
                    
            # Step 3: Start backend
            if not self.start_backend():
                print(f"{Fore.RED}Cannot continue without backend{Style.RESET_ALL}")
                sys.exit(1)
                
            # Step 4: Test endpoints
            self.test_endpoints()
            
            # Step 5: Start frontend
            response = input(f"\n{Fore.YELLOW}Start frontend? (yes/no): {Style.RESET_ALL}")
            if response.lower() in ['yes', 'y']:
                self.start_frontend()
                
            # Show summary
            self.show_summary()
            
            # Keep running
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.cleanup()
            
        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
            self.cleanup()
            sys.exit(1)


if __name__ == "__main__":
    runner = PipelineRunner()
    runner.run()