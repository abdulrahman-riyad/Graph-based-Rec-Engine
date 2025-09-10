# backend/app/database.py
"""Database connection management for Neo4j"""

from neo4j import GraphDatabase
from .config import settings  # Fixed: Use relative import
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages Neo4j database connections"""
    
    def __init__(self):
        self.driver = None
        
    def connect(self):
        """Create connection to Neo4j"""
        try:
            self.driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password)
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("Successfully connected to Neo4j")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
            
    def close(self):
        """Close database connection"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
            
    def get_session(self):
        """Get a Neo4j session"""
        if not self.driver:
            self.connect()
        return self.driver.session()
        
    def execute_query(self, query, parameters=None):
        """Execute a query and return results"""
        with self.get_session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
            
    def execute_write(self, query, parameters=None):
        """Execute a write transaction"""
        with self.get_session() as session:
            with session.begin_transaction() as tx:
                tx.run(query, parameters or {})
                tx.commit()
                
    def test_connection(self):
        """Test database connection"""
        try:
            with self.get_session() as session:
                result = session.run("MATCH (n) RETURN count(n) as count").single()
                return {"status": "connected", "node_count": result["count"]}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Create global database manager instance
db_manager = DatabaseManager()