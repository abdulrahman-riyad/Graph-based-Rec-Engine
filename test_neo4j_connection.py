"""
test_neo4j_connection_fixed.py
Test Neo4j Aura connection
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from colorama import init, Fore, Style

# Initialize colorama
init()

# Load environment variables
load_dotenv()

def test_connection():
    """Test Neo4j Aura connection"""

    print(Fore.CYAN + "=" * 60)
    print("TESTING NEO4J AURA CONNECTION")
    print("=" * 60 + Style.RESET_ALL)

    # Get connection details from .env
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")

    print(f"Connecting to: {uri}")
    print(f"User: {user}")

    try:
        # Connect to Neo4j Aura
        driver = GraphDatabase.driver(uri, auth=(user, password))

        # Test the connection
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            value = result.single()["test"]

            if value == 1:
                print(Fore.GREEN + "✅ SUCCESS: Connected to Neo4j Aura!" + Style.RESET_ALL)

                # Get node count
                node_count = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
                print(f"\nCurrent database has {node_count:,} nodes")

                driver.close()
                return True

    except Exception as e:
        print(Fore.RED + f"❌ ERROR: {e}" + Style.RESET_ALL)
        return False

if __name__ == "__main__":
    test_connection()