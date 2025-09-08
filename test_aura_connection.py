"""
test_aura_final.py
Test Neo4j Aura connection (fixed version)
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

def test_connection():
    """Test Neo4j Aura connection"""

    print("=" * 60)
    print("TESTING NEO4J AURA CONNECTION")
    print("=" * 60)

    # Get connection details
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")

    print(f"URI: {uri}")
    print(f"User: {user}")

    try:
        # Simple connection for Aura
        driver = GraphDatabase.driver(uri, auth=(user, password))

        # Test query
        with driver.session() as session:
            result = session.run("RETURN 'Hello from Aura!' as message")
            message = result.single()['message']
            print(f"✅ SUCCESS: {message}")

            # Check node count
            count = session.run("MATCH (n) RETURN count(n) as c").single()['c']
            print(f"📊 Database has {count} nodes")

        driver.close()
        print("✅ Connection successful!")
        return True

    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()